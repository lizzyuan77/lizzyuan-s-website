# Blog 2: What Is Your Student ID Worth?

Snapshot: September 21, 2026 America/New_York (acquisition log uses UTC, September 22). Eighteen institutions in eight cities, selected from 30 candidates. The two SAAM URLs are one institution. Barnes was a separate preliminary pilot exclusion.

## Reproduce without network access

Install R with rvest, xml2 and ggplot2. From this folder, run:

```
Rscript analyze.R
```

This re-extracts prices from `data/evidence/*.html`, recomputes museum/city/region CSVs and regenerates both charts. `rules.csv` contains reviewed label patterns, not assigned ticket prices. The code fails if a required label disappears. `results/session-info.txt` records the environment used. A Quarto render additionally needs knitr and rmarkdown. From the website root: `quarto render blog/posts/post2/index.qmd --no-clean`.

The evidence files are exact short matched price text in a NEW minimal HTML wrapper, not full preserved DOM pages. This supports offline checking of extraction and arithmetic, not independent reconstruction of all original layout context. Original downloaded pages are retained privately and hashed in `results/raw-manifest.csv`; no museum artwork or complete website is republished. To parse original cached HTML instead, run `Rscript analyze.R --raw PATH_TO_RAW_FOLDER`. Both modes use the same reviewed patterns. An independent fresh scrape can change results and requires a new review.

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
