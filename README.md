# HireFlow

AI-powered job marketplace and career assistant platform.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19.2.5-blue)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## About

HireFlow is a combined backend + frontend job platform for job seekers and recruiters, currently in active development.

It provides:
- Job posting, application tracking, and recruiter dashboards.
- AI tools for resume analysis, cover letters, salary estimation, interview practice, and CV generation.
- External job aggregation and candidate matching.
- A React SPA served by Django with a single deployable project root.

### Current Development Status
- **Core Backend APIs** — In progress (auth, jobs, applications, chat APIs functional)
- **Frontend UI** — In progress (React components being built with Tailwind CSS and Radix UI)
- **AI Features** — In development (CV generator, career assistant agent framework ready)
- **Job Aggregation** — Partially implemented (external job fetching framework in place)
- **Candidate Matching & CRM** — Architecture defined, integration in progress

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

## Current State & Development Notes

### Recently Updated
- Migration files for applications, jobs, and candidate notes (May 2025)
- Multiple database backups indicate ongoing schema refinements and data migrations
- Chat and messaging infrastructure with WebSocket routing in place

### In Active Development
- **Frontend Pages** — React components for job search, applications, recruiter dashboard
- **AI Integration** — CV generator and career assistant agent framework
- **Job Matching** — Candidate-to-job matching algorithms and recommendation engine
- **CRM Features** — Candidate pipeline management and engagement tracking

### Areas Needing Attention
- **Production Readiness**
  - `DEBUG=True` is enabled in `hireflow/settings.py` — must be disabled for production
  - `SECRET_KEY` is hardcoded in settings — move to environment variables
  - `ALLOWED_HOSTS` and `CORS_ALLOW_ALL_ORIGINS` are wide open — restrict for production
  - Channels use in-memory layers instead of Redis for WebSocket support
  
- **Code Quality**
  - `jobs/views.py` is large and should be refactored into smaller modules
  - Business logic mixed into views instead of dedicated service modules
  - Frontend components need testing and storybook documentation
  
- **Testing & Documentation**
  - No API documentation (Swagger/OpenAPI not yet implemented)
  - Limited automated tests in the repository
  - Need integration tests for AI endpoints and matching algorithms
  
- **Feature Gaps**
  - AI tools require valid `GEMINI_KEY` and `GROQ_API_KEY` to operate fully
  - Chat UI uses REST polling instead of real-time WebSocket
  - Candidate matching and CRM features need integration testing with frontend
  - No comprehensive error handling for third-party API failures

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

## Recommended Next Actions (Priority Order)

1. **Security Hardening** — Move `SECRET_KEY`, `ALLOWED_HOSTS`, and CORS settings to environment variables before any production deployment.
2. **Frontend Completion** — Finalize React UI for job search, application tracking, and recruiter dashboard.
3. **AI Feature Testing** — Validate CV generator and career assistant endpoints with real API keys and error handling.
4. **API Documentation** — Add Swagger/OpenAPI schema documentation for all endpoints.
5. **Code Refactoring** — Extract business logic from views into dedicated service modules (start with `jobs/views.py`).
6. **Integration Testing** — Add tests for candidate matching, AI features, and external job aggregation.
7. **WebSocket Chat** — Decide whether to implement real-time chat or remove WebSocket routing.
8. **Deployment** — Add containerization (Docker) and deployment documentation.

---

## Documentation

See `docs/architecture.md` and `docs/api-reference.md` for additional architecture and API details.

---

## License

This project is licensed under the MIT License.