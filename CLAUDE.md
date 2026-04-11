# Guest Book - AI Agent Project Context

## Project Overview

**Guest Book** is a fullstack web application for accommodation providers in Slovakia to collect foreign guest data, store it in a database, and generate pre-filled "Hlasenie pobytu" (Police Registration) PDF forms as required by Slovak law.

**Current Status**: Specification complete (requirements, design, tasks all approved). Ready for implementation.

## Architecture

- **Frontend**: Next.js (React + TypeScript) with shadcn/ui + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Auth**: fastapi-users (JWT-based, single user seeded from env vars)
- **Database**: PostgreSQL with async SQLAlchemy + asyncpg
- **PDF Generation**: reportlab (Python) with DejaVu Sans font for Slovak diacritics
- **Google Drive**: Google Drive API (service account)
- **Configuration**: `config.yaml` for accommodation details + Google Drive folder ID
- **Containerization**: Docker Compose (frontend + backend + db)

```
Browser (Next.js :3000)
    |
    | REST API (JSON) + JWT auth
    v
FastAPI Backend (:8000)
    |
    |-- async SQLAlchemy --> PostgreSQL (:5432)
    |
    |-- reportlab --> PDF (BytesIO) --> Google Drive API
    |
    |-- config.yaml (accommodation name/address, Drive folder ID)
```

## Project Structure

```
guest-book/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, startup, config loading
│   │   ├── config.py            # Pydantic config model, YAML loader
│   │   ├── database.py          # Async SQLAlchemy engine, session, Base
│   │   ├── models.py            # ORM models (Guest, Child, User)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── auth.py              # fastapi-users JWT setup
│   │   ├── routers/             # auth.py, guests.py, config.py
│   │   ├── services/            # pdf.py, drive.py
│   │   └── fonts/               # DejaVu Sans TTF
│   ├── config.yaml
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages (login, guests, guests/new)
│   │   ├── components/          # guest-form.tsx, guest-table.tsx, ui/
│   │   ├── lib/                 # api.ts, types.ts
│   │   └── hooks/               # use-auth.ts
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── config.yaml
└── spec/
    ├── master-spec.md           # High-level project specification
    ├── examples/                # Reference PDF form (T MV SR 11-060-1 VII/2018)
    └── 001-mvp/                 # MVP spec (requirements, design, tasks — all approved)
```

## Key Design Decisions

- **No edit/PUT in MVP** — delete + re-create for corrections
- **No settings UI in MVP** — accommodation config via `config.yaml`
- **Accommodation snapshotted per guest** — name/address saved on guest record at creation time
- **`date_of_birth` + `birth_place` separate in DB** — combined on PDF for field 3
- **`pdf_generated_at` on guest record** — tracks PDF generation status
- **Single user auth** — seeded from FIRST_USER_EMAIL / FIRST_USER_PASSWORD env vars

## API Endpoints

All `/api/*` endpoints require JWT except auth routes.

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/login | Login, returns JWT |
| GET | /api/config | Accommodation config (read-only) |
| GET | /api/guests | List guests (paginated, searchable, filterable) |
| POST | /api/guests | Create guest record |
| GET | /api/guests/{id} | Get single guest |
| DELETE | /api/guests/{id} | Delete guest (cascades children) |
| POST | /api/guests/{id}/pdf | Generate PDF + upload to Drive |

## Specification

See `spec/master-spec.md` for the high-level spec and `spec/001-mvp/` for:
- `requirements.md` — Product requirements (approved)
- `design.md` — Technical design (approved)
- `tasks.md` — Implementation tasks (approved, 29 tasks in 5 phases)

## Conventions

### Code Style — Python (Backend)

- **Type Hints**: Required on all function signatures
- **Docstrings**: Required for all public APIs (modules, classes, functions)
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
  - Private: prefix with `_`

### Code Style — TypeScript (Frontend)

- **Strict mode**: Enabled in tsconfig
- **Components**: Functional components with TypeScript props interfaces
- **Naming**:
  - Components/types: `PascalCase`
  - Functions/variables: `camelCase`
  - Constants: `UPPER_SNAKE_CASE`

### Data Handling

- **Dates**: Use `datetime.date` in Python, ISO 8601 strings in API
- **Validation**: Pydantic models for all request/response schemas (backend)
- **Serialization**: Pydantic models for all structured data
- **DB transactions**: All writes use transactions; children cascade-delete with parent

### Testing

- **Test Files**: `test_*.py` pattern in `backend/tests/` directory
- **Fixtures**: Share common fixtures in `conftest.py`
- **Run**: `pytest` for backend tests
- **PDF QA**: `backend/scripts/generate_sample_pdf.py` for visual comparison against reference form

## Security

- **NEVER** commit secrets to git
- **ALWAYS** use environment variables for credentials (DB, JWT secret, Google Drive service account)
- Passwords hashed with bcrypt (fastapi-users default)
- All API endpoints require valid JWT token
- Google Drive service account JSON key mounted as file, path in env var
- CORS restricted to frontend origin
- SQLAlchemy parameterized queries only — no raw SQL
