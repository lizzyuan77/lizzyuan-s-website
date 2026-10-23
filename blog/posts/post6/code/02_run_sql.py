"""
02_run_sql.py  -  Run the SQL steps inside Python and audit the result.

  1. code/02_match.sql      parent-child match, parent and child income histories
  2. code/03_summarize.sql  one summary row per child
  3. sample-flow counts by sex, join checks  ->  results/

Run from the post6 folder:  python code/02_run_sql.py
"""
from pathlib import Path
import os
import sqlite3

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("PSID_DIR", ROOT / "data"))
RESULTS = ROOT / "results"
con = sqlite3.connect(DATA / "working" / "blog6.sqlite")

for script in ["02_match.sql", "03_summarize.sql"]:
    con.executescript((ROOT / "code" / script).read_text())
    print("ran", script)

q = lambda sql: pd.read_sql_query(sql, con)

# ---------------------------------------------------------------------------
# Join checks: every analysis table must have one row per child
# ---------------------------------------------------------------------------
checks = q("""
SELECT 'pairs' AS tbl, COUNT(*) AS n_rows,
       COUNT(DISTINCT child_id68 || '-' || child_pn) AS n_children FROM pairs
UNION ALL
SELECT 'parent_summary', COUNT(*), COUNT(DISTINCT child_id68 || '-' || child_pn) FROM parent_summary
UNION ALL
SELECT 'matched', COUNT(*), COUNT(DISTINCT child_id68 || '-' || child_pn) FROM matched
""")
# The "nine-row trap": joining yearly rows of both generations directly
trap = q("""
SELECT COUNT(*) AS n_rows, COUNT(DISTINCT h.child_id68 || '-' || h.child_pn) AS n_children
FROM parent_history AS h
JOIN earnings AS e
  ON e.id68 = h.child_id68 AND e.pn = h.child_pn
JOIN matched AS m
  ON m.child_id68 = h.child_id68 AND m.child_pn = h.child_pn
WHERE e.income_year IN (2010, 2012, 2014)
""")
checks.loc[len(checks)] = ["naive_year_by_year_join", trap.n_rows[0], trap.n_children[0]]
assert (checks.loc[checks.tbl != "naive_year_by_year_join", "n_rows"]
        == checks.loc[checks.tbl != "naive_year_by_year_join", "n_children"]).all()
checks.to_csv(RESULTS / "join_checks.csv", index=False)
print(checks)

# ---------------------------------------------------------------------------
# Analysis samples. Logs need positive incomes; zeros stay inside the
# 3-year averages but a child with a zero single-year value is excluded.
# ---------------------------------------------------------------------------
con.executescript("""
DROP TABLE IF EXISTS analysis;
CREATE TABLE analysis AS
SELECT *,
       (weight > 0 AND parent_single > 0 AND parent_mean > 0
                   AND child_single  > 0 AND child_mean  > 0) AS main_sample,
       (weight > 0 AND parent_single > 0 AND parent_mean > 0
                   AND child_single  > 0 AND child_mean  > 0
                   AND early_single  > 0 AND early_mean  > 0) AS lifecycle_sample
FROM matched;
""")

flow = q("""
WITH cohort AS (
  SELECT sex, COUNT(*) AS n FROM people
  WHERE birth_year BETWEEN 1970 AND 1974 AND sex IS NOT NULL GROUP BY sex),
linked AS (SELECT sex, COUNT(*) AS n FROM pairs GROUP BY sex),
lived AS (
  SELECT p.sex, COUNT(DISTINCT p.child_id68 || '-' || p.child_pn) AS n
  FROM pairs p JOIN parent_history h
    ON h.child_id68 = p.child_id68 AND h.child_pn = p.child_pn GROUP BY p.sex),
parent3 AS (
  SELECT p.sex, COUNT(*) AS n FROM pairs p JOIN parent_summary s
    ON s.child_id68 = p.child_id68 AND s.child_pn = p.child_pn GROUP BY p.sex),
child3 AS (SELECT sex, COUNT(*) AS n FROM matched GROUP BY sex),
weighted AS (SELECT sex, SUM(weight > 0) AS n FROM matched GROUP BY sex),
positive AS (SELECT sex, SUM(main_sample) AS n FROM analysis GROUP BY sex),
lifecycle AS (SELECT sex, SUM(lifecycle_sample) AS n FROM analysis GROUP BY sex)
SELECT 1 AS step, 'Born 1970-1974, sex recorded' AS description, sex, n FROM cohort
UNION ALL SELECT 2, 'Linked to a birth mother with a PSID record', sex, n FROM linked
UNION ALL SELECT 3, 'Lived with her in at least one 1981-1983 interview', sex, n FROM lived
UNION ALL SELECT 4, 'Family income for all three years 1980-1982', sex, n FROM parent3
UNION ALL SELECT 5, 'Own labor earnings in 2010, 2012 and 2014', sex, n FROM child3
UNION ALL SELECT 6, 'Positive 2015 longitudinal weight', sex, n FROM weighted
UNION ALL SELECT 7, 'Positive single-year and averaged incomes (main sample)', sex, n FROM positive
UNION ALL SELECT 8, 'Also positive 2000/2002/2004 earnings (life-cycle sample)', sex, n FROM lifecycle
ORDER BY step, sex
""")
flow_wide = flow.pivot_table(index=["step", "description"], columns="sex", values="n").reset_index()
flow_wide.columns.name = None
flow_wide.to_csv(RESULTS / "sample_flow.csv", index=False)
print(flow_wide)

q("SELECT * FROM link_audit").to_csv(RESULTS / "link_audit.csv", index=False)

# Why are main-sample children dropped from step 6 to 7? Count zeros by sex.
zeros = q("""
SELECT sex,
       SUM(child_single <= 0) AS zero_child_2012,
       SUM(child_mean   <= 0) AS zero_child_mean,
       SUM(parent_single <= 0) AS nonpositive_parent_1981
FROM matched WHERE weight > 0 GROUP BY sex
""")
zeros.to_csv(RESULTS / "zero_exclusions.csv", index=False)
print(zeros)
con.close()
