"""
Check that the manuscript's headline numbers still match the analysis output.

The prose is written by hand, so a rerun that moves an estimate leaves the text
stale unless someone notices. This reads the current tables, formats each
headline figure the way the manuscript writes it, and fails if the string is
absent. It also checks that every table cited in the prose is rendered and
every rendered table is cited, that no em dash appears, and that the body and
abstract are within the length limits.

Run after run_all.py and before make_manuscript.py.
"""

from __future__ import annotations

import re
import sys

import pandas as pd

import config

MS = config.ROOT / "manuscript" / "Paper3_manuscript.md"
T = config.TABLES
BODY_WORD_LIMIT = 6_200
ABSTRACT_WORD_LIMIT = 250


def load():
    US, NG = "United States", "Nigeria"
    t1 = pd.read_csv(T / "table1_che_harmonised.csv")
    ov = t1[t1["dimension"] == "Overall"].set_index(["country", "measure"])
    t2 = pd.read_csv(T / "table2_burden_quantiles.csv").set_index("quantile")
    t4 = pd.read_csv(T / "table4_tail_risk.csv").set_index(["country", "basis", "group"])
    t6 = pd.read_csv(T / "table6_parity.csv")
    inf = t6[(t6["nigeria_reference"] == "Nigerian informal households")]
    inf = inf.set_index(["basis", "us_group", "reference_quantile"])
    t6b = pd.read_csv(T / "table6b_crossover.csv")
    t6b = t6b[t6b["nigeria_reference"] == "Nigerian informal households"]
    t6b = t6b.set_index(["basis", "us_group"])
    t7 = pd.read_csv(T / "table7_rif.csv").set_index(["country", "quantile", "term"])
    t8 = pd.read_csv(T / "table8_ppp_absolute.csv").set_index("country")
    t9 = pd.read_csv(T / "table9_robustness.csv").set_index(["variant", "country"])
    t9c = pd.read_csv(T / "table9c_rif_poverty_basis.csv").set_index(["basis", "quantile"])
    t10 = pd.read_csv(T / "table10_denominator_tests.csv").set_index("construction")
    t12 = pd.read_csv(T / "table12_gpd_diagnostics.csv").set_index(["construction", "country"])
    t13 = pd.read_csv(T / "table13_access_debt.csv").set_index(["country", "measure", "group"])
    t1c = pd.read_csv(T / "table1c_underinsurance.csv").set_index("group")

    NET, SDG = "consumption net of OOP", "consumption (SDG basis)"
    pct1 = lambda x: f"{x:.1f}%"
    xi = lambda x: f"{x:+.3f}"

    checks = {
        "CHE 10%, US": pct1(ov.loc[(US, "Budget share > 10%"), "estimate_pct"]),
        "CHE 10%, Nigeria": pct1(ov.loc[(NG, "Budget share > 10%"), "estimate_pct"]),
        "CHE 10% ratio": f'{ov.loc[(NG, "Budget share > 10%"), "estimate_pct"] / ov.loc[(US, "Budget share > 10%"), "estimate_pct"]:.1f} times',
        "CTP 40%, US": pct1(ov.loc[(US, "Capacity to pay >= 40%"), "estimate_pct"]),
        "CTP 40%, Nigeria": pct1(ov.loc[(NG, "Capacity to pay >= 40%"), "estimate_pct"]),
        "no capacity, Nigeria": pct1(ov.loc[(NG, "No capacity to pay (at or below the floor)"), "estimate_pct"]),
        "no capacity, US": pct1(ov.loc[(US, "No capacity to pay (at or below the floor)"), "estimate_pct"]),
        "food-share floor, Nigeria CTP": pct1(t9.loc[("Nigeria: food-share floor", NG), "ctp40_pct"]),
        "q99 burden, US": pct1(t2.loc[0.99, "us_burden_pct"]),
        "q99 burden, Nigeria SDG": pct1(t2.loc[0.99, "nigeria_burden_pct"]),
        "q99 burden, Nigeria net": pct1(t2.loc[0.99, "nigeria_net_pct"]),
        "q99 burden, US gross": pct1(t2.loc[0.99, "us_gross_pct"]),
        "q95 burden, Nigeria net": pct1(t2.loc[0.95, "nigeria_net_pct"]),
        "xi, US all": xi(t4.loc[(US, "income", "All families"), "xi"]),
        "xi, Nigeria SDG": xi(t4.loc[(NG, SDG, "All households"), "xi"]),
        "xi, Nigeria net": xi(t4.loc[(NG, NET, "All households"), "xi"]),
        "xi US insured": xi(t4.loc[(US, "income", "Insured all year"), "xi"]),
        "xi diff net p": f'p = {t10.loc["net", "xi_diff_p"]:.2f}',
        "xi floor US": xi(t10.loc["floor", "us_xi"]),
        "xi floor NG": xi(t10.loc["floor", "ng_xi"]),
        "xi two-year US": xi(t10.loc["two_year", "us_xi"]),
        "xi levels hh US": xi(t10.loc["levels_household", "us_xi"]),
        "xi levels hh NG": xi(t10.loc["levels_household", "ng_xi"]),
        "xi levels pp US": xi(t10.loc["levels_person", "us_xi"]),
        "xi gross US": xi(t10.loc["gross", "us_xi"]),
        "KS US published": f'{t12.loc[("published", "us"), "ks"]:.3f}',
        "KS NG net": f'{t12.loc[("net", "ng"), "ks"]:.3f}',
        "CVaR95, US all": pct1(100 * t4.loc[(US, "income", "All families"), "cvar95"]),
        "CVaR95, Nigeria SDG": pct1(100 * t4.loc[(NG, SDG, "All households"), "cvar95"]),
        "CVaR95, Nigeria net": pct1(100 * t4.loc[(NG, NET, "All households"), "cvar95"]),
        "CVaR95, US gross": pct1(100 * t10.loc["gross", "us_cvar95"]),
        "CVaR95, US poor": pct1(100 * t4.loc[(US, "income", "Poor or near poor"), "cvar95"]),
        "CVaR95, US poor two-year": pct1(100 * t10.loc["poor_two_year", "us_cvar95"]),
        "CVaR95, US poor one-year linked": pct1(100 * t10.loc["poor_one_year", "us_cvar95"]),
        "RIF poverty q95, US": f'{t7.loc[(US, 0.95, "Below the poverty line"), "coef_pp"]:.2f}',
        "RIF poverty q95, Nigeria": f'{t7.loc[(NG, 0.95, "Below the poverty line"), "coef_pp"]:.2f}',
        "RIF poverty q95, Nigeria gross": f'{t9c.loc[("Nigeria, gross consumption", 0.95), "coef_pp"]:.2f}',
        "RIF chronic q95, Nigeria": f'{t7.loc[(NG, 0.95, "Any chronic condition"), "coef_pp"]:.1f}',
        "parity, all US vs NG median": pct1(inf.loc[("published", "All US families", 0.50), "us_share_above_pct"]),
        "parity, elderly vs NG median": pct1(inf.loc[("published", "Elderly member", 0.50), "us_share_above_pct"]),
        "crossover, poor US, SDG": f'{t6b.loc[("published", "Poor or near poor"), "crossover_percentile"]:.0f}th',
        "crossover, poor US, net": f'{t6b.loc[("net", "Poor or near poor"), "crossover_percentile"]:.1f}th',
        "share > income, linked one-year": f'{100 * t10.loc["linked_one_year", "us_share_above_1"]:.2f}%',
        "share > income, two-year": f'{100 * t10.loc["two_year", "us_share_above_1"]:.2f}%',
        "log income correlation": f'{t10["us_log_income_corr_adjacent_years"].iloc[0]:.2f}',
        "RIF 60+ q95, US": f'{t7.loc[(US, 0.95, "Any member aged 60+"), "coef_pp"]:.1f} points',
        "RIF 60+ q95, Nigeria": f'{t7.loc[(NG, 0.95, "Any member aged 60+"), "coef_pp"]:.1f} in Nigeria',
        "parity net informal median": f'{inf.loc[("net", "All US families", 0.50), "reference_burden_pct"]:.2f}% net',
        "parity net informal q90": f'{inf.loc[("net", "All US families", 0.90), "reference_burden_pct"]:.1f}% net',
        "cost barrier, US all": pct1(t13.loc[(US, "Cost barrier to care", "All families"), "estimate_pct"]),
        "medical debt, burden >= 100%": pct1(t13.loc[(US, "Any medical debt (2024)", "100% or more"), "estimate_pct"]),
        "NG ill consulted no one": pct1(t13.loc[(NG, "Ill, consulted no one", "All"), "estimate_pct"]),
        "NG no consult cost, Q1": pct1(t13.loc[(NG, "Ill, consulted no one because of cost", "Q1 (poorest)"), "estimate_pct"]),
        "NG no consult cost, Q5": pct1(t13.loc[(NG, "Ill, consulted no one because of cost", "Q5 (richest)"), "estimate_pct"]),
        "underinsured": pct1(t1c.loc["All families insured all year", "estimate_pct"]),
        "PPP mean OOP p.p., US": f'${t8.loc[US, "mean_oop_per_person"]:,.0f}',
        "PPP mean OOP p.p., Nigeria": f'${t8.loc[NG, "mean_oop_per_person"]:,.0f}',
    }
    return checks


def cross_reference():
    """Every table cited in the prose is rendered, and vice versa."""
    tb = config.ROOT / "manuscript" / "tables.md"
    if not tb.exists():
        print("  tables.md not built yet; skipping the cross-reference check")
        return []
    rendered = set(re.findall(r"\*\*Table ([0-9A-Za-z]+)\.\*\*", tb.read_text()))
    cited = set()
    for m in re.finditer(r"Tables? ([0-9]+[a-f]?|A[0-9]+)"
                         r"(?:\s+and\s+([0-9]+[a-f]?|A[0-9]+))?", MS.read_text()):
        cited.add(m.group(1))
        if m.group(2):
            cited.add(m.group(2))
    problems = []
    for t in sorted(cited - rendered):
        problems.append(f"Table {t} is cited in the prose but not rendered")
    for t in sorted(rendered - cited):
        problems.append(f"Table {t} is rendered but never cited")
    print(f"  {len(rendered)} tables rendered, {len(cited)} cited"
          + ("" if not problems else f"  <-- {len(problems)} mismatch(es)"))
    for p_ in problems:
        print(f"      {p_}")
    return problems


def style(text):
    """Em dashes, spaced en dashes and the word limits."""
    problems = []
    if "—" in text:
        problems.append(f"{text.count('—')} em dash(es) in the manuscript")
    if re.search(r"\s–\s", text):
        problems.append("spaced en dash used as punctuation")
    tb = config.ROOT / "manuscript" / "tables.md"
    if tb.exists() and "—" in tb.read_text():
        problems.append("em dash in tables.md")
    body = text[text.index("## 1. Introduction"):text.index("## Declarations")]
    body = re.sub(r"!\[\]\([^)]*\)", "", body)
    body = re.sub(r"\*\*Figure \d+\.\*\*[^\n]*", "", body)
    n_body = len(body.split())
    abstract = text[text.index("## Abstract"):text.index("**Keywords")]
    n_abs = len(abstract.split()) - 1
    print(f"  body {n_body:,} words (limit {BODY_WORD_LIMIT:,}); "
          f"abstract {n_abs} words (limit {ABSTRACT_WORD_LIMIT})")
    if n_body > BODY_WORD_LIMIT:
        problems.append("body exceeds the word limit")
    if n_abs > ABSTRACT_WORD_LIMIT:
        problems.append("abstract exceeds the word limit")
    return problems


def main():
    raw = MS.read_text()
    text = raw.replace("−", "-").replace("**", "")
    checks = load()
    bad = [(k, v) for k, v in checks.items() if v.replace("−", "-") not in text]
    width = max(len(k) for k in checks)
    for k, v in checks.items():
        print(f"  {'ok ' if (k, v) not in bad else 'MISSING'}  {k:<{width}}  {v}")
    xref = cross_reference()
    sty = style(raw)
    for p_ in sty:
        print(f"      {p_}")
    if bad or xref or sty:
        if bad:
            print(f"\n{len(bad)} headline figure(s) do not appear in "
                  f"{MS.name}. Update the prose, then rebuild.")
        if xref:
            print(f"{len(xref)} table cross-reference problem(s).")
        if sty:
            print(f"{len(sty)} style problem(s).")
        sys.exit(1)
    print(f"\nAll {len(checks)} headline figures match the current tables.")


if __name__ == "__main__":
    main()
