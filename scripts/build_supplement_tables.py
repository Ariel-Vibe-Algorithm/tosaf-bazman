"""בונה טבלאות על תוספים נפוצים מתוך NHANES 2017-2018, לאותם 5,068 מבוגרים שבקובץ הנקי.
הרצה: python scripts/build_supplement_tables.py  (אחרי clean_data.py)
פלט: data/supplement_intake_by_person.csv  ו-  data/supplement_prevalence.csv
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, DATA = ROOT / "data" / "raw", ROOT / "data"

# עמודה ב-DSQTOT_J: (שם בעברית, שם קצר באנגלית, יחידה)
NUTRIENTS = {
    "DSQTVD": ("ויטמין D", "vitd", "מק\"ג"),
    "DSQTVC": ("ויטמין C", "vitc", "מ\"ג"),
    "DSQTVB12": ("ויטמין B12", "b12", "מק\"ג"),
    "DSQTVB6": ("ויטמין B6", "b6", "מ\"ג"),
    "DSQTFA": ("חומצה פולית", "folic_acid", "מק\"ג"),
    "DSQTVB1": ("ויטמין B1 (תיאמין)", "b1", "מ\"ג"),
    "DSQTVB2": ("ויטמין B2 (ריבופלבין)", "b2", "מ\"ג"),
    "DSQTNIAC": ("ניאצין (B3)", "niacin", "מ\"ג"),
    "DSQTVK": ("ויטמין K", "vitk", "מק\"ג"),
    "DSQTCALC": ("סידן", "calcium", "מ\"ג"),
    "DSQTMAGN": ("מגנזיום", "magnesium", "מ\"ג"),
    "DSQTIRON": ("ברזל", "iron", "מ\"ג"),
    "DSQTZINC": ("אבץ", "zinc", "מ\"ג"),
    "DSQTCOPP": ("נחושת", "copper", "מ\"ג"),
    "DSQTSELE": ("סלניום", "selenium", "מק\"ג"),
    "DSQTIODI": ("יוד", "iodine", "מק\"ג"),
}

clean = pd.read_csv(DATA / "nhanes_supplements_vitd_clean.csv", usecols=["seqn"])
tot = pd.read_sas(RAW / "DSQTOT_J.xpt", format="xport", encoding=None)
tot["seqn"] = tot.SEQN.astype(int)
tot = clean.merge(tot, on="seqn", how="left")
assert len(tot) == len(clean) and tot.DSQTVD.notna().sum() > 0

per = tot[["seqn"]].copy()
rows = []
for col, (he, en, unit) in NUTRIENTS.items():
    s = tot[col].fillna(0).round(2)
    per[f"dose_{en}"] = s
    users = s[s > 0]
    rows.append({"nutrient_he": he, "nutrient_en": en, "unit": unit, "users_n": len(users),
                 "users_pct": round(100 * len(users) / len(per), 1),
                 "median_daily_dose_among_users": round(users.median(), 1) if len(users) else 0,
                 "p90_daily_dose_among_users": round(users.quantile(0.9), 1) if len(users) else 0})
per.to_csv(DATA / "supplement_intake_by_person.csv", index=False, encoding="utf-8")
prev = pd.DataFrame(rows).sort_values("users_pct", ascending=False)
prev.to_csv(DATA / "supplement_prevalence.csv", index=False, encoding="utf-8-sig")
print(prev[["nutrient_he", "users_n", "users_pct", "median_daily_dose_among_users", "unit"]].to_string(index=False))
