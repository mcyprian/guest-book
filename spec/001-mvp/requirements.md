# MVP Requirements

**Spec:** 001-mvp
**Source:** [Master Spec](../master-spec.md) + official form [T MV SR 11-060-1 VII/2018](../examples/hlasenie-pobytu-SVK.pdf)
**Status:** Draft

---

## Feature Overview

Deliver a working fullstack application that lets an accommodation provider in Slovakia:
1. Enter foreign guest data through a web form.
2. Store and manage guest records in a database.
3. Generate a pre-filled "Hlasenie pobytu" PDF matching the official form layout.
4. Upload the PDF to Google Drive.

The MVP targets a single user operating a single property.

---

## User Stories

### US-1: Register and log in
**As** an accommodation provider,
**I want** to log in,
**so that** only I can access guest data.

**Acceptance criteria:**
- User can register with email and password (single auth prefilled in production env for MVP, no explicit user accounts).
- User can log in and receive a JWT token.
- All `/api/*` endpoints reject unauthenticated requests with 401.
- Token expiry is handled (user is redirected to login).

### US-2: Configure accommodation details
**As** an accommodation provider,
**I want** to set my property name and address once (static YAML config),
**so that** it is automatically filled in for every guest record and PDF.

**Acceptance criteria:**
- Accommodation name, address, and Google Drive folder ID are configured in `config.yaml`.
- No settings UI in MVP — values are edited directly in the YAML file.
- Backend reads config on startup and exposes it via API for the frontend.
- Field 9 on new guest forms is pre-filled with the configured accommodation details.

### US-3: Create a guest record
**As** a foriegn accommodation guest,
**I want** to enter a my data via a web form,
**so that** the record is saved and available for PDF generation.

**Acceptance criteria:**
- Form contains all fields from the official form (see Functional Requirements).
- Required fields are validated before submission.
- Accommodation name/address (field 9) is pre-filled from configuration.
- Up to 4 accompanying children can be added (field 10).
- On success, user is redirected to the guest list.

### US-4: View, search, and filter guests
**As** an accommodation provider,
**I want** to see all guest records in a table and filter them,
**so that** I can quickly find a specific guest.

**Acceptance criteria:**
- Guest list displays key columns: name, nationality, stay dates, passport number.
- Search by guest name (first or last).
- Filter by date range (stay_from / stay_to).
- Filter by nationality.
- Results are paginated.

### US-5: Delete a guest record
**As** an accommodation provider,
**I want** to delete a guest record,
**so that** I can remove entries created by mistake.

**Acceptance criteria:**
- Confirmation dialog before deletion.
- Associated children records are deleted (cascade).
- Record is removed from the list.

### US-6: Generate and upload PDF
**As** an accommodation provider,
**I want** to generate a pre-filled PDF and upload it to Google Drive,
**so that** I have a digital copy of the official form ready for submission.

**Acceptance criteria:**
- PDF layout matches the official T MV SR 11-060-1 VII/2018 form.
- All guest data fields are placed in the correct positions on the PDF.
- Slovak labels and field numbering match the original form exactly.
- PDF is uploaded to the configured Google Drive folder.
- File is named `{last_name}_{first_name}_{stay_from}.pdf`.
- User sees a success/failure notification after the operation.

---

## Functional Requirements

### P0 — Must Have

| ID | Requirement | Story |
|----|-------------|-------|
| F-01 | JWT-based authentication (register + login) | US-1 |
| F-02 | Guest create form with all official fields: stay_from, stay_to, first_name, last_name, date_of_birth, birth_place (incl. state), nationality, permanent_address, travel_purpose, passport_number, visa_details (optional), accommodation (pre-filled), children (0-4) | US-3 |
| F-03 | Server-side validation: all required fields present, dates are valid, stay_to >= stay_from | US-3 |
| F-04 | Guest list page with pagination | US-4 |
| F-05 | Delete guest record with cascade delete of children | US-5 |
| F-06 | PDF generation matching official form layout (T MV SR 11-060-1 VII/2018) | US-6 |
| F-07 | Upload generated PDF to Google Drive folder | US-6 |
| F-08 | Accommodation name and address read from `config.yaml` and pre-filled on forms | US-2 |
| F-09 | Google Drive folder ID read from `config.yaml` | US-2 |

### P1 — Should Have

| ID | Requirement | Story |
|----|-------------|-------|
| F-11 | Search guests by name | US-4 |
| F-12 | Filter guests by date range | US-4 |
| F-13 | Filter guests by nationality | US-4 |
| F-14 | Client-side form validation with inline error messages | US-3 |
| F-15 | Success/error toast notifications for all mutations | All |


## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NF-01 | Security | Passwords hashed (bcrypt or argon2). JWT tokens have expiry. |
| NF-02 | Security | All API endpoints behind authentication. No guest data exposed without valid token. |
| NF-03 | Security | Google Drive credentials stored as environment variables, never committed to repo. |
| NF-04 | Performance | Guest list loads within 1s for up to 1,000 records. |
| NF-05 | PDF fidelity | Generated PDF must be visually comparable to the official form — field positions, labels, and numbering must match. |
| NF-06 | Data integrity | All DB writes use transactions. Children cascade-delete with parent guest. |
| NF-07 | Deployability | App runs locally via `docker compose up` with zero manual setup beyond env vars. |
| NF-08 | Deployability | Frontend deployable to Vercel; backend deployable as Vercel serverless function. |
| NF-09 | Maintainability | Backend has typed Pydantic models for all request/response schemas. |
| NF-10 | Maintainability | Frontend uses TypeScript with strict mode. |

---

## Constraints and Assumptions

### Constraints
- PDF layout is defined by the official form T MV SR 11-060-1 VII/2018 — we cannot alter it.
- Google Drive upload requires a service account with pre-configured access to the target folder.
- Slovak diacritics (e.g. s, z, c, t, d, l, n, a, e, i, o, u with haceks/acutes) must render correctly in the PDF.

### Assumptions
- The app serves a single user (the accommodation provider). No multi-tenancy.
- The user has a Google Cloud service account JSON key file.
- PostgreSQL is available (via Docker locally, managed service in production).
- The official form layout has not changed since VII/2018.

---

## Out of Scope (MVP)

- Multi-user accounts / role-based access control
- Guest entry edits
- Multi-property support
- Batch PDF generation or export
- Email or push notifications
- Passport OCR / camera scanning
- UI localization (UI is English-only; PDF output is Slovak per the official form)
- Offline / PWA support
- Audit log / change history

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Guest record creation | End-to-end form submission in under 2 minutes |
| PDF accuracy | All 10 form fields correctly placed and filled |
| PDF upload | Successful upload to Google Drive with correct file name |
| Data retrieval | Find any guest by name within 3 clicks from the guest list |
| Deployment | `docker compose up` to working app in under 2 minutes |

---

## Open Questions

1. **API completeness:** Master spec lists only GET and POST for guests. MVP needs a DELETE endpoint — should be added to the API design. PUT is deferred (no edits in MVP).
2. **Field 3 numbering:** The official form uses field 3 for both date of birth and place of birth (combined field). The master spec splits them into two rows both numbered 3. Should the DB keep them separate (date_of_birth + birth_place) but combine them on the PDF?
3. **Accommodation storage:** Should accommodation name/address be stored per guest record (snapshot at time of creation) or resolved from config at PDF generation time? Storing per-record is safer if the provider changes address.
