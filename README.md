# Guest Book

A web application for accommodation providers in Slovakia to collect foreign guest data and generate pre-filled "Hlasenie pobytu" (Police Registration) PDF forms.

## Prerequisites

- Docker and Docker Compose
- Google Cloud service account with Drive API access (for PDF upload)

## Quick Start

1. **Clone and configure:**

   ```bash
   cp .env.example .env
   # Edit .env with your JWT secret and user credentials
   ```

2. **Configure accommodation details:**

   Edit `backend/config.yaml` with your property name, address, and Google Drive folder ID.

3. **Set up Google Drive (optional):**

   Place your Google Cloud service account JSON key at `credentials/service-account.json`. The service account must have write access to the Google Drive folder specified in `config.yaml`.

   ```bash
   mkdir -p credentials
   cp /path/to/your/service-account.json credentials/service-account.json
   ```

4. **Start the application:**

   ```bash
   docker compose up --build
   ```

5. **Access the app:**

   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

   Log in with the credentials from your `.env` file (default: `admin@example.com` / `changeme`).

## Development (without Docker)

### Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Requires a running PostgreSQL instance. Set `DATABASE_URL` in `.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local`.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, React, TypeScript, shadcn/ui, Tailwind CSS |
| Backend | FastAPI, Python 3.12 |
| Auth | fastapi-users (JWT) |
| Database | PostgreSQL, async SQLAlchemy |
| PDF | reportlab |
| Cloud Storage | Google Drive API |
| Deployment | Docker Compose |

## Project Structure

```
guest-book/
├── backend/          # FastAPI application
│   ├── app/          # Main package (models, routes, services)
│   └── config.yaml   # Accommodation + Drive config
├── frontend/         # Next.js application
│   └── src/          # Pages, components, hooks
├── credentials/      # Google service account key (gitignored)
├── docker-compose.yml
├── .env.example
└── spec/             # Project specifications
```
