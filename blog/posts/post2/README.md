# Blog 2 — What Is Your Student ID Worth?

**Start here:** [read the article](https://lizzyuan77.github.io/lizzyuan-s-website/blog/posts/post2/) · [editable article](index.qmd) · [clean admission data](data/derived/museum_prices.csv) · [analysis script](analyze.R).

The question is how much a student ID saves on the **same museum visit**, comparing a student and nonstudent of the same age. The September 21, 2026 snapshot covers 18 institutions in eight cities. It is a selected sample, not a representative city ranking. Original collection timestamps are UTC (September 22). Two SAAM URLs represent one institution; Barnes was a separate preliminary pilot exclusion.

## File guide

| File or folder | Purpose |
| --- | --- |
| `index.qmd`, `post.css` | Article source and styling |
| `run.R` | One-command, offline rebuild of all analysis outputs and the download bundle |
| `analyze.R` | rvest extraction, cleaning, price comparisons, CSV summaries, and two figures |
| `build-explorer.R`, `explorer-template.html` | Generate every explorer row, price, source link, and condition from the same analysis data |
| `explorer.html` | Generated table included in the article; do not edit prices here |
| `package.R`, `research.zip` | Rebuildable download bundle with code, evidence, results, and documentation |
| `acquire.R`, `sources.csv` | Optional collection script and candidate official URLs; never run by a render |
| `rules.csv` | Reviewed label patterns, price types, and manually reviewed eligibility/schedule notes |
| `data/evidence/` | 18 short factual HTML extracts supporting offline price extraction |
| `data/derived/` | Generated museum-level data and city/region summaries |
| `results/` | Two generated figures, session information, original collection log, screening decisions, and raw-page hashes |

Scripts live beside the article rather than in a separate code folder. This table is the map to their roles. The repository's `docs/blog/posts/post2/` contains rendered publication files, not the editable sources.

## Reproduce the published snapshot offline

1. Install R. Install these packages once:

   ```r
   install.packages(c("rvest", "xml2", "ggplot2", "knitr", "rmarkdown"))
   ```

2. From the **website root**, run:

   ```sh
   Rscript blog/posts/post2/run.R
   ```

   This reads the supplied local evidence, re-extracts admission prices with rvest, checks required labels and valid prices, and regenerates all three CSVs, both PNG figures, `explorer.html`, `results/session-info.txt`, and `research.zip`. It makes **no network requests**. It requires the standard `zip` utility on your PATH to build the bundle; on Windows, Rtools supplies one. In an extracted bundle, run `Rscript run.R` from its post folder.

3. Install [Quarto](https://quarto.org/docs/get-started/). From the **website root**, build the article:

   ```sh
   quarto render blog/posts/post2/index.qmd
   ```

   Quarto re-runs the offline analysis and writes `docs/blog/posts/post2/index.html`. Use `run.R` first when updating the downloadable bundle. The article's numerical claims use inline R expressions rather than copied results. The explorer uses the same generated data as the figures.

The last successful environment is recorded in `results/session-info.txt`. The original analysis used R 4.6.1, rvest 1.0.5, and ggplot2 4.0.3. The revised replay is also checked locally; the generated session file records its actual versions. Package versions are documented, not locked: different graphics-library versions may change rendering without changing prices.

### What offline reproduction does and does not establish

The evidence files are exact short matched price text inside a **new minimal HTML wrapper**, not original preserved DOM pages. Offline replay checks the extraction logic, arithmetic, and presentation against those extracts. It cannot independently reconstruct omitted page context or verify that a price is still current. Original downloaded pages are not required for offline replay and are not included publicly; their recorded hashes are in `results/raw-manifest.csv`.

If you possess an original raw cache, from this post folder use `Rscript analyze.R --raw /absolute/path/to/cache`, then `Rscript package.R`. Both raw and evidence modes use the same label patterns. A fresh scrape is a separate exercise and may produce different prices: do not silently relabel it as the September snapshot. Missing labels stop the parser; failed requests never become zero prices.

## Collection and exclusions

`acquire.R` documents collection for approved sources; it is intentionally not run during rendering. Before collecting, review current terms and robots instructions, then pass explicit museum IDs. An access failure is a failure, never a zero-price observation. The acquisition log records actual request outcomes, and `screening.csv` records later content/terms exclusions. The public raw manifest includes only analyzed institutions.

The pilot used a two-second delay before new content requests; subsequent review found the Frick's robots file requests ten seconds. The refresh script uses at least ten seconds and honors longer reported delays. This retrospective correction is recorded rather than claiming perfect compliance in the initial run. No authentication, CAPTCHA solving, rate-limit evasion, personal data collection, or bypass was used. Cached pages were reused. Terms reviews informed exclusions but are not a comprehensive legal assessment of every museum.

Barnes terms prohibit systematic database extraction, so its pilot data were excluded. The Broad was excluded following terms review. Met/MoMA/NGA/Morgan requests failed; de Young and Menil had robot exclusions; MFAH's robots request was forbidden; Guggenheim returned a challenge; Asian Art Museum's URL returned 404. MFA Boston and LACMA lacked usable paired admission categories on the fetched pages. These exclusions can bias comparisons.

## Definitions

- Unit: institution, one regular general-admission visit; no repeated prices, buildings, or categories treated as extra observations.
- Baseline: age 30, nonresident, full-time college student with ID versus nonstudent of the same age. Not a claim about the author's age. No Penn/other school partnership or residency benefits assumed.
- Age 22 sensitivity: Whitney is free for both groups. Other observed youth limits do not change these rows.
- Dollars are USD, posted rates, excluding fees, travel, parking and separate special exhibitions. MCA Chicago prices are posted online rates; in-person pay-what-you-can remains an explicit alternative, never coded as mandatory zero or mandatory full price.
- City mean includes always-free institutions. Paid-only sensitivity excludes adult-price-zero rows. Region means give equal weight to cities, using Census regions (Washington DC is South); not population estimates. Boston includes Cambridge.
- Raw dollar saving is adult minus student. Discount percentages are deliberately not used for free/free pairs.
- Hours and reservation notes are manually reviewed annotations. Some refer to official pages instead of pretending all schedules were fully extracted. Recheck before travel.

## Source attribution

Every row links its museum's official visit page. Museum names identify sources and imply no endorsement. Gardner source: Isabella Stewart Gardner Museum, Boston, https://www.gardnermuseum.org/visit/admissions. Full code and data: https://github.com/lizzyuan77/lizzyuan-s-website/tree/main/blog/posts/post2 . Article drafting and code used AI assistance.
