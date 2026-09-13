"""
Export the model payload for the public tail-risk comparison.

The paper's argument is about the shape of two distributions, which is hard to
convey in a sentence and easy to convey by letting someone put themselves on
them. The page needs the full burden distribution for each group in each
country, at enough resolution to place a user's own ratio.

Shipping the microdata would be both a disclosure problem and unnecessary.
What the page actually needs is each group's quantile function, so that is
what is exported: burden at every percentile from 1 to 99, per group, plus the
tail statistics the paper reports.

Writes tool/model_data.json.
"""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

import config
from svy import Design

OUT = config.ROOT / "tool" / "model_data.json"
GRID = list(range(1, 100))

US_GROUPS = [
    ("All families", None),
    ("Insured all year", ("insurance_group", "Insured all year")),
    ("Partly uninsured", ("insurance_group", "Partly uninsured")),
    ("Uninsured all year", ("insurance_group", "Uninsured all year")),
    ("Poor or near poor", ("_povcat_low", 1)),
    ("Chronic condition", ("any_chronic", 1)),
    ("Elderly member", ("_elderly", 1)),
]
NG_GROUPS = [
    ("All households", None),
    ("Informal sector", ("sector_group", "Informal")),
    ("Formal sector", ("sector_group", "Formal")),
    ("Poorest quintile", ("quintile", 1)),
    ("Richest quintile", ("quintile", 5)),
    ("Rural", ("urban", 0)),
]


def curves(df, groups, design):
    b = df["burden"].to_numpy(float)
    out = {}
    for label, spec in groups:
        mask = (np.ones(len(df), bool) if spec is None
                else (df[spec[0]] == spec[1]).to_numpy())
        if mask.sum() < 100:
            continue
        sub = design.subset(mask)
        q = [float(sub.quantile(b, [p / 100.0])[0]) for p in GRID]
        out[label] = {"q": [round(100 * v, 4) for v in q],
                      "n": int(mask.sum())}
    return out


def main():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")

    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    us["burden"] = us["oop"] / us["faminc"]
    us["_povcat_low"] = us["povcat"].isin([1, 2]).astype(int)
    us["_elderly"] = (us["n_over64"] > 0).astype(int)
    us = us[np.isfinite(us["burden"])].copy()
    ng = ng[np.isfinite(ng["burden"])].copy()

    d_us = Design(us, "weight", "stratum", "psu")
    d_ng = Design(ng, "weight", "stratum", "psu")

    tail = pd.read_csv(config.TABLES / "table4_tail_risk.csv")
    tail_by = {}
    for _, r in tail.iterrows():
        tail_by.setdefault(r["country"], {})[r["group"]] = {
            "var95": round(100 * r["var95"], 3),
            "cvar95": round(100 * r["cvar95"], 3),
            "cvar99": round(100 * r["cvar99"], 3),
            "xi": round(float(r["xi"]), 4),
            "xi_lo": (None if pd.isna(r.get("xi_lo"))
                      else round(float(r["xi_lo"]), 4)),
            "xi_hi": (None if pd.isna(r.get("xi_hi"))
                      else round(float(r["xi_hi"]), 4)),
        }

    che = pd.read_csv(config.TABLES / "table1_che_harmonised.csv")
    che = che[che["dimension"] == "Overall"]
    headline = {}
    for _, r in che.iterrows():
        headline.setdefault(r["country"], {})[r["measure"]] = \
            round(float(r["estimate_pct"]), 2)

    payload = {
        "meta": {
            "us_source": "MEPS Full-Year Consolidated files, 2019-2024 pooled, "
                         "2024 dollars",
            "ng_source": "Nigeria General Household Survey-Panel wave 5 "
                         "(2023/24)",
            "us_n": int(len(us)), "ng_n": int(len(ng)),
            "generated": date.today().isoformat(),
            "denominator_note": "Burden is out-of-pocket spending over family "
                                "income in the United States and over household "
                                "consumption in Nigeria. The two denominators "
                                "are different variables; this is a comparison "
                                "of relative burden, not of welfare.",
        },
        "grid": GRID,
        "us": curves(us, US_GROUPS, d_us),
        "ng": curves(ng, NG_GROUPS, d_ng),
        "tail": tail_by,
        "headline": headline,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"wrote {OUT.relative_to(config.ROOT)} "
          f"({OUT.stat().st_size / 1024:,.0f} KB)")
    print(f"  {len(payload['us'])} US groups, {len(payload['ng'])} Nigerian "
          f"groups, {len(GRID)} percentiles each")

    # ---- the page must reproduce the paper -------------------------------
    print("\n  reference values the page must reproduce:")
    for c, g, p in (("us", "All families", 99), ("ng", "All households", 99),
                    ("us", "Poor or near poor", 95)):
        v = payload[c][g]["q"][p - 1]
        print(f"    {c.upper():<3} {g:<20} q{p}  {v:6.2f}%")
    print(f"    US  all families      xi   {payload['tail']['United States']['All families']['xi']:+.3f}")
    print(f"    NG  all households    xi   {payload['tail']['Nigeria']['All households']['xi']:+.3f}")


if __name__ == "__main__":
    main()
