# Financial Protection against Health-Cost Shocks: A Harmonized US–Nigeria Comparison of Catastrophic Spending, Underinsurance, and Out-of-Pocket Tail Risk

Comparative financial-protection studies report average catastrophic-spending
rates. This paper applies actuarial tail measures (Value-at-Risk, expected
shortfall and generalized Pareto tail estimation) to household out-of-pocket
burden in the United States and Nigeria on one harmonized basis, and tests
whether the tail comparison survives the way each survey's denominator is
built.

## Interactive comparison

**https://us-nigeria-tail-risk.vercel.app**

Put a household's out-of-pocket spending and resources in and see where that
ratio lands on both countries' distributions, switch the Nigerian denominator
between the SDG basis and consumption net of health spending, and see the tail
index under every construction of the denominator. The page carries each
group's quantile function and the published tail statistics, not the microdata.

Build it with `python/export_tool_data.py` then `python/build_tool.py`; both
run as part of `run_all.py`. The export prints the reference values the page
must reproduce.

## Status

Complete draft. The pipeline runs end to end from the raw survey files in a
few minutes and produces every table, figure and the submission `.docx` and
`.pdf`.

**Headline.** Nigerian households exceed a 10% out-of-pocket budget share 2.3
times as often as US families (17.2% against 7.4%) and carry the heavier
burden at every quantile. On the published denominators the generalized
Pareto tail index is +0.672 in the United States and +0.088 in Nigeria, but
that gap is an artifact: the Nigerian SDG consumption aggregate contains the
out-of-pocket spending, so the ratio is bounded below one. On matched
constructions the two indices are +0.672 and +0.581 (p = 0.35), and +0.472
and +0.424 for spending levels in international dollars. Both distributions
are heavy-tailed. Poverty raises the 95th percentile of burden by 25 points in
the United States and 11 in Nigeria once Nigerian poverty is measured on
consumption net of health spending.

## Data

Both sources are free. Neither is redistributed here.

| Source | What | Access |
|---|---|---|
| MEPS Full-Year Consolidated, 2019–2024 (HC-216, 224, 233, 243, 251, 256) | US household health spending, income, insurance, cost barriers, medical debt (2024) | [AHRQ](https://meps.ahrq.gov/mepsweb/data_stats/download_data_files.jsp), direct download, no registration |
| MEPS HC-036 Pooled Linkage File (1996–2024) | Common variance structure, required to pool years | Same page |
| Nigeria GHS-Panel wave 5 (2023/24) | Nigerian household spending, consumption, care-seeking | [World Bank Microdata](https://microdata.worldbank.org/index.php/catalog/6410), free registration |
| World Bank `FP.CPI.TOTL` (USA) | Deflators to 2024 dollars | API, free |
| World Bank `PA.NUS.PRVT.PP` | Private-consumption PPP, for the absolute comparison | API, free |
| Census Bureau `thresh24.xlsx` | 2024 poverty thresholds, for validation | Public, values in `config.py` |

```bash
# US side: downloads about 45 MB
cd data/raw/meps
for h in h216 h224 h233 h243 h251 h256; do
  curl -sSLO "https://meps.ahrq.gov/mepsweb/data_files/pufs/${h}/${h}dta.zip"
done
curl -sSL -o h36u24.zip "https://meps.ahrq.gov/mepsweb/data_files/pufs/h036/h36u24dta.zip"
for z in *.zip; do unzip -qo "$z"; done
```

The Nigeria side is the output of the companion paper's pipeline
([`nigeria-health-protection-gap`](https://github.com/tosin-babs/nigeria-health-protection-gap)),
copied into `data/derived/` as `nigeria_hh_w5.csv` and `nigeria_ind_w5.csv`.
Run that repository's `run_all.py` to regenerate them from the raw survey. The
care-seeking table also needs one file from the raw GHS-Panel CSV release,
`Post Planting Wave 5/Household/sect3_plantingw5.csv`, placed in
`data/raw/ghs_w5/`; without it that table is skipped and the run says so.

## Harmonization

The two surveys do not measure the same things. Every choice is in
`config.py` with its reasoning. The ones that matter:

**Resources and the denominator.** MEPS has income and no consumption; GHS has
consumption and unreliable income. Each country uses its own standard resource
measure, so this is a comparison of relative burden. The Nigerian consumption
aggregate contains the out-of-pocket spending it is divided into, so the SDG
ratio cannot exceed one and a generalized Pareto fit to it must find a light
tail; US income does not, so the US ratio is unbounded. Every tail comparison
is therefore repeated on matched constructions (both denominators excluding
health spending; both including it; both floored at the poverty line), on
two-year income for panel-linked US families, and on spending levels in
international dollars (`python/denominator.py`, Table 4).

**Subsistence floor.** The capacity-to-pay measure needs one. Xu et al. derive
it from food shares, which MEPS cannot support, so the harmonized floor is the
national poverty threshold in both countries. Nigeria's food-share floor is
kept as a check. Half of Nigerian households sit at or below the poverty line;
a household in that position that spends anything on health is counted as
catastrophic, since dropping them would drop the poorest half of the country.
The capacity-to-pay comparison ranges from 10.8% to 39.5% for Nigeria across
floors and nothing rests on it.

**Underinsurance is an outcome, not a group.** The Commonwealth Fund
definition is itself a burden measure, so stratifying burden by it is
circular. Comparison groups are insurance status, which is measured
independently of what anyone spent.

**Poverty in the regressions.** Nigerian poverty position is measured on
consumption net of out-of-pocket spending. Ranking on gross consumption
places a household that spent heavily on health higher in the distribution
and reverses the sign of the poverty coefficient (Table A10).

## Validation

`build_meps.py` reconstructs the poverty threshold from family income and
`POVLEV`. The derived medians match the 2024 Census Bureau thresholds for the
modal family composition of each size to within a dollar:

| Family size | Derived median | Census 2024, modal cell |
|---|---:|---:|
| 1 | $16,319 | $16,320 |
| 2 | $21,004 | $21,006 |
| 3 | $25,248 | $25,249 |
| 4 | $31,812 | $31,812 |

Pooled MEPS weights gross to 323.8 million people a year in in-scope
families, against 334 million on the person weight; the 3% difference is
families out of scope for part of the year, which carry a zero family weight
and are dropped.

## Reproducing

```bash
python3 -m venv .venv
.venv/bin/pip install numpy pandas scipy matplotlib
.venv/bin/python python/run_all.py
```

| Stage | Script | Output |
|---|---|---|
| Build the US family file from MEPS | `python/build_meps.py` | `data/derived/us_family.csv` |
| Put Nigeria on the harmonized basis | `python/build_nigeria.py` | `data/derived/ng_household.csv`, `ng_care.csv` |
| Harmonized catastrophic spending | `python/burden.py` | Tables 1, 1c, 2, 3, A1 |
| Tail risk: VaR, CVaR, GPD | `python/tailrisk.py` | Tables 4, 5 |
| Denominator tests and GPD diagnostics | `python/denominator.py` | Tables 10, 11, 12 |
| Forgone care and medical debt | `python/censoring.py` | Table 13 |
| Parity and crossover | `python/parity.py` | Tables 6, 6b |
| Drivers of the upper tail (RIF) | `python/rif.py` | Table 7 |
| Absolute comparison in PPP dollars | `python/absolute.py` | Table 8 |
| Robustness grid | `python/robustness.py` | Tables 9, 9b, 9c |
| Figures | `python/exhibits.py` | `output/figures/*` |
| Tool payload and page | `python/export_tool_data.py`, `python/build_tool.py` | `tool/` |
| Check the prose against the tables | `python/check_manuscript.py` | pass/fail |
| Submission documents | `python/make_manuscript.py` | `manuscript/*.docx`, `*.pdf` |

Table numbers in `output/tables` are the pipeline's; `make_tables.py` maps
them to the manuscript's numbering. Building the documents needs pandoc
(`brew install pandoc`); the PDF uses headless Chrome rather than LaTeX.

## Methodological notes

**The GPD likelihood is weighted** by the survey weights, so the fit refers
to the population rather than the sample. Confidence intervals come from a
Rao-Wu bootstrap over primary sampling units within strata (n_h minus one
draws, weights rescaled), which is unbiased even in the 35 MEPS strata with two
PSUs; the threshold is re-estimated in every replicate. The US minus Nigeria
difference is tested formally from the two independent bootstrap
distributions.

**Goodness of fit** is reported by quantile-quantile plots and a weighted
Kolmogorov-Smirnov distance (Figure 4, Table A6), with the shape refitted at
five thresholds (Table A5).

**Mechanism.** MEPS cost-barrier items and the 2024 medical-debt item, and the
GHS-Panel reasons for not consulting when ill, are tabulated by burden band,
income and quintile (Table 5). Medical debt rises with burden in the United
States; cost-related forgone care is concentrated among the poorest Nigerian
fifth but is small relative to the catastrophic-spending rate.

`python/svy.py` is the shared complex-survey module from the companion paper:
Taylor-linearized variances for a stratified single-stage cluster design and
weighted quantiles. It is survey-agnostic and used unchanged on MEPS.

## Authors

- Oluwatosin Dorcas Babalola, Department of Actuarial Science and Quantitative Risk Analysis and Management, Georgia State University, Atlanta, GA, USA, obabalola4@student.gsu.edu (corresponding)
- Eniola Zainab Olamilekan, Department of Actuarial Science, University of Lagos, Lagos, Nigeria
- Adebolu Temitope, Department of Epidemiology and Medical Statistics, University of Ibadan, Ibadan, Nigeria

## License

Code is MIT-licensed. MEPS is a public-use file governed by AHRQ's data-use
agreement; the GHS-Panel microdata are governed by the World Bank Microdata
Library's terms. Neither is redistributed here.
