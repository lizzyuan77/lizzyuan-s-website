"""
04_estimate.py  -  Weighted intergenerational elasticities (IGE).

  log(child income) = a + b * log(parent income) + e,   weights = 2015 longitudinal weight

Standard errors are clustered by mother, because siblings share a mother
and her family income. Differences between estimates (daughters vs sons,
averaged vs single-year, mature vs early) use a cluster bootstrap that
redraws whole mothers, so both estimates are always computed on the same
resampled people.

Outputs (results/):
  ige_results.csv      main sample: single-year vs 3-year averages, by sex
  ige_lifecycle.csv    life-cycle sample: child earnings at ~age 30 vs ~age 40
  ige_differences.csv  bootstrap differences between specifications
  sample_stats.csv     weighted descriptive statistics
  session-info.txt     software versions

Run from the post6 folder:  python code/04_estimate.py
"""
from pathlib import Path
import os
import platform
import sqlite3
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("PSID_DIR", ROOT / "data"))
RESULTS = ROOT / "results"
rng = np.random.default_rng(20261023)
N_BOOT = int(os.environ.get("N_BOOT", 2000))

con = sqlite3.connect(DATA / "working" / "blog6.sqlite")
d = pd.read_sql_query("SELECT * FROM analysis", con)
ages = pd.read_sql_query("""
    SELECT e.id68, e.pn, e.income_year, e.age - 1 AS age FROM earnings e
    JOIN analysis a ON a.child_id68 = e.id68 AND a.child_pn = e.pn
    WHERE e.income_year IN (2002, 2012)""", con)
con.close()
d["mother"] = d["parent_id68"].astype(str) + "-" + d["parent_pn"].astype(str)


# ---------------------------------------------------------------------------
# Weighted least squares with mother-clustered (CR1) standard errors
# ---------------------------------------------------------------------------
def wls(y, X, w):
    Xw = X * w[:, None]
    bread = np.linalg.inv(X.T @ Xw)
    beta = bread @ (Xw.T @ y)
    return beta, bread


def fit_ige(df, child_col, parent_col):
    y = np.log(df[child_col].to_numpy())
    X = np.column_stack([np.ones(len(df)), np.log(df[parent_col].to_numpy())])
    w = df["weight"].to_numpy()
    beta, bread = wls(y, X, w)
    resid = y - X @ beta
    score = X * (w * resid)[:, None]
    groups = pd.factorize(df["mother"])[0]
    G = groups.max() + 1
    meat_parts = np.zeros((G, X.shape[1]))
    np.add.at(meat_parts, groups, score)
    n, k = X.shape
    adj = G / (G - 1) * (n - 1) / (n - k)
    V = adj * bread @ (meat_parts.T @ meat_parts) @ bread
    se = np.sqrt(V[1, 1])
    return {"ige": beta[1], "se": se,
            "ci_low": beta[1] - 1.96 * se, "ci_high": beta[1] + 1.96 * se,
            "n": n, "mothers": G,
            "effective_n": w.sum() ** 2 / (w ** 2).sum()}


def wslope(y, x, w):
    """Weighted OLS slope of y on x with an intercept (same as wls()[0][1])."""
    xm = (w * x).sum() / w.sum()
    ym = (w * y).sum() / w.sum()
    return (w * (x - xm) * (y - ym)).sum() / (w * (x - xm) ** 2).sum()


def cluster_boot(df, stat):
    """Redraw mothers with replacement; return the bootstrap draws of stat.
    stat receives a dict of NumPy arrays (log incomes, weight, daughter flag)."""
    df = df.reset_index(drop=True)
    arr = {c: np.log(df[c].to_numpy()) for c in
           ["parent_single", "parent_mean", "child_single", "child_mean",
            "early_single", "early_mean"] if df[c].notna().all()}
    arr["w"] = df["weight"].to_numpy()
    arr["daughter"] = (df["sex"] == "daughter").to_numpy()
    rows_of = list(df.groupby("mother").indices.values())   # row positions per mother
    est = stat(arr)
    draws = np.empty(N_BOOT)
    for b in range(N_BOOT):
        pick = rng.integers(0, len(rows_of), size=len(rows_of))
        idx = np.concatenate([rows_of[i] for i in pick])
        draws[b] = stat({k: v[idx] for k, v in arr.items()})
    return est, draws


GROUPS = {"daughters": "daughter", "sons": "son", "all children": None}


def subset(df, label):
    s = GROUPS[label]
    return df if s is None else df[df["sex"] == s]


# ---------------------------------------------------------------------------
# 1. Main sample: single year vs three-year averages
# ---------------------------------------------------------------------------
main = d[d["main_sample"] == 1].copy()
SPECS = [  # (label, child measure, parent measure)
    ("Single year", "child_single", "parent_single"),
    ("Parent averaged only", "child_single", "parent_mean"),
    ("Child averaged only", "child_mean", "parent_single"),
    ("Three-year averages", "child_mean", "parent_mean"),
]
rows = []
for g in GROUPS:
    for spec, c, p in SPECS:
        rows.append({"group": g, "spec": spec, "child_measure": c,
                     "parent_measure": p, **fit_ige(subset(main, g), c, p)})
res = pd.DataFrame(rows)
res.to_csv(RESULTS / "ige_results.csv", index=False)
print(res[["group", "spec", "ige", "se", "n"]].round(3))

# ---------------------------------------------------------------------------
# 2. Life-cycle sample: same children, child earnings at two ages
#    Parent measure held fixed (three-year average).
# ---------------------------------------------------------------------------
life = d[d["lifecycle_sample"] == 1].copy()
LIFE_SPECS = [
    ("Age ~30, single year (2002)", "early_single"),
    ("Age ~30, averaged (2000-04)", "early_mean"),
    ("Age ~40, single year (2012)", "child_single"),
    ("Age ~40, averaged (2010-14)", "child_mean"),
]
rows = []
for g in GROUPS:
    for spec, c in LIFE_SPECS:
        rows.append({"group": g, "spec": spec, "child_measure": c,
                     **fit_ige(subset(life, g), c, "parent_mean")})
life_res = pd.DataFrame(rows)
life_res.to_csv(RESULTS / "ige_lifecycle.csv", index=False)
print(life_res[["group", "spec", "ige", "se", "n"]].round(3))

# Year by year: one IGE per child income year, on a FIXED group of children
# (life-cycle sample members with positive earnings in all six years).
con = sqlite3.connect(DATA / "working" / "blog6.sqlite")
yearly = pd.read_sql_query("""
    SELECT e.id68 AS child_id68, e.pn AS child_pn, e.income_year,
           e.age, e.real_earnings
    FROM earnings AS e
    JOIN analysis AS a ON a.child_id68 = e.id68 AND a.child_pn = e.pn
    WHERE a.lifecycle_sample = 1
      AND e.income_year IN (2000, 2002, 2004, 2010, 2012, 2014)""", con)
con.close()
always_positive = (yearly.groupby(["child_id68", "child_pn"])["real_earnings"]
                   .agg(lambda s: (s > 0).sum() == 6 and len(s) == 6))
keep = always_positive[always_positive].reset_index()[["child_id68", "child_pn"]]
yearly = yearly.merge(keep).merge(
    life[["child_id68", "child_pn", "sex", "weight", "mother", "parent_mean"]])
rows = []
for g in GROUPS:
    for yr, s in subset(yearly, g).groupby("income_year"):
        rows.append({"group": g, "income_year": yr,
                     "mean_age": np.average(s["age"] - 1, weights=s["weight"]),
                     **fit_ige(s, "real_earnings", "parent_mean")})
by_year = pd.DataFrame(rows)
by_year.to_csv(RESULTS / "ige_by_year.csv", index=False)
print(by_year[["group", "income_year", "mean_age", "ige", "se", "n"]].round(3))

# ---------------------------------------------------------------------------
# 2b. What one bad year does: treat PSID's $1 bottom code as if it were a
#     real $1 income (the mistake 01_import.py avoids). Same people as the
#     main sample, plus the children whose 1981 parental value is that code.
# ---------------------------------------------------------------------------
cpi_1981_to_2020 = 258.811 / 90.9
naive = d[(d["weight"] > 0) & (d["parent_mean"] > 0)
          & (d["child_single"] > 0) & (d["child_mean"] > 0)].copy()
naive["parent_single"] = naive["parent_single"].where(naive["parent_single"] > 0,
                                                      1 * cpi_1981_to_2020)
rows = []
for g in GROUPS:
    for label, df in [("$1 code treated as income", naive),
                      ("$1 code treated as no income (main)", main)]:
        for spec, c, p in [SPECS[0], SPECS[3]]:
            rows.append({"group": g, "treatment": label, "spec": spec,
                         **fit_ige(subset(df, g), c, p)})
sens = pd.DataFrame(rows)
sens.to_csv(RESULTS / "ige_bottomcode_sensitivity.csv", index=False)
print(sens[["group", "treatment", "spec", "ige", "n"]].round(3))

# How noisy is one year? Correlation of log income across years, same people.
con = sqlite3.connect(DATA / "working" / "blog6.sqlite")
ph = pd.read_sql_query("""
    SELECT h.child_id68, h.child_pn, h.income_year, h.real_income AS v
    FROM parent_history h JOIN analysis a USING (child_id68, child_pn)
    WHERE a.main_sample = 1""", con)
ce = pd.read_sql_query("""
    SELECT e.id68 AS child_id68, e.pn AS child_pn, e.income_year, e.real_earnings AS v
    FROM earnings e JOIN analysis a ON a.child_id68 = e.id68 AND a.child_pn = e.pn
    WHERE a.main_sample = 1 AND e.income_year IN (2010, 2012, 2014)""", con)
con.close()
rows = []
for who, df, y0, y1 in [("parents", ph, 1980, 1982), ("parents", ph, 1980, 1981),
                        ("children", ce, 2010, 2014), ("children", ce, 2010, 2012)]:
    w = df.pivot_table(index=["child_id68", "child_pn"], columns="income_year", values="v")
    w = w[(w[y0] > 0) & (w[y1] > 0)]
    rows.append({"generation": who, "year_a": y0, "year_b": y1, "n": len(w),
                 "corr_log_income": np.corrcoef(np.log(w[y0]), np.log(w[y1]))[0, 1]})
pd.DataFrame(rows).to_csv(RESULTS / "year_to_year_correlation.csv", index=False)
print(pd.DataFrame(rows).round(3))

# ---------------------------------------------------------------------------
# 3. Bootstrap differences
# ---------------------------------------------------------------------------
def by_sex_gap(c, p):
    def stat(a):
        d_, s_ = a["daughter"], ~a["daughter"]
        return (wslope(a[c][d_], a[p][d_], a["w"][d_])
                - wslope(a[c][s_], a[p][s_], a["w"][s_]))
    return stat


def within(c1, p1, c0, p0):
    return lambda a: wslope(a[c1], a[p1], a["w"]) - wslope(a[c0], a[p0], a["w"])


diff_specs = []
for g in GROUPS:
    diff_specs.append((g, "Averages minus single year", main,
                       within("child_mean", "parent_mean", "child_single", "parent_single")))
    diff_specs.append((g, "Age ~40 minus age ~30 (averaged)", life,
                       within("child_mean", "parent_mean", "early_mean", "parent_mean")))
diff_specs.append(("daughters minus sons", "Single year", main,
                   by_sex_gap("child_single", "parent_single")))
diff_specs.append(("daughters minus sons", "Three-year averages", main,
                   by_sex_gap("child_mean", "parent_mean")))

rows = []
for g, label, sample, stat in diff_specs:
    df = sample if g == "daughters minus sons" else subset(sample, g)
    est, draws = cluster_boot(df, stat)
    rows.append({"group": g, "comparison": label, "difference": est,
                 "boot_se": draws.std(ddof=1),
                 "ci_low": np.quantile(draws, 0.025), "ci_high": np.quantile(draws, 0.975),
                 "share_draws_positive": (draws > 0).mean(), "n": len(df)})
diffs = pd.DataFrame(rows)
diffs.to_csv(RESULTS / "ige_differences.csv", index=False)
print(diffs.round(3))

# ---------------------------------------------------------------------------
# 4. Weighted descriptive statistics for the main sample
# ---------------------------------------------------------------------------
def wmean(x, w):
    x, w = np.asarray(x, float), np.asarray(w, float)
    ok = ~np.isnan(x)
    return float(np.sum(x[ok] * w[ok]) / np.sum(w[ok]))


age_wide = ages.pivot_table(index=["id68", "pn"], columns="income_year", values="age").reset_index()
age_wide.columns = ["child_id68", "child_pn", "age_2002", "age_2012"]
m2 = main.merge(age_wide, on=["child_id68", "child_pn"], how="left")
rows = []
for g in GROUPS:
    s = subset(m2, g)
    w = s["weight"].to_numpy()
    rows.append({
        "group": g, "n": len(s),
        "mean_parent_income_1981": wmean(s.parent_single, w),
        "mean_parent_income_avg": wmean(s.parent_mean, w),
        "mean_child_earnings_2012": wmean(s.child_single, w),
        "mean_child_earnings_avg": wmean(s.child_mean, w),
        "median_parent_income_avg": float(s.parent_mean.median()),
        "median_child_earnings_avg": float(s.child_mean.median()),
        "mean_age_2012": wmean(s.age_2012, w),
        "mean_age_2002": wmean(s.age_2002, w),   # among those observed in 2003
        "sd_log_parent_single": float(np.log(s.parent_single).std()),
        "sd_log_parent_mean": float(np.log(s.parent_mean).std()),
        "sd_log_child_single": float(np.log(s.child_single).std()),
        "sd_log_child_mean": float(np.log(s.child_mean).std()),
    })
pd.DataFrame(rows).to_csv(RESULTS / "sample_stats.csv", index=False)

with open(RESULTS / "session-info.txt", "w") as f:
    import matplotlib
    f.write(f"Python {sys.version.split()[0]} on {platform.system()} {platform.machine()}\n")
    f.write(f"pandas {pd.__version__}\nnumpy {np.__version__}\n")
    f.write(f"matplotlib {matplotlib.__version__}\nsqlite {sqlite3.sqlite_version}\n")
    f.write(f"bootstrap draws {N_BOOT}, seed 20261023\n")
print("done")
