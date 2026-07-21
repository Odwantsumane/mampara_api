# Mampara API

FastAPI backend for the Mampara payday-advance platform. No database yet —
everything lives in plain Python lists/dicts in `store.py`, seeded with dummy
data. Restarting the server resets all state back to the seed data.

## Setup

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

## Run

```
venv\Scripts\uvicorn main:app --reload --port 8000
```

The frontend (`../mampara`) expects this running at `http://localhost:8000`
(configurable via `VITE_API_BASE_URL` in `mampara/.env`). Interactive API docs
are available at `http://localhost:8000/docs` once running.

## Structure

- `store.py` — the in-memory "database": users, sessions, advances, KYC queue,
  billing/payment methods, credit bureau result, platform settings.
- `schemas.py` — request body models (Pydantic), field names match the
  frontend's camelCase JSON exactly.
- `routers/` — one file per resource (`auth`, `dashboard`, `advances`,
  `profile`, `kyc`, `billing`, `credit_bureau`, `settings`).
- `main.py` — app wiring + CORS (allows the Vite dev server origins).

## Notes for adding a real database later

Every router talks to `store.py` through plain function calls
(`store.users`, `store.advances`, etc.) — swap those for real queries
(SQLAlchemy/an ORM of your choice) without touching router logic or
response shapes, and the frontend won't need any changes.
