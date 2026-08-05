"""
Daily Habit & Task Reminder Telegram Bot
==========================================
Features:
  - Each user can add their own daily tasks to track (study, code, exercise, etc.)
  - Set a personal daily reminder time (e.g. 20:00)
  - At that time, the bot sends a check-in message with tappable buttons
  - Tracks streaks (consecutive days completed) per task
  - /stats shows a 7-day completion report

Run:
    pip install -r requirements.txt
    python bot.py

Environment variable required:
    BOT_TOKEN   - your Telegram bot token from @BotFather

Timezone:
    Defaults to Asia/Phnom_Penh (UTC+7). Change TIMEZONE_OFFSET_HOURS below if needed.
"""

import os
import sqlite3
import logging
import asyncio
import threading
from datetime import datetime, time, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "PUT_YOUR_TOKEN_HERE")
TIMEZONE_OFFSET_HOURS = 7  # Asia/Phnom_Penh (UTC+7), no DST
TZ = timezone(timedelta(hours=TIMEZONE_OFFSET_HOURS))
DB_PATH = os.path.join(os.path.dirname(__file__), "habit_bot.db")
DEFAULT_REMINDER_HOUR = 20
DEFAULT_REMINDER_MINUTE = 0

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# In-memory: pending (not-yet-confirmed) check-in state per chat_id
# { chat_id: { task_id: bool } }
pending_checkins = {}


# ------------------------------------------------------------------
# DATABASE
# ------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            reminder_hour INTEGER DEFAULT 20,
            reminder_minute INTEGER DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            name TEXT,
            streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            last_done_date TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            date TEXT,
            done INTEGER
        )
    """)
    conn.commit()
    conn.close()


def today_str():
    return datetime.now(TZ).strftime("%Y-%m-%d")


def yesterday_str():
    return (datetime.now(TZ) - timedelta(days=1)).strftime("%Y-%m-%d")


# ------------------------------------------------------------------
# COMMANDS
# ------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (chat_id, reminder_hour, reminder_minute) VALUES (?, ?, ?)",
        (chat_id, DEFAULT_REMINDER_HOUR, DEFAULT_REMINDER_MINUTE),
    )
    conn.commit()
    conn.close()

    schedule_user_reminder(context.application, chat_id, DEFAULT_REMINDER_HOUR, DEFAULT_REMINDER_MINUTE)

    await update.message.reply_text(
        "👋 Welcome to your Daily Habit Bot!\n\n"
        "Commands:\n"
        "/addtask <name> - add a daily task to track\n"
        "/removetask <name> - remove a task\n"
        "/mytasks - list your tasks\n"
        "/settime HH:MM - set your daily check-in time (24h format)\n"
        "/checkin - trigger a check-in right now (for testing)\n"
        "/stats - see your 7-day completion report\n\n"
        f"Default reminder time is {DEFAULT_REMINDER_HOUR:02d}:{DEFAULT_REMINDER_MINUTE:02d} "
        "(Phnom Penh time). Use /settime to change it."
    )


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Usage: /addtask <task name>\nExample: /addtask Study Python")
        return
    name = " ".join(context.args).strip()

    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM tasks WHERE chat_id=? AND name=?", (chat_id, name)
    ).fetchone()
    if existing:
        await update.message.reply_text(f"⚠️ You already have a task called '{name}'.")
        conn.close()
        return

    conn.execute("INSERT INTO tasks (chat_id, name) VALUES (?, ?)", (chat_id, name))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Added daily task: {name}")


async def remove_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Usage: /removetask <task name>")
        return
    name = " ".join(context.args).strip()

    conn = get_conn()
    task = conn.execute(
        "SELECT id FROM tasks WHERE chat_id=? AND name=?", (chat_id, name)
    ).fetchone()
    if not task:
        await update.message.reply_text(f"⚠️ No task found named '{name}'.")
        conn.close()
        return

    conn.execute("DELETE FROM tasks WHERE id=?", (task["id"],))
    conn.execute("DELETE FROM logs WHERE task_id=?", (task["id"],))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"🗑️ Removed task: {name}")


async def my_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conn = get_conn()
    tasks = conn.execute(
        "SELECT name, streak, best_streak FROM tasks WHERE chat_id=?", (chat_id,)
    ).fetchall()
    conn.close()

    if not tasks:
        await update.message.reply_text("You have no tasks yet. Add one with /addtask <name>")
        return

    lines = ["📋 Your daily tasks:\n"]
    for t in tasks:
        lines.append(f"• {t['name']}  (streak: {t['streak']} 🔥, best: {t['best_streak']})")
    await update.message.reply_text("\n".join(lines))


async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args or ":" not in context.args[0]:
        await update.message.reply_text("Usage: /settime HH:MM  (24-hour format, e.g. /settime 21:30)")
        return

    try:
        hour, minute = map(int, context.args[0].split(":"))
        assert 0 <= hour <= 23 and 0 <= minute <= 59
    except (ValueError, AssertionError):
        await update.message.reply_text("⚠️ Invalid time. Use 24h format like 21:30.")
        return

    conn = get_conn()
    conn.execute(
        "INSERT INTO users (chat_id, reminder_hour, reminder_minute) VALUES (?, ?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET reminder_hour=?, reminder_minute=?",
        (chat_id, hour, minute, hour, minute),
    )
    conn.commit()
    conn.close()

    schedule_user_reminder(context.application, chat_id, hour, minute)

    await update.message.reply_text(f"⏰ Daily check-in time set to {hour:02d}:{minute:02d} (Phnom Penh time).")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conn = get_conn()
    tasks = conn.execute("SELECT id, name FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()

    if not tasks:
        await update.message.reply_text("You have no tasks yet. Add one with /addtask <name>")
        conn.close()
        return

    cutoff = (datetime.now(TZ) - timedelta(days=7)).strftime("%Y-%m-%d")
    lines = ["📊 Last 7 days:\n"]
    for t in tasks:
        logs = conn.execute(
            "SELECT done FROM logs WHERE task_id=? AND date>=?", (t["id"], cutoff)
        ).fetchall()
        done_count = sum(1 for l in logs if l["done"])
        total = len(logs) if logs else 0
        pct = f"{(done_count/total*100):.0f}%" if total else "n/a"
        lines.append(f"• {t['name']}: {done_count} done / {total} logged ({pct})")
    conn.close()
    await update.message.reply_text("\n".join(lines))


# ------------------------------------------------------------------
# CHECK-IN FLOW (inline buttons)
# ------------------------------------------------------------------
def build_checkin_keyboard(chat_id):
    state = pending_checkins.get(chat_id, {})
    conn = get_conn()
    tasks = conn.execute("SELECT id, name FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()

    rows = []
    for t in tasks:
        checked = state.get(t["id"], False)
        label = f"{'✅' if checked else '⬜'} {t['name']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"toggle:{t['id']}")])
    rows.append([InlineKeyboardButton("✔️ Confirm today's check-in", callback_data="confirm")])
    return InlineKeyboardMarkup(rows)


async def send_checkin(chat_id, context: ContextTypes.DEFAULT_TYPE):
    conn = get_conn()
    tasks = conn.execute("SELECT id FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()
    if not tasks:
        return  # nothing to check in on

    pending_checkins[chat_id] = {t["id"]: False for t in tasks}
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🌙 Daily check-in — {today_str()}\nTap each task you completed today, then Confirm:",
        reply_markup=build_checkin_keyboard(chat_id),
    )


async def manual_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_checkin(update.effective_chat.id, context)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()

    if chat_id not in pending_checkins:
        pending_checkins[chat_id] = {}

    if query.data.startswith("toggle:"):
        task_id = int(query.data.split(":")[1])
        current = pending_checkins[chat_id].get(task_id, False)
        pending_checkins[chat_id][task_id] = not current
        await query.edit_message_reply_markup(reply_markup=build_checkin_keyboard(chat_id))

    elif query.data == "confirm":
        state = pending_checkins.get(chat_id, {})
        conn = get_conn()
        summary_lines = []
        date = today_str()
        for task_id, done in state.items():
            task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not task:
                continue

            # avoid duplicate log for the same day
            existing_log = conn.execute(
                "SELECT id FROM logs WHERE task_id=? AND date=?", (task_id, date)
            ).fetchone()
            if existing_log:
                conn.execute("UPDATE logs SET done=? WHERE id=?", (1 if done else 0, existing_log["id"]))
            else:
                conn.execute(
                    "INSERT INTO logs (task_id, date, done) VALUES (?, ?, ?)",
                    (task_id, date, 1 if done else 0),
                )

            # update streak
            if done:
                new_streak = task["streak"] + 1 if task["last_done_date"] == yesterday_str() else 1
                best = max(new_streak, task["best_streak"])
                conn.execute(
                    "UPDATE tasks SET streak=?, best_streak=?, last_done_date=? WHERE id=?",
                    (new_streak, best, date, task_id),
                )
                summary_lines.append(f"✅ {task['name']} — streak {new_streak} 🔥")
            else:
                conn.execute("UPDATE tasks SET streak=0 WHERE id=?", (task_id,))
                summary_lines.append(f"❌ {task['name']} — streak reset")

        conn.commit()
        conn.close()
        pending_checkins.pop(chat_id, None)

        await query.edit_message_text(
            f"🌙 Check-in complete — {date}\n\n" + "\n".join(summary_lines)
        )


# ------------------------------------------------------------------
# SCHEDULING
# ------------------------------------------------------------------
def schedule_user_reminder(application: Application, chat_id: int, hour: int, minute: int):
    job_name = f"reminder_{chat_id}"
    for job in application.job_queue.get_jobs_by_name(job_name):
        job.schedule_removal()

    application.job_queue.run_daily(
        callback=lambda ctx: send_checkin(chat_id, ctx),
        time=time(hour=hour, minute=minute, tzinfo=TZ),
        name=job_name,
        chat_id=chat_id,
    )


async def schedule_all_users(application: Application):
    conn = get_conn()
    users = conn.execute("SELECT chat_id, reminder_hour, reminder_minute FROM users").fetchall()
    conn.close()
    for u in users:
        schedule_user_reminder(application, u["chat_id"], u["reminder_hour"], u["reminder_minute"])


# ------------------------------------------------------------------
# TINY HTTP SERVER (for UptimeRobot keep-alive on Render free tier)
# ------------------------------------------------------------------
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Daily Habit Bot is running")

    def log_message(self, format, *args):
        pass  # silence default logging


def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
async def post_init(application: Application):
    await schedule_all_users(application)


def main():
    if BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        # Debug: show which env var keys Render actually sees (no values, no secrets)
        env_keys = sorted(os.environ.keys())
        logger.error("BOT_TOKEN not found. Available env var keys: %s", env_keys)
        raise RuntimeError("Set the BOT_TOKEN environment variable before running.")

    init_db()

    threading.Thread(target=run_http_server, daemon=True).start()

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addtask", add_task))
    application.add_handler(CommandHandler("removetask", remove_task))
    application.add_handler(CommandHandler("mytasks", my_tasks))
    application.add_handler(CommandHandler("settime", set_time))
    application.add_handler(CommandHandler("checkin", manual_checkin))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot starting...")

    # Python 3.13+/3.14 removed the implicit "create a loop if none exists"
    # behavior of asyncio.get_event_loop(), which older python-telegram-bot/
    # APScheduler internals still rely on. Create and set one explicitly so
    # run_polling() has an event loop to attach to regardless of Python version.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()