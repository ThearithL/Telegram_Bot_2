## Button menu
Besides typing commands, you now get two menus:
- **Telegram's native "☰" menu** (next to the text box) lists every
  command with a short description, localized to Khmer or English based
  on the user's Telegram app language.
- **`/menu`** — also shown automatically right after `/start` — posts an
  in-chat button grid. Tapping "My Tasks", "Stats", "Check-in Now",
  "Export Data", etc. runs that action immediately. Buttons for commands
  that need typed input (`/addtask`, `/removetask`, `/addtime`,
  `/removetime`) show the usage line instead, since Telegram buttons
  can't pre-fill your message box.

## Weekly goals

- `/goal <task name> <1-7>` sets how many days per week you want to complete a task. For example: `/goal Read a book 5`.
- `/goals` shows each task's completions during the last 7 days and a progress bar. The same report is available from **Weekly Goals** in `/menu`.
- Existing tasks default to a target of 7. Startup adds the database column automatically, preserving existing local or Turso data.

## Telegram Mini App

The project includes a bilingual Mini App at `/app` (the service root `/` redirects there). Its simple mobile navigation has Home, Today, Habits, and More. Users can add/check/edit/delete habits, set weekly goals and reminder times, review a 7-day chart, switch English/Khmer, and export history to Excel. The Khmer Calendar card opens the requested source site. Admin-only tools appear in Settings for the configured `ADMIN_CHAT_ID`. The old password-protected web dashboard is at `/admin`.

The Mini App opens on a dedicated **Home** menu with welcome copy, today's completion and streak summaries, and direct cards for Today, Habits, Goals, Stats, Reminders, Export, Khmer Calendar, Settings, and Help. All menu and tab labels are available in English and Khmer.

The **More** tab also includes one-tap habit ideas (water, reading, walking, stretching, sleep, and meditation) plus a weekly completion snapshot with the average completion rate and strongest day. A Back to Home button and Telegram's native back button return users to the Home screen. The bot's `/menu` and `/start` button menus include an **Open Mini App** button, and the bot's **More** menu opens the Mini App directly on its More tab. In Settings, users can switch between Fullscreen and Windowed; Fullscreen is the default and the choice is remembered on that device. Telegram versions or devices without fullscreen support use the expanded view instead.

The Telegram chat menu keeps frequent actions on its main screen and groups reminder times, Excel export, language, and help under **More**.

For Render, set `RENDER_EXTERNAL_URL` automatically if available; otherwise set `MINI_APP_URL` to your public address ending in `/app` (for example, `https://your-service.onrender.com/app`). Configure BotFather's Main Mini App URL to the same HTTPS `/app` address. Mini App API requests validate Telegram `initData` and scope task operations to the verified user.

Check-in history now enforces one row per task per local date. Existing duplicate rows are cleaned at startup by keeping the latest row, and streak displays are recalculated from the daily logs. Weekly reports consistently use today plus the previous six Cambodia dates; unlogged days count as incomplete in completion rates.

## Deployment configuration

Set `BOT_TOKEN` and a strong, private `DASHBOARD_PASSWORD` in your host's environment settings. On Render, the bot stops at startup if the dashboard password is missing; local development generates a temporary password and prints it in the startup log. Optional settings: `ADMIN_CHAT_ID` (numeric Telegram chat ID), `TURSO_DATABASE_URL`, and `TURSO_AUTH_TOKEN`.

## Changelog

- **Added:** one-tap habit ideas in the Mini App's More tab and Mini App launch
  buttons in the bot's main and More menus.
- **Added:** a remembered Fullscreen/Windowed setting, with Fullscreen as the
  default and expanded-view fallback on unsupported Telegram clients.
- **Improved:** the screen-size setting follows changes made from Telegram's
  own fullscreen controls.
- **Added:** an in-app Back to Home button and Telegram native Back button
  behavior, plus a weekly insight card in More.

- **Improved:** Mini App navigation and mobile layout, with clearer Home, Today,
  Habits, and More sections, a weekly progress chart, reminder management,
  export shortcuts, and visible Telegram connection errors.

- **Added:** a dedicated Mini App Home menu with quick links into Today,
  Habits, Weekly Goals, and Settings, plus daily progress summaries. The menu
  and navigation labels are localized in English and Khmer.
- **Fixed:** `/mytasks` computed streak values after closing its database
  connection. It now keeps the connection open while calculating streaks and
  closes it reliably after the report is built.
- **Fixed:** Mini App Telegram `initData` signature validation now derives the
  Web App secret with Telegram's documented HMAC argument order, resolving the
  unauthorized API calls seen in the deployment logs.

- **Improved:** the `/menu` button grid is now fully tap-driven — no more
  typing required for day-to-day use:
  - **My Tasks** now shows a live ✅/⬜ checklist. Tap a task to mark it
    done/not-done for today instantly — no separate confirm step (that's
    still only needed for the scheduled `/checkin` reminder, which lets
    you tick several tasks before confirming).
  - **Add Task** / **Add Time** now ask "send me the name" / "send me the
    time" right in the chat, with a **Cancel** button, instead of just
    showing the `/addtask <name>` usage line.
  - **Remove Task** / **Remove Time** now list your existing tasks/times
    as buttons — tap one to remove it, no typing or exact spelling needed.
  - Nearly every reply (task lists, stats, check-in confirmation, add/
    remove results, help) now carries a **🔙 Back to Menu** button so you
    can keep navigating without retyping `/menu`.
- **Fixed:** streak could get wrongly reset to 1 if a task was confirmed
  at more than one reminder time on the same day. It's now left unchanged
  once already checked in for the day.
- **Improved:** the Turso Cloud connection no longer syncs on every single
  read (e.g. checking maintenance mode or a user's language on every
  message) — only when a write actually happened. This cuts network
  round-trips to Turso substantially and should reduce both latency and
  free-tier usage.
- **Added:** a global error handler, so an unexpected exception in a
  command no longer fails silently — it's logged, and the user gets a
  short "something went wrong" message instead of no response at all.
- **Added:** `/help` as an alias for `/start`.
- **Fixed:** the dashboard's maintenance toggle now requires a CSRF token
  tied to your session, so a malicious page can't flip maintenance mode
  just because you're logged in.
- **Fixed:** `.gitignore` had a broken `"README.md"` entry (literal quote
  characters, which don't match anything, plus you don't want your README
  excluded from the repo anyway) — removed it.
- **Fixed:** `.python-version` was empty; pinned to `3.11`.
- **Added:** an in-chat button menu (`/menu`, also shown after `/start`)
  and Telegram's native "☰" commands menu — see **Button menu** above.
- **Added:** customizable weekly completion goals with bilingual commands,
  menu access, progress bars, and automatic schema migration.
- **Fixed:** startup no longer logs environment variable names; `ADMIN_CHAT_ID`
  is validated, and Render requires an explicit dashboard password instead of
  silently using the publicly known `changeme` default.
