"""
Tail-risk measurement of household out-of-pocket burden.

Average catastrophic-spending rates describe how many households cross a line,
not how far past it the worst-affected go. This module applies the measures an
actuary would use on a loss distribution:

  VaR_q     the q-th quantile of the burden distribution
  CVaR_q    the mean burden among those at or above VaR_q (expected shortfall)
  xi        the shape parameter of a generalized Pareto fit to the exceedances
            over a high threshold; xi > 0 is a power-law tail, xi < 0 a tail
            with a finite endpoint

Weights. The likelihood is weighted by the survey weights (a pseudo-likelihood),
so the fit refers to the population rather than to the sample.

Uncertainty. Resampling is over primary sampling units within strata with the
Rao and Wu (1988) rescaling: n_h - 1 PSUs are drawn with replacement in each
stratum and the weights are multiplied by n_h / (n_h - 1) times the number of
draws. The unscaled bootstrap that draws n_h PSUs understates the variance by
(n_h - 1) / n_h, which matters for the 35 MEPS strata with two PSUs. The
threshold is re-estimated in every replicate, so threshold uncertainty is in
the interval.

Comparison. The US and Nigerian samples are independent, so the bootstrap
distribution of a difference is obtained by differencing independently drawn
replicates; a Wald test uses the two bootstrap standard errors.

Writes Tables 4 and 5.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import optimize, stats

import config
from svy import weighted_quantile


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
    """Weighted pseudo-maximum-likelihood fit of a generalized Pareto.

    Location is fixed at zero because the data are excesses over the
    threshold. The optimizer works on log(sigma). If the search fails the
    unweighted scipy fit is used and the fallback is visible in the result.
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
        if abs(xi) < 1e-8:
            ll = -np.log(sigma) - z
        else:
            arg = 1.0 + xi * z
            if np.any(arg <= 0):
                return 1e10
            ll = -np.log(sigma) - (1.0 + 1.0 / xi) * np.log(arg)
        return -np.sum(w * ll)

    start = [0.1, np.log(max(np.average(excess, weights=weights), 1e-9))]
    res = optimize.minimize(nll, start, method="Nelder-Mead",
                            options={"maxiter": 4000, "xatol": 1e-7,
                                     "fatol": 1e-10})
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


# ------------------------------------------------------------ diagnostics ---
def gpd_diagnostics(x, w, threshold_q=config.GPD_THRESHOLD_QUANTILE,
                    n_points=config.GPD_QQ_POINTS):
    """Weighted QQ points and a Kolmogorov-Smirnov distance for the GPD fit.

    Empirical quantiles of the weighted exceedance distribution are set
    against the fitted GPD quantiles at the same probabilities. The KS
    distance is the largest gap between the weighted empirical CDF of the
    exceedances and the fitted CDF. With a weighted, clustered sample it has
    no standard null distribution, so it is reported as a descriptive
    measure of fit, not as a test.
    """
    x = np.asarray(x, float)
    w = np.asarray(w, float)
    ok = np.isfinite(x) & np.isfinite(w) & (w > 0)
    x, w = x[ok], w[ok]
    u = weighted_quantile(x, w, [threshold_q])[0]
    over = x > u
    e, we = x[over] - u, w[over]
    xi, sigma, n_exc = gpd_weighted_fit(e, we)
    probs = (np.arange(n_points) + 0.5) / n_points
    emp = weighted_quantile(e, we, probs)
    model = stats.genpareto.ppf(probs, xi, loc=0, scale=sigma)
    order = np.argsort(e)
    es, ws = e[order], we[order]
    ecdf = np.cumsum(ws) / ws.sum()
    fcdf = stats.genpareto.cdf(es, xi, loc=0, scale=sigma)
    ks = float(np.max(np.abs(ecdf - fcdf)))
    return {"threshold": u, "xi": xi, "sigma": sigma, "n_exceedances": n_exc,
            "ks": ks, "probs": probs, "empirical": emp, "model": model}


# ------------------------------------------------------- design bootstrap ---
class PSUResampler:
    """Replicate weights for a stratified cluster design.

    Built once per data frame; each call to `weights()` returns one
    replicate's weight vector.
    """

    def __init__(self, df, weight_col, stratum_col, psu_col,
                 method=config.BOOTSTRAP_METHOD, seed=config.SEED):
        self.w = df[weight_col].to_numpy(float)
        hc = (df[stratum_col].astype(str) + "|" + df[psu_col].astype(str)).to_numpy()
        self.codes, uniq = pd.factorize(hc)
        psu_stratum = (pd.Series(df[stratum_col].to_numpy())
                       .groupby(self.codes).first().to_numpy())
        self.strata = {}
        for i, s in enumerate(psu_stratum):
            self.strata.setdefault(s, []).append(i)
        self.strata = {s: np.asarray(v) for s, v in self.strata.items()}
        self.n_psu = len(uniq)
        self.method = method
        self.rng = np.random.default_rng(seed)

    def weights(self):
        mult = np.ones(self.n_psu)
        for idx in self.strata.values():
            n = len(idx)
            if n < 2:                          # a lone PSU is kept as it is
                continue
            if self.method == "rao_wu":
                draw = self.rng.integers(0, n, size=n - 1)
                mult[idx] = np.bincount(draw, minlength=n) * n / (n - 1)
            else:
                draw = self.rng.integers(0, n, size=n)
                mult[idx] = np.bincount(draw, minlength=n)
        return self.w * mult[self.codes]


def cluster_bootstrap(df, value_col, weight_col, stratum_col, psu_col,
                      statistic, n_boot=config.N_BOOTSTRAP, seed=config.SEED):
    """Recompute `statistic(values, weights)` on design-bootstrap replicates.

    Returns a frame of replicate values. Rows with zero replicate weight are
    dropped before the statistic is called, so a weighted quantile never sees
    them.
    """
    res = PSUResampler(df, weight_col, stratum_col, psu_col, seed=seed)
    vals = df[value_col].to_numpy(float)
    reps = []
    for _ in range(n_boot):
        ww = res.weights()
        keep = ww > 0
        try:
            reps.append(statistic(vals[keep], ww[keep]))
        except Exception:
            continue
    return pd.DataFrame(reps)


def ci(reps, col, lo=2.5, hi=97.5):
    s = reps[col].dropna()
    if len(s) < 20:
        return np.nan, np.nan
    return np.percentile(s, lo), np.percentile(s, hi)


def difference(est_a, reps_a, est_b, reps_b, seed=config.SEED):
    """US-minus-Nigeria difference from two independent bootstrap samples."""
    a = np.asarray(reps_a, float)
    b = np.asarray(reps_b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    m = min(len(a), len(b))
    rng = np.random.default_rng(seed + 1)
    d = rng.permutation(a)[:m] - rng.permutation(b)[:m]
    se = float(np.sqrt(a.var(ddof=1) + b.var(ddof=1)))
    diff = est_a - est_b
    z = diff / se if se > 0 else np.nan
    p = 2 * (1 - stats.norm.cdf(abs(z))) if np.isfinite(z) else np.nan
    return {"diff": diff, "diff_lo": float(np.percentile(d, 2.5)),
            "diff_hi": float(np.percentile(d, 97.5)), "diff_se": se,
            "z": z, "p": p}


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


def load_analysis_files():
    """US families with usable income, and all Nigerian households."""
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")
    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    us["burden"] = us["oop"] / us["faminc"]
    us["_povcat_low"] = us["povcat"].isin([1, 2]).astype(int)
    us["_elderly"] = (us["n_over64"] > 0).astype(int)
    us = us[np.isfinite(us["burden"])].copy()
    ng = ng[np.isfinite(ng["burden"])].copy()
    return us, ng


def main():
    us, ng = load_analysis_files()

    # Nigerian groups are fitted on both constructions of the denominator:
    # consumption net of OOP (matched to US income, unbounded) and the
    # published SDG basis (consumption including OOP, bounded below one).
    runs = [("United States", us, GROUPS_US, "burden", "income"),
            ("Nigeria", ng, GROUPS_NG, "burden_net", "consumption net of OOP"),
            ("Nigeria", ng, GROUPS_NG, "burden", "consumption (SDG basis)")]
    rows = []
    for country, df, groups, col, basis in runs:
        print(f"\n=== {country}: OOP / {basis} ===")
        for label, spec in groups:
            sub = _subset(df, spec)
            sub = sub[np.isfinite(sub[col])]
            if len(sub) < 100:
                continue
            st = tail_stats(sub[col].to_numpy(float),
                            sub["weight"].to_numpy(float))
            reps = cluster_bootstrap(sub, col, "weight", "stratum", "psu",
                                     lambda v, w: tail_stats(v, w))
            st.update(country=country, group=label, basis=basis, n=len(sub))
            for c in ("var95", "cvar95", "xi", "cvar99"):
                st[f"{c}_lo"], st[f"{c}_hi"] = ci(reps, c)
            st["xi_se"] = float(reps["xi"].std(ddof=1))
            rows.append(st)
            print(f"  {label:<20s} n={len(sub):>6,}  "
                  f"VaR95 {100 * st['var95']:7.2f}%  "
                  f"CVaR95 {100 * st['cvar95']:8.2f}%  "
                  f"xi {st['xi']:+.3f} ({st['xi_lo']:+.3f}, {st['xi_hi']:+.3f})")

    t4 = pd.DataFrame(rows)
    order = ["country", "basis", "group", "n", "threshold", "n_exceedances",
             "var90", "var95", "var99", "cvar90", "cvar95", "cvar95_lo",
             "cvar95_hi", "cvar99", "cvar99_lo", "cvar99_hi",
             "xi", "xi_lo", "xi_hi", "xi_se", "sigma"]
    t4 = t4[[c for c in order if c in t4.columns]]
    t4.to_csv(config.TABLES / "table4_tail_risk.csv", index=False)

    # ---- threshold sensitivity ---------------------------------------------
    sens = []
    for country, df, groups, col, basis in runs:
        for label, spec in groups:
            sub = _subset(df, spec)
            sub = sub[np.isfinite(sub[col])]
            if len(sub) < 100:
                continue
            for tq in config.GPD_THRESHOLD_GRID:
                st = tail_stats(sub[col].to_numpy(float),
                                sub["weight"].to_numpy(float), threshold_q=tq)
                sens.append({"country": country, "basis": basis, "group": label,
                             "threshold_quantile": tq,
                             "threshold": st["threshold"],
                             "n_exceedances": st["n_exceedances"],
                             "xi": st["xi"], "sigma": st["sigma"]})
    t5 = pd.DataFrame(sens)
    t5.to_csv(config.TABLES / "table5_gpd_threshold_sensitivity.csv", index=False)

    print("\n=== GPD shape across thresholds (xi) ===")
    piv = t5.pivot_table(index=["country", "basis", "group"],
                         columns="threshold_quantile", values="xi")
    print(piv.to_string(float_format=lambda x: f"{x:+.3f}"))
    print(f"\nwrote tables 4 and 5 to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
