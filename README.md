# Daily Habit & Task Reminder Bot

A Telegram bot that reminds you every day at a set time to check in on your
daily tasks (studying, coding, exercise, etc.), tracks streaks, and gives you
a weekly completion report.

## Commands
| Command | Description |
|---|---|
| `/start` | Register and see instructions |
| `/addtask <name>` | Add a daily task to track |
| `/removetask <name>` | Remove a task |
| `/mytasks` | List your tasks and current streaks |
| `/settime HH:MM` | Set your daily check-in time (24h, Phnom Penh time) |
| `/checkin` | Trigger a check-in immediately (for testing) |
| `/stats` | See your 7-day completion report |

## How it works
1. Add the tasks you want to track daily with `/addtask`.
2. Every day at your chosen time, the bot sends a message with a button for
   each task.
3. Tap the tasks you completed (they toggle ✅ / ⬜), then tap
   **Confirm today's check-in**.
4. Streaks increase when you complete a task on consecutive days, and reset
   to 0 if you miss a day.

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
5. Add an environment variable: `BOT_TOKEN` = your bot token from @BotFather.
6. Render assigns a `PORT` automatically — the bot's built-in tiny HTTP
   server binds to it so Render sees the service as "live."
7. Add the Render URL to **UptimeRobot** (ping every 5 minutes) so the free
   dyno doesn't spin down from inactivity.

## Notes
- Data is stored in a local SQLite file (`habit_bot.db`). On Render's free
  tier the filesystem is **not persistent across deploys/restarts** — if you
  need data to survive redeploys, consider Render's paid persistent disk, or
  swap SQLite for a hosted database later.
- Timezone is hardcoded to UTC+7 (Asia/Phnom_Penh) in `bot.py` — change
  `TIMEZONE_OFFSET_HOURS` if needed.
