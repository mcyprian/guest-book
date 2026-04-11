# MVP Implementation Tasks

**Spec:** 001-mvp
**Prerequisites:** [Design](design.md) (approved)
**Status:** Complete — All 29 tasks done

---

## Overview

| Phase | Description | Tasks |
|-------|-------------|-------|
| 1. Foundation | Project scaffolding, DB, config, auth | 8 |
| 2. Guest CRUD | Backend API + frontend for guest management | 7 |
| 3. PDF & Drive | PDF generation and Google Drive upload | 5 |
| 4. Frontend Polish | Search, filters, validation, notifications | 5 |
| 5. Deployment | Docker Compose, env setup, documentation | 4 |

**Total:** 29 tasks

---

## Phase 1: Foundation

> Goal: Backend and frontend projects running, DB connected, auth working.

- [x] **T-01** Project scaffolding — create `backend/` and `frontend/` directory structure as defined in design.md
  - Create `backend/app/` package with `__init__.py`, `main.py`
  - Create `backend/requirements.txt` with pinned dependencies (fastapi, uvicorn, sqlalchemy, asyncpg, fastapi-users, pydantic, pydantic-settings, pyyaml, reportlab, google-api-python-client, google-auth)
  - Initialize Next.js project in `frontend/` with TypeScript
  - Install shadcn/ui and Tailwind CSS

- [x] **T-02** Configuration loader — `backend/app/config.py`
  - Pydantic model for `config.yaml` (accommodation name/address, Google Drive folder ID)
  - YAML loader function called at startup
  - Environment variables via `pydantic-settings` for secrets (DATABASE_URL, JWT_SECRET, etc.)
  - Create `backend/config.yaml` with example values
  - Create `.env.example` with all required env vars

- [x] **T-03** Database setup — `backend/app/database.py`
  - Async SQLAlchemy engine with asyncpg
  - Async session factory
  - Declarative Base
  - Startup event to create tables (or Alembic later)

- [x] **T-04** ORM models — `backend/app/models.py`
  - `User` model (fastapi-users compatible)
  - `Guest` model with all columns from design (including `accommodation_name`, `accommodation_address`, `pdf_generated_at`)
  - `Child` model with FK to Guest, ON DELETE CASCADE
  - Index on `children.guest_id`
  - Depends on: T-03

- [x] **T-05** Pydantic schemas — `backend/app/schemas.py`
  - `GuestCreate`, `GuestResponse`, `GuestListResponse`, `ChildCreate`, `ChildResponse`
  - `stay_to >= stay_from` validator
  - `children` list max length 4
  - `ConfigResponse` for the /api/config endpoint
  - Depends on: T-04

- [x] **T-06** Auth setup — `backend/app/auth.py` + `backend/app/routers/auth.py`
  - fastapi-users configuration with JWT strategy
  - JWT secret from env, configurable lifetime
  - Register + login routes mounted at `/api/auth`
  - Seed first user from `FIRST_USER_EMAIL` / `FIRST_USER_PASSWORD` env vars on startup
  - Depends on: T-03, T-04

- [x] **T-07** FastAPI app assembly — `backend/app/main.py`
  - Create FastAPI app instance
  - Load config.yaml on startup
  - Include auth router
  - CORS middleware (allowed origins from env)
  - Health check endpoint `GET /api/health`
  - Depends on: T-02, T-03, T-06

- [x] **T-08** Frontend auth — login page + API client
  - `src/lib/api.ts` — fetch wrapper that attaches JWT from localStorage, handles 401 redirect
  - `src/hooks/use-auth.ts` — login function, token storage, logout
  - `src/lib/types.ts` — TypeScript types matching backend schemas
  - `src/app/login/page.tsx` — email + password form, calls POST /api/auth/login
  - `src/app/layout.tsx` — root layout with auth guard (redirect to /login if no token)
  - Depends on: T-06, T-07

---

## Phase 2: Guest CRUD

> Goal: Create, list, view, and delete guest records end-to-end.

- [x] **T-09** Guest create endpoint — `backend/app/routers/guests.py`
  - `POST /api/guests` — validate input, snapshot accommodation from config, save guest + children in a transaction
  - Return `GuestResponse` with 201
  - Depends on: T-05, T-07

- [x] **T-10** Guest list endpoint
  - `GET /api/guests` — paginated response with `page` and `size` query params
  - Default page=1, size=20
  - Eager-load children with each guest
  - Return `GuestListResponse`
  - Depends on: T-09

- [x] **T-11** Guest detail + delete endpoints
  - `GET /api/guests/{id}` — return single guest with children, 404 if not found
  - `DELETE /api/guests/{id}` — delete guest (children cascade), 204 on success, 404 if not found
  - Depends on: T-09

- [x] **T-12** Config endpoint — `backend/app/routers/config.py`
  - `GET /api/config` — return accommodation name and address from loaded config
  - Requires auth
  - Depends on: T-02, T-07

- [x] **T-13** Guest form component — `frontend/src/components/guest-form.tsx`
  - All fields from the official form
  - Accommodation pre-filled from `GET /api/config`
  - Dynamic children section (add/remove, max 4)
  - Submit calls `POST /api/guests`
  - Depends on: T-08, T-12

- [x] **T-14** New guest page — `frontend/src/app/guests/new/page.tsx`
  - Renders `GuestForm`
  - On success, redirect to `/guests`
  - Depends on: T-13

- [x] **T-15** Guest list page — `frontend/src/app/guests/page.tsx`
  - Fetch and display guests in a table (`guest-table.tsx` component)
  - Columns: Name, Nationality, Stay dates, Passport, PDF status, Actions
  - Delete button with confirmation dialog
  - "New Guest" button linking to `/guests/new`
  - Pagination controls
  - Depends on: T-08, T-10, T-11

---

## Phase 3: PDF & Google Drive

> Goal: Generate official form PDF and upload to Google Drive.

- [x] **T-16** Font setup
  - Download DejaVu Sans TTF (or Liberation Sans)
  - Add to `backend/app/fonts/`
  - Register font with reportlab in app startup
  - Depends on: T-07

- [x] **T-17** PDF generation service — `backend/app/services/pdf.py`
  - Function `generate_pdf(guest: Guest) -> BytesIO`
  - Replicate official form layout: title, stay dates box, fields 1-10, footer
  - Combine `date_of_birth` + `birth_place` for field 3
  - Render up to 4 children for field 10
  - Draw horizontal rules between field rows
  - Form identifier at bottom-right
  - Depends on: T-04, T-16

- [x] **T-18** PDF visual QA script
  - `backend/scripts/generate_sample_pdf.py` — generates a PDF with sample data for visual comparison against the reference form
  - Not part of the app, just a dev tool
  - Depends on: T-17

- [x] **T-19** Google Drive upload service — `backend/app/services/drive.py`
  - Function `upload_to_drive(file_buffer: BytesIO, filename: str) -> str`
  - Authenticate with service account JSON key
  - Upload to configured folder_id
  - Return the Drive file URL
  - Depends on: T-02

- [x] **T-20** PDF generation endpoint
  - `POST /api/guests/{id}/pdf` — load guest, generate PDF, upload to Drive, set `pdf_generated_at`, return `{ url, filename }`
  - Error handling: guest not found (404), PDF generation failure (500), Drive upload failure (500)
  - Frontend: "Generate PDF" button on guest list triggers this endpoint, shows success/error notification
  - Depends on: T-17, T-19, T-15

---

## Phase 4: Frontend Polish (P1 requirements)

> Goal: Search, filters, validation, and notifications.

- [x] **T-21** Guest search — backend
  - Add `search` query param to `GET /api/guests`
  - Case-insensitive search on `first_name` and `last_name` (ILIKE)
  - Depends on: T-10

- [x] **T-22** Guest filters — backend
  - Add `nationality`, `date_from`, `date_to` query params to `GET /api/guests`
  - Filter by nationality (exact match), date range on `stay_from`
  - Depends on: T-10

- [x] **T-23** Search + filter UI
  - Search input above the guest table
  - Nationality dropdown filter
  - Date range picker for stay dates
  - Debounced search (300ms)
  - Depends on: T-15, T-21, T-22

- [x] **T-24** Client-side form validation
  - Inline error messages on required fields
  - Date validation (stay_to >= stay_from)
  - Visual error state on invalid fields
  - Depends on: T-13

- [x] **T-25** Toast notifications
  - Install/configure shadcn/ui toast component
  - Show success toast on: guest created, guest deleted, PDF generated
  - Show error toast on: API errors, validation failures
  - Depends on: T-14, T-15, T-20

---

## Phase 5: Deployment

> Goal: One-command local setup with Docker Compose.

- [x] **T-26** Backend Dockerfile
  - Python 3.12 slim base
  - Copy requirements.txt, install deps
  - Copy app code, config.yaml, fonts
  - CMD: uvicorn app.main:app
  - Depends on: T-07

- [x] **T-27** Frontend Dockerfile
  - Node 20 base, multi-stage build
  - Install deps, build Next.js, run with standalone output
  - Depends on: T-15

- [x] **T-28** Docker Compose
  - `docker-compose.yml` as defined in design.md
  - PostgreSQL 16 with volume
  - Backend with config + credentials mounts
  - Frontend with API URL env
  - Depends on: T-26, T-27

- [x] **T-29** Environment setup documentation
  - Complete `.env.example` with all variables and comments
  - README.md with: prerequisites, setup steps, running with Docker Compose, Google Drive service account setup
  - Depends on: T-28

---

## Task Dependencies (Critical Path)

```
T-01 → T-02 → T-07 ──→ T-09 → T-10 → T-15 → T-20 → T-28
       T-03 → T-04 ↗        → T-11 ↗       → T-23
              T-05 ↗                         → T-25
       T-06 → T-08 ──────────────→ T-13 → T-14
                                    T-12 ↗
       T-16 → T-17 → T-18
              T-19 ↗→ T-20
```

**Critical path:** T-01 → T-02/T-03 → T-04 → T-05 → T-07 → T-09 → T-10 → T-15 → T-20 → T-28 → T-29

**Parallelizable work:**
- After T-07: backend routes (T-09-T-12) and frontend auth (T-08) can proceed in parallel
- T-16/T-17 (PDF) can proceed in parallel with T-13-T-15 (frontend guest CRUD)
- T-19 (Drive upload) can proceed in parallel with T-17 (PDF generation)
- Phase 4 tasks (T-21-T-25) are independent of Phase 3

---

## Risk Mitigation Tasks

These are embedded in the task list above but called out for visibility:

| Risk | Mitigation Task |
|------|----------------|
| PDF layout mismatch | T-18: Visual QA script for side-by-side comparison with reference PDF |
| Slovak diacritics | T-16: Font setup with DejaVu Sans, verified before PDF work begins |
| Google Drive auth issues | T-19: Drive service isolated, testable independently with a simple upload test |
| fastapi-users breaking changes | T-01: Pin exact dependency versions in requirements.txt |
