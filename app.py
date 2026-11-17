"""דשבורד EDA: תוספי תזונה ורמת ויטמין D בדם (NHANES 2017-2018).
הרצה: streamlit run app.py
"""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="תוספי תזונה וויטמין D", page_icon=None, layout="wide")

DATA = Path(__file__).resolve().parent / "data" / "nhanes_supplements_vitd_clean.csv"
LOW_CUTOFF = 50  # nmol/L, לפי NIH ODS: מתחת ל-50 הרמה לא מספקת

st.markdown(
    """<style>
    .block-container {direction: rtl; text-align: right;}
    [data-testid="stSidebar"] {direction: rtl; text-align: right;}
    [data-testid="stMetric"] {direction: rtl; text-align: right;}
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_data
def load() -> pd.DataFrame:
    return pd.read_csv(DATA)


df = load()

# ---------------------------------------------------------------- סינון (sidebar)
st.sidebar.header("סינון")
age_lo, age_hi = st.sidebar.slider("טווח גילאים", int(df.age_years.min()), int(df.age_years.max()),
                                   (int(df.age_years.min()), int(df.age_years.max())))
sex_map = {"male": "גברים", "female": "נשים"}
sexes = st.sidebar.multiselect("מין", list(sex_map), default=list(sex_map), format_func=sex_map.get)
races = sorted(df.race_ethnicity.unique())
chosen_races = st.sidebar.multiselect("מוצא (קטגוריות NHANES)", races, default=races)
st.sidebar.caption("הפילטרים משנים את כל המדדים, הגרפים והטבלה.")

f = df[df.age_years.between(age_lo, age_hi) & df.sex.isin(sexes) & df.race_ethnicity.isin(chosen_races)]
if len(f) < 30:
    st.warning("הסינון הותיר פחות מ-30 נבדקים, ולכן אי אפשר להציג תוצאות. הרחיבי את הסינון בצד.")
    st.stop()

# ---------------------------------------------------------------- חישובים
bins = [-1, 0, 10, 25, 50, 10_000]
labels = ["ללא", "1–10", "10–25", "25–50", "50+"]
f = f.assign(dose_group=pd.cut(f.supp_vitd_mcg, bins, labels=labels))
by_dose = (f.groupby("dose_group", observed=True)
             .agg(n=("seqn", "size"), low_pct=("vitd_low", "mean"), mean_vitd=("vitd_nmol_l", "mean"))
             .reset_index())
by_dose["low_pct"] *= 100

none_row = by_dose[by_dose.dose_group == "ללא"]
top_rows = by_dose[(by_dose.dose_group != "ללא") & (by_dose.n >= 30)]

# ---------------------------------------------------------------- כותרת ותובנה
st.title("תוספי תזונה ורמת ויטמין D בדם")
st.caption("נתוני NHANES 2017–2018 (CDC), מבוגרים בארה\"ב. 5,068 נבדקים לפני סינון.")

if not none_row.empty and not top_rows.empty and none_row.n.iloc[0] >= 30:
    best = top_rows.sort_values("low_pct").iloc[0]
    st.info(
        f"**גילינו ש**{none_row.low_pct.iloc[0]:.0f}% מהנבדקים שלא נוטלים ויטמין D מתוספים נמצאים ברמה נמוכה "
        f"(מתחת ל-{LOW_CUTOFF} nmol/L), לעומת {best.low_pct:.0f}% בקרב מי שנוטלים {best.dose_group} מק\"ג ביום. "
        "כלומר, נטילת תוסף ויטמין D קשורה לרמה גבוהה יותר בדם. הנתונים מראים קשר ולא סיבתיות, "
        "ומי שנוטל תוסף עשוי להיות שונה גם בהרגלים אחרים."
    )
else:
    st.info("**גילינו ש**נטילת תוסף ויטמין D קשורה לרמה גבוהה יותר בדם. הרחיבי את הסינון כדי לראות מספרים.")

# ---------------------------------------------------------------- מדדים
low_rate = f.vitd_low.mean() * 100
overall_low = df.vitd_low.mean() * 100
c1, c2, c3, c4 = st.columns(4)
c1.metric("מספר נבדקים (אחרי סינון)", f"{len(f):,}")
c2.metric("ממוצע ויטמין D בדם (nmol/L)", f"{f.vitd_nmol_l.mean():.1f}")
c3.metric("KPI: אחוז עם רמה נמוכה (<50)", f"{low_rate:.1f}%", delta=f"{low_rate - overall_low:+.1f} נק' מכלל הנבדקים",
          delta_color="inverse")
c4.metric("אחוז הנוטלים תוסף כלשהו", f"{f.takes_supplement.mean() * 100:.1f}%")

# baseline: החיזוי הכי פשוט שאפשר
med = f.vitd_nmol_l.median()
mae = (f.vitd_nmol_l - med).abs().mean()
majority_acc = max(f.vitd_low.mean(), 1 - f.vitd_low.mean()) * 100
st.subheader("Baseline: מה המודל הראשון צריך לנצח")
b1, b2, b3 = st.columns(3)
b1.metric("Baseline רגרסיה: חיזוי החציון (nmol/L)", f"{med:.1f}")
b2.metric("שגיאה ממוצעת של ה-baseline (MAE, nmol/L)", f"{mae:.1f}")
b3.metric("Baseline סיווג: דיוק של 'תמיד הקטגוריה הנפוצה'", f"{majority_acc:.1f}%")
st.caption("מודל שיחזה רמת ויטמין D צריך להגיע לשגיאה נמוכה מה-MAE הזה, ולדיוק גבוה מהאחוז האחרון.")

# ---------------------------------------------------------------- גרפים
st.subheader("גרפים")
g1, g2 = st.columns(2)

with g1:
    st.markdown("**כמה ויטמין D מתוסף ביום וכמה נמצאים ברמה נמוכה**")
    ch = (alt.Chart(by_dose).mark_bar(color="#2f6f8f")
          .encode(x=alt.X("dose_group:N", sort=labels, title="מינון ויטמין D מתוספים (מק\"ג ביום)", axis=alt.Axis(labelAngle=0)),
                  y=alt.Y("low_pct:Q", title="% עם רמה נמוכה (<50 nmol/L)"),
                  tooltip=[alt.Tooltip("dose_group:N", title="מינון"), alt.Tooltip("n:Q", title="נבדקים"),
                           alt.Tooltip("low_pct:Q", title="% נמוך", format=".1f"),
                           alt.Tooltip("mean_vitd:Q", title="ממוצע nmol/L", format=".1f")])
          .properties(height=330))
    st.altair_chart(ch, width="stretch")

with g2:
    st.markdown("**התפלגות רמת ויטמין D: נוטלי תוסף מול לא נוטלים**")
    hist = f.assign(group=np.where(f.takes_supplement == 1, "נוטלים תוסף", "לא נוטלים"))
    hch = (alt.Chart(hist).mark_bar(opacity=0.65)
           .encode(x=alt.X("vitd_nmol_l:Q", bin=alt.Bin(maxbins=30), title="ויטמין D בדם (nmol/L)"),
                   y=alt.Y("count():Q", stack=None, title="מספר נבדקים"),
                   color=alt.Color("group:N", title="", scale=alt.Scale(domain=["נוטלים תוסף", "לא נוטלים"],
                                                                         range=["#2f6f8f", "#c9863a"])))
           .properties(height=330))
    rule = alt.Chart(pd.DataFrame({"x": [LOW_CUTOFF]})).mark_rule(color="red", strokeDash=[5, 4]).encode(x="x:Q")
    st.altair_chart(hch + rule, width="stretch")
    st.caption("הקו האדום הוא סף 50 nmol/L. משמאלו הרמה לא מספקת.")

st.markdown("**ממוצע ויטמין D בדם: נוטלים מול לא נוטלים, לפי סוג התוסף**")
types = {"פרוביוטיקה": "takes_probiotic", "שמן דגים/אומגה 3": "takes_fish_oil", "מולטי-ויטמין": "takes_multivitamin",
         "ויטמין C": "supp_vitc_mg", "מגנזיום": "supp_magnesium_mg", "ברזל": "supp_iron_mg", "אבץ": "supp_zinc_mg",
         "B12": "supp_b12_mcg", "סידן": "supp_calcium_mg"}
rows = []
for name, col in types.items():
    takes = f[col] > 0
    for flag, lab in ((True, "נוטלים"), (False, "לא נוטלים")):
        sub = f[takes == flag]
        if len(sub) >= 20:
            rows.append({"תוסף": name, "קבוצה": lab, "ממוצע": sub.vitd_nmol_l.mean(), "n": len(sub)})
tdf = pd.DataFrame(rows)
if not tdf.empty:
    tch = (alt.Chart(tdf).mark_bar()
           .encode(y=alt.Y("תוסף:N", title="", sort=list(types), axis=alt.Axis(orient="right", labelLimit=220, labelPadding=8)), yOffset="קבוצה:N",
                   x=alt.X("ממוצע:Q", title="ממוצע ויטמין D (nmol/L)"),
                   color=alt.Color("קבוצה:N", title="", scale=alt.Scale(domain=["נוטלים", "לא נוטלים"], range=["#2f6f8f", "#c9863a"])),
                   tooltip=["תוסף", "קבוצה", alt.Tooltip("ממוצע:Q", format=".1f"), "n"])
           .properties(height=420))
    st.altair_chart(tch, width="stretch")
st.caption("קריאטין ואבקת חלבון לא מוצגים: יש בנתונים רק 11 ו-16 נבדקים כאלה. נוטלי מוצרים עם ויטמין D "
           "(למשל מולטי-ויטמין) מקבלים ויטמין D גם ממנו, ולכן הגרף מראה קשר ולא סיבתיות.")

# ---------------------------------------------------------------- טבלה
st.subheader("דוגמה מהנתונים הנקיים")
show = f.drop(columns=["dose_group"]).sample(min(25, len(f)), random_state=1)
st.dataframe(show, width="stretch", hide_index=True)
st.caption("אין עמודות מיקום בנתונים, ולכן אין מפה. לפירוט הניקוי והמגבלות: README ו-docs/DATA_CARD_he.md.")
