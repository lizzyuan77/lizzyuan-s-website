# Blog 5: Gender earnings, technology and geography

**Question:** Do states with more technology workers or higher household income have smaller gender earnings gaps? Did technology employment growth accompany a narrowing gap between 2019 and 2024?

[Read the published article](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post5/) · [Detailed methodology](METHODOLOGY.md) · [Rubric review](RUBRIC_REVIEW.md)

The analysis uses Census American Community Survey (ACS) 1-year estimates for **2019 and 2021–2024**, covering **50 states**, plus separate U.S. estimates. It combines two central GIS maps with earnings, representation and trend charts. The article discusses Claudia Goldin's research while distinguishing possible mechanisms from the descriptive evidence.

## Start here

**All required public data and boundaries are included.** You can reproduce the analysis without downloading new data, using a Census API key, or accessing another computer. An internet connection is needed only to install missing software/packages or optionally refresh the source data.

Two ways to get the files:

- Clone/download this repository, then open `blog/posts/post5/`.
- Download [research.zip](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post5/research.zip), unzip it, and open the extracted `post5/` folder. This standalone package contains the same analysis and documentation.

**Run every command below from the `post5` folder.** If starting at the repository root, first run:

```sh
cd blog/posts/post5
```

## 1. Install the software and packages

Required software: R, **Python 3.12**, and [Quarto](https://quarto.org/docs/get-started/). The published analysis was tested with R 4.6.1, Python 3.12 and Quarto 1.10.18. The Python requirements file pins the tested package versions; an older system Python may not support them.

Install the R packages once:

```sh
Rscript -e "install.packages(c('jsonlite', 'ggplot2', 'knitr', 'rmarkdown'), repos='https://cloud.r-project.org')"
```

Create and activate a Python environment:

**macOS / Linux**

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r code/requirements.txt
```

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r code/requirements.txt
```

If PowerShell does not allow activation, use `.\.venv\Scripts\python.exe` instead of `python` in the commands below; changing the computer's execution policy is not necessary. On Windows, R and Quarto must also be available in the terminal's PATH.

## 2. Regenerate the analysis and figures

Run these in order, with the Python environment active:

```sh
Rscript code/analyze.R
Rscript code/mechanisms.R
Rscript code/trends.R
python code/maps.py
```

| Step | What it produces |
| --- | --- |
| `analyze.R` | 2024 state earnings ratios, household income and technology shares; supporting scatterplots |
| `mechanisms.R` | Women's representation, earnings within technology, national comparisons and the expanded state data |
| `trends.R` | 250 state-year observations, five U.S. observations, endpoint changes, sensitivity checks and three trend figures |
| `maps.py` | State maps joined by FIPS, including the two maps used in the article |

The scripts save their outputs in `results/`; you do not need to copy numbers into the article manually. Inline calculations in `index.qmd` read the saved CSV files when rendered.

## 3. Rebuild the downloadable package and article

```sh
python code/package.py
quarto render index.qmd
```

`package.py` creates `research.zip` from the article source, documentation, code, cached data and results. It excludes temporary caches, virtual environments and rendered website files.

When working inside the full website repository, Quarto writes the article to `docs/blog/posts/post5/index.html`. When using the standalone ZIP, it writes `index.html` in the extracted folder. Open that HTML file to review the article. The standalone version reproduces the article; website navigation comes from the full repository's `_quarto.yml`.

## Folder guide

```text
post5/
├── README.md             # Setup and replication instructions
├── METHODOLOGY.md        # Variables, sources, geography and limitations
├── RUBRIC_REVIEW.md      # Evidence for the ten grading criteria
├── index.qmd             # Article source, including calculated numerical claims
├── post.css              # Article styling
├── code/                 # Acquisition, analysis, mapping and packaging scripts
├── data/                 # Cached Census estimates, metadata and boundaries
│   └── trends/           # Year-specific source extracts and source manifest
├── results/              # Derived CSV files, figures and sensitivity checks
└── research.zip          # Downloadable replication package
```

## Data and interpretation essentials

- **Earnings ratio:** women's median annual earnings divided by men's median, multiplied by 100. The full-time, year-round state comparison uses ACS B20017. It is an unadjusted group comparison, not equal-pay-for-identical-work evidence.
- **Technology:** computer and mathematical occupations, not the entire technology industry or AI adoption. Representation and technology employment shares use employed residents, including people working part time.
- **Income:** median household income, not accumulated wealth. The income comparison is for 2024; the multi-year charts compare ratios, shares and counts rather than unadjusted dollar growth.
- **Geography:** 50 states; DC and Puerto Rico are excluded from state comparisons. U.S. results use national tabulations, not an average of states. State boundaries and estimates are joined by FIPS. Alaska and Hawaii are relocated/resized insets.
- **Missing 2020:** Census did not release standard 2020 ACS 1-year estimates because pandemic-related response problems prevented them from meeting its quality standards. The analysis does not mix experimental estimates into the series or interpolate a value.
- **Limits:** correlations and changes are descriptive. The analysis does not identify a causal technology effect, explain each state's gap, or measure discrimination. Published margins of error are retained; figures show point estimates without significance claims.

The exact table cells, population definitions, formulas, URLs, retrieval dates, projections and Goldin references are documented in [METHODOLOGY.md](METHODOLOGY.md). The national occupation earnings comparison uses a consistent B24022 civilian-employed population; its universe differs from the broader B20017 state measure.

## Optional: refresh the public source files

This is **not needed for replication from the included data**. It downloads Census files and requires an internet connection:

```sh
python code/acquire.py
python code/acquire_trends.py
```

Then repeat the analysis, maps, package and render commands above. `acquire.py` retains the included S2401 API response; instructions for refreshing it separately are in [METHODOLOGY.md](METHODOLOGY.md). `acquire_trends.py` records source URLs and retained columns in `data/trends/source-manifest.json`.

## Troubleshooting

| Message or symptom | What to do |
| --- | --- |
| A `data/...` or `results/...` file cannot be found | Run from `post5/` and run all analysis steps in order. |
| R reports a missing package | Run the R package installation command in step 1. |
| Python reports `No module named ...` | Activate `.venv` and install `code/requirements.txt` using that environment's Python. |
| `Rscript` or `quarto` is not found | Install the application and make its command available in the terminal. |
| `maps.py` cannot find `states-expanded.csv` | Run `analyze.R` and then `mechanisms.R` first. |
| A fresh Census download fails | Use the included cached data; downloads are optional. |

## Submission

The assignment requires **both** the [published article URL](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post5/) and the [GitHub repository URL](https://github.com/lizzyuan77/lizzyuan-s-website). The relevant repository folder is [`blog/posts/post5/`](https://github.com/lizzyuan77/lizzyuan-s-website/tree/main/blog/posts/post5).
