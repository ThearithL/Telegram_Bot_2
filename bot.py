"""
Daily Habit & Task Reminder Telegram Bot
==========================================
Features:
  - Daily tasks with tappable check-in and streak tracking
  - Multiple reminder times per day (/addtime, /removetime, /mytimes)
  - Snooze button (delay a check-in by 1 hour)
  - Motivational quotes with each check-in
  - Streak milestone badges (7 / 30 / 100 days)
  - Weekly personal data backup sent to you as a JSON file (+/export on demand)
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
import io
import json
import random
import sqlite3
import logging
import asyncio
import threading
from datetime import datetime, time, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
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
BADGE_MILESTONES = (7, 30, 100)
BACKUP_WEEKDAY = 6  # 0=Monday ... 6=Sunday
BACKUP_HOUR = 23
BACKUP_MINUTE = 55

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# In-memory: pending (not-yet-confirmed) check-in state per chat_id
# { chat_id: { task_id: bool } }
pending_checkins = {}


# ------------------------------------------------------------------
# QUOTES
# ------------------------------------------------------------------
QUOTES = {
    "km": [
        "រាល់ថ្ងៃដែលអ្នកខិតខំ គឺជាជំហានមួយទៅមុខ។",
        "ភាពជោគជ័យមិនមែនចេញពីថ្ងៃណាមួយទេ វាចេញពីភាពស្ថិតស្ថេរ។",
        "កុំបោះបង់ streak ដែលអ្នកបានកសាងមក!",
        "ជំហានតូចៗប្រចាំថ្ងៃ នាំទៅរកលទ្ធផលធំ។",
        "ថ្ងៃនេះជាឱកាសមួយទៀតដើម្បីកាន់តែប្រសើរ។",
    ],
    "en": [
        "Every day you show up is a step forward.",
        "Success isn't from one day — it's from consistency.",
        "Don't break the streak you've built!",
        "Small daily steps lead to big results.",
        "Today is another chance to get a little better.",
    ],
}


def random_quote(lang):
    return random.choice(QUOTES.get(lang, QUOTES[DEFAULT_LANGUAGE]))


# ------------------------------------------------------------------
# TRANSLATIONS
# ------------------------------------------------------------------
TEXT = {
    "welcome": {
        "km": (
            "👋 សូមស្វាគមន៍មកកាន់ Daily Habit Bot!\n\n"
            "Commands:\n"
            "/addtask <ឈ្មោះ> - បន្ថែម task ថ្មី\n"
            "/removetask <ឈ្មោះ> - លុប task\n"
            "/mytasks - មើលបញ្ជី task\n"
            "/addtime HH:MM - បន្ថែមម៉ោងជូនដំណឹង (អាចមានច្រើន)\n"
            "/removetime HH:MM - លុបម៉ោងជូនដំណឹង\n"
            "/mytimes - មើលម៉ោងជូនដំណឹងទាំងអស់\n"
            "/checkin - សាកល្បង check-in ភ្លាមៗ\n"
            "/stats - របាយការណ៍ 7 ថ្ងៃចុងក្រោយ\n"
            "/export - ទាញយកទិន្នន័យខ្លួនឯង (JSON)\n"
            "/language - ប្តូរភាសា\n\n"
            "ម៉ោងជូនដំណឹង default គឺ {hour:02d}:{minute:02d} (ម៉ោងកម្ពុជា)។ ប្រើ /addtime ដើម្បីបន្ថែម។"
        ),
        "en": (
            "👋 Welcome to your Daily Habit Bot!\n\n"
            "Commands:\n"
            "/addtask <name> - add a task\n"
            "/removetask <name> - remove a task\n"
            "/mytasks - list your tasks\n"
            "/addtime HH:MM - add a reminder time (you can have several)\n"
            "/removetime HH:MM - remove a reminder time\n"
            "/mytimes - list all your reminder times\n"
            "/checkin - trigger a check-in now\n"
            "/stats - see your 7-day report\n"
            "/export - download your own data (JSON)\n"
            "/language - switch language\n\n"
            "Default reminder time is {hour:02d}:{minute:02d} (Phnom Penh time). Use /addtime to add more."
        ),
    },
    "addtask_usage": {"km": "របៀបប្រើ: /addtask <ឈ្មោះ task>", "en": "Usage: /addtask <task name>"},
    "addtask_duplicate": {"km": "⚠️ អ្នកមាន task ឈ្មោះ '{name}' រួចហើយ។", "en": "⚠️ You already have a task called '{name}'."},
    "addtask_success": {"km": "✅ បានបន្ថែម task: {name}", "en": "✅ Added daily task: {name}"},
    "removetask_usage": {"km": "របៀបប្រើ: /removetask <ឈ្មោះ task>", "en": "Usage: /removetask <task name>"},
    "removetask_notfound": {"km": "⚠️ រកមិនឃើញ task '{name}' ទេ។", "en": "⚠️ No task found named '{name}'."},
    "removetask_success": {"km": "🗑️ បានលុប task: {name}", "en": "🗑️ Removed task: {name}"},
    "mytasks_empty": {"km": "អ្នកមិនទាន់មាន task ទេ។ ប្រើ /addtask <ឈ្មោះ>", "en": "You have no tasks yet. Add one with /addtask <name>"},
    "mytasks_header": {"km": "📋 Task ប្រចាំថ្ងៃរបស់អ្នក:\n", "en": "📋 Your daily tasks:\n"},
    "mytasks_line": {"km": "• {name}  (streak: {streak} 🔥, ល្អបំផុត: {best})", "en": "• {name}  (streak: {streak} 🔥, best: {best})"},
    "addtime_usage": {"km": "របៀបប្រើ: /addtime HH:MM (ឧ. /addtime 07:30)", "en": "Usage: /addtime HH:MM (e.g. /addtime 07:30)"},
    "addtime_invalid": {"km": "⚠️ ម៉ោងមិនត្រឹមត្រូវ។ ប្រើទម្រង់ 24h ដូចជា 21:30", "en": "⚠️ Invalid time. Use 24h format like 21:30."},
    "addtime_exists": {"km": "⚠️ អ្នកមានម៉ោង {hour:02d}:{minute:02d} រួចហើយ។", "en": "⚠️ You already have {hour:02d}:{minute:02d} set."},
    "addtime_success": {"km": "⏰ បានបន្ថែមម៉ោងជូនដំណឹង: {hour:02d}:{minute:02d}", "en": "⏰ Added reminder time: {hour:02d}:{minute:02d}"},
    "removetime_usage": {"km": "របៀបប្រើ: /removetime HH:MM", "en": "Usage: /removetime HH:MM"},
    "removetime_notfound": {"km": "⚠️ រកមិនឃើញម៉ោង {hour:02d}:{minute:02d} ទេ។", "en": "⚠️ No reminder found at {hour:02d}:{minute:02d}."},
    "removetime_success": {"km": "🗑️ បានលុបម៉ោង: {hour:02d}:{minute:02d}", "en": "🗑️ Removed reminder time: {hour:02d}:{minute:02d}"},
    "mytimes_empty": {"km": "អ្នកមិនទាន់មានម៉ោងជូនដំណឹងទេ។ ប្រើ /addtime HH:MM", "en": "You have no reminder times yet. Add one with /addtime HH:MM"},
    "mytimes_header": {"km": "⏰ ម៉ោងជូនដំណឹងរបស់អ្នក:\n", "en": "⏰ Your reminder times:\n"},
    "stats_empty": {"km": "អ្នកមិនទាន់មាន task ទេ។ ប្រើ /addtask <ឈ្មោះ>", "en": "You have no tasks yet. Add one with /addtask <name>"},
    "stats_header": {"km": "📊 7 ថ្ងៃចុងក្រោយ:\n", "en": "📊 Last 7 days:\n"},
    "stats_line": {"km": "• {name}: បានធ្វើ {done} / កត់ត្រា {total} ({pct})", "en": "• {name}: {done} done / {total} logged ({pct})"},
    "checkin_prompt": {
        "km": "🌙 Check-in ប្រចាំថ្ងៃ — {date}\nចុចរាល់ task ដែលបានធ្វើថ្ងៃនេះ រួចចុច Confirm:\n\n💬 {quote}",
        "en": "🌙 Daily check-in — {date}\nTap each task you completed today, then Confirm:\n\n💬 {quote}",
    },
    "checkin_confirm_button": {"km": "✔️ បញ្ជាក់ check-in", "en": "✔️ Confirm check-in"},
    "checkin_snooze_button": {"km": "😴 រំលឹកម្តងទៀតក្នុង 1 ម៉ោង", "en": "😴 Snooze 1 hour"},
    "checkin_snoozed": {"km": "😴 បានពន្យារពេល — នឹងរំលឹកម្តងទៀតក្នុង 1 ម៉ោង។", "en": "😴 Snoozed — I'll remind you again in 1 hour."},
    "checkin_done": {"km": "🌙 Check-in ចប់ — {date}\n\n", "en": "🌙 Check-in complete — {date}\n\n"},
    "checkin_task_done": {"km": "✅ {name} — streak {streak} 🔥", "en": "✅ {name} — streak {streak} 🔥"},
    "checkin_task_reset": {"km": "❌ {name} — streak ត្រូវបានកំណត់ឡើងវិញ", "en": "❌ {name} — streak reset"},
    "badge_earned": {
        "km": "🏆 អបអរសាទរ! អ្នកទទួល badge '{badge}' សម្រាប់ task '{name}' (streak {streak} ថ្ងៃ)!",
        "en": "🏆 Congrats! You earned the '{badge}' badge for '{name}' ({streak}-day streak)!",
    },
    "language_prompt": {"km": "🌐 សូមជ្រើសរើសភាសា:", "en": "🌐 Choose your language:"},
    "language_set": {"km": "✅ ភាសាត្រូវបានប្តូរទៅជា ខ្មែរ", "en": "✅ Language switched to English"},
    "export_caption": {"km": "📦 ទិន្នន័យរបស់អ្នក (task, streak, log)", "en": "📦 Your data export (tasks, streaks, logs)"},
}

BADGE_NAMES = {
    7: {"km": "ភ្លើងសប្តាហ៍", "en": "Week Streak"},
    30: {"km": "ខ្លាំងពិសេស", "en": "Monthly Master"},
    100: {"km": "តារាហ្វូង", "en": "Century Club"},
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
    task_cols = [row["name"] for row in c.execute("PRAGMA table_info(tasks)").fetchall()]
    if "last_badge" not in task_cols:
        c.execute("ALTER TABLE tasks ADD COLUMN last_badge INTEGER DEFAULT 0")

    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            date TEXT,
            done INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS reminder_times (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            hour INTEGER,
            minute INTEGER
        )
    """)
    conn.commit()

    # Migrate old single reminder_hour/reminder_minute into reminder_times, once.
    users = c.execute("SELECT chat_id, reminder_hour, reminder_minute FROM users").fetchall()
    for u in users:
        existing = c.execute(
            "SELECT id FROM reminder_times WHERE chat_id=? AND hour=? AND minute=?",
            (u["chat_id"], u["reminder_hour"], u["reminder_minute"]),
        ).fetchone()
        any_time = c.execute("SELECT id FROM reminder_times WHERE chat_id=?", (u["chat_id"],)).fetchone()
        if not existing and not any_time:
            c.execute(
                "INSERT INTO reminder_times (chat_id, hour, minute) VALUES (?, ?, ?)",
                (u["chat_id"], u["reminder_hour"], u["reminder_minute"]),
            )
    conn.commit()
    conn.close()


def get_user_language(chat_id):
    conn = get_conn()
    row = conn.execute("SELECT language FROM users WHERE chat_id=?", (chat_id,)).fetchone()
    conn.close()
    return row["language"] if row and row["language"] else DEFAULT_LANGUAGE


def ensure_user(chat_id, language=None):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (chat_id, reminder_hour, reminder_minute, language) VALUES (?, ?, ?, ?)",
        (chat_id, DEFAULT_REMINDER_HOUR, DEFAULT_REMINDER_MINUTE, language or DEFAULT_LANGUAGE),
    )
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
    ensure_user(chat_id)

    conn = get_conn()
    has_time = conn.execute("SELECT id FROM reminder_times WHERE chat_id=?", (chat_id,)).fetchone()
    if not has_time:
        conn.execute(
            "INSERT INTO reminder_times (chat_id, hour, minute) VALUES (?, ?, ?)",
            (chat_id, DEFAULT_REMINDER_HOUR, DEFAULT_REMINDER_MINUTE),
        )
        conn.commit()
    conn.close()

    schedule_all_times_for_user(context.application, chat_id)

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
    existing = conn.execute("SELECT id FROM tasks WHERE chat_id=? AND name=?", (chat_id, name)).fetchone()
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
    task = conn.execute("SELECT id FROM tasks WHERE chat_id=? AND name=?", (chat_id, name)).fetchone()
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
    tasks = conn.execute("SELECT name, streak, best_streak FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()

    if not tasks:
        await update.message.reply_text(t(lang, "mytasks_empty"))
        return

    lines = [t(lang, "mytasks_header")]
    for row in tasks:
        lines.append(t(lang, "mytasks_line", name=row["name"], streak=row["streak"], best=row["best_streak"]))
    await update.message.reply_text("\n".join(lines))


def _parse_hhmm(text):
    hour, minute = map(int, text.split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("out of range")
    return hour, minute


async def add_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    ensure_user(chat_id, lang)
    if not context.args or ":" not in context.args[0]:
        await update.message.reply_text(t(lang, "addtime_usage"))
        return
    try:
        hour, minute = _parse_hhmm(context.args[0])
    except ValueError:
        await update.message.reply_text(t(lang, "addtime_invalid"))
        return

    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM reminder_times WHERE chat_id=? AND hour=? AND minute=?", (chat_id, hour, minute)
    ).fetchone()
    if existing:
        await update.message.reply_text(t(lang, "addtime_exists", hour=hour, minute=minute))
        conn.close()
        return

    conn.execute("INSERT INTO reminder_times (chat_id, hour, minute) VALUES (?, ?, ?)", (chat_id, hour, minute))
    conn.commit()
    conn.close()

    schedule_all_times_for_user(context.application, chat_id)
    await update.message.reply_text(t(lang, "addtime_success", hour=hour, minute=minute))


async def remove_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    if not context.args or ":" not in context.args[0]:
        await update.message.reply_text(t(lang, "removetime_usage"))
        return
    try:
        hour, minute = _parse_hhmm(context.args[0])
    except ValueError:
        await update.message.reply_text(t(lang, "addtime_invalid"))
        return

    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM reminder_times WHERE chat_id=? AND hour=? AND minute=?", (chat_id, hour, minute)
    ).fetchone()
    if not row:
        await update.message.reply_text(t(lang, "removetime_notfound", hour=hour, minute=minute))
        conn.close()
        return

    conn.execute("DELETE FROM reminder_times WHERE id=?", (row["id"],))
    conn.commit()
    conn.close()

    schedule_all_times_for_user(context.application, chat_id)
    await update.message.reply_text(t(lang, "removetime_success", hour=hour, minute=minute))


async def my_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    conn = get_conn()
    rows = conn.execute(
        "SELECT hour, minute FROM reminder_times WHERE chat_id=? ORDER BY hour, minute", (chat_id,)
    ).fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text(t(lang, "mytimes_empty"))
        return

    lines = [t(lang, "mytimes_header")]
    for row in rows:
        lines.append(f"• {row['hour']:02d}:{row['minute']:02d}")
    await update.message.reply_text("\n".join(lines))


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
    for row in tasks:
        logs = conn.execute("SELECT done FROM logs WHERE task_id=? AND date>=?", (row["id"], cutoff)).fetchall()
        done_count = sum(1 for l in logs if l["done"])
        total = len(logs) if logs else 0
        pct = f"{(done_count/total*100):.0f}%" if total else "n/a"
        lines.append(t(lang, "stats_line", name=row["name"], done=done_count, total=total, pct=pct))
    conn.close()
    await update.message.reply_text("\n".join(lines))


def build_user_export(chat_id):
    conn = get_conn()
    tasks = conn.execute("SELECT * FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    data = {"chat_id": chat_id, "exported_at": datetime.now(TZ).isoformat(), "tasks": []}
    for task_row in tasks:
        logs = conn.execute("SELECT date, done FROM logs WHERE task_id=? ORDER BY date", (task_row["id"],)).fetchall()
        data["tasks"].append({
            "name": task_row["name"],
            "streak": task_row["streak"],
            "best_streak": task_row["best_streak"],
            "logs": [{"date": l["date"], "done": bool(l["done"])} for l in logs],
        })
    conn.close()
    return json.dumps(data, ensure_ascii=False, indent=2)


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    payload = build_user_export(chat_id)
    file_obj = io.BytesIO(payload.encode("utf-8"))
    file_obj.name = f"habit_data_{chat_id}_{today_str()}.json"
    await update.message.reply_document(document=InputFile(file_obj), caption=t(lang, "export_caption"))


# ------------------------------------------------------------------
# CHECK-IN FLOW (inline buttons)
# ------------------------------------------------------------------
def build_checkin_keyboard(chat_id, lang):
    state = pending_checkins.get(chat_id, {})
    conn = get_conn()
    tasks = conn.execute("SELECT id, name FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()

    rows = []
    for row in tasks:
        checked = state.get(row["id"], False)
        label = f"{'✅' if checked else '⬜'} {row['name']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"toggle:{row['id']}")])
    rows.append([InlineKeyboardButton(t(lang, "checkin_confirm_button"), callback_data="confirm")])
    rows.append([InlineKeyboardButton(t(lang, "checkin_snooze_button"), callback_data="snooze")])
    return InlineKeyboardMarkup(rows)


async def send_checkin(chat_id, context: ContextTypes.DEFAULT_TYPE):
    conn = get_conn()
    tasks = conn.execute("SELECT id FROM tasks WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()
    if not tasks:
        return

    lang = get_user_language(chat_id)
    pending_checkins[chat_id] = {row["id"]: False for row in tasks}
    await context.bot.send_message(
        chat_id=chat_id,
        text=t(lang, "checkin_prompt", date=today_str(), quote=random_quote(lang)),
        reply_markup=build_checkin_keyboard(chat_id, lang),
    )


async def manual_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_checkin(update.effective_chat.id, context)


async def _snoozed_checkin_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await send_checkin(chat_id, context)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    lang = get_user_language(chat_id)

    if query.data.startswith("setlang:"):
        new_lang = query.data.split(":")[1]
        ensure_user(chat_id, new_lang)
        conn = get_conn()
        conn.execute("UPDATE users SET language=? WHERE chat_id=?", (new_lang, chat_id))
        conn.commit()
        conn.close()
        await query.edit_message_text(t(new_lang, "language_set"))
        return

    if query.data == "snooze":
        context.job_queue.run_once(_snoozed_checkin_job, when=3600, chat_id=chat_id, name=f"snooze_{chat_id}_{datetime.now(TZ).timestamp()}")
        pending_checkins.pop(chat_id, None)
        await query.edit_message_text(t(lang, "checkin_snoozed"))
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
        badge_lines = []
        date = today_str()
        for task_id, done in state.items():
            task_row = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if not task_row:
                continue

            existing_log = conn.execute("SELECT id FROM logs WHERE task_id=? AND date=?", (task_id, date)).fetchone()
            if existing_log:
                conn.execute("UPDATE logs SET done=? WHERE id=?", (1 if done else 0, existing_log["id"]))
            else:
                conn.execute("INSERT INTO logs (task_id, date, done) VALUES (?, ?, ?)", (task_id, date, 1 if done else 0))

            if done:
                new_streak = task_row["streak"] + 1 if task_row["last_done_date"] == yesterday_str() else 1
                best = max(new_streak, task_row["best_streak"])
                conn.execute(
                    "UPDATE tasks SET streak=?, best_streak=?, last_done_date=? WHERE id=?",
                    (new_streak, best, date, task_id),
                )
                summary_lines.append(t(lang, "checkin_task_done", name=task_row["name"], streak=new_streak))

                last_badge = task_row["last_badge"] or 0
                for milestone in BADGE_MILESTONES:
                    if new_streak >= milestone > last_badge:
                        badge_name = BADGE_NAMES[milestone].get(lang, BADGE_NAMES[milestone]["en"])
                        badge_lines.append(t(lang, "badge_earned", badge=badge_name, name=task_row["name"], streak=new_streak))
                        conn.execute("UPDATE tasks SET last_badge=? WHERE id=?", (milestone, task_id))
            else:
                conn.execute("UPDATE tasks SET streak=0 WHERE id=?", (task_id,))
                summary_lines.append(t(lang, "checkin_task_reset", name=task_row["name"]))

        conn.commit()
        conn.close()
        pending_checkins.pop(chat_id, None)

        await query.edit_message_text(t(lang, "checkin_done", date=date) + "\n".join(summary_lines))
        for badge_msg in badge_lines:
            await context.bot.send_message(chat_id=chat_id, text=badge_msg)


# ------------------------------------------------------------------
# SCHEDULING
# ------------------------------------------------------------------
def schedule_all_times_for_user(application: Application, chat_id: int):
    for job in application.job_queue.get_jobs_by_name(f"reminder_{chat_id}_all"):
        job.schedule_removal()
    # remove any previously-scheduled per-time jobs for this user
    for job in list(application.job_queue.jobs()):
        if job.name and job.name.startswith(f"reminder_{chat_id}_"):
            job.schedule_removal()

    conn = get_conn()
    times = conn.execute("SELECT hour, minute FROM reminder_times WHERE chat_id=?", (chat_id,)).fetchall()
    conn.close()

    for row in times:
        job_name = f"reminder_{chat_id}_{row['hour']:02d}{row['minute']:02d}"
        application.job_queue.run_daily(
            callback=lambda ctx: send_checkin(chat_id, ctx),
            time=time(hour=row["hour"], minute=row["minute"], tzinfo=TZ),
            name=job_name,
            chat_id=chat_id,
        )


async def schedule_all_users(application: Application):
    conn = get_conn()
    chat_ids = [row["chat_id"] for row in conn.execute("SELECT DISTINCT chat_id FROM reminder_times").fetchall()]
    conn.close()
    for chat_id in chat_ids:
        schedule_all_times_for_user(application, chat_id)


async def weekly_backup_job(context: ContextTypes.DEFAULT_TYPE):
    conn = get_conn()
    chat_ids = [row["chat_id"] for row in conn.execute("SELECT chat_id FROM users").fetchall()]
    conn.close()
    for chat_id in chat_ids:
        try:
            lang = get_user_language(chat_id)
            payload = build_user_export(chat_id)
            file_obj = io.BytesIO(payload.encode("utf-8"))
            file_obj.name = f"habit_backup_{chat_id}_{today_str()}.json"
            await context.bot.send_document(chat_id=chat_id, document=InputFile(file_obj), caption=t(lang, "export_caption"))
        except Exception as exc:
            logger.warning("Weekly backup failed for chat_id=%s: %s", chat_id, exc)


# ------------------------------------------------------------------
# TINY HTTP SERVER (for UptimeRobot keep-alive on Render free tier)
# ------------------------------------------------------------------
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK - Daily Habit Bot is running")

    def log_message(self, format, *args):
        pass


def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), PingHandler)
    server.serve_forever()


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
async def post_init(application: Application):
    await schedule_all_users(application)
    application.job_queue.run_daily(
        callback=weekly_backup_job,
        time=time(hour=BACKUP_HOUR, minute=BACKUP_MINUTE, tzinfo=TZ),
        days=(BACKUP_WEEKDAY,),
        name="weekly_backup",
    )


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
    application.add_handler(CommandHandler("addtime", add_time))
    application.add_handler(CommandHandler("removetime", remove_time))
    application.add_handler(CommandHandler("mytimes", my_times))
    application.add_handler(CommandHandler("checkin", manual_checkin))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("export", export_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot starting...")

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()