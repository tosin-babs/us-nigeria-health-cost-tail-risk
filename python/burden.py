"""
Harmonised burden measures and the catastrophic-spending comparison.

Two measures, applied identically to both countries:

  budget share      OOP / resources
  capacity to pay   OOP / (resources - subsistence floor)

The capacity-to-pay measure needs care. Half of Nigerian households sit at or
below the national poverty line, so their capacity to pay is zero or negative
and the ratio is undefined. Dropping them would drop the poorest half of the
country, which would be a far worse error than any handling rule. A household
below the subsistence floor that spends anything at all on health is, by the
logic the measure exists to capture, sacrificing subsistence to do it, so it
is counted as catastrophic whenever out-of-pocket spending is positive. The
share of households in that position is reported in every table, because it is
itself one of the sharper contrasts between the two countries.

Writes Tables 1, 2 and 3.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from svy import Design


def load():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")
    return us, ng


def designs(us, ng, weight="weight"):
    return (Design(us, weight, "stratum", "psu"),
            Design(ng, weight, "stratum", "psu"))


def che_flags(oop, resources, ctp, thresholds=config.CHE_BUDGET_THRESHOLDS,
              ctp_threshold=config.CHE_CTP_THRESHOLD):
    """Catastrophic flags on both definitions, with the below-floor rule."""
    oop = np.asarray(oop, float)
    resources = np.asarray(resources, float)
    ctp = np.asarray(ctp, float)

    share = np.divide(oop, resources, out=np.full_like(oop, np.nan),
                      where=resources > 0)
    out = {f"che{int(100 * t)}": (share > t).astype(float) for t in thresholds}

    # Below or at the floor: no capacity to pay, so any spending is catastrophic.
    no_capacity = ~(ctp > 0)
    ratio = np.divide(oop, ctp, out=np.full_like(oop, np.nan), where=ctp > 0)
    ctp_flag = np.where(no_capacity, (oop > 0).astype(float),
                        (ratio >= ctp_threshold).astype(float))
    out["che_ctp40"] = ctp_flag
    out["_no_capacity"] = no_capacity.astype(float)
    out["_burden"] = share
    out["_burden_ctp"] = ratio
    return out


def _row(design, y, label, dimension, group, n):
    est, se = design.mean(np.nan_to_num(y, nan=0.0))
    return {"measure": label, "dimension": dimension, "group": group,
            "estimate_pct": 100 * est, "se_pct": 100 * se,
            "ci_low": 100 * (est - 1.96 * se), "ci_high": 100 * (est + 1.96 * se),
            "n": int(n)}


LABELS = {"che10": "Budget share > 10%", "che25": "Budget share > 25%",
          "che40": "Budget share > 40%",
          "che_ctp40": "Capacity to pay >= 40%",
          "_no_capacity": "No capacity to pay (at or below the floor)"}


def country_table(d, flags, dims):
    """CHE by every requested dimension for one country."""
    rows = []
    for key, label in LABELS.items():
        y = flags[key]
        rows.append(_row(d, y, label, "Overall", "All", len(y)))
        for dim_name, series in dims.items():
            for g in pd.Series(series).dropna().unique():
                mask = (pd.Series(series) == g).to_numpy()
                if mask.sum() < 30:
                    continue
                rows.append(_row(d.subset(mask), y, label, dim_name, str(g),
                                 mask.sum()))
    return pd.DataFrame(rows)


def quantile_table(d_us, b_us, d_ng, b_ng, probs=(0.25, 0.5, 0.75, 0.9,
                                                  0.95, 0.99)):
    rows = []
    for q in probs:
        u = d_us.quantile(b_us, [q])[0]
        n = d_ng.quantile(b_ng, [q])[0]
        rows.append({"quantile": q, "us_burden_pct": 100 * u,
                     "nigeria_burden_pct": 100 * n,
                     "ratio_ng_to_us": n / u if u > 0 else np.nan,
                     "gap_pp": 100 * (n - u)})
    return pd.DataFrame(rows)


def main():
    us, ng = load()

    # US burden is undefined where income is unusable; keep the rows but let
    # the measure be missing, so the sample size is honest.
    us_ok = (us["income_usable"] == 1) & (us["poverty_threshold"] > 0)
    print(f"US families: {len(us):,}  usable for burden: {us_ok.sum():,} "
          f"({100 * us_ok.mean():.1f}%)")

    us_f = che_flags(us["oop"], us["faminc"].where(us_ok),
                     us["ctp"].where(us_ok))
    ng_f = che_flags(ng["oop"], ng["resources"], ng["ctp_poverty"])

    d_us, d_ng = designs(us, ng)

    # ---------------------------------------------------------- Table 1 ----
    us_dims = {
        "Insurance status": us["insurance_group"],
        "Poverty category": us["povcat"].map(
            {1: "Poor/negative", 2: "Near poor", 3: "Low income",
             4: "Middle income", 5: "High income"}),
        "Any chronic condition": us["any_chronic"].map({0: "No", 1: "Yes"}),
        "Elderly member": (us["n_over64"] > 0).map({False: "No", True: "Yes"}),
    }
    ng_dims = {
        "Sector": ng["sector_group"],
        "Consumption quintile": ng["quintile"].map(
            {1: "Q1 (poorest)", 2: "Q2", 3: "Q3", 4: "Q4", 5: "Q5 (richest)"}),
        "Insurance status": ng["insurance_group"],
        "Residence": ng["urban"].map({0: "Rural", 1: "Urban"}),
    }
    t_us = country_table(d_us, us_f, us_dims).assign(country="United States")
    t_ng = country_table(d_ng, ng_f, ng_dims).assign(country="Nigeria")
    t1 = pd.concat([t_us, t_ng], ignore_index=True)
    t1.to_csv(config.TABLES / "table1_che_harmonised.csv", index=False)

    print("\n=== Catastrophic spending, harmonised (overall) ===")
    ov = t1[t1["dimension"] == "Overall"]
    for c in ("United States", "Nigeria"):
        print(f"\n  {c}")
        for _, r in ov[ov["country"] == c].iterrows():
            print(f"    {r['measure']:<46s} {r['estimate_pct']:6.2f}%  "
                  f"({r['ci_low']:5.2f}-{r['ci_high']:5.2f})")

    # ---------------------------------------------------------- Table 2 ----
    b_us = us_f["_burden"]
    b_ng = ng_f["_burden"]
    t2 = quantile_table(d_us, b_us, d_ng, b_ng)
    t2.to_csv(config.TABLES / "table2_burden_quantiles.csv", index=False)
    print("\n=== Burden distribution: OOP as a share of resources ===")
    print(f"  {'quantile':>9} {'US':>9} {'Nigeria':>9} {'ratio':>7}")
    for _, r in t2.iterrows():
        print(f"  {'q' + str(int(100 * r['quantile'])):>9} "
              f"{r['us_burden_pct']:8.2f}% {r['nigeria_burden_pct']:8.2f}% "
              f"{r['ratio_ng_to_us']:7.2f}")

    # ---------------------------------------------------------- Table 3 ----
    # The same comparison inside subgroups, which is where the tail lives.
    rows = []
    for label, mask in [
        ("US, insured all year", (us["insurance_group"] == "Insured all year")),
        ("US, partly uninsured", (us["insurance_group"] == "Partly uninsured")),
        ("US, uninsured all year", (us["insurance_group"] == "Uninsured all year")),
        ("US, poor or near poor", us["povcat"].isin([1, 2])),
        ("US, chronic condition", us["any_chronic"] == 1),
    ]:
        m = (mask & us_ok).to_numpy()
        sub = d_us.subset(m)
        r = {"group": label, "country": "United States", "n": int(m.sum())}
        for q in (0.5, 0.75, 0.9, 0.95, 0.99):
            r[f"q{int(100 * q)}"] = 100 * sub.quantile(b_us, [q])[0]
        rows.append(r)
    for label, mask in [
        ("Nigeria, all", pd.Series(True, index=ng.index)),
        ("Nigeria, informal", ng["sector_group"] == "Informal"),
        ("Nigeria, formal", ng["sector_group"] == "Formal"),
        ("Nigeria, poorest quintile", ng["quintile"] == 1),
    ]:
        m = mask.to_numpy()
        sub = d_ng.subset(m)
        r = {"group": label, "country": "Nigeria", "n": int(m.sum())}
        for q in (0.5, 0.75, 0.9, 0.95, 0.99):
            r[f"q{int(100 * q)}"] = 100 * sub.quantile(b_ng, [q])[0]
        rows.append(r)
    t3 = pd.DataFrame(rows)
    t3.to_csv(config.TABLES / "table3_burden_by_group.csv", index=False)
    print("\n=== Burden quantiles by group (% of resources) ===")
    print(t3.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

    np.save(config.DERIVED / "burden_us.npy", b_us)
    np.save(config.DERIVED / "burden_ng.npy", b_ng)
    print(f"\nwrote 3 tables to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
