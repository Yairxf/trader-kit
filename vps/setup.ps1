# setup.ps1 — הרצה חד-פעמית ב-VPS (PowerShell כמנהל)
# מתקין: Python, ffmpeg, Node, edge-tts, n8n, cloudflared, NSSM
$ErrorActionPreference = "Stop"

winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
winget install -e --id Gyan.FFmpeg
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Cloudflare.cloudflared
winget install -e --id NSSM.NSSM

# רענון PATH בחלון הנוכחי
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

python -m pip install --upgrade pip
python -m pip install edge-tts
npm install -g n8n

# משתני סביבה ל-n8n (הזן את המפתחות שלך)
$mlKey   = Read-Host "MailerLite API key (Integrations -> API)"
$mlGroup = Read-Host "MailerLite group ID for buyers (Subscribers -> Groups)"
[System.Environment]::SetEnvironmentVariable("MAILERLITE_API_KEY", $mlKey, "Machine")
[System.Environment]::SetEnvironmentVariable("MAILERLITE_BUYERS_GROUP", $mlGroup, "Machine")
[System.Environment]::SetEnvironmentVariable("N8N_BLOCK_ENV_ACCESS_IN_NODE", "false", "Machine")

# n8n כשירות Windows שעולה אחרי אתחול
$n8n = (Get-Command n8n.cmd).Source
nssm install n8n $n8n start
nssm set n8n AppEnvironmentExtra MAILERLITE_API_KEY=$mlKey MAILERLITE_BUYERS_GROUP=$mlGroup N8N_BLOCK_ENV_ACCESS_IN_NODE=false
nssm start n8n

Write-Host ""
Write-Host "n8n רץ על http://localhost:5678 — פתח בדפדפן של ה-VPS, צור משתמש, וייבא את vps\n8n-lemonsqueezy-to-mailerlite.json"
Write-Host "לחשיפה ל-Lemon Squeezy בלי לפתוח פורטים:  cloudflared tunnel --url http://localhost:5678"
Write-Host "(ל-URL קבוע: cloudflared tunnel login  ואז צור Named Tunnel — ראה README)"
