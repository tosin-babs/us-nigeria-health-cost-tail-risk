"""
Figures, in a plain journal style.

Everything is drawn from the CSVs the analysis wrote, so a figure cannot
disagree with the table it belongs to. The figures carry no "Figure N" label
of their own; the manuscript numbers them in reading order.
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
def figure_che_comparison():
    """Catastrophic spending on both definitions, both countries."""
    t1 = pd.read_csv(config.TABLES / "table1_che_harmonised.csv")
    ov = t1[t1["dimension"] == "Overall"]
    measures = ["Budget share > 10%", "Budget share > 25%",
                "Capacity to pay >= 40%",
                "No capacity to pay (at or below the floor)"]
    short = ["OOP > 10%\nof resources", "OOP > 25%\nof resources",
             "OOP >= 40% of\ncapacity to pay", "Below the\nsubsistence floor"]

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
    ax.set_title("Catastrophic spending on harmonized definitions")
    ax.legend(fontsize=8.5)
    _save(fig, "figure1_che_comparison")


def figure_distributions():
    """Burden by percentile, with the Nigerian curve on both constructions."""
    grid = np.load(config.DERIVED / "qgrid.npy")
    ng = np.load(config.DERIVED / "ng_inf_curve.npy")
    ng_net = np.load(config.DERIVED / "ng_inf_curve_net.npy")
    uc = pd.read_csv(config.DERIVED / "us_quantile_curves.csv")

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    ax.plot(100 * grid, 100 * ng_net, color=P["ng"], linewidth=2.2,
            label="Nigeria, informal: OOP / consumption net of OOP")
    ax.plot(100 * grid, 100 * ng, ":", color=P["ng_light"], linewidth=2.0,
            label="Nigeria, informal: OOP / consumption (published basis)")
    ax.plot(100 * uc["quantile"], 100 * uc["All US families"],
            color=P["us"], linewidth=2.0, label="US, all families: OOP / income")
    ax.plot(100 * uc["quantile"], 100 * uc["Poor or near poor"], "--",
            color=P["us_light"], linewidth=2.0, label="US, poor or near poor")
    ax.set_xlabel("Percentile of each group's own burden distribution")
    ax.set_ylabel("Out-of-pocket burden (% of resources)")
    ax.set_title("Burden by percentile: the far tail depends on how the "
                 "denominator is built")
    ax.set_xlim(45, 100)
    ax.set_ylim(0, 130)
    ax.legend(loc="upper left", fontsize=8)
    _save(fig, "figure2_burden_distributions")


def figure_denominator():
    """The tail index in both countries under each construction."""
    t = pd.read_csv(config.TABLES / "table10_denominator_tests.csv")
    labels = {
        "published": "Published:\nUS OOP/income, NG OOP/consumption",
        "net": "Matched net:\nboth over resources excluding OOP",
        "gross": "Matched gross:\nboth over resources including OOP",
        "floor": "Matched net, denominator\nfloored at the poverty line",
        "two_year": "US two-year average income\n(panel-linked families)",
        "levels_household": "OOP level per household,\n2023 international $",
        "levels_person": "OOP level per person,\n2023 international $",
    }
    t = t[t["construction"].isin(labels)].copy()
    t["order"] = t["construction"].map({k: i for i, k in enumerate(labels)})
    t = t.sort_values("order", ascending=False)
    y = np.arange(len(t))

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    h = 0.32
    for k, (tag, colour, name) in enumerate((("us", P["us"], "United States"),
                                             ("ng", P["ng"], "Nigeria"))):
        err = [t[f"{tag}_xi"] - t[f"{tag}_xi_lo"], t[f"{tag}_xi_hi"] - t[f"{tag}_xi"]]
        ax.barh(y + (0.5 - k) * h, t[f"{tag}_xi"], h, color=colour, label=name,
                xerr=err, error_kw=dict(ecolor="#444", elinewidth=0.8, capsize=2))
    ax.axvline(0, color=P["ink"], linewidth=1.0)
    ax.axvline(0.5, color=P["warn"], linestyle="--", linewidth=1.1)
    ax.text(0.505, len(t) - 0.45, "xi = 0.5: infinite variance", fontsize=7.5,
            color=P["warn"], va="top")
    for yi, p in zip(y, t["xi_diff_p"]):
        ax.text(1.02, yi, f"p = {p:.2f}" if p >= 0.005 else "p < 0.01",
                fontsize=7.5, va="center", color=P["muted"])
    ax.set_yticks(y)
    ax.set_yticklabels([labels[c] for c in t["construction"]], fontsize=7.8)
    ax.set_xlabel("Generalized Pareto shape (xi), exceedances over the 90th "
                  "percentile, with 95% design-bootstrap intervals")
    ax.set_xlim(-0.3, 1.2)
    ax.set_title("The tail-shape gap appears only where the denominators "
                 "are built differently")
    ax.legend(loc="lower left", fontsize=8)
    _save(fig, "figure3_denominator_tests")


def figure_gpd_qq():
    """QQ plots of the exceedances against the fitted GPD."""
    qq = pd.read_csv(config.DERIVED / "gpd_qq.csv")
    diag = pd.read_csv(config.TABLES / "table12_gpd_diagnostics.csv")
    panels = [("published", "us", "US: OOP / income"),
              ("published", "ng", "Nigeria: OOP / consumption\n(published basis)"),
              ("net", "ng", "Nigeria: OOP / consumption\nnet of OOP"),
              ("levels_household", "ng", "Nigeria: OOP level\n(2023 international $)")]
    fig, axes = plt.subplots(1, 4, figsize=(11.5, 3.3))
    fig.subplots_adjust(wspace=0.32)
    for ax, (cons, ctry, title) in zip(axes, panels):
        s = qq[(qq["construction"] == cons) & (qq["country"] == ctry)]
        d = diag[(diag["construction"] == cons) & (diag["country"] == ctry)].iloc[0]
        colour = P["us"] if ctry == "us" else P["ng"]
        ax.plot(s["model"], s["empirical"], "o", markersize=2.6, color=colour,
                alpha=0.8)
        lim = max(s["model"].max(), s["empirical"].max())
        ax.plot([0, lim], [0, lim], color=P["ink"], linewidth=0.8)
        ax.set_title(title, fontsize=8.5, fontweight="normal")
        ax.set_xlabel("Fitted GPD quantile", fontsize=8)
        ax.text(0.04, 0.95, f"xi = {d['xi']:+.2f}\nKS = {d['ks']:.3f}\n"
                f"n = {int(d['n_exceedances']):,}",
                transform=ax.transAxes, fontsize=7.5, va="top")
    axes[0].set_ylabel("Empirical exceedance quantile", fontsize=8)
    fig.suptitle("Generalized Pareto fit to exceedances over the 90th percentile",
                 fontsize=10, fontweight="bold", y=1.03)
    _save(fig, "figure4_gpd_qq")


def figure_access_debt():
    """Cost barriers, medical debt and forgone care."""
    t = pd.read_csv(config.TABLES / "table13_access_debt.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.8))

    us = t[(t["country"] == "United States")
           & (t["dimension"] == "Burden (OOP / income)")]
    bands = list(dict.fromkeys(us["group"]))
    x = np.arange(len(bands))
    w = 0.36
    for k, (m, colour, lab) in enumerate((("Cost barrier to care", P["us_light"],
                                           "delayed or went without care because of cost"),
                                          ("Any medical debt (2024)", P["us"],
                                           "any medical debt (2024 only)"))):
        s = us[us["measure"] == m].set_index("group").reindex(bands)
        ax1.bar(x + (k - 0.5) * w, s["estimate_pct"], w, color=colour, label=lab)
        ax1.errorbar(x + (k - 0.5) * w, s["estimate_pct"],
                     yerr=1.96 * s["se_pct"], fmt="none", ecolor="#444",
                     elinewidth=0.8, capsize=2)
    ax1.set_xticks(x)
    ax1.set_xticklabels([b.replace(" to under ", " to\nunder ") for b in bands],
                        fontsize=7.5)
    ax1.set_xlabel("Out-of-pocket burden, share of family income")
    ax1.set_ylabel("Share of families (%)")
    ax1.set_title("United States", fontsize=9, fontweight="normal")
    ax1.legend(fontsize=7.5, loc="upper left")

    ng = t[(t["country"] == "Nigeria")
           & (t["dimension"] == "Quintile, consumption net of OOP")]
    qs = list(dict.fromkeys(ng["group"]))
    x = np.arange(len(qs))
    for k, (m, colour, lab) in enumerate((
            ("Ill, consulted no one", P["ng_light"],
             "ill in the last 4 weeks, consulted no one"),
            ("Ill, consulted no one because of cost", P["ng"],
             "of which: because of cost"))):
        s = ng[ng["measure"] == m].set_index("group").reindex(qs)
        ax2.bar(x + (k - 0.5) * w, s["estimate_pct"], w, color=colour, label=lab)
        ax2.errorbar(x + (k - 0.5) * w, s["estimate_pct"],
                     yerr=1.96 * s["se_pct"], fmt="none", ecolor="#444",
                     elinewidth=0.8, capsize=2)
    ax2.set_xticks(x)
    ax2.set_xticklabels([q.replace(" (", "\n(") for q in qs], fontsize=7.5)
    ax2.set_xlabel("Quintile of per-capita consumption net of OOP")
    ax2.set_ylabel("Share of ill persons (%)")
    ax2.set_title("Nigeria", fontsize=9, fontweight="normal")
    ax2.legend(fontsize=7.5, loc="upper right")
    fig.suptitle("Credit on one side, forgone care on the other",
                 fontsize=10, fontweight="bold", y=1.02)
    _save(fig, "figure5_access_debt")


def main():
    print("Drawing figures ...")
    for stale in ("figure1_burden_distributions", "figure2_tail_measures",
                  "figure3_tail_index", "figure4_che_comparison",
                  "figure5_parity"):
        for ext in ("png", "pdf"):
            (config.FIGURES / f"{stale}.{ext}").unlink(missing_ok=True)
    figure_che_comparison()
    figure_distributions()
    figure_denominator()
    figure_gpd_qq()
    figure_access_debt()


if __name__ == "__main__":
    main()
