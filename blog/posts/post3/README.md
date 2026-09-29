# Blog 3 — replication materials

Question: Did changes in age composition account for the change in U.S. labor-force participation between 2019 and 2024?

Real IPUMS CPS extract analyzed: 2,611,419 records, with 2,115,648 eligible person-months. Annual participation: 63.40% (2019), 62.86% (2024). Composition: -0.98 percentage points; within-age: +0.44. Synthetic tests validate calculations separately and are never used as empirical results.

## Replication

Install R packages `ipumsr` and `ggplot2` from CRAN. Obtain the extract specified in DATA_REQUEST.md. Run from this directory:

```
Rscript test_analysis.R
Rscript analysis.R "path/to/cps_extract.xml"
quarto render index.qmd
```

Quarto also needs knitr/rmarkdown. The DDI imports corresponding raw data with correct implied decimal handling; do not rescale WTFINL by hand. Keep downloaded data outside this folder. Publish code, documentation, aggregated results and figures only after review, not the raw extract.

## Statistical design

Population: civilians age 16+ with LABFORCE=1 or 2 and positive WTFINL. Participation is LABFORCE=2 (employed or unemployed), not employment alone. All population statistics use WTFINL. Zero weights are removed; invalid/missing weights or unknown codes stop execution.

Weights are divided by the monthly eligible-population total and by 12. Thus each year's overall rate equals the arithmetic average of its twelve monthly weighted rates. Annual age shares equal the average monthly population share; annual within-age rates use the same normalized person-month weights. These definitions make the decomposition exact. They are not seasonally adjusted monthly estimates or counts of distinct people.

For age group g, share s and participation rate r, the change in the overall rate is exactly:

`sum((s_2024-s_2019)*(r_2024+r_2019)/2) + sum((r_2024-r_2019)*(s_2024+s_2019)/2)`.

The first term is composition; the second is within-group participation. Broad age bins are 16–24, 25–34, 35–44, 45–54, 55–64, 65–74, 75+. A narrower-bin sensitivity uses 16–19, five-year groups through 75–79, and 80+. Aging within the highest open-ended group remains unseparated. Group composition changes do not identify individual retirement transitions.

CPS repeats people across months. Repeated records across different months are expected and retained for monthly cross-sectional estimates. No independent-person standard errors, naive bootstrap intervals, or significance claims are produced. Population-control revisions and other demographic changes can also affect comparisons. No pandemic causal effect is identified by two-year accounting.

## Rubric mapping

Question and motivation: headline question and pre-pandemic comparison. Clear explanation: weighted participation and aging intuition. Interpretation: age composition outweighs positive within-age changes. Data presentation: three labeled complementary figures. Organization: code here, raw files outside project, outputs in results. Reproducibility: executable script and validation tests. Specific requirements: genuine IPUMS CPS input, WTFINL weighting, three figures, one coherent story.

## Sources

IPUMS CPS, University of Minnesota, https://cps.ipums.org/ . Underlying CPS: U.S. Census Bureau and Bureau of Labor Statistics. Version 13.0, DOI:10.18128/D030.V13.0; extract generated 2026-09-28. Weight documentation: https://cps.ipums.org/cps/sample_weights.shtml . Labor-force definition: https://cps.ipums.org/cps-action/variables/LABFORCE . Citation guidance: https://cps.ipums.org/cps/citation.shtml .

