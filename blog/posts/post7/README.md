# Blog 7: College majors, earnings parity, and earnings levels

A roughly 700-word draft with **one interactive Plotly chart**. Question: which majors have the smallest observed gender earnings gaps among comparable full-time, year-round employees? This is an unpublished draft.

## Inputs and population

Source: 2024 ACS 1-year PUMS U.S. person CSV archive, containing **both** `psam_pusa.csv` and `psam_pusb.csv`. Puerto Rico is not in this U.S. archive. The source file and variable metadata are public Census products; no account or API key is needed. `data/source_manifest.json` records the URL, retrieval date, SHA-256, size, software versions, and display-family mapping.

Filter: AGEP 25–64; SCHL >= 21 (BA or higher); valid FOD1P (first degree entry); WKHP >= 35; WKWN >= 50; WAGP > 0; COW in 1–5; positive PWGTP. COW 1–5 denotes private/government employee classes. This is a wage-and-salary comparison, not total income or self-employment income. The class-of-worker report describes the current or most recent job, while annual income covers the prior 12 months; it does not identify every job contributing to that income.

Both representation and earnings refer to the **same included sample**. No mixing all degree holders with earners or different ages. Representation is not the share of students or all graduates. Sex is tabulated male/female. Graduate-degree holders are included; their undergraduate first major is used. Different reported second majors are not additional records.

## Measures

- Real annual wages/salary = WAGP × ADJINC / 1,000,000, in 2024 dollars.
- Weighted median: sort adjusted earnings; select the first earnings value where cumulative weights reach half the total. No interpolation or averaging of two middle observations.
- Cents per male dollar = 100 × women's weighted median / men's weighted median. Equality is 100. A value above 100 means the women's median is higher.
- Closeness to parity = absolute distance of that ratio from 100; not simply the highest female-to-male ratio.
- Women's share = 100 × sum(PWGTP for included women) / sum(PWGTP for all included workers).
- Each shown major requires >=100 sampled women and >=100 sampled men. This author-chosen screen is not a Census reliability standard. `excluded_majors.csv` lists the 45 omitted categories. The displayed 129 majors have 420,080 sample records; all eligible workers total 431,517 records.

Six author-created display families group the major codes; these are navigation aids, not new estimates of group medians. Full mapping is in `code/analyze.py` and the source manifest. The chart always plots individual major estimates. It never averages subgroup medians to make a family median.

## Uncertainty

For each statistic, recalculate it using PWGTP1–PWGTP80. SDR standard error is `sqrt((4/80) * sum((replicate_estimate - full_estimate)**2))`. Ratio errors come from **replicated ratios**, preserving covariance of the two medians. The chart's pointwise 90% interval is estimate +/- 1.645 × SE. Census source: https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2024AccuracyPUMS.pdf.

Signed replicate weights are retained exactly as supplied (121 negative cells among included workers' replicate weights). For replicate quantiles, use the same first cumulative half-total crossing convention; do not clamp weights. Full-sample weights are positive. Ratios require positive male medians and replicate totals. These conditions are asserted.

General Business has identical ratio estimates in all replicates. This does not establish zero uncertainty. Its ratio interval is marked unavailable, rather than displayed with zero width; a generalized-variance fallback is not implemented. Survey rounding and concentration at common earnings amounts can limit quantile precision. The chart says this explicitly.

Intervals do not account for selecting the closest estimate across 129 majors. No claim is made that a particular major is the statistically established smallest-gap major. Estimates are unadjusted for age composition, occupation, geography, seniority, graduate education, or within-full-time hours. Differences in medians do not measure equal pay for identical work or the causal effect of selecting a major.

## Reproduce

Tested with Python 3.12, numpy 2.3.5, pandas 2.2.3. Quarto is needed only for the article. The chart uses the included official Plotly.js **basic 3.1.0** bundle, which supports scatterplots; Python's plotly package is not needed.

From the `post7/` folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r code/requirements.txt
python code/acquire.py --cache /path/to/census-cache
python code/analyze.py --source /path/to/census-cache/csv_pus.zip
python code/occupation_context.py --source /path/to/census-cache/csv_pus.zip
python code/build_chart.py
python code/package.py
```

The national archive is about **575 MB compressed**, about 2.4 GB uncompressed. The analysis reads it in 100,000-row chunks without extracting the full CSV files, retaining eligible records for the weighted calculations. Allow sufficient disk, memory, and several minutes. No individual identifiers are written to the published outputs. Only aggregate estimates, metadata, and code are packaged.

Alternatively, explore or rebuild the chart directly from included aggregates with `python code/build_chart.py`; this does not rerun the microdata analysis.

From the website root:

```sh
quarto render blog/posts/post7/index.qmd
quarto preview
```

Outside the website, `quarto render index.qmd` makes a standalone page. Serve the rendered folder over HTTP so the embedded chart and local Plotly script load reliably. The chart itself is self-contained with the included `vendor/` folder and needs no remote scripts.

## Files and interactions

- `code/analyze.py`: population filter, weighted medians/shares, replicate uncertainty, sample screen, saved estimates.
- `code/acquire.py`: downloads public national data and degree/occupation metadata; no API key.
- `code/occupation_context.py`: weighted occupation shares and usual weekly hours on exactly the original worker sample. Joins context to chart estimates without changing any earnings ratios.
- `code/chart_template.html`, `code/build_chart.py`: chart controls, Plotly scatter, interval toggle, accessible table.
- `results/majors.csv`, `majors.json`: the same 129 aggregate estimates, full precision and presentation precision respectively.
- `results/sample_flow.json`, `excluded_majors.csv`: population/coverage checks.
- `results/chart.html`: the one article visualization.
- `data/FOD1P.json`, `source_manifest.json`: public code labels and provenance.
- `vendor/plotly-basic-3.1.0.min.js`: official plotting library (license included in its header).
- `research.zip`: code, documentation, aggregates, chart, and plotting library; excludes the large national microdata archive.

The redesigned explorer uses one Plotly canvas with three linked views:

1. **Compare gaps:** labeled point estimates and 90% intervals, ten majors per page. Filter by family and order by closeness to parity, women's earnings, representation, or name. Click a dot or use the major dropdown to select a major. Changing a view preserves that selection. Ordering is descriptive, not statistically established ranking.
2. **Pay & hours:** paired annual median earnings and weighted mean usual weekly hours for the selected major. Both scales begin at zero. The two measures refer to the same included workers, but no hourly wage or causal hours effect is calculated.
3. **Career destinations:** two 100% stacked bars, with a shared category set for women and men. Categories are the union of each sex's top three occupations, plus journalists for journalism. All remaining jobs are grouped as Other. The numerical legend gives exact shares by sex.

Guided question buttons open Journalism/careers, Finance/pay-and-hours, and Nursing/careers. Reset restores the initial comparison. A numerical data table is available for keyboard and touch users. All controls run locally in the browser. The embedded frame resizes to its contents. Income ratios and uncertainty are unchanged from the original analysis.

## Economic interpretation and research

The revised article asks readers to interpret earnings by degree as a mixture of career destinations, rather than pay for one occupation. It does not claim that occupational sorting or hours causally explains the observed ratio for any particular major.

- Sloane, Carolyn M., Erik G. Hurst, and Dan A. Black (2021). **College Majors, Occupations, and the Gender Wage Gap.** Journal of Economic Perspectives 35(4):223–248. https://www.aeaweb.org/articles?id=10.1257/jep.35.4.223. Evidence about sorting between majors and into occupations within majors motivates the occupation context.
- Goldin, Claudia (2014). **A Grand Gender Convergence: Its Last Chapter.** American Economic Review 104(4):1091–1119. https://www.aeaweb.org/articles?id=10.1257/aer.104.4.1091. The job-design/temporal-flexibility framework concerns how hours and availability are rewarded. The chart does not estimate the return to an extra hour or a flexibility penalty.
- Goldin, Claudia, and Lawrence F. Katz (2016). **A Most Egalitarian Profession: Pharmacy and the Evolution of a Family-Friendly Occupation.** Journal of Labor Economics 34(3):705–746. https://www.journals.uchicago.edu/doi/abs/10.1086/685505. Substitutability and organizational changes in the pharmacist profession provide an example of job design. These occupation-based historical findings are not treated as an explanation of today's journalism or pharmacy-major estimates. The paper's erratum corrects axis labels in Figure 4: https://www.journals.uchicago.edu/doi/abs/10.1086/688621.
- Additional background consulted: Bertrand, Marianne, Claudia Goldin, and Lawrence F. Katz (2010). **Dynamics of the Gender Gap for Young Professionals in the Financial and Corporate Sectors.** AEJ: Applied Economics 2(3):228–255. https://www.aeaweb.org/articles?id=10.1257/app.2.3.228. This study follows MBAs from one U.S. school and links divergent careers to prior training, interruptions, and weekly hours. It is not evidence about the causal mechanisms in our undergraduate-major sample.

### Added descriptive context

`OCCP` is the current or most recent occupation. Labels come from `data/OCCP.json`. Occupation shares and mean usual hours use PWGTP, the same filters as the earnings calculation, and the same source archive. The code verifies that the eligible count equals the original analysis and that merging context leaves every earnings ratio unchanged.

`results/occupation_context.csv` contains the weighted modal occupation and its share separately by sex, mean WKHP, and the share reporting OCCP 2810 (news analysts, reporters, and journalists). The occupation with the largest share may employ only a small minority; the chart displays that share, not a claim that most graduates enter it. In the included journalism-major sample, 4.4816% report OCCP 2810. It is not a share of all journalism graduates regardless of employment or hours.

Hours and occupation shares are exploratory point estimates; uncertainty ranges in the chart apply to the earnings ratio only. No adjustment/decomposition is made for job mix, experience, age, hours, graduate education, or career breaks. In particular, the draft does not claim journalism has flexible schedules or that its near-parity is caused by the observed job mix.

### Career composition output

`results/occupation_shares.json` contains the shared occupational categories and weighted female/male shares for every displayed major. Each sex's bar is checked to sum to 100%. The Other category is explicitly shown; the selected occupations are not presented as the whole career distribution. `occupation_context.py` generates this file along with the modal-job context. Earnings and hours modes use the original `majors.json` estimates. The chart's views are coordinated alternatives within one explorer, not additional unrelated article figures.
