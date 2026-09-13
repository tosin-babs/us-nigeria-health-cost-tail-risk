"""
Build the US analysis file from MEPS Full-Year Consolidated public-use files.

MEPS is a person file. Health-cost burden is felt by the family, so persons are
aggregated to the annual family (DUID + FAMIDYR) and every burden measure is
computed at that level. Six years are pooled to give the tail enough
exceedances to fit; pooling requires the HC-036 linkage file, which carries a
variance structure common to all years, and weights divided by the number of
years.

Writes data/derived/us_family.csv.
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd

import config

warnings.filterwarnings("ignore", category=FutureWarning)

# Variables needed from each yearly file, with the year suffix filled in.
PERSON_VARS = [
    "DUID", "PID", "DUPERSID", "FAMIDYR", "PANEL",
    "TOTEXP{yy}",   # total health expenditure, all sources
    "TOTSLF{yy}",   # paid by self or family - our out-of-pocket measure
    "PERWT{yy}F",   # person weight
    "FAMWT{yy}F",   # family weight
    "VARSTR", "VARPSU",
    "INSCOV{yy}",   # 1 any private, 2 public only, 3 uninsured (all year)
    "INSURC{yy}",   # finer coverage detail, including part-year
    "POVCAT{yy}",   # poverty category
    "POVLEV{yy}",   # family income as % of the poverty line
    "FAMINC{yy}",   # family income
    "TTLP{yy}X",    # person total income
    "AGE{yy}X", "SEX", "RACETHX", "REGION{yy}",
    "FAMSZE{yy}",
]

# Priority-condition flags, used for the chronic indicator. MEPS renamed these
# with an _M18 suffix from 2018 onward.
CHRONIC = ["HIBPDX", "CHDDX", "STRKDX", "EMPHDX", "CHOLDX", "CANCERDX",
           "DIABDX_M18", "ARTHDX", "ASTHDX"]


def _yearly(year: int, path) -> pd.DataFrame:
    yy = str(year)[-2:]
    wanted = [v.format(yy=yy) for v in PERSON_VARS] + CHRONIC

    it = pd.read_stata(path, iterator=True)
    available = set(it.variable_labels().keys())
    use = [c for c in wanted if c in available]
    missing = [c for c in wanted if c not in available]

    d = pd.read_stata(path, columns=use, convert_categoricals=False)
    # Rename explicitly. A generic strip of the year suffix is a trap here:
    # "FAMWT23F" loses both of its F's to a naive replace and becomes "AMWT".
    ren = {f"PERWT{yy}F": "perwt", f"FAMWT{yy}F": "famwt",
           f"TOTEXP{yy}": "total_exp", f"TOTSLF{yy}": "oop",
           f"INSCOV{yy}": "inscov", f"INSURC{yy}": "insurc",
           f"POVCAT{yy}": "povcat", f"POVLEV{yy}": "povlev",
           f"FAMINC{yy}": "faminc", f"TTLP{yy}X": "person_income",
           f"AGE{yy}X": "age", f"REGION{yy}": "region",
           f"FAMSZE{yy}": "famsize"}
    d = d.rename(columns={k: v for k, v in ren.items() if k in d.columns})
    d["year"] = year

    have_chronic = [c for c in CHRONIC if c in d.columns]
    # MEPS codes 1 = yes; negatives are the various non-response codes.
    d["chronic"] = (d[have_chronic] == 1).any(axis=1).astype(int) if have_chronic else 0

    return d, missing


def load_meps() -> pd.DataFrame:
    frames, notes = [], {}
    for year, fname in config.MEPS_FILES.items():
        path = config.MEPS / fname
        if not path.exists():
            raise SystemExit(f"missing {path}; see README for the download step")
        d, missing = _yearly(year, path)
        frames.append(d)
        notes[year] = missing
        print(f"  {year}: {len(d):>7,} persons"
              + (f"   missing: {missing}" if missing else ""))
    return pd.concat(frames, ignore_index=True), notes


def attach_pooled_variance(d: pd.DataFrame) -> pd.DataFrame:
    """Swap in the common variance structure required for pooling years.

    Each yearly file carries VARSTR/VARPSU valid for that year alone. HC-036
    provides strata and PSU codes that are consistent across 1996-2024, which
    is what makes a pooled standard error meaningful.
    """
    path = config.MEPS / config.MEPS_POOLED_LINKAGE
    link = pd.read_stata(path, convert_categoricals=False)
    cols = {c.upper(): c for c in link.columns}
    keep = {}
    for want in ("DUPERSID", "PANEL"):
        if want in cols:
            keep[cols[want]] = want
    # The pooled strata/PSU are named for the span they cover, e.g. VARSTR /
    # VARPSU or STRA9624 / PSU9624 depending on the release.
    for c in link.columns:
        u = c.upper()
        if u.startswith(("STRA", "VARSTR")):
            keep[c] = "pooled_stratum"
        elif u.startswith(("PSU", "VARPSU")):
            keep[c] = "pooled_psu"
    link = link[list(keep)].rename(columns=keep)
    print(f"  linkage file: {len(link):,} rows, columns {list(link.columns)}")

    before = len(d)
    on = ["DUPERSID", "PANEL"] if "PANEL" in link.columns and "PANEL" in d.columns \
        else ["DUPERSID"]
    d = d.merge(link.drop_duplicates(on), on=on, how="left")
    matched = d["pooled_stratum"].notna().sum()
    print(f"  matched {matched:,} of {before:,} persons "
          f"({100 * matched / before:.1f}%) to the pooled variance structure")
    # Anyone unmatched keeps the single-year structure, which is the safe
    # fallback: it cannot make the design better than it is, only cruder.
    d["pooled_stratum"] = d["pooled_stratum"].fillna(d["VARSTR"])
    d["pooled_psu"] = d["pooled_psu"].fillna(d["VARPSU"])
    return d


def to_families(d: pd.DataFrame) -> pd.DataFrame:
    """Aggregate persons to annual families and build the burden measures."""
    d = d.copy()
    # Deflate every dollar amount to the base year before anything is summed.
    defl = d["year"].map(config.CPI_TO_BASE)
    for c in ("total_exp", "oop", "faminc", "person_income"):
        if c in d.columns:
            d[c] = d[c] * defl

    d["fam_id"] = (d["year"].astype(str) + "_" + d["DUID"].astype(str)
                   + "_" + d["FAMIDYR"].astype(str))

    agg = d.groupby("fam_id").agg(
        year=("year", "first"),
        oop=("oop", "sum"),
        total_exp=("total_exp", "sum"),
        n_persons=("DUPERSID", "size"),
        n_chronic=("chronic", "sum"),
        any_chronic=("chronic", "max"),
        n_uninsured=("inscov", lambda s: int((s == 3).sum())),
        n_public_only=("inscov", lambda s: int((s == 2).sum())),
        n_private=("inscov", lambda s: int((s == 1).sum())),
        age_max=("age", "max"),
        age_mean=("age", "mean"),
        n_over64=("age", lambda s: int((s >= 65).sum())),
        n_under18=("age", lambda s: int((s < 18).sum())),
        faminc=("faminc", "first"),
        povlev=("povlev", "first"),
        povcat=("povcat", "first"),
        famsize=("famsize", "first"),
        region=("region", "first"),
        racethx=("RACETHX", "first"),
        famwt=("famwt", "first"),
        stratum=("pooled_stratum", "first"),
        psu=("pooled_psu", "first"),
    ).reset_index()

    # MEPS gives a zero family weight to units out of scope for the full year.
    # They contribute nothing to any weighted estimate, so carrying them only
    # inflates the unweighted n and misstates the sample size in a table.
    zero = int((agg["famwt"] <= 0).sum())
    persons_lost = int(agg.loc[agg["famwt"] <= 0, "n_persons"].sum())
    agg = agg[agg["famwt"] > 0].copy()
    print(f"  dropped {zero:,} family-years with a zero weight "
          f"({persons_lost:,} persons, out of scope for the full year)")

    # Pooling: each year's weight represents that year's population, so the
    # pooled weight is divided by the number of years to keep totals sane.
    n_years = d["year"].nunique()
    agg["weight"] = agg["famwt"] / n_years

    # Coverage group for the whole family-year.
    agg["all_uninsured"] = (agg["n_uninsured"] == agg["n_persons"]).astype(int)
    agg["any_uninsured"] = (agg["n_uninsured"] > 0).astype(int)
    agg["all_insured"] = (agg["n_uninsured"] == 0).astype(int)

    # Burden. Families with implausibly low income cannot support a ratio;
    # they are flagged rather than dropped, so the exclusion is visible.
    agg["income_usable"] = (agg["faminc"] >= config.INCOME_FLOOR_USD).astype(int)
    inc = agg["faminc"].where(agg["faminc"] >= config.INCOME_FLOOR_USD)
    agg["burden"] = agg["oop"] / inc

    # Capacity to pay, on the harmonised poverty-line floor. POVLEV is family
    # income as a percentage of the poverty threshold, so the threshold itself
    # is income / (povlev/100).
    pov_threshold = np.where(agg["povlev"] > 0,
                             agg["faminc"] / (agg["povlev"] / 100.0), np.nan)
    agg["poverty_threshold"] = pov_threshold
    ctp = (agg["faminc"] - pov_threshold)
    agg["ctp"] = np.where(ctp > 0, ctp, np.nan)
    agg["burden_ctp"] = agg["oop"] / agg["ctp"]

    agg["eqsize"] = agg["n_persons"] ** config.EQ_SCALE_POWER
    agg["popwt"] = agg["weight"] * agg["n_persons"]
    agg["country"] = "US"
    return agg


def add_underinsurance(fam: pd.DataFrame) -> pd.DataFrame:
    """Commonwealth-style underinsurance, at family level, without criterion (c)."""
    insured = fam["all_insured"] == 1
    low_income = fam["povlev"] < 100 * config.UNDERINSURED_LOW_INCOME_FPL
    high_burden = fam["burden"] >= config.UNDERINSURED_OOP_SHARE
    low_income_burden = low_income & (fam["burden"]
                                      >= config.UNDERINSURED_LOW_INCOME_SHARE)
    fam["underinsured"] = (insured & fam["income_usable"].astype(bool)
                           & (high_burden | low_income_burden)).astype(int)

    # Underinsurance is defined *by* the burden measure, so it cannot also
    # serve as a stratifier for burden: grouping families that way and then
    # comparing catastrophic spending across the groups is circular, and
    # produces the giveaway result that 0% of the "adequately insured" and 72%
    # of the "underinsured" exceed a 10% burden. The comparison groups are
    # therefore insurance status alone, which is measured independently of
    # what anyone spent. Underinsurance is reported as an outcome in its own
    # right, never as a group.
    fam["insurance_group"] = np.select(
        [fam["all_uninsured"] == 1, fam["any_uninsured"] == 1],
        ["Uninsured all year", "Partly uninsured"],
        default="Insured all year")
    return fam


def main():
    print("Loading MEPS Full-Year Consolidated files ...")
    d, notes = load_meps()
    print(f"  pooled: {len(d):,} person-years, {d['year'].nunique()} years\n")

    print("Attaching the pooled variance structure ...")
    d = attach_pooled_variance(d)

    print("\nAggregating to annual families ...")
    fam = to_families(d)
    fam = add_underinsurance(fam)

    print(f"  {len(fam):,} family-years")
    print(f"  {fam['income_usable'].sum():,} with usable income "
          f"({100 * fam['income_usable'].mean():.1f}%)")
    print(f"  weighted families per year: "
          f"{fam['weight'].sum() / 1e6:,.1f} million")
    print(f"  weighted persons per year:  "
          f"{fam['popwt'].sum() / 1e6:,.1f} million")
    print("  (MEPS person weights gross to about 334 million; the family "
          "weight\n   covers the population living in in-scope families, "
          "about 3% fewer)")

    print("\nInsurance status (weighted share of families):")
    w = fam.groupby("insurance_group")["weight"].sum()
    for k, v in (100 * w / w.sum()).sort_values(ascending=False).items():
        print(f"  {k:<24s} {v:5.2f}%")
    ui = fam[fam["all_insured"] == 1]
    share = 100 * (ui["underinsured"] * ui["weight"]).sum() / ui["weight"].sum()
    print(f"\n  Underinsured, among families insured all year: {share:.2f}%")
    print("  (reported as an outcome, not used as a comparison group; "
          "excludes\n   the deductible criterion, so it is a lower bound)")

    out = config.DERIVED / "us_family.csv"
    fam.to_csv(out, index=False)
    print(f"\nwrote {out.relative_to(config.ROOT)}  ({len(fam):,} rows)")


if __name__ == "__main__":
    main()
