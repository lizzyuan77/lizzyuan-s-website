# Blog 3 — Participation, population aging, and the Kitagawa decomposition

**Start here:** [article](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post3/) · [editable source](index.qmd) · [data request](DATA_REQUEST.md) · [analysis](analysis.R).

Question: How much of the change in U.S. labor-force participation between 2019 and 2024 reflects age composition rather than participation within age groups? The real IPUMS CPS extract has 2,611,419 records and 2,115,648 eligible person-months. The net change is −0.54 percentage points: composition −0.98, within-age participation +0.44 (rounded).

## Where to find each file

| File or folder | Purpose |
| --- | --- |
| `DATA_REQUEST.md` | **Read first:** exact samples, variables, and data/DDI download instructions |
| `analysis.R` | Functions for weighted estimates, broad/narrow age bins, symmetric decomposition, data checks, and all three figures; command-line entry point for real microdata |
| `test_analysis.R` | Synthetic fixtures that check the calculation; never a source of empirical results |
| `index.qmd`, `draft.css` | Article source and styling; the article reads the saved real-data results |
| `results/groups.csv` | Age shares and participation rates by year; inputs behind Figures 1–2 |
| `results/annual.csv`, `results/decomposition.csv` | Annual rates and each age group's contributions; inputs behind Figure 3 |
| [results/sensitivity.csv](results/sensitivity.csv) | Broad versus narrower age-bin comparison |
| `results/audit.csv` | Record counts before and after sample restrictions |
| `results/analysis.rds` | Saved real-data result object read by the article |
| `results/provenance.txt`, `results/session-info.txt` | Original extract identifier/hash, analysis date, and R/package environment |
| `package.R`, `research.zip` | Rebuild script and downloadable code/aggregate-results bundle |
| `test-output/` | Created only by tests; figures are explicitly labeled synthetic and are excluded from the bundle |

Scripts live beside the article; data products and figures live in `results/`. Raw IPUMS files stay outside this folder. The website's `docs/blog/posts/post3/` is generated publication output, not the editable source.

## Run in this order

1. **Obtain the data.** Follow [DATA_REQUEST.md](DATA_REQUEST.md): all 12 Basic Monthly samples in 2019 and 2024, with the listed variables and ASECFLAG. Download the matching DDI XML and `.dat.gz` together; keep original names in an external data directory. You need your own IPUMS access; the raw extract is not bundled.
2. **Install dependencies once.** Install R and [Quarto](https://quarto.org/docs/get-started/), then in R:

   ```r
   install.packages(c("ipumsr", "ggplot2", "knitr", "rmarkdown"))
   ```

   The original empirical environment is in `results/session-info.txt`; versions are recorded rather than locked.
3. **From the website root, enter this post folder and check the code:**

   ```sh
   cd blog/posts/post3
   Rscript test_analysis.R
   ```

   Expected: two `PASS` messages. These use artificial fixtures and create labeled figures in `test-output/`. Passing tests does not reproduce the CPS findings.
4. **Rebuild empirical results from your DDI** (replace the example path):

   ```sh
   Rscript analysis.R "/absolute/path/to/cps_extract.xml"
   ```

   The DDI imports its corresponding raw file with correct implied decimals. Do not rescale WTFINL manually. The script saves all CSVs, `analysis.rds`, three figures, and updated provenance/session files in `results/`. It stops for missing months, duplicate person-month IDs, invalid codes/weights, ASEC inclusion, or failure of the decomposition identity. No download occurs during this step.
5. **Refresh the download bundle** from this post folder:

   ```sh
   Rscript package.R
   ```

   A standard `zip` utility must be on PATH (Rtools provides one on Windows). The explicit file list excludes raw data and `test-output/`.
6. **Render from the website root:**

   ```sh
   cd ../../..
   quarto render blog/posts/post3/index.qmd
   ```

   Quarto reads saved real-data results and writes `docs/blog/posts/post3/index.html`. Rendering alone does **not** rerun the CPS analysis. If you only want to inspect the supplied snapshot, skip data acquisition and steps 3–5 and render it directly; that checks presentation, not independent replication from microdata.

## Statistical design

Population: civilians age 16+ with LABFORCE=1 or 2 and positive WTFINL. Participation is LABFORCE=2 (employed or unemployed), not employment alone. All population statistics use WTFINL. Zero weights are removed; invalid/missing weights or unknown codes stop execution.

Weights are divided by the monthly eligible-population total and by 12. Thus each year's overall rate equals the arithmetic average of its twelve monthly weighted rates. Annual age shares equal the average monthly population share; annual within-age rates use the same normalized person-month weights. These definitions make the decomposition exact. They are not seasonally adjusted monthly estimates or counts of distinct people.

For age group g, share s and participation rate r, the change in the overall rate is exactly:

`sum((s_2024-s_2019)*(r_2024+r_2019)/2) + sum((r_2024-r_2019)*(s_2024+s_2019)/2)`.

The first term is composition; the second is within-group participation. Broad age bins are 16–24, 25–34, 35–44, 45–54, 55–64, 65–74, 75+. A narrower-bin sensitivity uses 16–19, five-year groups through 75–79, and 80+. Aging within the highest open-ended group remains unseparated. Group composition changes do not identify individual retirement transitions.

CPS repeats people across months. Repeated records across different months are expected and retained for monthly cross-sectional estimates. No independent-person standard errors, naive bootstrap intervals, or significance claims are produced. Population-control revisions and other demographic changes can also affect comparisons. No pandemic causal effect is identified by two-year accounting.

## Reading the decomposition

The article defines $P_t=\sum_g s_{g,t}p_{g,t}$, where `s` is an age group's population share and `p` its participation rate, both proportions. The two symmetric terms use the opposite variable's two-year average. Their sum equals `P_2024 - P_2019` exactly; `analysis.R` multiplies contributions by 100 to express them in percentage points. `results/decomposition.csv` contains the age-specific contributions, while Figure 3 sums each column. The article's 35–44 example is read from those results, not manually entered.

## Sources

IPUMS CPS, University of Minnesota, https://cps.ipums.org/ . Underlying CPS: U.S. Census Bureau and Bureau of Labor Statistics. Version 13.0, DOI:10.18128/D030.V13.0; extract generated 2026-09-28. Weight documentation: https://cps.ipums.org/cps/sample_weights.shtml . Labor-force definition: https://cps.ipums.org/cps-action/variables/LABFORCE . Citation guidance: https://cps.ipums.org/cps/citation.shtml .


Method: Evelyn M. Kitagawa (1955), [Components of a Difference Between Two Rates](https://doi.org/10.1080/01621459.1955.10501299), Journal of the American Statistical Association, 50(272), 1168–1194.

## Economic interpretation and background reading

The takeaway is to read age-group participation alongside the national rate when evaluating recovery. Changing population age shares can lower the headline even when participation rises within several age groups. This is an accounting finding, not evidence identifying individual retirement decisions or the causal effect of the pandemic.

- Aaronson, Cajner, Fallick, Galbis-Reig, Smith, and Wascher (2014), [Labor Force Participation: Recent Developments and Future Prospects](https://www.federalreserve.gov/pubs/feds/2014/201464/201464pap.pdf), FEDS 2014-64. Distinguishes demographic and other longer-run influences from participation changes related to the business cycle. Its historical period differs from this post's 2019–2024 comparison.
- Montes, Smith, and Dajon (2022), [The Great Retirement Boom](https://www.federalreserve.gov/econres/feds/the-great-retirement-boom.htm), FEDS 2022-081. Models retirements relative to pre-pandemic trends and distinguishes population aging from excess pandemic-era retirements. That separation uses additional assumptions and evidence not supplied by this post's age-only decomposition.

The post does not estimate discouraged-worker effects, retirement transitions, or an age-invariant causal effect. Within-age differences may reflect health, education, and other composition changes; the highest age bin also contains aging. The narrower-bin results are in [results/sensitivity.csv](results/sensitivity.csv).
