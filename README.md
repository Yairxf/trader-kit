# ערכת הסוחר הישראלי

חנות דיגיטלית ב-0 ₪: דף נחיתה סטטי, מוצר Excel, משפך מיילים ואוטומציה על ה-VPS.

```
site/        דף הנחיתה (Cloudflare Pages). config.js = הקובץ היחיד לעריכה
  downloads/ המחשבון החינמי (ציבורי בכוונה)
product/     המוצר בתשלום — מעלים ל-Lemon Squeezy, לא לאתר
  trader-kit-full.xlsx   הערכה המלאה
  free-offset-calculator.xlsx
  guide.pdf              מדריך התחלה לקונה
vps/         סקריפטים ל-Windows VPS
  setup.ps1              התקנה חד-פעמית
  make_short.py          תסריט → סרטון 9:16 עם קריינות וכתוביות
  n8n-lemonsqueezy-to-mailerlite.json   קונה → קבוצת buyers
content/
  scripts/               5 תסריטים מוכנים לסרטונים
  hooks-and-prompts.md   15 הוקים + פרומפטים
  email-sequence.md      5 מיילים לאוטומציה
```

---

## מה נשאר לך לעשות (בסדר הזה)

### 0. לפני המכירה הראשונה
- [ ] פתיחת תיק עוסק ברשות המסים (מקוון, ללא עלות). בדוק עם רו״ח איזה סוג מתאים.
- [ ] שיחה קצרה עם רו״ח/יועץ מס על הניסוח של המוצר והסרטונים (כלי לארגון נתונים, לא ייעוץ).

### 1. אתר — Cloudflare Pages (5 דקות)
1. dash.cloudflare.com → Workers & Pages → Create → Pages → Connect to Git → בחר `trader-kit`.
2. Build command: **ריק**. Build output directory: **`site`**.
3. Deploy. מקבלים `trader-kit.pages.dev` (או שם דומה).
4. באותו מסך: Web Analytics → Enable.

### 2. תשלומים — Lemon Squeezy (15 דקות)
1. הרשמה ב-lemonsqueezy.com, יצירת Store, השלמת פרטי תשלום (בדוק שמשיכה לישראל נתמכת לחשבון שלך).
2. Products → New: "ערכת הסוחר הישראלי", מחיר המקביל ל-69 ₪, קבצים: `product/trader-kit-full.xlsx` + `product/guide.pdf`.
3. Discounts → קוד `FIRST50`, ‏30%, מוגבל ל-50 שימושים.
4. Affiliates → הפעלה, עמלה 30%.
5. Share → העתק את ה-**Checkout URL** → שלח לי (או הדבק ב-`site/config.js` → `CHECKOUT_URL`).

### 3. מיילים — MailerLite (20 דקות)
1. הרשמה (Free). Subscribers → Groups: צור `free-calculator` ו-`buyers`.
2. Forms → Embedded form → מחובר לקבוצה `free-calculator`, ובהגדרות: אחרי הרשמה redirect ל-`https://<האתר>/thanks.html`.
3. מה-HTML של הטופס העתק את ה-`action` (נראה כמו `https://assets.mailerlite.com/jsonp/.../subscribe`) → `MAILERLITE_ACTION` ב-config.js.
4. Automations → New → טריגר "joins group free-calculator" → העתק את 5 המיילים מ-`content/email-sequence.md`. הוסף תנאי יציאה: חבר בקבוצה `buyers`.
5. Integrations → API → צור מפתח (לשלב 4). **אל תשלח לי אותו בצ'אט** — מזינים אותו רק ב-VPS.

### 4. VPS (Windows)
```powershell
git clone https://github.com/Yairxf/trader-kit C:\trader-kit
cd C:\trader-kit\vps
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1          # שואל על MailerLite API key ו-Group ID של buyers
```
אחר כך:
1. פתח `http://localhost:5678` → צור משתמש → Workflows → Import from file → `n8n-lemonsqueezy-to-mailerlite.json` → Activate.
2. חשיפה ציבורית: `cloudflared tunnel --url http://localhost:5678` מחזיר כתובת `https://xxxx.trycloudflare.com`.
   הכתובת הזמנית מתחלפת בכל הפעלה; לכתובת קבועה צריך דומיין ב-Cloudflare ו-Named Tunnel.
3. Lemon Squeezy → Settings → Webhooks → URL: `https://<tunnel>/webhook/<הנתיב מ-vps/WEBHOOK_PATH.txt>`, אירוע `order_created`.
4. בדיקה: קנייה עם מצב Test Mode ב-Lemon Squeezy → המייל אמור להופיע בקבוצה `buyers`.

### 5. סרטונים
1. פתח את `product/trader-kit-full.xlsx` עם **נתוני הדמה בלבד** והקלט מסך של 20–30 שניות (OBS, חינם) → `vps\backgrounds\screen.mp4`.
2. `python make_short.py --all ..\content\scripts backgrounds\screen.mp4 out`
3. העלאה דרך TikTok Studio / YouTube Studio / Meta Business Suite עם תזמון. בלי בוטים ובלי חשבונות כפולים.
4. תסריטים 1 ו-2 עדיף לצלם בפנים שלך — קריינות סינתטית מתאימה יותר לסרטוני הסבר.

---

## הערות
- המוצר בתשלום **לא** נמצא בתיקיית `site` ולכן לא נגיש מהאתר. ה-repo חייב להישאר פרטי.
- `site/downloads/free-offset-calculator.xlsx` ציבורי בכוונה (מגנט הלידים).
- `legal.html` הוא טיוטה — כדאי שעו״ד יעבור עליו.
- לשינוי המוצר: `python build_kit.py` (בתיקיית tools) מייצר מחדש את שני קבצי ה-xlsx.
