# Financial Protection against Health-Cost Shocks: A Harmonized US–Nigeria Comparison of Catastrophic Spending, Underinsurance, and Out-of-Pocket Tail Risk

Paper 3 of the *Health-Cost Risk and Financial Protection* research programme.

Comparative financial-protection studies report *average* catastrophic-spending
rates. Averages hide the tail, which is where household ruin actually happens.
This paper applies actuarial tail-risk measurement — Value-at-Risk, Conditional
Value-at-Risk, and generalised Pareto tail estimates — to household
out-of-pocket burden in a high-income and a low-income health system on one
harmonised basis, and asks where the two distributions meet.

## Status

Complete draft. The pipeline runs end to end from the raw survey files in about
30 seconds and produces every table, figure and the submission `.docx` and
`.pdf`.

**Headline.** Nigeria has 2.4 times the catastrophic-spending rate of the United
States (17.2% against 7.2% above a 10% burden). The United States has the far
heavier tail: a generalised Pareto shape of **+0.672** against **+0.088**, with
no overlap between any US and any Nigerian group at any threshold tested. Expected
shortfall at the 95th percentile is already higher in the US (42.9% of resources
against 38.1%), and reaches **124.7% of annual income** among poor and near-poor
US families. The two burden distributions have essentially met by the 99th
percentile (42.1% against 48.2%).

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
.venv/bin/python python/run_all.py
```

| Stage | Script | Output |
|---|---|---|
| Build the US family file from MEPS | `python/build_meps.py` | `data/derived/us_family.csv` |
| Put Nigeria on the harmonised basis | `python/build_nigeria.py` | `data/derived/ng_household.csv` |
| Harmonised catastrophic spending | `python/burden.py` | Tables 1–3 |
| Tail risk: VaR, CVaR, GPD | `python/tailrisk.py` | Tables 4–5 |
| Parity and crossover | `python/parity.py` | Tables 6, 6b |
| Figures | `python/exhibits.py` | `output/figures/*` |
| Check the prose against the tables | `python/check_manuscript.py` | pass/fail |
| Submission documents | `python/make_manuscript.py` | `manuscript/*.docx`, `*.pdf` |

Building the documents needs pandoc (`brew install pandoc`); the PDF uses
headless Chrome rather than LaTeX.

## Two methodological notes

**The GPD likelihood is weighted.** An ordinary maximum-likelihood fit would
treat a household representing 40,000 others the same as one representing 400.
Confidence intervals come from a bootstrap over primary sampling units within
strata, not a naive resample, and propagate through the shape parameter.

**Half of Nigerian households have no capacity to pay.** They sit at or below
the national poverty line, so the capacity-to-pay ratio is undefined for them.
Dropping them would drop the poorest half of the country. A household below the
subsistence floor that spends anything on health is sacrificing subsistence to
do it, so it counts as catastrophic whenever out-of-pocket spending is positive,
and the share in that position is reported in every table — 49.9% in Nigeria
against 12.7% in the United States.

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
