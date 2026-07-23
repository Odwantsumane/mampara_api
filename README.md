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
JWT_SECRET_KEY=<random-hex-string>
JWT_EXPIRES_MINUTES=1440
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

Routers stay thin — they parse the request, call into `crud/`, and shape the
response. All actual persistence logic and business rules live in `crud/`;
authentication concerns (hashing, tokens) live in `auth/`.

- `db.py` — SQLAlchemy engine/session setup, reads `DATABASE_URL` from `.env`.
- `models.py` — SQLAlchemy ORM tables: `users`, `advances`, `kyc_documents`,
  `billing_profiles`, `payment_methods`, `invoices`, `platform_settings`, plus
  JSON-blob tables for static content (`dashboard_copy`, `chart_data`,
  `public_teaser`, `credit_bureau_template`).
- `auth/userAuthentication.py` — JWT creation/verification
  (`create_access_token`, `decode_user_id`, `get_current_user_id`) and bcrypt
  password hashing (`hash_password`, `verify_password`). `JWT_SECRET_KEY` and
  `JWT_EXPIRES_MINUTES` come from `.env`.
- `crud/` — one module per resource (`users`, `advances`, `kyc`, `billing`,
  `settings`, `dashboard`, `credit_bureau`) — every DB read/write goes through
  here, nothing queries `models.*` directly from a router.
- `serializers.py` — turns ORM rows into the plain dicts the frontend expects.
- `utils.py` — display-id/formatting helpers (`next_advance_id`,
  `detect_card_brand`, etc.) — not used for primary keys, see below.
- `schemas.py` — request body models (Pydantic), field names match the
  frontend's camelCase JSON exactly.
- `routers/` — `auth`, `dashboard`, `advances`, `profile`, `kyc`, `billing`,
  `credit_bureau`, `settings`.
- `main.py` — app wiring, CORS (allows the Vite dev server origins), table
  creation + seeding on startup.

## Auth

Login/signup issue a JWT (`sub` = user id, default 24h expiry) instead of the
old opaque token + `sessions` table — fully stateless, so there's no session
table to clean up and no behavior change for the frontend (it already just
stores whatever string it's given and sends it back as `Authorization:
Bearer <token>`). `get_current_user_id` (in `auth/userAuthentication.py`) is
available as a strict `Depends(...)` for any route that should hard-401
unauthenticated requests; `/api/auth/me` uses the lenient
`decode_user_id` instead since "not logged in" is a valid state there.

Passwords are bcrypt-hashed (`auth.hash_password` / `auth.verify_password`) —
including the two seed users, hashed once at seed time in `seed.py`.

## IDs

- `users`, `kyc_documents` (`key`), and `payment_methods` use real UUID
  primary keys (`models.new_uuid`, a `uuid.uuid4()` default) — none of these
  are ever displayed to a user, so there's no UX reason to keep them
  human-readable.
- `advances` and `invoices` keep their display-friendly reference codes
  (`#ADV-2026-892`, `#INV-2026-07`) as the primary key on purpose — the
  frontend renders that id directly (Advance Book, Billing history), so
  switching those to raw UUIDs would visibly degrade the product.

## Notes

- Advance ids look like `#ADV-2026-892` — the `#` is unsafe as a raw URL path
  segment (browsers treat it as a fragment delimiter), so `/api/advances/approve`
  and `/decline` take the id in the request body instead of the path.
- `sortOrder` on `advances` is a `BigInteger` (holds millisecond epoch
  timestamps) so newly created advances always sort first, same as the old
  in-memory mock's `list.insert(0, ...)` behavior.
