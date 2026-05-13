# HireFlow

AI-powered job marketplace and career assistant platform.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19.2.5-blue)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## About

HireFlow is a combined backend + frontend job platform for job seekers and recruiters.

It provides:
- Job posting, application tracking, and recruiter dashboards.
- AI tools for resume analysis, cover letters, salary estimation, interview practice, and CV generation.
- External job aggregation and candidate matching.
- A React SPA served by Django with a single deployable project root.

---

## Technology Stack

- Backend: Django 6, Django REST Framework, Django Channels
- Frontend: React 19, Vite, Tailwind CSS, Radix UI
- Database: SQLite for local development, PostgreSQL optional in production
- AI: `google-generativeai`, `groq`, `pdfplumber`
- ML: `scikit-learn`

---

## Prerequisites

- Python 3.10 or newer
- Node.js 18+ and npm
- Git
- Optional: PostgreSQL 14+ if using a production database

---

## Setup

1. Clone the repository:

```powershell
git clone <repo-url>
cd "d:\Semester 6\Software\Project\Hireflow-land-a-job-"
```

2. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

4. Install frontend dependencies:

```powershell
npm install
```

5. Create `.env.local` in the repository root and add the keys below.

6. Build the frontend and start the app:

```powershell
.\start.ps1
```

The app is served at `http://localhost:8000`.

---

## Environment Variables

Create `.env.local` with:

```env
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=hireflow
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
GEMINI_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
JSEARCH_KEY=your_jsearch_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
```

Notes:
- If `DB_NAME` is unset, the project uses local `db.sqlite3`.
- `DEBUG=True` is fine for local development but must be disabled for production.
- `.env.local` is loaded by `python-dotenv` in `hireflow/settings.py`.

---

## Running Locally

The `start.ps1` script does:
- `npm run build`
- `python manage.py migrate`
- `python manage.py runserver`

If you only want to run the backend and build once:

```powershell
npm run build
python manage.py migrate
python manage.py runserver
```

For frontend-only development:

```powershell
npm run dev
```

> Use `npm run dev` only for frontend debugging. Production mode relies on the built `dist/` folder served by Django.

---

## Project Structure

- `hireflow/` — Django config, settings, URLs, ASGI/WGSI entrypoints
- `users/` — auth, custom user model, profile APIs
- `jobs/` — job posting, recruiter analytics, optimization logic
- `applications/` — application models, candidate notes, status updates
- `chat/` — messaging API and optional websocket routing
- `jobs_aggregator/` — external job search and aggregator service
- `ai_features/` — resume, cover letter, salary, interview, CV, and LinkedIn AI tools
- `candidate_matching/` — matching logic and ranking
- `candidate_crm/` — CRM workflows and pipeline management
- `src/` — React SPA
- `dist/` — built React production app
- `db.sqlite3` — local SQLite database
- `requirements.txt` — backend Python dependencies
- `package.json` — frontend dependencies and scripts
- `.env.local` — environment settings (not committed)

---

## Important Notes

- `hireflow/settings.py` currently enables `DEBUG=True`, `ALLOWED_HOSTS=['*']`, and `CORS_ALLOW_ALL_ORIGINS=True`.
- `SECRET_KEY` is hardcoded in settings and must be moved to environment variables before production.
- `dist/` is built into the repository and served by Django; rebuild it after frontend changes.
- `db.sqlite3` is used locally and should not be treated as a production database.
- Chat backend includes websocket routing, but the frontend currently uses REST polling.

---

## Known Issues and Improvements

### Production readiness
- `DEBUG=True` is enabled in `hireflow/settings.py`
- `SECRET_KEY` is hardcoded
- `ALLOWED_HOSTS` and CORS are wide open
- Channels use in-memory layers instead of Redis
- No production deployment or containerization docs

### Functional gaps
- Some AI tools require valid `GEMINI_KEY` and `GROQ_API_KEY` to operate
- Chat UI is not fully real-time; it polls REST endpoints
- Candidate matching and CRM features need integration testing
- No API documentation like Swagger/OpenAPI
- No automated tests in the current repository

### Code quality
- `jobs/views.py` is large and should be split into smaller modules
- Business logic is mixed into view logic instead of dedicated services
- A few frontend pages rely on assumptions about job data shape

---

## API Quick Reference

Primary endpoints are served from `/api/`.

- `/api/users/` — auth and profile APIs
- `/api/jobs/` — job management and analytics
- `/api/applications/` — applications and candidate notes
- `/api/chat/` — messaging APIs
- `/api/ai/` — AI career tools
- `/api/jobs-aggregator/` — external job search
- `/api/candidate-matching/` — matching workflows
- `/api/candidate-crm/` — CRM actions

---

## Recommended Next Actions

1. Add environment-based settings and remove hardcoded secrets.
2. Add API documentation with DRF schema tools.
3. Add basic backend tests for auth, jobs, and applications.
4. Refactor the largest Django views into service modules.
5. Validate AI endpoints with actual API keys and error handling.
6. Decide if WebSocket chat should be used or the websocket route removed.

---

## Documentation

See `docs/architecture.md` and `docs/api-reference.md` for additional architecture and API details.

---

## License

This project is licensed under the MIT License.