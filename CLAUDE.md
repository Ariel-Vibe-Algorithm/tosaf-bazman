# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

**תוסף בזמן (TosafBazman)**: a student project for the "Vibe Coding with Claude" course at Ariel University (semester A, 5787). It builds a personal schedule for taking dietary supplements and estimates who should get tested for a deficiency.

- **Team:** all three are first-year nutrition sciences students.
  - Ran Refaelov: programmer, repo and Streamlit.
  - Polina Shifitsin: data and product (NHANES cleaning, Data Card, timing rules table).
  - Avital Magnetza: UX/UI.
- **Repo:** team repo in the course org: https://github.com/Ariel-Vibe-Algorithm/tosaf-bazman (moved from `refaeloveran/M1--nutrition`). Grading = what is on `main` at the deadline.
- **Milestones:** M1 done. **M2 (25/11/2026 14:00) = `eda.ipynb`**, a Jupyter notebook that answers the four EDA questions (column types, quality, distributions esp. of y, correlation with y incl. leakage), with a conclusion under every chart, plus clean data, README (problem, y, source, fixes, team table, insight, baseline), updated CLAUDE.md and a commit from every member. Streamlit is no longer required for M2 (update of 24/11); `app.py` stays as a bonus. 3-minute pitch straight from the notebook. Next: 2/12 bootcamp 2 (first model), **M3 16/12** model in the app, 23/12 deploy, **Demo Day 6/1/2027**.
- **Language:** the user writes in Hebrew, and `README.md` is in Hebrew. Reply in Hebrew unless asked otherwise. The team has no programming background, so explain in plain words.
- **Source of truth:** `README.md` is the spec and also holds the M2 Data Card, "what we fixed and why", insights, baseline and team table. Read it before planning work.

## Repo layout

- `eda.ipynb`: the M2 deliverable. Built to run top to bottom (Run All) from the repo root, Hebrew RTL markdown, English chart labels (matplotlib breaks Hebrew). Main y = `vitd_low`. Leakage findings: `vitd_low`/`vitd_status` derive from `vitd_nmol_l`, `iron_low` from ferritin (100% reproducible), `seqn` encodes the cycle (r = 0.20); no real feature has |r| > 0.9. 466 people answered "no supplement" yet have calcium/magnesium doses (likely antacids counted by NHANES, vitamin D never affected). Keep every conclusion consistent with the printed numbers.

- `app.py`: Streamlit EDA dashboard (RTL Hebrew). The main insight sits on top, then a `st.segmented_control` switches between two views. Each view has its own sidebar filters.
  1. **Timing and dosing, all 40 supplements.** Reads `data/timing_rules.csv` and `data/supplement_research.csv`. Filters: category, confidence, source country. KPI = % of supplements that need separating from another one. Charts: time of day, separation map, facts per supplement by country, confidence by category. Also a per-supplement card and the research table with links.
  2. **Blood levels: vitamin D and iron.** Reads `data/nhanes_supplements_vitd_clean.csv` and `data/supplement_intake_by_person.csv`. Filters: survey cycle, age, sex, race/ethnicity, exam season. Includes a cycle-comparison chart. A target switch (vitamin D / iron) changes the metrics, baseline and charts. Also an "Israel" table of Israeli research rows and a sample table.
  - No map: the data has no location. Inside charts the CSS keeps `direction: ltr`, otherwise RTL breaks the Vega axis labels.
- `data/supplement_research.csv`: research facts table (one fact per row, each with `source`, `url`, `country` ישראל/ארה"ב/בינלאומי and `source_type`). Built by `scripts/build_research_table.py` from `data/supplement_timing_reference.csv` + `data/research_sources/*.csv`. The script dedupes rows, maps name variants to the `timing_rules.csv` names (see `SAME_AS`), and asserts ≥300 rows and an http url on every row. To add facts, add a CSV in `research_sources/` with the same 9 columns and rebuild.
- `data/raw/`: original NHANES XPT files from two cycles: 2017–2018 (`_J`) and Aug 2021–Aug 2023 (`_L`), each with `DEMO`, `DSQTOT`, `DSQIDS`, `VID`, `FERTIN`, `BMX`. Never modify them. The 2019–2020 cycle was cut short by COVID and has no vitamin D, so it is not used.
- `scripts/clean_data.py`: raw (both cycles) → `data/nhanes_supplements_vitd_clean.csv` + `data/cleaning_log.csv`. Must print `21187 שורות -> נקי: 9626 שורות` (2017-2018: 5090, 2021-2023: 4536).
- `scripts/build_supplement_tables.py`: → `data/supplement_intake_by_person.csv` (16 nutrients per person) and `data/supplement_prevalence.csv`.
- `scripts/build_timing_rules.py`: the rules are written in Python dicts here and it writes `data/timing_rules.csv`. `scripts/make_xlsx.py` turns that CSV into `docs/timing_rules.xlsx` for human review. Edit rules in the script, then rebuild both.
- `prototype/tosaf-bazman.html`: the M1 prototype (single-file Hebrew RTL HTML, vanilla JS). Published artifact: https://claude.ai/artifact/XW47W1rhrcCKfZRuuHZBdY. Republish to that same URL; a new publish creates a new link.
- `requirements.txt`: pinned (`streamlit==1.67.0`, `altair==6.3.0`, `pandas==3.1.1`, `numpy==2.5.5`, `matplotlib==3.11.2`, `ipykernel==7.4.0` for the notebook). Tested in a fresh venv (Python 3.13, and again with 3.15 in `.venv/`) on 18/11/2026.
- `.gitignore` excludes `venv/`, `.venv/`, `.vs/`, `__pycache__/`. Never commit a virtual environment.

## What we learned from the data (M2)

- Clean file: **9,626 adults × 27 columns** (2017–2018: 5,090; 2021–2023: 4,536), no duplicates. Column `cycle` marks the survey round. 21,187 → 9,626: adults 18+, not pregnant, with a vitamin D measurement, BMI, and an answer to the supplement question (1,202 adults in 2021–23 skipped the supplement interview).
- **Ferritin is intentionally missing** for 3,634 rows (`ferritin_ng_ml` and `iron_low` empty): in 2021–23 the CDC measured ferritin only in women 12–49. Rows are kept for vitamin D; iron analyses use only the 5,992 rows with ferritin. All other columns have no missing values.
- 2021–23 used a different sample design (no oversampling by race/Hispanic origin; 62% Non-Hispanic White vs 35% in 2017–18), and the CDC advises caution when combining it with earlier cycles. Cycle differences are association only.
- Empty supplement doses were filled with 0 (= no intake from supplements), not the mean. Ferritin and doses were clipped at the 99th percentile. The target was not clipped. NHANES survey weights were **not** applied, so numbers describe the sample, not the US population.
- Target: `vitd_nmol_l` (regression). Derived: `vitd_low` (1 if < 50 nmol/L) and `vitd_status` (<30 deficient, 30–49.9 insufficient, ≥50 sufficient, per NIH ODS).
- Both cycles: mean 25(OH)D 75.1 nmol/L, median 70.2, **24.4%** below 50. By cycle: 2017–18 29.4% low, 37.7% take vitamin D supplements; 2021–23 18.7% low, 51.2% take them (Non-Hispanic Black 51.2% → 39.8%).
- % low by vitamin D dose from supplements (both cycles): none 38.0% (n=5,386) · >0–10 mcg 20.5% · >10–25 mcg 7.3% · >25–50 mcg 2.4% · >50 mcg 0.5%.
- 59.3% took any supplement in the last 30 days. Large race/ethnicity gap (Non-Hispanic Black 47.8% low vs Non-Hispanic White 11.8%); small sex gap. BMI > 30: 28.2% low vs ~21% at 18.5–30.
- Exam season (`exam_season`, from `RIDEXMON`): Nov-Apr 30.4% low vs May-Oct 18.9% (vitamin D non-users: 46.3% vs 30.1%). NHANES runs winter exams mostly in southern states, so the true seasonal gap is likely larger.
- Second target `iron_low` = ferritin < 15 ng/mL (WHO 2020 cutoff for healthy adults), on the 5,992 measured: 6.5% overall, women 10.1% vs men 1.4% (men only from 2017–18). In 2017–18 alone: women 9.3% vs men 1.4%. Women 18–50 ≈15%, 51+ 2.3%. Ferritin is clipped at p99, so use the classification target, not ferritin regression.
- NHANES does not measure creatine or protein powder as nutrients (only 34 and 53 people across both cycles named such a product). Never write "too few people take creatine" as if it were a research gap: the creatine and protein facts come from the research table (ISSN position stands, NIH ODS).
- **Baseline for M3 (both cycles):** vitamin D regression = predict the median 70.2 → MAE 26.7 nmol/L. `vitd_low` = always "not low" → accuracy 75.6%. `iron_low` = always "not low" → accuracy 93.5% on rows with ferritin (imbalanced, so report recall too). The dashboard recomputes these per cycle filter.
- **Israel focus:** the app is for Israel first. There is no open Israeli person-level blood dataset, so the model trains on NHANES and the dashboard shows Israeli research next to it. For example, Clalit 2009: 46.5% of Jews and 76.7% of Arabs were below 50 nmol/L (Saliba 2012). NIH ODS and gov.il (Ministry of Health) block automated fetching. The user can save those pages as PDF and upload them.

## Timing rules table (`data/timing_rules.csv`)

- 40 supplements, one row each. Columns: `best_time`, `with_food`, `doses_per_day`, `next_dose_after_hours` (24 = once a day, 12 = twice), `can_split`, `separate_from` (format `name:minutes; name:minutes`, applies in both directions), `avoid_food_drinks` + `food_drinks_gap_minutes`, `drug_interactions` + `drug_gap`, `severity` (חמורה/בינונית/קלה), `works_well_with`, `caution`, `confidence`, `confidence_note`, `source_main`, `source_extra`.
- `confidence`: מבוסס = stated in NIH ODS / NCCIH; חלקי = partly sourced, partly common practice (usually time of day); מקובל = common practice only and needs team review. Keep every rule traceable to a source, and never upgrade a confidence level without a source.
- Known gaps: psyllium and collagen have no source yet; glucosamine and L-theanine are only loosely sourced. MedlinePlus was not reachable when the table was built.
- The prototype's `SEP` pairs (iron vs calcium/zinc/magnesium, zinc vs calcium) match this table.

## Writing rules (important)

- **Association, not causation.** Cross-sectional data. Write "supplement users have higher levels on average", never "the supplement raised the level".
- NHANES has no performance data (strength, running), and it is US-only, not Israel. Israeli facts must come from Israeli sources (`country=ישראל`).
- Every research fact needs the url of the page it came from. Don't add a number you did not see on that page.
- Every number in the README or the pitch must come from the clean file or a script. Don't invent numbers.
- The app is a helper, not medical advice. No personal dosing instructions.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```
