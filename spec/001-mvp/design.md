# MVP Technical Design

**Spec:** 001-mvp
**Prerequisites:** [Requirements](requirements.md) (approved)
**Status:** Draft

---

## Architecture Overview

```
┌─────────────────────┐
│   Browser (Next.js)  │
│   shadcn/ui + TW CSS │
└─────────┬───────────┘
          │ REST API (JSON)
          │ Authorization: Bearer <JWT>
          v
┌─────────────────────┐
│   FastAPI Backend    │
│                     │
│  ┌───────────────┐  │
│  │ Auth (JWT)    │  │
│  │ fastapi-users │  │
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │    ┌──────────────┐
│  │ Guest CRUD    │──┼───>│ PostgreSQL   │
│  │ SQLAlchemy    │  │    └──────────────┘
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │    ┌──────────────┐
│  │ PDF Generator │──┼───>│ Google Drive  │
│  │ reportlab     │  │    │ (service acc) │
│  └───────────────┘  │    └──────────────┘
│                     │
│  ┌───────────────┐  │
│  │ Config Loader │  │
│  │ config.yaml   │  │
│  └───────────────┘  │
└─────────────────────┘
```

### Request Flow

1. Browser sends JSON request with JWT in `Authorization` header.
2. FastAPI middleware validates JWT; rejects with 401 if invalid/expired.
3. Route handler processes request, interacts with DB via SQLAlchemy.
4. For PDF: backend generates PDF with reportlab, uploads to Google Drive, returns status.
5. JSON response returned to browser.

---

## Project Layout

```
guest-book/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app, startup, config loading
│   │   ├── config.py            # Pydantic config model, YAML loader
│   │   ├── database.py          # SQLAlchemy engine, session, Base
│   │   ├── models.py            # SQLAlchemy ORM models (Guest, Child)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── auth.py              # fastapi-users setup, JWT config
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py          # /api/auth/* routes
│   │   │   ├── guests.py        # /api/guests/* routes
│   │   │   └── config.py        # /api/config route (read-only)
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── pdf.py           # PDF generation with reportlab
│   │   │   └── drive.py         # Google Drive upload
│   │   └── dependencies.py      # Shared FastAPI dependencies
│   ├── config.yaml              # Accommodation + Google Drive config
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile
│   └── tests/
│       ├── conftest.py
│       ├── test_guests.py
│       └── test_pdf.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx         # Redirect to /guests
│   │   │   ├── login/
│   │   │   │   └── page.tsx     # Login page
│   │   │   └── guests/
│   │   │       ├── page.tsx     # Guest list
│   │   │       └── new/
│   │   │           └── page.tsx # New guest form
│   │   ├── components/
│   │   │   ├── guest-form.tsx
│   │   │   ├── guest-table.tsx
│   │   │   └── ui/             # shadcn/ui components
│   │   ├── lib/
│   │   │   ├── api.ts          # API client (fetch wrapper with JWT)
│   │   │   └── types.ts        # TypeScript types matching backend schemas
│   │   └── hooks/
│   │       └── use-auth.ts     # Auth state + token management
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── config.yaml                  # Symlink or copy — see Configuration section
└── spec/
```

---

## Data Model

### Database Schema

#### `users` table (managed by fastapi-users)

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| email | VARCHAR(320) | Unique |
| hashed_password | VARCHAR(1024) | bcrypt |
| is_active | BOOLEAN | Default true |
| is_superuser | BOOLEAN | Default false |
| is_verified | BOOLEAN | Default false |

> fastapi-users provides this table automatically. For MVP, a single user is seeded via environment variables or first registration.

#### `guests` table

| Column | Type | Constraints | Maps to form field |
|--------|------|-------------|-------------------|
| id | UUID | PK, default gen | — |
| stay_from | DATE | NOT NULL | Pobyt od |
| stay_to | DATE | NOT NULL, >= stay_from | Pobyt do |
| first_name | VARCHAR(255) | NOT NULL | 1. Meno |
| last_name | VARCHAR(255) | NOT NULL | 2. Priezvisko |
| date_of_birth | DATE | NOT NULL | 3. Datum narodenia |
| birth_place | VARCHAR(500) | NOT NULL | 3. Miesto narodenia (stat) |
| nationality | VARCHAR(255) | NOT NULL | 4. Statna prislusnost |
| permanent_address | TEXT | NOT NULL | 5. Trvaly pobyt |
| travel_purpose | VARCHAR(500) | NOT NULL | 6. Ucel cesty |
| passport_number | VARCHAR(100) | NOT NULL | 7. Cislo pasu |
| visa_details | TEXT | NULLABLE | 8. Vizum / doklad o pobyte |
| accommodation_name | VARCHAR(500) | NOT NULL | 9. Meno ubytovacieho zariadenia |
| accommodation_address | VARCHAR(500) | NOT NULL | 9. Adresa ubytovacieho zariadenia |
| pdf_generated_at | TIMESTAMP | NULLABLE | — |
| created_at | TIMESTAMP | NOT NULL, default now | — |
| updated_at | TIMESTAMP | NOT NULL, auto-update | — |

**Design decision — Open Question #3 resolved:** Accommodation name and address are **snapshotted into each guest record** at creation time. This ensures the PDF is always accurate even if the provider later changes their config. The form pre-fills from `config.yaml`, but the saved value lives in the guest row.

**Design decision — Open Question #2 resolved:** `date_of_birth` and `birth_place` are stored as separate columns in the DB. They are combined into a single line on the PDF to match the official form's field 3 layout: `"{date_of_birth}, {birth_place}"`.

#### `children` table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| guest_id | UUID | FK -> guests.id, ON DELETE CASCADE |
| name | VARCHAR(255) | NOT NULL |
| position | SMALLINT | NOT NULL, 1-4 |

**Index:** `(guest_id)` for fast lookup when loading a guest.

#### `pdf_generated_at` field

Tracks whether a PDF has been generated for this guest. Set to current timestamp on successful PDF generation + upload. Used by the frontend to show a visual indicator (F-17, P2).

---

## API Design

Base URL: `/api`

All endpoints except auth require `Authorization: Bearer <token>` header.

### Authentication

| Method | Path | Request Body | Response | Notes |
|--------|------|-------------|----------|-------|
| POST | /api/auth/register | `{ email, password }` | `{ id, email }` | 201 Created |
| POST | /api/auth/login | `{ username, password }` | `{ access_token, token_type }` | OAuth2 form (fastapi-users convention) |

### Guests

| Method | Path | Request Body | Response | Notes |
|--------|------|-------------|----------|-------|
| GET | /api/guests | — | `{ items: Guest[], total, page, size }` | Query params: `search`, `nationality`, `date_from`, `date_to`, `page`, `size` |
| POST | /api/guests | `GuestCreate` | `Guest` | 201 Created |
| GET | /api/guests/{id} | — | `Guest` | 404 if not found |
| DELETE | /api/guests/{id} | — | 204 No Content | Cascades to children |
| POST | /api/guests/{id}/pdf | — | `{ url, filename }` | Generates PDF + uploads to Drive |

### Configuration

| Method | Path | Response | Notes |
|--------|------|----------|-------|
| GET | /api/config | `{ accommodation_name, accommodation_address }` | Read-only, from config.yaml |

### Pydantic Schemas

```python
class ChildCreate(BaseModel):
    name: str = Field(max_length=255)
    position: int = Field(ge=1, le=4)

class GuestCreate(BaseModel):
    stay_from: date
    stay_to: date
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    date_of_birth: date
    birth_place: str = Field(max_length=500)
    nationality: str = Field(max_length=255)
    permanent_address: str
    travel_purpose: str = Field(max_length=500)
    passport_number: str = Field(max_length=100)
    visa_details: str | None = None
    children: list[ChildCreate] = Field(default_factory=list, max_length=4)

    @field_validator("stay_to")
    def stay_to_after_stay_from(cls, v, info):
        if info.data.get("stay_from") and v < info.data["stay_from"]:
            raise ValueError("stay_to must be >= stay_from")
        return v

class GuestResponse(BaseModel):
    id: UUID
    stay_from: date
    stay_to: date
    first_name: str
    last_name: str
    date_of_birth: date
    birth_place: str
    nationality: str
    permanent_address: str
    travel_purpose: str
    passport_number: str
    visa_details: str | None
    accommodation_name: str
    accommodation_address: str
    children: list[ChildResponse]
    pdf_generated_at: datetime | None
    created_at: datetime
    updated_at: datetime

class GuestListResponse(BaseModel):
    items: list[GuestResponse]
    total: int
    page: int
    size: int
```

### Error Responses

Standard error shape for all endpoints:

```json
{
  "detail": "Human-readable error message"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Validation error (bad input) |
| 401 | Missing or invalid JWT |
| 404 | Guest not found |
| 500 | Internal error (PDF generation, Drive upload) |

---

## Configuration

### `config.yaml`

```yaml
accommodation:
  name: "Hotel Example"
  address: "123 Main Street, Bratislava"

google_drive:
  folder_id: "your-google-drive-folder-id"
```

### Environment Variables (`.env`)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/guestbook

# Auth
JWT_SECRET=<random-secret>
JWT_LIFETIME_SECONDS=3600
FIRST_USER_EMAIL=admin@example.com
FIRST_USER_PASSWORD=<password>

# Google Drive
GOOGLE_SERVICE_ACCOUNT_KEY_PATH=/app/credentials/service-account.json
```

### Loading Strategy

- `config.yaml` is loaded once at startup via Pydantic's `BaseSettings` with a YAML source.
- Environment variables are loaded from `.env` via `pydantic-settings`.
- The `/api/config` endpoint returns the accommodation portion for frontend pre-fill.

---

## PDF Generation

### Approach

Use reportlab to draw text directly onto a blank A4 canvas, replicating the official form layout.

### Layout Mapping

The official form (T MV SR 11-060-1 VII/2018) is a single A4 page. Field positions are measured from the reference PDF:

```
Page: A4 (595.28 x 841.89 points)

Title:     "HLASENIE POBYTU"              centered, top
Stay:      "Pobyt od: {stay_from}"         top-left box
           "do: {stay_to}"                 top-right of same box
Field 1:   "1. Meno: {first_name}"         left column
Field 2:   "2. Priezvisko: {last_name}"    right column
Field 3:   "3. Datum...: {dob}, {place}"   left column (combined)
Field 4:   "4. Statna...: {nationality}"   right column
Field 5:   "5. Trvaly pobyt...: {address}" full width
Field 6:   "6. Ucel cesty...: {purpose}"   left column
Field 7:   "7. Cislo pasu: {passport}"     right column
Field 8:   "8. Vizum...: {visa_details}"   full width
Field 9:   "9. Meno a adresa...: {name}, {addr}" full width
Field 10:  "10. Spolucestujuce deti:"      full width
           "1. {child_1}"
           "2. {child_2}" (up to 4)
Footer:    "Podpis cudzinca"               bottom-left
           "T MV SR 11-060-1  VII/2018"    bottom-right
```

### Font

- Use a font that supports Slovak diacritics (e.g. DejaVu Sans or Liberation Sans).
- Bundle the `.ttf` file in the backend Docker image.
- Register the font with reportlab at startup.

### Implementation Notes

- Labels are drawn as static text (Slovak), values filled from guest data.
- Horizontal rules drawn as lines between field rows.
- The form identifier `T MV SR 11-060-1 VII/2018` is rendered at the bottom-right.

---

## Google Drive Upload

### Flow

1. PDF is generated in memory (BytesIO buffer).
2. Google Drive API client authenticates via service account JSON key.
3. File is uploaded to the configured `folder_id`.
4. File name: `{last_name}_{first_name}_{stay_from}.pdf`.
5. On success, `pdf_generated_at` is updated on the guest record.
6. Drive file URL is returned in the response.

### Library

Use `google-api-python-client` + `google-auth` with a service account.

```python
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
```

---

## Frontend Design

### Pages

| Route | Component | Description |
|-------|-----------|-------------|
| `/login` | LoginPage | Email + password form |
| `/` | — | Redirect to `/guests` |
| `/guests` | GuestListPage | Table with search, filters, pagination, action buttons |
| `/guests/new` | NewGuestPage | Guest creation form |

### State Management

- **Auth state:** Custom `useAuth` hook storing JWT in `localStorage`. Wraps API client to attach token. Redirects to `/login` on 401.
- **Server state:** Use `fetch` directly (or SWR/React Query if needed) — keep it simple for MVP.

### Guest Form Component

- Single `GuestForm` component used by `/guests/new`.
- Accommodation fields pre-filled from `/api/config` on mount.
- Dynamic children section: "Add child" button, up to 4 entries.
- Client-side validation with inline errors (P1).
- Submit calls `POST /api/guests`.

### Guest Table Component

- Columns: Name, Nationality, Stay dates, Passport, PDF status, Actions.
- Actions per row: "Generate PDF" button, "Delete" button (with confirmation dialog).
- Search input + filter dropdowns above the table.
- Pagination controls below.

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| Auth bypass | All `/api/*` routes use FastAPI dependency injection to require valid JWT. |
| Password storage | fastapi-users uses bcrypt by default. |
| JWT secret | Stored in `.env`, never in code or config.yaml. |
| Google credentials | Service account JSON key mounted as file, path in env var. Never committed to repo. |
| SQL injection | SQLAlchemy parameterized queries — no raw SQL. |
| XSS | Next.js auto-escapes JSX. No `dangerouslySetInnerHTML`. |
| CORS | Backend allows only the frontend origin (configurable via env). |
| Input validation | Pydantic enforces types and constraints on all API inputs. |

---

## Deployment

### Local (Docker Compose)

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: guestbook
      POSTGRES_USER: guestbook
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://guestbook:${DB_PASSWORD}@db:5432/guestbook
      JWT_SECRET: ${JWT_SECRET}
      GOOGLE_SERVICE_ACCOUNT_KEY_PATH: /app/credentials/service-account.json
    volumes:
      - ./backend/config.yaml:/app/config.yaml:ro
      - ./credentials:/app/credentials:ro
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  pgdata:
```

### Production (Vercel + managed DB)

- **Frontend:** Deployed to Vercel (Next.js native support).
- **Backend:** Deployed as Vercel serverless function (Python runtime) or alternative (Railway, Fly.io).
- **Database:** Managed PostgreSQL (Neon, Supabase, or Vercel Postgres).
- **Config:** `config.yaml` values provided via environment variables in production (override YAML with env).

---

## Technical Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PDF layout doesn't match official form | Generated forms rejected by police | Overlay approach: measure exact positions from reference PDF. Manual QA against printed original. |
| Slovak diacritics render as boxes/? | Unreadable PDF | Bundle a Unicode-capable font (DejaVu Sans). Test with all Slovak characters. |
| Google Drive API rate limits | Upload failures | MVP has low volume (single user). Add retry with exponential backoff. |
| fastapi-users version churn | Breaking changes | Pin exact version in requirements.txt. |
| reportlab positioning is trial-and-error | Slow development | Create a test script that generates a sample PDF for visual comparison. Iterate on coordinates. |

---

## Design Decisions Log

| # | Decision | Rationale |
|---|----------|-----------|
| D-1 | Snapshot accommodation into guest record | If provider changes address, existing guest PDFs stay accurate. |
| D-2 | Separate `date_of_birth` + `birth_place` columns, combine on PDF | Cleaner DB schema; PDF rendering handles the display format. |
| D-3 | No PUT endpoint in MVP | Simplifies scope. Delete + re-create is acceptable for corrections. |
| D-4 | Config in YAML, no settings UI | MVP simplicity. Config changes require redeployment or container restart. |
| D-5 | `pdf_generated_at` field on guest | Lightweight way to track PDF status without a separate table. |
| D-6 | Async SQLAlchemy with asyncpg | Matches FastAPI's async nature. Better performance under concurrent requests. |
