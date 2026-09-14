"""
Paper 3 - Harmonized US-Nigeria comparison of health-cost tail risk.

Central configuration. Every analytic choice lives here, not in the analysis
scripts, so that a reviewer can see the whole basis in one file and the
robustness grid can move any of it.

The harmonisation decisions are the substance of this paper, so they are
documented here at length rather than buried in code.
"""

from pathlib import Path

# ---------------------------------------------------------------- paths ----
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
MEPS = RAW / "meps"
DERIVED = ROOT / "data" / "derived"
TABLES = ROOT / "output" / "tables"
FIGURES = ROOT / "output" / "figures"

for _p in (DERIVED, TABLES, FIGURES):
    _p.mkdir(parents=True, exist_ok=True)

SEED = 2026

# --------------------------------------------------------- survey design ----
# Shared with Paper 2 via svy.py. A singleton PSU is centred on the grand mean
# rather than dropped, matching R's survey package with
# options(survey.lonely.psu = "adjust"); MEPS strata do contain singletons once
# a domain is narrow enough.
LONELY_PSU = "adjust"

# ----------------------------------------------------------- MEPS years ----
# Full-Year Consolidated files. 2024 (HC-256) is the latest release.
# 2020 is kept in the pooled file but flagged: the pandemic suppressed
# utilisation and distorted the cost distribution, so the robustness grid
# refits the tail excluding it.
MEPS_FILES = {
    2019: "h216.dta",
    2020: "h224.dta",
    2021: "h233.dta",
    2022: "h243.dta",
    2023: "h251.dta",
    2024: "h256.dta",
}
MEPS_POOLED_LINKAGE = "h36u24.dta"   # HC-036, common variance structure
PANDEMIC_YEARS = (2020,)
BASE_YEAR = 2024

# CPI-U, all items, United States. World Bank FP.CPI.TOTL (2010 = 100),
# the same series family used for Nigeria in Paper 2.
# https://api.worldbank.org/v2/country/USA/indicator/FP.CPI.TOTL
CPI_TO_BASE = {
    2019: 1.22699,
    2020: 1.21204,
    2021: 1.15765,
    2022: 1.07187,
    2023: 1.02950,
    2024: 1.00000,
}

# ------------------------------------------------- harmonisation choices ----
# The two surveys measure different things, and pretending otherwise would be
# the easiest way to produce a wrong answer. What follows is the explicit
# mapping, with the reasoning.
#
# UNIT. MEPS is a person file with family identifiers; GHS is a household
# file. Burden is computed at family/household level in both, because that is
# the unit that absorbs a medical bill. MEPS families are the annual
# "FAMIDYR" construct within a dwelling unit (DUID).
#
# RESOURCES. MEPS has income and no consumption; GHS has consumption and
# unreliable income. There is no way to make these the same variable, so the
# paper does not try. Each country uses its own standard resource measure -
# WHO's own guidance accepts either - and the comparison is of *relative*
# burden, stated prominently. A PPP-converted absolute comparison is reported
# alongside, where the denominators do not have to match.
#
# SUBSISTENCE. The capacity-to-pay measure needs a subsistence floor. Xu et
# al. derive it from food shares, which MEPS cannot support. The harmonised
# floor is therefore the national poverty threshold in both countries: MEPS
# publishes family income as a percentage of the federal poverty line, and
# Paper 2 already carries Nigeria's national line. Nigeria's food-share-based
# floor is retained as a country-specific check, so the reader can see how
# much the choice of floor moves the Nigerian figure.
RESOURCE_FLOOR = "poverty_line"      # harmonised; "food_share" for Nigeria only
INCOME_FLOOR_USD = 1_000.0           # burden undefined below this; MEPS has
                                     # zero and negative family incomes

# Catastrophic thresholds, identical in both countries.
CHE_BUDGET_THRESHOLDS = (0.10, 0.25, 0.40)
CHE_CTP_THRESHOLD = 0.40
EQ_SCALE_POWER = 0.56                # Xu et al. (2003), applied in both

# Underinsurance, adapted from the Commonwealth Fund biennial survey to what
# MEPS can support. Insured all year AND any of:
#   (a) out-of-pocket excluding premiums >= 10% of family income
#   (b) out-of-pocket >= 5% of family income when income < 200% of poverty
#   (c) deductible >= 5% of income  -- NOT computed; MEPS deductible data are
#       thin, so criterion (c) is omitted and the omission is reported. This
#       makes our underinsurance rate a lower bound.
UNDERINSURED_OOP_SHARE = 0.10
UNDERINSURED_LOW_INCOME_SHARE = 0.05
UNDERINSURED_LOW_INCOME_FPL = 2.00
UNDERINSURED_INCLUDES_DEDUCTIBLE = False

# ------------------------------------------------------- tail-risk model ----
# The point of the paper: averages hide the tail, so measure the tail.
VAR_LEVELS = (0.90, 0.95, 0.99)
CVAR_LEVELS = (0.90, 0.95, 0.99)
# Generalised Pareto fit to exceedances over a high threshold. The threshold
# is chosen as a quantile of the burden distribution; sensitivity over the
# grid is reported, because GPD shape estimates are notoriously
# threshold-sensitive.
GPD_THRESHOLD_QUANTILE = 0.90
GPD_THRESHOLD_GRID = (0.80, 0.85, 0.90, 0.95, 0.975)
# Design bootstrap for every tail statistic. "rao_wu" draws n_h - 1 PSUs with
# replacement in each stratum and rescales the weights by n_h / (n_h - 1)
# (Rao and Wu 1988), which is unbiased for the linearised variance even with
# two PSUs per stratum; "naive" draws n_h and understates the variance by the
# factor (n_h - 1) / n_h. MEPS has 35 strata with two PSUs.
BOOTSTRAP_METHOD = "rao_wu"
N_BOOTSTRAP = 400                    # replicates for every tail interval
GPD_QQ_POINTS = 200                  # probability points in the QQ diagnostic

# ------------------------------------------------ denominator construction ----
# The tail index of a ratio depends on how its denominator is built, so the
# US-Nigeria comparison of tail shape is repeated on matched constructions.
#
# Nigeria's SDG-style consumption aggregate CONTAINS the out-of-pocket spending
# it is divided into (Paper 2, build_data.py), so OOP / consumption < 1 by
# construction and its tail is bounded. US family income does not contain OOP,
# so OOP / income is unbounded. Two matched pairs follow:
#   "net"   OOP over resources excluding health spending:
#           US OOP / income  against  Nigeria OOP / (consumption - OOP)
#   "gross" OOP over resources including health spending:
#           US OOP / (income + OOP)  against  Nigeria OOP / consumption
# Neither pair is exact (income is not consumption), so a conclusion is
# treated as established only if it holds under both.
#
# Low transitory income can make a ratio heavy-tailed mechanically. Two checks:
# floor the denominator at a multiple of the poverty threshold in both
# countries, and (US only) replace one-year income by the two-year average
# for the same persons, using the overlap of MEPS panels across annual files.
DENOMINATOR_POVERTY_FLOOR = 1.0      # floor = this multiple of the poverty line
LINK_ADJACENT_YEAR_INCOME = True     # build the two-year income measure

# Harmonized household composition. The Nigerian file carries members aged
# 60+ and children under 5, so the US covariates use the same cut-offs.
ELDERLY_AGE = 60
CHILD_AGE = 5

# ------------------------------------------------------ access and credit ----
# MEPS round 4/2 items: delayed or could not afford medical care or
# prescription medicines because of cost (1 = yes, 2 = no, negatives missing).
MEPS_COST_BARRIER_VARS = ("DLAYCA42", "AFRDCA42", "DLAYPM42", "AFRDPM42")
# Amount of medical debt (0 = none, 1-7 amount bands). Fielded in 2024 only.
MEPS_MEDICAL_DEBT_VAR = "MEDDEBT42"
# Burden bands for the access and debt tabulation.
BURDEN_BANDS = (0.0, 0.10, 0.40, 1.00, float("inf"))
# GHS-Panel wave 5, post-planting health section (individual level). Needed
# for the reason a sick member consulted no one. Extract it from the World
# Bank CSV release (catalog 6410) into data/raw/ghs_w5/.
NG_HEALTH_SECTION = RAW / "ghs_w5" / "sect3_plantingw5.csv"

# Official poverty thresholds used by MEPS POVLEV are the Census Bureau's, not
# the HHS guidelines. 2024 weighted average thresholds, families of 1-4:
# https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-thresholds/thresh24.xlsx
# The cell used is the modal family type for each size: one person under 65;
# two people, householder under 65, no children; three people with one child;
# four people with two children. The weighted averages are shown alongside.
CENSUS_THRESHOLDS_2024 = {1: 16_320, 2: 21_006, 3: 25_249, 4: 31_812}
CENSUS_WEIGHTED_AVERAGE_2024 = {1: 15_940, 2: 20_220, 3: 24_950, 4: 32_130}
HHS_GUIDELINES_2024 = {1: 15_060, 2: 20_440, 3: 25_820, 4: 31_200}

# Parity: the percentile at which a US subgroup's burden reaches a Nigerian
# reference burden. Reported against the Nigerian informal median and upper
# quartile.
PARITY_REFERENCE_QUANTILES = (0.50, 0.75)

# --------------------------------------------------------------- Nigeria ----
# Built by Paper 2 and copied in; see README for provenance. Naira are in
# constant August-2023 prices there.
NIGERIA_HH = DERIVED / "nigeria_hh_w5.csv"
NIGERIA_IND = DERIVED / "nigeria_ind_w5.csv"
NGN_PRICE_BASE = "August 2023"

# PPP conversion for the absolute comparison. World Bank PA.NUS.PRVT.PP,
# private-consumption PPP, naira per international dollar.  [VERIFY at write-up]
PPP_NGN_PER_INTL_USD = None          # filled by build_nigeria.py from the API

# --------------------------------------------------------------- plotting ----
FIG_DPI = 300
PALETTE = {
    "us": "#1B4F72",
    "us_light": "#5499C7",
    "ng": "#A04000",
    "ng_light": "#DC7633",
    "ink": "#1A1A1A",
    "muted": "#7F8C8D",
    "rule": "#D5D8DC",
    "accent": "#117A65",
    "warn": "#B7950B",
}
