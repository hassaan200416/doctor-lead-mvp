## Healthcare Lead Management System

This project is a full stack healthcare lead management system built using FastAPI and React. It ingests NPPES physician data, stores it in a PostgreSQL database, and exposes a secure API for querying leads. The frontend provides a usable internal tool for filtering, searching, paginating, and exporting healthcare leads.

### Features

**Backend**

- **Data ingestion from NPPES dataset**: Loads and filters raw CSV data, cleans it, and inserts leads into PostgreSQL.
- **PostgreSQL database storage**: Persists normalized lead records (NPI, name, phone, specialty, state, timestamps).
- **Filtering by state and specialty**: Query engine supports exact filters on state and taxonomy specialty code.
- **Name-based search**: Case-insensitive search on provider name using `ILIKE`.
- **Offset/limit pagination**: Supports `limit` and `offset` with total count for proper pagination.
- **CSV export endpoint**: Returns filtered leads as a downloadable CSV file.
- **API key authentication**: All lead routes require a valid `X-API-Key` header.

**Frontend**

- **Login screen with API key**: Simple login page where the user enters the backend API key.
- **Protected routes**: Leads UI only loads once a valid key is present in localStorage.
- **Debounced search**: Name search input debounces requests to reduce backend load.
- **Paginated table**: Displays leads with correct `Page X of Y` behavior.
- **Disabled pagination controls**: Previous/Next buttons are disabled when on first/last page.
- **Loading overlay**: Shows a subtle loading state over the table while data is fetching.
- **Empty state handling**: Displays “No leads match your filters.” when there are no results.
- **CSV file download**: Export button downloads filtered leads as a CSV using the export endpoint.

### Tech Stack

**Backend**

- **Python**
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Uvicorn**

**Frontend**

- **React**
- **TypeScript**
- **Vite**
- **Axios**

### Project Structure

**Backend**

```text
backend/
 ├── data/
 │    └── npi_raw.csv
 ├── src/
 │    ├── main.py              # FastAPI app entrypoint
 │    ├── api/
 │    │    └── routes/
 │    │         └── lead_routes.py
 │    ├── core/
 │    │    ├── config.py       # Settings and environment configuration
 │    │    └── security.py     # API key verification dependency
 │    ├── db/
 │    │    ├── database.py     # Engine and Base
 │    │    ├── session.py      # SessionLocal factory
 │    │    └── models.py       # Re-exports ORM models
 │    ├── models/
 │    │    └── lead.py         # Lead ORM model
 │    ├── schemas/
 │    │    └── lead.py         # Pydantic schemas for leads
 │    ├── services/
 │    │    ├── lead_service.py # Lead query logic + CSV export
 │    │    └── npi_loader.py   # CSV filtering/cleaning pipeline
 │    └── scripts/
 │         └── run_import.py   # Command-line importer for NPPES CSV
 └── .env
```

**Frontend**

```text
frontend/
 ├── src/
 │    ├── api/
 │    │    ├── client.ts       # Axios client with API base URL and X-API-Key header
 │    │    └── leads.ts        # Leads API wrappers (list + export)
 │    ├── components/
 │    │    ├── Filters.tsx     # Search, state, specialty, export button
 │    │    ├── LeadsTable.tsx  # Table rendering + loading/empty states
 │    │    └── Pagination.tsx  # Page/limit controls
 │    ├── pages/
 │    │    ├── LeadsPage.tsx   # Orchestrates state, effects, and children
 │    │    └── LoginPage.tsx   # API key login screen
 │    ├── types/
 │    │    └── lead.ts         # LeadResponse / LeadListResponse types
 │    ├── App.tsx              # App-level routing based on API key
 │    └── main.tsx             # React/Vite bootstrap
 └── package.json
```

### How It Works (Architecture Overview)

1. **User login and API key handling**
   - User opens the frontend and sees the login screen.
   - User enters an API key; the key is saved to `localStorage` under `apiKey`.
   - `App.tsx` reads `apiKey` and, if present, renders the leads UI.

2. **Attaching API key to requests**
   - The Axios client (`api/client.ts`) has a request interceptor.
   - Before each request, it reads `localStorage.apiKey` and sets the `X-API-Key` header if present.

3. **Backend authentication**
   - All `/api/v1/leads` routes use the `verify_api_key` dependency.
   - `verify_api_key` reads the `X-API-Key` header and compares it to `settings.API_KEY` from `.env`.
   - If missing or incorrect, FastAPI returns `401 Unauthorized`.

4. **Lead query flow**
   - `LeadsPage` maintains query state (`stateFilter`, `specialtyFilter`, `searchTerm`, `limit`, `offset`).
   - A debounced `searchTerm` and filters feed into `getLeads` calls.
   - Backend `get_leads_with_count` builds a SQLAlchemy query with optional `state`, `specialty`, and name `ILIKE` search, computes `total`, then applies `offset` and `limit`.
   - The API returns a typed payload: `{ total, limit, offset, data: LeadResponse[] }`.
   - React updates table rows and pagination info accordingly.

5. **CSV export**
   - The export button in `Filters` calls `exportLeads` with the current filters/search.
   - Backend `export_leads_to_csv` applies the same filters (no pagination) and streams a CSV.
   - Frontend receives a blob, creates a temporary object URL, and triggers a `leads.csv` download.

### Setup Instructions

#### Backend Setup

1. **Clone repository**

```bash
git clone <repo-url>
cd doctor-lead-mvp/backend
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1    # PowerShell on Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in `backend/`:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
API_KEY=your-secret-api-key
```

5. **Run the server**

```bash
uvicorn src.main:app --reload
```

6. **Access API docs**

Open: `http://127.0.0.1:8000/docs`

#### Frontend Setup

1. **Navigate to frontend**

```bash
cd ../frontend
```

2. **Install dependencies**

```bash
npm install
```

3. **Start dev server**

```bash
npm run dev
```

4. **Open browser**

Visit: `http://localhost:5173`

### Environment Variables

Backend `.env` (not committed to version control) should define:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
API_KEY=your-secret-api-key
ABSTRACT_EMAIL_API_KEY=your-abstract-email-key   # optional for email validation endpoint
```

These values are loaded via `core/config.py` using Pydantic settings.

### API Endpoints

All endpoints require the header:

```http
X-API-Key: your-secret-api-key
```

**List leads**

- **GET** `/api/v1/leads/`
- Query parameters:
  - `state` (optional): 2-letter state code (e.g. `TX`)
  - `specialty` (optional): taxonomy code (e.g. `363LF0000X`)
  - `search` (optional): case-insensitive name search
  - `limit` (optional, default 50)
  - `offset` (optional, default 0)
- Response:

```json
{
  "total": 1318,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "uuid",
      "npi": "string",
      "name": "string",
      "phone": "string",
      "specialty": "string",
      "state": "string",
      "created_at": "ISO timestamp"
    }
  ]
}
```

**Export leads as CSV**

- **GET** `/api/v1/leads/export`
- Query parameters:
  - `state` (optional)
  - `specialty` (optional)
  - `search` (optional)
- Response:
  - `text/csv` file download (`leads.csv`) with `id,npi,name,phone,specialty,state,created_at` columns.

**Validate email (optional integration)**

- **POST** `/api/v1/leads/{npi}/validate-email`
- Body:

```json
{ "email": "example@test.com" }
```

- Calls Abstract Email API to validate deliverability; currently does not persist email in the DB.

### Pagination Logic

- Backend:
  - Accepts `limit` and `offset`.
  - Computes `total` based on the filtered query before pagination.
  - Returns `{ total, limit, offset, data }`.
- Frontend:
  - Computes:
    - `currentPage = Math.floor(offset / limit) + 1`
    - `totalPages = Math.ceil(total / limit)`
  - Disables:
    - `Previous` when `offset === 0`
    - `Next` when `offset + limit >= total`

This ensures consistent pagination across API and UI.

### Authentication Mechanism

- API key is stored on the backend in environment (`API_KEY`) and loaded via `settings.API_KEY`.
- Each leads route has a router-level dependency `verify_api_key`.
- `verify_api_key` checks the `X-API-Key` header and raises `HTTPException(401)` for missing/invalid keys.
- Axios response interceptor:
  - On `401`, removes the stored key, records an error message, and reloads the page.
- Login page reads the error message and shows “Invalid API key. Please try again.” then prompts for a new key.

### Known Limitations

- Uses static API key authentication instead of JWT or OAuth2.
- No user roles or per-user permissions.
- No server-side sorting of results (filters and search only).
- No create/update/delete flows in the UI (read-only for now).
- Not deployed to a production environment; configuration assumes local development.

### Conclusion

This project demonstrates a complete full stack workflow including data ingestion from NPPES, backend API design with filtering/pagination/export, API key authentication, and a React/TypeScript frontend that consumes the API. The codebase follows clear separation of concerns between models, schemas, services, routes, and UI components, making it a solid foundation for further extension into a production-grade healthcare lead management tool.

