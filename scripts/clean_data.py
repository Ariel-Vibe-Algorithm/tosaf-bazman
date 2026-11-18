"""ניקוי נתוני NHANES משני סבבים (2017-2018 ו-2021-2023): תוספי תזונה מול ויטמין D וברזל בדם.
הרצה: python scripts/clean_data.py   (מהתיקייה הראשית של הריפו)
קלט: data/raw/*.xpt   (סיומת _J = 2017-2018, סיומת _L = 2021-2023)
פלט: data/nhanes_supplements_vitd_clean.csv + data/cleaning_log.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "data"
CYCLES = {"J": "2017-2018", "L": "2021-2023"}
read = lambda n: pd.read_sas(RAW / f"{n}.xpt", format="xport", encoding=None)
log = []
def step(name, before, after, why, affected=None):
    log.append({"step": name, "rows_before": before, "rows_after": after,
                "rows_affected": before - after if affected is None else affected, "why": why})

parts, ids_parts, dups = [], [], 0
for suf, label in CYCLES.items():
    demo, tot, vid, fer, bmx, ids = (read(f"{n}_{suf}") for n in ["DEMO", "DSQTOT", "VID", "FERTIN", "BMX", "DSQIDS"])
    dups += sum(int(d.SEQN.duplicated().sum()) for d in (demo, tot, vid, fer, bmx))
    d = demo[["SEQN", "RIDAGEYR", "RIAGENDR", "RIDRETH3", "RIDEXPRG", "RIDEXMON"]]
    d = d.merge(vid[["SEQN", "LBXVIDMS"]], on="SEQN", how="left")
    d = d.merge(fer[["SEQN", "LBXFER"]], on="SEQN", how="left")
    d = d.merge(bmx[["SEQN", "BMXBMI", "BMXWT"]], on="SEQN", how="left")
    d = d.merge(tot[["SEQN", "DSD010", "DSDCOUNT", "DSQTVD", "DSQTVC", "DSQTMAGN", "DSQTIRON",
                     "DSQTZINC", "DSQTVB12", "DSQTCALC"]], on="SEQN", how="left")
    d["cycle"] = label
    parts.append(d)
    ids_parts.append(ids[["SEQN", "DSDSUPP"]])
    print(f"{label}: {len(d)} נבדקים בקובץ הדמוגרפיה")

# 0. איחוד הסבבים ובדיקת כפילויות (מפתח: SEQN, מספר רץ שלא חוזר בין סבבים)
df = pd.concat(parts, ignore_index=True)
ids = pd.concat(ids_parts, ignore_index=True)
n = len(df)
dups += int(df.SEQN.duplicated().sum())
step("combine_cycles_and_duplicates", n, n,
     "איחדנו את סבב 2017-2018 (קבצי _J) עם סבב 2021-2023 (קבצי _L), ובדקנו SEQN כפול בכל הקבצים ובין הסבבים; "
     "לא נמצאו כפילויות. נוספה עמודה cycle כדי שאפשר יהיה להשוות בין הסבבים", affected=dups)

# 1. מבוגרים בלבד
b = len(df); df = df[df.RIDAGEYR >= 18]; step("adults_only", b, len(df), "משאירים גיל 18 ומעלה: מינוני תוספים וספי ויטמין D מוגדרים למבוגרים")
# 2. הריון
b = len(df); df = df[df.RIDEXPRG != 1]; step("drop_pregnant", b, len(df), "מסירים נשים בהריון: דרישות הוויטמינים והרמות בדם שונות")
# 3. אין ערך y
b = len(df); df = df[df.LBXVIDMS.notna()]; step("drop_missing_target", b, len(df), "בלי מדידת ויטמין D בדם אין משתנה יעד; אי אפשר להשלים אותו בלי להמציא נתונים")
# 4. קודי סירוב/לא יודע בשאלה האם נוטל תוסף
no_interview = int(df.DSD010.isna().sum())
b = len(df); df = df[df.DSD010.isin([1, 2])]
step("drop_no_supplement_answer", b, len(df),
     f"בלי תשובה לשאלה אם נטל תוסף אין לנו את המאפיין המרכזי. {no_interview} נבדקים (כמעט כולם מ-2021-2023) לא עברו "
     "את ראיון התוספים בכלל, והשאר ענו קוד 7 (סירב) או 9 (לא יודע), שהם לא ערך אמיתי")
# 5. BMI חסר
b = len(df); df = df[df.BMXBMI.notna()]; step("drop_missing_bmi", b, len(df), "BMI חסר (לא נמדד); משתנה מרכזי בהסבר רמת ויטמין D")
# 6. פריטין חסר: מסמנים ולא מוחקים
df = df.copy()
no_fer = int(df.LBXFER.isna().sum())
step("mark_missing_ferritin", len(df), len(df),
     "פריטין לא נמדד אצל כולם: ב-2021-2023 ה-CDC מדד פריטין רק לנשים בגילאי 12-49, וב-2017-2018 חסרים מעט ערכים. "
     "לא מחקנו את השורות (ויטמין D נמדד אצלן) ולא השלמנו ערך: השארנו את ferritin_ng_ml ואת iron_low ריקים. "
     "ניתוחי הברזל משתמשים רק בשורות שבהן הפריטין נמדד", affected=no_fer)

# 7. מינוני תוספים: לא נוטל -> 0, נוטל בלי ערך -> המוצר לא מכיל את החומר -> 0
dose = {"DSQTVD": "supp_vitd_mcg", "DSQTVC": "supp_vitc_mg", "DSQTMAGN": "supp_magnesium_mg", "DSQTIRON": "supp_iron_mg",
        "DSQTZINC": "supp_zinc_mg", "DSQTVB12": "supp_b12_mcg", "DSQTCALC": "supp_calcium_mg"}
nan_filled = int(df[list(dose)].isna().sum().sum())
df[list(dose)] = df[list(dose)].fillna(0)
step("fill_doses_with_zero", len(df), len(df),
     "תאים ריקים במינון = אין צריכה מתוספים של אותו חומר (לא נוטל תוסף, או שהמוצר לא מכיל אותו); מילאנו ב-0 ולא בממוצע",
     affected=nan_filled)
df = df.rename(columns=dose)
df["n_supplements"] = df.DSDCOUNT.fillna(0).round().astype(int)
df["takes_supplement"] = (df.DSD010 == 1).astype(int)

# 8. דגלי תוספים לפי שם מוצר (קבצי DSQIDS)
ids["name"] = ids.DSDSUPP.astype(str).str.replace(r"^b'|'$", "", regex=True).str.upper()
pat = {"takes_creatine": r"CREATINE", "takes_probiotic": r"PROBIOTIC|LACTOBACILL|ACIDOPHIL|BIFIDO",
       "takes_fish_oil": r"FISH OIL|OMEGA", "takes_multivitamin": r"MULTIVITAMIN|MULTI-VITAMIN",
       "takes_protein_powder": r"PROTEIN|WHEY"}
for col, p in pat.items():
    users = set(ids.loc[ids.name.str.contains(p, regex=True, na=False), "SEQN"])
    df[col] = df.SEQN.isin(users).astype(int)

# 9. סוגי עמודות ותוויות קריאות (הקודים זהים בשני הסבבים, לפי תיעוד DEMO_J ו-DEMO_L)
df["sex"] = df.RIAGENDR.map({1: "male", 2: "female"})
df["race_ethnicity"] = df.RIDRETH3.map({1: "Mexican American", 2: "Other Hispanic", 3: "Non-Hispanic White",
                                        4: "Non-Hispanic Black", 6: "Non-Hispanic Asian", 7: "Other/Multiracial"})
df["exam_season"] = df.RIDEXMON.map({1: "Nov-Apr", 2: "May-Oct"})  # עונת הבדיקה: חשיפה לשמש משפיעה על ויטמין D
df["age_years"] = df.RIDAGEYR.round().astype(int)
df = df.rename(columns={"SEQN": "seqn", "BMXBMI": "bmi", "BMXWT": "weight_kg", "LBXFER": "ferritin_ng_ml", "LBXVIDMS": "vitd_nmol_l"})
df["seqn"] = df.seqn.astype(int)
step("types_and_labels", len(df), len(df),
     "קודים מספריים הוחלפו בתוויות (מין, מוצא, עונת הבדיקה); גיל ו-SEQN הומרו למספר שלם; שמות עמודות תורגמו לשמות ברורים",
     affected=len(df))

# 10. חריגים: חיתוך (winsorize) באחוזון 99 לפריטין ולמינוני תוספים; y נשאר כפי שנמדד
clipped = 0
for c in ["ferritin_ng_ml"] + list(dose.values()):
    base = df.loc[df[c] > 0, c] if c.startswith("supp_") else df[c].dropna()
    cap = base.quantile(0.99)
    m = df[c] > cap
    clipped += int(m.sum()); df.loc[m, c] = cap
step("clip_outliers_p99", len(df), len(df),
     "ערכים קיצוניים (למשל פריטין מעל אלפי ng/mL, מגה-מינונים) נחתכו לאחוזון 99 כדי שלא יעוותו גרפים וממוצעים; "
     "לא מחקנו שורות. משתנה היעד לא נחתך", affected=clipped)

# 11. משתני יעד נגזרים
df["vitd_status"] = pd.cut(df.vitd_nmol_l, [0, 30, 50, np.inf], right=False,
                           labels=["deficient (<30)", "inadequate (30-49.9)", "sufficient (>=50)"]).astype(str)
df["vitd_low"] = (df.vitd_nmol_l < 50).astype(int)
# y שני: מאגרי ברזל נמוכים. סף WHO 2020 למבוגרים בריאים: פריטין מתחת ל-15 ng/mL (= µg/L).
# ריק כשהפריטין לא נמדד. החיתוך באחוזון 99 נוגע רק לערכים הגבוהים, ולכן לא משנה את הסיווג הזה.
df["iron_low"] = (df.ferritin_ng_ml < 15).astype("Int64").where(df.ferritin_ng_ml.notna())
step("derive_targets", len(df), len(df),
     "נגזרו משתני יעד: vitd_status ו-vitd_low (סף 50 nmol/L, NIH ODS) ו-iron_low (פריטין מתחת ל-15 ng/mL, WHO 2020; "
     "ריק כשהפריטין לא נמדד)", affected=len(df))

cols = ["seqn", "cycle", "age_years", "sex", "race_ethnicity", "exam_season", "bmi", "weight_kg", "ferritin_ng_ml",
        "takes_supplement", "n_supplements",
        "supp_vitd_mcg", "supp_vitc_mg", "supp_magnesium_mg", "supp_iron_mg", "supp_zinc_mg", "supp_b12_mcg", "supp_calcium_mg",
        "takes_creatine", "takes_probiotic", "takes_fish_oil", "takes_multivitamin", "takes_protein_powder",
        "vitd_nmol_l", "vitd_status", "vitd_low", "iron_low"]
df = df[cols].round(2).reset_index(drop=True)
# החוסרים היחידים מותרים בעמודות הפריטין, ושם הם מסומנים בכוונה
assert df.drop(columns=["ferritin_ng_ml", "iron_low"]).isna().sum().sum() == 0 and not df.seqn.duplicated().any()
assert (df.ferritin_ng_ml.isna() == df.iron_low.isna()).all()
df.to_csv(OUT / "nhanes_supplements_vitd_clean.csv", index=False, encoding="utf-8")
pd.DataFrame(log).to_csv(OUT / "cleaning_log.csv", index=False, encoding="utf-8-sig")
by_cycle = ", ".join(f"{c}: {k}" for c, k in df.cycle.value_counts().sort_index().items())
print(f"נתונים גולמיים: {n} שורות -> נקי: {len(df)} שורות, {df.shape[1]} עמודות ({by_cycle})")
print(f"פריטין נמדד ב-{df.ferritin_ng_ml.notna().sum()} שורות")
