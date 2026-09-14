"""
Does the difference in tail shape survive the construction of the denominator?

The published comparison divides US out-of-pocket spending by family income and
Nigerian out-of-pocket spending by household consumption. The Nigerian
consumption aggregate contains the out-of-pocket spending itself, so the
Nigerian ratio cannot exceed one and its upper tail is bounded by construction.
US income does not contain the spending, so the US ratio is unbounded, and a
ratio whose denominator can be small is heavy-tailed for reasons that have
nothing to do with medical bills. Either feature alone could produce a larger
US tail index.

The comparison is therefore repeated on constructions that treat both
countries alike (see config.py for the reasoning):

  published   US OOP / income              NG OOP / consumption
  net         US OOP / income              NG OOP / (consumption - OOP)
  gross       US OOP / (income + OOP)      NG OOP / consumption
  floor       both "net", with the denominator floored at the poverty line
  two-year    US OOP / two-year average income (linked panel members),
              NG as in "net"
  levels      OOP in 2023 international dollars, per household and per person

For each, the generalized Pareto shape is estimated in both countries with
Rao-Wu design-bootstrap intervals, and the US-Nigeria difference is tested
formally rather than by comparing intervals.

Writes Tables 10, 11 and 12 and the QQ points used by the diagnostic figure.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

import config
from tailrisk import (cluster_bootstrap, ci, difference, gpd_diagnostics,
                      tail_stats)


def load():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")
    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    ppp = json.loads((config.DERIVED / "ppp.json").read_text())
    return us, ng, float(ppp["ppp_ngn_per_intl_usd"])


def constructions(us, ng, ppp):
    """(key, label, unit, US series, NG series). NaN marks a unit left out."""
    to_2023 = 1.0 / config.CPI_TO_BASE[2023]
    fl = config.DENOMINATOR_POVERTY_FLOOR
    inc = us["faminc"]
    two = us["faminc_2yr"].where(us["faminc_2yr"] >= config.INCOME_FLOOR_USD)
    linked_one_year = (us["oop"] / inc).where(two.notna())
    poor = us["povcat"].isin([1, 2])
    ng_net = ng["oop"] / ng["resources_net"].where(ng["resources_net"] > 0)
    return [
        ("published", "Published: US OOP/income; Nigeria OOP/consumption",
         "ratio", us["oop"] / inc, ng["burden"]),
        ("net", "Matched net: both over resources excluding OOP",
         "ratio", us["oop"] / inc, ng_net),
        ("gross", "Matched gross: both over resources including OOP",
         "ratio", us["oop"] / (inc + us["oop"]), ng["burden"]),
        ("floor", "Matched net, denominator floored at the poverty line",
         "ratio", us["oop"] / np.maximum(inc, fl * us["poverty_threshold"]),
         ng["oop"] / np.maximum(ng["resources_net"],
                                fl * ng["poverty_threshold"])),
        ("linked_one_year", "US panel-linked families, one-year income",
         "ratio", linked_one_year, ng_net),
        ("two_year", "US panel-linked families, two-year average income",
         "ratio", us["oop"] / two, ng_net),
        ("poor_one_year", "US poor or near poor, one-year income; "
                          "Nigeria poorest quintile, net",
         "ratio", (us["oop"] / inc).where(poor & two.notna()),
         ng_net.where(ng["quintile_net"] == 1)),
        ("poor_two_year", "US poor or near poor, two-year income; "
                          "Nigeria poorest quintile, net",
         "ratio", (us["oop"] / two).where(poor),
         ng_net.where(ng["quintile_net"] == 1)),
        ("levels_household", "OOP level per household, 2023 intl $",
         "intl $", us["oop"] * to_2023, ng["oop"] / ppp),
        ("levels_person", "OOP level per person, 2023 intl $",
         "intl $", us["oop"] * to_2023 / us["n_persons"].clip(lower=1),
         ng["oop"] / ppp / ng["n_persons"].clip(lower=1)),
    ]


def _frame(df, values):
    out = df[["weight", "stratum", "psu"]].copy()
    out["y"] = np.asarray(values, float)
    return out[np.isfinite(out["y"])]


def main():
    us, ng, ppp = load()
    rows, stab, diag, qq = [], [], [], []
    for key, label, unit, u_vals, n_vals in constructions(us, ng, ppp):
        u = _frame(us, u_vals)
        n = _frame(ng, n_vals)
        row = {"construction": key, "label": label, "unit": unit}
        reps = {}
        for tag, df in (("us", u), ("ng", n)):
            st = tail_stats(df["y"].to_numpy(float), df["weight"].to_numpy(float))
            rp = cluster_bootstrap(df, "y", "weight", "stratum", "psu",
                                   lambda v, w: tail_stats(v, w))
            reps[tag] = rp
            above = (np.average(df["y"] > 1, weights=df["weight"])
                     if unit == "ratio" else np.nan)
            row.update({f"{tag}_n": len(df), f"{tag}_xi": st["xi"],
                        f"{tag}_share_above_1": above,
                        f"{tag}_q99": st["var99"], f"{tag}_cvar95": st["cvar95"],
                        f"{tag}_max": float(df["y"].max())})
            row[f"{tag}_xi_lo"], row[f"{tag}_xi_hi"] = ci(rp, "xi")
            row[f"{tag}_cvar95_lo"], row[f"{tag}_cvar95_hi"] = ci(rp, "cvar95")
            for tq in config.GPD_THRESHOLD_GRID:
                s2 = tail_stats(df["y"].to_numpy(float),
                                df["weight"].to_numpy(float), threshold_q=tq)
                stab.append({"construction": key, "country": tag,
                             "threshold_quantile": tq, "xi": s2["xi"],
                             "n_exceedances": s2["n_exceedances"]})
            if key in ("published", "net", "gross", "levels_household"):
                g = gpd_diagnostics(df["y"].to_numpy(float),
                                    df["weight"].to_numpy(float))
                diag.append({"construction": key, "country": tag,
                             "threshold": g["threshold"],
                             "n_exceedances": g["n_exceedances"],
                             "xi": g["xi"], "sigma": g["sigma"], "ks": g["ks"]})
                qq.append(pd.DataFrame({"construction": key, "country": tag,
                                        "prob": g["probs"],
                                        "empirical": g["empirical"],
                                        "model": g["model"]}))
        dx = difference(row["us_xi"], reps["us"]["xi"],
                        row["ng_xi"], reps["ng"]["xi"])
        row.update({"xi_diff": dx["diff"], "xi_diff_lo": dx["diff_lo"],
                    "xi_diff_hi": dx["diff_hi"], "xi_diff_p": dx["p"]})
        if unit == "ratio":
            dc = difference(row["us_cvar95"], reps["us"]["cvar95"],
                            row["ng_cvar95"], reps["ng"]["cvar95"])
            row.update({"cvar95_diff": dc["diff"], "cvar95_diff_lo": dc["diff_lo"],
                        "cvar95_diff_hi": dc["diff_hi"], "cvar95_diff_p": dc["p"]})
        rows.append(row)
        print(f"  {key:<17s} US xi {row['us_xi']:+.3f} "
              f"({row['us_xi_lo']:+.3f}, {row['us_xi_hi']:+.3f})  "
              f"NG xi {row['ng_xi']:+.3f} ({row['ng_xi_lo']:+.3f}, "
              f"{row['ng_xi_hi']:+.3f})  diff {dx['diff']:+.3f} "
              f"({dx['diff_lo']:+.3f}, {dx['diff_hi']:+.3f}) p={dx['p']:.3f}")

    t10 = pd.DataFrame(rows)
    # How closely one-year income tracks the two-year average, in logs.
    lk = us["faminc_2yr"].notna() & (us["faminc_other"] >= config.INCOME_FLOOR_USD)
    t10["us_log_income_corr_adjacent_years"] = float(np.corrcoef(
        np.log(us.loc[lk, "faminc"]), np.log(us.loc[lk, "faminc_other"]))[0, 1])
    t10.to_csv(config.TABLES / "table10_denominator_tests.csv", index=False)
    pd.DataFrame(stab).to_csv(config.TABLES / "table11_xi_stability.csv",
                              index=False)
    pd.DataFrame(diag).to_csv(config.TABLES / "table12_gpd_diagnostics.csv",
                              index=False)
    pd.concat(qq).to_csv(config.DERIVED / "gpd_qq.csv", index=False)

    print("\n=== xi across thresholds, by construction ===")
    s = pd.DataFrame(stab).pivot_table(index=["construction", "country"],
                                       columns="threshold_quantile", values="xi")
    print(s.to_string(float_format=lambda x: f"{x:+.3f}"))
    print(f"\nwrote tables 10-12 to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
