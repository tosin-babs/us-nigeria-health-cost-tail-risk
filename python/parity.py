"""
Where does the American distribution meet the Nigerian one?

Two ways of locating that point:

  parity percentile   the percentile of a US group's burden distribution at
                      which it reaches a given Nigerian reference burden
  exceedance share    the share of US families already carrying a burden
                      heavier than that reference
  crossover           the percentile above which the US burden at a given
                      percentile exceeds the Nigerian burden at the same
                      percentile

Both are reported against the Nigerian informal household at its median,
upper quartile and 90th percentile, and on two constructions of the Nigerian
denominator: the published one (consumption, which contains out-of-pocket
spending) and the net one (consumption excluding it). The median and upper
quartile barely move between them; the far tail does, because the published
ratio is bounded by construction.

Writes Tables 6 and 6b.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from svy import Design


def parity_percentile(x, w, target):
    """The percentile of the weighted distribution of x that equals `target`."""
    x = np.asarray(x, float)
    w = np.asarray(w, float)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    x, w = x[ok], w[ok]
    if len(x) == 0 or target <= np.min(x):
        return np.nan
    below = w[x <= target].sum() / w.sum()
    return 100 * below


BASES = (("published", "burden"), ("net", "burden_net"))


def main():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")

    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    us["burden"] = us["oop"] / us["faminc"]
    us = us[np.isfinite(us["burden"])]
    us["_povcat_low"] = us["povcat"].isin([1, 2]).astype(int)
    us["_elderly"] = (us["n_over64"] > 0).astype(int)
    ng = ng[np.isfinite(ng["burden"]) & np.isfinite(ng["burden_net"])].copy()

    d_ng = Design(ng, "weight", "stratum", "psu")
    d_us = Design(us, "weight", "stratum", "psu")
    b_us = us["burden"].to_numpy(float)
    informal = (ng["sector_group"] == "Informal").to_numpy()

    us_groups = [
        ("All US families", np.ones(len(us), bool)),
        ("Insured all year", (us["insurance_group"] == "Insured all year").to_numpy()),
        ("Partly uninsured", (us["insurance_group"] == "Partly uninsured").to_numpy()),
        ("Uninsured all year", (us["insurance_group"] == "Uninsured all year").to_numpy()),
        ("Poor or near poor", (us["_povcat_low"] == 1).to_numpy()),
        ("Chronic condition", (us["any_chronic"] == 1).to_numpy()),
        ("Elderly member", (us["_elderly"] == 1).to_numpy()),
    ]

    # The grid runs from the 5th to the 99.9th percentile. A crossing found at
    # either end is flagged, because it may lie beyond the grid.
    grid = np.concatenate([np.arange(0.05, 0.99, 0.005),
                           np.arange(0.99, 0.9991, 0.001)])
    us_curves = {}
    for label, mask in us_groups:
        sub = d_us.subset(mask)
        us_curves[label] = np.array([sub.quantile(b_us, [q])[0] for q in grid])

    rows, cross, ng_curves = [], [], {}
    for basis, col in BASES:
        b_ng = ng[col].to_numpy(float)
        refs = {}
        for name, mask in (("All Nigerian households", np.ones(len(ng), bool)),
                           ("Nigerian informal households", informal)):
            sub = d_ng.subset(mask)
            for q in config.PARITY_REFERENCE_QUANTILES + (0.90,):
                refs[(name, q)] = sub.quantile(b_ng, [q])[0]
            ng_curves[(basis, name)] = np.array(
                [sub.quantile(b_ng, [q])[0] for q in grid])

        for label, mask in us_groups:
            sub = d_us.subset(mask)
            w = us["weight"].to_numpy(float) * mask
            for (ref_name, q), target in refs.items():
                share_above = sub.mean((b_us > target).astype(float))[0]
                rows.append({
                    "basis": basis, "us_group": label,
                    "nigeria_reference": ref_name, "reference_quantile": q,
                    "reference_burden_pct": 100 * target,
                    "us_parity_percentile": parity_percentile(b_us, w, target),
                    "us_share_above_pct": 100 * share_above,
                    "n": int(mask.sum()),
                })
            for ref_label in ("All Nigerian households",
                              "Nigerian informal households"):
                curve = ng_curves[(basis, ref_label)]
                us_curve = us_curves[label]
                over = us_curve >= curve
                # The last sustained crossing, not the first touch: the
                # curves brush near zero at the bottom. A "crossing" that
                # starts at the first grid point is the two curves sitting
                # together at zero, which is no crossing at all.
                idx = (int(np.argmax(np.cumsum(~over[::-1])[::-1] == 0))
                       if over.any() else -1)
                if idx > 0:
                    first, burden = grid[idx], us_curve[idx]
                    at_edge = idx == len(grid) - 1
                else:
                    first, burden, at_edge = np.nan, np.nan, False
                cross.append({"basis": basis, "us_group": label,
                              "nigeria_reference": ref_label,
                              "crossover_percentile": 100 * first,
                              "us_burden_at_crossover_pct": 100 * burden,
                              "at_grid_edge": bool(at_edge)})

    t6 = pd.DataFrame(rows)
    t6.to_csv(config.TABLES / "table6_parity.csv", index=False)
    t6b = pd.DataFrame(cross)
    t6b.to_csv(config.TABLES / "table6b_crossover.csv", index=False)

    for basis, _ in BASES:
        inf = t6[(t6["nigeria_reference"] == "Nigerian informal households")
                 & (t6["basis"] == basis)]
        print(f"\n=== Share of US families above the Nigerian informal "
              f"reference ({basis} basis) ===")
        piv = inf.pivot_table(index="us_group", columns="reference_quantile",
                              values="us_share_above_pct")
        piv.columns = [f"above q{int(100 * c)}" for c in piv.columns]
        print(piv.to_string(float_format=lambda x: f"{x:6.2f}%"))
        print(f"\n=== Crossover percentile ({basis} basis) ===")
        sub = t6b[t6b["basis"] == basis]
        print(sub.pivot_table(index="us_group", columns="nigeria_reference",
                              values="crossover_percentile")
              .to_string(float_format=lambda x: f"{x:6.1f}"))
        edge = sub[sub["at_grid_edge"]]
        if len(edge):
            print("  at the edge of the grid (may lie beyond it): "
                  + ", ".join(edge["us_group"].unique()))

    np.save(config.DERIVED / "qgrid.npy", grid)
    np.save(config.DERIVED / "ng_curve.npy",
            ng_curves[("published", "All Nigerian households")])
    np.save(config.DERIVED / "ng_inf_curve.npy",
            ng_curves[("published", "Nigerian informal households")])
    np.save(config.DERIVED / "ng_inf_curve_net.npy",
            ng_curves[("net", "Nigerian informal households")])
    pd.DataFrame({"quantile": grid, **us_curves}).to_csv(
        config.DERIVED / "us_quantile_curves.csv", index=False)
    print(f"\nwrote tables 6 and 6b to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
