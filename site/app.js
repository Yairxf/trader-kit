(function () {
  var K = window.KIT || {};
  var ils = new Intl.NumberFormat("he-IL", { style: "currency", currency: "ILS", maximumFractionDigits: 0 });

  // checkout links
  document.querySelectorAll(".checkout").forEach(function (a) {
    if (K.CHECKOUT_URL) a.href = K.CHECKOUT_URL;
    else a.addEventListener("click", function (e) { e.preventDefault(); alert("קישור התשלום עוד לא הוגדר (config.js)."); });
  });
  if (K.CONTACT_EMAIL) document.querySelectorAll(".contact").forEach(function (a) { a.href = "mailto:" + K.CONTACT_EMAIL; });

  // days until Dec 31 (Israel time)
  function daysLeft() {
    var now = new Date(new Date().toLocaleString("en-US", { timeZone: "Asia/Jerusalem" }));
    var end = new Date(now.getFullYear(), 11, 31, 23, 59, 59);
    return Math.max(0, Math.ceil((end - now) / 864e5));
  }
  var d = daysLeft();
  var clock = document.getElementById("clock");
  var big = document.getElementById("days-left");
  if (d > 0 && d < 75) {
    clock.textContent = "נשארו " + d + " ימים עד 31.12";
    big.textContent = "נשארו " + d + " ימים לסדר את המספרים של השנה.";
  } else {
    clock.textContent = "";
    big.textContent = "הדוח השנתי יגיע. עדיף שהמספרים יהיו מוכנים.";
  }

  // hero calculator
  function num(id) { var v = parseFloat(String(document.getElementById(id).value).replace(/[^\d.\-]/g, "")); return isNaN(v) ? 0 : v; }
  function calc() {
    var gain = num("gain"), loss = Math.abs(num("loss")), fx = num("fx") || 0;
    var off = gain > 0 ? Math.min(gain, loss) : 0;
    document.getElementById("offset").textContent = ils.format(off * fx);
    document.getElementById("saving").textContent = ils.format(off * fx * 0.25);
  }
  ["gain", "loss", "fx"].forEach(function (id) { document.getElementById(id).addEventListener("input", calc); });
  calc();

  // email signup → MailerLite → thanks page
  var form = document.getElementById("signup"), msg = document.getElementById("form-msg");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var email = document.getElementById("email").value.trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { msg.className = "form-msg err"; msg.textContent = "הכתובת לא נראית תקינה. בדוק ונסה שוב."; return; }
    if (!K.MAILERLITE_ACTION) { location.href = "/thanks.html"; return; }
    msg.className = "form-msg"; msg.textContent = "שולח…";
    var fd = new FormData(); fd.append("fields[email]", email); fd.append("ml-submit", "1"); fd.append("anticsrf", "true");
    fetch(K.MAILERLITE_ACTION, { method: "POST", body: fd, mode: "no-cors" })
      .then(function () { location.href = "/thanks.html"; })
      .catch(function () { msg.className = "form-msg err"; msg.textContent = "השליחה נכשלה. בדוק את החיבור ונסה שוב."; });
  });
})();
