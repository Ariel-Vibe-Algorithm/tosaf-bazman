# -*- coding: utf-8 -*-
"""בונה את data/timing_rules.csv: טבלה אחת, שורה לכל תוסף (40 תוספים).
עמודות עם שמות באנגלית (נוח לקוד), תוכן בעברית.
separate_from: רשימה בפורמט 'שם:דקות; שם:דקות' כדי שהקוד יוכל לפרק אותה.
confidence: 'מבוסס' = כתוב במקור רשמי (NIH ODS / NCCIH); 'חלקי' = חלק מהכלל מהמקור וחלק נוהג מקובל;
'מקובל' = נוהג מקובל בפועל, המקור הרשמי לא מתייחס לשעה/אוכל. כל כלל 'מקובל' צריך בדיקה של הצוות.
"""
import csv, sys
from pathlib import Path

ODS = "https://ods.od.nih.gov/factsheets/{}-HealthProfessional/"
NCC = "https://www.nccih.nih.gov/health/{}"
EX = ODS.format("ExerciseAndAthleticPerformance")
CREAT = "https://pmc.ncbi.nlm.nih.gov/articles/PMC5469049/"

COLS = ["id", "supplement_he", "supplement_en", "category",
        "best_time", "with_food", "doses_per_day", "next_dose_after_hours", "can_split",
        "separate_from", "avoid_food_drinks", "food_drinks_gap_minutes",
        "drug_interactions", "drug_gap", "severity",
        "works_well_with", "caution", "confidence", "confidence_note", "source_main", "source_extra"]

ANTIBIO = "אנטיביוטיקה מסוג טטרציקלינים וקווינולונים (למשל ציפרו)"
R = []
def add(**k):
    k["id"] = len(R) + 1
    R.append(k)

# ---------------- ויטמינים
add(supplement_he="ויטמין D3", supplement_en="Vitamin D3", category="ויטמין",
    best_time="עם הארוחה הגדולה של היום (צהריים או ערב)", with_food="עם ארוחה שיש בה שומן",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="orlistat ו-cholestyramine מפחיתים ספיגה; סטרואידים מורידים רמת D; משתנים מסוג thiazide יחד עם D עלולים להעלות סידן בדם; סטטינים: אינטראקציה אפשרית במינון גבוה",
    drug_gap="להתייעץ עם רופא/רוקח", severity="בינונית",
    works_well_with="ויטמין K2; סידן", caution="תקרה למבוגרים: 100 מק\"ג (4,000 IU) ביום",
    confidence="חלקי", confidence_note="'עם ארוחה שומנית' מבוסס (NIH). השעה ביום לא מצוינת במקור",
    source_main=ODS.format("VitaminD"), source_extra="https://ods.od.nih.gov/factsheets/VitaminD-Consumer/")
add(supplement_he="ויטמין B12", supplement_en="Vitamin B12", category="ויטמין",
    best_time="בוקר", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך (במינון גבוה נספג רק אחוז קטן, ולכן מנה אחת מספיקה)",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="מעכבי חומצה (PPI כמו אומפרזול, חוסמי H2) ו-metformin מורידים ספיגה ורמה בדם",
    drug_gap="אין צורך בהפרדה. כדאי לבדוק רמה בדם", severity="קלה",
    works_well_with="חומצה פולית", caution="טבעונים וצמחונים בסיכון לחסר",
    confidence="חלקי", confidence_note="אינטראקציות מבוססות (NIH). 'בוקר' הוא נוהג מקובל לויטמיני B",
    source_main=ODS.format("VitaminB12"), source_extra="")
add(supplement_he="ויטמין C", supplement_en="Vitamin C", category="ויטמין",
    best_time="בבוקר יחד עם הברזל (אם לוקחים ברזל), אחרת לא משנה", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן, מעל 1 גרם ביום עדיף לפצל ל-2 (12 שעות)",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="יחד עם נוגדי חמצון אחרים עלול להחליש את השפעת niacin+simvastatin על HDL",
    drug_gap="להתייעץ", severity="קלה",
    works_well_with="ברזל (מגביר ספיגה)", caution="תקרה 2,000 מ\"ג ביום. אנשים עם המוכרומטוזיס: להימנע",
    confidence="מבוסס", confidence_note="הקשר לברזל והספיגה מבוססים (NIH)",
    source_main=ODS.format("VitaminC"), source_extra=ODS.format("Iron"))
add(supplement_he="מולטי-ויטמין", supplement_en="Multivitamin/mineral", category="ויטמין",
    best_time="בוקר", with_food="עם ארוחה (מפחית בחילה ומשפר ספיגת ויטמינים מסיסי שומן)",
    doses_per_day=1, next_dose_after_hours=24, can_split="לפי התווית",
    separate_from="ברזל:120; סידן:120",
    avoid_food_drinks="קפה ותה (אם יש בו ברזל)", food_drinks_gap_minutes=60,
    drug_interactions=f"warfarin (אם יש ויטמין K); לבותירוקסין (אלטרוקסין) כשיש בו ברזל/סידן; {ANTIBIO}",
    drug_gap="לבותירוקסין: 4 שעות; אנטיביוטיקה: שעתיים לפני או 4–6 שעות אחרי", severity="בינונית",
    works_well_with="", caution="לא לשלב עם תוספים נפרדים של אותם רכיבים בלי לבדוק סכום מינונים",
    confidence="חלקי", confidence_note="warfarin מבוסס (NIH MVMS). הפרדת לבותירוקסין/אנטיביוטיקה מבוססת על דפי ברזל וסידן",
    source_main=ODS.format("MVMS"), source_extra=ODS.format("Calcium"))
add(supplement_he="B קומפלקס", supplement_en="Vitamin B complex", category="ויטמין",
    best_time="בוקר", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="ביוטין במינון גבוה משבש בדיקות דם (תירואיד, טרופונין, ויטמין D); תרופות נגד אפילפסיה מורידות רמות B",
    drug_gap="לעדכן את הרופא לפני בדיקת דם", severity="בינונית",
    works_well_with="", caution="B6 במינון גבוה לאורך זמן גורם לפגיעה עצבית. באירופה התקרה ל-B6 היא 12 מ\"ג ביום",
    confidence="חלקי", confidence_note="אזהרות מבוססות (NIH). 'בוקר עם ארוחה' נוהג מקובל",
    source_main=ODS.format("VitaminB6"), source_extra=ODS.format("Biotin"))
add(supplement_he="חומצה פולית", supplement_en="Folic acid (B9)", category="ויטמין",
    best_time="בוקר", with_food="לא משנה (בלי אוכל נספגת כמעט 100%)",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="methotrexate; תרופות נגד אפילפסיה (phenytoin, carbamazepine, valproate); sulfasalazine",
    drug_gap="להתייעץ עם רופא", severity="בינונית",
    works_well_with="ויטמין B12", caution="מינון גבוה עלול להסתיר חסר B12. תקרה 1,000 מק\"ג ביום. נשים שמתכננות הריון: 400 מק\"ג מחודש לפני",
    confidence="מבוסס", confidence_note="ספיגה ואינטראקציות מ-NIH",
    source_main=ODS.format("Folate"), source_extra="")
add(supplement_he="ויטמין B6", supplement_en="Vitamin B6", category="ויטמין",
    best_time="בוקר", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="תרופות נגד אפילפסיה; levodopa (בלי carbidopa)",
    drug_gap="להתייעץ", severity="בינונית",
    works_well_with="", caution="מינון גבוה לאורך זמן גורם לנוירופתיה. תקרה בארה\"ב 100 מ\"ג, באירופה 12 מ\"ג ביום",
    confidence="חלקי", confidence_note="אזהרות מבוססות (NIH). השעה נוהג מקובל",
    source_main=ODS.format("VitaminB6"), source_extra="")
add(supplement_he="ויטמין E", supplement_en="Vitamin E", category="ויטמין",
    best_time="עם הארוחה הגדולה של היום", with_food="עם ארוחה שיש בה שומן",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="warfarin ונוגדי טסיות: מינון גבוה מעלה סיכון לדימום",
    drug_gap="לא לשלב בלי רופא", severity="בינונית",
    works_well_with="", caution="תקרה 1,000 מ\"ג ביום",
    confidence="חלקי", confidence_note="צורך בשומן לספיגה מבוסס (NIH)",
    source_main=ODS.format("VitaminE"), source_extra="")
add(supplement_he="ויטמין A", supplement_en="Vitamin A", category="ויטמין",
    best_time="עם הארוחה הגדולה של היום", with_food="עם ארוחה שיש בה שומן",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="orlistat מפחית ספיגה; רטינואידים (למשל רואקוטן, acitretin) יחד עם A מעלים סיכון להרעלה",
    drug_gap="לא לשלב עם רטינואידים", severity="חמורה",
    works_well_with="", caution="הריון: לא מעל 3,000 מק\"ג (10,000 IU) מתוספים, סיכון למומים",
    confidence="חלקי", confidence_note="אינטראקציות ואזהרת הריון מבוססות (NIH)",
    source_main=ODS.format("VitaminA"), source_extra="")
add(supplement_he="ויטמין K2", supplement_en="Vitamin K2 (MK-7)", category="ויטמין",
    best_time="עם הארוחה הגדולה של היום (אפשר יחד עם D3)", with_food="עם ארוחה שיש בה שומן",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך (MK-7 נשאר בגוף זמן רב)",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="warfarin (קומדין): אינטראקציה חמורה, משנה את השפעת התרופה; אנטיביוטיקה ממושכת; cholestyramine, orlistat",
    drug_gap="נוטלי warfarin: לא להתחיל או להפסיק בלי רופא", severity="חמורה",
    works_well_with="ויטמין D3", caution="",
    confidence="חלקי", confidence_note="warfarin מבוסס (NIH). השילוב עם D3 נוהג מקובל",
    source_main=ODS.format("VitaminK"), source_extra="")
add(supplement_he="ביוטין (B7)", supplement_en="Biotin", category="ויטמין",
    best_time="בוקר", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="משבש בדיקות מעבדה (הורמוני תירואיד, טרופונין, ויטמין D); תרופות נגד אפילפסיה מורידות רמה",
    drug_gap="לעדכן את הרופא לפני בדיקת דם. מנה של 10 מ\"ג שיבשה בדיקות בתוך 24 שעות", severity="בינונית",
    works_well_with="", caution="",
    confidence="חלקי", confidence_note="שיבוש בדיקות מבוסס (NIH). השעה נוהג מקובל",
    source_main=ODS.format("Biotin"), source_extra="")

# ---------------- מינרלים
add(supplement_he="ברזל", supplement_en="Iron", category="מינרל",
    best_time="בוקר, 30–60 דקות לפני ארוחת הבוקר", with_food="על בטן ריקה (אם כואבת הבטן: עם מעט אוכל)",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא כדאי לפצל",
    separate_from="סידן:120; אבץ:120; מגנזיום:120; מולטי-ויטמין:120; ויטמינים להריון:120; סיבים (פסיליום):120",
    avoid_food_drinks="קפה; תה; חלב ומוצרי חלב", food_drinks_gap_minutes=60,
    drug_interactions=f"לבותירוקסין (אלטרוקסין); PPI (אומפרזול) מפחיתים ספיגה; {ANTIBIO}; levodopa",
    drug_gap="לבותירוקסין: 4 שעות; אנטיביוטיקה: שעתיים לפני או 4–6 שעות אחרי", severity="בינונית",
    works_well_with="ויטמין C", caution="המוכרומטוזיס: לא ליטול. תקרה 45 מ\"ג ביום. מינון גבוה על בטן ריקה עלול לגרום לבחילה ועצירות",
    confidence="חלקי", confidence_note="ויטמין C, סידן, אבץ ולבותירוקסין מבוססים (NIH). המרווח מקפה/תה והשעה הם נוהג מקובל, לבדוק מקור נוסף",
    source_main=ODS.format("Iron"), source_extra="https://ods.od.nih.gov/factsheets/Iron-Consumer/")
add(supplement_he="מגנזיום", supplement_en="Magnesium", category="מינרל",
    best_time="ערב, כשעה לפני השינה (אפשר לפצל: בוקר + ערב)", with_food="עם ארוחה או חטיף (מפחית שלשול)",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: 2 מנות בהפרש 12 שעות (בוקר + ערב)",
    separate_from="ברזל:120",
    avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions=f"{ANTIBIO}; ביספוספונטים לעצם (alendronate); PPI לאורך זמן ומשתנים מורידים מגנזיום",
    drug_gap="אנטיביוטיקה: שעתיים לפני או 4–6 שעות אחרי; ביספוספונטים: שעתיים", severity="בינונית",
    works_well_with="ויטמין D", caution="תקרה מתוספים: 350 מ\"ג ביום. מינון גבוה גורם לשלשול",
    confidence="חלקי", confidence_note="תרופות מבוססות (NIH). 'ערב לשינה' לא מופיע ב-NIH, נוהג מקובל",
    source_main=ODS.format("Magnesium"), source_extra="")
add(supplement_he="סידן", supplement_en="Calcium", category="מינרל",
    best_time="צהריים או ערב, עם ארוחה", with_food="עם ארוחה (סידן קרבונט חייב אוכל; ציטראט לא חייב)",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: לא יותר מ-500 מ\"ג במנה. מעל זה לפצל ל-2 מנות בהפרש 6 שעות לפחות",
    separate_from="ברזל:120; אבץ:120",
    avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="לבותירוקסין (אלטרוקסין); קווינולונים; dolutegravir (HIV)",
    drug_gap="לבותירוקסין: 4 שעות; קווינולונים: שעתיים; dolutegravir: שעתיים לפני או 6 שעות אחרי", severity="בינונית",
    works_well_with="ויטמין D", caution="תקרה 2,500 מ\"ג ביום (גיל 19–50). שילוב עם D הוביל לעלייה קטנה באבנים בכליות",
    confidence="מבוסס", confidence_note="מנה עד 500 מ\"ג ואינטראקציות מבוססות (NIH)",
    source_main=ODS.format("Calcium"), source_extra=ODS.format("Iron"))
add(supplement_he="אבץ", supplement_en="Zinc", category="מינרל",
    best_time="ערב או בין ארוחות", with_food="אפשר בלי אוכל; אם יש בחילה, עם ארוחה קלה (לא עם קטניות ודגנים מלאים)",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="ברזל:120; סידן:120",
    avoid_food_drinks="קטניות ודגנים מלאים (פיטאטים)", food_drinks_gap_minutes=60,
    drug_interactions=f"{ANTIBIO}; penicillamine; משתנים מסוג thiazide מגבירים איבוד אבץ",
    drug_gap="אנטיביוטיקה: שעתיים לפני או 4–6 שעות אחרי", severity="בינונית",
    works_well_with="", caution="תקרה 40 מ\"ג ביום. 50 מ\"ג ומעלה לאורך זמן גורם לחסר נחושת",
    confidence="חלקי", confidence_note="ברזל, אנטיביוטיקה ונחושת מבוססים (NIH). 'עם/בלי אוכל' לא מוזכר במקור",
    source_main=ODS.format("Zinc"), source_extra="")
add(supplement_he="סלניום", supplement_en="Selenium", category="מינרל",
    best_time="בוקר", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="cisplatin (כימותרפיה)", drug_gap="להתייעץ", severity="קלה",
    works_well_with="", caution="תקרה 400 מק\"ג ביום. אגוז ברזיל אחד מכיל 68–91 מק\"ג. עודף: ריח שום מהפה, נשירת שיער",
    confidence="חלקי", confidence_note="תקרה ואינטראקציה מבוססות (NIH). השעה נוהג מקובל",
    source_main=ODS.format("Selenium"), source_extra="")
add(supplement_he="אשלגן", supplement_en="Potassium", category="מינרל",
    best_time="עם ארוחה", with_food="עם ארוחה וכוס מים מלאה",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן, לפי הוראת רופא",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="מעכבי ACE ו-ARB (תרופות ללחץ דם) ומשתנים חוסכי אשלגן: סכנת אשלגן גבוה בדם; משתנים מסוג loop/thiazide מורידים אשלגן",
    drug_gap="לא לשלב בלי רופא", severity="חמורה",
    works_well_with="", caution="מחלת כליות: לא ליטול בלי רופא. רוב התוספים מוגבלים ל-99 מ\"ג במנה",
    confidence="חלקי", confidence_note="אינטראקציות מבוססות (NIH). 'עם ארוחה' נוהג מקובל",
    source_main=ODS.format("Potassium"), source_extra="")
add(supplement_he="יוד", supplement_en="Iodine", category="מינרל",
    best_time="בוקר", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="תרופות לפעילות יתר של בלוטת התריס (methimazole); מעכבי ACE ומשתנים חוסכי אשלגן (כשהיוד הוא יודיד אשלגן)",
    drug_gap="להתייעץ עם רופא", severity="בינונית",
    works_well_with="", caution="תקרה 1,100 מק\"ג ביום. מחלת תריס אוטואימונית: רגישות לעודף",
    confidence="חלקי", confidence_note="אינטראקציות מבוססות (NIH). השעה נוהג מקובל",
    source_main=ODS.format("Iodine"), source_extra="")
add(supplement_he="כרום", supplement_en="Chromium", category="מינרל",
    best_time="עם ארוחה", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="נוגדי חומצה (אנטאצידים):120",
    avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="אינסולין ו-metformin: סכנת סוכר נמוך; לבותירוקסין: ספיגה ירדה כשנלקחו יחד",
    drug_gap="לבותירוקסין: להפריד כמה שעות (במחקר נבדקו 6 שעות)", severity="בינונית",
    works_well_with="ויטמין C (מגביר ספיגה)", caution="",
    confidence="חלקי", confidence_note="אינטראקציות מבוססות (NIH). אורך ההפרדה ושעה נוהג מקובל",
    source_main=ODS.format("Chromium"), source_extra="")

# ---------------- חומצות שומן
add(supplement_he="אומגה 3 (שמן דגים)", supplement_en="Omega-3 fish oil", category="חומצות שומן",
    best_time="עם הארוחה הגדולה של היום", with_food="עם ארוחה (מפחית גיהוקים בטעם דג)",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: 2 מנות בהפרש 12 שעות להפחתת תופעות לוואי",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="warfarin ונוגדי קרישה: מינון גבוה מעלה סיכון לדימום", drug_gap="להתייעץ עם רופא", severity="בינונית",
    works_well_with="ויטמין D", caution="ה-FDA: לא יותר מ-5 גרם EPA+DHA ביום מתוספים",
    confidence="חלקי", confidence_note="אינטראקציה ותקרה מבוססות (NIH). 'עם ארוחה' נוהג מקובל",
    source_main="https://ods.od.nih.gov/factsheets/Omega3FattyAcids-Consumer/", source_extra="")
add(supplement_he="אומגה 3 צמחית (שמן אצות / פשתן)", supplement_en="Plant omega-3 (algal oil / flaxseed oil)", category="חומצות שומן",
    best_time="עם הארוחה הגדולה של היום", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: 2 מנות בהפרש 12 שעות",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="warfarin ונוגדי קרישה (מינון גבוה)", drug_gap="להתייעץ עם רופא", severity="קלה",
    works_well_with="", caution="שמן אצות מכיל EPA/DHA. שמן פשתן מכיל רק ALA, שהגוף ממיר רק מעט ממנו",
    confidence="מקובל", confidence_note="מבוסס על דף אומגה 3 של NIH. אין כלל תזמון במקור",
    source_main="https://ods.od.nih.gov/factsheets/Omega3FattyAcids-Consumer/", source_extra=NCC.format("flaxseed-and-flaxseed-oil"))

# ---------------- מערכת עיכול
add(supplement_he="פרוביוטיקה", supplement_en="Probiotics", category="מערכת עיכול",
    best_time="בוקר, עם ארוחת הבוקר או מעט לפניה", with_food="עם ארוחה או לפניה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="אנטיביוטיקה:120",
    avoid_food_drinks="שתייה חמה מאוד", food_drinks_gap_minutes="",
    drug_interactions="אנטיביוטיקה: להתחיל פרוביוטיקה בתוך יומיים מתחילת האנטיביוטיקה, אבל לא באותה שעה",
    drug_gap="שעתיים מהאנטיביוטיקה", severity="קלה",
    works_well_with="סיבים תזונתיים", caution="פגים ומדוכאי חיסון: רק עם רופא",
    confidence="חלקי", confidence_note="התחלה בתוך יומיים מבוססת (NIH). השעה וההפרדה של שעתיים נוהג מקובל",
    source_main=ODS.format("Probiotics"), source_extra="")
add(supplement_he="סיבים תזונתיים (פסיליום)", supplement_en="Psyllium fiber", category="מערכת עיכול",
    best_time="לפני ארוחה", with_food="עם כוס מים מלאה לפחות",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: עד 3 מנות ביום לפני ארוחות",
    separate_from="ברזל:120; סידן:120; אבץ:120; מגנזיום:120; מולטי-ויטמין:120",
    avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="עלול להפחית ספיגה של כל תרופה שנלקחת באותה שעה",
    drug_gap="שעתיים מכל תרופה", severity="בינונית",
    works_well_with="פרוביוטיקה", caution="בלי מספיק מים: סכנת חנק או חסימה",
    confidence="מקובל", confidence_note="אין דף NIH ODS ולא הייתה גישה ל-MedlinePlus. מבוסס על הוראות תווית מקובלות. צריך למצוא מקור",
    source_main="", source_extra="")

# ---------------- צמחים
add(supplement_he="כורכום (כורכומין)", supplement_en="Turmeric / curcumin", category="צמחי מרפא",
    best_time="עם ארוחה", with_food="עם ארוחה שיש בה שומן, עדיף עם פלפל שחור (פיפרין)",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: 2 מנות בהפרש 12 שעות",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="נוגדי קרישה: חשש לדימום (נוהג מקובל, לא מופיע ב-NCCIH)", drug_gap="להתייעץ עם רופא", severity="בינונית",
    works_well_with="פלפל שחור", caution="מוצרים 'זמינים במיוחד' נקשרו לפגיעה בכבד. להפסיק אם יש עייפות, שתן כהה או צהבת. בטוח עד 2–3 חודשים",
    confidence="חלקי", confidence_note="כבד ופיפרין מבוססים (NCCIH). נוגדי קרישה ושעה נוהג מקובל",
    source_main=NCC.format("turmeric"), source_extra="")
add(supplement_he="אשווגנדה", supplement_en="Ashwagandha", category="צמחי מרפא",
    best_time="ערב (לשינה), או בוקר וערב (ללחץ)", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: 2 מנות בהפרש 12 שעות",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="הורמון בלוטת התריס; תרופות הרגעה ושינה; מדכאי חיסון; תרופות לסוכרת וללחץ דם",
    drug_gap="לא לשלב בלי רופא", severity="בינונית",
    works_well_with="", caution="הריון: לא מומלץ. דווחו מקרים של פגיעה בכבד. בטוח עד כ-3 חודשים",
    confidence="חלקי", confidence_note="אינטראקציות ובטיחות מבוססות (NIH). השעה לא מוגדרת במקור",
    source_main=ODS.format("Ashwagandha"), source_extra="")
add(supplement_he="ג'ינג'ר", supplement_en="Ginger", category="צמחי מרפא",
    best_time="לפני ארוחה או לפני נסיעה (נגד בחילה)", with_food="עם מעט אוכל (מפחית צרבת)",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: 2–3 מנות ביום",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="נוגדי קרישה: אינטראקציה אפשרית (נוהג מקובל)", drug_gap="להתייעץ", severity="קלה",
    works_well_with="", caution="תופעות לוואי: צרבת, שלשול, אי נוחות בבטן. הריון: להתייעץ",
    confidence="מקובל", confidence_note="תופעות לוואי מ-NCCIH. אין כלל תזמון במקור",
    source_main=NCC.format("ginger"), source_extra="")
add(supplement_he="שום", supplement_en="Garlic", category="צמחי מרפא",
    best_time="עם ארוחה", with_food="עם ארוחה (מפחית ריח ואי נוחות)",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="נוגדי קרישה ואספירין: סיכון לדימום; לעדכן לפני ניתוח", drug_gap="לא לשלב בלי רופא", severity="בינונית",
    works_well_with="", caution="להפסיק לפני ניתוח (לעדכן את הרופא)",
    confidence="חלקי", confidence_note="דימום מבוסס (NCCIH). 'עם ארוחה' נוהג מקובל",
    source_main=NCC.format("garlic"), source_extra="")
add(supplement_he="ג'ינסנג", supplement_en="Ginseng", category="צמחי מרפא",
    best_time="בוקר (עלול לגרום לנדודי שינה)", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="קפה ומשקאות אנרגיה (ממריצים)", food_drinks_gap_minutes="",
    drug_interactions="תרופות לסוכרת (מוריד סוכר); נוגדי קרישה", drug_gap="להתייעץ עם רופא", severity="בינונית",
    works_well_with="", caution="עד 6 חודשים. לא לילדים ולא בהריון",
    confidence="חלקי", confidence_note="נדודי שינה ואינטראקציות מבוססים (NCCIH). 'בוקר' נגזר מתופעת הלוואי",
    source_main="https://nccih.nih.gov/health/asianginseng", source_extra="")
add(supplement_he="אכינצאה", supplement_en="Echinacea", category="צמחי מרפא",
    best_time="בתחילת הצטננות, לאורך היום", with_food="לא משנה",
    doses_per_day=2, next_dose_after_hours=12, can_split="כן",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="מדכאי חיסון; קפאין (תיאורטי)", drug_gap="להתייעץ", severity="קלה",
    works_well_with="", caution="לשימוש קצר בלבד. תגובות אלרגיות. הריון: עד 7 ימים ורק עם רופא",
    confidence="מקובל", confidence_note="בטיחות מ-NCCIH. מספר המנות לפי התווית",
    source_main=NCC.format("echinacea"), source_extra="")
add(supplement_he="סמבוק (Elderberry)", supplement_en="Elderberry", category="צמחי מרפא",
    best_time="בזמן הצטננות, לאורך היום", with_food="לא משנה",
    doses_per_day=2, next_dose_after_hours=12, can_split="כן",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="לא ידוע. להתייעץ אם נוטלים תרופות", drug_gap="להתייעץ", severity="קלה",
    works_well_with="", caution="רק מוצר מבושל או מסחרי. פרי לא בשל, עלים וגבעולים רעילים",
    confidence="מקובל", confidence_note="בטיחות מ-NCCIH. אין כלל תזמון במקור",
    source_main=NCC.format("elderberry"), source_extra="")
add(supplement_he="היפריקום (St. John's Wort)", supplement_en="St. John's wort", category="צמחי מרפא",
    best_time="בוקר", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לפי התווית",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="מחליש: גלולות למניעת הריון, נוגדי דיכאון, ציקלוספורין, warfarin, digoxin, תרופות לאפילפסיה, תרופות HIV, סימבסטטין, תרופות לסרטן. עם נוגדי דיכאון: סכנת תסמונת סרוטונין",
    drug_gap="הפרדה בזמן לא עוזרת. לא לשלב בלי רופא", severity="חמורה",
    works_well_with="", caution="רגישות לשמש",
    confidence="מבוסס", confidence_note="רשימת האינטראקציות מ-NCCIH",
    source_main=NCC.format("st-johns-wort"), source_extra="")
add(supplement_he="גינקו בילובה", supplement_en="Ginkgo biloba", category="צמחי מרפא",
    best_time="בוקר וערב", with_food="עם ארוחה",
    doses_per_day=2, next_dose_after_hours=12, can_split="כן",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="warfarin ונוגדי קרישה: סיכון לדימום", drug_gap="לא לשלב בלי רופא", severity="חמורה",
    works_well_with="", caution="הריון: עלול לא להיות בטוח. זרעים טריים רעילים",
    confidence="חלקי", confidence_note="דימום מבוסס (NCCIH). מספר המנות לפי התווית",
    source_main=NCC.format("ginkgo"), source_extra="")

# ---------------- נוספים
add(supplement_he="קולגן", supplement_en="Collagen peptides", category="תוספים נוספים",
    best_time="בוקר או אחרי אימון", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="לא ידועות אינטראקציות משמעותיות", drug_gap="", severity="קלה",
    works_well_with="ויטמין C", caution="אין דף NIH. העדויות ליעילות מוגבלות",
    confidence="מקובל", confidence_note="אין מקור רשמי. נוהג מקובל בלבד, לבדוק מאמר מדעי",
    source_main="", source_extra="")
add(supplement_he="קואנזים Q10", supplement_en="Coenzyme Q10", category="תוספים נוספים",
    best_time="בוקר או צהריים (בערב עלול לפגוע בשינה)", with_food="עם ארוחה שיש בה שומן",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: 2 מנות במינון גבוה",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="warfarin: עלול לשנות את השפעת התרופה", drug_gap="לא לשלב בלי רופא", severity="בינונית",
    works_well_with="", caution="תופעות לוואי: נדודי שינה, אי נוחות בבטן",
    confidence="חלקי", confidence_note="warfarin ונדודי שינה מ-NCCIH. 'עם שומן' נוהג מקובל (מסיס בשומן)",
    source_main="https://nccih.nih.gov/health/supplements/coq10", source_extra="")
add(supplement_he="מלטונין", supplement_en="Melatonin", category="תוספים נוספים",
    best_time="30–60 דקות לפני השינה", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא",
    separate_from="", avoid_food_drinks="אלכוהול", food_drinks_gap_minutes="",
    drug_interactions="נוגדי קרישה; תרופות לאפילפסיה; תרופות הרגעה ושינה", drug_gap="רק תחת השגחת רופא", severity="בינונית",
    works_well_with="", caution="ישנוניות למחרת, במיוחד אצל מבוגרים. ילדים: רק עם רופא. גומיות מסומנות לעיתים לא נכון",
    confidence="מבוסס", confidence_note="נטילה כשעה לפני השינה נבדקה במחקר שמוזכר ב-NCCIH",
    source_main=NCC.format("melatonin-what-you-need-to-know"), source_extra="")
add(supplement_he="גלוקוזאמין וכונדרויטין", supplement_en="Glucosamine & chondroitin", category="תוספים נוספים",
    best_time="עם ארוחה", with_food="עם ארוחה (מפחית אי נוחות בבטן)",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: עד 3 מנות ביום",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="warfarin: דווח על עלייה בסיכון לדימום", drug_gap="לא לשלב בלי רופא", severity="בינונית",
    works_well_with="", caution="אלרגיה לפירות ים: לבדוק את מקור המוצר",
    confidence="מקובל", confidence_note="המקור הוא מחקר GAIT של NIH על יעילות. האינטראקציות והתזמון לא נבדקו מול דף רשמי (לא הייתה גישה ל-MedlinePlus). לבדוק",
    source_main="https://nccih.nih.gov/research/results/gait/qa.htm", source_extra="")
add(supplement_he="קריאטין", supplement_en="Creatine monohydrate", category="ספורט",
    best_time="כל יום באותה שעה. בימי אימון נוח אחרי האימון", with_food="עם ארוחה (פחמימה וחלבון משפרים אגירה בשריר)",
    doses_per_day=1, next_dose_after_hours=24, can_split="בשלב העמסה: 4 מנות של 5 גרם, 5–7 ימים. אחר כך 3–5 גרם פעם ביום",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="מחלת כליות או תרופות שפוגעות בכליות: להתייעץ", drug_gap="", severity="קלה",
    works_well_with="חלבון; פחמימה", caution="עלייה קלה במשקל (נוזלים). המאגרים חוזרים לבסיס 4–6 שבועות אחרי הפסקה",
    confidence="חלקי", confidence_note="מינון והעמסה מבוססים (NIH, ISSN). שעה ביחס לאימון לא חד-משמעית",
    source_main=EX, source_extra=CREAT)
add(supplement_he="אבקת חלבון", supplement_en="Protein powder", category="ספורט",
    best_time="אחרי אימון או בין ארוחות", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="כן: לפזר את החלבון היומי על פני כמה ארוחות",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="לא ידועות אינטראקציות משמעותיות", drug_gap="", severity="קלה",
    works_well_with="קריאטין", caution="צורך יומי של ספורטאים: 1.2–2.0 גרם לק\"ג. מחלת כליות: להתייעץ",
    confidence="חלקי", confidence_note="כמות יומית מבוססת (NIH). לא ברור אם לפני או אחרי אימון עדיף",
    source_main=EX, source_extra="")
add(supplement_he="L-תיאנין", supplement_en="L-theanine", category="תוספים נוספים",
    best_time="ערב (להרגעה) או בבוקר יחד עם קפה", with_food="לא משנה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לא צריך",
    separate_from="", avoid_food_drinks="", food_drinks_gap_minutes="",
    drug_interactions="תרופות ללחץ דם ותרופות הרגעה: אפקט מצטבר אפשרי", drug_gap="להתייעץ", severity="קלה",
    works_well_with="", caution="אין דף NIH ייעודי",
    confidence="מקובל", confidence_note="אין מקור רשמי ל-L-תיאנין עצמו (הקישור הוא לדף תה ירוק). נוהג מקובל בלבד, לבדוק מאמר מדעי",
    source_main=NCC.format("green-tea"), source_extra="")
add(supplement_he="ויטמינים להריון", supplement_en="Prenatal vitamins", category="ויטמין",
    best_time="בוקר, או בערב אם יש בחילות", with_food="עם ארוחה",
    doses_per_day=1, next_dose_after_hours=24, can_split="לפי התווית",
    separate_from="סידן:120",
    avoid_food_drinks="קפה ותה (בגלל הברזל)", food_drinks_gap_minutes=60,
    drug_interactions="לבותירוקסין (בגלל ברזל וסידן); warfarin אם יש ויטמין K", drug_gap="לבותירוקסין: 4 שעות", severity="בינונית",
    works_well_with="", caution="חומצה פולית 400 מק\"ג מחודש לפני ההריון. לא לקחת ויטמין A (רטינול) נוסף. ייתכן שיחסרו יוד וכולין",
    confidence="חלקי", confidence_note="תוכן ההמלצות מבוסס (NIH MVMS). ההפרדה נגזרת מדפי ברזל וסידן",
    source_main=ODS.format("MVMS"), source_extra=ODS.format("Iron"))

assert len(R) == 40, len(R)
out = Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    for r in R:
        w.writerow({c: r.get(c, "") for c in COLS})
print("wrote", out, len(R), "rows")
