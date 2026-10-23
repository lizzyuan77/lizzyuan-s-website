-- 03_summarize.sql
-- Collapse each income history to ONE row per child before joining the
-- generations. (Joining 3 parent years to 3 child years directly would
-- create 3 x 3 = 9 rows per child.)

-- Parents: income years 1980-1982 (child roughly age 6-12).
DROP TABLE IF EXISTS parent_summary;
CREATE TABLE parent_summary AS
SELECT child_id68, child_pn,
       AVG(real_income) AS parent_mean,
       MAX(CASE WHEN income_year = 1981 THEN real_income END) AS parent_single
FROM parent_history
WHERE income_year IN (1980, 1981, 1982)
GROUP BY child_id68, child_pn
HAVING COUNT(*) = 3 AND COUNT(real_income) = 3;

-- Children, mature window: income years 2010, 2012, 2014 (age about 36-44).
DROP TABLE IF EXISTS child_summary;
CREATE TABLE child_summary AS
SELECT id68, pn,
       AVG(real_earnings) AS child_mean,
       MAX(CASE WHEN income_year = 2012 THEN real_earnings END) AS child_single
FROM earnings
WHERE income_year IN (2010, 2012, 2014)
GROUP BY id68, pn
HAVING COUNT(*) = 3 AND COUNT(real_earnings) = 3;

-- Children, early-career window: income years 2000, 2002, 2004 (age about 26-34).
DROP TABLE IF EXISTS child_early;
CREATE TABLE child_early AS
SELECT id68, pn,
       AVG(real_earnings) AS early_mean,
       MAX(CASE WHEN income_year = 2002 THEN real_earnings END) AS early_single
FROM earnings
WHERE income_year IN (2000, 2002, 2004)
GROUP BY id68, pn
HAVING COUNT(*) = 3 AND COUNT(real_earnings) = 3;

-- One row per child: identifiers, weight, and every income measure.
DROP TABLE IF EXISTS matched;
CREATE TABLE matched AS
SELECT p.*,
       a.parent_single, a.parent_mean,
       b.child_single,  b.child_mean,
       e.early_single,  e.early_mean
FROM pairs AS p
JOIN parent_summary AS a
  ON p.child_id68 = a.child_id68 AND p.child_pn = a.child_pn
JOIN child_summary AS b
  ON p.child_id68 = b.id68 AND p.child_pn = b.pn
LEFT JOIN child_early AS e
  ON p.child_id68 = e.id68 AND p.child_pn = e.pn;
