"""
Tail-risk measurement of household out-of-pocket burden.

Average catastrophic-spending rates are the standard summary in the financial-
protection literature. They describe how many households cross a line, not how
far past it the worst-affected go, and it is the far tail that ruins people.
This module applies the measures an actuary would use on a loss distribution:

  VaR_q     the q-th quantile of the burden distribution
  CVaR_q    the mean burden among those above VaR_q (expected shortfall)
  xi        the shape parameter of a generalised Pareto fit to the exceedances
            over a high threshold; xi > 0 means a heavy, power-law tail with
            xi >= 1 implying an infinite mean

Two things need care with survey data.

Weights. A GPD fitted by ordinary maximum likelihood to survey observations
treats a household representing 40,000 others the same as one representing
400. The likelihood here is weighted, which is the estimating-equation
analogue of the usual MLE and is what makes the shape estimate population-
referenced rather than sample-referenced.

Uncertainty. The observations are clustered and stratified, so a naive
bootstrap understates the standard error. Resampling is done over primary
sampling units within strata, which is the standard design-consistent
bootstrap and propagates through every statistic here, including the GPD
shape.

Writes Tables 4, 5 and 6.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, stats

import config
from svy import Design, weighted_quantile


# --------------------------------------------------------------- measures ---
def var_cvar(x, w, levels=config.VAR_LEVELS):
    """Weighted Value-at-Risk and Conditional Value-at-Risk."""
    x = np.asarray(x, float)
    w = np.asarray(w, float)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    x, w = x[ok], w[ok]
    out = {}
    for q in levels:
        v = weighted_quantile(x, w, [q])[0]
        tail = x >= v
        cv = np.average(x[tail], weights=w[tail]) if tail.any() else np.nan
        out[q] = (v, cv)
    return out


def gpd_weighted_fit(excess, weights):
    """Weighted MLE for a generalised Pareto fit to exceedances.

    Parameterised by shape xi and scale sigma with location fixed at zero,
    since the data are already excesses over the threshold. The optimiser
    works on log(sigma) to keep the scale positive, and falls back to the
    unweighted scipy fit if the search does not converge.
    """
    excess = np.asarray(excess, float)
    weights = np.asarray(weights, float)
    ok = np.isfinite(excess) & (excess > 0) & np.isfinite(weights) & (weights > 0)
    excess, weights = excess[ok], weights[ok]
    if len(excess) < 30:
        return np.nan, np.nan, len(excess)

    w = weights / weights.sum()

    def nll(theta):
        xi, log_sigma = theta
        sigma = np.exp(log_sigma)
        z = excess / sigma
        if abs(xi) < 1e-8:                     # exponential limit
            ll = -np.log(sigma) - z
        else:
            arg = 1.0 + xi * z
            if np.any(arg <= 0):
                return 1e10
            ll = -np.log(sigma) - (1.0 + 1.0 / xi) * np.log(arg)
        return -np.sum(w * ll)

    start = [0.1, np.log(max(np.average(excess, weights=weights), 1e-6))]
    res = optimize.minimize(nll, start, method="Nelder-Mead",
                            options={"maxiter": 4000, "xatol": 1e-7,
                                     "fatol": 1e-9})
    if not res.success:
        try:
            xi, _, sigma = stats.genpareto.fit(excess, floc=0)
            return xi, sigma, len(excess)
        except Exception:
            return np.nan, np.nan, len(excess)
    xi, log_sigma = res.x
    return xi, np.exp(log_sigma), len(excess)


def tail_stats(x, w, threshold_q=config.GPD_THRESHOLD_QUANTILE):
    """VaR, CVaR and a GPD fit above the threshold quantile, in one pass."""
    x = np.asarray(x, float)
    w = np.asarray(w, float)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    x, w = x[ok], w[ok]
    u = weighted_quantile(x, w, [threshold_q])[0]
    over = x > u
    xi, sigma, n_exc = gpd_weighted_fit(x[over] - u, w[over])
    vc = var_cvar(x, w)
    return {"threshold": u, "n_exceedances": n_exc, "xi": xi, "sigma": sigma,
            **{f"var{int(100 * q)}": vc[q][0] for q in vc},
            **{f"cvar{int(100 * q)}": vc[q][1] for q in vc}}


# ------------------------------------------------------- design bootstrap ---
def cluster_bootstrap(df, value_col, weight_col, stratum_col, psu_col,
                      statistic, n_boot=config.N_BOOTSTRAP, seed=config.SEED):
    """Resample PSUs within strata and recompute `statistic` each time.

    `statistic(values, weights)` returns a dict of scalars. Returns a frame of
    the replicate values, from which any percentile interval can be taken.
    """
    rng = np.random.default_rng(seed)
    groups = {}
    # groupby on a single column yields scalar keys, on a list of one it has
    # varied by pandas version; take the column directly and stay out of it.
    for stratum, idx in df.groupby(stratum_col).indices.items():
        sub = df.iloc[idx]
        groups[stratum] = [idx[v] for v in sub.groupby(psu_col).indices.values()]

    vals = df[value_col].to_numpy(float)
    wts = df[weight_col].to_numpy(float)

    reps = []
    for _ in range(n_boot):
        take = []
        for _, psus in groups.items():
            k = len(psus)
            if k < 2:                       # a lone PSU contributes as it is
                take.extend(psus)
                continue
            pick = rng.integers(0, k, size=k)
            for p in pick:
                take.append(psus[p])
        sel = np.concatenate(take)
        try:
            reps.append(statistic(vals[sel], wts[sel]))
        except Exception:
            continue
    return pd.DataFrame(reps)


def ci(reps, col, lo=2.5, hi=97.5):
    s = reps[col].dropna()
    if len(s) < 20:
        return np.nan, np.nan
    return np.percentile(s, lo), np.percentile(s, hi)


# ------------------------------------------------------------------ main ---
GROUPS_US = [
    ("All families", None),
    ("Insured all year", ("insurance_group", "Insured all year")),
    ("Partly uninsured", ("insurance_group", "Partly uninsured")),
    ("Uninsured all year", ("insurance_group", "Uninsured all year")),
    ("Poor or near poor", ("_povcat_low", 1)),
    ("Chronic condition", ("any_chronic", 1)),
    ("Elderly member", ("_elderly", 1)),
]
GROUPS_NG = [
    ("All households", None),
    ("Informal sector", ("sector_group", "Informal")),
    ("Formal sector", ("sector_group", "Formal")),
    ("Poorest quintile", ("quintile", 1)),
    ("Richest quintile", ("quintile", 5)),
    ("Rural", ("urban", 0)),
]


def _subset(df, spec):
    if spec is None:
        return df
    col, val = spec
    return df[df[col] == val]


def main():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")

    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    us["burden"] = us["oop"] / us["faminc"]
    us["_povcat_low"] = us["povcat"].isin([1, 2]).astype(int)
    us["_elderly"] = (us["n_over64"] > 0).astype(int)
    us = us[np.isfinite(us["burden"])]

    ng = ng[np.isfinite(ng["burden"])].copy()

    rows, boot_rows = [], []
    for country, df, groups in (("United States", us, GROUPS_US),
                                ("Nigeria", ng, GROUPS_NG)):
        print(f"\n=== {country} ===")
        for label, spec in groups:
            sub = _subset(df, spec)
            if len(sub) < 100:
                continue
            st = tail_stats(sub["burden"].to_numpy(float),
                            sub["weight"].to_numpy(float))
            st.update(country=country, group=label, n=len(sub))
            rows.append(st)
            print(f"  {label:<20s} n={len(sub):>6,}  "
                  f"VaR95 {100 * st['var95']:7.2f}%  "
                  f"CVaR95 {100 * st['cvar95']:8.2f}%  "
                  f"xi {st['xi']:+.3f}  ({st['n_exceedances']:,} exceedances)")

            reps = cluster_bootstrap(
                sub, "burden", "weight", "stratum", "psu",
                lambda v, w: tail_stats(v, w), n_boot=250)
            b = {"country": country, "group": label}
            for c in ("var95", "cvar95", "xi", "cvar99"):
                lo, hi = ci(reps, c)
                b[f"{c}_lo"], b[f"{c}_hi"] = lo, hi
            boot_rows.append(b)

    t4 = pd.DataFrame(rows).merge(pd.DataFrame(boot_rows),
                                  on=["country", "group"], how="left")
    order = ["country", "group", "n", "threshold", "n_exceedances",
             "var90", "var95", "var99", "cvar90", "cvar95", "cvar95_lo",
             "cvar95_hi", "cvar99", "cvar99_lo", "cvar99_hi",
             "xi", "xi_lo", "xi_hi", "sigma"]
    t4 = t4[[c for c in order if c in t4.columns]]
    t4.to_csv(config.TABLES / "table4_tail_risk.csv", index=False)

    # ---- threshold sensitivity: GPD shape is notoriously threshold-driven --
    sens = []
    for country, df, groups in (("United States", us, GROUPS_US),
                                ("Nigeria", ng, GROUPS_NG)):
        for label, spec in groups:
            sub = _subset(df, spec)
            if len(sub) < 100:
                continue
            for tq in config.GPD_THRESHOLD_GRID:
                st = tail_stats(sub["burden"].to_numpy(float),
                                sub["weight"].to_numpy(float), threshold_q=tq)
                sens.append({"country": country, "group": label,
                             "threshold_quantile": tq,
                             "threshold": st["threshold"],
                             "n_exceedances": st["n_exceedances"],
                             "xi": st["xi"], "sigma": st["sigma"]})
    t5 = pd.DataFrame(sens)
    t5.to_csv(config.TABLES / "table5_gpd_threshold_sensitivity.csv", index=False)

    print("\n=== GPD shape across thresholds (xi) ===")
    piv = t5.pivot_table(index=["country", "group"],
                         columns="threshold_quantile", values="xi")
    print(piv.to_string(float_format=lambda x: f"{x:+.3f}"))

    print(f"\nwrote tables 4 and 5 to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
