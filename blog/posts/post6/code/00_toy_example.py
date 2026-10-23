"""
00_toy_example.py  -  A FICTIONAL two-generation example for the tutorial.

Every row below is invented. It uses the same table layout and the same SQL
as the real analysis, so the outputs shown in the article are genuine query
results, but they describe no PSID respondent.

Writes results/toy_*.csv.  Run from the post6 folder:  python code/00_toy_example.py
"""
from pathlib import Path
import sqlite3

import pandas as pd

RES = Path(__file__).resolve().parents[1] / "results"
RES.mkdir(exist_ok=True)
con = sqlite3.connect(":memory:")

people = pd.DataFrame({
    "id68":       [101, 101, 101, 205, 205],
    "pn":         [1,   2,   31,  2,   30],
    "name":       ["Ana (mother)", "Ben (father)", "Cleo (daughter)", "Dee (mother)", "Eli (son)"],
    "birth_year": [1948, 1946, 1972, 1950, 1973],
})
parent_links = pd.DataFrame({
    "child_id68": [101, 205], "child_pn": [31, 30],
    "parent_id68": [101, 205], "parent_pn": [1, 2],
})
# Note: Eli's pn (30) and Dee's id68 (205) both also appear on other people.
# Only the PAIR (id68, pn) identifies one person.
parent_income = pd.DataFrame({
    "child_id68": [101] * 3 + [205] * 3, "child_pn": [31] * 3 + [30] * 3,
    "income_year": [1980, 1981, 1982] * 2,
    "real_income": [62000, 18000, 64000, 41000, 43000, 42000],
})
child_earnings = pd.DataFrame({
    "id68": [101] * 3 + [205] * 3, "pn": [31] * 3 + [30] * 3,
    "income_year": [2010, 2012, 2014] * 2,
    "real_earnings": [51000, 53000, 55000, 39000, 47000, 40000],
})
for name, df in {"people": people, "parent_links": parent_links,
                 "parent_history": parent_income, "earnings": child_earnings}.items():
    df.to_sql(name, con, index=False)
    df.to_csv(RES / f"toy_{name}.csv", index=False)

q = lambda sql: pd.read_sql_query(sql, con)

pairs = q("""
SELECT c.name AS child, c.birth_year,
       p.name AS parent, p.id68 AS parent_id68, p.pn AS parent_pn
FROM people AS c
JOIN parent_links AS l
  ON c.id68 = l.child_id68 AND c.pn = l.child_pn
JOIN people AS p
  ON p.id68 = l.parent_id68 AND p.pn = l.parent_pn
WHERE c.birth_year BETWEEN 1970 AND 1974
""")
pairs.to_csv(RES / "toy_pairs.csv", index=False)

# The mistake: join the yearly rows of both generations directly
trap = q("""
SELECT h.child_id68, h.child_pn, h.income_year AS parent_year, e.income_year AS child_year
FROM parent_history AS h
JOIN earnings AS e ON e.id68 = h.child_id68 AND e.pn = h.child_pn
""")
trap.to_csv(RES / "toy_nine_row_trap.csv", index=False)

summary = q("""
SELECT child_id68, child_pn,
       AVG(real_income) AS parent_mean,
       MAX(CASE WHEN income_year = 1981 THEN real_income END) AS parent_single
FROM parent_history
WHERE income_year IN (1980, 1981, 1982)
GROUP BY child_id68, child_pn
HAVING COUNT(*) = 3 AND COUNT(real_income) = 3
""")
summary.to_csv(RES / "toy_parent_summary.csv", index=False)
print(pairs, trap.groupby(["child_id68", "child_pn"]).size(), summary, sep="\n\n")
