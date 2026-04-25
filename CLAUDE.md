# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stack

- **Backend**: FastAPI + SQLAlchemy + Alembic (Python), MySQL (`os_services_planner`).
- **Frontend**: Vue 3 (Composition API) + Vite + Pinia + Vue Router + Tailwind + axios + dayjs.
- **Tray icon**: Python GTK3 / AppIndicator3 (uses system packages, venv created with `--system-site-packages`).
- **Notifications**: an *external* long-running service listens on `NOTIFICATION_PORT` (default 52346) — not part of this repo. See "Notifications" below.

## Common commands

All commands assume the repo root is the CWD unless noted. Environment variables come from `.env` (not committed; see `.env.example`). `start-dev.sh`, `backend/run-dev.sh`, and `vite.config.js` all read `.env` directly — there is no secondary config.

```bash
./start-dev.sh                         # Starts backend + frontend + tray icon; trap-kills children on Ctrl+C
cd backend && ./run-dev.sh             # Backend only (uvicorn --reload on API_PORT)
cd frontend && npm run dev             # Frontend only (Vite on FRONTEND_PORT)
cd frontend && npm run build           # Production build

# Database migrations (from backend/, with venv activated)
source backend/venv/bin/activate
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "message"

# Seed / reset test data (DESTRUCTIVE: truncates all tables)
cd backend && python seed_test_data.py

# Systemd user services (see systemd/README.md)
systemctl --user start ubuntu-planner.target
journalctl --user -u ubuntu-planner-backend.service -f
```

Tests: `backend/tests/` exists but is empty and there is no configured runner — there is nothing to run. `backend/test_notification_config.py` at repo root is a standalone script, not a pytest suite. No frontend test setup.

## Ports and env

`API_PORT`, `FRONTEND_PORT`, and `VITE_API_URL` in `.env` must stay in sync — `VITE_API_URL` must equal `http://localhost:${API_PORT}` or the frontend can't reach the API. Defaults in code (1717/1718) differ from defaults in SETUP.md historical text (9090/5173); trust `.env`. CORS in `backend/app/main.py` is derived from `FRONTEND_PORT` automatically. See `PORT-CONFIG.md`.

## Architecture

### Backend layering (strict)

`app/api/*.py` (routers) → `app/services/*.py` (business logic) → `app/models/*.py` (SQLAlchemy). API layer is thin: parse request → call service → map `ValueError` to `HTTPException(400)`. Don't put DB queries in routers. Schemas (`app/schemas/`) are Pydantic v2 request/response models, not ORM classes.

Routers are registered in `app/main.py` via `app.include_router(...)` — new API modules must be added there. All routers are mounted under `/api/<resource>`.

### Data model (see `backend/app/models/`)

Five resources: `projects` (self-referential tree via `parent_id`), `tags` (global or project-scoped), `planning` (scheduled work), `sessions` (actual tracked work), `settings` (key/value). `planning` and `sessions` both many-to-many to `tags` via junction tables. A session can link back to the planning it was started from (`sessions.planning_id`). `sessions.actual_duration` is a MySQL computed column (`TIMESTAMPDIFF`) — don't try to write to it. "Active session" = the single row with `end_time IS NULL`; much of the session logic assumes at most one exists.

### Notification pipeline

The backend does *not* display notifications itself. Flow:

1. `NotificationWorker` (`app/tasks/notification_worker.py`) is an asyncio task started in the FastAPI lifespan. It polls the DB every 60 s for planning items whose `scheduled_start` just passed and for overdue active sessions.
2. For each hit it calls `NotificationService.send_notification()` (`app/services/notification_service.py`), which writes an INI config file to `notifications/` and sends the **file path** over a TCP socket to `NOTIFICATION_HOST:NOTIFICATION_PORT`.
3. A separate, external notification daemon (not in this repo) consumes that path and renders the desktop notification. If that daemon isn't running, notifications silently fail — log says "Failed to connect to notification service".

The worker dedupes via an in-memory cache (`_notification_cache`) with a 60 s TTL, so restarting the backend resets dedup state. Notification intervals come from `projects.notification_interval` (default 10 min); escalate at every multiple past the planned end time. `sessions.notification_disabled` suppresses session nags per-session.

### Frontend

Pinia stores in `frontend/src/stores/` (projects, tags, planning, sessions, settings) hold server state and wrap the axios client in `src/services/api.js`. Views in `src/views/` are routed pages; reusable UI in `src/components/`. Vite proxies `/api` → `VITE_API_URL` (see `vite.config.js`). Alias `@` → `src`. i18n strings live in `src/lang/en.json` (single file today; project is i18n-ready but not multi-locale yet).

### Tray icon

Separate Python process in `tray-icon/`, own venv, own `requirements.txt`. Talks to the backend HTTP API (read-only status + quick actions) via `api_client.py`. Requires `python3-gi`, `gir1.2-appindicator3-0.1` etc. — `tray-icon/setup.sh` handles this. Not needed for backend development.

## Roadmap-driven development

Feature work is organized in phases under `Documents/roadmap/{0..5}/`. When the user asks to "implement version N" or "roadmap N", read all markdown files in `Documents/roadmap/N/` first, then cross-reference detailed specs in `Documents/readme-*.md` (database, planning, execution, etc.). `Documents/ai-guide.md` has project-wide coding conventions worth respecting: Python PEP 8 + type hints + Google-style docstrings, Vue 3 Composition API, user-facing strings through `src/lang/`, schema changes via Alembic only.

## Things that will bite you

- `.env` lives at repo root, not inside `backend/`. Pydantic `Settings` resolves it via a relative path — running scripts from unexpected CWDs can break config loading.
- The notification daemon is out-of-tree. Absence is normal in dev; don't chase "failed to connect" errors unless the daemon is actually supposed to be running.
- `seed_test_data.py` truncates every table and resets auto-increment. Never run against data you care about.
- No auth layer by design — the app is localhost-only. Don't add one without discussing.
- Alembic migrations live in `backend/alembic/versions/`. Never edit schema via raw SQL; generate a revision.
