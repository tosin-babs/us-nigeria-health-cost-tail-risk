"""
Robustness: does the headline survive the choices behind it?

The paper's claim is that Nigeria is worse on average and the United States is
worse in the tail. Every number supporting that rests on a decision someone
could have made differently: which years to pool, where to floor income, how
to define the subsistence floor, whether to equivalize, where to set the tail
threshold, which out-of-pocket instrument to use in Nigeria, and how the
denominator is built. This runs the whole comparison again under each.

The grid reports the four quantities the argument depends on:

    CHE10      catastrophic spending at the 10% budget share
    CTP40      catastrophic spending on capacity to pay
    CVaR95     expected shortfall at the 95th percentile
    xi         the generalized Pareto tail shape

A second table reruns the unconditional quantile regression's poverty
coefficient with Nigerian poverty measured on gross and on net-of-OOP
consumption, because the sign of that coefficient depends on it.

Writes Tables 9, 9b and 9c.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from burden import che_flags
from rif import ng_spec, run_country
from svy import Design
from tailrisk import tail_stats


def load():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")
    return us, ng


def evaluate(us, ng, label, income_floor=None, drop_years=(),
             ng_floor="poverty", equivalise=False,
             threshold_q=config.GPD_THRESHOLD_QUANTILE,
             ng_oop="health_module", denominator="published",
             us_min_povlev=None):
    """Run the whole comparison once and return one row per country."""
    u = us.copy()
    n = ng.copy()

    if drop_years:
        u = u[~u["year"].isin(drop_years)]
    floor = config.INCOME_FLOOR_USD if income_floor is None else income_floor
    u = u[(u["faminc"] >= floor) & (u["poverty_threshold"] > 0)].copy()
    if us_min_povlev is not None:
        u = u[u["povlev"] >= us_min_povlev].copy()

    # Nigerian out-of-pocket instrument. The consumption aggregate is rebuilt
    # so that health spending enters the denominator exactly once.
    base_cons = n["food"] + n["nonfood_excl_health"] + n["edu"]
    if ng_oop == "health_module":
        n_oop = n["oop"]
    elif ng_oop == "with_transport":
        n_oop = n["oop_with_transport"]
    elif ng_oop == "consumption_module":
        n_oop = n["oop_consumption_module"]
    else:
        raise ValueError(ng_oop)
    n_gross = base_cons + n_oop
    n_net = base_cons

    u_oop = u["oop"]
    if denominator == "published":
        u_res, n_res = u["faminc"], n_gross
    elif denominator == "net":
        u_res, n_res = u["faminc"], n_net
    elif denominator == "gross":
        u_res, n_res = u["faminc"] + u["oop"], n_gross
    else:
        raise ValueError(denominator)

    u_eq = u["n_persons"] ** config.EQ_SCALE_POWER
    n_eq = n["n_persons"] ** config.EQ_SCALE_POWER
    if equivalise:
        u_floor = (u["poverty_threshold"] / u["n_persons"].clip(lower=1)) * u_eq
        n_floor = (n["poverty_threshold"] / n["n_persons"].clip(lower=1)) * n_eq
        u_ctp = (u_res - u_floor).where(lambda x: x > 0)
        n_ctp = (n_res - n_floor).where(lambda x: x > 0)
    else:
        u_ctp = (u_res - u["poverty_threshold"]).where(lambda x: x > 0)
        if ng_floor == "poverty":
            n_ctp = (n_res - n["poverty_threshold"]).where(lambda x: x > 0)
        else:
            # Xu et al.'s rule, as carried in the companion file: the floor is
            # the food-share subsistence line when food spending is at or
            # above it and actual food spending otherwise.
            xu_floor = n["resources"] - n["ctp_food"]
            n_ctp = (n_res - xu_floor).where(lambda x: x > 0)

    rows = []
    for country, df, oop, res, ctp in (
            ("United States", u, u_oop, u_res, u_ctp),
            ("Nigeria", n, n_oop, n_res, n_ctp)):
        f = che_flags(oop, res, ctp)
        d = Design(df, "weight", "stratum", "psu")
        b = f["_burden"]
        ok = np.isfinite(b)
        st = tail_stats(b[ok], df["weight"].to_numpy(float)[ok],
                        threshold_q=threshold_q)
        rows.append({
            "variant": label, "country": country, "n": int(ok.sum()),
            "che10_pct": 100 * d.mean(f["che10"])[0],
            "ctp40_pct": 100 * d.mean(f["che_ctp40"])[0],
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
    ("US income at or above the poverty line", {"us_min_povlev": 100.0}),
    ("Nigeria: food-share floor", {"ng_floor": "food"}),
    ("Per equivalent adult", {"equivalise": True}),
    ("GPD threshold q85", {"threshold_q": 0.85}),
    ("GPD threshold q95", {"threshold_q": 0.95}),
    ("Nigeria: OOP including transport", {"ng_oop": "with_transport"}),
    ("Nigeria: consumption-module OOP", {"ng_oop": "consumption_module"}),
    ("Matched net denominators", {"denominator": "net"}),
    ("Matched gross denominators", {"denominator": "gross"}),
]


def rif_poverty_table(us, ng):
    """The Nigerian poverty coefficient on gross and net consumption."""
    u = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    u["burden"] = u["oop"] / u["faminc"]
    u = u[np.isfinite(u["burden"])].copy()
    n = ng[np.isfinite(ng["burden"])].copy()
    us_spec = {
        "Below the poverty line": (u["povlev"] < 100).astype(float),
        "1-2x the poverty line": u["povlev"].between(100, 200).astype(float),
        "Uninsured any part of the year": (u["insurance_group"]
                                           != "Insured all year").astype(float),
        "Any chronic condition": u["any_chronic"].astype(float),
        f"Any member aged {config.ELDERLY_AGE}+": (u["n_elderly_h"] > 0).astype(float),
        f"Any child under {config.CHILD_AGE}": (u["n_child_h"] > 0).astype(float),
        "Household size": u["n_persons"].astype(float),
    }
    out = []
    for label, df, spec in (
            ("United States, income", u, us_spec),
            ("Nigeria, consumption net of OOP", n, ng_spec(n, "net")),
            ("Nigeria, gross consumption", n, ng_spec(n, "gross"))):
        r = run_country(df, spec, label)
        r = r[r["term"] == "Below the poverty line"]
        out.append(r[["country", "quantile", "coef_pp", "se_pp", "t"]]
                   .rename(columns={"country": "basis"}))
    return pd.concat(out, ignore_index=True)


def main():
    us, ng = load()
    rows = []
    for label, kw in VARIANTS:
        rows.extend(evaluate(us, ng, label, **kw))
    t9 = pd.DataFrame(rows)
    t9.to_csv(config.TABLES / "table9_robustness.csv", index=False)

    order = [v for v, _ in VARIANTS]
    print("=== Robustness: does the headline survive? ===\n")
    print(f"  {'variant':<40} {'CHE10':>14} {'CTP40':>14} "
          f"{'CVaR95':>15} {'xi':>17}")
    for v in order:
        r = t9[t9["variant"] == v].set_index("country")
        u_, n_ = r.loc["United States"], r.loc["Nigeria"]
        print(f"  {v:<40} {u_['che10_pct']:5.1f}% {n_['che10_pct']:6.1f}% "
              f"{u_['ctp40_pct']:5.1f}% {n_['ctp40_pct']:6.1f}% "
              f"{u_['cvar95_pct']:6.1f}% {n_['cvar95_pct']:6.1f}% "
              f"{u_['xi']:+8.3f} {n_['xi']:+8.3f}")

    checks = []
    for v in order:
        r = t9[t9["variant"] == v].set_index("country")
        checks.append({
            "variant": v,
            "Nigeria worse on CHE10":
                r.loc["Nigeria", "che10_pct"] > r.loc["United States", "che10_pct"],
            "US tail heavier (xi)":
                r.loc["United States", "xi"] > r.loc["Nigeria", "xi"],
            "US CVaR95 higher":
                r.loc["United States", "cvar95_pct"] > r.loc["Nigeria", "cvar95_pct"],
        })
    chk = pd.DataFrame(checks)
    chk.to_csv(config.TABLES / "table9b_robustness_checks.csv", index=False)

    print("\n=== Do the paper's claims hold in every variant? ===")
    for col in chk.columns[1:]:
        n_ok = int(chk[col].sum())
        flag = "yes" if n_ok == len(chk) else "NO"
        print(f"  {col:<26} {n_ok}/{len(chk)} variants   {flag}")
        if n_ok < len(chk):
            for v in chk.loc[~chk[col], "variant"]:
                print(f"      fails under: {v}")

    t9c = rif_poverty_table(us, ng)
    t9c.to_csv(config.TABLES / "table9c_rif_poverty_basis.csv", index=False)
    print("\n=== RIF poverty coefficient by basis (pp) ===")
    print(t9c.pivot_table(index="basis", columns="quantile", values="coef_pp")
          .to_string(float_format=lambda x: f"{x:+.2f}"))

    print(f"\nwrote tables 9, 9b and 9c to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
