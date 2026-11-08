import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from datetime import date

F = "Arial"
H_FILL = PatternFill("solid", fgColor="1F2A44")
IN_FILL = PatternFill("solid", fgColor="FFF7CC")
EX_FILL = PatternFill("solid", fgColor="E8F0FE")
KPI_FILL = PatternFill("solid", fgColor="EAF7EE")
thin = Side(style="thin", color="D0D5DD")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
USD = '$#,##0.00;[Red]($#,##0.00);-'
ILS = '₪#,##0;[Red](₪#,##0);-'
DATE = 'dd/mm/yyyy'

def font(**k): return Font(name=F, **k)

def setup(ws, widths):
    ws.sheet_view.rightToLeft = True
    for col, w in widths.items(): ws.column_dimensions[col].width = w

def header(ws, row, labels):
    for i, l in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=l)
        c.font = font(bold=True, color="FFFFFF"); c.fill = H_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BOX
    ws.row_dimensions[row].height = 32
    ws.freeze_panes = ws.cell(row=row+1, column=1)

def build(full=True, nrows=500):
    wb = Workbook()
    # ---------- Start ----------
    st = wb.active; st.title = "התחלה"; setup(st, {"A": 4, "B": 95})
    title = "ערכת הסוחר הישראלי" if full else "מחשבון קיזוז הפסדים — גרסה חינמית"
    lines = [
        (title, font(bold=True, size=18)),
        ("יומן מסחר, המרה לשקלים וסיכום רווח/הפסד ממומש לסוחרים עם ברוקר זר" if full else "20 עסקאות סגורות + 20 פוזיציות פתוחות. רואים בדקה כמה רווח ממומש יש השנה וכמה הפסד פתוח קיים.", font(size=11, color="555555")),
        ("", None),
        ("איך משתמשים", font(bold=True, size=13)),
    ]
    if full:
        lines += [
            ("1. גיליון 'שערים': הזן את השער היציג USD/ILS של בנק ישראל לכל יום מסחר רלוונטי (תאריכים בסדר עולה).", None),
            ("2. גיליון 'עסקאות סגורות': הדבק עסקאות סגורות מהברוקר (ב-IBKR: Flex Query → Trades → Closed Lots). עמודות לבנות-צהובות בלבד.", None),
            ("3. גיליון 'פוזיציות פתוחות': הזן פוזיציות פתוחות ומחיר נוכחי כדי לראות הפסדים פתוחים.", None),
            ("4. גיליון 'יומן מסחר': תעד כל טרייד — סטאפ, סטופ, יציאה ותגית טעות. ה-R והרווח מחושבים אוטומטית.", None),
            ("5. גיליון 'דשבורד': בחר שנה ושער נוכחי. רואים רווח ממומש, הפסדים פתוחים, ופוטנציאל קיזוז.", None),
        ]
    else:
        lines += [
            ("1. בגיליון 'מחשבון' הזן את השער הנוכחי USD/ILS בתא הצהוב.", None),
            ("2. הזן עסקאות סגורות של השנה (עלות ותמורה בדולרים).", None),
            ("3. הזן פוזיציות פתוחות ומחיר נוכחי.", None),
            ("4. התוצאה למטה: רווח ממומש נטו, הפסדים פתוחים, ופוטנציאל קיזוז משוער.", None),
            ("הגרסה המלאה כוללת המרה לפי שער יציג ליום כל עסקה, יומן מסחר עם R ותגיות טעות, ודשבורד שנתי.", font(bold=True, color="1F2A44")),
        ]
    lines += [
        ("", None),
        ("מקרא צבעים", font(bold=True, size=13)),
        ("תא צהוב = שדה להזנה שלך. שורה כחלחלה = שורת דוגמה (מחק או החלף). תאים לבנים = נוסחאות, לא לגעת.", None),
        ("", None),
        ("חשוב לקרוא", font(bold=True, size=13, color="B42318")),
        ("הכלי מסייע בארגון נתונים בלבד ואינו ייעוץ מס, ייעוץ השקעות או תחליף לרואה חשבון.", None),
        ("החישובים נומינליים ואינם כוללים תיאום אינפלציה, דיבידנדים, ריבית, מס שנוכה במקור או כללים מיוחדים.", None),
        ("שיעור המס והשיטה החלה עליך תלויים בנסיבות האישיות שלך — בדוק עם רו״ח או יועץ מס לפני הגשת דוח או פעולה כלשהי.", None),
    ]
    for i, (t, f) in enumerate(lines, 1):
        c = st.cell(row=i, column=2, value=t); c.font = f or font(size=11)
        c.alignment = Alignment(wrap_text=True, vertical="top")

    lists = wb.create_sheet("רשימות"); setup(lists, {"A": 22, "B": 26, "C": 12})
    setups = ["פריצה עם ווליום", "חציית 10/21", "פולבק לממוצע", "נר היפוך שבועי", "פריצת טווח", "אחר"]
    mistakes = ["ללא טעות", "סטופ צפוף מדי", "יציאה מוקדמת", "מיצוע מטה", "כניסה מאוחרת (רדיפה)", "בלי סטופ", "גודל פוזיציה גדול", "מכירה וקנייה חוזרת", "אחר"]
    for i, h in enumerate(["סטאפים", "תגיות טעות", "כיוון"], 1):
        c = lists.cell(row=1, column=i, value=h); c.font = font(bold=True)
    for i, s in enumerate(setups, 2): lists.cell(row=i, column=1, value=s).font = font()
    for i, s in enumerate(mistakes, 2): lists.cell(row=i, column=2, value=s).font = font()
    for i, s in enumerate(["לונג", "שורט"], 2): lists.cell(row=i, column=3, value=s).font = font()
    lists.cell(row=12, column=1, value="אפשר לערוך את הרשימות — הן מזינות את התפריטים ביומן.").font = font(italic=True, color="555555")

    if not full:
        build_free(wb); wb.move_sheet("רשימות", offset=10); return wb

    # ---------- Rates ----------
    rt = wb.create_sheet("שערים", 1); setup(rt, {"A": 16, "B": 18, "C": 60})
    header(rt, 1, ["תאריך", "שער יציג USD/ILS", "הערה"])
    ex = [(date(2026,1,2),3.70),(date(2026,3,2),3.65),(date(2026,6,1),3.60),(date(2026,9,1),3.62),(date(2026,11,2),3.68)]
    for i,(d,r) in enumerate(ex,2):
        rt.cell(row=i,column=1,value=d).number_format=DATE
        rt.cell(row=i,column=2,value=r).number_format='0.000'
        for c in (1,2):
            rt.cell(row=i,column=c).fill=EX_FILL; rt.cell(row=i,column=c).font=font(color="0000FF")
    rt["C2"] = "ערכי דוגמה בלבד — החלף בשערים היציגים מאתר בנק ישראל. התאריכים חייבים להיות בסדר עולה."
    rt["C2"].font = font(color="B42318"); rt["C2"].alignment = Alignment(wrap_text=True)
    rt["C3"] = "אם אין שער לתאריך מסוים, הכלי לוקח את השער האחרון שלפניו."
    rt["C3"].font = font(color="555555"); rt["C3"].alignment = Alignment(wrap_text=True)
    for r in range(7, 1500):
        rt.cell(row=r,column=1).number_format=DATE; rt.cell(row=r,column=2).number_format='0.000'

    # ---------- Closed trades ----------
    ct = wb.create_sheet("עסקאות סגורות", 2)
    setup(ct, {c: w for c, w in zip("ABCDEFGHIJKLMNO", [10,13,13,9,14,14,13,10,10,14,14,15,15,7,12])})
    header(ct, 1, ["סימול", "תאריך פתיחה", "תאריך סגירה", "כמות", "עלות ($)", "תמורה נטו ($)", "רווח/הפסד ($)",
                   "שער בפתיחה", "שער בסגירה", "עלות (₪)", "תמורה (₪)", "רו״ה בשקלים — שיטה א׳ (₪)", "רו״ה בדולר × שער סגירה — שיטה ב׳ (₪)", "שנה", "בדיקה"])
    rr = "'שערים'!$B$2:$B$1500"; rd = "'שערים'!$A$2:$A$1500"
    for r in range(2, nrows+2):
        ct[f"G{r}"] = f'=IF($A{r}="","",F{r}-E{r})'
        ct[f"H{r}"] = f'=IF($A{r}="","",IFERROR(INDEX({rr},MATCH(B{r},{rd},1)),"חסר שער"))'
        ct[f"I{r}"] = f'=IF($A{r}="","",IFERROR(INDEX({rr},MATCH(C{r},{rd},1)),"חסר שער"))'
        ct[f"J{r}"] = f'=IF($A{r}="","",IFERROR(E{r}*H{r},""))'
        ct[f"K{r}"] = f'=IF($A{r}="","",IFERROR(F{r}*I{r},""))'
        ct[f"L{r}"] = f'=IF($A{r}="","",IFERROR(K{r}-J{r},""))'
        ct[f"M{r}"] = f'=IF($A{r}="","",IFERROR(G{r}*I{r},""))'
        ct[f"N{r}"] = f'=IF($A{r}="","",YEAR(C{r}))'
        ct[f"O{r}"] = f'=IF($A{r}="","",IF(OR(H{r}="חסר שער",I{r}="חסר שער"),"הוסף שער","תקין"))'
        for c in "ABCDEF": ct[f"{c}{r}"].fill = IN_FILL
        for c in "BC": ct[f"{c}{r}"].number_format = DATE
        for c in "EFG": ct[f"{c}{r}"].number_format = USD
        for c in "HI": ct[f"{c}{r}"].number_format = '0.000'
        for c in "JKLM": ct[f"{c}{r}"].number_format = ILS
        for c in "ABCDEFGHIJKLMNO": ct[f"{c}{r}"].font = font()
    # example row
    for c, v in zip("ABCDEF", ["DEMO", date(2026,3,5), date(2026,9,10), 100, 2500, 2300]):
        ct[f"{c}2"] = v; ct[f"{c}2"].fill = EX_FILL; ct[f"{c}2"].font = font(color="0000FF")
    ct.conditional_formatting.add(f"O2:O{nrows+1}", CellIsRule(operator="equal", formula=['"הוסף שער"'], font=Font(name=F, color="B42318", bold=True)))

    # ---------- Open positions ----------
    op = wb.create_sheet("פוזיציות פתוחות", 3); setup(op, {c: w for c, w in zip("ABCDEF", [10,10,16,16,18,18])})
    header(op, 1, ["סימול", "כמות", "מחיר קנייה ממוצע ($)", "מחיר נוכחי ($)", "רו״ה פתוח ($)", "הפסד פתוח בלבד ($)"])
    for r in range(2, 202):
        op[f"E{r}"] = f'=IF($A{r}="","",(D{r}-C{r})*B{r})'
        op[f"F{r}"] = f'=IF($A{r}="","",MIN(0,E{r}))'
        for c in "ABCD": op[f"{c}{r}"].fill = IN_FILL
        for c in "CDEF": op[f"{c}{r}"].number_format = USD
        for c in "ABCDEF": op[f"{c}{r}"].font = font()
    for c, v in zip("ABCD", ["DEMO2", 50, 40, 32]):
        op[f"{c}2"] = v; op[f"{c}2"].fill = EX_FILL; op[f"{c}2"].font = font(color="0000FF")

    # ---------- Journal ----------
    jr = wb.create_sheet("יומן מסחר", 4)
    setup(jr, {c: w for c, w in zip("ABCDEFGHIJKLM", [12,10,18,8,11,11,11,8,12,8,14,22,40])})
    header(jr, 1, ["תאריך", "סימול", "סטאפ", "כיוון", "כניסה ($)", "סטופ ($)", "יציאה ($)", "כמות", "סיכון למניה ($)", "R", "רו״ה ($)", "תגית טעות", "הערות / מה למדתי"])
    dv_s = DataValidation(type="list", formula1="='רשימות'!$A$2:$A$10", allow_blank=True)
    dv_m = DataValidation(type="list", formula1="='רשימות'!$B$2:$B$11", allow_blank=True)
    dv_d = DataValidation(type="list", formula1="='רשימות'!$C$2:$C$3", allow_blank=True)
    for dv in (dv_s, dv_m, dv_d): jr.add_data_validation(dv)
    dv_s.add(f"C2:C{nrows+1}"); dv_m.add(f"L2:L{nrows+1}"); dv_d.add(f"D2:D{nrows+1}")
    for r in range(2, nrows+2):
        jr[f"I{r}"] = f'=IF(OR(E{r}="",F{r}=""),"",ABS(E{r}-F{r}))'
        jr[f"J{r}"] = f'=IF(OR(G{r}="",I{r}="",I{r}=0),"",IF(D{r}="שורט",(E{r}-G{r})/I{r},(G{r}-E{r})/I{r}))'
        jr[f"K{r}"] = f'=IF(OR(G{r}="",H{r}=""),"",IF(D{r}="שורט",(E{r}-G{r})*H{r},(G{r}-E{r})*H{r}))'
        for c in "ABCDEFGHLM": jr[f"{c}{r}"].fill = IN_FILL
        jr[f"A{r}"].number_format = DATE
        for c in "EFGIK": jr[f"{c}{r}"].number_format = USD
        jr[f"J{r}"].number_format = '0.00"R";[Red]-0.00"R";-'
        for c in "ABCDEFGHIJKLM": jr[f"{c}{r}"].font = font()
    for c, v in zip("ABCDEFGHLM", [date(2026,10,6), "DEMO", "פריצה עם ווליום", "לונג", 20, 19, 22.5, 100, "ללא טעות", "דוגמה — מחק שורה זו"]):
        jr[f"{c}2"] = v; jr[f"{c}2"].fill = EX_FILL; jr[f"{c}2"].font = font(color="0000FF")
    jr.conditional_formatting.add(f"K2:K{nrows+1}", CellIsRule(operator="lessThan", formula=["0"], font=Font(name=F, color="B42318")))
    jr.conditional_formatting.add(f"K2:K{nrows+1}", CellIsRule(operator="greaterThan", formula=["0"], font=Font(name=F, color="067647")))

    # ---------- Dashboard ----------
    db = wb.create_sheet("דשבורד", 1); setup(db, {"A": 3, "B": 44, "C": 20, "D": 4, "E": 28, "F": 12, "G": 14})
    db["B2"] = "דשבורד"; db["B2"].font = font(bold=True, size=18)
    inputs = [("שנת מס לבדיקה", 2026, '0'), ("שער USD/ILS נוכחי (להערכת פוזיציות פתוחות)", 3.68, '0.000'), ("שיעור מס להערכה (בדוק מול רו״ח)", 0.25, '0%')]
    for i, (l, v, nf) in enumerate(inputs, 4):
        db[f"B{i}"] = l; db[f"B{i}"].font = font(bold=True)
        db[f"C{i}"] = v; db[f"C{i}"].number_format = nf; db[f"C{i}"].fill = IN_FILL; db[f"C{i}"].font = font(color="0000FF", bold=True); db[f"C{i}"].border = BOX
    CT = "'עסקאות סגורות'"
    yr = "$C$4"
    kpis = [
        ("רווח/הפסד ממומש נטו ($)", f"=SUMIFS({CT}!$G:$G,{CT}!$N:$N,{yr})", USD),
        ("רו״ה ממומש נטו — שיטה א׳ (₪)", f"=SUMIFS({CT}!$L:$L,{CT}!$N:$N,{yr})", ILS),
        ("   מתוכו רווחים (₪)", f'=SUMIFS({CT}!$L:$L,{CT}!$N:$N,{yr},{CT}!$L:$L,">0")', ILS),
        ("   מתוכו הפסדים (₪)", f'=SUMIFS({CT}!$L:$L,{CT}!$N:$N,{yr},{CT}!$L:$L,"<0")', ILS),
        ("רו״ה ממומש נטו — שיטה ב׳ (₪)", f"=SUMIFS({CT}!$M:$M,{CT}!$N:$N,{yr})", ILS),
        ("עסקאות שחסר להן שער", f'=COUNTIFS({CT}!$O:$O,"הוסף שער")', '0'),
        ("הפסדים פתוחים בפוזיציות ($)", "=SUM('פוזיציות פתוחות'!$F:$F)", USD),
        ("הפסדים פתוחים בהערכה (₪)", "=C16*$C$5", ILS),
        ("פוטנציאל קיזוז אם ימומשו (₪)", "=IF(C11>0,MIN(C11,-C17),0)", ILS),
        ("הערכת מס שהקיזוז עשוי לחסוך (₪)", "=C18*$C$6", ILS),
    ]
    db["B9"] = "רווח והפסד לשנה הנבחרת"; db["B9"].font = font(bold=True, size=13)
    # rows 10..19 ; C11= method A net is row 11, positive gains row 12
    for i, (l, f, nf) in enumerate(kpis, 10):
        db[f"B{i}"] = l; db[f"B{i}"].font = font()
        db[f"C{i}"] = f; db[f"C{i}"].number_format = nf; db[f"C{i}"].font = font(bold=True); db[f"C{i}"].fill = KPI_FILL; db[f"C{i}"].border = BOX
    db["B21"] = "שיטה א׳: כל צד מומר לפי השער ביום שלו. שיטה ב׳: הרווח בדולרים כפול השער ביום המכירה. איזו שיטה חלה עליך — שאלה לרו״ח."
    db["B22"] = "פוטנציאל הקיזוז = הקטן מבין הרווחים הממומשים לבין ההפסדים הפתוחים. זו הערכה בלבד ואינה המלצה למכור."
    for c in ("B21","B22"):
        db[c].font = font(size=9, color="555555"); db[c].alignment = Alignment(wrap_text=True)
        db.merge_cells(f"{c}:C{c[1:]}"); db.row_dimensions[int(c[1:])].height = 36

    JR = "'יומן מסחר'"
    db["E9"] = "ביצועים מהיומן (כל השנים)"; db["E9"].font = font(bold=True, size=13)
    js = [("טריידים עם תוצאה", f"=COUNT({JR}!$K:$K)", '0'),
          ("אחוז הצלחה", f'=IFERROR(COUNTIF({JR}!$K:$K,">0")/COUNT({JR}!$K:$K),0)', '0%'),
          ("R ממוצע", f"=IFERROR(AVERAGE({JR}!$J:$J),0)", '0.00'),
          ("רו״ה מצטבר ביומן ($)", f"=SUM({JR}!$K:$K)", USD)]
    for i, (l, f, nf) in enumerate(js, 10):
        db[f"E{i}"] = l; db[f"F{i}"] = f; db[f"F{i}"].number_format = nf
        db[f"E{i}"].font = font(); db[f"F{i}"].font = font(bold=True); db[f"F{i}"].fill = KPI_FILL; db[f"F{i}"].border = BOX
    db["E15"] = "תגית טעות"; db["F15"] = "פעמים"; db["G15"] = "רו״ה ($)"
    for c in ("E15","F15","G15"): db[c].font = font(bold=True, color="FFFFFF"); db[c].fill = H_FILL
    for i in range(10):
        r = 16 + i
        db[f"E{r}"] = f"=IF('רשימות'!B{i+2}=\"\",\"\",'רשימות'!B{i+2})"
        db[f"F{r}"] = f'=IF(E{r}="","",COUNTIF({JR}!$L:$L,E{r}))'
        db[f"G{r}"] = f'=IF(E{r}="","",SUMIF({JR}!$L:$L,E{r},{JR}!$K:$K))'
        db[f"G{r}"].number_format = USD
        for c in "EFG": db[f"{c}{r}"].font = font(); db[f"{c}{r}"].border = BOX
    db["E27"] = "הטעות עם רו״ה השלילי הגדול ביותר — זו הטעות לתקן קודם."
    db["E27"].font = font(size=9, color="555555")

    order = ["התחלה", "דשבורד", "עסקאות סגורות", "פוזיציות פתוחות", "יומן מסחר", "שערים", "רשימות"]
    wb._sheets = [wb[n] for n in order]
    wb.active = 0
    return wb

def build_free(wb):
    ws = wb.create_sheet("מחשבון", 1); setup(ws, {"A": 3, "B": 14, "C": 12, "D": 16, "E": 16, "F": 16, "G": 4})
    ws["B2"] = "מחשבון קיזוז הפסדים — גרסה חינמית"; ws["B2"].font = font(bold=True, size=16)
    ws["B4"] = "שער USD/ILS נוכחי"; ws["B4"].font = font(bold=True)
    ws["D4"] = 3.68; ws["D4"].fill = IN_FILL; ws["D4"].number_format = '0.000'; ws["D4"].font = font(color="0000FF", bold=True)
    ws["E4"] = "← עדכן לשער היום"; ws["E4"].font = font(size=9, color="555555")
    ws["B6"] = "עסקאות שנסגרו השנה"; ws["B6"].font = font(bold=True, size=12)
    for i, h in enumerate(["סימול", "כמות", "עלות ($)", "תמורה נטו ($)", "רו״ה ($)"], 2):
        c = ws.cell(row=7, column=i, value=h); c.font = font(bold=True, color="FFFFFF"); c.fill = H_FILL
    for r in range(8, 28):
        ws[f"F{r}"] = f'=IF(B{r}="","",E{r}-D{r})'
        for c in "BCDE": ws[f"{c}{r}"].fill = IN_FILL
        for c in "DEF": ws[f"{c}{r}"].number_format = USD
        for c in "BCDEF": ws[f"{c}{r}"].font = font()
    for c, v in zip("BCDE", ["DEMO", 100, 2000, 2600]):
        ws[f"{c}8"] = v; ws[f"{c}8"].fill = EX_FILL; ws[f"{c}8"].font = font(color="0000FF")
    ws["B30"] = "פוזיציות פתוחות"; ws["B30"].font = font(bold=True, size=12)
    for i, h in enumerate(["סימול", "כמות", "מחיר קנייה ($)", "מחיר נוכחי ($)", "רו״ה פתוח ($)"], 2):
        c = ws.cell(row=31, column=i, value=h); c.font = font(bold=True, color="FFFFFF"); c.fill = H_FILL
    for r in range(32, 52):
        ws[f"F{r}"] = f'=IF(B{r}="","",(E{r}-D{r})*C{r})'
        for c in "BCDE": ws[f"{c}{r}"].fill = IN_FILL
        for c in "DEF": ws[f"{c}{r}"].number_format = USD
        for c in "BCDEF": ws[f"{c}{r}"].font = font()
    for c, v in zip("BCDE", ["DEMO2", 50, 40, 32]):
        ws[f"{c}32"] = v; ws[f"{c}32"].fill = EX_FILL; ws[f"{c}32"].font = font(color="0000FF")
    res = [("רווח ממומש נטו השנה ($)", "=SUM(F8:F27)", USD),
           ("הפסדים פתוחים ($)", '=SUMIF(F32:F51,"<0")', USD),
           ("פוטנציאל קיזוז ($)", "=IF(D54>0,MIN(D54,-D55),0)", USD),
           ("פוטנציאל קיזוז בהערכה (₪)", "=D56*D4", ILS)]
    for i, (l, f, nf) in enumerate(res, 54):
        ws[f"B{i}"] = l; ws[f"B{i}"].font = font(bold=True)
        ws[f"D{i}"] = f; ws[f"D{i}"].number_format = nf; ws[f"D{i}"].fill = KPI_FILL; ws[f"D{i}"].font = font(bold=True); ws[f"D{i}"].border = BOX
    ws["B59"] = "הערכה גסה בשער אחיד. הגרסה המלאה ממירה כל עסקה לפי השער היציג ביום שלה. אינו ייעוץ מס — בדוק עם רו״ח."
    ws["B59"].font = font(size=9, color="555555")

build(full=True).save("../product/trader-kit-full.xlsx")
build(full=False).save("../product/free-offset-calculator.xlsx")
print("ok")
