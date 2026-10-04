# Blog 4: More Tech, Better Jobs?

Blog 4 publication materials. National comparisons are the 50 states. DC is downloaded and excluded from estimates. County supplement uses fixed San Francisco (06075) and Santa Clara (06085) counties, not the entire Bay Area.

## Reproduce from the included public data

Run from this directory, with R and the ggplot2 package installed:

    Rscript code/analyze.R
    Rscript code/check.R
    quarto render index.qmd

Quarto requires knitr and rmarkdown. Source downloads and CSV inputs are provided in data/, analysis and acquisition scripts in code/, and derived results in results/.

## Refresh from Census

Use PowerShell 7. Set CENSUS_API_KEY in your process environment using your own activated Census key. Do not put it in this repository or a script. Run code/acquire.ps1 and code/acquire-bay.ps1 from the project root. Both scripts read the environment; error messages suppress authenticated request URLs. Published raw responses contain public tabulations only. Source metadata: https://api.census.gov/data/2024/acs/acs1/subject/groups.html . Variables are verified before interpreting them.

Years: 2018, 2019, 2021, 2022, 2023, 2024. Standard 2020 ACS 1-year estimates were not released; do not interpolate, fill zeroes, or mix 5-year estimates into the annual panel.

## Measures

S2401_C01_007E: employed residents in computer and mathematical occupations.
S2401_C01_001E: civilian employed population age 16+.
Tech share = 100 * first count / second count. This is an occupational concentration proxy, not technology adoption or productivity.
S2301_C03_001E: employment/population ratio.
S2301_C04_001E: unemployment rate.
Matching M variables are published margins of error. They are retained, not interpreted as standard deviations. No formal inference or significance claims are made. Derived share uncertainty would require appropriate ratio variance estimation.

Rate differences are percentage points; count growth is percent. Each state counts equally. ACS point estimates already account for survey weights; no further microdata weights are applied. Counts describe employed residents, not workplace jobs. Period correlations compare within-state endpoint changes; periods have unequal lengths and do not identify causal or lagged effects. The 2019–2021 interval combines pandemic disruption and partial recovery. Cross-sectional correlations are not evidence of what happened to individual residents.

Validation checks cover 306 state-year rows (including DC), 12 county-year rows, unique state-year keys and valid numerical ranges. check.R reports rank correlations and sensitivity excluding California. Population aging, migration, education, changes in remote work, industrial mix, survey sampling error and Census controls remain limitations.

## Assignment mapping

New appropriate data: ACS published tables, not the Blog 3 CPS extract.
At least three substantive visualizations: four figures connect levels, changes, timing and a Bay Area case.
Programmatic acquisition: Census API via PowerShell, with public responses cached.
Meaningful transformations: occupational shares, percentage-point changes, and count growth.
Interpretation: associations vary by outcome and period; no causal claim.
Final submission requires the published article URL and GitHub repository link.

