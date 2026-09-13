"""
Check that the manuscript's headline numbers still match the analysis output.

The prose is written by hand, so a rerun that moves an estimate leaves the text
stale unless someone notices. This reads the current tables, formats each
headline figure the way the manuscript writes it, and fails if the string is
absent. It is a spelling check against the data, not a proof that every
sentence is right, but it catches the failure that actually happens.

Run after run_all.py and before make_manuscript.py.
"""

from __future__ import annotations

import sys

import pandas as pd

import config

MS = config.ROOT / "manuscript" / "Paper3_manuscript.md"
T = config.TABLES


def load():
    t1 = pd.read_csv(T / "table1_che_harmonised.csv")
    ov = t1[t1["dimension"] == "Overall"].set_index(["country", "measure"])
    t2 = pd.read_csv(T / "table2_burden_quantiles.csv").set_index("quantile")
    t4 = pd.read_csv(T / "table4_tail_risk.csv").set_index(["country", "group"])
    t6 = pd.read_csv(T / "table6_parity.csv")
    inf = t6[t6["nigeria_reference"] == "Nigerian informal households"]
    inf = inf.set_index(["us_group", "reference_quantile"])
    t6b = pd.read_csv(T / "table6b_crossover.csv")
    t6b = t6b[t6b["nigeria_reference"] == "Nigerian informal households"]
    t6b = t6b.set_index("us_group")
    t7 = pd.read_csv(T / "table7_rif.csv")
    t7 = t7.set_index(["country", "quantile", "term"])
    t8 = pd.read_csv(T / "table8_ppp_absolute.csv").set_index("country")
    t9 = pd.read_csv(T / "table9_robustness.csv")
    t9 = t9.set_index(["variant", "country"])

    US, NG = "United States", "Nigeria"
    checks = {
        "CHE 10%, US": f'{ov.loc[(US, "Budget share > 10%"), "estimate_pct"]:.1f}%',
        "CHE 10%, Nigeria": f'{ov.loc[(NG, "Budget share > 10%"), "estimate_pct"]:.1f}%',
        "CTP 40%, US": f'{ov.loc[(US, "Capacity to pay >= 40%"), "estimate_pct"]:.1f}%',
        "CTP 40%, Nigeria": f'{ov.loc[(NG, "Capacity to pay >= 40%"), "estimate_pct"]:.1f}%',
        "no capacity, Nigeria":
            f'{ov.loc[(NG, "No capacity to pay (at or below the floor)"), "estimate_pct"]:.1f}%',
        "no capacity, US":
            f'{ov.loc[(US, "No capacity to pay (at or below the floor)"), "estimate_pct"]:.1f}%',
        "q99 burden, US": f'{t2.loc[0.99, "us_burden_pct"]:.2f}%',
        "q99 burden, Nigeria": f'{t2.loc[0.99, "nigeria_burden_pct"]:.2f}%',
        "xi, US all": f'{t4.loc[(US, "All families"), "xi"]:+.3f}'.replace("+", "+"),
        "xi, Nigeria all": f'{t4.loc[(NG, "All households"), "xi"]:+.3f}',
        "CVaR95, US all": f'{100 * t4.loc[(US, "All families"), "cvar95"]:.1f}%',
        "CVaR95, Nigeria all": f'{100 * t4.loc[(NG, "All households"), "cvar95"]:.1f}%',
        "CVaR95, US poor": f'{100 * t4.loc[(US, "Poor or near poor"), "cvar95"]:.1f}%',
        "parity, all US vs NG median":
            f'{inf.loc[("All US families", 0.50), "us_share_above_pct"]:.1f}%',
        "parity, elderly vs NG median":
            f'{inf.loc[("Elderly member", 0.50), "us_share_above_pct"]:.1f}%',
        "RIF poverty q95, US":
            f'{t7.loc[("United States", 0.95, "Below the poverty line"), "coef_pp"]:.2f}',
        "RIF poverty q95, Nigeria":
            f'{t7.loc[("Nigeria", 0.95, "Below the poverty line"), "coef_pp"]:.2f}'.lstrip("-"),
        "PPP mean OOP p.p., US":
            f'${t8.loc[US, "mean_oop_per_person"]:,.0f}',
        "PPP mean OOP p.p., Nigeria":
            f'${t8.loc[NG, "mean_oop_per_person"]:,.0f}',
        "food-share floor, Nigeria CTP":
            f'{t9.loc[("Nigeria: food-share floor", NG), "ctp40_pct"]:.1f}%',
        "crossover, poor US":
            f'{t6b.loc["Poor or near poor", "crossover_percentile"]:.0f}th',
    }
    return checks


def main():
    text = MS.read_text().replace("−", "-").replace("**", "")
    checks = load()
    bad = [(k, v) for k, v in checks.items() if v.replace("−", "-") not in text]
    width = max(len(k) for k in checks)
    for k, v in checks.items():
        print(f"  {'ok ' if (k, v) not in bad else 'MISSING'}  {k:<{width}}  {v}")
    if bad:
        print(f"\n{len(bad)} headline figure(s) do not appear in {MS.name}. "
              f"Update the prose, then rebuild the documents.")
        sys.exit(1)
    print(f"\nAll {len(checks)} headline figures match the current tables.")


if __name__ == "__main__":
    main()
