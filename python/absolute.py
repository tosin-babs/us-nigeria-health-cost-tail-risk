"""
The absolute comparison, in purchasing-power-parity dollars.

Everything else in this paper compares *relative* burden, because the two
denominators are different variables and no transformation makes them the
same. The one comparison where the denominators do not have to match is the
numerator: what a household actually pays, converted to a common unit.

Two conversions are needed and both are stated rather than buried:

  * Nigerian naira are in constant August-2023 prices and are converted at the
    World Bank's 2023 private-consumption PPP factor.
  * US dollars are in constant 2024 prices, so they are first deflated to 2023
    with the same CPI series used to build them. The US dollar is the numeraire
    for international dollars, so no further conversion applies.

A PPP factor for private consumption is not a health-specific price index, and
medical prices diverge from general ones in both countries. The comparison is
indicative of what households pay, not of what they buy.

Writes Table 8.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

import config
from svy import Design

QUANTILES = (0.50, 0.75, 0.90, 0.95, 0.99)


def main():
    ppp_path = config.DERIVED / "ppp.json"
    if not ppp_path.exists():
        raise SystemExit("run build_nigeria.py first; it fetches the PPP factor")
    ppp = json.loads(ppp_path.read_text())
    ngn_per_intl = float(ppp["ppp_ngn_per_intl_usd"])
    ppp_year = ppp["ppp_year_ng"]

    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")

    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    ng = ng[np.isfinite(ng["burden"])].copy()

    # Put both on 2023 international dollars.
    us_to_ppp_year = 1.0 / config.CPI_TO_BASE[2023]   # 2024 USD -> 2023 USD
    us["oop_intl"] = us["oop"] * us_to_ppp_year
    us["oop_intl_pc"] = us["oop_intl"] / us["n_persons"].clip(lower=1)
    us["res_intl_pc"] = (us["faminc"] * us_to_ppp_year
                         / us["n_persons"].clip(lower=1))

    ng["oop_intl"] = ng["oop"] / ngn_per_intl
    ng["oop_intl_pc"] = ng["oop_intl"] / ng["n_persons"].clip(lower=1)
    ng["res_intl_pc"] = (ng["resources"] / ngn_per_intl
                         / ng["n_persons"].clip(lower=1))

    d_us = Design(us, "weight", "stratum", "psu")
    d_ng = Design(ng, "weight", "stratum", "psu")

    print(f"PPP: {ngn_per_intl:,.2f} naira per international dollar ({ppp_year})")
    print(f"US amounts deflated from {config.BASE_YEAR} to 2023 by "
          f"x{us_to_ppp_year:.4f}\n")

    rows = []
    for label, d, df in (("United States", d_us, us), ("Nigeria", d_ng, ng)):
        oop = df["oop_intl"].to_numpy(float)
        oop_pc = df["oop_intl_pc"].to_numpy(float)
        res_pc = df["res_intl_pc"].to_numpy(float)
        row = {"country": label,
               "mean_oop_household": d.mean(oop)[0],
               "mean_oop_per_person": d.mean(oop_pc)[0],
               "mean_resources_per_person": d.mean(res_pc)[0]}
        for q in QUANTILES:
            row[f"oop_hh_q{int(100 * q)}"] = d.quantile(oop, [q])[0]
            row[f"oop_pc_q{int(100 * q)}"] = d.quantile(oop_pc, [q])[0]
        rows.append(row)
    t8 = pd.DataFrame(rows)
    t8.to_csv(config.TABLES / "table8_ppp_absolute.csv", index=False)

    print("=== Out-of-pocket spending in 2023 international dollars ===")
    print(f"  {'':<16} {'US':>12} {'Nigeria':>12} {'ratio':>8}")
    a, b = t8.iloc[0], t8.iloc[1]
    for lab, key in (("mean, household", "mean_oop_household"),
                     ("mean, per person", "mean_oop_per_person"),
                     ("resources p.p.", "mean_resources_per_person")):
        print(f"  {lab:<16} {a[key]:12,.0f} {b[key]:12,.0f} "
              f"{a[key] / b[key]:8.1f}")
    print()
    for q in QUANTILES:
        k = f"oop_pc_q{int(100 * q)}"
        r = a[k] / b[k] if b[k] > 0 else np.nan
        print(f"  per person q{int(100 * q):<3d}  {a[k]:12,.0f} {b[k]:12,.0f} "
              f"{r:8.1f}")

    print("\n  The absolute gap is an order of magnitude wide and roughly")
    print("  constant across the distribution, which is why the paper's")
    print("  comparison is of burden rather than of spending.")
    print(f"\nwrote table 8 to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
