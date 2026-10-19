# Blog 5 rubric review

Reviewed October 19, 2026 against the supplied `Blog_Posts.pdf` and `blog_post_rubric.pdf` for Computational Methods for Economists. This maps the work to the requirements; it is a self-review, not an instructor-assigned grade.

## Ten grading criteria

| # | Requirement | Evidence in this submission | Review |
| --- | --- | --- | --- |
| 1 | Question and motivation | The introduction asks whether technology employment and prosperity accompany gender earnings equality, using Goldin's research to motivate the question. | Covered |
| 2 | Clear explanation | Successive sections explain the earnings ratio, income comparison, technology representation, within-occupation earnings and time comparison in general-audience language. Population definitions are stated. | Covered; length is the main readability trade-off |
| 3 | Interpretation and takeaway | The final substantive section distinguishes access to high-paying occupations from career progression and flexibility. Correlations are explicitly descriptive. | Covered |
| 4 | Data sources and presentation | ACS table IDs, years, source links, the 2020 omission, units, populations and insets are documented. Figures have titles, legends/captions and alternative text. | Covered |
| 5 | Organized repository and replication README | Code, data and results are separated. README provides setup, execution order, expected outputs and troubleshooting; METHODOLOGY contains detailed definitions. | Covered after documentation revision |
| 6 | Reproducibility and coding practices | Scripts read included inputs, validate joins/counts, calculate results and save CSV/PNG files. Article numbers are evaluated from saved results. The replication ZIP includes required source materials. | Covered; see verification below |
| 7 | Appropriate GIS/spatial data | Census cartographic boundaries are matched to ACS estimates by state FIPS. Coordinate transformations are explicit in `code/maps.py`. | Covered |
| 8 | At least one substantive central map | `map-earnings.png` and `map-representation.png` are embedded as central evidence in the article. | Covered: two central maps |
| 9 | Map communicates geographic pattern | State labels, separate quantitative legends, contrasting palettes, AK/HI insets and documented coverage make the measures interpretable. An exact 50-state spatial join is asserted. | Covered |
| 10 | Interprets spatial patterns | Washington/Maryland comparisons distinguish technology concentration from representation and earnings; the maps connect to all-state correlations and 2019–2024 changes. The text explains why tech concentration alone is insufficient. | Covered |

## General requirements and scope

- **Submission:** both the published article and repository links appear in the article and READMEs. Submit both URLs; the ZIP alone is not the repository link.
- **Length:** approximately 2,100 words excluding figure captions but including headings and source notes. This exceeds the suggested 400–800 words. The assignment explicitly says there is no strict word limit. The expanded article is retained; brevity remains a presentation trade-off.
- **GIS emphasis:** this is Blog 5. IPUMS CPS microdata, CPS sampling weights and a minimum of three substantive visualizations belong to Blog 3, not Blog 5. ACS tabulations already incorporate survey weights; correlations give states equal weight.
- **Interpretation:** the analysis does not estimate discrimination, a technology treatment effect, or causal childcare/flexibility policy effects. Goldin's research supplies possible mechanisms, not causal findings from these maps.
- **Comparability:** ratios, shares and counts are compared over time, not nominal dollar growth. The 2024 dollar comparison uses one year's dollars. The different B20017/B24022 populations and missing standard 2020 release are explained.
- **Timing:** late penalties or extensions depend on the course deadline and cannot be assessed from the supplied materials.

## Documentation improvements

The root README now points to the live article and replication materials. The Blog 5 README begins with software setup and the working directory, then gives the pipeline in order. It separates optional downloads from offline replication, explains outputs and includes troubleshooting. Detailed formulas and research notes moved to METHODOLOGY.md. The package builder now uses an explicit allowlist so render artifacts and virtual environments do not enter the ZIP.

## Fresh-copy verification procedure

Extract the ZIP into a separate folder, remove the included `results/`, and run all three R scripts and the Python mapping script with the documented dependencies. Compare regenerated analytical CSVs with the published results, check the figures/spatial join, and render the standalone Quarto article. This tests independence from the developer checkout's precomputed results and files on another computer.

**Verification result (October 19, 2026): passed.** After removing all precomputed results in a freshly extracted copy, all three R scripts and the Python mapper completed. All nine analytical CSV files matched the published results byte-for-byte; all seven article figures regenerated. The package builder excluded render artifacts and environments. Quarto successfully rendered the standalone article, and its local resource/download links resolved after building the replication ZIP. The test used the documented installed dependencies and required no source-data downloads.
