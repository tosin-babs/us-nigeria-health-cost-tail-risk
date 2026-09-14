"""
Export the model payload for the public tail-risk comparison.

The page lets a reader place a household's own out-of-pocket ratio on the
American and the Nigerian burden distributions at once, and shows how the
tail-shape comparison depends on how the denominator is built. It needs each
group's quantile function, not the microdata, so that is what is exported:
burden at every percentile from 1 to 99 per group, the Nigerian curves on both
denominator constructions, the tail statistics by group, and the denominator
tests from Table 10.

Writes tool/model_data.json.
"""

from __future__ import annotations

import json
from datetime import date

import numpy as np
import pandas as pd

import config
from svy import Design
from tailrisk import GROUPS_NG, GROUPS_US, load_analysis_files, tail_stats

OUT = config.ROOT / "tool" / "model_data.json"
GRID = list(range(1, 100))


def curves(df, groups, design, col):
    b = df[col].to_numpy(float)
    out = {}
    for label, spec in groups:
        mask = (np.ones(len(df), bool) if spec is None
                else (df[spec[0]] == spec[1]).to_numpy())
        if mask.sum() < 100:
            continue
        sub = design.subset(mask)
        q = [float(sub.quantile(b, [p / 100.0])[0]) for p in GRID]
        st = tail_stats(b[mask], df["weight"].to_numpy(float)[mask])
        out[label] = {"q": [round(100 * v, 4) for v in q],
                      "n": int(mask.sum()),
                      "var95": round(100 * st["var95"], 3),
                      "cvar95": round(100 * st["cvar95"], 3),
                      "cvar99": round(100 * st["cvar99"], 3),
                      "xi": round(float(st["xi"]), 4)}
    return out


def main():
    us, ng = load_analysis_files()
    ng = ng[np.isfinite(ng["burden_net"])].copy()
    d_us = Design(us, "weight", "stratum", "psu")
    d_ng = Design(ng, "weight", "stratum", "psu")

    t10 = pd.read_csv(config.TABLES / "table10_denominator_tests.csv")
    tests = []
    for _, r in t10.iterrows():
        tests.append({"key": r["construction"], "label": r["label"],
                      "unit": r["unit"],
                      "us_xi": round(float(r["us_xi"]), 4),
                      "us_lo": round(float(r["us_xi_lo"]), 4),
                      "us_hi": round(float(r["us_xi_hi"]), 4),
                      "ng_xi": round(float(r["ng_xi"]), 4),
                      "ng_lo": round(float(r["ng_xi_lo"]), 4),
                      "ng_hi": round(float(r["ng_xi_hi"]), 4),
                      "p": round(float(r["xi_diff_p"]), 4),
                      "us_cvar95": round(100 * float(r["us_cvar95"]), 2)
                      if r["unit"] == "ratio" else None,
                      "ng_cvar95": round(100 * float(r["ng_cvar95"]), 2)
                      if r["unit"] == "ratio" else None})

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
                                "income in the United States. For Nigeria the "
                                "matched construction divides by consumption "
                                "net of out-of-pocket spending; the SDG basis "
                                "divides by consumption including it, which "
                                "bounds the ratio below one.",
        },
        "grid": GRID,
        "us": curves(us, GROUPS_US, d_us, "burden"),
        "ng": curves(ng, GROUPS_NG, d_ng, "burden_net"),
        "ng_published": curves(ng, GROUPS_NG, d_ng, "burden"),
        "tests": tests,
        "headline": headline,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"wrote {OUT.relative_to(config.ROOT)} "
          f"({OUT.stat().st_size / 1024:,.0f} KB)")
    print("\n  reference values the page must reproduce:")
    print(f"    US  all families      q99  {payload['us']['All families']['q'][98]:6.2f}%")
    print(f"    NG  all households    q99  {payload['ng']['All households']['q'][98]:6.2f}%  (net basis)")
    print(f"    NG  all households    q99  {payload['ng_published']['All households']['q'][98]:6.2f}%  (published basis)")
    for t in tests:
        if t["key"] in ("published", "net"):
            print(f"    xi {t['key']:<10} US {t['us_xi']:+.3f}  NG {t['ng_xi']:+.3f}  p={t['p']:.3f}")


if __name__ == "__main__":
    main()
