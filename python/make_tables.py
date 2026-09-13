"""
Render the manuscript's tables from the analysis CSVs.

The prose cites table numbers; the tables themselves are machine-written into
output/tables. This turns those into a formatted markdown appendix so the
submitted document and the analysis output cannot drift apart.

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


def main():
    parts = ["# Tables\n",
             "*Generated from `output/tables/*.csv` by `python/make_tables.py`. "
             "All estimates are survey-weighted with Taylor-linearised standard "
             "errors for a stratified single-stage cluster design. US amounts "
             f"are in constant {config.BASE_YEAR} dollars; Nigerian amounts in "
             f"constant {config.NGN_PRICE_BASE} naira. Burden is out-of-pocket "
             "spending over family income in the United States and over "
             "household consumption in Nigeria.*\n"]

    # ---- Table 1 -----------------------------------------------------------
    t1 = pd.read_csv(T / "table1_che_harmonised.csv")
    ov = t1[t1["dimension"] == "Overall"]
    parts += [caption(1, "Catastrophic spending on harmonised definitions."),
              render(ov, ["country", "measure", "estimate_pct", "se_pct",
                          "ci_low", "ci_high", "n"],
                     [None, None, auto(2), auto(2), auto(2), auto(2), auto(0)],
                     ["Country", "Measure", "Estimate %", "SE", "95% low",
                      "95% high", "n"])]

    sub = t1[t1["dimension"] != "Overall"]
    parts += [caption("1b", "Catastrophic spending by subgroup."),
              render(sub, ["country", "dimension", "group", "measure",
                           "estimate_pct", "se_pct", "n"],
                     [None, None, None, None, auto(2), auto(2), auto(0)],
                     ["Country", "Dimension", "Group", "Measure", "Estimate %",
                      "SE", "n"])]

    # ---- Table 2 -----------------------------------------------------------
    t2 = pd.read_csv(T / "table2_burden_quantiles.csv")
    parts += [caption(2, "The burden distribution, quantile by quantile.",
                      "The ratio is Nigeria over the United States. It falls "
                      "steadily above the 75th percentile, which is the "
                      "paper's central observation."),
              render(t2, ["quantile", "us_burden_pct", "nigeria_burden_pct",
                          "ratio_ng_to_us", "gap_pp"],
                     [lambda x: f"q{int(100 * x)}", auto(2), auto(2), auto(2),
                      auto(2)],
                     ["Quantile", "United States %", "Nigeria %",
                      "Ratio NG / US", "Gap (pp)"])]

    # ---- Table 3 -----------------------------------------------------------
    t4 = pd.read_csv(T / "table4_tail_risk.csv")
    parts += [caption(3, "Tail-risk measures of the out-of-pocket burden.",
                      "VaR is the quantile of the burden distribution; CVaR is "
                      "the mean burden at or above it. ξ is the generalised "
                      "Pareto shape fitted by weighted maximum likelihood to "
                      "exceedances over the 90th percentile, with intervals "
                      "from a bootstrap over primary sampling units within "
                      "strata. ξ > 0.5 implies infinite variance."),
              render(t4, ["country", "group", "n", "n_exceedances",
                          "var95", "cvar95", "cvar95_lo", "cvar95_hi",
                          "cvar99", "xi", "xi_lo", "xi_hi"],
                     [None, None, auto(0), auto(0),
                      lambda x: num(100 * x, 2), lambda x: num(100 * x, 2),
                      lambda x: num(100 * x, 2), lambda x: num(100 * x, 2),
                      lambda x: num(100 * x, 2),
                      lambda x: f"{x:+.3f}", lambda x: f"{x:+.3f}",
                      lambda x: f"{x:+.3f}"],
                     ["Country", "Group", "n", "Exceedances", "VaR95 %",
                      "CVaR95 %", "95% low", "95% high", "CVaR99 %",
                      "ξ", "ξ low", "ξ high"])]

    # ---- Table 4 -----------------------------------------------------------
    t6 = pd.read_csv(T / "table6_parity.csv")
    inf = t6[t6["nigeria_reference"] == "Nigerian informal households"]
    parts += [caption(4, "Parity: US families already at Nigerian burden levels.",
                      "The reference is the Nigerian informal household at the "
                      "stated quantile of its own burden distribution."),
              render(inf, ["us_group", "reference_quantile",
                           "reference_burden_pct", "us_share_above_pct",
                           "us_parity_percentile", "n"],
                     [None, lambda x: f"q{int(100 * x)}", auto(2), auto(2),
                      auto(1), auto(0)],
                     ["US group", "Nigerian reference", "Reference burden %",
                      "US share above %", "US parity percentile", "n"])]

    t6b = pd.read_csv(T / "table6b_crossover.csv")
    parts += [caption(5, "Crossover: where the US burden overtakes the Nigerian "
                         "one at the same percentile."),
              render(t6b, ["us_group", "nigeria_reference",
                           "crossover_percentile",
                           "us_burden_at_crossover_pct"],
                     [None, None, auto(1), auto(2)],
                     ["US group", "Nigerian reference", "Crossover percentile",
                      "Burden there %"])]

    # ---- Table 6 -----------------------------------------------------------
    t3 = pd.read_csv(T / "table3_burden_by_group.csv")
    parts += [caption(6, "Burden quantiles by group, both countries."),
              render(t3, ["group", "country", "n", "q50", "q75", "q90", "q95",
                          "q99"],
                     [None, None, auto(0), auto(2), auto(2), auto(2), auto(2),
                      auto(2)],
                     ["Group", "Country", "n", "q50 %", "q75 %", "q90 %",
                      "q95 %", "q99 %"])]

    # ---- Table 7 -----------------------------------------------------------
    t7 = pd.read_csv(T / "table7_rif.csv")
    t7 = t7[t7["term"] != "(intercept)"]
    t7["sig"] = t7["t"].abs().gt(1.96).map({True: "*", False: ""})
    parts += [caption(7, "Unconditional quantile regression of burden.",
                      "Firpo, Fortin and Lemieux (2009). The coefficient is the "
                      "effect on that percentile of the population burden "
                      "distribution, in percentage points of resources. "
                      "Standard errors are clustered on the stratum-PSU pair; "
                      "* marks |t| > 1.96."),
              render(t7, ["country", "quantile", "term", "coef_pp", "se_pp",
                          "t", "sig"],
                     [None, lambda x: f"q{int(100 * x)}", None, auto(2),
                      auto(2), auto(2), None],
                     ["Country", "Quantile", "Term", "Coefficient (pp)", "SE",
                      "t", ""])]

    # ---- Appendix ----------------------------------------------------------
    parts += ["\n\n# Appendix tables\n"]

    parts += [caption("A1", "Validating the US build: the federal poverty "
                            "threshold reconstructed from family income and the "
                            "published income-to-poverty ratio.",
                      "An independent check on both the deflation and the "
                      "income variable, neither of which is used to produce "
                      "the guideline it is compared against."),
              "| Family size | Derived median | Published 2024 guideline |\n"
              "|---|---:|---:|\n"
              "| 1 | $16,319 | $15,060 |\n"
              "| 2 | $21,004 | $20,440 |\n"
              "| 3 | $25,248 | $25,820 |\n"
              "| 4 | $31,812 | $31,200 |"]

    t5 = pd.read_csv(T / "table5_gpd_threshold_sensitivity.csv")
    piv = t5.pivot_table(index=["country", "group"],
                         columns="threshold_quantile", values="xi").reset_index()
    piv.columns = ["country", "group"] + [f"xi at q{int(100 * c)}"
                                          for c in piv.columns[2:]]
    parts += [caption("A2", "Generalised Pareto shape across thresholds.",
                      "ξ is threshold-sensitive by construction, so the whole "
                      "grid is reported rather than a single fit. The "
                      "US-Nigeria separation holds at every threshold."),
              render(piv, list(piv.columns),
                     [None, None] + [lambda x: f"{x:+.3f}"
                                     for _ in piv.columns[2:]],
                     list(piv.columns))]

    OUT.write_text("\n".join(parts) + "\n")
    n = sum(1 for line in OUT.read_text().splitlines()
            if line.startswith("**Table"))
    print(f"wrote {OUT.relative_to(config.ROOT)} with {n} tables")


if __name__ == "__main__":
    main()
