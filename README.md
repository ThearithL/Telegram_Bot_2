# Daily Habit & Task Reminder Bot

A Telegram bot that reminds you every day to check in on your daily tasks
(studying, coding, exercise, etc.), tracks streaks, gives you a weekly
report, and speaks both Khmer and English.

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
| `/export` | Download your own data as a JSON file |
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
6. Every Sunday night, the bot automatically sends each user a JSON backup
   of their own tasks and logs (also available anytime via `/export`) —
   this protects your data since Render's free tier storage isn't
   persistent across redeploys.

## Local setup
```bash
pip install -r requirements.txt
set BOT_TOKEN=your_token_from_botfather        # Windows cmd
$env:BOT_TOKEN="your_token_from_botfather"     # Windows PowerShell
python bot.py
```

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
6. Render assigns a `PORT` automatically — the bot's built-in tiny HTTP
   server binds to it so Render sees the service as "live."
7. Add the Render URL to **UptimeRobot** (ping every 5 minutes) so the free
   dyno doesn't spin down from inactivity — this also keeps scheduled
   reminders firing on time.

## Maintenance mode
Run `/maintenance on` (as the admin) to pause the bot for everyone else —
regular users get a "under maintenance" message instead of a response, and
scheduled reminders/weekly backups are skipped while it's on. You (the
admin) still have full access to test. Run `/maintenance off` to resume,
or `/maintenance status` / `/maintenance` (no args) to check the current
state.

## Notes
- Data is stored in a local SQLite file (`habit_bot.db`). On Render's free
  tier the filesystem is **not persistent across deploys/restarts** — the
  weekly `/export` backup sent to each user's Telegram chat is the safety
  net for this; consider a paid persistent disk if you want the server
  itself to keep data across redeploys.
- Timezone is hardcoded to UTC+7 (Asia/Phnom_Penh) in `bot.py` — change
  `TIMEZONE_OFFSET_HOURS` if needed. The weekly backup runs Sunday 23:55.