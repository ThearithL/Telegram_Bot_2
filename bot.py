"""
Daily Habit & Task Reminder Telegram Bot
==========================================
Features:
  - Each user can add their own daily tasks to track (study, code, exercise, etc.)
  - Set a personal daily reminder time (e.g. 20:00)
  - At that time, the bot sends a check-in message with tappable buttons
  - Tracks streaks (consecutive days completed) per task
  - /stats shows a 7-day completion report
  - Bilingual: Khmer (ខ្មែរ) and English, switch anytime with /language

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
DEFAULT_LANGUAGE = "km"  # "km" = Khmer, "en" = English

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# In-memory: pending (not-yet-confirmed) check-in state per chat_id
# { chat_id: { task_id: bool } }
pending_checkins = {}


# ------------------------------------------------------------------
# TRANSLATIONS
# ------------------------------------------------------------------
TEXT = {
    "welcome": {
        "km": (
            "👋 សូមស្វាគមន៍មកកាន់ Daily Habit Bot!\n\n"
            "Commands:\n"
            "/addtask <ឈ្មោះ> - បន្ថែម task ថ្មីត្រូវតាមដានប្រចាំថ្ងៃ\n"
            "/removetask <ឈ្មោះ> - លុប task\n"
            "/mytasks - មើលបញ្ជី task របស់អ្នក\n"
            "/settime HH:MM - កំណត់ម៉ោងជូនដំណឹងប្រចាំថ្ងៃ (ទម្រង់ 24h)\n"
            "/checkin - សាកល្បង check-in ភ្លាមៗ\n"
            "/stats - មើលរបាយការណ៍ 7 ថ្ងៃចុងក្រោយ\n"
            "/language - ប្តូរភាសា (ខ្មែរ/English)\n\n"
            "ម៉ោងជូនដំណឹង default គឺ {hour:02d}:{minute:02d} (ម៉ោងកម្ពុជា)។ "
            "ប្រើ /settime ដើម្បីប្តូរ។"
        ),
        "en": (
            "👋 Welcome to your Daily Habit Bot!\n\n"
            "Commands:\n"
            "/addtask <name> - add a daily task to track\n"
            "/removetask <name> - remove a task\n"
            "/mytasks - list your tasks\n"
            "/settime HH:MM - set your daily check-in time (24h format)\n"
            "/checkin - trigger a check-in right now (for testing)\n"
            "/stats - see your 7-day completion report\n"
            "/language - switch language (Khmer/English)\n\n"
            "Default reminder time is {hour:02d}:{minute:02d} (Phnom Penh time). "
            "Use /settime to change it."
        ),
    },
    "addtask_usage": {
        "km": "របៀបប្រើ: /addtask <ឈ្មោះ task>\nឧទាហរណ៍: /addtask សិក្សា Python",
        "en": "Usage: /addtask <task name>\nExample: /addtask Study Python",
    },
    "addtask_duplicate": {
        "km": "⚠️ អ្នកមាន task ឈ្មោះ '{name}' រួចហើយ។",
        "en": "⚠️ You already have a task called '{name}'.",
    },
    "addtask_success": {
        "km": "✅ បានបន្ថែម task ប្រចាំថ្ងៃ: {name}",
        "en": "✅ Added daily task: {name}",
    },
    "removetask_usage": {
        "km": "របៀបប្រើ: /removetask <ឈ្មោះ task>",
        "en": "Usage: /removetask <task name>",
    },
    "removetask_notfound": {
        "km": "⚠️ រកមិនឃើញ task ឈ្មោះ '{name}' ទេ។",
        "en": "⚠️ No task found named '{name}'.",
    },
    "removetask_success": {
        "km": "🗑️ បានលុប task: {name}",
        "en": "🗑️ Removed task: {name}",
    },
    "mytasks_empty": {
        "km": "អ្នកមិនទាន់មាន task ទេ។ បន្ថែមមួយជាមួយ /addtask <ឈ្មោះ>",
        "en": "You have no tasks yet. Add one with /addtask <name>",
    },
    "mytasks_header": {
        "km": "📋 Task ប្រចាំថ្ងៃរបស់អ្នក:\n",
        "en": "📋 Your daily tasks:\n",
    },
    "mytasks_line": {
        "km": "• {name}  (streak: {streak} 🔥, ល្អបំផុត: {best})",
        "en": "• {name}  (streak: {streak} 🔥, best: {best})",
    },
    "settime_usage": {
        "km": "របៀបប្រើ: /settime HH:MM  (ទម្រង់ 24h ឧ. /settime 21:30)",
        "en": "Usage: /settime HH:MM  (24-hour format, e.g. /settime 21:30)",
    },
    "settime_invalid": {
        "km": "⚠️ ម៉ោងមិនត្រឹមត្រូវ។ សូមប្រើទម្រង់ 24h ដូចជា 21:30",
        "en": "⚠️ Invalid time. Use 24h format like 21:30.",
    },
    "settime_success": {
        "km": "⏰ បានកំណត់ម៉ោង check-in ប្រចាំថ្ងៃទៅ {hour:02d}:{minute:02d} (ម៉ោងកម្ពុជា)។",
        "en": "⏰ Daily check-in time set to {hour:02d}:{minute:02d} (Phnom Penh time).",
    },
    "stats_empty": {
        "km": "អ្នកមិនទាន់មាន task ទេ។ បន្ថែមមួយជាមួយ /addtask <ឈ្មោះ>",
        "en": "You have no tasks yet. Add one with /addtask <name>",
    },
    "stats_header": {
        "km": "📊 7 ថ្ងៃចុងក្រោយ:\n",
        "en": "📊 Last 7 days:\n",
    },
    "stats_line": {
        "km": "• {name}: បានធ្វើ {done} / កត់ត្រា {total} ({pct})",
        "en": "• {name}: {done} done / {total} logged ({pct})",
    },
    "checkin_prompt": {
        "km": "🌙 Check-in ប្រចាំថ្ងៃ — {date}\nចុចរាល់ task ដែលអ្នកបានធ្វើថ្ងៃនេះ រួចចុច Confirm:",
        "en": "🌙 Daily check-in — {date}\nTap each task you completed today, then Confirm:",
    },
    "checkin_confirm_button": {
        "km": "✔️ បញ្ជាក់ check-in ថ្ងៃនេះ",
        "en": "✔️ Confirm today's check-in",
    },
    "checkin_done": {
        "km": "🌙 Check-in ចប់ — {date}\n\n",
        "en": "🌙 Check-in complete — {date}\n\n",
    },
    "checkin_task_done": {
        "km": "✅ {name} — streak {streak} 🔥",
        "en": "✅ {name} — streak {streak} 🔥",
    },
    "checkin_task_reset": {
        "km": "❌ {name} — streak ត្រូវបានកំណត់ឡើងវិញ",
        "en": "❌ {name} — streak reset",
    },
    "language_prompt": {
        "km": "🌐 សូមជ្រើសរើសភាសា:",
        "en": "🌐 Choose your language:",
    },
    "language_set": {
        "km": "✅ ភាសាត្រូវបានប្តូរទៅជា ខ្មែរ",
        "en": "✅ Language switched to English",
    },
}


def t(lang, key, **kwargs):
    lang = lang if lang in ("km", "en") else DEFAULT_LANGUAGE
    template = TEXT[key].get(lang, TEXT[key][DEFAULT_LANGUAGE])
    return template.format(**kwargs) if kwargs else template


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
            reminder_minute INTEGER DEFAULT 0,
            language TEXT DEFAULT 'km'
        )
    """)
    # Add the language column if this DB was created before this field existed
    existing_cols = [row["name"] for row in c.execute("PRAGMA table_info(users)").fetchall()]
    if "language" not in existing_cols:
        c.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'km'")

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


def get_user_language(chat_id):
    conn = get_conn()
    row = conn.execute("SELECT language FROM users WHERE chat_id=?", (chat_id,)).fetchone()
    conn.close()
    return row["language"] if row and row["language"] else DEFAULT_LANGUAGE


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
        "INSERT OR IGNORE INTO users (chat_id, reminder_hour, reminder_minute, language) VALUES (?, ?, ?, ?)",
        (chat_id, DEFAULT_REMINDER_HOUR, DEFAULT_REMINDER_MINUTE, DEFAULT_LANGUAGE),
    )
    conn.commit()
    conn.close()

    schedule_user_reminder(context.application, chat_id, DEFAULT_REMINDER_HOUR, DEFAULT_REMINDER_MINUTE)

    lang = get_user_language(chat_id)
    await update.message.reply_text(
        t(lang, "welcome", hour=DEFAULT_REMINDER_HOUR, minute=DEFAULT_REMINDER_MINUTE)
    )


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇰🇭 ខ្មែរ", callback_data="setlang:km"),
            InlineKeyboardButton("🇬🇧 English", callback_data="setlang:en"),
        ]
    ])
    await update.message.reply_text(t(lang, "language_prompt"), reply_markup=keyboard)


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    if not context.args:
        await update.message.reply_text(t(lang, "addtask_usage"))
        return
    name = " ".join(context.args).strip()

    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM tasks WHERE chat_id=? AND name=?", (chat_id, name)
    ).fetchone()
    if existing:
        await update.message.reply_text(t(lang, "addtask_duplicate", name=name))
        conn.close()
        return

    conn.execute("INSERT INTO tasks (chat_id, name) VALUES (?, ?)", (chat_id, name))
    conn.commit()
    conn.close()
    await update.message.reply_text(t(lang, "addtask_success", name=name))


async def remove_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    if not context.args:
        await update.message.reply_text(t(lang, "removetask_usage"))
        return
    name = " ".join(context.args).strip()

    conn = get_conn()
    task = conn.execute(
        "SELECT id FROM tasks WHERE chat_id=? AND name=?", (chat_id, name)
    ).fetchone()
    if not task:
        await update.message.reply_text(t(lang, "removetask_notfound", name=name))
        conn.close()
        return

    conn.execute("DELETE FROM tasks WHERE id=?", (task["id"],))
    conn.execute("DELETE FROM logs WHERE task_id=?", (task["id"],))
    conn.commit()
    conn.close()
    await update.message.reply_text(t(lang, "removetask_success", name=name))


async def my_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    conn = get_conn()
    tasks = conn.execute(
        "SELECT name, streak, best_streak FROM tasks WHERE chat_id=?", (chat_id,)
    ).fetchall()
    conn.close()

    if not tasks:
        await update.message.reply_text(t(lang, "mytasks_empty"))
        return

    lines = [t(lang, "mytasks_header")]
    for task_row in tasks:
        lines.append(t(lang, "mytasks_line", name=task_row["name"], streak=task_row["streak"], best=task_row["best_streak"]))
    await update.message.reply_text("\n".join(lines))


async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    if not context.args or ":" not in context.args[0]:
        await update.message.reply_text(t(lang, "settime_usage"))
        return

    try:
        hour, minute = map(int, context.args[0].split(":"))
        assert 0 <= hour <= 23 and 0 <= minute <= 59
    except (ValueError, AssertionError):
        await update.message.reply_text(t(lang, "settime_invalid"))
        return

    conn = get_conn()
    conn.execute(
        "INSERT INTO users (chat_id, reminder_hour, reminder_minute, language) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET reminder_hour=?, reminder_minute=?",
        (chat_id, hour, minute, lang, hour, minute),
    )
    conn.commit()
    conn.close()

    schedule_user_reminder(context.application, chat_id, hour, minute)

    await update.message.reply_text(t(lang, "settime_success", hour=hour, minute=minute))


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    conn = get_conn()
    tasks = conn.execute("SELECT id, name FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()

    if not tasks:
        await update.message.reply_text(t(lang, "stats_empty"))
        conn.close()
        return

    cutoff = (datetime.now(TZ) - timedelta(days=7)).strftime("%Y-%m-%d")
    lines = [t(lang, "stats_header")]
    for task_row in tasks:
        logs = conn.execute(
            "SELECT done FROM logs WHERE task_id=? AND date>=?", (task_row["id"], cutoff)
        ).fetchall()
        done_count = sum(1 for l in logs if l["done"])
        total = len(logs) if logs else 0
        pct = f"{(done_count/total*100):.0f}%" if total else "n/a"
        lines.append(t(lang, "stats_line", name=task_row["name"], done=done_count, total=total, pct=pct))
    conn.close()
    await update.message.reply_text("\n".join(lines))


# ------------------------------------------------------------------
# CHECK-IN FLOW (inline buttons)
# ------------------------------------------------------------------
def build_checkin_keyboard(chat_id, lang):
    state = pending_checkins.get(chat_id, {})
    conn = get_conn()
    tasks = conn.execute("SELECT id, name FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()

    rows = []
    for task_row in tasks:
        checked = state.get(task_row["id"], False)
        label = f"{'✅' if checked else '⬜'} {task_row['name']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"toggle:{task_row['id']}")])
    rows.append([InlineKeyboardButton(t(lang, "checkin_confirm_button"), callback_data="confirm")])
    return InlineKeyboardMarkup(rows)


async def send_checkin(chat_id, context: ContextTypes.DEFAULT_TYPE):
    conn = get_conn()
    tasks = conn.execute("SELECT id FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()
    if not tasks:
        return  # nothing to check in on

    lang = get_user_language(chat_id)
    pending_checkins[chat_id] = {task_row["id"]: False for task_row in tasks}
    await context.bot.send_message(
        chat_id=chat_id,
        text=t(lang, "checkin_prompt", date=today_str()),
        reply_markup=build_checkin_keyboard(chat_id, lang),
    )


async def manual_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_checkin(update.effective_chat.id, context)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    lang = get_user_language(chat_id)

    if query.data.startswith("setlang:"):
        new_lang = query.data.split(":")[1]
        conn = get_conn()
        conn.execute(
            "INSERT INTO users (chat_id, reminder_hour, reminder_minute, language) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(chat_id) DO UPDATE SET language=?",
            (chat_id, DEFAULT_REMINDER_HOUR, DEFAULT_REMINDER_MINUTE, new_lang, new_lang),
        )
        conn.commit()
        conn.close()
        await query.edit_message_text(t(new_lang, "language_set"))
        return

    if chat_id not in pending_checkins:
        pending_checkins[chat_id] = {}

    if query.data.startswith("toggle:"):
        task_id = int(query.data.split(":")[1])
        current = pending_checkins[chat_id].get(task_id, False)
        pending_checkins[chat_id][task_id] = not current
        await query.edit_message_reply_markup(reply_markup=build_checkin_keyboard(chat_id, lang))

    elif query.data == "confirm":
        state = pending_checkins.get(chat_id, {})
        conn = get_conn()
        summary_lines = []
        date = today_str()
        for task_id, done in state.items():
            task_row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not task_row:
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
                new_streak = task_row["streak"] + 1 if task_row["last_done_date"] == yesterday_str() else 1
                best = max(new_streak, task_row["best_streak"])
                conn.execute(
                    "UPDATE tasks SET streak=?, best_streak=?, last_done_date=? WHERE id=?",
                    (new_streak, best, date, task_id),
                )
                summary_lines.append(t(lang, "checkin_task_done", name=task_row["name"], streak=new_streak))
            else:
                conn.execute("UPDATE tasks SET streak=0 WHERE id=?", (task_id,))
                summary_lines.append(t(lang, "checkin_task_reset", name=task_row["name"]))

        conn.commit()
        conn.close()
        pending_checkins.pop(chat_id, None)

        await query.edit_message_text(
            t(lang, "checkin_done", date=date) + "\n".join(summary_lines)
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
    application.add_handler(CommandHandler("language", language_command))
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