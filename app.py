"""דשבורד EDA של "תוסף בזמן": תזמון ומינון של 40 תוספים, ורמות ויטמין D וברזל בדם.
הרצה: streamlit run app.py
"""
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="תוסף בזמן: דשבורד", layout="wide")

DATA = Path(__file__).resolve().parent / "data"
LOW_VITD = 50  # nmol/L, NIH ODS: מתחת ל-50 הרמה לא מספקת
LOW_FERRITIN = 15  # ng/mL, WHO 2020: מתחת ל-15 = מאגרי ברזל נמוכים במבוגרים בריאים
BLUE, ORANGE, GREEN, GREY = "#2f6f8f", "#c9863a", "#4f8a4b", "#9aa5ad"

# כיווניות מימין לשמאל לעברית
st.markdown(
    """<style>
    .block-container {direction: rtl; text-align: right;}
    [data-testid="stSidebar"] {direction: rtl; text-align: right;}
    [data-testid="stMetric"] {direction: rtl; text-align: right;}
    /* בתוך הגרפים משאירים כיוון רגיל, אחרת התוויות עולות על העמודות */
    [data-testid="stVegaLiteChart"] {direction: ltr;}
    </style>""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- טעינת נתונים
@st.cache_data
def load_people() -> pd.DataFrame:
    return pd.read_csv(DATA / "nhanes_supplements_vitd_clean.csv")


@st.cache_data
def load_intake() -> pd.DataFrame:
    return pd.read_csv(DATA / "supplement_intake_by_person.csv")


@st.cache_data
def load_rules() -> pd.DataFrame:
    return pd.read_csv(DATA / "timing_rules.csv", encoding="utf-8-sig")


@st.cache_data
def load_research() -> pd.DataFrame:
    return pd.read_csv(DATA / "supplement_research.csv", encoding="utf-8-sig").fillna("")


people, rules, research = load_people(), load_rules(), load_research()

# ---------------------------------------------------------------- כותרת ותובנה מרכזית
st.title("תוסף בזמן: תזמון, מינון ורמות בדם")
st.caption(
    f"{len(rules)} תוספים · {len(research):,} עובדות ממחקרים ומסמכים רשמיים, כל אחת עם מקור · "
    f"{len(people):,} מבוגרים עם בדיקות דם (NHANES, שני סבבים: 2017–2018 ו-2021–2023). כלי לימודי, לא ייעוץ רפואי."
)

none_d = people[people.supp_vitd_mcg == 0].vitd_low.mean() * 100
some_d = people[(people.supp_vitd_mcg > 10) & (people.supp_vitd_mcg <= 25)].vitd_low.mean() * 100
n_sep_all = rules.separate_from.notna().sum()
st.info(
    f"גילינו ש-{none_d:.0f}% ממי שלא לוקחים ויטמין D מתוסף נמצאים ברמה נמוכה בדם, לעומת {some_d:.0f}% "
    f"בקרב מי שלוקחים 10 עד 25 מק\"ג ביום. בנוסף, {n_sep_all} מתוך {len(rules)} התוספים צריכים הפרדה של "
    "שעתיים לפחות מתוסף אחר. למשתמש זה אומר: לבדוק רמה בדם לפני שקונים תוסף, ולא לקחת את כל התוספים "
    "יחד בבוקר. הנתונים מראים קשר ולא סיבתיות.",
    title="התובנה המרכזית",
)

view = st.segmented_control(
    "מה להציג", ["תזמון ומינון: כל התוספים", "רמות בדם: ויטמין D וברזל"],
    default="תזמון ומינון: כל התוספים", key="view",
) or "תזמון ומינון: כל התוספים"

# ================================================================= תצוגה 1: תזמון ומינון
if view.startswith("תזמון"):
    with st.sidebar:
        st.header("סינון")
        cats = sorted(rules.category.unique())
        chosen_cats = st.multiselect("סוג תוסף", cats, default=cats)
        confs = ["מבוסס", "חלקי", "מקובל"]
        chosen_conf = st.pills("רמת ביטחון בכלל התזמון", confs, selection_mode="multi", default=confs)
        countries = sorted(research.country.unique())
        chosen_countries = st.pills("מאיפה המקור", countries, selection_mode="multi", default=countries)
        st.caption("הפילטרים משנים את כל המדדים, הגרפים והטבלאות בתצוגה הזו.")

    rf = rules[rules.category.isin(chosen_cats) & rules.confidence.isin(chosen_conf)]
    res_f = research[research.supplement_he.isin(rf.supplement_he) & research.country.isin(chosen_countries)]
    if rf.empty:
        st.warning("אין תוספים שמתאימים לסינון. הרחיבי את הסינון בצד.")
        st.stop()

    n_sep = rf.separate_from.notna().sum()
    n_avoid = rf.avoid_food_drinks.notna().sum()
    n_il = (res_f.country == "ישראל").sum()

    with st.container(horizontal=True):
        st.metric("תוספים בתצוגה", len(rf), border=True)
        st.metric("KPI: צריכים הפרדה מתוסף אחר", f"{100 * n_sep / len(rf):.0f}%", border=True,
                  help="אחוז התוספים שצריך להרחיק מתוסף אחר בשעתיים לפחות. זה הדבר הראשון שהמשתמש בודק: מה אסור לקחת יחד.")
        n_extra = (~research.supplement_he.isin(rules.supplement_he)).sum()
        extra_note = (f"סופרים רק עובדות על התוספים שבתצוגה. בטבלה יש עוד {n_extra} עובדות רקע על תוספים "
                      "שאינם בין ה-40 (למשל קפאין ובטא-אלנין), והן לא נספרות כאן.")
        st.metric("עובדות ממחקרים (עם מקור)", f"{len(res_f):,}", border=True, help=extra_note)
        st.metric("עובדות ממקורות ישראליים", f"{n_il:,}", border=True, help=extra_note)

    st.markdown(
        f"**בתצוגה הזו:** {n_sep} מתוך {len(rf)} תוספים צריכים הפרדה מתוסף אחר, ו-{n_avoid} צריכים להתרחק "
        "ממזון או שתייה מסוימים (למשל קפה, תה או חלב)."
    )

    # ----- גרפים
    g1, g2 = st.columns(2)
    with g1:
        with st.container(border=True):
            st.markdown("**מתי ביום מומלץ לקחת**")
            slots = {"בוקר": "בוקר", "צהריים": "צהריים", "ערב": "ערב", "לפני השינה": "שינה",
                     "עם ארוחה": "ארוחה", "סביב אימון": "אימון", "לאורך היום / לא משנה": "לאורך היום|באותה שעה"}
            slot_rows = [{"זמן": s, "תוספים": rf.best_time.str.contains(p, regex=True).sum()} for s, p in slots.items()]
            sdf = pd.DataFrame(slot_rows)
            ch = (alt.Chart(sdf).mark_bar(color=BLUE)
                  .encode(x=alt.X("זמן:N", sort=list(slots), title="",
                                  axis=alt.Axis(labelAngle=-30, labelOverlap=False, labelLimit=160)),
                          y=alt.Y("תוספים:Q", title="מספר תוספים"), tooltip=["זמן", "תוספים"])
                  .properties(height=320))
            st.altair_chart(ch, alt="מספר התוספים לפי זמן הנטילה המומלץ, הכי הרבה בבוקר ועם ארוחה")
            st.caption("תוסף אחד יכול להתאים ליותר מזמן אחד. מקור: data/timing_rules.csv")

    with g2:
        with st.container(border=True):
            st.markdown("**ממה צריך להפריד, ובכמה דקות**")
            pairs = []
            for _, r in rf[rf.separate_from.notna()].iterrows():
                for part in str(r.separate_from).split(";"):
                    if ":" in part:
                        other, mins = part.rsplit(":", 1)
                        pairs.append({"תוסף": r.supplement_he, "להפריד מ": other.strip(), "דקות": int(mins)})
            pdf = pd.DataFrame(pairs)
            if pdf.empty:
                st.caption("אין הפרדות בין התוספים שבתצוגה.")
            else:
                hm = (alt.Chart(pdf).mark_rect(color=ORANGE)
                      .encode(x=alt.X("להפריד מ:N", title="", axis=alt.Axis(labelAngle=-40, labelOverlap=False)),
                              y=alt.Y("תוסף:N", title="", axis=alt.Axis(orient="right", labelLimit=220)),
                              opacity=alt.value(0.85), tooltip=["תוסף", "להפריד מ", "דקות"])
                      .properties(height=320))
                st.altair_chart(hm, alt="מפת הפרדות: ברזל, סידן, אבץ ומגנזיום צריכים שעתיים בינם לבין עצמם")
                st.caption("כל משבצת היא זוג שצריך שעתיים (120 דקות) בין המנות. ההפרדה חלה לשני הכיוונים.")

    g3, g4 = st.columns(2)
    with g3:
        with st.container(border=True):
            st.markdown("**כמה עובדות מחקריות יש לכל תוסף, ומאיפה**")
            cnt = res_f.groupby(["supplement_he", "country"]).size().reset_index(name="עובדות")
            bar = (alt.Chart(cnt).mark_bar()
                   .encode(y=alt.Y("supplement_he:N", sort="-x", title="",
                                   axis=alt.Axis(orient="right", labelLimit=220, labelOverlap=False)),
                           x=alt.X("sum(עובדות):Q", title="מספר עובדות עם מקור"),
                           color=alt.Color("country:N", title="מקור",
                                           scale=alt.Scale(domain=["ישראל", "ארה\"ב", "בינלאומי"],
                                                           range=[GREEN, BLUE, ORANGE])),
                           tooltip=["supplement_he", "country", "עובדות"])
                   .properties(height=max(300, 22 * cnt.supplement_he.nunique())))
            st.altair_chart(bar, alt="מספר העובדות המחקריות לכל תוסף, לפי ארץ המקור")

    with g4:
        with st.container(border=True):
            st.markdown("**כמה כל כלל תזמון מבוסס, לפי סוג תוסף**")
            conf = rf.groupby(["category", "confidence"]).size().reset_index(name="תוספים")
            cb = (alt.Chart(conf).mark_bar()
                  .encode(y=alt.Y("category:N", title="", axis=alt.Axis(orient="right")),
                          x=alt.X("תוספים:Q", title="מספר תוספים"),
                          color=alt.Color("confidence:N", title="רמת ביטחון",
                                          scale=alt.Scale(domain=confs, range=[GREEN, ORANGE, GREY])),
                          tooltip=["category", "confidence", "תוספים"])
                  .properties(height=320))
            st.altair_chart(cb, alt="רמת הביטחון של כללי התזמון לפי סוג התוסף")
            st.caption("מבוסס = כתוב במקור רשמי. חלקי = חלק מהכלל מהמקור וחלק נוהג מקובל. מקובל = נוהג מקובל בלבד.")

    # ----- כרטיס לתוסף בודד
    st.subheader("כרטיס תוסף")
    pick = st.selectbox("בחרי תוסף", rf.supplement_he.tolist())
    r = rf[rf.supplement_he == pick].iloc[0]

    def val(x) -> str:
        return "—" if pd.isna(x) or str(x).strip() == "" else str(x)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**מתי לקחת:** {val(r.best_time)}  \n**עם אוכל?** {val(r.with_food)}")
        c2.markdown(f"**מנות ביום:** {val(r.doses_per_day)} (המנה הבאה אחרי {val(r.next_dose_after_hours)} שעות)  \n"
                    f"**אפשר לפצל?** {val(r.can_split)}")
        c3.markdown(f"**רמת ביטחון:** {val(r.confidence)}  \n{val(r.confidence_note)}")
        sep_txt = "; ".join(f"{p.rsplit(':', 1)[0].strip()} ({p.rsplit(':', 1)[1]} דקות)"
                            for p in str(r.separate_from).split(";") if ":" in p) if pd.notna(r.separate_from) else "—"
        st.markdown(f"**להפריד מ:** {sep_txt}  \n**להתרחק מ:** {val(r.avoid_food_drinks)}  \n"
                    f"**תרופות:** {val(r.drug_interactions)} ({val(r.drug_gap)})  \n"
                    f"**משתלב טוב עם:** {val(r.works_well_with)}  \n**זהירות:** {val(r.caution)}")
    mine = res_f[res_f.supplement_he == pick][["topic", "fact_he", "value", "country", "source", "url"]]
    st.dataframe(
        mine, hide_index=True, alt=f"עובדות מחקריות על {pick}",
        column_config={"topic": "נושא", "fact_he": "העובדה", "value": "ערך", "country": "ארץ", "source": "מקור",
                       "url": st.column_config.LinkColumn("קישור", display_text="פתיחה")},
    )

    # ----- טבלת המחקרים המלאה (מסוננת)
    st.subheader("טבלת המחקרים (לפי הסינון)")
    st.dataframe(
        res_f[["supplement_he", "topic", "fact_he", "value", "country", "source_type", "source", "url"]],
        hide_index=True, alt="כל העובדות המחקריות לפי הסינון",
        column_config={"supplement_he": "תוסף", "topic": "נושא", "fact_he": "העובדה", "value": "ערך",
                       "country": "ארץ", "source_type": "סוג מקור", "source": "מקור",
                       "url": st.column_config.LinkColumn("קישור", display_text="פתיחה")},
    )
    st.caption("מינונים בטבלה הם ערכים כלליים מהמחקר, לא הוראת מינון אישית. לפני שמתחילים תוסף, בעיקר עם תרופות, "
               "כדאי להתייעץ עם רופא, רוקח או דיאטנית.")

# ================================================================= תצוגה 2: רמות בדם
else:
    with st.sidebar:
        st.header("סינון")
        cycles = sorted(people.cycle.unique())
        chosen_cycles = st.pills("סבב הסקר", cycles, selection_mode="multi", default=cycles,
                                 help="2017–2018 ו-2021–2023. בסבב החדש ה-CDC לא דגם יותר אנשים מקבוצות מוצא מסוימות, "
                                      "כמו שעשה בסבב הקודם, ולכן ההרכב שונה. ההבדל בין הסבבים הוא קשר ולא בהכרח שינוי אמיתי.")
        age_lo, age_hi = st.slider("טווח גילאים", int(people.age_years.min()), int(people.age_years.max()),
                                   (int(people.age_years.min()), int(people.age_years.max())))
        sex_map = {"female": "נשים", "male": "גברים"}
        sexes = st.pills("מין", list(sex_map), selection_mode="multi", default=list(sex_map), format_func=sex_map.get)
        races = sorted(people.race_ethnicity.unique())
        chosen_races = st.multiselect("מוצא (קטגוריות NHANES)", races, default=races)
        season_map = {"Nov-Apr": "נובמבר–אפריל", "May-Oct": "מאי–אוקטובר"}
        seasons = st.pills("עונת הבדיקה", list(season_map), selection_mode="multi", default=list(season_map),
                           format_func=season_map.get)
        st.caption("הפילטרים משנים את כל המדדים, הגרפים והטבלה בתצוגה הזו.")

    f = people[people.cycle.isin(chosen_cycles) & people.age_years.between(age_lo, age_hi) & people.sex.isin(sexes)
               & people.race_ethnicity.isin(chosen_races) & people.exam_season.isin(seasons)]
    if len(f) < 30:
        st.warning("הסינון השאיר פחות מ-30 נבדקים, ולכן אי אפשר להציג תוצאות. הרחיבי את הסינון בצד.")
        st.stop()

    target = st.segmented_control("משתנה היעד (y)", ["ויטמין D", "ברזל (פריטין)"], default="ויטמין D",
                                  key="target") or "ויטמין D"
    is_d = target == "ויטמין D"

    if is_d:
        bins, labels = [-1, 0, 10, 25, 50, 10_000], ["ללא", "1 עד 10", "10 עד 25", "25 עד 50", "50 ומעלה"]
        f = f.assign(dose_group=pd.cut(f.supp_vitd_mcg, bins, labels=labels))
        by_dose = (f.groupby("dose_group", observed=True)
                   .agg(n=("seqn", "size"), low_pct=("vitd_low", "mean"), mean_y=("vitd_nmol_l", "mean")).reset_index())
        by_dose["low_pct"] *= 100
        none_row = by_dose[by_dose.dose_group == "ללא"]
        top = by_dose[(by_dose.dose_group != "ללא") & (by_dose.n >= 30)]
        if not none_row.empty and not top.empty and none_row.n.iloc[0] >= 30:
            best = top.sort_values("low_pct").iloc[0]
            st.info(f"גילינו ש-{none_row.low_pct.iloc[0]:.0f}% מהנבדקים שלא לוקחים ויטמין D מתוסף נמצאים ברמה נמוכה "
                    f"(מתחת ל-{LOW_VITD} nmol/L), לעומת {best.low_pct:.0f}% בקרב מי שלוקחים {best.dose_group} מק\"ג ביום. "
                    "זה קשר ולא סיבתיות: מי שלוקח תוסף עשוי להיות שונה גם בהרגלים אחרים.", title="תובנה: ויטמין D")
        y, low, unit = f.vitd_nmol_l, f.vitd_low, "nmol/L"
        overall = people.vitd_low.mean() * 100
        with st.container(horizontal=True):
            st.metric("נבדקים אחרי סינון", f"{len(f):,}", border=True)
            st.metric("ממוצע ויטמין D בדם (nmol/L)", f"{y.mean():.1f}", border=True)
            st.metric("KPI: אחוז עם רמה נמוכה (<50)", f"{low.mean() * 100:.1f}%", border=True,
                      delta=f"{low.mean() * 100 - overall:+.1f} נק' מכלל הנבדקים", delta_color="inverse")
            st.metric("לוקחים תוסף ויטמין D", f"{(f.supp_vitd_mcg > 0).mean() * 100:.1f}%", border=True)
    else:
        # פריטין נמדד רק אצל חלק מהנבדקים (ב-2021–2023 רק לנשים בגילאי 18–49), ולכן ניתוחי הברזל רק עליהם
        f = f[f.iron_low.notna()]
        if len(f) < 30:
            st.warning("בסינון הזה יש פחות מ-30 נבדקים שנמדד להם פריטין. הרחיבי את הסינון בצד.")
            st.stop()
        st.caption(f"ניתוחי הברזל כוללים רק את {len(f):,} הנבדקים שנמדד להם פריטין. ב-2021–2023 ה-CDC מדד פריטין "
                   "רק לנשים בגילאי 18–49, ולכן גברים ונשים מבוגרות מגיעים רק מ-2017–2018.")
        female, male = f[f.sex == "female"], f[f.sex == "male"]
        f = f.assign(age_group=pd.cut(f.age_years, [17, 30, 50, 80], labels=["18–30", "31–50", "51–80"]))
        if len(female) >= 30 and len(male) >= 30 and male.iron_low.mean() > 0:
            st.info(f"גילינו שמאגרי ברזל נמוכים (פריטין מתחת ל-{LOW_FERRITIN} ng/mL) נפוצים אצל נשים פי "
                    f"{female.iron_low.mean() / male.iron_low.mean():.0f} בערך מאשר אצל גברים "
                    f"({female.iron_low.mean() * 100:.1f}% לעומת {male.iron_low.mean() * 100:.1f}%), "
                    "ובעיקר בגילאי 18 עד 50. למשתמשת זה אומר: לנשים בגיל הפוריות כדאי לבדוק פריטין.",
                    title="תובנה: ברזל")
        y, low, unit = f.ferritin_ng_ml, f.iron_low, "ng/mL"
        overall = people.iron_low.mean() * 100
        with st.container(horizontal=True):
            st.metric("נבדקים אחרי סינון", f"{len(f):,}", border=True)
            st.metric("חציון פריטין (ng/mL)", f"{y.median():.1f}", border=True)
            st.metric("KPI: אחוז עם מאגרי ברזל נמוכים (<15)", f"{low.mean() * 100:.1f}%", border=True,
                      delta=f"{low.mean() * 100 - overall:+.1f} נק' מכלל הנבדקים", delta_color="inverse")
            st.metric("לוקחים תוסף עם ברזל", f"{(f.supp_iron_mg > 0).mean() * 100:.1f}%", border=True)

    # ----- baseline
    st.subheader(f"Baseline: מה המודל ב-M3 צריך לנצח ({target})")
    med = y.median()
    mae = (y - med).abs().mean()
    acc = max(low.mean(), 1 - low.mean()) * 100
    with st.container(horizontal=True):
        st.metric(f"רגרסיה: תמיד לחזות את החציון ({unit})", f"{med:.1f}", border=True)
        st.metric(f"השגיאה הממוצעת של זה (MAE, {unit})", f"{mae:.1f}", border=True)
        st.metric("סיווג: דיוק של 'תמיד לא נמוך'", f"{acc:.1f}%", border=True)
    if is_d:
        st.caption("מודל שיחזה רמת ויטמין D צריך שגיאה נמוכה מה-MAE הזה, ודיוק גבוה מהאחוז האחרון.")
    else:
        st.caption("בברזל רק מעטים נמוכים, ולכן 'תמיד לא נמוך' מקבל דיוק גבוה בלי למצוא אף אחד. "
                   "ב-M3 נמדוד גם כמה מהנמוכים המודל מוצא (recall). הפריטין נחתך באחוזון 99, ולכן ה-y לברזל הוא "
                   "הסיווג iron_low ולא הרגרסיה.")

    # ----- גרפים
    g1, g2 = st.columns(2)
    if is_d:
        with g1:
            with st.container(border=True):
                st.markdown("**מינון ויטמין D מתוסף מול אחוז הרמה הנמוכה**")
                ch = (alt.Chart(by_dose).mark_bar(color=BLUE)
                      .encode(x=alt.X("dose_group:N", sort=labels, title="מק\"ג ביום מתוספים", axis=alt.Axis(labelAngle=0)),
                              y=alt.Y("low_pct:Q", title="% עם רמה נמוכה (<50 nmol/L)"),
                              tooltip=[alt.Tooltip("dose_group:N", title="מינון"), alt.Tooltip("n:Q", title="נבדקים"),
                                       alt.Tooltip("low_pct:Q", title="% נמוך", format=".1f")])
                      .properties(height=320))
                st.altair_chart(ch, alt="ככל שמינון ויטמין D מתוספים גבוה יותר, פחות נבדקים ברמה נמוכה")
        with g2:
            with st.container(border=True):
                st.markdown("**רמה נמוכה לפי עונת הבדיקה ומין**")
                ss = (f.assign(עונה=f.exam_season.map(season_map), מין=f.sex.map(sex_map))
                      .groupby(["עונה", "מין"]).vitd_low.mean().mul(100).reset_index(name="% נמוך"))
                sc = (alt.Chart(ss).mark_bar()
                      .encode(x=alt.X("עונה:N", title="", axis=alt.Axis(labelAngle=0)), xOffset="מין:N",
                              y=alt.Y("% נמוך:Q", title="% עם רמה נמוכה"),
                              color=alt.Color("מין:N", title="", scale=alt.Scale(range=[ORANGE, BLUE])),
                              tooltip=["עונה", "מין", alt.Tooltip("% נמוך:Q", format=".1f")])
                      .properties(height=320))
                st.altair_chart(sc, alt="בחורף יותר נבדקים ברמת ויטמין D נמוכה מאשר בקיץ")
                st.caption("בישראל החורף שמשי יותר, ולכן כדאי להשוות לעובדות הישראליות שבחלק 'מה ידוע על ישראל'.")
        with st.container(border=True):
            st.markdown("**השוואה בין סבבי הסקר: 2017–2018 מול 2021–2023**")
            cyc = (f.groupby("cycle")
                   .agg(**{"% עם רמה נמוכה": ("vitd_low", "mean"),
                           "% לוקחים תוסף ויטמין D": ("supp_vitd_mcg", lambda s: (s > 0).mean())})
                   .mul(100).reset_index().melt("cycle", var_name="מדד", value_name="אחוז"))
            cc = (alt.Chart(cyc).mark_bar()
                  .encode(x=alt.X("מדד:N", title="", axis=alt.Axis(labelAngle=0)), xOffset="cycle:N",
                          y=alt.Y("אחוז:Q", title="% מהנבדקים"),
                          color=alt.Color("cycle:N", title="סבב", scale=alt.Scale(range=[GREY, BLUE])),
                          tooltip=["cycle", "מדד", alt.Tooltip("אחוז:Q", format=".1f")])
                  .properties(height=300))
            st.altair_chart(cc, alt="בסבב 2021–2023 יותר נבדקים לוקחים תוסף ויטמין D, ופחות נמצאים ברמה נמוכה")
            st.caption("זה קשר ולא סיבתיות. בנוסף, ההרכב של המדגם שונה בין הסבבים: ב-2021–2023 ה-CDC לא דגם יותר "
                       "אנשים מקבוצות מוצא מסוימות, כמו בסבב הקודם. כדי להשוות בהגינות, סנני בצד לקבוצת מוצא אחת.")
    else:
        with g1:
            with st.container(border=True):
                st.markdown("**מאגרי ברזל נמוכים לפי מין וגיל**")
                ag = (f.assign(מין=f.sex.map(sex_map)).groupby(["age_group", "מין"], observed=True)
                      .iron_low.mean().mul(100).reset_index(name="% נמוך"))
                ac = (alt.Chart(ag).mark_bar()
                      .encode(x=alt.X("age_group:N", title="גיל", axis=alt.Axis(labelAngle=0)), xOffset="מין:N",
                              y=alt.Y("% נמוך:Q", title="% עם פריטין מתחת ל-15"),
                              color=alt.Color("מין:N", title="", scale=alt.Scale(range=[ORANGE, BLUE])),
                              tooltip=["age_group", "מין", alt.Tooltip("% נמוך:Q", format=".1f")])
                      .properties(height=320))
                st.altair_chart(ac, alt="מאגרי ברזל נמוכים נפוצים בעיקר אצל נשים בגילאי 18 עד 50")
        with g2:
            with st.container(border=True):
                st.markdown("**התפלגות הפריטין: נשים מול גברים**")
                hist = f.assign(מין=f.sex.map(sex_map), log_fer=np.log10(f.ferritin_ng_ml))
                hc = (alt.Chart(hist).mark_bar(opacity=0.6)
                      .encode(x=alt.X("log_fer:Q", bin=alt.Bin(maxbins=35),
                                      title="פריטין (ng/mL, סקאלה לוגריתמית: 1=10, 2=100)"),
                              y=alt.Y("count():Q", stack=None, title="מספר נבדקים"),
                              color=alt.Color("מין:N", title="", scale=alt.Scale(range=[ORANGE, BLUE])))
                      .properties(height=320))
                rule = (alt.Chart(pd.DataFrame({"x": [np.log10(LOW_FERRITIN)]}))
                        .mark_rule(color="red", strokeDash=[5, 4]).encode(x="x:Q"))
                st.altair_chart(hc + rule, alt="אצל נשים הפריטין נמוך יותר, וחלק גדול יותר נמצא משמאל לסף 15")
                st.caption("הקו האדום הוא סף 15 ng/mL (WHO 2020). משמאלו מאגרי הברזל נמוכים.")

    # ----- תוספים נפוצים
    with st.container(border=True):
        st.markdown("**אילו תוספים אנשים לוקחים (16 חומרים, צריכה מתוספים בלבד)**")
        NAMES = {"vitd": "ויטמין D", "calcium": "סידן", "vitc": "ויטמין C", "b12": "ויטמין B12", "b6": "ויטמין B6",
                 "folic_acid": "חומצה פולית", "niacin": "ניאצין (B3)", "zinc": "אבץ", "b2": "ויטמין B2", "b1": "ויטמין B1",
                 "magnesium": "מגנזיום", "copper": "נחושת", "iodine": "יוד", "selenium": "סלניום", "vitk": "ויטמין K",
                 "iron": "ברזל"}
        intake = load_intake()
        intake = intake[intake.seqn.isin(f.seqn)]
        prev = pd.DataFrame([{"חומר": he, "% לוקחים": 100 * (intake[f"dose_{k}"] > 0).mean()} for k, he in NAMES.items()])
        pch = (alt.Chart(prev).mark_bar(color=BLUE)
               .encode(y=alt.Y("חומר:N", sort="-x", title="", axis=alt.Axis(orient="right")),
                       x=alt.X("% לוקחים:Q", title="% מהנבדקים ב-30 הימים האחרונים"),
                       tooltip=["חומר", alt.Tooltip("% לוקחים:Q", format=".1f")])
               .properties(height=380))
        st.altair_chart(pch, alt="ויטמין D, סידן וויטמין C הם החומרים הנפוצים ביותר בתוספים, וברזל הכי פחות")
        st.caption("סקר NHANES מודד ויטמינים ומינרלים בלבד. קריאטין ואבקת חלבון לא נמדדים בו כחומרים, "
                   "ולכן המידע עליהם (מינון, תזמון ובטיחות) מגיע ממחקרים, בתצוגת 'תזמון ומינון'.")

    # ----- ישראל
    st.subheader("מה ידוע על ישראל")
    key = "ויטמין D3" if is_d else "ברזל"
    il = research[(research.country == "ישראל") & (research.supplement_he == key)]
    if il.empty:
        st.caption("עדיין אין בטבלת המחקרים עובדות ישראליות על הנושא הזה.")
    else:
        st.dataframe(il[["topic", "fact_he", "value", "source", "url"]], hide_index=True,
                     alt=f"עובדות מחקריות מישראל על {target}",
                     column_config={"topic": "נושא", "fact_he": "העובדה", "value": "ערך", "source": "מקור",
                                    "url": st.column_config.LinkColumn("קישור", display_text="פתיחה")})
    st.caption("NHANES הוא סקר אמריקאי, כי בישראל אין מאגר פתוח של בדיקות דם ברמת האדם. המודל ילמד מהנתונים "
               "האמריקאיים, והמחקרים הישראליים משמשים כדי לבדוק עד כמה התמונה אצלנו דומה.")

    # ----- טבלה
    st.subheader("דוגמה מהנתונים הנקיים")
    show = f.drop(columns=[c for c in ("dose_group", "age_group") if c in f]).sample(min(25, len(f)), random_state=1)
    st.dataframe(show, hide_index=True, alt="25 שורות לדוגמה מהנתונים הנקיים")
    st.caption("אין עמודות מיקום בנתונים, ולכן אין מפה. פירוט הניקוי והמגבלות: README ו-docs/DATA_CARD_he.md.")
