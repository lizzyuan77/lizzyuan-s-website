"""
01_import.py  -  Build the Blog 6 SQLite database from the raw PSID files.

Inputs (PSID terms do not allow redistribution; request them, see README):
  <PSID_DIR>/raw/J366624/J366624.xlsx   Data Center extract, 95 variables, all individuals
  <PSID_DIR>/raw/pid23/PID23.txt        Parent Identification File, 2023 release (fixed width)

Output:
  <PSID_DIR>/working/blog6.sqlite with five clean tables
     people, parent_links, membership, family_income, cpi
  results/table_counts.csv

PSID_DIR defaults to post6/data/ (git-ignored). Run from the post6 folder:
  python code/01_import.py
"""
from pathlib import Path
import os
import sqlite3

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("PSID_DIR", ROOT / "data"))
RAW = DATA / "raw"
WORK = DATA / "working"
RESULTS = ROOT / "results"
WORK.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(exist_ok=True)


# --------------------------------------------------------------------------
# 1. Read the Data Center extract
# --------------------------------------------------------------------------
def read_psid_xlsx(path):
    """PSID's .xlsx carries a nonstandard sheet property (synchVertical)
    that openpyxl rejects. Drop it while reading; the data are untouched."""
    import openpyxl.worksheet.properties as props

    original = props.WorksheetProperties.__init__

    def patched(self, *args, **kwargs):
        kwargs.pop("synchVertical", None)
        kwargs.pop("synchHorizontal", None)
        original(self, *args, **kwargs)

    props.WorksheetProperties.__init__ = patched
    try:
        return pd.read_excel(path)
    finally:
        props.WorksheetProperties.__init__ = original


ind = read_psid_xlsx(RAW / "J366624" / "J366624.xlsx")

# --------------------------------------------------------------------------
# 2. Variable map: wave -> PSID variable names
#    (checked against the PSID codebook; see documentation/variable_dictionary.csv)
# --------------------------------------------------------------------------
# Individual file: interview (family) number, sequence number,
# relationship to reference person, age
IND_VARS = {
    1981: ("ER30343", "ER30344", "ER30345", "ER30346"),
    1982: ("ER30373", "ER30374", "ER30375", "ER30376"),
    1983: ("ER30399", "ER30400", "ER30401", "ER30402"),
    2001: ("ER33601", "ER33602", "ER33603", "ER33604"),
    2003: ("ER33701", "ER33702", "ER33703", "ER33704"),
    2005: ("ER33801", "ER33802", "ER33803", "ER33804"),
    2011: ("ER34101", "ER34102", "ER34103", "ER34104"),
    2013: ("ER34201", "ER34202", "ER34203", "ER34204"),
    2015: ("ER34301", "ER34302", "ER34303", "ER34305"),
}
# Family file: interview number, total family income,
# reference-person labor income, spouse/partner labor income.
# Income refers to the calendar year BEFORE the interview.
FAM_VARS = {
    1981: ("V7502", "V8065", None, None),
    1982: ("V8202", "V8689", None, None),
    1983: ("V8802", "V9375", None, None),
    2001: ("ER17002", "ER20456", "ER20443", "ER20447"),
    2003: ("ER21002", "ER24099", "ER24116", "ER24135"),
    2005: ("ER25002", "ER28037", "ER27931", "ER27943"),
    2011: ("ER47302", "ER52343", "ER52237", "ER52249"),
    2013: ("ER53002", "ER58152", "ER58038", "ER58050"),
    2015: ("ER60002", "ER65349", "ER65216", "ER65244"),
}
# Year of birth as reported in each wave (9999 = not known)
BIRTH_VARS = ["ER34307", "ER34206", "ER34106", "ER33806", "ER33706", "ER33606", "ER30404"]

# --------------------------------------------------------------------------
# 3. people: one row per person
# --------------------------------------------------------------------------
birth = ind[BIRTH_VARS].where((ind[BIRTH_VARS] >= 1880) & (ind[BIRTH_VARS] <= 2023))
people = pd.DataFrame({
    "id68": ind["ER30001"].astype(int),
    "pn": ind["ER30002"].astype(int),
    "sex": ind["ER32000"].map({1: "son", 2: "daughter"}),   # 9 = NA -> missing
    # most recent valid report of year of birth
    "birth_year": birth.bfill(axis=1).iloc[:, 0],
    "weight": ind["ER34413"],          # 2015 core/immigrant individual longitudinal weight
    "stratum": ind["ER31996"],
    "cluster": ind["ER31997"],
})

# --------------------------------------------------------------------------
# 4. membership: one row per person x interview wave
# --------------------------------------------------------------------------
rows = []
for wave, (fam, seq, rel, age) in IND_VARS.items():
    m = pd.DataFrame({
        "id68": ind["ER30001"], "pn": ind["ER30002"], "wave": wave,
        "family_id": ind[fam], "seq": ind[seq], "rel": ind[rel], "age": ind[age],
    })
    rows.append(m[m["family_id"] > 0])          # 0 = not interviewed that wave
membership = pd.concat(rows, ignore_index=True)
membership["current_member"] = membership["seq"].between(1, 20).astype(int)
# role in the family (codes 1/2 before 1983; 10/20/22 from 1983 on)
membership["role"] = np.select(
    [membership["rel"].isin([1, 10]),
     membership["rel"].isin([2, 20, 22])],
    ["reference_person", "spouse_partner"], default="other")

# --------------------------------------------------------------------------
# 5. family_income: one row per interview wave x family (nominal dollars)
#    The extract repeats family values on every member's row, so de-duplicate.
# --------------------------------------------------------------------------
rows = []
for wave, (fam, tot, head, spouse) in FAM_VARS.items():
    f = pd.DataFrame({
        "wave": wave, "income_year": wave - 1, "family_id": ind[fam],
        "total_income": ind[tot],
        "head_labor": ind[head] if head else np.nan,
        "spouse_labor": ind[spouse] if spouse else np.nan,
    })
    f = f[f["family_id"].notna() & (f["family_id"] > 0)].drop_duplicates()
    rows.append(f)
family_income = pd.concat(rows, ignore_index=True)
# Codebook, V8065/V8689/V9375: value 1 = "One dollar or less, including zero
# and negative amounts". It is a bottom code, not a $1 income, so store it as
# 0: it still enters 3-year averages but fails the positivity rule for logs.
bottom = (family_income["wave"] <= 1983) & (family_income["total_income"] == 1)
print(f"recoded {bottom.sum()} bottom-coded ($1) family incomes in 1980-1982 to 0")
family_income.loc[bottom, "total_income"] = 0

# --------------------------------------------------------------------------
# 6. parent_links from the Parent Identification File (fixed width,
#    column positions from PID23.do). 0 = no information about that parent.
# --------------------------------------------------------------------------
colspecs = [(1, 5), (5, 8), (8, 12), (12, 15), (42, 46), (46, 49)]
names = ["child_id68", "child_pn", "mother_id68", "mother_pn", "father_id68", "father_pn"]
pid = pd.read_fwf(RAW / "pid23" / "PID23.txt", colspecs=colspecs, names=names, header=None)
links = []
for parent in ["mother", "father"]:
    p = pid[["child_id68", "child_pn", f"{parent}_id68", f"{parent}_pn"]].copy()
    p.columns = ["child_id68", "child_pn", "parent_id68", "parent_pn"]
    p["parent_type"] = "birth_" + parent
    links.append(p[p["parent_id68"] > 0])
parent_links = pd.concat(links, ignore_index=True)

# --------------------------------------------------------------------------
# 7. CPI-U, U.S. city average, all items, annual average (1982-84 = 100)
#    Source: BLS historical CPI-U table (series CUUR0000SA0), retrieved 2026-10-23.
#    Indexed by INCOME year, not interview year.
# --------------------------------------------------------------------------
cpi = pd.DataFrame({
    "year": [1980, 1981, 1982, 2000, 2002, 2004, 2010, 2012, 2014, 2020],
    "cpi": [82.4, 90.9, 96.5, 172.2, 179.9, 188.9, 218.056, 229.594, 236.736, 258.811],
})

# --------------------------------------------------------------------------
# 8. Key checks before anything is written
# --------------------------------------------------------------------------
checks = {
    "people unique on (id68, pn)": not people.duplicated(["id68", "pn"]).any(),
    "membership unique on (id68, pn, wave)": not membership.duplicated(["id68", "pn", "wave"]).any(),
    "family_income unique on (wave, family_id)": not family_income.duplicated(["wave", "family_id"]).any(),
    "parent_links unique on (child, parent_type)":
        not parent_links.duplicated(["child_id68", "child_pn", "parent_type"]).any(),
}
for k, ok in checks.items():
    print(f"{'OK  ' if ok else 'FAIL'} {k}")
assert all(checks.values()), "key check failed"

# --------------------------------------------------------------------------
# 9. Write to SQLite
# --------------------------------------------------------------------------
db = WORK / "blog6.sqlite"
db.unlink(missing_ok=True)
con = sqlite3.connect(db)
for name, df in {"people": people, "parent_links": parent_links, "membership": membership,
                 "family_income": family_income, "cpi": cpi}.items():
    df.to_sql(name, con, index=False)
con.executescript("""
    CREATE UNIQUE INDEX ix_people ON people(id68, pn);
    CREATE UNIQUE INDEX ix_mem ON membership(id68, pn, wave);
    CREATE INDEX ix_mem_fam ON membership(wave, family_id);
    CREATE UNIQUE INDEX ix_fam ON family_income(wave, family_id);
    CREATE INDEX ix_links ON parent_links(child_id68, child_pn);
""")
counts = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
          for t in ["people", "parent_links", "membership", "family_income", "cpi"]}
con.close()
pd.Series(counts, name="rows").rename_axis("table").to_csv(RESULTS / "table_counts.csv")
print(counts)
