"""
Figures, in a plain journal style.

Everything is drawn from the CSVs the analysis wrote, so a figure cannot
disagree with the table it belongs to. The figures carry no "Figure N" label
of their own; the manuscript numbers them in reading order and a number baked
into the artwork would contradict its caption.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.22, "grid.linewidth": 0.5,
    "axes.axisbelow": True, "figure.dpi": 110,
    "legend.frameon": False, "axes.titlesize": 10, "axes.titleweight": "bold",
})
P = config.PALETTE


def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(config.FIGURES / f"{name}.{ext}", dpi=config.FIG_DPI,
                    bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


# ---------------------------------------------------------------------------
def figure_distributions():
    """The whole paper in one picture: two burden curves and where they cross."""
    grid = np.load(config.DERIVED / "qgrid.npy")
    ng = np.load(config.DERIVED / "ng_inf_curve.npy")
    uc = pd.read_csv(config.DERIVED / "us_quantile_curves.csv")
    cross = pd.read_csv(config.TABLES / "table6b_crossover.csv")

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(100 * grid, 100 * ng, color=P["ng"], linewidth=2.2,
            label="Nigeria, informal households")
    ax.plot(100 * uc["quantile"], 100 * uc["Insured all year"],
            color=P["us"], linewidth=2.0, label="US, insured all year")
    ax.plot(100 * uc["quantile"], 100 * uc["Poor or near poor"], "--",
            color=P["us_light"], linewidth=2.0, label="US, poor or near poor")

    c = cross[(cross["us_group"] == "Poor or near poor")
              & (cross["nigeria_reference"] == "Nigerian informal households")]
    if len(c):
        x = float(c["crossover_percentile"].iloc[0])
        y = float(c["us_burden_at_crossover_pct"].iloc[0])
        ax.plot([x], [y], marker="*", markersize=15, color=P["accent"], zorder=5)
        ax.annotate(f"poor US families overtake\nNigeria's informal sector\nat the "
                    f"{x:.0f}th percentile",
                    xy=(x, y), xytext=(x - 26, y + 30), fontsize=8,
                    color=P["accent"], ha="left",
                    arrowprops=dict(arrowstyle="->", color=P["accent"],
                                    linewidth=0.9,
                                    connectionstyle="arc3,rad=-0.2"))

    ax.set_xlabel("Percentile of each group's own burden distribution")
    ax.set_ylabel("Out-of-pocket burden (% of resources)")
    ax.set_title("Nigeria is worse in the middle; the United States is worse "
                 "in the tail")
    ax.set_xlim(45, 100)
    ax.set_ylim(0, 120)
    ax.legend(loc="upper left", fontsize=8.5)
    _save(fig, "figure1_burden_distributions")


def figure_tail_measures():
    """VaR and CVaR side by side, US groups against Nigerian ones."""
    t4 = pd.read_csv(config.TABLES / "table4_tail_risk.csv")
    t4 = t4.sort_values(["country", "cvar95"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.2), sharey=True)
    labels = [f"{r.group}" for r in t4.itertuples()]
    colours = [P["us"] if r.country == "United States" else P["ng"]
               for r in t4.itertuples()]
    y = np.arange(len(t4))

    ax1.barh(y, 100 * t4["var95"], color=colours, height=0.68)
    ax1.set_yticks(y)
    ax1.set_yticklabels(labels, fontsize=8)
    ax1.set_xlabel("VaR$_{95}$  (% of resources)")
    ax1.set_title("The 95th-percentile burden", fontsize=9, fontweight="normal")

    err = None
    if {"cvar95_lo", "cvar95_hi"}.issubset(t4.columns) and t4["cvar95_lo"].notna().any():
        err = [100 * (t4["cvar95"] - t4["cvar95_lo"]),
               100 * (t4["cvar95_hi"] - t4["cvar95"])]
    ax2.barh(y, 100 * t4["cvar95"], color=colours, height=0.68,
             xerr=err, error_kw=dict(ecolor="#444", elinewidth=0.8, capsize=2))
    ax2.axvline(100, color=P["ink"], linestyle=":", linewidth=1.2)
    ax2.text(101, len(t4) - 0.6, "burden equals\nannual resources",
             fontsize=7.5, color=P["ink"], va="top")
    ax2.set_xlabel("CVaR$_{95}$  (% of resources)")
    ax2.set_title("The mean burden of the worst-affected 5%", fontsize=9,
                  fontweight="normal")

    handles = [plt.Rectangle((0, 0), 1, 1, color=P["us"]),
               plt.Rectangle((0, 0), 1, 1, color=P["ng"])]
    ax1.legend(handles, ["United States", "Nigeria"], loc="lower right",
               fontsize=8)
    fig.suptitle("Expected shortfall: what the worst-affected actually pay",
                 fontsize=10, fontweight="bold", y=1.01)
    _save(fig, "figure2_tail_measures")


def figure_tail_index():
    """The heavy-tail finding, with threshold sensitivity behind it."""
    t4 = pd.read_csv(config.TABLES / "table4_tail_risk.csv")
    t5 = pd.read_csv(config.TABLES / "table5_gpd_threshold_sensitivity.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.0),
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    t = t4.sort_values(["country", "xi"])
    y = np.arange(len(t))
    colours = [P["us"] if r.country == "United States" else P["ng"]
               for r in t.itertuples()]
    err = None
    if {"xi_lo", "xi_hi"}.issubset(t.columns) and t["xi_lo"].notna().any():
        err = [t["xi"] - t["xi_lo"], t["xi_hi"] - t["xi"]]
    ax1.barh(y, t["xi"], color=colours, height=0.68, xerr=err,
             error_kw=dict(ecolor="#444", elinewidth=0.8, capsize=2))
    ax1.axvline(0, color=P["ink"], linewidth=1.0)
    ax1.axvline(0.5, color=P["warn"], linestyle="--", linewidth=1.1)
    ax1.text(0.51, -0.4, "ξ = 0.5\ninfinite variance", fontsize=7.5,
             color=P["warn"])
    ax1.set_yticks(y)
    ax1.set_yticklabels(t["group"], fontsize=8)
    ax1.set_xlabel("Generalised Pareto shape, ξ")
    ax1.set_title("Tail heaviness", fontsize=9, fontweight="normal")

    for country, colour in (("United States", P["us"]), ("Nigeria", P["ng"])):
        sub = t5[t5["country"] == country]
        for g, grp in sub.groupby("group"):
            grp = grp.sort_values("threshold_quantile")
            ax2.plot(100 * grp["threshold_quantile"], grp["xi"], "o-",
                     color=colour, alpha=0.55, linewidth=1.2, markersize=3.5)
    ax2.axhline(0, color=P["ink"], linewidth=1.0)
    ax2.set_xlabel("Threshold (percentile of the burden distribution)")
    ax2.set_ylabel("ξ")
    ax2.set_title("Stable across thresholds", fontsize=9, fontweight="normal")
    handles = [plt.Line2D([], [], color=P["us"], marker="o"),
               plt.Line2D([], [], color=P["ng"], marker="o")]
    ax2.legend(handles, ["United States", "Nigeria"], fontsize=8)

    fig.suptitle("The American burden distribution is heavy-tailed; "
                 "the Nigerian one is not", fontsize=10, fontweight="bold",
                 y=1.02)
    _save(fig, "figure3_tail_index")


def figure_che_comparison():
    """Catastrophic spending on both definitions, both countries."""
    t1 = pd.read_csv(config.TABLES / "table1_che_harmonised.csv")
    ov = t1[t1["dimension"] == "Overall"]
    measures = ["Budget share > 10%", "Budget share > 25%",
                "Capacity to pay >= 40%",
                "No capacity to pay (at or below the floor)"]
    short = ["OOP > 10%\nof resources", "OOP > 25%\nof resources",
             "OOP ≥ 40% of\ncapacity to pay", "Below the\nsubsistence floor"]

    fig, ax = plt.subplots(figsize=(7.0, 3.9))
    x = np.arange(len(measures))
    w = 0.36
    for k, (c, colour) in enumerate([("United States", P["us"]),
                                     ("Nigeria", P["ng"])]):
        s = ov[ov["country"] == c].set_index("measure").reindex(measures)
        err = [s["estimate_pct"] - s["ci_low"], s["ci_high"] - s["estimate_pct"]]
        ax.bar(x + (k - 0.5) * w, s["estimate_pct"], w, label=c, color=colour,
               edgecolor="white", linewidth=0.5)
        ax.errorbar(x + (k - 0.5) * w, s["estimate_pct"], yerr=err, fmt="none",
                    ecolor="#444", elinewidth=0.8, capsize=2)
        for xi_, v in zip(x + (k - 0.5) * w, s["estimate_pct"]):
            ax.text(xi_, v + 1.4, f"{v:.1f}", ha="center", fontsize=7.5,
                    color=colour, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(short, fontsize=8)
    ax.set_ylabel("Households affected (%)")
    ax.set_title("Catastrophic spending on harmonised definitions")
    ax.legend(fontsize=8.5)
    _save(fig, "figure4_che_comparison")


def figure_parity():
    """How much of the US already lives above the Nigerian burden."""
    t6 = pd.read_csv(config.TABLES / "table6_parity.csv")
    inf = t6[t6["nigeria_reference"] == "Nigerian informal households"]
    piv = inf.pivot_table(index="us_group", columns="reference_quantile",
                          values="us_share_above_pct")
    piv = piv.sort_values(0.5)

    fig, ax = plt.subplots(figsize=(7.4, 3.9))
    y = np.arange(len(piv))
    shades = [P["us_light"], P["us"], P["ink"]]
    labels = ["above the Nigerian informal median",
              "above its upper quartile",
              "above its 90th percentile"]
    h = 0.26
    for k, (q, colour, lab) in enumerate(zip(piv.columns, shades, labels)):
        ax.barh(y + (1 - k) * h, piv[q], h, color=colour, label=lab)
        for yi, v in zip(y + (1 - k) * h, piv[q]):
            ax.text(v + 0.6, yi, f"{v:.1f}%", va="center", fontsize=7.2,
                    color=colour)
    ax.set_yticks(y)
    ax.set_yticklabels(piv.index, fontsize=8.5)
    ax.set_xlabel("Share of US families (%)")
    ax.set_title("US families already carrying a Nigerian burden")
    ax.legend(fontsize=8, loc="lower right")
    ax.set_xlim(0, max(piv.max()) * 1.18)
    _save(fig, "figure5_parity")


def main():
    print("Drawing figures ...")
    figure_distributions()
    figure_tail_measures()
    figure_tail_index()
    figure_che_comparison()
    figure_parity()


if __name__ == "__main__":
    main()
