# Daily Habit & Task Reminder Bot

A Telegram bot that reminds you every day to check in on your daily tasks
(studying, coding, exercise, etc.), tracks streaks, and speaks both Khmer
and English.

## Commands
| Command | Description |
|---|---|
| `/start` | Register and see instructions |
| `/addtask <name>` | Add a daily task to track |
| `/removetask <name>` | Remove a task |
| `/mytasks` | List your tasks and current streaks |
| `/addtime HH:MM` | Add a daily reminder time (you can have several) |
| `/removetime HH:MM` | Remove a reminder time |
| `/mytimes` | List all your reminder times |
| `/checkin` | Trigger a check-in immediately (for testing) |
| `/stats` | See your 7-day completion report |
| `/export` | Download your own data as an Excel (.xlsx) file |
| `/language` | Switch between Khmer and English |
| `/maintenance on\|off\|status` | Admin-only: pause/resume the bot for regular users |

## How it works
1. Add the tasks you want to track daily with `/addtask`.
2. Add one or more daily reminder times with `/addtime HH:MM` (e.g. a
   morning and an evening check-in).
3. At each reminder time, the bot sends a message with a button for each
   task, plus a motivational quote.
4. Tap the tasks you completed (they toggle ✅ / ⬜), then tap
   **Confirm check-in** — or tap **Snooze 1 hour** to get reminded again
   later instead.
5. Streaks increase when you complete a task on consecutive days, and reset
   to 0 if you miss a day. Hitting a 7 / 30 / 100-day streak earns a badge.
6. Run `/export` any time to get a `.xlsx` file with two sheets: **Tasks**
   (name, current streak, best streak, total check-ins, completed count)
   and **Logs** (every task/date/done entry), ready to open in Excel,
   Google Sheets, or LibreOffice.

## Local setup
```bash
pip install -r requirements.txt
set BOT_TOKEN=your_token_from_botfather        # Windows cmd
$env:BOT_TOKEN="your_token_from_botfather"     # Windows PowerShell
python bot.py
```
Without any Turso env vars set, it just uses a local `habit_bot.db` file —
perfect for local development and testing.

## Deploying on Render (free tier)
1. Push this folder to a GitHub repo.
2. On Render: **New +** → **Web Service** → connect your repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `python bot.py`
5. Add environment variables:
   - `BOT_TOKEN` = your bot token from @BotFather.
   - `ADMIN_CHAT_ID` = your own Telegram chat_id (message [@userinfobot](https://t.me/userinfobot)
     to get it). This unlocks `/maintenance` for you and exempts you from
     maintenance mode.
   - `DASHBOARD_PASSWORD` = a password for the web control panel (see below).
   - `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` — see **Permanent storage**
     below. Without these two, your data is wiped every time Render
     redeploys the service.
6. Render assigns a `PORT` automatically — the bot's built-in dashboard
   server binds to it so Render sees the service as "live."
7. Add the Render URL + `/ping` (e.g. `https://your-app.onrender.com/ping`)
   to **UptimeRobot** (ping every 5 minutes) so the free dyno doesn't spin
   down from inactivity — this also keeps scheduled reminders firing on
   time.

## Permanent storage (free, via Turso)
Render's free tier wipes the local disk on every redeploy/restart, so a
plain SQLite file can't live there permanently. This bot solves that for
**free** using [Turso](https://turso.tech) — a hosted SQLite-compatible
database with a generous free tier. The bot keeps reading and writing a
normal local SQLite file (same speed, same SQL as before), and
automatically syncs every write up to your Turso database in the cloud
whenever a connection closes. On startup it pulls the latest data back
down first, so a redeploy never loses anything.

**One-time setup (about 5 minutes):**
1. Install the Turso CLI and sign in (free, no credit card):
   ```bash
   curl -sSfL https://get.tur.so/install.sh | bash   # macOS/Linux/WSL
   turso auth login                                   # opens a browser to log in
   ```
2. Create a database:
   ```bash
   turso db create habit-bot
   ```
3. Get your connection URL and an auth token:
   ```bash
   turso db show habit-bot --url
   turso db tokens create habit-bot
   ```
4. Add both as environment variables on Render (and locally, if you want
   to test against Turso before deploying):
   - `TURSO_DATABASE_URL` = the `libsql://...` URL from step 3.
   - `TURSO_AUTH_TOKEN` = the token from step 3.
5. Redeploy. The dashboard (see below) will show a **☁️ Turso Cloud — data
   is permanent** badge once it's picked up correctly. If you ever see
   **💾 Local only — data resets on redeploy** instead, double-check both
   env vars are set exactly as Turso gave them to you, and that
   `libsql-experimental` installed correctly (it's in `requirements.txt`).

If you skip this setup, the bot still works fine — it just falls back to a
plain local SQLite file, and you'll lose data on every Render redeploy.

## Maintenance mode
Run `/maintenance on` (as the admin) to pause the bot for everyone else —
regular users get an "under maintenance" message instead of a response,
and scheduled reminders are skipped while it's on. You (the admin) still
have full access to test. Run `/maintenance off` to resume, or
`/maintenance status` / `/maintenance` (no args) to check the current
state. You can also toggle it from the **web dashboard** below.

## Web dashboard
The bot serves a small password-protected control panel on the same port
Render exposes:

- **URL**: your Render URL, e.g. `https://your-app.onrender.com/`
- **Login**: the password in the `DASHBOARD_PASSWORD` env var (set one —
  it defaults to `changeme`, which is logged as a warning if left unset).
- Shows: maintenance status, a database status badge (Turso Cloud vs.
  local-only), a one-click maintenance toggle, total users/tasks,
  check-ins today/this week, a 14-day check-in chart, language split,
  top streaks, and a per-user table (chat_id, language, task count,
  reminder times).
- UptimeRobot should ping `/ping` instead of `/` (the root now requires
  login, `/ping` stays open and unauthenticated).

Add these env vars on Render alongside `BOT_TOKEN` and `ADMIN_CHAT_ID`:
- `DASHBOARD_PASSWORD` — the login password for the dashboard.
- `FLASK_SECRET_KEY` — (optional) a random string for session signing; if
  omitted a random one is generated at startup, which just means you'll
  be logged out on every redeploy.

## Notes
- Data lives in a local SQLite file (`habit_bot.db`) that's automatically
  synced to Turso Cloud when `TURSO_DATABASE_URL`/`TURSO_AUTH_TOKEN` are
  set (see **Permanent storage** above) — no manual backups needed.
- Timezone is hardcoded to UTC+7 (Asia/Phnom_Penh) in `bot.py` — change
  `TIMEZONE_OFFSET_HOURS` if needed.