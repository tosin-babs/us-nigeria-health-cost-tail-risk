"""
Render the manuscript's tables from the analysis CSVs.

The prose cites table numbers; the tables themselves are machine-written into
output/tables. This turns those into formatted markdown so the submitted
document and the analysis output cannot drift apart.

Writes manuscript/tables.md.
"""

from __future__ import annotations

import pandas as pd

import config

OUT = config.ROOT / "manuscript" / "tables.md"
T = config.TABLES


def num(x, d=2):
    return "" if pd.isna(x) else f"{x:,.{d}f}"


def auto(d=2):
    def f(x):
        if pd.isna(x):
            return ""
        return f"{x:,.{d}f}" if isinstance(x, (int, float)) else str(x)
    return f


def signed(d=3):
    return lambda x: "" if pd.isna(x) else f"{x:+.{d}f}"


def pct_of(d=2):
    return lambda x: num(100 * x, d)


def pval(x):
    if pd.isna(x):
        return ""
    return "< 0.001" if x < 0.001 else f"{x:.3f}"


def render(df, cols, fmts, headers=None):
    out = pd.DataFrame({c: df[c].map(f) if f else df[c].astype(str)
                        for c, f in zip(cols, fmts)})
    out.columns = headers or cols
    align = ["---" if i == 0 else "---:" for i in range(len(out.columns))]
    lines = ["| " + " | ".join(out.columns) + " |",
             "|" + "|".join(align) + "|"]
    for _, r in out.iterrows():
        lines.append("| " + " | ".join(str(v) for v in r) + " |")
    return "\n".join(lines)


def caption(n, title, note=None):
    s = f"\n**Table {n}.** {title}\n"
    if note:
        s += f"\n*{note}*\n"
    return s


NG_NET = "consumption net of OOP"
NG_SDG = "consumption (SDG basis)"


def main():
    parts = ["# Tables\n",
             "*Generated from `output/tables/*.csv` by `python/make_tables.py`. "
             "All estimates are survey-weighted with Taylor-linearized standard "
             "errors for a stratified single-stage cluster design. US amounts "
             f"are in constant {config.BASE_YEAR} dollars; Nigerian amounts in "
             f"constant {config.NGN_PRICE_BASE} naira. Burden is out-of-pocket "
             "(OOP) spending over family income in the United States. For "
             "Nigeria the published (SDG) basis divides by household "
             "consumption, which contains OOP; the matched basis divides by "
             "consumption net of OOP. Each table states which is used.*\n"]

    # ---- Table 1: CHE overall --------------------------------------------
    t1 = pd.read_csv(T / "table1_che_harmonised.csv")
    ov = t1[t1["dimension"] == "Overall"]
    parts += [caption(1, "Catastrophic spending on harmonized definitions.",
                      "Budget share is OOP over income (US) or over consumption "
                      "on the SDG basis (Nigeria). Capacity to pay is resources "
                      "net of the national poverty threshold; a household at or "
                      "below the threshold is counted as catastrophic whenever "
                      "it spends anything."),
              render(ov, ["country", "measure", "estimate_pct", "se_pct",
                          "ci_low", "ci_high", "n"],
                     [None, None, auto(2), auto(2), auto(2), auto(2), auto(0)],
                     ["Country", "Measure", "Estimate %", "SE", "95% low",
                      "95% high", "n"])]

    # ---- Table 2: quantiles ------------------------------------------------
    t2 = pd.read_csv(T / "table2_burden_quantiles.csv")
    parts += [caption(2, "The burden distribution by quantile, on the published "
                         "and the matched constructions of the denominator.",
                      "Published: US OOP over income, Nigeria OOP over "
                      "consumption (SDG basis). Matched net: both over resources "
                      "excluding OOP, so the US column is unchanged and the "
                      "Nigerian one is OOP over consumption net of OOP. Matched "
                      "gross: both over resources including OOP, so the US "
                      "column becomes OOP over income plus OOP and the Nigerian "
                      "one is unchanged."),
              render(t2, ["quantile", "us_burden_pct", "nigeria_burden_pct",
                          "ratio_ng_to_us", "nigeria_net_pct", "us_gross_pct"],
                     [lambda x: f"q{int(100 * x)}", auto(2), auto(2), auto(2),
                      auto(2), auto(2)],
                     ["Quantile", "US, published %", "Nigeria, published %",
                      "Ratio NG / US", "Nigeria, net of OOP %",
                      "US, income plus OOP %"])]

    # ---- Table 3: tail measures by group (matched basis) -------------------
    t4 = pd.read_csv(T / "table4_tail_risk.csv")
    main_rows = t4[t4["basis"].isin(["income", NG_NET])]
    parts += [caption(3, "Tail-risk measures of the out-of-pocket burden by "
                         "group, matched net construction.",
                      "US burden is OOP over family income; Nigerian burden is "
                      "OOP over consumption net of OOP. VaR is the quantile of "
                      "the burden distribution; CVaR is the mean burden at or "
                      "above it. xi is the generalized Pareto shape fitted by "
                      "weighted maximum likelihood to exceedances over the 90th "
                      "percentile, with 95% intervals from a Rao-Wu bootstrap "
                      "over primary sampling units within strata. xi above 0.5 "
                      "implies infinite variance. The same Nigerian groups on "
                      "the SDG basis are in Table A4."),
              render(main_rows, ["country", "group", "n", "n_exceedances",
                                 "var95", "cvar95", "cvar95_lo", "cvar95_hi",
                                 "cvar99", "xi", "xi_lo", "xi_hi"],
                     [None, None, auto(0), auto(0), pct_of(2), pct_of(2),
                      pct_of(2), pct_of(2), pct_of(2), signed(), signed(),
                      signed()],
                     ["Country", "Group", "n", "Exceedances", "VaR95 %",
                      "CVaR95 %", "95% low", "95% high", "CVaR99 %",
                      "xi", "xi low", "xi high"])]

    # ---- Table 4: denominator tests ---------------------------------------
    t10 = pd.read_csv(T / "table10_denominator_tests.csv")
    parts += [caption(4, "The US-Nigeria difference in tail shape under each "
                         "construction of the denominator.",
                      "xi is the generalized Pareto shape above the 90th "
                      "percentile with 95% Rao-Wu bootstrap intervals. The "
                      "difference is US minus Nigeria, its interval from "
                      "independently drawn replicates, and p from a Wald test "
                      "on the two bootstrap standard errors. CVaR95 is in "
                      "percent of resources for ratio constructions and in 2023 "
                      "international dollars for levels. Thresholds other than "
                      "the 90th percentile are in Table A12."),
              render(t10, ["label", "us_n", "ng_n", "us_xi", "us_xi_lo",
                           "us_xi_hi", "ng_xi", "ng_xi_lo", "ng_xi_hi",
                           "xi_diff", "xi_diff_lo", "xi_diff_hi", "xi_diff_p",
                           "us_cvar95", "ng_cvar95", "us_share_above_1"],
                     [None, auto(0), auto(0), signed(), signed(), signed(),
                      signed(), signed(), signed(), signed(), signed(),
                      signed(), pval,
                      lambda x: num(x, 0) if x > 5 else num(100 * x, 1),
                      lambda x: num(x, 0) if x > 5 else num(100 * x, 1),
                      lambda x: num(100 * x, 2)],
                     ["Construction", "US n", "NG n", "US xi", "low", "high",
                      "NG xi", "low", "high", "Difference", "low", "high",
                      "p", "US CVaR95", "NG CVaR95", "US share > 100% of resources"])]

    # ---- Table 5: access and debt ----------------------------------------
    t13 = pd.read_csv(T / "table13_access_debt.csv")
    parts += [caption(5, "Cost barriers to care, medical debt and forgone care.",
                      "United States: families in which any member delayed or "
                      "went without medical care or prescription medicines "
                      "because of cost (MEPS round 4/2), and families with any "
                      "medical debt (asked in 2024 only). Nigeria: persons ill "
                      "or injured in the last four weeks who consulted no one, "
                      "those who gave cost as the reason, and households with "
                      "an ill member and no out-of-pocket spending, by quintile "
                      "of per-capita consumption net of OOP."),
              render(t13, ["country", "measure", "dimension", "group",
                           "estimate_pct", "se_pct", "n"],
                     [None, None, None, None, auto(2), auto(2), auto(0)],
                     ["Country", "Measure", "Dimension", "Group", "Estimate %",
                      "SE", "n"])]

    # ---- Table 6: RIF -----------------------------------------------------
    t7 = pd.read_csv(T / "table7_rif.csv")
    t7 = t7[t7["term"] != "(intercept)"].copy()
    t7["sig"] = t7["t"].abs().gt(1.96).map({True: "*", False: ""})
    parts += [caption(6, "Unconditional quantile regression of burden.",
                      "Firpo, Fortin and Lemieux (2009). The coefficient is the "
                      "effect on that percentile of the population burden "
                      "distribution, in percentage points of resources. US "
                      "burden is OOP over income; Nigerian burden is OOP over "
                      "consumption net of OOP, and Nigerian poverty position "
                      "is measured on the same net consumption. Standard errors "
                      "are clustered on the stratum-PSU pair; * marks |t| > "
                      "1.96."),
              render(t7, ["country", "quantile", "term", "coef_pp", "se_pp",
                          "t", "sig"],
                     [None, lambda x: f"q{int(100 * x)}", None, auto(2),
                      auto(2), auto(2), None],
                     ["Country", "Quantile", "Term", "Coefficient (pp)", "SE",
                      "t", ""])]

    # ---- Table 7: parity --------------------------------------------------
    t6 = pd.read_csv(T / "table6_parity.csv")
    inf = t6[t6["nigeria_reference"] == "Nigerian informal households"].copy()
    inf["basis"] = inf["basis"].map({"published": "SDG", "net": "net of OOP"})
    parts += [caption(7, "US families whose burden exceeds that of the Nigerian "
                         "informal household at its median, upper quartile and "
                         "90th percentile.",
                      "The reference is the Nigerian informal household at the "
                      "stated quantile of its own burden distribution, on the "
                      "SDG basis and on consumption net of OOP. The parity "
                      "percentile is the point in the US group's distribution "
                      "at which the reference burden is reached."),
              render(inf, ["basis", "us_group", "reference_quantile",
                           "reference_burden_pct", "us_share_above_pct",
                           "us_parity_percentile", "n"],
                     [None, None, lambda x: f"q{int(100 * x)}", auto(2),
                      auto(2), auto(1), auto(0)],
                     ["Nigerian basis", "US group", "Reference quantile",
                      "Reference burden %", "US share above %",
                      "US parity percentile", "n"])]

    # ---- Table 8: robustness ---------------------------------------------
    t9 = pd.read_csv(T / "table9_robustness.csv")
    parts += [caption(8, "Robustness: the comparison under sixteen variants.",
                      "Each row reruns the whole comparison under one change. "
                      "Variants that alter the denominator construction or the "
                      "Nigerian out-of-pocket instrument are the ones that move "
                      "the tail columns. Table A8 records which orderings hold."),
              render(t9, ["variant", "country", "n", "che10_pct", "ctp40_pct",
                          "var95_pct", "cvar95_pct", "xi"],
                     [None, None, auto(0), auto(2), auto(2), auto(2), auto(2),
                      signed()],
                     ["Variant", "Country", "n", "CHE10 %", "CTP40 %",
                      "VaR95 %", "CVaR95 %", "xi"])]

    # ---- Appendix ----------------------------------------------------------
    parts += ["\n\n# Appendix tables\n"]

    sub = t1[t1["dimension"] != "Overall"]
    parts += [caption("A1", "Catastrophic spending by subgroup."),
              render(sub, ["country", "dimension", "group", "measure",
                           "estimate_pct", "se_pct", "n"],
                     [None, None, None, None, auto(2), auto(2), auto(0)],
                     ["Country", "Dimension", "Group", "Measure", "Estimate %",
                      "SE", "n"])]

    t1c = pd.read_csv(T / "table1c_underinsurance.csv")
    parts += [caption("A2", "Underinsurance among US families insured all year.",
                      "Adapted from the Commonwealth Fund definition: OOP at or "
                      "above 10% of income, or at or above 5% for families "
                      "below 200% of poverty. The deductible criterion is not "
                      "applied, so the rate is a lower bound."),
              render(t1c, ["group", "estimate_pct", "se_pct", "ci_low",
                           "ci_high", "n"],
                     [None, auto(2), auto(2), auto(2), auto(2), auto(0)],
                     ["Group", "Estimate %", "SE", "95% low", "95% high", "n"])]

    t3 = pd.read_csv(T / "table3_burden_by_group.csv")
    parts += [caption("A3", "Burden quantiles by group, published basis."),
              render(t3, ["group", "country", "n", "q50", "q75", "q90", "q95",
                          "q99"],
                     [None, None, auto(0), auto(2), auto(2), auto(2), auto(2),
                      auto(2)],
                     ["Group", "Country", "n", "q50 %", "q75 %", "q90 %",
                      "q95 %", "q99 %"])]

    sdg_rows = t4[t4["basis"] == NG_SDG]
    parts += [caption("A4", "Tail-risk measures for Nigerian groups on the SDG "
                            "basis (OOP over consumption including OOP).",
                      "The ratio cannot exceed one on this basis, so the fitted "
                      "shape tends toward zero or below at high thresholds."),
              render(sdg_rows, ["group", "n", "n_exceedances", "var95",
                                "cvar95", "cvar95_lo", "cvar95_hi", "cvar99",
                                "xi", "xi_lo", "xi_hi"],
                     [None, auto(0), auto(0), pct_of(2), pct_of(2), pct_of(2),
                      pct_of(2), pct_of(2), signed(), signed(), signed()],
                     ["Group", "n", "Exceedances", "VaR95 %", "CVaR95 %",
                      "95% low", "95% high", "CVaR99 %", "xi", "xi low",
                      "xi high"])]

    t5 = pd.read_csv(T / "table5_gpd_threshold_sensitivity.csv")
    piv = t5.pivot_table(index=["country", "basis", "group"],
                         columns="threshold_quantile", values="xi").reset_index()
    piv.columns = ["country", "basis", "group"] + [
        f"xi at q{100 * c:g}" for c in piv.columns[3:]]
    parts += [caption("A5", "Generalized Pareto shape across thresholds.",
                      "Blank cells have fewer than 30 exceedances."),
              render(piv, list(piv.columns),
                     [None, None, None] + [signed() for _ in piv.columns[3:]],
                     ["Country", "Basis", "Group"] + list(piv.columns[3:]))]

    t12 = pd.read_csv(T / "table12_gpd_diagnostics.csv")
    t12["country"] = t12["country"].map({"us": "United States", "ng": "Nigeria"})
    parts += [caption("A6", "Goodness of fit of the generalized Pareto "
                            "distribution.",
                      "KS is the largest gap between the weighted empirical "
                      "distribution of the exceedances and the fitted one; it "
                      "is descriptive, since a weighted clustered sample has no "
                      "standard reference distribution for it. Thresholds are "
                      "in the unit of the construction. QQ plots are in Figure "
                      "4."),
              render(t12, ["construction", "country", "threshold",
                           "n_exceedances", "xi", "sigma", "ks"],
                     [None, None, lambda x: num(x, 0) if x > 5 else num(x, 4),
                      auto(0), signed(), lambda x: num(x, 0) if x > 5 else num(x, 4),
                      auto(3)],
                     ["Construction", "Country", "Threshold", "Exceedances",
                      "xi", "sigma", "KS"])]

    t6b = pd.read_csv(T / "table6b_crossover.csv")
    t6b = t6b[t6b["nigeria_reference"] == "Nigerian informal households"].copy()
    t6b["basis"] = t6b["basis"].map({"published": "SDG", "net": "net of OOP"})
    t6b["edge"] = t6b["at_grid_edge"].map({True: "yes", False: ""})
    parts += [caption("A7", "Crossover: the percentile above which a US group's "
                            "burden exceeds the Nigerian informal burden at the "
                            "same percentile.",
                      "Blank means the US curve never exceeds the Nigerian one "
                      "between the 5th and 99.9th percentiles. A crossing at "
                      "the last grid point is flagged, since it may lie "
                      "beyond the grid."),
              render(t6b, ["basis", "us_group", "crossover_percentile",
                           "us_burden_at_crossover_pct", "edge"],
                     [None, None, auto(1), auto(2), None],
                     ["Nigerian basis", "US group", "Crossover percentile",
                      "Burden there %", "At grid edge"])]

    t8 = pd.read_csv(T / "table8_ppp_absolute.csv")
    parts += [caption("A8", "Out-of-pocket spending in 2023 international "
                            "dollars.",
                      "Converted at the World Bank private-consumption PPP "
                      "factor. A PPP for private consumption is not a medical "
                      "price index; the comparison indicates what households "
                      "pay, not what they buy."),
              render(t8, ["country", "mean_oop_household", "mean_oop_per_person",
                          "mean_resources_per_person", "oop_pc_q50",
                          "oop_pc_q90", "oop_pc_q99"],
                     [None, auto(0), auto(0), auto(0), auto(0), auto(0),
                      auto(0)],
                     ["Country", "Mean OOP, household", "Mean OOP, per person",
                      "Mean resources, per person", "q50 p.p.", "q90 p.p.",
                      "q99 p.p."])]

    t9b = pd.read_csv(T / "table9b_robustness_checks.csv")
    parts += [caption("A9", "Which orderings hold in each robustness variant."),
              render(t9b, list(t9b.columns),
                     [None] + [(lambda x: "yes" if x else "no")
                               for _ in t9b.columns[1:]],
                     list(t9b.columns))]

    t9c = pd.read_csv(T / "table9c_rif_poverty_basis.csv")
    parts += [caption("A10", "The poverty coefficient of the unconditional "
                             "quantile regression with Nigerian poverty measured "
                             "on gross and on net-of-OOP consumption.",
                      "Coefficients in percentage points of resources. The "
                      "gross ranking places a household that spent heavily on "
                      "health higher in the consumption distribution, which "
                      "reverses the sign."),
              render(t9c, ["basis", "quantile", "coef_pp", "se_pp", "t"],
                     [None, lambda x: f"q{int(100 * x)}", auto(2), auto(2),
                      auto(2)],
                     ["Basis", "Quantile", "Coefficient (pp)", "SE", "t"])]

    ta1 = pd.read_csv(T / "tableA1_poverty_validation.csv")
    parts += [caption("A11", "Validating the US build: the poverty threshold "
                             "reconstructed from family income and the published "
                             "income-to-poverty ratio, against the 2024 Census "
                             "thresholds.",
                      "MEPS POVLEV uses the Census Bureau thresholds, which "
                      "vary by family composition; the modal cell for each size "
                      "is one person under 65, two adults, three people with one "
                      "child, and four with two children. The weighted average "
                      "and the HHS guideline are shown for reference."),
              render(ta1, ["family_size", "derived_median",
                           "census_threshold_modal_cell",
                           "census_weighted_average", "hhs_guideline", "n"],
                     [auto(0), lambda x: f"${x:,.0f}", lambda x: f"${x:,.0f}",
                      lambda x: f"${x:,.0f}", lambda x: f"${x:,.0f}", auto(0)],
                     ["Family size", "Derived median", "Census, modal cell",
                      "Census, weighted average", "HHS guideline", "n"])]

    t11 = pd.read_csv(T / "table11_xi_stability.csv")
    t11["country"] = t11["country"].map({"us": "United States", "ng": "Nigeria"})
    piv11 = t11.pivot_table(index=["construction", "country"],
                            columns="threshold_quantile", values="xi").reset_index()
    piv11.columns = ["construction", "country"] + [
        f"xi at q{100 * c:g}" for c in piv11.columns[2:]]
    parts += [caption("A12", "Generalized Pareto shape across thresholds, by "
                             "construction of the denominator."),
              render(piv11, list(piv11.columns),
                     [None, None] + [signed() for _ in piv11.columns[2:]],
                     ["Construction", "Country"] + list(piv11.columns[2:]))]

    OUT.write_text("\n".join(parts) + "\n")
    n = sum(1 for line in OUT.read_text().splitlines()
            if line.startswith("**Table"))
    print(f"wrote {OUT.relative_to(config.ROOT)} with {n} tables")


if __name__ == "__main__":
    main()
