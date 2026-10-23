-- 02_match.sql
-- Link each child to a parent, attach the parent's family income during
-- childhood, and build each adult's own labor earnings.
-- Run by code/02_run_sql.py against data/working/blog6.sqlite.

-- ---------------------------------------------------------------------------
-- Step 1. pairs: one row per child born 1970-1974 with a birth-mother record.
--   A person is identified by BOTH parts of the key: (id68, pn).
--   people appears twice: once as the child (c) and once as the parent (p).
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS pairs;
CREATE TABLE pairs AS
SELECT c.id68 AS child_id68, c.pn AS child_pn,
       c.sex, c.birth_year, c.weight,
       p.id68 AS parent_id68, p.pn AS parent_pn
FROM people AS c
JOIN parent_links AS l
  ON c.id68 = l.child_id68 AND c.pn = l.child_pn
 AND l.parent_type = 'birth_mother'
JOIN people AS p
  ON p.id68 = l.parent_id68 AND p.pn = l.parent_pn
WHERE c.birth_year BETWEEN 1970 AND 1974
  AND c.sex IS NOT NULL;

-- Audit: why do some cohort members have no usable mother link?
-- A LEFT JOIN keeps every child; missing matches show up as NULL.
DROP TABLE IF EXISTS link_audit;
CREATE TABLE link_audit AS
SELECT c.sex,
       COUNT(*)                                        AS cohort_children,
       SUM(l.child_id68 IS NULL)                       AS no_mother_in_pid,
       SUM(l.child_id68 IS NOT NULL AND p.id68 IS NULL) AS mother_without_record,
       SUM(p.id68 IS NOT NULL)                         AS matched_to_mother
FROM people AS c
LEFT JOIN parent_links AS l
  ON c.id68 = l.child_id68 AND c.pn = l.child_pn
 AND l.parent_type = 'birth_mother'
LEFT JOIN people AS p
  ON p.id68 = l.parent_id68 AND p.pn = l.parent_pn
WHERE c.birth_year BETWEEN 1970 AND 1974
  AND c.sex IS NOT NULL
GROUP BY c.sex;

-- ---------------------------------------------------------------------------
-- Step 2. parent_history: one row per child x childhood income year.
--   Rule: use the family income of the family in which the child AND the
--   mother were both current members (sequence 1-20) in that interview.
--   Family IDs are wave-specific, so every join uses wave AND family_id.
--   Amounts are converted to 2020 dollars with the CPI of the INCOME year.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS parent_history;
CREATE TABLE parent_history AS
SELECT pr.child_id68, pr.child_pn, f.income_year,
       f.total_income AS nominal_income,
       f.total_income * (SELECT cpi FROM cpi WHERE year = 2020) / k.cpi AS real_income
FROM pairs AS pr
JOIN membership AS mc                       -- the child in a childhood wave
  ON mc.id68 = pr.child_id68 AND mc.pn = pr.child_pn
 AND mc.wave IN (1981, 1982, 1983) AND mc.current_member = 1
JOIN membership AS mp                       -- the mother, same wave, same family
  ON mp.id68 = pr.parent_id68 AND mp.pn = pr.parent_pn
 AND mp.wave = mc.wave AND mp.family_id = mc.family_id
 AND mp.current_member = 1
JOIN family_income AS f
  ON f.wave = mc.wave AND f.family_id = mc.family_id
JOIN cpi AS k
  ON k.year = f.income_year;

-- ---------------------------------------------------------------------------
-- Step 3. earnings: one row per person x adult income year.
--   PSID reports labor income for the reference person and the
--   spouse/partner separately. Pick the field that matches the person's
--   ROLE in that wave (not their sex). Other members get NULL, not zero.
-- ---------------------------------------------------------------------------
DROP TABLE IF EXISTS earnings;
CREATE TABLE earnings AS
SELECT m.id68, m.pn, f.income_year, m.age, m.role,
       CASE m.role
            WHEN 'reference_person' THEN f.head_labor
            WHEN 'spouse_partner'   THEN f.spouse_labor
       END * (SELECT cpi FROM cpi WHERE year = 2020) / k.cpi AS real_earnings
FROM membership AS m
JOIN family_income AS f
  ON f.wave = m.wave AND f.family_id = m.family_id
JOIN cpi AS k
  ON k.year = f.income_year
WHERE m.wave >= 2001 AND m.current_member = 1;
