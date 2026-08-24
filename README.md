
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

## Changelog

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
