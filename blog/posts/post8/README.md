# Blog 8 — What Can a Campus Poll Really Tell Us?

A beginner-friendly tutorial about bootstrap confidence intervals and hypothesis tests. Four interactive experiments appear directly in the article. All poll responses are simulated; the Penn Fund and Penn First Plus provide background, not survey data.

## Start here

- **Read/edit the article:** `index.qmd`.
- **Reproduce the analysis:** run `code/simulate.py` first, then render the article with Quarto. Exact steps are below.
- **Inspect results:** `results/summary.csv` contains the main numerical findings.
- **Download everything for this post:** `research.zip` contains the article, code, documentation, simulated data, and interactive assets. It does not include the whole website theme.

## Where the files are

| File or folder | Purpose |
| --- | --- |
| `index.qmd`, `post.css` | Article source and post styling |
| `code/simulate.py` | Draws samples, runs the simulations, validates results, and rebuilds the HTML demos and download bundle |
| `code/chart_template.html` | Shared demo layout, chart code, instructions, and controls |
| `code/requirements.txt` | Pinned NumPy dependency |
| `results/bootstrap.html` | Experiment 1: construct a bootstrap interval |
| `results/coverage.html` | Experiment 2: check interval coverage |
| `results/hypothesis-test.html` | Experiment 3: simulate a test under a tie |
| `results/sampling.html` | Extra: compare new polls and sample sizes |
| `results/chart.html` | Compatible entry point for older links; opens experiment 1 |
| `results/simulation-data.js` | Shared data loaded by all demos |
| `results/simulation.json` | Full simulation results, intervals, bootstrap percentages, and validation quantities |
| `results/poll_n*.csv` | Original yes/no sample responses for each sample size |
| `results/coverage_n*.csv` | All 2,000 coverage intervals per sample size |
| `results/summary.csv` | Coverage, simulated/exact p-values, and false-rejection rates |
| `results/text_values.json` | Numbers imported into the article automatically |
| `results/environment.json` | Python/NumPy versions, seed, and simulation counts |
| `vendor/plotly-basic-3.1.0.min.js` | Bundled chart library; no external library requests |

Edit the source files, then regenerate outputs. Do not edit generated HTML or result files by hand.

## Reproduce in order

### 1. Run the simulation

Install Python 3.12. From the repository root:

```sh
cd blog/posts/post8
python3 -m venv .venv
.venv/bin/python -m pip install -r code/requirements.txt
.venv/bin/python code/simulate.py
```

On Windows, use `.venv\Scripts\python` instead of `.venv/bin/python`. If you extracted `research.zip`, start in its extracted folder and omit the `cd` command.

No data downloads, login, API key, or R packages are required. This step rebuilds `results/` and `research.zip`. The virtual environment is excluded from version control and the bundle.

### 2. Render the blog

Install [Quarto](https://quarto.org/docs/get-started/), return to the website repository root, and run:

```sh
quarto render blog/posts/post8/index.qmd
```

The published output goes to `docs/blog/posts/post8/`. Rendering uses the saved results; it does not rerun the simulations. The article lists its required HTML, JavaScript, and download files in its `resources` section so Quarto copies them into the published folder.

For a local website preview, run `quarto preview` from the repository root. With only the extracted bundle, open `results/bootstrap.html` to try the standalone demos; full website rendering also requires the repository's `_quarto.yml` and theme assets.

## How the simulations work

- **Randomness:** seed `20261028`, with a separate stream for each sample size: 100, 200, 500, and 1,000. Original answers are independent yes/no draws with 55% probability of yes. Changing sample size loads a different independently drawn poll.
- **Bootstrap:** draw sample-size-many response cards with replacement, 4,000 times. The 95% percentile interval uses the 2.5th and 97.5th percentiles with linear interpolation. The browser also offers 90% and 99% intervals. Endpoints appear after 100 resamples, a display threshold rather than a precision guarantee.
- **Coverage:** draw 2,000 new polls from the 55% population. Bootstrap each poll 4,000 times and check whether its interval includes 55%. For binary answers, a bootstrap yes count follows `Binomial(n, observed_yes/n)`; the inner loop uses that equivalent resampling law for efficiency. It does not substitute the true 55%. The three confidence levels use the same underlying draws. Initially, ten intervals appear; the running fraction uses only intervals shown.
- **Hypothesis test:** simulate 100,000 polls with true support set to 50%. The statistic is distance from 50%; the chart reports it in percentage points. The two-sided p-value counts results at least as far away as the observed poll, including equality. Both directions become one right-hand tail in the distance chart.
- **Rejection rule:** exact binomial probabilities define a symmetric cutoff with false-rejection probability at most 5%. Orange bars show the observed p-value tail; shading shows the prechosen rejection region. These boundaries need not coincide. Exact p-values also validate the simulated ones.

The buttons replay consecutive saved simulation results, not newly collected responses. Each experiment has independent controls. Reset returns that experiment to sample size 500 and confidence 95%. Embedded mode hides duplicate headings/navigation; standalone versions retain Previous/Next links.

Coverage is approximate, not a guarantee for every population or sample size. More simulations improve numerical stability; they cannot fix biased sampling. The generator checks probability totals, simulated-versus-exact p-values, interval consistency, and coverage. Simulation standard errors are saved in `simulation.json`. The bootstrap interval and exact-calibrated test are different procedures and need not be exact inverses.

## Sources and interpretation

- [The Penn Fund](https://giving.upenn.edu/the-penn-fund/) and [Penn First Plus](https://pennfirstplus.upenn.edu/), consulted October 28, 2026: context for the fictional undergraduate poll. First-generation and lower-income identities are not interchangeable.
- [ASA statement on p-values (2016)](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf): a p-value is not the probability that a hypothesis is true.
- Course supplementary material, *Simulation and Resampling: Monte Carlo, Bootstrap, and Jackknife* (STAT 5200, Fall 2026): conceptual background.

The post does not report actual Penn votes or verify an official ballot with these options. It groups every other funding priority into “no.” It assumes fair, independent sampling and does not estimate whether a funding choice improves student outcomes.
