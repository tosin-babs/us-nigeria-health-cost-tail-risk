# Financial Protection against Health-Cost Shocks: A Harmonized US–Nigeria Comparison of Catastrophic Spending, Underinsurance, and Out-of-Pocket Tail Risk

Paper 3 of the *Health-Cost Risk and Financial Protection* research programme.

Comparative financial-protection studies report *average* catastrophic-spending
rates. Averages hide the tail, which is where household ruin actually happens.
This paper applies actuarial tail-risk measurement — Value-at-Risk, Conditional
Value-at-Risk, and generalised Pareto tail estimates — to household
out-of-pocket burden in a high-income and a low-income health system on one
harmonised basis, and asks where the two distributions meet.

## Status

Data acquired and both analysis files built. The harmonised burden comparison
runs. Modelling, tail estimation and the manuscript are in progress.

## Data

Both sources are free. Neither is redistributed here.

| Source | What | Access |
|---|---|---|
| MEPS Full-Year Consolidated, 2019–2024 (HC-216, 224, 233, 243, 251, 256) | US household health spending, income, insurance | [AHRQ](https://meps.ahrq.gov/mepsweb/data_stats/download_data_files.jsp) — direct download, no registration |
| MEPS HC-036 Pooled Linkage File (1996–2024) | Common variance structure, required to pool years | Same page |
| Nigeria GHS-Panel wave 5 (2023/24) | Nigerian household spending and consumption | [World Bank Microdata](https://microdata.worldbank.org/index.php/catalog/6410) — free registration |
| World Bank `FP.CPI.TOTL` (USA) | Deflators to 2024 dollars | API, free |
| World Bank `PA.NUS.PRVT.PP` | Private-consumption PPP, for the absolute comparison | API, free |

```bash
# US side - downloads about 45 MB
cd data/raw/meps
for h in h216 h224 h233 h243 h251 h256; do
  curl -sSLO "https://meps.ahrq.gov/mepsweb/data_files/pufs/${h}/${h}dta.zip"
done
curl -sSL -o h36u24.zip "https://meps.ahrq.gov/mepsweb/data_files/pufs/h036/h36u24dta.zip"
for z in *.zip; do unzip -qo "$z"; done
```

The Nigeria side is the output of Paper 2's pipeline
([`nigeria-health-protection-gap`](https://github.com/tosin-babs/nigeria-health-protection-gap)),
copied into `data/derived/` as `nigeria_hh_w5.csv` and `nigeria_ind_w5.csv`.
Run that repository's `run_all.py` to regenerate them from the raw survey.

## Harmonisation

The two surveys do not measure the same things, and the honest response is to
say so rather than force a false equivalence. Every choice is in `config.py`
with its reasoning. The three that matter:

**Resources.** MEPS has income and no consumption; GHS has consumption and
unreliable income. Each country uses its own standard resource measure — WHO
guidance accepts either — so this is explicitly a comparison of *relative*
burden. A PPP-converted absolute comparison is reported alongside, where the
denominators need not match.

**Subsistence floor.** The capacity-to-pay measure needs one. Xu et al. derive
it from food shares, which MEPS cannot support, so the harmonised floor is the
national poverty threshold in both countries. Nigeria's food-share floor is kept
as a country-specific check.

**Underinsurance is an outcome, not a group.** The Commonwealth Fund definition
is itself a burden measure, so stratifying burden by it and then comparing is
circular — it yields the giveaway result that 0% of the "adequately insured" and
72% of the "underinsured" exceed a 10% burden. Comparison groups are insurance
status, which is measured independently of what anyone spent.

## Validation

`build_meps.py` reconstructs the federal poverty threshold from family income
and `POVLEV`, which is an independent check on both the deflation and the
income variable:

| Family size | Derived median | 2024 guideline |
|---|---:|---:|
| 1 | $16,319 | $15,060 |
| 2 | $21,004 | $20,440 |
| 3 | $25,248 | $25,820 |
| 4 | $31,812 | $31,200 |

Pooled MEPS weights gross to 323.8 million people a year in in-scope families,
against 334 million on the person weight; the 3% difference is families out of
scope for part of the year, which carry a zero family weight and are dropped.

## Reproducing

```bash
python3 -m venv .venv
.venv/bin/pip install numpy pandas scipy statsmodels matplotlib
.venv/bin/python python/build_meps.py
```

`python/svy.py` is the shared complex-survey module from Paper 2 — Taylor-
linearised variances for a stratified single-stage cluster design, weighted
quantiles, concentration indices. It is survey-agnostic and used unchanged on
MEPS.

## The research programme

| # | Repository | Subject |
|---|---|---|
| 2 | [`nigeria-health-protection-gap`](https://github.com/tosin-babs/nigeria-health-protection-gap) | Nigeria's protection gap and informal-sector pricing |
| 3 | [`us-nigeria-health-cost-tail-risk`](https://github.com/tosin-babs/us-nigeria-health-cost-tail-risk) | Harmonized US-Nigeria comparison of tail risk |
| 4 | [`aca-risk-pool-subsidy-cliff`](https://github.com/tosin-babs/aca-risk-pool-subsidy-cliff) | ACA individual-market selection after the subsidy cliff |
| 5 | [`medicare-cost-of-aging`](https://github.com/tosin-babs/medicare-cost-of-aging) | Multi-state model of lifetime Medicare cost |
| 6 | [`fair-ml-health-risk-adjustment`](https://github.com/tosin-babs/fair-ml-health-risk-adjustment) | Fair, interpretable ML for risk adjustment |

## Author

Oluwatosin Dorcas Babalola — Georgia State University — obabalola4@student.gsu.edu

## Licence

Code is MIT-licensed. MEPS is a public-use file governed by AHRQ's data-use
agreement; the GHS-Panel microdata are governed by the World Bank Microdata
Library's terms. Neither is redistributed here.
