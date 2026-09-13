"""
Where does the American tail meet the Nigerian middle?

The comparison the paper is built around. Average catastrophic-spending rates
say Nigeria is roughly two and a half times worse than the United States. That
is true and it is not the whole story, because the two distributions have very
different shapes: Nigeria's burden is high in the middle and bounded above,
the United States' is low in the middle with a long heavy tail. Somewhere up
the American distribution the two cross.

Two ways of locating that point:

  parity percentile   the percentile of a US group's burden distribution at
                      which it reaches a given Nigerian reference burden
  exceedance share    the share of US families already carrying a burden
                      heavier than that reference

Both are reported against the Nigerian informal household at its median and
upper quartile, since the informal sector is the population Paper 2 priced.

Writes Table 6.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from svy import Design, weighted_quantile


def parity_percentile(x, w, target):
    """The percentile of the weighted distribution of x that equals `target`.

    Equivalently one minus the weighted share above the target, expressed as a
    percentile. Returns NaN when the target sits outside the support.
    """
    x = np.asarray(x, float)
    w = np.asarray(w, float)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    x, w = x[ok], w[ok]
    if len(x) == 0 or target <= np.min(x):
        return np.nan
    below = w[x <= target].sum() / w.sum()
    return 100 * below


def main():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")

    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    us["burden"] = us["oop"] / us["faminc"]
    us = us[np.isfinite(us["burden"])]
    us["_povcat_low"] = us["povcat"].isin([1, 2]).astype(int)
    us["_elderly"] = (us["n_over64"] > 0).astype(int)
    ng = ng[np.isfinite(ng["burden"])].copy()

    d_ng = Design(ng, "weight", "stratum", "psu")
    d_us = Design(us, "weight", "stratum", "psu")

    b_ng = ng["burden"].to_numpy(float)
    b_us = us["burden"].to_numpy(float)

    # ---- Nigerian reference points ----------------------------------------
    refs = {}
    for name, mask in (("All Nigerian households", np.ones(len(ng), bool)),
                       ("Nigerian informal households",
                        (ng["sector_group"] == "Informal").to_numpy())):
        sub = d_ng.subset(mask)
        for q in config.PARITY_REFERENCE_QUANTILES + (0.90,):
            refs[(name, q)] = sub.quantile(b_ng, [q])[0]

    print("Nigerian reference burdens (OOP as a share of consumption):")
    for (name, q), v in refs.items():
        print(f"  {name:<30s} q{int(100 * q):<3d} {100 * v:6.2f}%")

    # ---- where each US group reaches them ----------------------------------
    us_groups = [
        ("All US families", np.ones(len(us), bool)),
        ("Insured all year", (us["insurance_group"] == "Insured all year").to_numpy()),
        ("Partly uninsured", (us["insurance_group"] == "Partly uninsured").to_numpy()),
        ("Uninsured all year", (us["insurance_group"] == "Uninsured all year").to_numpy()),
        ("Poor or near poor", (us["_povcat_low"] == 1).to_numpy()),
        ("Chronic condition", (us["any_chronic"] == 1).to_numpy()),
        ("Elderly member", (us["_elderly"] == 1).to_numpy()),
    ]

    rows = []
    for label, mask in us_groups:
        sub = d_us.subset(mask)
        w = us["weight"].to_numpy(float) * mask
        for (ref_name, q), target in refs.items():
            share_above = sub.mean((b_us > target).astype(float))[0]
            rows.append({
                "us_group": label,
                "nigeria_reference": ref_name,
                "reference_quantile": q,
                "reference_burden_pct": 100 * target,
                "us_parity_percentile": parity_percentile(b_us, w, target),
                "us_share_above_pct": 100 * share_above,
                "n": int(mask.sum()),
            })
    t6 = pd.DataFrame(rows)
    t6.to_csv(config.TABLES / "table6_parity.csv", index=False)

    print("\n=== Share of US families already above the Nigerian reference ===")
    inf = t6[t6["nigeria_reference"] == "Nigerian informal households"]
    piv = inf.pivot_table(index="us_group", columns="reference_quantile",
                          values="us_share_above_pct")
    piv.columns = [f"above NG informal q{int(100 * c)}" for c in piv.columns]
    print(piv.to_string(float_format=lambda x: f"{x:6.2f}%"))

    print("\n=== The percentile at which each US group reaches it ===")
    piv2 = inf.pivot_table(index="us_group", columns="reference_quantile",
                           values="us_parity_percentile")
    piv2.columns = [f"parity pctile vs NG q{int(100 * c)}" for c in piv2.columns]
    print(piv2.to_string(float_format=lambda x: f"{x:6.1f}"))

    # ---- the crossing point ------------------------------------------------
    # At which percentile of its own distribution does each US group's burden
    # first exceed the Nigerian burden at the same percentile? That is the
    # point where being American stops being the safer place to be ill.
    # The grid has to start low enough that a crossing at the bottom is a
    # real crossing and not the edge of the grid: families with an elderly
    # member overtake the Nigerian burden well below the median.
    grid = np.arange(0.05, 0.999, 0.005)
    ng_curve = np.array([d_ng.quantile(b_ng, [q])[0] for q in grid])
    ng_inf = d_ng.subset((ng["sector_group"] == "Informal").to_numpy())
    ng_inf_curve = np.array([ng_inf.quantile(b_ng, [q])[0] for q in grid])

    cross = []
    us_curves = {}
    for label, mask in us_groups:
        sub = d_us.subset(mask)
        us_curve = np.array([sub.quantile(b_us, [q])[0] for q in grid])
        us_curves[label] = us_curve
        for ref_label, curve in (("All Nigerian households", ng_curve),
                                 ("Nigerian informal households", ng_inf_curve)):
            over = us_curve >= curve
            # Take the last sustained crossing, not the first touch: the two
            # curves can brush at the very bottom where both burdens are near
            # zero, which is not the crossover the paper is about.
            if over.any():
                idx = int(np.argmax(np.cumsum(~over[::-1])[::-1] == 0))
                first, burden = grid[idx], us_curve[idx]
                at_edge = idx == 0
            else:
                first, burden, at_edge = np.nan, np.nan, False
            cross.append({"us_group": label, "nigeria_reference": ref_label,
                          "crossover_percentile": 100 * first if over.any() else np.nan,
                          "us_burden_at_crossover_pct": 100 * burden if over.any() else np.nan,
                          "crosses_below_grid": bool(at_edge)})
    t6b = pd.DataFrame(cross)
    t6b.to_csv(config.TABLES / "table6b_crossover.csv", index=False)

    print("\n=== Quantile-for-quantile crossover ===")
    print("  the percentile above which the US burden exceeds the Nigerian one")
    print("  at the same percentile\n")
    print(t6b.pivot_table(index="us_group", columns="nigeria_reference",
                          values="crossover_percentile")
          .to_string(float_format=lambda x: f"{x:6.1f}"))

    np.save(config.DERIVED / "qgrid.npy", grid)
    np.save(config.DERIVED / "ng_curve.npy", ng_curve)
    np.save(config.DERIVED / "ng_inf_curve.npy", ng_inf_curve)
    # Full quantile curves for the figure. Plotting the US from five points
    # while Nigeria gets a smooth curve would flatter the US shape.
    pd.DataFrame({"quantile": grid, **us_curves}).to_csv(
        config.DERIVED / "us_quantile_curves.csv", index=False)
    print(f"\nwrote tables 6 and 6b to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
