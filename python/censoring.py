"""
Evidence on the mechanism: forgone care and medical debt.

The interpretation offered for the shape of the two distributions is that
out-of-pocket spending is truncated where households cannot pay (they go
without care) and extended where they can borrow (bills exceed a year's
income). Neither survey observes that directly, but both carry items that
bear on it.

United States (MEPS, round 4/2 of each year):
  cost barrier   delayed, or could not afford, medical care or prescription
                 medicines because of cost (any of four items)
  medical debt   any medical debt (2024 file only)
tabulated by burden band and by income relative to the poverty line.

Nigeria (GHS-Panel wave 5, post-planting health section):
  among members ill or injured in the last four weeks, the share who
  consulted no one, and the share who consulted no one and gave cost as a
  reason; among households with an ill member, the share with no
  out-of-pocket spending. All by quintile of per-capita consumption net of
  out-of-pocket spending, so that spending on health does not move a
  household up the ranking.

Writes Table 13.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from svy import Design


def _est(design, mask, y, country, measure, dimension, group):
    fin = np.isfinite(y) & mask
    est, se = design.subset(mask).mean(y)
    return {"country": country, "measure": measure, "dimension": dimension,
            "group": group, "estimate_pct": 100 * est, "se_pct": 100 * se,
            "ci_low": 100 * (est - 1.96 * se), "ci_high": 100 * (est + 1.96 * se),
            "n": int(fin.sum())}


def band_labels():
    b = config.BURDEN_BANDS
    out = []
    for lo, hi in zip(b[:-1], b[1:]):
        if np.isinf(hi):
            out.append((lo, hi, f"{100 * lo:.0f}% or more"))
        else:
            out.append((lo, hi, f"{100 * lo:.0f}% to under {100 * hi:.0f}%"))
    return out


def us_rows():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    b = (us["oop"] / us["faminc"]).to_numpy(float)
    d = Design(us, "weight", "stratum", "psu")
    rows = []
    US = "United States"
    cb = us["cost_barrier"].to_numpy(float)
    debt = us["med_debt"].to_numpy(float)
    y24 = (us["year"] == 2024).to_numpy()
    allm = np.ones(len(us), bool)
    rows.append(_est(d, allm, cb, US, "Cost barrier to care", "All", "All families"))
    rows.append(_est(d, y24, debt, US, "Any medical debt (2024)", "All",
                     "All families"))
    for lo, hi, lab in band_labels():
        m = (b >= lo) & (b < hi)
        rows.append(_est(d, m, cb, US, "Cost barrier to care",
                         "Burden (OOP / income)", lab))
        rows.append(_est(d, m & y24, debt, US, "Any medical debt (2024)",
                         "Burden (OOP / income)", lab))
    pov = us["povlev"].to_numpy(float)
    for lab, m in (("Below 100% of poverty", pov < 100),
                   ("100% to under 200%", (pov >= 100) & (pov < 200)),
                   ("200% to under 400%", (pov >= 200) & (pov < 400)),
                   ("400% or more", pov >= 400)):
        rows.append(_est(d, m, cb, US, "Cost barrier to care",
                         "Income relative to poverty", lab))
        rows.append(_est(d, m & y24, debt, US, "Any medical debt (2024)",
                         "Income relative to poverty", lab))
    return rows


def ng_rows():
    path = config.DERIVED / "ng_care.csv"
    if not path.exists():
        print("  ng_care.csv missing; Nigerian rows skipped")
        return []
    care = pd.read_csv(path)
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")
    NG = "Nigeria"
    rows = []
    dp = Design(care, "weight", "stratum", "psu")
    ill = (care["ill"] == 1).to_numpy()
    y_none = care["consulted_no_one"].to_numpy(float)
    y_cost = care["no_consult_cost"].to_numpy(float)
    q = care["quintile_net"].to_numpy()

    hh_ill = care.groupby("hhid")["ill"].max().rename("any_ill")
    h = ng.merge(hh_ill, left_on="hhid", right_index=True, how="left")
    h["any_ill"] = h["any_ill"].fillna(0)
    dh = Design(h, "weight", "stratum", "psu")
    hill = (h["any_ill"] == 1).to_numpy()
    y_zero = (h["oop"] == 0).astype(float).to_numpy()
    hq = h["quintile_net"].to_numpy()

    groups = [("All", np.ones(len(care), bool), np.ones(len(h), bool))]
    groups += [(f"Q{k}" + (" (poorest)" if k == 1 else " (richest)" if k == 5
                           else ""), q == k, hq == k) for k in range(1, 6)]
    for lab, mp, mh in groups:
        dim = "All" if lab == "All" else "Quintile, consumption net of OOP"
        rows.append(_est(dp, ill & mp, y_none, NG,
                         "Ill, consulted no one", dim, lab))
        rows.append(_est(dp, ill & mp, y_cost, NG,
                         "Ill, consulted no one because of cost", dim, lab))
        rows.append(_est(dh, hill & mh, y_zero, NG,
                         "Household with an ill member, no OOP", dim, lab))
    return rows


def main():
    t13 = pd.DataFrame(us_rows() + ng_rows())
    t13.to_csv(config.TABLES / "table13_access_debt.csv", index=False)
    print("=== Cost barriers, medical debt and forgone care ===")
    print(t13[["country", "measure", "group", "estimate_pct", "se_pct", "n"]]
          .to_string(index=False, float_format=lambda x: f"{x:,.2f}"))
    print(f"\nwrote table 13 to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
