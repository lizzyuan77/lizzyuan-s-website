# Blog 5 — Gender earnings, technology, and income geography

## Reproduce offline

Run from this post5 directory. R packages: jsonlite, ggplot2. Python 3.12+ packages: matplotlib, numpy, pyshp, pyproj; install the tested versions with `python3 -m pip install -r code/requirements.txt`. Quarto with knitr and rmarkdown renders the article. Tested with R 4.6.1, Python 3.12, and Quarto 1.10.18; R package versions are recorded in results/session-info.txt.

```sh
Rscript code/analyze.R
Rscript code/mechanisms.R
Rscript code/trends.R
python3 code/maps.py
python3 code/package.py
quarto render index.qmd
```

The included public raw inputs suffice; neither the other computer nor an API key is needed. `data/` contains raw Census tables, metadata, and state boundaries; `code/` holds acquisition, analysis and map scripts; `results/` holds derived data and figures. The article reads numerical claims from results/states-expanded.csv, national.csv and mechanism-correlations.csv during rendering. Run all three analysis scripts and maps before packaging and rendering. The longer article follows the user's request for deeper sequential analysis rather than the assignment's approximate word-count guideline.

## Public sources and measures

- ACS 2024 **1-year**, B20017: male median annual earnings for full-time, year-round workers B20017_003E and female B20017_006E. Universe: population age 16+ with earnings. Full-time, year-round means usually working 35+ hours a week and working 50–52 weeks. The summary-file columns are B20017_E003 and B20017_E006, with M columns giving published 90% margins of error.
- Female/male ratio = 100 × female median / male median. Gap = 100 − ratio, measured as percent of the male median. This is a ratio of two group medians, not a median individual pay ratio or an adjusted equal-work comparison. Earnings include wages/salaries and net self-employment income.
- B19013_001E (summary column B19013_E001): median household income. This is income, **not wealth**, and its universe differs from the earnings sample. Dollars use 2024 purchasing power, without geographic price adjustment.
- S2401_C01_007E / S2401_C01_001E × 100: computer and mathematical occupations as a share of civilian employed residents age 16+. This occupational concentration measure is not an industry definition or technology adoption measure. It covers all employed residents, not only full-time/year-round workers; the difference is deliberate and documented.
- Same-year state FIPS join; 50 states, excluding DC and Puerto Rico. Correlations weight states equally. ACS estimates already reflect sampling weights. No microdata weights should be reapplied.
- 2024 1:20m Census state boundaries. Original CRS NAD83 (EPSG:4269). Lower 48 projection EPSG:5070; Alaska EPSG:3338; Hawaii EPSG:26904. Alaska and Hawaii are resized and relocated insets. State names/labels are joined via FIPS, not row order. Legends differ across maps.

Data URLs:

- https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b20017.dat
- https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/acsdt1y2024-b19013.dat
- https://api.census.gov/data/2024/acs/acs1/subject/groups/S2401.json
- https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip

Earnings/income retrieved October 19, 2026. S2401 cached response copied unchanged from Blog 4, originally retrieved October 4, 2026. These are the same 2024 release, not mixed years. Boundary archive also copied from Blog 4.

## Refresh

`python3 code/acquire.py` refreshes the public detailed tables, their metadata and boundaries. It preserves the cached S2401 response, so offline replication does not depend on API access. To refresh S2401 separately, request NAME,S2401_C01_001E,S2401_C01_001M,S2401_C01_007E,S2401_C01_007M from the 2024 ACS 1-year subject API for state:* and save its JSON array to data/acs-state-2024.json. An authenticated request may be necessary. Keep your own key outside the repository and never write authenticated URLs to logs. The analysis uses named columns and permits the extra S2301 columns in the included original response.

## Interpretation and validation

### Five-year comparison

`python3 code/acquire_trends.py` retrieves 2019, 2021, 2022, 2023 and 2024 ACS 1-year tables B20017, B24010 and B24022. Its offline caches under data/trends/ preserve exact source strings for selected estimate/MOE columns and US/state rows. Each year/table has its own retained variable metadata. The acquisition asserts that full-time and occupational definitions match the intended measures; the older metadata use different capitalization. Source URLs and the retained columns are recorded in data/trends/source-manifest.json. The 2019 files use Census's table-based prototype *file format*, which contains the standard 2019 ACS estimates; these are not the 2020 experimental estimates.

`Rscript code/trends.R` produces 250 state-year observations and five separate US observations. DC and Puerto Rico are excluded from comparisons. The 2024 observations are reconciled against the independent cross-sectional files. National trends use US tabulations, not averages of state values. State endpoint comparisons are 2024 minus 2019 in percentage points. Tech-share and earnings-ratio growth correlations compare those within-state endpoint differences, equally weighting states. Spearman correlations and a sensitivity omitting the largest absolute earnings-ratio change (Wyoming) accompany Pearson correlations. This is not a causal regression, a difference-in-differences design, or a panel following the same people.

The national earnings trend compares all occupations and computer/mathematical occupations within B24022's identical full-time, year-round civilian employed universe. The state earnings map/changes use B20017's broader population with earnings, consistent with the original gap definition. B24010 technology concentration and representation use all civilian employed residents. These universe distinctions are explicit in captions and article notes.

There is no standard 2020 ACS 1-year release. No interpolated point, filled value or connecting line bridges that year. Population-control updates, pandemic employment selection, migration and demographic changes limit temporal interpretation. Suppressed/nonpositive earnings become missing, not zero. Cross-year comparisons use ratios, shares and counts; no unadjusted nominal dollar growth is reported. Published MOEs are preserved; no trend or endpoint difference is claimed statistically significant. Results include national-trends.csv, state-trends.csv, state-trend-changes.csv, trend-correlations.csv and three trend figures.

### Additional occupation analysis and Goldin framing

`code/mechanisms.R` adds three 2024 ACS 1-year detailed tables:

- B24010: all civilian employed residents age 16+. Male total E002, female total E153; male computer/mathematical E020, female computer/mathematical E171. Female tech share = 100 × E171/(E020 + E171); female workforce share = 100 × E153/E001. Representation shortfall is workforce share minus tech share, in percentage points. Female tech employment rate = 100 × E171/E153; male rate = 100 × E020/E002. The same code checks that these counts match the independently cached S2401 numerator and denominator exactly in all 50 states.
- B24020: the same sex/count definitions among full-time, year-round civilian employed residents. This checks whether underrepresentation persists when part-time workers are excluded. The narrower workforce has a different female share; compare each universe with its own denominator.
- B24022: full-time, year-round civilian employed residents' median earnings by sex/occupation. E008 is the male computer/mathematical median, E044 the female median. E002/E038 supply male/female medians across all occupations for the national chart, giving its two groups an identical population definition. This employed/civilian universe differs from B20017's broader population with earnings; the article's state map retains the conventional B20017 measure. The published M columns retain 90% MOEs. Nonpositive/suppressed earnings values become missing, never zero; no state claim uses a suppressed value. These are broad occupational medians, not adjusted identical-job comparisons.

Files ending `-states.dat` preserve the original header and original source rows for the US (0100000US) and all state-level geographies (0400000US prefix): 53 rows including US, 50 states, DC and Puerto Rico. The acquisition script downloads the complete public file to a temporary directory, selects those geographic rows without changing their values, and saves the subset. Only 50 states enter state comparisons. National figures use the separate US row, not an average of state medians.

The conditional correlations are correlations between residuals from two linear regressions, each on an intercept and median household income. This is a transparent descriptive partial correlation, not a causal control strategy. Income may be jointly determined with earnings and household formation. No coefficients, causal effects, p-values, or significance claims are inferred from these comparisons. Small state occupation medians may have substantial sampling error; the article does not rank states on within-tech pay or test differences.

Results include states-expanded.csv (joined estimates and MOEs), national.csv, mechanism-correlations.csv, a representation map, a four-state comparison, national earnings bars, and a supplemental all-state representation scatterplot. The technology-concentration map and representation scatterplot are retained as supplemental outputs even when not embedded in the article. Maps are now generated from states-expanded.csv.

The article distinguishes three facts: women are underrepresented in technology; a broad within-tech earnings gap remains; and representation alone is weakly correlated with the overall state ratio. It does not assert that occupational representation explains the state gap. Medians are not additive, so no decomposition of median earnings into occupational contributions is attempted. Nor does a single-year geographic correlation show what narrows a gap over time.

Claudia Goldin (2014), A Grand Gender Convergence: Its Last Chapter, https://doi.org/10.1257/aer.104.4.1091, provides the job-hours/flexibility framework. Her results identify relatively smaller adjusted technology/science gaps than business gaps; the article preserves that distinction. Goldin and Katz (2016), A Most Egalitarian Profession: Pharmacy and the Evolution of a Family-Friendly Occupation, https://doi.org/10.1086/685505 (open working paper https://www.nber.org/papers/w18410), illustrates how work organization can reduce flexibility costs. The Nobel 2023 background supplies the parenthood context. These are research-informed mechanisms, not findings causally established by this state analysis. Suggested practices are questions for evaluation, not estimated policy effects.

Additional source URLs follow the existing detailed-table download base with filenames acsdt1y2024-b24010.dat, acsdt1y2024-b24020.dat and acsdt1y2024-b24022.dat. Their API group metadata are included. Retrieved October 19, 2026.

Analysis asserts 50 unique states, positive usable earnings/income and matching state labels. Maps assert an exact 50-state spatial join and no out-of-range color values. Published MOEs are retained; no significance, causal, or adjusted discrimination claim is made. Correlations are Pearson and Spearman descriptive comparisons, not causal estimates. No ratio confidence intervals are constructed because covariance is not available in these tabulations. An earnings ratio is not an hourly wage comparison. Employment selection, occupation, experience, education, caregiving, and within-full-time hours remain uncontrolled. States conceal substantial within-state differences; large map areas do not have larger statistical weight.

The earnings tables use Census's male/female sex categories and do not cover all gender identities. “Gender earnings gap” is used in the article with this limitation explicit.

## Assignment coverage

A clear geographic question; two substantive GIS maps with interpretation; two supporting scatterplots; documented Census sources; saved programmatic results; organized code/data/results and these replication instructions. Blog 5 does not require CPS microdata or three maps. Submit the published post URL and repository URL.
