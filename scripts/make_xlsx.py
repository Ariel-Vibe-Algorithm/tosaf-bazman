import pandas as pd, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
d = pd.read_csv(sys.argv[1]).fillna("")
HE = {"id":"#","supplement_he":"תוסף","supplement_en":"שם באנגלית","category":"קטגוריה","best_time":"מתי לקחת",
"with_food":"עם או בלי אוכל","doses_per_day":"מנות ביום","next_dose_after_hours":"מנה הבאה אחרי (שעות)","can_split":"אפשר לפצל?",
"separate_from":"להפריד מתוספים (שם:דקות)","avoid_food_drinks":"להרחיק ממאכלים/משקאות","food_drinks_gap_minutes":"מרווח ממאכלים (דקות)",
"drug_interactions":"התנגשות עם תרופות","drug_gap":"מרווח מתרופות","severity":"חומרה","works_well_with":"עובד טוב עם",
"caution":"אזהרות","confidence":"רמת ביטחון","confidence_note":"הסבר לרמת הביטחון","source_main":"מקור ראשי","source_extra":"מקור נוסף"}
W = {"id":4,"supplement_he":18,"supplement_en":18,"category":12,"best_time":24,"with_food":22,"doses_per_day":8,"next_dose_after_hours":10,
"can_split":24,"separate_from":24,"avoid_food_drinks":18,"food_drinks_gap_minutes":10,"drug_interactions":40,"drug_gap":24,"severity":9,
"works_well_with":16,"caution":36,"confidence":9,"confidence_note":34,"source_main":36,"source_extra":30}
wb = Workbook(); ws = wb.active; ws.title = "כללי תזמון"; ws.sheet_view.rightToLeft = True
thin = Side(style="thin", color="BBBBBB"); b = Border(left=thin,right=thin,top=thin,bottom=thin)
cols = list(d.columns)
for j,c in enumerate(cols,1):
    x = ws.cell(1,j,HE[c]); x.font=Font(name="Arial",bold=True,color="FFFFFF"); x.fill=PatternFill("solid",fgColor="2F6F8F")
    x.alignment=Alignment(wrap_text=True,vertical="center",horizontal="center"); x.border=b
    ws.column_dimensions[get_column_letter(j)].width = W[c]
sev = {"חמורה":"F4C7C3","בינונית":"FCE8B2","קלה":"D9EAD3"}
conf = {"מבוסס":"D9EAD3","חלקי":"FCE8B2","מקובל":"F4C7C3"}
for i,row in enumerate(d.itertuples(index=False),2):
    for j,c in enumerate(cols,1):
        v = getattr(row,c)
        x = ws.cell(i,j,v); x.font=Font(name="Arial",size=10); x.alignment=Alignment(wrap_text=True,vertical="top"); x.border=b
        if c=="severity" and v in sev: x.fill=PatternFill("solid",fgColor=sev[v])
        if c=="confidence" and v in conf: x.fill=PatternFill("solid",fgColor=conf[v])
        if c=="supplement_he": x.font=Font(name="Arial",size=10,bold=True)
        if c.startswith("source") and v: x.hyperlink=v; x.font=Font(name="Arial",size=10,color="0563C1",underline="single")
ws.freeze_panes="C2"; ws.auto_filter.ref=ws.dimensions; ws.row_dimensions[1].height=36
lg = wb.create_sheet("מקרא"); lg.sheet_view.rightToLeft=True
rows=[("מה זה הקובץ","טבלת כללי תזמון ל-40 תוספים: שורה לכל תוסף. הגרסה לקוד היא data/timing_rules.csv (אותו תוכן, שמות עמודות באנגלית)."),
("מנה הבאה אחרי (שעות)","כמה שעות אחרי המנה הקודמת לוקחים שוב. 24 = פעם ביום, 12 = פעמיים ביום (בוקר וערב)."),
("להפריד מתוספים","פורמט 'שם:דקות'. למשל 'סידן:120' = לפחות שעתיים בין התוסף הזה לסידן. כל הפרדה חלה לשני הכיוונים, גם אם היא כתובה רק בשורה של אחד מהתוספים."),
("חומרה","חמורה = לא לשלב בלי רופא. בינונית = צריך הפרדה או מעקב. קלה = השפעה קטנה."),
("רמת ביטחון: מבוסס","הכלל כתוב במקור רשמי (NIH ODS או NCCIH)."),
("רמת ביטחון: חלקי","חלק מהכלל מהמקור הרשמי, וחלק (בדרך כלל השעה ביום) הוא נוהג מקובל. ההסבר בעמודה 'הסבר לרמת הביטחון'."),
("רמת ביטחון: מקובל","אין כלל רשמי. נוהג מקובל בלבד, וצריך שהצוות יבדוק ויוסיף מקור."),
("הסתייגות","כלי עזר ללימודים. לא מחליף ייעוץ של רופא, רוקח או דיאטנית.")]
lg.column_dimensions["A"].width=26; lg.column_dimensions["B"].width=100
for i,(a,c) in enumerate(rows,1):
    lg.cell(i,1,a).font=Font(name="Arial",bold=True); x=lg.cell(i,2,c); x.font=Font(name="Arial"); x.alignment=Alignment(wrap_text=True)
wb.save(sys.argv[2]); print("ok")
