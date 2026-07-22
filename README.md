# Mampara API

FastAPI backend for the Mampara payday-advance platform, backed by MySQL.
Tables are created automatically on startup and seeded with dummy data the
first time each table is empty — real data entered afterwards is never
overwritten by the seed.

## Setup

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

Create a `.env` file (see `.env` already in this folder) with:

```
DATABASE_URL=mysql+pymysql://root:<password>@localhost:3306/mampara
```

The database itself (`mampara`) must already exist — create it once with:

```
CREATE DATABASE mampara CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## Run

```
venv\Scripts\uvicorn main:app --reload --port 8000
```

The frontend (`../mampara`) expects this running at `http://localhost:8000`
(configurable via `VITE_API_BASE_URL` in `mampara/.env`). Interactive API docs
are available at `http://localhost:8000/docs` once running.

## Structure

- `db.py` — SQLAlchemy engine/session setup, reads `DATABASE_URL` from `.env`.
- `models.py` — SQLAlchemy ORM tables: `users`, `sessions`, `advances`,
  `kyc_documents`, `billing_profiles`, `payment_methods`, `invoices`,
  `platform_settings`, plus JSON-blob tables for static content
  (`dashboard_copy`, `chart_data`, `public_teaser`, `credit_bureau_template`).
- `seed_data.py` / `seed.py` — the dummy content and the idempotent
  seed-if-empty logic run on every startup.
- `serializers.py` — turns ORM rows into the plain dicts the frontend expects.
- `utils.py` — id/token generation helpers (`make_token`, `next_advance_id`,
  `detect_card_brand`, etc.).
- `schemas.py` — request body models (Pydantic), field names match the
  frontend's camelCase JSON exactly.
- `routers/` — one file per resource (`auth`, `dashboard`, `advances`,
  `profile`, `kyc`, `billing`, `credit_bureau`, `settings`), each querying
  MySQL directly through a `Depends(get_db)` session.
- `main.py` — app wiring, CORS (allows the Vite dev server origins), table
  creation + seeding on startup.

## Notes

- Advance ids look like `#ADV-2026-892` — the `#` is unsafe as a raw URL path
  segment (browsers treat it as a fragment delimiter), so `/api/advances/approve`
  and `/decline` take the id in the request body instead of the path.
- `sortOrder` on `advances` is a `BigInteger` (holds millisecond epoch
  timestamps) so newly created advances always sort first, same as the old
  in-memory mock's `list.insert(0, ...)` behavior.
