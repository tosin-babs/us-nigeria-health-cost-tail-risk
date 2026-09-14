"""
What drives the upper tail? Unconditional quantile regression.

An ordinary regression of burden on household characteristics describes the
mean. A conditional quantile regression describes a quantile of the
conditional distribution, which is not the quantity anyone wants here: the
policy question is what moves the 90th percentile of the burden distribution
*in the population*, not the 90th percentile among households that happen to
share a covariate profile.

Firpo, Fortin and Lemieux (2009) give the estimator for that. Replace the
outcome with its recentered influence function for the statistic of interest,

    RIF(y; q_tau) = q_tau + (tau - 1{y <= q_tau}) / f(q_tau)

and regress it on the covariates by least squares. The coefficient is the
effect of a marginal shift in the covariate distribution on the unconditional
quantile. The density at the quantile is estimated by a Gaussian kernel with a
Silverman bandwidth, both weighted.

Standard errors are clustered on the primary sampling unit, which is the
design feature that matters most here; the strata contribute a finite-
population correction we conservatively ignore. The density in the RIF is
held fixed at its full-sample estimate, so the standard errors do not carry
the sampling variability of the density; that is the usual practice and the
usual caveat.

The cluster is the stratum-PSU *pair*, not the PSU label. MEPS numbers PSUs
within strata, so eight labels are reused across 117 strata; clustering on the
label alone would pool PSU 1 of stratum 1 with PSU 1 of stratum 50 and leave
eight clusters instead of 411, which is far too few for cluster-robust
inference to mean anything.

Writes Table 7.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import config
from svy import weighted_quantile

QUANTILES = (0.50, 0.75, 0.90, 0.95)


def weighted_kde_at(x, w, point, bandwidth=None):
    """Weighted Gaussian kernel density estimate at a single point."""
    x = np.asarray(x, float)
    w = np.asarray(w, float) / np.sum(w)
    if bandwidth is None:
        mean = np.sum(w * x)
        sd = np.sqrt(np.sum(w * (x - mean) ** 2))
        iqr = (weighted_quantile(x, w, [0.75])[0]
               - weighted_quantile(x, w, [0.25])[0])
        spread = min(sd, iqr / 1.349) if iqr > 0 else sd
        n_eff = 1.0 / np.sum(w ** 2)          # Kish effective sample size
        bandwidth = 0.9 * spread * n_eff ** (-0.2)
    if bandwidth <= 0:
        return np.nan
    z = (point - x) / bandwidth
    return float(np.sum(w * np.exp(-0.5 * z ** 2)) / (bandwidth * np.sqrt(2 * np.pi)))


def rif_quantile(y, w, tau):
    """Recentered influence function of the tau-th unconditional quantile."""
    y = np.asarray(y, float)
    q = weighted_quantile(y, w, [tau])[0]
    f = weighted_kde_at(y, w, q)
    if not np.isfinite(f) or f <= 0:
        return None, q, f
    return q + (tau - (y <= q).astype(float)) / f, q, f


def wls_cluster(X, y, w, cluster):
    """Weighted least squares with cluster-robust (CR0) standard errors."""
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    w = np.asarray(w, float)
    W = w / w.mean()

    XtWX = X.T @ (X * W[:, None])
    XtWX_inv = np.linalg.pinv(XtWX)
    beta = XtWX_inv @ (X.T @ (W * y))
    resid = y - X @ beta

    # Sum the score over clusters before squaring: that is what makes the
    # estimator robust to arbitrary within-cluster correlation.
    meat = np.zeros((X.shape[1], X.shape[1]))
    order = np.argsort(cluster)
    cl = np.asarray(cluster)[order]
    Xs, rs, Ws = X[order], resid[order], W[order]
    bounds = np.flatnonzero(np.r_[True, cl[1:] != cl[:-1], True])
    for a, b in zip(bounds[:-1], bounds[1:]):
        u = (Xs[a:b] * (Ws[a:b] * rs[a:b])[:, None]).sum(axis=0)
        meat += np.outer(u, u)

    n_cl = len(bounds) - 1
    scale = n_cl / max(n_cl - 1, 1)
    V = XtWX_inv @ (scale * meat) @ XtWX_inv
    return beta, np.sqrt(np.maximum(np.diag(V), 0))


def design_matrix(df, spec):
    """Build X and the column names from a spec of {name: series}."""
    cols, names = [np.ones(len(df))], ["(intercept)"]
    for name, series in spec.items():
        v = np.asarray(series, float)
        cols.append(v)
        names.append(name)
    return np.column_stack(cols), names


def run_country(df, spec, label, weight_col="weight", psu_col="psu",
                stratum_col="stratum"):
    y = df["burden"].to_numpy(float)
    w = df[weight_col].to_numpy(float)
    cl = (df[stratum_col].astype(str) + "_" + df[psu_col].astype(str)).to_numpy()
    X, names = design_matrix(df, spec)

    rows = []
    for tau in QUANTILES:
        r, q, f = rif_quantile(y, w, tau)
        if r is None:
            print(f"  {label} q{int(100 * tau)}: density at the quantile is "
                  f"zero, skipped")
            continue
        beta, se = wls_cluster(X, r, w, cl)
        for nm, b, s in zip(names, beta, se):
            rows.append({"country": label, "quantile": tau,
                         "unconditional_quantile_pct": 100 * q,
                         "term": nm, "coef_pp": 100 * b, "se_pp": 100 * s,
                         "t": b / s if s > 0 else np.nan,
                         "n": len(df), "n_clusters": len(np.unique(cl))})
    return pd.DataFrame(rows)


def ng_spec(ng, basis="net"):
    """Nigerian covariates, with poverty on gross or net-of-OOP consumption."""
    res = ng["resources_net"] if basis == "net" else ng["resources"]
    pc = res / ng["n_persons"].clip(lower=1)
    line = ng["poverty_threshold"] / ng["n_persons"].clip(lower=1)
    return {
        "Below the poverty line": (pc < line).astype(float),
        "1-2x the poverty line": ((pc >= line) & (pc < 2 * line)).astype(float),
        "Uninsured any part of the year": (ng["insured"] == 0).astype(float),
        "Any chronic condition": ng["any_chronic"].astype(float),
        f"Any member aged {config.ELDERLY_AGE}+": (ng["n_over60"] > 0).astype(float),
        f"Any child under {config.CHILD_AGE}": (ng["n_under5"] > 0).astype(float),
        "Household size": ng["n_persons"].astype(float),
    }


def main():
    us = pd.read_csv(config.DERIVED / "us_family.csv")
    ng = pd.read_csv(config.DERIVED / "ng_household.csv")

    us = us[(us["income_usable"] == 1) & (us["poverty_threshold"] > 0)].copy()
    us["burden"] = us["oop"] / us["faminc"]
    us = us[np.isfinite(us["burden"])].copy()

    ng = ng[np.isfinite(ng["burden"])].copy()

    # Covariates are matched in meaning across the two countries. Income
    # position is relative to each country's own poverty line. Age cut-offs
    # are those the Nigerian file carries (60+, under 5), applied to MEPS too.
    #
    # Nigeria's poverty position is measured on consumption NET of
    # out-of-pocket spending. Gross consumption contains the outcome, so a
    # household that spent heavily on health is mechanically ranked richer;
    # the sign of the poverty coefficient on the gross ranking is an artifact
    # of that (it flips), which is shown in the robustness grid.
    us_spec = {
        "Below the poverty line": (us["povlev"] < 100).astype(float),
        "1-2x the poverty line": us["povlev"].between(100, 200).astype(float),
        "Uninsured any part of the year": (us["insurance_group"]
                                           != "Insured all year").astype(float),
        "Any chronic condition": us["any_chronic"].astype(float),
        f"Any member aged {config.ELDERLY_AGE}+":
            (us["n_elderly_h"] > 0).astype(float),
        f"Any child under {config.CHILD_AGE}": (us["n_child_h"] > 0).astype(float),
        "Household size": us["n_persons"].astype(float),
    }
    out = pd.concat([run_country(us, us_spec, "United States"),
                     run_country(ng, ng_spec(ng, "net"), "Nigeria")],
                    ignore_index=True)
    out.to_csv(config.TABLES / "table7_rif.csv", index=False)

    print("\n=== Unconditional quantile regression of burden (pp per unit) ===")
    print("    coefficient is the effect on that percentile of the burden")
    print("    distribution, in percentage points of resources\n")
    for country in ("United States", "Nigeria"):
        sub = out[(out["country"] == country) & (out["term"] != "(intercept)")]
        piv = sub.pivot_table(index="term", columns="quantile", values="coef_pp")
        sig = sub.pivot_table(index="term", columns="quantile", values="t")
        piv.columns = [f"q{int(100 * c)}" for c in piv.columns]
        marked = piv.copy().astype(object)
        for i, col in enumerate(piv.columns):
            for term in piv.index:
                v = piv.loc[term, col]
                tv = sig.loc[term, sig.columns[i]]
                star = "*" if abs(tv) > 1.96 else " "
                marked.loc[term, col] = f"{v:+7.2f}{star}"
        print(f"  {country}  (n={int(sub['n'].iloc[0]):,}, "
              f"{int(sub['n_clusters'].iloc[0]):,} clusters)")
        print(marked.to_string())
        print()
    print("  * |t| > 1.96 on cluster-robust standard errors")
    print(f"\nwrote table 7 to {config.TABLES.relative_to(config.ROOT)}")


if __name__ == "__main__":
    main()
