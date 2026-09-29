# Required IPUMS CPS extract

The assignment explicitly requires IPUMS CPS microdata. Extract 1 was submitted on 2026-09-28 and IPUMS reports Completed (38.7 MB compressed). The matching data and DDI were downloaded and analyzed.

1. Sign in at https://cps.ipums.org/cps/ using your own account. Do not send passwords or API keys in chat.
2. Select **Basic Monthly** samples: January–December **2019** and January–December **2024** (24 samples). Do not select ASEC.
3. Select YEAR, MONTH, SERIAL, PERNUM, AGE, LABFORCE, WTFINL. Keep all person records; no custom subpopulation filter is needed.
4. Choose the normal rectangular data format, download the microdata `.dat.gz` and its matching **DDI XML**. Keep them together with original filenames.
5. Run analysis.R with the DDI path as described in README.md. Keep default ASECFLAG to verify that no ASEC records entered the extract.

Official references:
- Access: https://cps.ipums.org/cps/data.shtml
- Person weights: https://cps.ipums.org/cps-action/variables/WTFINL
- Labor-force coding: https://cps.ipums.org/cps-action/variables/LABFORCE

2019 provides a pre-pandemic baseline. 2024 provides a complete recent calendar year; October 2025 was not collected, so 2025 is deliberately not used for this full-year design.


