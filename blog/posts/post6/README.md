# Blog 6: Does one year of income mislead us about mobility?

**Question:** How much does the estimated parent–child income association change when income is averaged across three observations instead of measured in one year?

[Read the published tutorial](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post6/)

The analysis links children born 1970–1974 in the Panel Study of Income Dynamics (PSID) to their birth mothers with SQL (SQLite) inside Python. It builds inflation-adjusted parental family income for 1980–1982 and children's own labor earnings for 2000–2004 and 2010–2014, then estimates weighted intergenerational elasticities (IGEs) by sex.

## Folder guide

| Path | Contents |
| --- | --- |
| `index.qmd` | The tutorial. Every number in the text comes from `results/text_values.yml` via `{{< meta >}}`. |
| `post.css` | Page styling |
| `code/00_toy_example.py` | Fictional two-generation example used in the tutorial (no PSID data) |
| `code/01_import.py` | Reads the PSID files and builds `data/working/blog6.sqlite` (5 tables) |
| `code/02_match.sql` | Parent–child match, `LEFT JOIN` audit, parent and child income histories |
| `code/03_summarize.sql` | `GROUP BY` summaries: one row per child |
| `code/02_run_sql.py` | Runs both `.sql` files from Python, checks joins, writes sample-flow counts |
| `code/04_estimate.py` | Weighted IGEs, mother-clustered SEs, cluster-bootstrap differences |
| `code/05_figures.py` | Figures, including the two used in the article |
| `code/06_text_values.py` | Writes every number quoted in the article to `results/text_values.yml`, plus two small Markdown tables |
| `code/package.py` | Builds `research.zip` from an allowlist (never includes microdata) |
| `results/` | Aggregate tables (`.csv`) and figures (`.png`). Nothing at the person level. |
| `data/` | **Not in the repository.** Your local PSID files and SQLite database (git-ignored). |

## 1. Request the PSID data (free, registration required)

PSID's conditions of use do not allow redistributing the microdata, so you need your own copy. Register at <https://simba.isr.umich.edu/>, then:

**A. Data Center extract.** Go to Data Center → Variable List, paste the list below, then Add Variables. Check out with *Microsoft Excel Spreadsheet*, *HTML codebook*, *compressed (.zip)*, and **All Individuals**, with no subsetting. PSID emails a download link. Unzip it to `data/raw/J366624/` and rename the spreadsheet to `J366624.xlsx` if your job number differs (or edit the path in `01_import.py`).

```
ER30001 ER30002 ER32000 ER31996 ER31997
ER30343 ER30344 ER30345 ER30346 V7502 V8065
ER30373 ER30374 ER30375 ER30376 V8202 V8689
ER30399 ER30400 ER30401 ER30402 ER30404 V8802 V9375
ER33601 ER33602 ER33603 ER33604 ER33606 ER33637 ER17002 ER20456 ER20443 ER20447
ER33701 ER33702 ER33703 ER33704 ER33706 ER33740 ER21002 ER24099 ER24116 ER24135
ER33801 ER33802 ER33803 ER33804 ER33806 ER33848 ER25002 ER28037 ER27931 ER27943
ER34101 ER34102 ER34103 ER34104 ER34106 ER34154 ER47302 ER52343 ER52237 ER52249
ER34201 ER34202 ER34203 ER34204 ER34206 ER34268 ER53002 ER58152 ER58038 ER58050
ER34301 ER34302 ER34303 ER34305 ER34307 ER34413 ER60002 ER65349 ER65216 ER65244
```

Each line is one interview wave: individual-file interview number, sequence number, relationship to reference person, age, year of birth, and longitudinal weight, followed by the family-file interview number, total family income, and reference-person and spouse labor income. PSID adds a few release-number and family-ID variables automatically (95 columns in total).

**B. Parent Identification File.** Data → Packaged Data → Main and Supplemental Studies → *Parent Identification: 2023*. Unzip `pid23.zip` to `data/raw/pid23/`.

Expected layout:

```
post6/data/raw/J366624/J366624.xlsx
post6/data/raw/pid23/PID23.txt
```

To keep the data elsewhere, set `PSID_DIR` to the folder that contains `raw/`, for example `export PSID_DIR=~/psid` (macOS/Linux) or `$env:PSID_DIR="C:\psid"` (PowerShell).

## 2. Install Python packages

Tested with Python 3.10 and the versions in `code/requirements.txt`. `sqlite3` is part of Python.

```sh
cd blog/posts/post6
python3 -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r code/requirements.txt
```

The regression and clustered standard errors are written directly in NumPy (see `fit_ige` in `04_estimate.py`), so `statsmodels` is not required. `statsmodels.api.WLS` gives identical point estimates if you want to compare.

## 3. Run the analysis (from the `post6` folder)

```sh
python code/00_toy_example.py   # fictional tables for the tutorial
python code/01_import.py        # builds data/working/blog6.sqlite
python code/02_run_sql.py       # runs 02_match.sql and 03_summarize.sql
python code/04_estimate.py      # IGEs and bootstrap (2,000 draws, seed 20261023)
python code/05_figures.py       # figures
python code/06_text_values.py   # numbers quoted in the article
python code/package.py          # research.zip
```

All scripts are fast (a few seconds each). `01_import.py` stops if any table key is not unique, and `02_run_sql.py` stops if any analysis table has more than one row per child.

## 4. Render the page

From the website root:

```sh
quarto render blog/posts/post6/index.qmd
```

The page runs no code when rendered: it only needs Quarto (tested with 1.10.18). Output goes to `docs/blog/posts/post6/index.html`.

## Outputs

| File | Contents |
| --- | --- |
| `table_counts.csv` | Rows in each SQLite table |
| `link_audit.csv` | `LEFT JOIN` audit of the mother link, by sex |
| `join_checks.csv` | One-row-per-child checks, and the 9-rows-per-child naive join |
| `sample_flow.csv` | Sample selection, step by step, by sex |
| `zero_exclusions.csv` | Children dropped for zero earnings or bottom-coded parental income |
| `ige_results.csv` | Main sample: single-year, partly averaged and fully averaged IGEs |
| `ige_bottomcode_sensitivity.csv` | IGE if PSID's $1 bottom code were read as a real income |
| `year_to_year_correlation.csv` | Correlation of log income across years (noise in one year) |
| `ige_lifecycle.csv`, `ige_by_year.csv` | Life-cycle comparisons on a fixed group of children |
| `ige_differences.csv` | Cluster-bootstrap differences (daughters − sons, averaged − single, age 40 − age 30) |
| `sample_stats.csv` | Weighted means and medians, ages, and log-income spread |
| `toy_*.csv`, `_toy_*.md` | Fictional example tables |
| `text_values.yml` | Every number quoted in the article, generated from the CSV files |
| `*.png` | Article figures |
| `session-info.txt` | Software versions |

## Key definitions and choices

- **Children:** born 1970–1974 (most recent valid report of year of birth), sex recorded.
- **Parent:** birth mother from the Parent Identification File. A childhood year counts only if child and mother were current members (sequence 1–20) of the **same** family in that interview.
- **Parental income:** total family money income, income years 1980–1982 (interviews 1981–1983). Single-year measure: 1981. The value `1` is PSID's bottom code for "one dollar or less, including zero and negative amounts" and is stored as 0.
- **Child income:** a role-dependent labor-earnings measure. Reference-person fields include total labor income, while spouse fields exclude farm and business income. They are not harmonized measures of total labor income. The tutorial reports the existing estimates as a workflow illustration; do not interpret the sex or age comparisons as clean comparisons of total earnings persistence. Household-role changes can change coverage within a person's history. Construct comparable fields across roles and years and rerun before making that substantive claim. Fields are listed in the extraction recipe above. Mature window: income years 2010, 2012 and 2014 (single year 2012); early window: 2000, 2002 and 2004 (single year 2002). Other family members have no earnings field and are not imputed.
- **Real dollars:** 2020 dollars using BLS CPI-U U.S. city average, all items, annual averages (1980 = 82.4, 1981 = 90.9, 1982 = 96.5, 2000 = 172.2, 2002 = 179.9, 2004 = 188.9, 2010 = 218.056, 2012 = 229.594, 2014 = 236.736, 2020 = 258.811), deflated by income year.
- **Averaging and logs:** average real dollars across all three years first, including genuine zeros, then take logs. Regressions need positive single-year and averaged incomes for both generations.
- **Weights and uncertainty:** the child's 2015 core/immigrant individual longitudinal weight (ER34413). Standard errors are clustered by mother; differences use a cluster bootstrap. Neither reflects PSID's full stratified design.

## Limitations and interpretation

The matched sample is small (about 200 children per sex), so intervals are wide. Requiring records from two generations over three decades adds selection that weights may not fully remove. Three years of parental income is still a short average. Annual personal earnings do not measure total household resources. The analysis does not test whether caregiving, hours, or participation explains a sex difference. The averaged daughter–son difference and each group's averaged-minus-single change have bootstrap intervals including zero. The sons' averaged age-window difference also has an interval including zero. Changes across ages also span different calendar periods and do not isolate life-cycle bias.

## Note on SQLite and network or synced folders

If `01_import.py` fails with `sqlite3.OperationalError: disk I/O error`, the folder is probably a network, cloud-synced or virtual mount that does not support SQLite's journal file. Point `PSID_DIR` at an ordinary local folder.
