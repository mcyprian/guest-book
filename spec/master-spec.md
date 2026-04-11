# Guest Book - High Level Specification

## Overview

A fullstack web application for accommodation providers in Slovakia to collect personal data from foreign guests, store it in a database, and generate pre-filled "Hlasenie pobytu" (Police Registration) PDF forms as required by Slovak law.

## Problem Statement

Accommodation providers must collect specific data from foreign guests and submit the official "Hlasenie pobytu" form (T MV SR 11-060-1) to the foreign police. Currently this is done manually on paper, which is error-prone, slow, and hard to archive. This app digitizes the workflow.

## Core Features

### 1. Guest Data Entry Form

A web form capturing all fields from the official PDF:

| # | Field | Type | Required |
|---|-------|------|----------|
| - | Stay from (Pobyt od) | Date | Yes |
| - | Stay to (Pobyt do) | Date | Yes |
| 1 | First name (Meno) | Text | Yes |
| 2 | Surname (Priezvisko) | Text | Yes |
| 3 | Date of birth (Datum narodenia) | Date | Yes |
| 3 | Place of birth incl. state (Miesto narodenia, stat) | Text | Yes |
| 4 | Nationality (Statna prislusnost) | Text | Yes |
| 5 | Permanent address in home country (Trvaly pobyt) | Text | Yes |
| 6 | Purpose of travel to Slovakia (Ucel cesty) | Text | Yes |
| 7 | Passport number (Cislo pasu) | Text | Yes |
| 8 | Visa / EU residence permit details (type, number, validity, place of issue) | Text | No |
| 9 | Accommodation name and address in Slovakia | Text | Yes (pre-filled from config) |
| 10 | Accompanying children (up to 4) | List of text | No |

### 2. Guest Database

- Store all submitted guest records persistently.
- List / search / filter guests by name, date of stay, nationality.
- Edit and delete existing records.
- Each record has timestamps (created, updated).

### 3. PDF Generation & Upload

- Generate the official "Hlasenie pobytu" PDF pre-filled with guest data.
- The generated PDF must match the layout of the official form (T MV SR 11-060-1 VII/2018).
- Upload the generated PDF to a configured Google Drive folder.
- File naming convention: `{last_name}_{first_name}_{stay_from}.pdf` (e.g. `Smith_John_2026-04-11.pdf`).

### 4. Accommodation Configuration

- Configure the accommodation provider's name and address (field 9) once.
- This value is automatically pre-filled for every new guest entry.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js (React + TypeScript) |
| UI Components | shadcn/ui + Tailwind CSS |
| Backend | FastAPI (Python) |
| Auth | fastapi-users (JWT-based) |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| PDF Generation | reportlab (Python) |
| Google Drive | Google Drive API (service account) |
| Containerization | Docker Compose (app + db) |

## Architecture

```
Browser (Next.js)
    |
    | REST API (JSON)
    v
FastAPI Backend
    |
    |-- SQLAlchemy --> PostgreSQL
    |
    |-- reportlab  --> PDF file --> Google Drive API
```

### API Endpoints

All `/api/*` endpoints require a valid JWT token.

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Register a new user |
| POST | /api/auth/login | Login, returns JWT |
| GET | /api/guests | List all guests |
| POST | /api/guests | Create a new guest record |
| GET | /api/guests/{id} | Get a single guest |

### Database Schema

**guests**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| stay_from | DATE | |
| stay_to | DATE | |
| first_name | VARCHAR | |
| last_name | VARCHAR | |
| date_of_birth | DATE | |
| birth_place | VARCHAR | City, country |
| nationality | VARCHAR | |
| permanent_address | TEXT | Full address in home country |
| travel_purpose | VARCHAR | |
| passport_number | VARCHAR | |
| visa_details | TEXT | Nullable |
| created_at | TIMESTAMP | |
| updated_at | TIMESTAMP | |

**children**

| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| guest_id | UUID | FK -> guests.id |
| name | VARCHAR | Child's full name |

### Configuration File

Accommodation details are stored in a YAML config file (`config.yaml`):

```yaml
accommodation:
  name: "Hotel Example"
  address: "123 Main Street, Bratislava"
google_drive:
  folder_id: "your-google-drive-folder-id"
```

## Pages / Screens

1. **Guest List** - Table with search, filter by date range / nationality, pagination. Action buttons: view, edit, delete, generate & upload PDF.
2. **New Guest Form** - Form with all fields, accommodation pre-filled from config.
3. **Edit Guest** - Same form, pre-populated with existing data.
4. **Settings** - Configure accommodation name and address, Google Drive folder ID.

## Out of Scope (v1)

- Multi-user / roles
- Multi-property (single accommodation only)
- Batch PDF export
- Email / notification features
- Passport OCR / scanning
- Localization (UI will be in English, PDF output in Slovak as per the official form)

## Deployment

### Local (Docker Compose)

- `docker compose up` starts both the PostgreSQL database and the FastAPI backend.
- Environment variables for DB credentials, app port, and Google Drive service account key path / folder ID.
- Data persists via a Docker volume for PostgreSQL.

### Production (Vercel + hosted services)

- **Frontend (Next.js):** Deployed to Vercel.
- **Backend (FastAPI):** Deployed as a Vercel serverless function via the Python runtime.
- **Database:** Managed PostgreSQL (e.g. Vercel Postgres, Supabase, or Neon).
- Environment variables configured in Vercel project settings (DB connection string, JWT secret, Google Drive credentials).
