"""
Robustness: does the headline survive the choices behind it?

The paper's claim is that Nigeria is worse on average and the United States is
worse in the tail. Every number supporting that rests on a decision someone
could have made differently - which years to pool, where to floor income, how
to define the subsistence floor, whether to equivalise for household size,
where to set the tail threshold. This runs the whole comparison again under
each of them.

The grid reports the four quantities the argument depends on:

    CHE10      catastrophic spending at the 10% budget share
    CTP40      catastrophic spending on capacity to pay
    CVaR95     expected shortfall at the 95th percentile
    xi         the generalised Pareto tail shape

A variant is a problem for the paper only if it changes the *sign* of the
US-Nigeria gap on one of these, not if it moves a level.

Writes Table 9.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from burden import che_flags
from svy import Design
from tailrisk import tail_stats


def load():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")
    return us, ng


def evaluate(us, ng, label, income_floor=None, drop_years=(),
             ng_floor="poverty", equivalise=False,
             threshold_q=config.GPD_THRESHOLD_QUANTILE):
    """Run the whole comparison once and return one row per country."""
    u = us.copy()
    n = ng.copy()

    if drop_years:
        u = u[~u["year"].isin(drop_years)]
    floor = config.INCOME_FLOOR_USD if income_floor is None else income_floor
    u = u[(u["faminc"] >= floor) & (u["poverty_threshold"] > 0)].copy()

    # The budget-share burden is a ratio, so scaling numerator and denominator
    # by the same equivalence factor leaves it untouched. The scale only bites
    # on the subsistence floor, which is where Xu et al. apply it: the floor is
    # a per-person amount multiplied by household size, and equivalising
    # replaces that with size^0.56. That is the variant worth running.
    u_res, u_oop = u["faminc"], u["oop"]
    n_res, n_oop = n["resources"], n["oop"]

    u_eq = u["n_persons"] ** config.EQ_SCALE_POWER
    n_eq = n["n_persons"] ** config.EQ_SCALE_POWER
    if equivalise:
        u_floor = (u["poverty_threshold"] / u["n_persons"].clip(lower=1)) * u_eq
        n_floor = (n["poverty_threshold"] / n["n_persons"].clip(lower=1)) * n_eq
        u_ctp = (u_res - u_floor).where(lambda x: x > 0)
        n_ctp = (n_res - n_floor).where(lambda x: x > 0)
    else:
        u_ctp = u["ctp"]
        n_ctp = (n["ctp_poverty"] if ng_floor == "poverty"
                 else n["ctp_food"].where(n["ctp_food"] > 0))

    rows = []
    for country, df, oop, res, ctp, wcol in (
            ("United States", u, u_oop, u_res, u_ctp, "weight"),
            ("Nigeria", n, n_oop, n_res, n_ctp, "weight")):
        f = che_flags(oop, res, ctp)
        d = Design(df, wcol, "stratum", "psu")
        b = f["_burden"]
        ok = np.isfinite(b)
        st = tail_stats(b[ok], df[wcol].to_numpy(float)[ok],
                        threshold_q=threshold_q)
        rows.append({
            "variant": label, "country": country, "n": int(len(df)),
            "che10_pct": 100 * d.mean(np.nan_to_num(f["che10"]))[0],
            "ctp40_pct": 100 * d.mean(np.nan_to_num(f["che_ctp40"]))[0],
            "var95_pct": 100 * st["var95"],
            "cvar95_pct": 100 * st["cvar95"],
            "xi": st["xi"],
        })
    return rows


VARIANTS = [
    ("Baseline", {}),
    ("Excluding 2020 (pandemic)", {"drop_years": config.PANDEMIC_YEARS}),
    ("US 2024 only", {"drop_years": (2019, 2020, 2021, 2022, 2023)}),
    ("US 2019 only", {"drop_years": (2020, 2021, 2022, 2023, 2024)}),
    ("Income floor $500", {"income_floor": 500.0}),
    ("Income floor $2,000", {"income_floor": 2_000.0}),
    ("Income floor $5,000", {"income_floor": 5_000.0}),
    ("Nigeria: food-share floor", {"ng_floor": "food"}),
    ("Per equivalent adult", {"equivalise": True}),
    ("GPD threshold q85", {"threshold_q": 0.85}),
    ("GPD threshold q95", {"threshold_q": 0.95}),
]


def main():
    us, ng = load()
    rows = []
    for label, kw in VARIANTS:
        rows.extend(evaluate(us, ng, label, **kw))
    t9 = pd.DataFrame(rows)
    t9.to_csv(config.TABLES / "table9_robustness.csv", index=False)

    piv = t9.pivot_table(index="variant", columns="country",
                         values=["che10_pct", "cvar95_pct", "xi"])
    order = [v for v, _ in VARIANTS]

    print("=== Robustness: does the headline survive? ===\n")
    print(f"  {'variant':<27} {'CHE10':>14} {'CTP40':>14} "
          f"{'CVaR95':>15} {'xi':>17}")
    print(f"  {'':<27} {'US':>6} {'NG':>7} {'US':>6} {'NG':>7} "
          f"{'US':>7} {'NG':>7} {'US':>8} {'NG':>8}")
    for v in order:
        r = t9[t9["variant"] == v].set_index("country")
        u_, n_ = r.loc["United States"], r.loc["Nigeria"]
        print(f"  {v:<27} {u_['che10_pct']:5.1f}% {n_['che10_pct']:6.1f}% "
              f"{u_['ctp40_pct']:5.1f}% {n_['ctp40_pct']:6.1f}% "
              f"{u_['cvar95_pct']:6.1f}% {n_['cvar95_pct']:6.1f}% "
              f"{u_['xi']:+8.3f} {n_['xi']:+8.3f}")

    # The two claims the paper actually makes, checked variant by variant.
    checks = []
    for v in order:
        r = t9[t9["variant"] == v].set_index("country")
        checks.append({
            "variant": v,
            "Nigeria worse on CHE10":
                r.loc["Nigeria", "che10_pct"] > r.loc["United States", "che10_pct"],
            "US tail heavier (xi)":
                r.loc["United States", "xi"] > r.loc["Nigeria", "xi"],
        })
    chk = pd.DataFrame(checks)
    chk.to_csv(config.TABLES / "table9b_robustness_checks.csv", index=False)

    print("\n=== Do the paper's two claims hold in every variant? ===")
    for col in ("Nigeria worse on CHE10", "US tail heavier (xi)"):
        n_ok = int(chk[col].sum())
        flag = "yes" if n_ok == len(chk) else "NO"
        print(f"  {col:<26} {n_ok}/{len(chk)} variants   {flag}")
        if n_ok < len(chk):
            for v in chk.loc[~chk[col], "variant"]:
                print(f"      fails under: {v}")

    print(f"\nwrote tables 9 and 9b to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
