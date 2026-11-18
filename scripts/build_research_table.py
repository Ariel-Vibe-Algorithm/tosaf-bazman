"""בונה את data/supplement_research.csv: טבלת עובדות מחקריות על 40 התוספים, לכל שורה מקור וקישור.

מקורות הקלט:
- data/supplement_timing_reference.csv  עובדות מ-NIH ODS, NCCIH ו-ISSN (נאספו בשלב הקודם)
- data/research_sources/*.csv           עובדות נוספות: ויטמינים ומינרלים, צמחים וספורט, ישראל

הרצה: python scripts/build_research_table.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
COLS = ["supplement_he", "supplement_en", "topic", "fact_he", "value", "source", "url", "country", "source_type"]

# 1. העובדות שנאספו קודם (מקורות רשמיים אמריקאיים ועמדות ISSN)
ref = pd.read_csv(DATA / "supplement_timing_reference.csv", encoding="utf-8-sig")
ref["country"] = ref.source.str.contains("ISSN").map({True: "בינלאומי", False: 'ארה"ב'})
ref["source_type"] = ref.source.str.contains("ISSN").map({True: "עמדת איגוד מקצועי", False: "מסמך רשמי"})
parts = [ref[COLS]]

# 2. קבצי העובדות הנוספים
for p in sorted((DATA / "research_sources").glob("*.csv")):
    d = pd.read_csv(p, encoding="utf-8-sig")
    missing = set(COLS) - set(d.columns)
    assert not missing, f"{p.name}: חסרות עמודות {missing}"
    parts.append(d[COLS])

df = pd.concat(parts, ignore_index=True)
for c in COLS:
    df[c] = df[c].fillna("").astype(str).str.strip()

# שמות שונים לאותו תוסף -> השם שבטבלת התזמון
SAME_AS = {"ויטמין D": "ויטמין D3", "ויטמין K": "ויטמין K2", "אומגה 3": "אומגה 3 (שמן דגים)",
           "אשוואגנדה": "אשווגנדה", "חלבון": "אבקת חלבון", "תוסף Q10": "קואנזים Q10",
           "ויטמין B1 (תיאמין)": "B קומפלקס", "ניאצין (B3)": "B קומפלקס"}
df["supplement_he"] = df.supplement_he.replace(SAME_AS)
# תוספי ספורט ומינרלים שאינם בין 40 התוספים של האפליקציה (מדף התוספים לספורטאים של NIH ODS).
# נשארים בטבלה כמידע רקע.
EXTRA = {"בטא-אלנין", "כולין", "מיץ סלק (ניטרט)", "סודיום ביקרבונט", "קפאין", "קרניטין", "נחושת"}

# 3. ניקוי: בלי שורות ריקות, בלי כפילויות, ורק תוספים שמופיעים בטבלת התזמון (או "כללי")
before = len(df)
df = df[(df.fact_he != "") & (df.url.str.startswith("http"))]
df = df.drop_duplicates(subset=["supplement_he", "fact_he"])  # אותה עובדה בדיוק על אותו תוסף
known = set(pd.read_csv(DATA / "timing_rules.csv", encoding="utf-8-sig").supplement_he) | {"כללי"} | EXTRA
unknown = sorted(set(df.supplement_he) - known)
assert not unknown, f"שמות תוספים שלא קיימים בטבלת התזמון: {unknown}"

df = df.sort_values(["supplement_he", "country", "topic"]).reset_index(drop=True)
df.insert(0, "id", range(1, len(df) + 1))
assert len(df) >= 300, f"רק {len(df)} שורות; נדרשות 300 לפחות"
df.to_csv(DATA / "supplement_research.csv", index=False, encoding="utf-8-sig")

print(f"טבלת מחקרים: {before} שורות לפני ניקוי -> {len(df)} שורות, {df.supplement_he.nunique()} תוספים")
print(df.country.value_counts().to_string())
