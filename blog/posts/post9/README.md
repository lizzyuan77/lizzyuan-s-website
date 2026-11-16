# Blog 9 — How Boosting Learns to Predict Stock Returns

A course-based demonstration of sequential boosting, followed by a comparison of the class stock model, a revised model, and simple benchmarks. Model choices use 2023 only; the final evaluation uses 2024–2025. This is a retrospective classroom experiment, not a live investment system.

## File guide and run order

| File | Purpose |
|---|---|
| `index.qmd`, `post.css` | Article and styling |
| `includes/boosting-demo.qmd` | Interactive, illustrative boosting lesson embedded in the opening section |
| `code/class_reference.R` | Unmodified supplied class script, `UPenn_XGBoostStockPrediction copy.R` |
| `code/design.json` | Dates, candidate settings, target, portfolio rules, and costs specified before evaluation |
| `code/download.py` | Optional download from Yahoo Finance; existing cached files are reused |
| `code/run.py` | **Run first for an offline rebuild:** analysis followed by figures and bundle |
| `code/analyze.py` | Features, time splits, validation search, frozen test predictions, portfolios and metrics |
| `code/present.py` | Generates the article figures, table/numbers, and `research.zip` |
| `code/validate.py` | Independent checks on split boundaries, saved predictions and portfolio accounting |
| `code/requirements.txt` | Pinned Python packages |
| `data/*.csv` | Included daily Yahoo price snapshot: 95 class stocks and SPY |
| `data/group_history_indexed.csv`, `group_source.json` | User-provided group portfolio, normalized to start at 100, and provenance |
| `code/import_group.py` | Optional importer for the original HTML-as-XLS group export; not needed to rebuild from included normalized data |
| `results/group_summary.json` | Group account-value change and observed drawdown, kept separate from model metrics |
| `data/manifest.json` | Requested tickers, download time, failures, and SHA-256 hashes |
| `results/validation_search.json` | All eight validation scores and their settings |
| `results/class_model.json`, `revised_model.json` | Saved fitted XGBoost models |
| `results/test_predictions.csv` | Every held-out forecast, realized outcome and outcome end date |
| `results/prediction_metrics.csv` | RMSE, MAE, R² against the training-mean benchmark, and daily rank correlation |
| `results/holdings.csv`, `portfolio_returns.csv` | Stock weights, common execution dates, realized returns and trading costs |
| `results/investment_metrics.csv` | Performance at 0, 10 and 25 basis points per dollar traded |
| `results/summary.json`, `environment.json` | Methodology, split audit, selected settings, results and package versions |
| `results/boosting-steps.png`, `wealth.png` | Article figures: sequential learning/overfitting and investment comparison |
| `results/boosting_learning_curve.csv` | Class-settings model fit on 2022, scored at successive tree counts on 2022 training and 2023 validation data |
| `results/text_values.json`, `investment_table.qmd` | Generated article values and table |
| `research.zip` | Self-contained post source, code, results and price snapshot; the website theme is separate |

## Reproduce from the included snapshot

Install Python 3.12. From this post folder:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r code/requirements.txt
.venv/bin/python code/run.py
.venv/bin/python code/validate.py
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python`. `run.py` confines the macOS OpenMP library search to its child processes, using the library bundled with the pinned scikit-learn wheel. No system installation is needed in the tested environment. Linux/Windows run the analysis normally.

These steps need no market-data login, key, R installation, or new download. `analyze.py` verifies the included price-file hashes. `run.py` rebuilds figures, tables and the downloadable bundle. The random seed is 123. Models run on CPU with two threads; tiny numerical differences can occur across hardware/library builds.

To acquire prices yourself, run `python code/download.py` in an environment with the requirements installed. Existing CSVs are reused. The downloader requires every stock and SPY and records failures; it does not silently choose a smaller universe. A new vendor snapshot can differ because dividend/split adjustments are revised. Use the included snapshot to reproduce the reported results.

From the **website root**, install Quarto and run:

```sh
quarto render blog/posts/post9/index.qmd
quarto preview
```

The rendered article belongs in `docs/blog/posts/post9/`. The full website's `_quarto.yml`, shared styles and assets are needed for the theme. An extracted bundle includes everything for analysis, figures and tables. Rendering uses saved results and does not refit models. Edit `.qmd`/Python sources, then rebuild; do not edit result numbers manually.

## Course foundation

The article follows `Class21_Decision_Trees_Random_Forests_Gradient_Boosting.qmd`, especially sections 37–44: start from the training mean, compute residuals, fit the next tree, and add its learning-rate-scaled correction. For squared-error loss, residuals are negative loss gradients. Sections 43–44 explain learning rate/tree-count tradeoffs and shallow trees. The supplied stock-prediction R script provides the applied experiment.

The learning-curve figure fits the supplied class settings on the purged 2022 fit sample and checks successive tree counts against 2023 validation data. No 2024–2025 labels are used in that figure. Its purpose is to demonstrate overfitting, not to expand or retune the eight-candidate search after viewing test performance. The candidate grid is intentionally limited and does not establish an optimal model. The main numerical results remain unchanged. Group performance appears only in one closing sentence.

## What is preserved from class?

The class file contains 95 stocks, despite its comment describing 100. We use all 95 and SPY, with daily prices from 2022-01-01 through 2026-01-30 (`end=2026-02-01`, exclusive). The class model keeps its 14 numeric predictors, including OHLC prices, volume, adjusted price, daily/market returns, inverse momentum ratios, 22-observation lagged volatility, reversal and excess return. Date and symbol are identifiers, not predictors.

It uses 300 trees, depth 5, learning rate .05, and child weight 10 (the regression counterpart of the R `min_n` setting). The Python XGBoost implementation is a documented port of the supplied settings, not bit-for-bit output from its R/tidymodels version. We do not claim to reproduce a particular classroom performance number: no saved classroom output was provided.

Both models predict the original target `adjusted[t+20] / adjusted[t+1] - 1`. This contains **19 close-to-close return intervals**, not 20. Forecast accuracy uses that same target for both models and the historical-average benchmark. Model forecasts are evaluated on 47,690 stock-day rows, but overlapping targets are correlated; this is not 47,690 independent investment trials.

## What changes in the revision?

The revision replaces nominal price levels with eight relative signals: correctly oriented 5/21/63/126-session price trends, lagged 21-day volatility, market-relative 21-session trend, relative volume, and signal-day market-relative return. Each is converted to a same-day cross-sectional percentile rank. Ranking uses only contemporaneously observable stocks, not future dates.

Eight configurations combine depth 2/3, 200/500 trees and L2 penalty 10/30. Learning rate .03, child weight 20 and L1 penalty 1 are fixed. Validation RMSE selects depth 2, 200 trees and L2 30. This is one combined feature/regularization change, not an experiment identifying the contribution of each component separately.

The first fit uses signal dates 2022-07-06–2022-12-01; validation signals run 2023-01-03–2023-11-30. Settings are selected with validation labels only. Both models are refitted on 2022–2023 data with target end dates strictly before 2024-01-01. Final test signal dates are 2024-01-02–2025-12-31, with labels extending through 2026-01-30. The original model does not receive a test-period tuning search. Neither model is updated during testing.

Every split is purged by **outcome end date**, rather than splitting on signal date alone. This prevents a late training signal from using a future test-period return. Initial rolling-feature rows and unavailable future targets are dropped in common, so the models are scored on the same observations.

## Portfolio accounting and benchmarks

The supplied script weights stocks by positive predictions, compounds short forward targets on a monthly schedule, uses different benchmark windows, and annualizes monthly observations with daily factors. Our comparison does **not** reproduce that backtest as if it were valid. It applies the following common corrected protocol to both models:

- Signal at the first trading-day close of each month; execute at the next trading-day close.
- Hold the top ten stocks **equally weighted**, regardless of prediction sign, until the next monthly execution. No leverage or short sales. This common allocation deliberately differs from the class script's prediction-proportional weights.
- Use actual entry-to-exit adjusted-price returns, not forecast labels, for both portfolios and benchmarks. Monthly holding lengths vary, while the class prediction target remains fixed; they are distinct evaluation tasks.
- Compare with monthly equal-weight holdings of the same stock universe and buy-and-hold SPY. The forecast-only benchmark predicts the training-set mean return for every stock; it does not produce a meaningful stock ranking.
- Rebalancing turnover accounts for weight drift. Charge the stated fee for every dollar bought or sold, including initial purchase and final liquidation. Test costs of 0%, .10% and .25% per dollar traded. These are illustrative assumptions, not estimated historical execution costs.
- There are 24 common monthly holdings, January 3, 2024–January 5, 2026. CAGR uses elapsed calendar time. Annualized volatility uses monthly sample standard deviation times √12. The supplementary Sharpe uses a **zero risk-free rate** and √12; it is not a risk-free-adjusted alpha claim. Drawdown is based on monthly marks and can miss larger within-month losses.

## Limits and sources

The class list is fixed and selected retrospectively. Survivor/selection bias and retrospectively adjusted prices mean this is not a point-in-time investable-market study. A two-year test cannot establish durable forecasting skill, a causal mechanism, or statistically significant excess performance. More ending wealth at higher volatility is not proof of alpha. No current portfolio recommendation is provided.

- Class source: supplied `UPenn_XGBoostStockPrediction copy.R`; retained unchanged for inspection.
- Prices: Yahoo Finance via [yfinance download](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html), `auto_adjust=False`; return calculations use `Adj Close` (split/dividend-adjusted). Download date and checksums are in the manifest.
- [Gu, Kelly and Xiu (2020), *Empirical Asset Pricing via Machine Learning*](https://doi.org/10.1093/rfs/hhaa009): research context, not a claim that this small experiment replicates their findings.
- [XGBoost parameter reference](https://xgboost.readthedocs.io/en/stable/parameter.html): depth, learning rate and regularization.

## Group portfolio context

The user supplied `performance-history-2026-11-10.xls`, which is an HTML table despite its extension. Its 54 observations run from 2026-08-27 to 2026-11-10. The user confirmed this was a separate group portfolio, not XGBoost picks, with no changes during the period. The article interprets the account-value change under the assumption of no external deposits/withdrawals. The normalized series reproduces the percentage change and observed peak-to-trough drawdown without needing original account balances.

The source has Saturday date labels; these are retained rather than silently shifted to another day or year. No SPY benchmark or annualization is inferred for this short history. The group series is motivational context, not model training, validation, test data, or proof about XGBoost. It is not plotted on the backtest's different date window. `import_group.py path/to/export.xls` can recreate the normalized input from the original file.

The article’s 1% → 1.1% boosting example is illustrative, not a saved stock forecast. It assumes a new tree recommends a 2-percentage-point correction, multiplied by the class learning rate of .05. Actual trees learn corrections across groups of training observations.

The opening teaching diagram (`results/boosting-update.png`) is generated by `code/illustrate_boosting.py`, called by `present.py`. Its numbers are illustrative, separate from the fitted stock forecasts.

The article embeds `includes/boosting-demo.qmd`: a browser-only, six-observation teaching example. Each click fits the least-squares one-split tree to current residuals and adds the selected learning-rate fraction. Changing the rate resets the example. It is separate from the stock analysis, uses no external libraries, and is included in the replication ZIP. The visual teaching approach was informed by 3Blue1Brown’s gradient-descent lesson; no video graphics were copied.
