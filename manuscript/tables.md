# Tables

*Generated from `output/tables/*.csv` by `python/make_tables.py`. All estimates are survey-weighted with Taylor-linearized standard errors for a stratified single-stage cluster design. US amounts are in constant 2024 dollars; Nigerian amounts in constant August 2023 naira. Burden is out-of-pocket (OOP) spending over family income in the United States. For Nigeria the published (SDG) basis divides by household consumption, which contains OOP; the matched basis divides by consumption net of OOP. Each table states which is used.*


**Table 1.** Catastrophic spending on harmonized definitions.

*Budget share is OOP over income (US) or over consumption on the SDG basis (Nigeria). Capacity to pay is resources net of the national poverty threshold; a household at or below the threshold is counted as catastrophic whenever it spends anything.*

| Country | Measure | Estimate % | SE | 95% low | 95% high | n |
|---|---:|---:|---:|---:|---:|---:|
| United States | Budget share > 10% | 7.39 | 0.16 | 7.08 | 7.70 | 61,447 |
| United States | Budget share > 25% | 2.25 | 0.08 | 2.09 | 2.41 | 61,447 |
| United States | Budget share > 40% | 1.10 | 0.06 | 0.99 | 1.21 | 61,447 |
| United States | Capacity to pay >= 40% | 10.98 | 0.25 | 10.48 | 11.47 | 61,447 |
| United States | No capacity to pay (at or below the floor) | 10.18 | 0.27 | 9.65 | 10.72 | 61,447 |
| Nigeria | Budget share > 10% | 17.24 | 0.80 | 15.66 | 18.82 | 4,685 |
| Nigeria | Budget share > 25% | 5.01 | 0.48 | 4.06 | 5.95 | 4,685 |
| Nigeria | Budget share > 40% | 1.56 | 0.25 | 1.08 | 2.04 | 4,685 |
| Nigeria | Capacity to pay >= 40% | 39.51 | 1.20 | 37.16 | 41.86 | 4,685 |
| Nigeria | No capacity to pay (at or below the floor) | 49.87 | 1.34 | 47.25 | 52.50 | 4,685 |

**Table 2.** The burden distribution by quantile, on the published and the matched constructions of the denominator.

*Published: US OOP over income, Nigeria OOP over consumption (SDG basis). Matched net: both over resources excluding OOP, so the US column is unchanged and the Nigerian one is OOP over consumption net of OOP. Matched gross: both over resources including OOP, so the US column becomes OOP over income plus OOP and the Nigerian one is unchanged.*

| Quantile | US, published % | Nigeria, published % | Ratio NG / US | Nigeria, net of OOP % | US, income plus OOP % |
|---|---:|---:|---:|---:|---:|
| q25 | 0.24 | 0.00 | 0.00 | 0.00 | 0.24 |
| q50 | 1.06 | 1.88 | 1.78 | 1.92 | 1.05 |
| q75 | 3.16 | 6.71 | 2.13 | 7.20 | 3.06 |
| q90 | 7.87 | 16.31 | 2.07 | 19.49 | 7.30 |
| q95 | 13.55 | 25.01 | 1.84 | 33.35 | 11.94 |
| q99 | 42.13 | 48.19 | 1.14 | 93.03 | 29.64 |

**Table 3.** Tail-risk measures of the out-of-pocket burden by group, matched net construction.

*US burden is OOP over family income; Nigerian burden is OOP over consumption net of OOP. VaR is the quantile of the burden distribution; CVaR is the mean burden at or above it. xi is the generalized Pareto shape fitted by weighted maximum likelihood to exceedances over the 90th percentile, with 95% intervals from a Rao-Wu bootstrap over primary sampling units within strata. xi above 0.5 implies infinite variance. The same Nigerian groups on the SDG basis are in Table A4.*

| Country | Group | n | Exceedances | VaR95 % | CVaR95 % | 95% low | 95% high | CVaR99 % | xi | xi low | xi high |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| United States | All families | 61,447 | 6,746 | 13.55 | 42.90 | 38.16 | 47.51 | 125.75 | +0.672 | +0.615 | +0.715 |
| United States | Insured all year | 55,173 | 6,109 | 13.60 | 42.49 | 38.04 | 48.14 | 124.93 | +0.659 | +0.607 | +0.715 |
| United States | Partly uninsured | 4,282 | 433 | 12.94 | 48.52 | 34.43 | 66.60 | 145.32 | +0.737 | +0.567 | +0.951 |
| United States | Uninsured all year | 1,992 | 215 | 14.40 | 42.12 | 32.40 | 53.37 | 98.17 | +0.594 | +0.316 | +0.881 |
| United States | Poor or near poor | 11,735 | 1,112 | 34.78 | 124.69 | 96.25 | 160.45 | 391.29 | +0.719 | +0.567 | +0.851 |
| United States | Chronic condition | 48,595 | 5,285 | 15.02 | 48.60 | 42.85 | 55.92 | 144.68 | +0.673 | +0.614 | +0.735 |
| United States | Elderly member | 22,606 | 2,353 | 19.62 | 54.18 | 49.27 | 59.74 | 146.73 | +0.637 | +0.556 | +0.713 |
| Nigeria | All households | 4,685 | 455 | 33.35 | 76.20 | 61.31 | 93.93 | 183.11 | +0.581 | +0.364 | +0.738 |
| Nigeria | Informal sector | 3,876 | 378 | 35.25 | 83.75 | 66.32 | 104.27 | 199.32 | +0.568 | +0.350 | +0.763 |
| Nigeria | Formal sector | 809 | 88 | 24.91 | 42.95 | 33.48 | 52.39 | 74.97 | +0.119 | -0.096 | +0.610 |
| Nigeria | Poorest quintile | 700 | 76 | 31.14 | 61.02 | 46.37 | 76.87 | 114.68 | +0.197 | -0.050 | +0.652 |
| Nigeria | Richest quintile | 1,428 | 143 | 41.29 | 121.57 | 85.89 | 164.03 | 294.77 | +0.598 | +0.288 | +0.944 |
| Nigeria | Rural | 3,205 | 311 | 36.02 | 87.35 | 67.74 | 109.56 | 216.19 | +0.509 | +0.274 | +0.749 |

**Table 4.** The US-Nigeria difference in tail shape under each construction of the denominator.

*xi is the generalized Pareto shape above the 90th percentile with 95% Rao-Wu bootstrap intervals. The difference is US minus Nigeria, its interval from independently drawn replicates, and p from a Wald test on the two bootstrap standard errors. CVaR95 is in percent of resources for ratio constructions and in 2023 international dollars for levels. Thresholds other than the 90th percentile are in Table A12.*

| Construction | US n | NG n | US xi | low | high | NG xi | low | high | Difference | low | high | p | US CVaR95 | NG CVaR95 | US share > 100% of resources |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Published: US OOP/income; Nigeria OOP/consumption | 61,447 | 4,685 | +0.672 | +0.615 | +0.715 | +0.088 | -0.068 | +0.199 | +0.584 | +0.461 | +0.728 | < 0.001 | 42.9 | 38.1 | 0.27 |
| Matched net: both over resources excluding OOP | 61,447 | 4,685 | +0.672 | +0.615 | +0.715 | +0.581 | +0.364 | +0.738 | +0.091 | -0.083 | +0.310 | 0.351 | 42.9 | 76.2 | 0.27 |
| Matched gross: both over resources including OOP | 61,447 | 4,685 | +0.343 | +0.297 | +0.378 | +0.088 | -0.068 | +0.199 | +0.255 | +0.143 | +0.396 | < 0.001 | 23.4 | 38.1 | 0.00 |
| Matched net, denominator floored at the poverty line | 61,447 | 4,685 | +0.543 | +0.497 | +0.584 | +0.596 | +0.380 | +0.802 | -0.053 | -0.252 | +0.149 | 0.620 | 30.5 | 59.4 | 0.15 |
| US panel-linked families, one-year income | 51,635 | 4,685 | +0.631 | +0.581 | +0.680 | +0.581 | +0.364 | +0.738 | +0.050 | -0.102 | +0.266 | 0.607 | 39.3 | 76.2 | 0.23 |
| US panel-linked families, two-year average income | 51,635 | 4,685 | +0.586 | +0.541 | +0.626 | +0.581 | +0.364 | +0.738 | +0.005 | -0.156 | +0.228 | 0.956 | 31.5 | 76.2 | 0.19 |
| US poor or near poor, one-year income; Nigeria poorest quintile, net | 10,033 | 714 | +0.609 | +0.476 | +0.753 | +0.385 | -0.023 | +0.813 | +0.224 | -0.207 | +0.655 | 0.311 | 103.8 | 91.2 | 0.95 |
| US poor or near poor, two-year income; Nigeria poorest quintile, net | 10,033 | 714 | +0.615 | +0.497 | +0.725 | +0.385 | -0.023 | +0.813 | +0.231 | -0.195 | +0.651 | 0.290 | 61.5 | 91.2 | 0.61 |
| OOP level per household, 2023 intl $ | 61,447 | 4,685 | +0.472 | +0.425 | +0.517 | +0.424 | +0.185 | +0.564 | +0.048 | -0.088 | +0.309 | 0.628 | 18,315 | 4,187 |  |
| OOP level per person, 2023 intl $ | 61,447 | 4,685 | +0.537 | +0.487 | +0.581 | +0.529 | +0.343 | +0.741 | +0.007 | -0.213 | +0.192 | 0.944 | 10,086 | 1,482 |  |

**Table 5.** Cost barriers to care, medical debt and forgone care.

*United States: families in which any member delayed or went without medical care or prescription medicines because of cost (MEPS round 4/2), and families with any medical debt (asked in 2024 only). Nigeria: persons ill or injured in the last four weeks who consulted no one, those who gave cost as the reason, and households with an ill member and no out-of-pocket spending, by quintile of per-capita consumption net of OOP.*

| Country | Measure | Dimension | Group | Estimate % | SE | n |
|---|---:|---:|---:|---:|---:|---:|
| United States | Cost barrier to care | All | All families | 15.79 | 0.24 | 61,049 |
| United States | Any medical debt (2024) | All | All families | 14.46 | 0.56 | 7,983 |
| United States | Cost barrier to care | Burden (OOP / income) | 0% to under 10% | 15.17 | 0.25 | 56,073 |
| United States | Any medical debt (2024) | Burden (OOP / income) | 0% to under 10% | 13.42 | 0.55 | 7,284 |
| United States | Cost barrier to care | Burden (OOP / income) | 10% to under 40% | 23.28 | 0.76 | 4,227 |
| United States | Any medical debt (2024) | Burden (OOP / income) | 10% to under 40% | 25.34 | 2.30 | 583 |
| United States | Cost barrier to care | Burden (OOP / income) | 40% to under 100% | 25.35 | 2.33 | 559 |
| United States | Any medical debt (2024) | Burden (OOP / income) | 40% to under 100% | 28.00 | 5.63 | 87 |
| United States | Cost barrier to care | Burden (OOP / income) | 100% or more | 28.05 | 4.21 | 190 |
| United States | Any medical debt (2024) | Burden (OOP / income) | 100% or more | 55.11 | 10.79 | 29 |
| United States | Cost barrier to care | Income relative to poverty | Below 100% of poverty | 20.86 | 0.64 | 8,323 |
| United States | Any medical debt (2024) | Income relative to poverty | Below 100% of poverty | 11.98 | 1.33 | 1,039 |
| United States | Cost barrier to care | Income relative to poverty | 100% to under 200% | 19.79 | 0.53 | 12,092 |
| United States | Any medical debt (2024) | Income relative to poverty | 100% to under 200% | 17.47 | 1.28 | 1,414 |
| United States | Cost barrier to care | Income relative to poverty | 200% to under 400% | 18.51 | 0.44 | 17,329 |
| United States | Any medical debt (2024) | Income relative to poverty | 200% to under 400% | 18.96 | 1.02 | 2,181 |
| United States | Cost barrier to care | Income relative to poverty | 400% or more | 11.24 | 0.30 | 23,305 |
| United States | Any medical debt (2024) | Income relative to poverty | 400% or more | 11.10 | 0.68 | 3,349 |
| Nigeria | Ill, consulted no one | All | All | 10.15 | 0.75 | 6,345 |
| Nigeria | Ill, consulted no one because of cost | All | All | 1.86 | 0.25 | 6,345 |
| Nigeria | Household with an ill member, no OOP | All | All | 12.41 | 0.86 | 3,301 |
| Nigeria | Ill, consulted no one | Quintile, consumption net of OOP | Q1 (poorest) | 11.96 | 1.97 | 987 |
| Nigeria | Ill, consulted no one because of cost | Quintile, consumption net of OOP | Q1 (poorest) | 4.34 | 1.04 | 987 |
| Nigeria | Household with an ill member, no OOP | Quintile, consumption net of OOP | Q1 (poorest) | 12.10 | 2.23 | 490 |
| Nigeria | Ill, consulted no one | Quintile, consumption net of OOP | Q2 | 9.68 | 1.56 | 1,203 |
| Nigeria | Ill, consulted no one because of cost | Quintile, consumption net of OOP | Q2 | 1.48 | 0.48 | 1,203 |
| Nigeria | Household with an ill member, no OOP | Quintile, consumption net of OOP | Q2 | 10.55 | 1.70 | 550 |
| Nigeria | Ill, consulted no one | Quintile, consumption net of OOP | Q3 | 11.75 | 1.92 | 1,228 |
| Nigeria | Ill, consulted no one because of cost | Quintile, consumption net of OOP | Q3 | 1.92 | 0.68 | 1,228 |
| Nigeria | Household with an ill member, no OOP | Quintile, consumption net of OOP | Q3 | 10.69 | 1.63 | 598 |
| Nigeria | Ill, consulted no one | Quintile, consumption net of OOP | Q4 | 9.73 | 1.59 | 1,370 |
| Nigeria | Ill, consulted no one because of cost | Quintile, consumption net of OOP | Q4 | 1.28 | 0.42 | 1,370 |
| Nigeria | Household with an ill member, no OOP | Quintile, consumption net of OOP | Q4 | 12.67 | 1.56 | 718 |
| Nigeria | Ill, consulted no one | Quintile, consumption net of OOP | Q5 (richest) | 8.73 | 1.13 | 1,557 |
| Nigeria | Ill, consulted no one because of cost | Quintile, consumption net of OOP | Q5 (richest) | 1.28 | 0.30 | 1,557 |
| Nigeria | Household with an ill member, no OOP | Quintile, consumption net of OOP | Q5 (richest) | 14.30 | 1.74 | 945 |

**Table 6.** Unconditional quantile regression of burden.

*Firpo, Fortin and Lemieux (2009). The coefficient is the effect on that percentile of the population burden distribution, in percentage points of resources. US burden is OOP over income; Nigerian burden is OOP over consumption net of OOP, and Nigerian poverty position is measured on the same net consumption. Standard errors are clustered on the stratum-PSU pair; * marks |t| > 1.96.*

| Country | Quantile | Term | Coefficient (pp) | SE | t |  |
|---|---:|---:|---:|---:|---:|---:|
| United States | q50 | Below the poverty line | 0.09 | 0.04 | 2.14 | * |
| United States | q50 | 1-2x the poverty line | 0.14 | 0.04 | 3.98 | * |
| United States | q50 | Uninsured any part of the year | -0.47 | 0.05 | -10.19 | * |
| United States | q50 | Any chronic condition | 0.75 | 0.04 | 20.50 | * |
| United States | q50 | Any member aged 60+ | 0.67 | 0.03 | 21.80 | * |
| United States | q50 | Any child under 5 | -0.06 | 0.06 | -1.08 |  |
| United States | q50 | Household size | 0.04 | 0.01 | 2.91 | * |
| United States | q75 | Below the poverty line | 1.86 | 0.12 | 15.77 | * |
| United States | q75 | 1-2x the poverty line | 1.51 | 0.10 | 15.39 | * |
| United States | q75 | Uninsured any part of the year | -0.78 | 0.11 | -7.37 | * |
| United States | q75 | Any chronic condition | 1.21 | 0.08 | 15.02 | * |
| United States | q75 | Any member aged 60+ | 1.62 | 0.09 | 18.52 | * |
| United States | q75 | Any child under 5 | -0.09 | 0.14 | -0.65 |  |
| United States | q75 | Household size | -0.02 | 0.03 | -0.68 |  |
| United States | q90 | Below the poverty line | 9.61 | 0.45 | 21.30 | * |
| United States | q90 | 1-2x the poverty line | 6.42 | 0.33 | 19.25 | * |
| United States | q90 | Uninsured any part of the year | -0.90 | 0.38 | -2.38 | * |
| United States | q90 | Any chronic condition | 2.42 | 0.24 | 10.12 | * |
| United States | q90 | Any member aged 60+ | 3.91 | 0.24 | 16.19 | * |
| United States | q90 | Any child under 5 | 0.12 | 0.38 | 0.31 |  |
| United States | q90 | Household size | -0.37 | 0.09 | -4.32 | * |
| United States | q95 | Below the poverty line | 25.22 | 1.20 | 20.96 | * |
| United States | q95 | 1-2x the poverty line | 12.78 | 0.78 | 16.45 | * |
| United States | q95 | Uninsured any part of the year | -0.95 | 0.86 | -1.11 |  |
| United States | q95 | Any chronic condition | 3.84 | 0.47 | 8.25 | * |
| United States | q95 | Any member aged 60+ | 6.54 | 0.51 | 12.78 | * |
| United States | q95 | Any child under 5 | -1.01 | 0.81 | -1.24 |  |
| United States | q95 | Household size | -0.83 | 0.17 | -5.00 | * |
| Nigeria | q50 | Below the poverty line | 0.31 | 0.39 | 0.79 |  |
| Nigeria | q50 | 1-2x the poverty line | 0.25 | 0.36 | 0.70 |  |
| Nigeria | q50 | Uninsured any part of the year | 0.86 | 0.76 | 1.14 |  |
| Nigeria | q50 | Any chronic condition | 2.48 | 0.33 | 7.39 | * |
| Nigeria | q50 | Any member aged 60+ | 0.53 | 0.26 | 2.04 | * |
| Nigeria | q50 | Any child under 5 | 1.13 | 0.25 | 4.53 | * |
| Nigeria | q50 | Household size | 0.13 | 0.04 | 3.12 | * |
| Nigeria | q75 | Below the poverty line | 2.91 | 0.86 | 3.39 | * |
| Nigeria | q75 | 1-2x the poverty line | 1.99 | 0.72 | 2.75 | * |
| Nigeria | q75 | Uninsured any part of the year | 0.95 | 1.67 | 0.57 |  |
| Nigeria | q75 | Any chronic condition | 8.68 | 1.06 | 8.16 | * |
| Nigeria | q75 | Any member aged 60+ | 2.18 | 0.64 | 3.42 | * |
| Nigeria | q75 | Any child under 5 | 1.84 | 0.71 | 2.57 | * |
| Nigeria | q75 | Household size | -0.30 | 0.09 | -3.36 | * |
| Nigeria | q90 | Below the poverty line | 7.68 | 1.71 | 4.50 | * |
| Nigeria | q90 | 1-2x the poverty line | 5.11 | 1.59 | 3.22 | * |
| Nigeria | q90 | Uninsured any part of the year | -1.72 | 5.63 | -0.31 |  |
| Nigeria | q90 | Any chronic condition | 20.20 | 3.21 | 6.30 | * |
| Nigeria | q90 | Any member aged 60+ | 5.27 | 1.37 | 3.84 | * |
| Nigeria | q90 | Any child under 5 | 1.95 | 1.57 | 1.24 |  |
| Nigeria | q90 | Household size | -0.69 | 0.21 | -3.28 | * |
| Nigeria | q95 | Below the poverty line | 10.68 | 2.94 | 3.63 | * |
| Nigeria | q95 | 1-2x the poverty line | 7.00 | 2.57 | 2.72 | * |
| Nigeria | q95 | Uninsured any part of the year | -13.11 | 13.42 | -0.98 |  |
| Nigeria | q95 | Any chronic condition | 32.50 | 6.30 | 5.16 | * |
| Nigeria | q95 | Any member aged 60+ | 6.65 | 2.45 | 2.72 | * |
| Nigeria | q95 | Any child under 5 | 0.65 | 2.73 | 0.24 |  |
| Nigeria | q95 | Household size | -0.98 | 0.34 | -2.84 | * |

**Table 7.** US families whose burden exceeds that of the Nigerian informal household at its median, upper quartile and 90th percentile.

*The reference is the Nigerian informal household at the stated quantile of its own burden distribution, on the SDG basis and on consumption net of OOP. The parity percentile is the point in the US group's distribution at which the reference burden is reached.*

| Nigerian basis | US group | Reference quantile | Reference burden % | US share above % | US parity percentile | n |
|---|---:|---:|---:|---:|---:|---:|
| SDG | All US families | q50 | 1.87 | 36.96 | 63.0 | 61,447 |
| SDG | All US families | q75 | 6.88 | 11.64 | 88.4 | 61,447 |
| SDG | All US families | q90 | 16.62 | 3.76 | 96.2 | 61,447 |
| SDG | Insured all year | q50 | 1.87 | 38.02 | 62.0 | 55,173 |
| SDG | Insured all year | q75 | 6.88 | 11.82 | 88.2 | 55,173 |
| SDG | Insured all year | q90 | 16.62 | 3.74 | 96.3 | 55,173 |
| SDG | Partly uninsured | q50 | 1.87 | 28.61 | 71.4 | 4,282 |
| SDG | Partly uninsured | q75 | 6.88 | 9.84 | 90.2 | 4,282 |
| SDG | Partly uninsured | q90 | 16.62 | 3.78 | 96.2 | 4,282 |
| SDG | Uninsured all year | q50 | 1.87 | 25.03 | 75.0 | 1,992 |
| SDG | Uninsured all year | q75 | 6.88 | 10.35 | 89.6 | 1,992 |
| SDG | Uninsured all year | q90 | 16.62 | 4.46 | 95.5 | 1,992 |
| SDG | Poor or near poor | q50 | 1.87 | 41.25 | 58.8 | 11,735 |
| SDG | Poor or near poor | q75 | 6.88 | 21.36 | 78.6 | 11,735 |
| SDG | Poor or near poor | q90 | 16.62 | 11.09 | 88.9 | 11,735 |
| SDG | Chronic condition | q50 | 1.87 | 41.53 | 58.5 | 48,595 |
| SDG | Chronic condition | q75 | 6.88 | 13.28 | 86.7 | 48,595 |
| SDG | Chronic condition | q90 | 16.62 | 4.35 | 95.6 | 48,595 |
| SDG | Elderly member | q50 | 1.87 | 50.45 | 49.6 | 22,606 |
| SDG | Elderly member | q75 | 6.88 | 18.23 | 81.8 | 22,606 |
| SDG | Elderly member | q90 | 16.62 | 6.26 | 93.7 | 22,606 |
| net of OOP | All US families | q50 | 1.91 | 36.52 | 63.5 | 61,447 |
| net of OOP | All US families | q75 | 7.39 | 10.69 | 89.3 | 61,447 |
| net of OOP | All US families | q90 | 19.94 | 2.96 | 97.0 | 61,447 |
| net of OOP | Insured all year | q50 | 1.91 | 37.59 | 62.4 | 55,173 |
| net of OOP | Insured all year | q75 | 7.39 | 10.85 | 89.2 | 55,173 |
| net of OOP | Insured all year | q90 | 19.94 | 2.92 | 97.1 | 55,173 |
| net of OOP | Partly uninsured | q50 | 1.91 | 27.94 | 72.1 | 4,282 |
| net of OOP | Partly uninsured | q75 | 7.39 | 9.16 | 90.8 | 4,282 |
| net of OOP | Partly uninsured | q90 | 19.94 | 3.03 | 97.0 | 4,282 |
| net of OOP | Uninsured all year | q50 | 1.91 | 24.85 | 75.1 | 1,992 |
| net of OOP | Uninsured all year | q75 | 7.39 | 9.53 | 90.5 | 1,992 |
| net of OOP | Uninsured all year | q90 | 19.94 | 3.85 | 96.2 | 1,992 |
| net of OOP | Poor or near poor | q50 | 1.91 | 41.02 | 59.0 | 11,735 |
| net of OOP | Poor or near poor | q75 | 7.39 | 20.52 | 79.5 | 11,735 |
| net of OOP | Poor or near poor | q90 | 19.94 | 9.13 | 90.9 | 11,735 |
| net of OOP | Chronic condition | q50 | 1.91 | 41.04 | 59.0 | 48,595 |
| net of OOP | Chronic condition | q75 | 7.39 | 12.24 | 87.8 | 48,595 |
| net of OOP | Chronic condition | q90 | 19.94 | 3.43 | 96.6 | 48,595 |
| net of OOP | Elderly member | q50 | 1.91 | 49.91 | 50.1 | 22,606 |
| net of OOP | Elderly member | q75 | 7.39 | 16.96 | 83.0 | 22,606 |
| net of OOP | Elderly member | q90 | 19.94 | 4.88 | 95.1 | 22,606 |

**Table 8.** Robustness: the comparison under sixteen variants.

*Each row reruns the whole comparison under one change. Variants that alter the denominator construction or the Nigerian out-of-pocket instrument are the ones that move the tail columns. Table A8 records which orderings hold.*

| Variant | Country | n | CHE10 % | CTP40 % | VaR95 % | CVaR95 % | xi |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | United States | 61,447 | 7.39 | 10.98 | 13.55 | 42.90 | +0.672 |
| Baseline | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| Excluding 2020 (pandemic) | United States | 49,595 | 7.47 | 10.96 | 13.61 | 44.19 | +0.683 |
| Excluding 2020 (pandemic) | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| US 2024 only | United States | 8,104 | 7.81 | 10.35 | 13.62 | 48.18 | +0.750 |
| US 2024 only | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| US 2019 only | United States | 11,547 | 7.84 | 11.86 | 13.92 | 43.94 | +0.628 |
| US 2019 only | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| Income floor $500 | United States | 61,530 | 7.46 | 11.06 | 13.75 | 46.96 | +0.707 |
| Income floor $500 | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| Income floor $2,000 | United States | 61,216 | 7.27 | 10.75 | 13.33 | 37.16 | +0.615 |
| Income floor $2,000 | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| Income floor $5,000 | United States | 60,527 | 7.02 | 10.18 | 12.90 | 32.69 | +0.558 |
| Income floor $5,000 | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| US income at or above the poverty line | United States | 53,020 | 6.17 | 3.34 | 11.59 | 28.32 | +0.550 |
| US income at or above the poverty line | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |
| Nigeria: food-share floor | United States | 61,447 | 7.39 | 10.98 | 13.55 | 42.90 | +0.672 |
| Nigeria: food-share floor | Nigeria | 4,685 | 17.24 | 10.79 | 25.01 | 38.09 | +0.088 |
| Per equivalent adult | United States | 61,447 | 7.39 | 8.62 | 13.55 | 42.90 | +0.672 |
| Per equivalent adult | Nigeria | 4,685 | 17.24 | 15.50 | 25.01 | 38.09 | +0.088 |
| GPD threshold q85 | United States | 61,447 | 7.39 | 10.98 | 13.55 | 42.90 | +0.643 |
| GPD threshold q85 | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.081 |
| GPD threshold q95 | United States | 61,447 | 7.39 | 10.98 | 13.55 | 42.90 | +0.670 |
| GPD threshold q95 | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.007 |
| Nigeria: OOP including transport | United States | 61,447 | 7.39 | 10.98 | 13.55 | 42.90 | +0.672 |
| Nigeria: OOP including transport | Nigeria | 4,685 | 18.25 | 40.48 | 26.41 | 39.74 | +0.019 |
| Nigeria: consumption-module OOP | United States | 61,447 | 7.39 | 10.98 | 13.55 | 42.90 | +0.672 |
| Nigeria: consumption-module OOP | Nigeria | 4,685 | 0.14 | 11.56 | 1.76 | 4.04 | +0.374 |
| Matched net denominators | United States | 61,447 | 7.39 | 10.98 | 13.55 | 42.90 | +0.672 |
| Matched net denominators | Nigeria | 4,685 | 18.54 | 41.80 | 33.35 | 76.20 | +0.581 |
| Matched gross denominators | United States | 61,447 | 6.53 | 9.76 | 11.94 | 23.39 | +0.343 |
| Matched gross denominators | Nigeria | 4,685 | 17.24 | 39.51 | 25.01 | 38.09 | +0.088 |


# Appendix tables


**Table A1.** Catastrophic spending by subgroup.

| Country | Dimension | Group | Measure | Estimate % | SE | n |
|---|---:|---:|---:|---:|---:|---:|
| United States | Insurance status | Insured all year | Budget share > 10% | 7.45 | 0.16 | 55,173 |
| United States | Insurance status | Partly uninsured | Budget share > 10% | 6.63 | 0.62 | 4,282 |
| United States | Insurance status | Uninsured all year | Budget share > 10% | 7.22 | 0.76 | 1,992 |
| United States | Poverty category | Middle income | Budget share > 10% | 6.80 | 0.24 | 17,402 |
| United States | Poverty category | Poor/negative | Budget share > 10% | 18.20 | 0.61 | 8,427 |
| United States | Poverty category | High income | Budget share > 10% | 3.06 | 0.14 | 23,338 |
| United States | Poverty category | Low income | Budget share > 10% | 12.65 | 0.50 | 8,972 |
| United States | Poverty category | Near poor | Budget share > 10% | 13.63 | 0.74 | 3,308 |
| United States | Any chronic condition | No | Budget share > 10% | 4.07 | 0.23 | 12,852 |
| United States | Any chronic condition | Yes | Budget share > 10% | 8.46 | 0.19 | 48,595 |
| United States | Elderly member | No | Budget share > 10% | 5.48 | 0.17 | 38,841 |
| United States | Elderly member | Yes | Budget share > 10% | 11.85 | 0.30 | 22,606 |
| United States | Insurance status | Insured all year | Budget share > 25% | 2.20 | 0.08 | 55,173 |
| United States | Insurance status | Partly uninsured | Budget share > 25% | 2.52 | 0.42 | 4,282 |
| United States | Insurance status | Uninsured all year | Budget share > 25% | 3.00 | 0.56 | 1,992 |
| United States | Poverty category | Middle income | Budget share > 25% | 1.67 | 0.12 | 17,402 |
| United States | Poverty category | Poor/negative | Budget share > 25% | 8.42 | 0.45 | 8,427 |
| United States | Poverty category | High income | Budget share > 25% | 0.54 | 0.05 | 23,338 |
| United States | Poverty category | Low income | Budget share > 25% | 3.66 | 0.27 | 8,972 |
| United States | Poverty category | Near poor | Budget share > 25% | 4.57 | 0.51 | 3,308 |
| United States | Any chronic condition | No | Budget share > 25% | 1.16 | 0.12 | 12,852 |
| United States | Any chronic condition | Yes | Budget share > 25% | 2.60 | 0.10 | 48,595 |
| United States | Elderly member | No | Budget share > 25% | 1.64 | 0.09 | 38,841 |
| United States | Elderly member | Yes | Budget share > 25% | 3.67 | 0.16 | 22,606 |
| United States | Insurance status | Insured all year | Budget share > 40% | 1.06 | 0.05 | 55,173 |
| United States | Insurance status | Partly uninsured | Budget share > 40% | 1.40 | 0.31 | 4,282 |
| United States | Insurance status | Uninsured all year | Budget share > 40% | 1.50 | 0.40 | 1,992 |
| United States | Poverty category | Middle income | Budget share > 40% | 0.71 | 0.08 | 17,402 |
| United States | Poverty category | Poor/negative | Budget share > 40% | 5.02 | 0.36 | 8,427 |
| United States | Poverty category | High income | Budget share > 40% | 0.23 | 0.03 | 23,338 |
| United States | Poverty category | Low income | Budget share > 40% | 1.48 | 0.15 | 8,972 |
| United States | Poverty category | Near poor | Budget share > 40% | 2.16 | 0.40 | 3,308 |
| United States | Any chronic condition | No | Budget share > 40% | 0.52 | 0.09 | 12,852 |
| United States | Any chronic condition | Yes | Budget share > 40% | 1.29 | 0.07 | 48,595 |
| United States | Elderly member | No | Budget share > 40% | 0.83 | 0.06 | 38,841 |
| United States | Elderly member | Yes | Budget share > 40% | 1.73 | 0.09 | 22,606 |
| United States | Insurance status | Insured all year | Capacity to pay >= 40% | 10.65 | 0.25 | 55,173 |
| United States | Insurance status | Partly uninsured | Capacity to pay >= 40% | 14.63 | 0.78 | 4,282 |
| United States | Insurance status | Uninsured all year | Capacity to pay >= 40% | 12.57 | 1.04 | 1,992 |
| United States | Poverty category | Middle income | Capacity to pay >= 40% | 1.64 | 0.12 | 17,402 |
| United States | Poverty category | Poor/negative | Capacity to pay >= 40% | 78.36 | 0.69 | 8,427 |
| United States | Poverty category | High income | Capacity to pay >= 40% | 0.31 | 0.04 | 23,338 |
| United States | Poverty category | Low income | Capacity to pay >= 40% | 8.48 | 0.37 | 8,972 |
| United States | Poverty category | Near poor | Capacity to pay >= 40% | 30.21 | 1.08 | 3,308 |
| United States | Any chronic condition | No | Capacity to pay >= 40% | 7.83 | 0.34 | 12,852 |
| United States | Any chronic condition | Yes | Capacity to pay >= 40% | 12.00 | 0.28 | 48,595 |
| United States | Elderly member | No | Capacity to pay >= 40% | 10.09 | 0.29 | 38,841 |
| United States | Elderly member | Yes | Capacity to pay >= 40% | 13.06 | 0.34 | 22,606 |
| United States | Insurance status | Insured all year | No capacity to pay (at or below the floor) | 9.54 | 0.27 | 55,173 |
| United States | Insurance status | Partly uninsured | No capacity to pay (at or below the floor) | 15.13 | 0.81 | 4,282 |
| United States | Insurance status | Uninsured all year | No capacity to pay (at or below the floor) | 17.61 | 1.23 | 1,992 |
| United States | Poverty category | Middle income | No capacity to pay (at or below the floor) | 0.00 | 0.00 | 17,402 |
| United States | Poverty category | Poor/negative | No capacity to pay (at or below the floor) | 100.00 | 0.00 | 8,427 |
| United States | Poverty category | High income | No capacity to pay (at or below the floor) | 0.00 | 0.00 | 23,338 |
| United States | Poverty category | Low income | No capacity to pay (at or below the floor) | 0.00 | 0.00 | 8,972 |
| United States | Poverty category | Near poor | No capacity to pay (at or below the floor) | 0.06 | 0.06 | 3,308 |
| United States | Any chronic condition | No | No capacity to pay (at or below the floor) | 10.78 | 0.43 | 12,852 |
| United States | Any chronic condition | Yes | No capacity to pay (at or below the floor) | 9.99 | 0.29 | 48,595 |
| United States | Elderly member | No | No capacity to pay (at or below the floor) | 10.88 | 0.34 | 38,841 |
| United States | Elderly member | Yes | No capacity to pay (at or below the floor) | 8.57 | 0.29 | 22,606 |
| Nigeria | Sector | Informal | Budget share > 10% | 17.54 | 0.85 | 3,876 |
| Nigeria | Sector | Formal | Budget share > 10% | 15.92 | 1.86 | 809 |
| Nigeria | Consumption quintile | Q4 | Budget share > 10% | 16.79 | 1.58 | 1,016 |
| Nigeria | Consumption quintile | Q5 (richest) | Budget share > 10% | 18.71 | 1.49 | 1,428 |
| Nigeria | Consumption quintile | Q3 | Budget share > 10% | 17.20 | 2.00 | 834 |
| Nigeria | Consumption quintile | Q1 (poorest) | Budget share > 10% | 13.90 | 1.75 | 700 |
| Nigeria | Consumption quintile | Q2 | Budget share > 10% | 17.49 | 1.95 | 707 |
| Nigeria | Insurance status | Uninsured | Budget share > 10% | 17.26 | 0.79 | 4,583 |
| Nigeria | Insurance status | Insured | Budget share > 10% | 16.35 | 6.55 | 102 |
| Nigeria | Residence | Urban | Budget share > 10% | 16.23 | 1.41 | 1,480 |
| Nigeria | Residence | Rural | Budget share > 10% | 17.89 | 1.00 | 3,205 |
| Nigeria | Sector | Informal | Budget share > 25% | 5.33 | 0.54 | 3,876 |
| Nigeria | Sector | Formal | Budget share > 25% | 3.60 | 0.89 | 809 |
| Nigeria | Consumption quintile | Q4 | Budget share > 25% | 4.66 | 0.88 | 1,016 |
| Nigeria | Consumption quintile | Q5 (richest) | Budget share > 25% | 6.68 | 0.94 | 1,428 |
| Nigeria | Consumption quintile | Q3 | Budget share > 25% | 2.96 | 0.66 | 834 |
| Nigeria | Consumption quintile | Q1 (poorest) | Budget share > 25% | 4.50 | 1.06 | 700 |
| Nigeria | Consumption quintile | Q2 | Budget share > 25% | 4.46 | 1.31 | 707 |
| Nigeria | Insurance status | Uninsured | Budget share > 25% | 4.91 | 0.46 | 4,583 |
| Nigeria | Insurance status | Insured | Budget share > 25% | 9.79 | 6.17 | 102 |
| Nigeria | Residence | Urban | Budget share > 25% | 3.66 | 0.65 | 1,480 |
| Nigeria | Residence | Rural | Budget share > 25% | 5.88 | 0.67 | 3,205 |
| Nigeria | Sector | Informal | Budget share > 40% | 1.83 | 0.30 | 3,876 |
| Nigeria | Sector | Formal | Budget share > 40% | 0.41 | 0.21 | 809 |
| Nigeria | Consumption quintile | Q4 | Budget share > 40% | 0.36 | 0.16 | 1,016 |
| Nigeria | Consumption quintile | Q5 (richest) | Budget share > 40% | 3.20 | 0.65 | 1,428 |
| Nigeria | Consumption quintile | Q3 | Budget share > 40% | 0.53 | 0.27 | 834 |
| Nigeria | Consumption quintile | Q1 (poorest) | Budget share > 40% | 1.16 | 0.43 | 700 |
| Nigeria | Consumption quintile | Q2 | Budget share > 40% | 1.08 | 0.61 | 707 |
| Nigeria | Insurance status | Uninsured | Budget share > 40% | 1.59 | 0.25 | 4,583 |
| Nigeria | Insurance status | Insured | Budget share > 40% | 0.20 | 0.20 | 102 |
| Nigeria | Residence | Urban | Budget share > 40% | 1.19 | 0.39 | 1,480 |
| Nigeria | Residence | Rural | Budget share > 40% | 1.80 | 0.32 | 3,205 |
| Nigeria | Sector | Informal | Capacity to pay >= 40% | 40.80 | 1.30 | 3,876 |
| Nigeria | Sector | Formal | Capacity to pay >= 40% | 33.96 | 2.48 | 809 |
| Nigeria | Consumption quintile | Q4 | Capacity to pay >= 40% | 38.10 | 2.20 | 1,016 |
| Nigeria | Consumption quintile | Q5 (richest) | Capacity to pay >= 40% | 8.30 | 0.92 | 1,428 |
| Nigeria | Consumption quintile | Q3 | Capacity to pay >= 40% | 68.18 | 2.51 | 834 |
| Nigeria | Consumption quintile | Q1 (poorest) | Capacity to pay >= 40% | 56.60 | 2.85 | 700 |
| Nigeria | Consumption quintile | Q2 | Capacity to pay >= 40% | 67.61 | 2.34 | 707 |
| Nigeria | Insurance status | Uninsured | Capacity to pay >= 40% | 39.74 | 1.20 | 4,583 |
| Nigeria | Insurance status | Insured | Capacity to pay >= 40% | 28.41 | 8.33 | 102 |
| Nigeria | Residence | Urban | Capacity to pay >= 40% | 33.55 | 2.08 | 1,480 |
| Nigeria | Residence | Rural | Capacity to pay >= 40% | 43.35 | 1.62 | 3,205 |
| Nigeria | Sector | Informal | No capacity to pay (at or below the floor) | 52.58 | 1.37 | 3,876 |
| Nigeria | Sector | Formal | No capacity to pay (at or below the floor) | 38.20 | 2.58 | 809 |
| Nigeria | Consumption quintile | Q4 | No capacity to pay (at or below the floor) | 27.88 | 1.99 | 1,016 |
| Nigeria | Consumption quintile | Q5 (richest) | No capacity to pay (at or below the floor) | 0.00 | 0.00 | 1,428 |
| Nigeria | Consumption quintile | Q3 | No capacity to pay (at or below the floor) | 100.00 | 0.00 | 834 |
| Nigeria | Consumption quintile | Q1 (poorest) | No capacity to pay (at or below the floor) | 100.00 | 0.00 | 700 |
| Nigeria | Consumption quintile | Q2 | No capacity to pay (at or below the floor) | 100.00 | 0.00 | 707 |
| Nigeria | Insurance status | Uninsured | No capacity to pay (at or below the floor) | 50.38 | 1.35 | 4,583 |
| Nigeria | Insurance status | Insured | No capacity to pay (at or below the floor) | 24.47 | 6.25 | 102 |
| Nigeria | Residence | Urban | No capacity to pay (at or below the floor) | 38.93 | 2.53 | 1,480 |
| Nigeria | Residence | Rural | No capacity to pay (at or below the floor) | 56.91 | 1.76 | 3,205 |

**Table A2.** Underinsurance among US families insured all year.

*Adapted from the Commonwealth Fund definition: OOP at or above 10% of income, or at or above 5% for families below 200% of poverty. The deductible criterion is not applied, so the rate is a lower bound.*

| Group | Estimate % | SE | 95% low | 95% high | n |
|---|---:|---:|---:|---:|---:|
| All families insured all year | 10.31 | 0.20 | 9.92 | 10.70 | 55,173 |
| Income below 200% of poverty | 26.44 | 0.55 | 25.35 | 27.52 | 17,612 |
| Income at or above 200% of poverty | 4.68 | 0.14 | 4.39 | 4.96 | 37,561 |

**Table A3.** Burden quantiles by group, published basis.

| Group | Country | n | q50 % | q75 % | q90 % | q95 % | q99 % |
|---|---:|---:|---:|---:|---:|---:|---:|
| US, insured all year | United States | 55,173 | 1.13 | 3.25 | 7.95 | 13.60 | 41.50 |
| US, partly uninsured | United States | 4,282 | 0.61 | 2.20 | 6.69 | 12.94 | 51.63 |
| US, uninsured all year | United States | 1,992 | 0.28 | 1.87 | 7.03 | 14.40 | 57.62 |
| US, poor or near poor | United States | 11,735 | 1.03 | 5.34 | 18.43 | 34.78 | 114.85 |
| US, chronic condition | United States | 48,595 | 1.34 | 3.62 | 8.76 | 15.02 | 47.47 |
| Nigeria, all | Nigeria | 4,685 | 1.88 | 6.71 | 16.31 | 25.01 | 48.19 |
| Nigeria, informal | Nigeria | 3,876 | 1.87 | 6.88 | 16.62 | 26.06 | 50.61 |
| Nigeria, formal | Nigeria | 809 | 1.90 | 5.92 | 14.00 | 19.94 | 35.73 |
| Nigeria, poorest quintile | Nigeria | 700 | 1.59 | 5.78 | 13.41 | 23.74 | 45.41 |

**Table A4.** Tail-risk measures for Nigerian groups on the SDG basis (OOP over consumption including OOP).

*The ratio cannot exceed one on this basis, so the fitted shape tends toward zero or below at high thresholds.*

| Group | n | Exceedances | VaR95 % | CVaR95 % | 95% low | 95% high | CVaR99 % | xi | xi low | xi high |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All households | 4,685 | 455 | 25.01 | 38.09 | 34.61 | 41.62 | 60.24 | +0.088 | -0.068 | +0.199 |
| Informal sector | 3,876 | 378 | 26.06 | 40.01 | 35.92 | 43.68 | 62.31 | +0.039 | -0.122 | +0.190 |
| Formal sector | 809 | 88 | 19.94 | 29.06 | 24.51 | 33.40 | 42.52 | -0.131 | -0.355 | +0.379 |
| Poorest quintile | 700 | 76 | 23.74 | 35.88 | 29.68 | 41.51 | 52.42 | -0.195 | -0.447 | +0.190 |
| Richest quintile | 1,428 | 143 | 29.22 | 48.01 | 41.20 | 55.18 | 71.14 | -0.134 | -0.430 | +0.230 |
| Rural | 3,205 | 311 | 26.48 | 40.59 | 36.52 | 45.14 | 63.39 | -0.011 | -0.169 | +0.152 |

**Table A5.** Generalized Pareto shape across thresholds.

*Blank cells have fewer than 30 exceedances.*

| Country | Basis | Group | xi at q80 | xi at q85 | xi at q90 | xi at q95 | xi at q97.5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Nigeria | consumption (SDG basis) | All households | +0.098 | +0.081 | +0.088 | +0.007 | -0.201 |
| Nigeria | consumption (SDG basis) | Formal sector | -0.092 | -0.081 | -0.131 | -0.255 |  |
| Nigeria | consumption (SDG basis) | Informal sector | +0.116 | +0.087 | +0.039 | -0.049 | -0.260 |
| Nigeria | consumption (SDG basis) | Poorest quintile | +0.141 | +0.003 | -0.195 | -0.272 |  |
| Nigeria | consumption (SDG basis) | Richest quintile | +0.067 | +0.105 | -0.134 | -0.365 | -0.150 |
| Nigeria | consumption (SDG basis) | Rural | +0.067 | +0.036 | -0.011 | -0.055 | -0.242 |
| Nigeria | consumption net of OOP | All households | +0.489 | +0.505 | +0.581 | +0.583 | +0.457 |
| Nigeria | consumption net of OOP | Formal sector | +0.146 | +0.160 | +0.119 | +0.017 |  |
| Nigeria | consumption net of OOP | Informal sector | +0.540 | +0.550 | +0.568 | +0.579 | +0.428 |
| Nigeria | consumption net of OOP | Poorest quintile | +0.504 | +0.412 | +0.197 | +0.123 |  |
| Nigeria | consumption net of OOP | Richest quintile | +0.614 | +0.738 | +0.598 | +0.387 | +0.731 |
| Nigeria | consumption net of OOP | Rural | +0.501 | +0.503 | +0.509 | +0.563 | +0.493 |
| United States | income | All families | +0.634 | +0.643 | +0.672 | +0.670 | +0.649 |
| United States | income | Chronic condition | +0.654 | +0.659 | +0.673 | +0.680 | +0.741 |
| United States | income | Elderly member | +0.605 | +0.601 | +0.637 | +0.605 | +0.648 |
| United States | income | Insured all year | +0.626 | +0.632 | +0.659 | +0.682 | +0.675 |
| United States | income | Partly uninsured | +0.783 | +0.781 | +0.737 | +0.682 | +0.613 |
| United States | income | Poor or near poor | +0.650 | +0.698 | +0.719 | +0.798 | +0.902 |
| United States | income | Uninsured all year | +0.722 | +0.659 | +0.594 | +0.333 | +0.430 |

**Table A6.** Goodness of fit of the generalized Pareto distribution.

*KS is the largest gap between the weighted empirical distribution of the exceedances and the fitted one; it is descriptive, since a weighted clustered sample has no standard reference distribution for it. Thresholds are in the unit of the construction. QQ plots are in Figure 4.*

| Construction | Country | Threshold | Exceedances | xi | sigma | KS |
|---|---:|---:|---:|---:|---:|---:|
| published | United States | 0.0787 | 6,746 | +0.672 | 0.0642 | 0.011 |
| published | Nigeria | 0.1631 | 455 | +0.088 | 0.1143 | 0.062 |
| net | United States | 0.0787 | 6,746 | +0.672 | 0.0642 | 0.011 |
| net | Nigeria | 0.1949 | 455 | +0.581 | 0.1434 | 0.047 |
| gross | United States | 0.0730 | 6,746 | +0.343 | 0.0609 | 0.022 |
| gross | Nigeria | 0.1631 | 455 | +0.088 | 0.1143 | 0.062 |
| levels_household | United States | 5,502 | 5,645 | +0.472 | 3,740 | 0.010 |
| levels_household | Nigeria | 1,358 | 423 | +0.424 | 946 | 0.051 |

**Table A7.** Crossover: the percentile above which a US group's burden exceeds the Nigerian informal burden at the same percentile.

*Blank means the US curve never exceeds the Nigerian one between the 5th and 99.9th percentiles. A crossing at the last grid point is flagged, since it may lie beyond the grid.*

| Nigerian basis | US group | Crossover percentile | Burden there % | At grid edge |
|---|---:|---:|---:|---:|
| SDG | All US families | 99.3 | 56.39 |  |
| SDG | Insured all year | 99.4 | 60.39 |  |
| SDG | Partly uninsured | 99.0 | 51.63 |  |
| SDG | Uninsured all year | 99.0 | 57.62 |  |
| SDG | Poor or near poor | 85.0 | 11.89 |  |
| SDG | Chronic condition | 99.1 | 52.24 |  |
| SDG | Elderly member | 99.0 | 59.27 |  |
| net of OOP | All US families |  |  |  |
| net of OOP | Insured all year |  |  |  |
| net of OOP | Partly uninsured |  |  |  |
| net of OOP | Uninsured all year |  |  |  |
| net of OOP | Poor or near poor | 95.5 | 37.49 |  |
| net of OOP | Chronic condition |  |  |  |
| net of OOP | Elderly member | 99.9 | 315.63 | yes |

**Table A8.** Out-of-pocket spending in 2023 international dollars.

*Converted at the World Bank private-consumption PPP factor. A PPP for private consumption is not a medical price index; the comparison indicates what households pay, not what they buy.*

| Country | Mean OOP, household | Mean OOP, per person | Mean resources, per person | q50 p.p. | q90 p.p. | q99 p.p. |
|---|---:|---:|---:|---:|---:|---:|
| United States | 2,303 | 1,194 | 48,309 | 411 | 2,702 | 11,449 |
| Nigeria | 499 | 142 | 2,279 | 24 | 318 | 1,795 |

**Table A9.** Which orderings hold in each robustness variant.

| variant | Nigeria worse on CHE10 | US tail heavier (xi) | US CVaR95 higher |
|---|---:|---:|---:|
| Baseline | yes | yes | yes |
| Excluding 2020 (pandemic) | yes | yes | yes |
| US 2024 only | yes | yes | yes |
| US 2019 only | yes | yes | yes |
| Income floor $500 | yes | yes | yes |
| Income floor $2,000 | yes | yes | no |
| Income floor $5,000 | yes | yes | no |
| US income at or above the poverty line | yes | yes | no |
| Nigeria: food-share floor | yes | yes | yes |
| Per equivalent adult | yes | yes | yes |
| GPD threshold q85 | yes | yes | yes |
| GPD threshold q95 | yes | yes | yes |
| Nigeria: OOP including transport | yes | yes | yes |
| Nigeria: consumption-module OOP | no | yes | yes |
| Matched net denominators | yes | yes | no |
| Matched gross denominators | yes | yes | no |

**Table A10.** The poverty coefficient of the unconditional quantile regression with Nigerian poverty measured on gross and on net-of-OOP consumption.

*Coefficients in percentage points of resources. The gross ranking places a household that spent heavily on health higher in the consumption distribution, which reverses the sign.*

| Basis | Quantile | Coefficient (pp) | SE | t |
|---|---:|---:|---:|---:|
| United States, income | q50 | 0.09 | 0.04 | 2.14 |
| United States, income | q75 | 1.86 | 0.12 | 15.77 |
| United States, income | q90 | 9.61 | 0.45 | 21.30 |
| United States, income | q95 | 25.22 | 1.20 | 20.96 |
| Nigeria, consumption net of OOP | q50 | 0.31 | 0.39 | 0.79 |
| Nigeria, consumption net of OOP | q75 | 2.91 | 0.86 | 3.39 |
| Nigeria, consumption net of OOP | q90 | 7.68 | 1.71 | 4.50 |
| Nigeria, consumption net of OOP | q95 | 10.68 | 2.94 | 3.63 |
| Nigeria, gross consumption | q50 | -0.78 | 0.37 | -2.09 |
| Nigeria, gross consumption | q75 | -0.97 | 0.88 | -1.09 |
| Nigeria, gross consumption | q90 | -3.52 | 1.71 | -2.06 |
| Nigeria, gross consumption | q95 | -8.17 | 3.11 | -2.63 |

**Table A11.** Validating the US build: the poverty threshold reconstructed from family income and the published income-to-poverty ratio, against the 2024 Census thresholds.

*MEPS POVLEV uses the Census Bureau thresholds, which vary by family composition; the modal cell for each size is one person under 65, two adults, three people with one child, and four with two children. The weighted average and the HHS guideline are shown for reference.*

| Family size | Derived median | Census, modal cell | Census, weighted average | HHS guideline | n |
|---|---:|---:|---:|---:|---:|
| 1 | $16,319 | $16,320 | $15,940 | $15,060 | 25,389 |
| 2 | $21,004 | $21,006 | $20,220 | $20,440 | 18,573 |
| 3 | $25,248 | $25,249 | $24,950 | $25,820 | 7,262 |
| 4 | $31,812 | $31,812 | $32,130 | $31,200 | 6,019 |

**Table A12.** Generalized Pareto shape across thresholds, by construction of the denominator.

| Construction | Country | xi at q80 | xi at q85 | xi at q90 | xi at q95 | xi at q97.5 |
|---|---:|---:|---:|---:|---:|---:|
| floor | Nigeria | +0.555 | +0.568 | +0.596 | +0.507 | +0.548 |
| floor | United States | +0.530 | +0.526 | +0.543 | +0.559 | +0.513 |
| gross | Nigeria | +0.098 | +0.081 | +0.088 | +0.007 | -0.201 |
| gross | United States | +0.397 | +0.372 | +0.343 | +0.221 | +0.083 |
| levels_household | Nigeria | +0.402 | +0.350 | +0.424 | +0.388 | +0.522 |
| levels_household | United States | +0.436 | +0.459 | +0.472 | +0.485 | +0.472 |
| levels_person | Nigeria | +0.590 | +0.560 | +0.529 | +0.523 | +0.459 |
| levels_person | United States | +0.519 | +0.531 | +0.537 | +0.545 | +0.547 |
| linked_one_year | Nigeria | +0.489 | +0.505 | +0.581 | +0.583 | +0.457 |
| linked_one_year | United States | +0.617 | +0.625 | +0.631 | +0.613 | +0.567 |
| net | Nigeria | +0.489 | +0.505 | +0.581 | +0.583 | +0.457 |
| net | United States | +0.634 | +0.643 | +0.672 | +0.670 | +0.649 |
| poor_one_year | Nigeria | +0.326 | +0.214 | +0.385 | +0.272 |  |
| poor_one_year | United States | +0.579 | +0.582 | +0.609 | +0.624 | +0.813 |
| poor_two_year | Nigeria | +0.326 | +0.214 | +0.385 | +0.272 |  |
| poor_two_year | United States | +0.572 | +0.584 | +0.615 | +0.556 | +0.555 |
| published | Nigeria | +0.098 | +0.081 | +0.088 | +0.007 | -0.201 |
| published | United States | +0.634 | +0.643 | +0.672 | +0.670 | +0.649 |
| two_year | Nigeria | +0.489 | +0.505 | +0.581 | +0.583 | +0.457 |
| two_year | United States | +0.578 | +0.579 | +0.586 | +0.604 | +0.526 |
