# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

**תוסף בזמן (TosafBazman)**: a student project for the "Vibe Coding with Claude" course at Ariel University (semester A, 5787). It builds a personal schedule for taking dietary supplements and estimates who should get tested for a deficiency.

- **Team:** all three are first-year nutrition sciences students.
  - Ran Refaelov: programmer, repo and Streamlit.
  - Polina Shifitsin: data and product (NHANES cleaning, Data Card, timing rules table).
  - Avital Magnetza: UX/UI.
- **Milestones:** M1 (definition doc) is done. M2 (data + dashboard) is due 25/11/2026 at 14:00 (public GitHub repo; every member submits the repo link on MoodLearn). Session 5 (18/11) is a checkpoint: data already loaded in the repo. The 3-minute pitch from the running dashboard at the start of session 6 is the lowest priority for the team. M3 is the trained model. A formal ML spec and a weekly plan will be added after course sessions 6 and 8.
- **Language:** the user writes in Hebrew, and `README.md` is in Hebrew. Reply in Hebrew unless asked otherwise. The team has no programming background, so explain in plain words.
- **Source of truth:** `README.md` is the spec and also holds the M2 Data Card, "what we fixed and why", insights, baseline and team table. Read it before planning work.

## Repo layout

- `app.py`: Streamlit EDA dashboard (RTL Hebrew). The main insight sits on top, then a `st.segmented_control` switches between two views. Each view has its own sidebar filters.
  1. **Timing and dosing, all 40 supplements.** Reads `data/timing_rules.csv` and `data/supplement_research.csv`. Filters: category, confidence, source country. KPI = % of supplements that need separating from another one. Charts: time of day, separation map, facts per supplement by country, confidence by category. Also a per-supplement card and the research table with links.
  2. **Blood levels: vitamin D and iron.** Reads `data/nhanes_supplements_vitd_clean.csv` and `data/supplement_intake_by_person.csv`. Filters: age, sex, race/ethnicity, exam season. A target switch (vitamin D / iron) changes the metrics, baseline and charts. Also an "Israel" table of Israeli research rows and a sample table.
  - No map: the data has no location. Inside charts the CSS keeps `direction: ltr`, otherwise RTL breaks the Vega axis labels.
- `data/supplement_research.csv`: research facts table (one fact per row, each with `source`, `url`, `country` ישראל/ארה"ב/בינלאומי and `source_type`). Built by `scripts/build_research_table.py` from `data/supplement_timing_reference.csv` + `data/research_sources/*.csv`. The script dedupes rows, maps name variants to the `timing_rules.csv` names (see `SAME_AS`), and asserts ≥300 rows and an http url on every row. To add facts, add a CSV in `research_sources/` with the same 9 columns and rebuild.
- `data/raw/`: original NHANES 2017–2018 XPT files (`DEMO_J`, `DSQTOT_J`, `DSQIDS_J`, `VID_J`, `FERTIN_J`, `BMX_J`). Never modify them.
- `scripts/clean_data.py`: raw → `data/nhanes_supplements_vitd_clean.csv` + `data/cleaning_log.csv`. Must print `9254 שורות -> נקי: 5068 שורות`.
- `scripts/build_supplement_tables.py`: → `data/supplement_intake_by_person.csv` (16 nutrients per person) and `data/supplement_prevalence.csv`.
- `scripts/build_timing_rules.py`: the rules are written in Python dicts here and it writes `data/timing_rules.csv`. `scripts/make_xlsx.py` turns that CSV into `docs/timing_rules.xlsx` for human review. Edit rules in the script, then rebuild both.
- `prototype/tosaf-bazman.html`: the M1 prototype (single-file Hebrew RTL HTML, vanilla JS). Published artifact: https://claude.ai/artifact/XW47W1rhrcCKfZRuuHZBdY. Republish to that same URL; a new publish creates a new link.
- `requirements.txt`: pinned (`streamlit==1.67.0`, `altair==6.3.0`, `pandas==3.1.1`, `numpy==2.5.5`). Tested in a fresh venv (Python 3.13, and again with 3.15 in `.venv/`) on 18/11/2026.
- `.gitignore` excludes `venv/`, `.venv/`, `.vs/`, `__pycache__/`. Never commit a virtual environment.

## What we learned from the data (M2)

- Clean file: **5,068 adults × 26 columns**, no missing values, no duplicates. 9,254 → 5,068: adults 18+, not pregnant, with a vitamin D measurement, BMI and ferritin, no "refused/don't know".
- Empty supplement doses were filled with 0 (= no intake from supplements), not the mean. Ferritin and doses were clipped at the 99th percentile. The target was not clipped. NHANES survey weights were **not** applied, so numbers describe the sample, not the US population.
- Target: `vitd_nmol_l` (regression). Derived: `vitd_low` (1 if < 50 nmol/L) and `vitd_status` (<30 deficient, 30–49.9 insufficient, ≥50 sufficient, per NIH ODS).
- Mean 25(OH)D 68.4 nmol/L, median 64.5. **29.4%** are below 50.
- % low by vitamin D dose from supplements: none 41.2% (n=3,151) · >0–10 mcg 23.6% · >10–25 mcg 9.0% · >25–50 mcg 3.6% · >50 mcg 1.4%.
- 55.3% took any supplement in the last 30 days. Large race/ethnicity gap (Non-Hispanic Black 51.2% low vs Non-Hispanic White 12.7%); small sex gap. BMI > 30: 33.8% low vs ~26% at 18.5–30.
- Exam season (`exam_season`, from `RIDEXMON`): Nov-Apr 35.4% low vs May-Oct 23.8% (non-users: 53.0% vs 38.2%). NHANES runs winter exams mostly in southern states, so the true seasonal gap is likely larger.
- Second target `iron_low` = ferritin < 15 ng/mL (WHO 2020 cutoff for healthy adults): 5.4% overall, women 9.3% vs men 1.4%. For women it is 15–17% at ages 18–50 and 2.3% at 51+. Ferritin is clipped at p99, so use the classification target, not ferritin regression.
- NHANES does not measure creatine or protein powder as nutrients (only 11 and 16 people named such a product). Never write "too few people take creatine" as if it were a research gap: the creatine and protein facts come from the research table (ISSN position stands, NIH ODS).
- **Baseline for M3:** vitamin D regression = predict the median 64.5 → MAE 23.8 nmol/L. `vitd_low` = always "not low" → accuracy 70.6%. `iron_low` = always "not low" → accuracy 94.6% (imbalanced, so report recall too).
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
