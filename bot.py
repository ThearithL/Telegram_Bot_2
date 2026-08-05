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
import secrets
import sqlite3
import logging
import asyncio
import threading
from functools import wraps
from datetime import datetime, time, timedelta, timezone

from flask import Flask, request, redirect, url_for, session, render_template_string, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile, Bot
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
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))  # your own Telegram chat_id (for /maintenance)
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "changeme")  # web dashboard login
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
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
    "maintenance_active": {
        "km": "🛠 Bot កំពុងស្ថិតក្នុងការថែទាំបណ្តោះអាសន្ន សូមរង់ចាំបន្តិច ហើយសាកល្បងម្តងទៀតពេលក្រោយ។",
        "en": "🛠 The bot is under maintenance right now. Please try again shortly.",
    },
    "maintenance_usage": {"km": "របៀបប្រើ: /maintenance on | off | status", "en": "Usage: /maintenance on | off | status"},
    "maintenance_no_permission": {"km": "⛔ Command នេះសម្រាប់តែ admin ប៉ុណ្ណោះ។", "en": "⛔ This command is admin-only."},
    "maintenance_now_on": {"km": "🛠 Maintenance mode: ON — reminders និង commands ត្រូវផ្អាកសម្រាប់ user ធម្មតា។", "en": "🛠 Maintenance mode: ON — reminders and commands are paused for regular users."},
    "maintenance_now_off": {"km": "✅ Maintenance mode: OFF — bot ដំណើរការធម្មតាវិញ។", "en": "✅ Maintenance mode: OFF — bot is back to normal."},
    "maintenance_status": {"km": "Maintenance mode ឥឡូវនេះ: {state}", "en": "Maintenance mode is currently: {state}"},
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
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
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


def get_setting(key, default=None):
    conn = get_conn()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_conn()
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


def is_maintenance_on():
    return get_setting("maintenance_mode", "false") == "true"


def is_admin(chat_id):
    return ADMIN_CHAT_ID != 0 and chat_id == ADMIN_CHAT_ID


def maintenance_guard(func):
    """Blocks a handler for non-admin users while maintenance mode is on."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        chat_id = update.effective_chat.id
        if is_maintenance_on() and not is_admin(chat_id):
            lang = get_user_language(chat_id)
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.message.reply_text(t(lang, "maintenance_active"))
            else:
                await update.message.reply_text(t(lang, "maintenance_active"))
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


def today_str():
    return datetime.now(TZ).strftime("%Y-%m-%d")


def yesterday_str():
    return (datetime.now(TZ) - timedelta(days=1)).strftime("%Y-%m-%d")


# ------------------------------------------------------------------
# COMMANDS
# ------------------------------------------------------------------
@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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


@maintenance_guard
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
    if is_maintenance_on() and not is_admin(chat_id):
        return  # don't ping users with reminders while the bot is under maintenance
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


@maintenance_guard
async def manual_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_checkin(update.effective_chat.id, context)


async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    if not is_admin(chat_id):
        await update.message.reply_text(t(lang, "maintenance_no_permission"))
        return

    if not context.args:
        state = "ON" if is_maintenance_on() else "OFF"
        await update.message.reply_text(t(lang, "maintenance_status", state=state))
        return

    arg = context.args[0].lower()
    if arg == "on":
        set_setting("maintenance_mode", "true")
        await update.message.reply_text(t(lang, "maintenance_now_on"))
    elif arg == "off":
        set_setting("maintenance_mode", "false")
        await update.message.reply_text(t(lang, "maintenance_now_off"))
    elif arg == "status":
        state = "ON" if is_maintenance_on() else "OFF"
        await update.message.reply_text(t(lang, "maintenance_status", state=state))
    else:
        await update.message.reply_text(t(lang, "maintenance_usage"))


async def backupnow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    lang = get_user_language(chat_id)
    if not is_admin(chat_id):
        await update.message.reply_text(t(lang, "maintenance_no_permission"))
        return
    await backup_db_to_telegram(context)
    await update.message.reply_text(
        "✅ បម្រុងទុកទិន្នន័យ ហើយ pin ក្នុង chat នេះរួចហើយ។" if lang == "km"
        else "✅ Backup sent and pinned in this chat."
    )


async def _snoozed_checkin_job(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.chat_id
    await send_checkin(chat_id, context)


@maintenance_guard
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

        await backup_db_to_telegram(context)


# ------------------------------------------------------------------
# PERSISTENCE VIA TELEGRAM (survives Render free-tier redeploys)
# ------------------------------------------------------------------
# Render's free tier wipes the local filesystem on every redeploy/restart,
# so habit_bot.db can't live there permanently. Instead: after every change
# we snapshot the DB and send+pin it as a document in the admin's chat.
# Telegram — not Render — is what actually keeps it, since a chat's pinned
# message survives independently of our server. On startup, before
# creating a fresh DB, we check that pinned message and restore from it.
def _snapshot_db_bytes():
    tmp_path = DB_PATH + ".snapshot"
    conn = get_conn()
    conn.execute("VACUUM INTO ?", (tmp_path,))
    conn.close()
    with open(tmp_path, "rb") as f:
        data = f.read()
    os.remove(tmp_path)
    return data


async def backup_db_to_telegram(context: ContextTypes.DEFAULT_TYPE):
    if ADMIN_CHAT_ID == 0:
        return
    try:
        data = _snapshot_db_bytes()
        file_obj = io.BytesIO(data)
        file_obj.name = "habit_bot.db"
        msg = await context.bot.send_document(
            chat_id=ADMIN_CHAT_ID,
            document=InputFile(file_obj),
            caption=f"🗄 Auto-backup — {datetime.now(TZ).strftime('%Y-%m-%d %H:%M')}",
            disable_notification=True,
        )
        try:
            await context.bot.unpin_all_chat_messages(chat_id=ADMIN_CHAT_ID)
        except Exception:
            pass  # nothing pinned yet, or not enough rights — still try to pin the new one
        await context.bot.pin_chat_message(chat_id=ADMIN_CHAT_ID, message_id=msg.message_id, disable_notification=True)
    except Exception as exc:
        logger.warning("DB backup to Telegram failed: %s", exc)


async def restore_db_from_telegram():
    if os.path.exists(DB_PATH):
        logger.info("Local database already present — skipping restore.")
        return
    if ADMIN_CHAT_ID == 0:
        logger.warning("ADMIN_CHAT_ID is not set — cannot restore from Telegram, starting with a fresh database.")
        return

    bot = Bot(token=BOT_TOKEN)
    await bot.initialize()
    try:
        chat = await bot.get_chat(ADMIN_CHAT_ID)
        pinned = chat.pinned_message
        if pinned and pinned.document:
            file = await bot.get_file(pinned.document.file_id)
            await file.download_to_drive(DB_PATH)
            logger.info("Restored habit_bot.db from the pinned Telegram backup.")
        else:
            logger.info("No pinned backup found in the admin chat — starting with a fresh database.")
    except Exception as exc:
        logger.warning("Could not restore database from Telegram: %s", exc)
    finally:
        await bot.shutdown()


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
    if is_maintenance_on():
        return
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
# WEB DASHBOARD (control panel + UptimeRobot keep-alive on Render free tier)
# ------------------------------------------------------------------
flask_app = Flask(__name__)
flask_app.secret_key = FLASK_SECRET_KEY

DASHBOARD_CSS = """
:root{--bg:#0f1115;--card:#171a21;--border:#262a33;--text:#e7e9ee;--muted:#8b90a0;
      --accent:#5b8cff;--good:#39d98a;--bad:#ff5c72;--warn:#ffb454;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--text);
     font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:960px;margin:0 auto;padding:32px 20px 60px;}
h1{font-size:22px;margin:0 0 4px;}
.sub{color:var(--muted);font-size:13px;margin:0 0 28px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;margin-bottom:18px;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-bottom:18px;}
.stat{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;}
.stat .n{font-size:26px;font-weight:700;}
.stat .l{color:var(--muted);font-size:12px;margin-top:4px;}
.badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:999px;font-size:13px;font-weight:600;}
.badge.on{background:rgba(255,92,114,.15);color:var(--bad);}
.badge.off{background:rgba(57,217,138,.15);color:var(--good);}
.row{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}
button{background:var(--accent);color:#fff;border:none;border-radius:10px;padding:10px 18px;
       font-size:14px;font-weight:600;cursor:pointer;}
button.danger{background:var(--bad);}
button.ghost{background:transparent;border:1px solid var(--border);color:var(--text);}
table{width:100%;border-collapse:collapse;font-size:13px;}
th{text-align:left;color:var(--muted);font-weight:600;padding:8px 10px;border-bottom:1px solid var(--border);}
td{padding:8px 10px;border-bottom:1px solid var(--border);}
tr:last-child td{border-bottom:none;}
.empty{color:var(--muted);font-size:13px;padding:8px 0;}
h2{font-size:15px;margin:0 0 14px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;}
input[type=password]{width:100%;padding:12px;border-radius:10px;border:1px solid var(--border);
       background:#0d0f14;color:var(--text);font-size:14px;margin-bottom:14px;}
.login-box{max-width:340px;margin:80px auto;}
.err{color:var(--bad);font-size:13px;margin-bottom:10px;}
a{color:var(--accent);text-decoration:none;font-size:13px;}
"""

LOGIN_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Habit Bot — Login</title><style>{{ css }}</style></head>
<body><div class="wrap login-box"><div class="card">
<h1>🔒 Habit Bot Dashboard</h1><p class="sub">Enter the admin password to continue.</p>
{% if error %}<p class="err">{{ error }}</p>{% endif %}
<form method="post"><input type="password" name="password" placeholder="Password" autofocus>
<button type="submit" style="width:100%">Log in</button></form>
</div></div></body></html>
"""

DASHBOARD_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Habit Bot — Dashboard</title><style>{{ css }}</style></head>
<body><div class="wrap">
<div class="row"><div>
<h1>📊 Daily Habit Bot</h1><p class="sub">Control panel &amp; live stats</p>
</div><a href="{{ url_for('logout') }}">Log out</a></div>

<div class="card row">
  <div>
    <span class="badge {{ 'on' if maintenance else 'off' }}">
      {{ '🛠 Maintenance ON' if maintenance else '✅ Running normally' }}
    </span>
  </div>
  <form method="post" action="{{ url_for('toggle_maintenance') }}">
    <button class="{{ 'ghost' if maintenance else 'danger' }}" type="submit">
      {{ 'Turn maintenance OFF' if maintenance else 'Turn maintenance ON' }}
    </button>
  </form>
</div>

<div class="grid">
  <div class="stat"><div class="n">{{ stats.users }}</div><div class="l">Total users</div></div>
  <div class="stat"><div class="n">{{ stats.tasks }}</div><div class="l">Total tasks</div></div>
  <div class="stat"><div class="n">{{ stats.checkins_today }}</div><div class="l">Check-ins today</div></div>
  <div class="stat"><div class="n">{{ stats.checkins_week }}</div><div class="l">Check-ins (7d)</div></div>
</div>

<div class="card">
  <h2>Top streaks</h2>
  {% if top_streaks %}
  <table><tr><th>Task</th><th>User (chat_id)</th><th>Streak</th><th>Best</th></tr>
  {% for r in top_streaks %}
  <tr><td>{{ r.name }}</td><td>{{ r.chat_id }}</td><td>🔥 {{ r.streak }}</td><td>{{ r.best_streak }}</td></tr>
  {% endfor %}</table>
  {% else %}<p class="empty">No tasks yet.</p>{% endif %}
</div>

<div class="card">
  <h2>Users</h2>
  {% if users %}
  <table><tr><th>chat_id</th><th>Language</th><th>Tasks</th><th>Reminder times</th></tr>
  {% for u in users %}
  <tr><td>{{ u.chat_id }}</td><td>{{ u.language }}</td><td>{{ u.task_count }}</td><td>{{ u.times }}</td></tr>
  {% endfor %}</table>
  {% else %}<p class="empty">No users yet.</p>{% endif %}
</div>

</div></body></html>
"""


def _require_login(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper


def _dashboard_stats():
    conn = get_conn()
    users = conn.execute("SELECT COUNT(*) c FROM users").fetchone()["c"]
    tasks = conn.execute("SELECT COUNT(*) c FROM tasks").fetchone()["c"]
    checkins_today = conn.execute(
        "SELECT COUNT(*) c FROM logs WHERE date=? AND done=1", (today_str(),)
    ).fetchone()["c"]
    week_cutoff = (datetime.now(TZ) - timedelta(days=7)).strftime("%Y-%m-%d")
    checkins_week = conn.execute(
        "SELECT COUNT(*) c FROM logs WHERE date>=? AND done=1", (week_cutoff,)
    ).fetchone()["c"]
    conn.close()
    return {"users": users, "tasks": tasks, "checkins_today": checkins_today, "checkins_week": checkins_week}


def _top_streaks(limit=10):
    conn = get_conn()
    rows = conn.execute(
        "SELECT chat_id, name, streak, best_streak FROM tasks ORDER BY streak DESC, best_streak DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _user_rows():
    conn = get_conn()
    users = conn.execute("SELECT chat_id, language FROM users ORDER BY chat_id").fetchall()
    out = []
    for u in users:
        task_count = conn.execute("SELECT COUNT(*) c FROM tasks WHERE chat_id=?", (u["chat_id"],)).fetchone()["c"]
        times = conn.execute(
            "SELECT hour, minute FROM reminder_times WHERE chat_id=? ORDER BY hour, minute", (u["chat_id"],)
        ).fetchall()
        times_str = ", ".join(f"{r['hour']:02d}:{r['minute']:02d}" for r in times) or "—"
        out.append({"chat_id": u["chat_id"], "language": u["language"], "task_count": task_count, "times": times_str})
    conn.close()
    return out


@flask_app.route("/ping")
def ping():
    return Response("OK - Daily Habit Bot is running", mimetype="text/plain")


@flask_app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if secrets.compare_digest(request.form.get("password", ""), DASHBOARD_PASSWORD):
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        error = "Wrong password."
    return render_template_string(LOGIN_HTML, css=DASHBOARD_CSS, error=error)


@flask_app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@flask_app.route("/")
@_require_login
def dashboard():
    return render_template_string(
        DASHBOARD_HTML,
        css=DASHBOARD_CSS,
        maintenance=is_maintenance_on(),
        stats=_dashboard_stats(),
        top_streaks=_top_streaks(),
        users=_user_rows(),
    )


@flask_app.route("/toggle-maintenance", methods=["POST"])
@_require_login
def toggle_maintenance():
    set_setting("maintenance_mode", "false" if is_maintenance_on() else "true")
    return redirect(url_for("dashboard"))


def run_dashboard():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port, threaded=True, use_reloader=False)


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
    application.job_queue.run_repeating(
        callback=backup_db_to_telegram,
        interval=timedelta(minutes=30),
        first=60,
        name="db_backup",
    )


def main():
    if BOT_TOKEN == "PUT_YOUR_TOKEN_HERE":
        env_keys = sorted(os.environ.keys())
        logger.error("BOT_TOKEN not found. Available env var keys: %s", env_keys)
        raise RuntimeError("Set the BOT_TOKEN environment variable before running.")

    asyncio.run(restore_db_from_telegram())
    init_db()

    if DASHBOARD_PASSWORD == "changeme":
        logger.warning("DASHBOARD_PASSWORD is not set — using the default 'changeme'. Set it in your environment!")

    threading.Thread(target=run_dashboard, daemon=True).start()

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
    application.add_handler(CommandHandler("maintenance", maintenance_command))
    application.add_handler(CommandHandler("backupnow", backupnow_command))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot starting...")

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()