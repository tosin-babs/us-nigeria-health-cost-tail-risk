"""
Put the Nigerian household file onto the same basis as the US one.

The input is Paper 2's derived household file, which already carries
out-of-pocket spending, the consumption aggregate, the survey design and the
food-share subsistence floor. Two things are added here:

  * a poverty-line subsistence floor, so that capacity to pay is defined the
    same way in both countries (MEPS cannot support a food-share floor);
  * PPP-converted amounts, for the absolute comparison where the two
    denominators do not have to match.

Writes data/derived/ng_household.csv.
"""

from __future__ import annotations

import json
import urllib.request

import numpy as np
import pandas as pd

import config

# Paper 2's poverty line, carried forward to its own price base.
# NBS, Poverty and Inequality in Nigeria 2019: N137,430 per person per year in
# 2018/19 prices; x2.31 composite CPI to August 2023 = N317,463.
NG_POVERTY_LINE_2019 = 137_430.0
NG_CPI_2019_TO_BASE = 2.31
NG_POVERTY_LINE = NG_POVERTY_LINE_2019 * NG_CPI_2019_TO_BASE


def fetch_ppp(country: str, year: int = 2023):
    """Private-consumption PPP conversion factor, local currency per intl $."""
    url = (f"https://api.worldbank.org/v2/country/{country}"
           f"/indicator/PA.NUS.PRVT.PP?format=json&per_page=100")
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            rows = json.load(r)[1]
        vals = {int(x["date"]): x["value"] for x in rows if x["value"] is not None}
        if year in vals:
            return vals[year], year
        latest = max(vals)
        return vals[latest], latest
    except Exception as exc:                       # offline or API change
        print(f"  PPP lookup failed for {country}: {exc}")
        return None, None


def main():
    hh = pd.read_csv(config.NIGERIA_HH)
    print(f"Nigeria households from Paper 2: {len(hh):,}")

    d = pd.DataFrame({
        "hhid": hh["hhid"],
        "weight": hh["hh_weight"],
        "stratum": hh["strata"],
        "psu": hh["cluster"],
        "n_persons": hh["hhsize"],
        "oop": hh["oop_annual"],
        "resources": hh["cons_annual"],
        "food": hh["food_annual"],
        "informal": hh["informal"],
        "insured": hh.get("insured_health", 0),
        "quintile": hh["quintile"],
        "urban": hh["urban"],
        "zone": hh["zone"],
        "any_chronic": hh.get("any_chronic", 0),
        "n_over60": hh.get("n_over60", 0),
        "n_under5": hh.get("n_under5", 0),
        "subsistence_food": hh["subsistence"],
        "ctp_food": hh["ctp"],
    })

    # ---- harmonised floor: the national poverty line, per person -----------
    d["poverty_threshold"] = NG_POVERTY_LINE * d["n_persons"]
    ctp_pov = d["resources"] - d["poverty_threshold"]
    d["ctp_poverty"] = np.where(ctp_pov > 0, ctp_pov, np.nan)

    d["burden"] = d["oop"] / d["resources"].where(d["resources"] > 0)
    d["burden_ctp"] = d["oop"] / d["ctp_poverty"]
    d["burden_ctp_food"] = d["oop"] / d["ctp_food"].where(d["ctp_food"] > 0)

    d["eqsize"] = d["n_persons"] ** config.EQ_SCALE_POWER
    d["popwt"] = d["weight"] * d["n_persons"]
    d["country"] = "Nigeria"
    d["insurance_group"] = np.where(d["insured"] == 1, "Insured", "Uninsured")
    d["sector_group"] = np.where(d["informal"] == 1, "Informal", "Formal")

    # ---- PPP, for the absolute comparison ----------------------------------
    ppp_ng, yr_ng = fetch_ppp("NGA")
    # The US dollar is the numeraire for international dollars, so the US
    # factor is 1 by construction; it is fetched only as a check and nothing
    # depends on the call succeeding.
    ppp_us, yr_us = fetch_ppp("USA")
    if ppp_us is None:
        ppp_us, yr_us = 1.0, "numeraire"
    if ppp_ng:
        print(f"  PPP Nigeria {yr_ng}: {ppp_ng:,.2f} naira per international $")
        print(f"  PPP USA     {yr_us}: {ppp_us:,.4f}")
        d["oop_ppp"] = d["oop"] / ppp_ng
        d["resources_ppp"] = d["resources"] / ppp_ng
        meta = {"ppp_ngn_per_intl_usd": ppp_ng, "ppp_year_ng": yr_ng,
                "ppp_usa": ppp_us, "ppp_year_us": yr_us,
                "ng_poverty_line_base_prices": NG_POVERTY_LINE}
        (config.DERIVED / "ppp.json").write_text(json.dumps(meta, indent=2))
    else:
        d["oop_ppp"] = np.nan
        d["resources_ppp"] = np.nan

    share_below_line = np.average((d["ctp_poverty"].isna()).to_numpy(float),
                                  weights=d["weight"])
    print(f"  households at or below the poverty line, so no capacity to pay: "
          f"{100 * share_below_line:.1f}%")
    print(f"  poverty line used: N{NG_POVERTY_LINE:,.0f} per person per year "
          f"({config.NGN_PRICE_BASE} prices)")

    out = config.DERIVED / "ng_household.csv"
    d.to_csv(out, index=False)
    print(f"\nwrote {out.relative_to(config.ROOT)}  ({len(d):,} rows)")


if __name__ == "__main__":
    main()
