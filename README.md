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

- `hireflow/` — Django config, settings, URLs, ASGI/WSGI entrypoints
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

### Completed Features (May 2026)

#### Recruiter Portal
- **Candidate Pipeline** — Candidates flow through: Pending → Screening → Interview → Offer → Accepted/Rejected. Each stage exposes contextually appropriate action buttons.
- **Bulk Decisions** — Select multiple candidates for screening, interview, accept, or reject in one action. Per-candidate quick actions include Screening, Interview, Accept, Reject.
- **Candidate Compare** — Select 2–4 candidates from the same job for side-by-side comparison. Scores are normalized relative to the selected group (best in group = 100%). The recruiter is excluded from comparisons.
- **Messaging** — Real-time-style chat with role-based user list, auto-scroll, and proper sender identification.
- **Analytics, Performance, Alerts, Optimize** — Available in the recruiter portal.

#### Jobseeker Portal
- **Dashboard, Jobs, Applications, Tracker** — Core job management features.
- **AI Tools** — Resume AI, Skill Gap, ATS Check, Cover Letter, Interview Coach, Salary Estimator, Career Roadmap, AI Assistant.
- **Messaging** — Communicate with recruiters via the Messages page.

### In Active Development
- **AI Integration** — CV generator and career assistant agent framework
- **Job Aggregation** — External job search and matching via Adzuna/JSearch APIs
- **WebSocket Chat** — Currently using REST polling every 3 seconds

### Areas Needing Attention

**Production Readiness**
- `DEBUG=True` is enabled in `hireflow/settings.py` — must be disabled for production
- `SECRET_KEY` is hardcoded in settings — move to environment variables
- `ALLOWED_HOSTS` and `CORS_ALLOW_ALL_ORIGINS` are wide open — restrict for production
- Channels use in-memory layers instead of Redis for WebSocket support

**Code Quality**
- `jobs/views.py` is large and should be refactored into smaller modules
- Business logic mixed into views instead of dedicated service modules
- Frontend components need testing

**Testing & Documentation**
- No API documentation (Swagger/OpenAPI not yet implemented)
- Limited automated tests
- Need integration tests for AI endpoints and matching algorithms

**Feature Gaps**
- AI tools require valid `GEMINI_KEY` and `GROQ_API_KEY` to operate fully
- Chat UI uses REST polling instead of real-time WebSocket
- No comprehensive error handling for third-party API failures

---

## API Quick Reference

Primary endpoints are served from `/api/`.

- `/api/users/` — auth and profile APIs
- `/api/jobs/` — job management and analytics
- `/api/applications/` — applications, compare, bulk decisions, candidate notes
- `/api/chat/` — messaging APIs
- `/api/ai/` — AI career tools
- `/api/jobs-aggregator/` — external job search
- `/api/candidate-matching/` — matching workflows
- `/api/candidate-crm/` — CRM actions

### Key Recruiter Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jobs/dashboard/` | GET | Dashboard stats |
| `/api/jobs/my-jobs/` | GET | Recruiter's posted jobs |
| `/api/applications/job/{jobId}/` | GET | Candidates for a job |
| `/api/applications/{id}/status/` | PATCH | Update candidate status |
| `/api/applications/bulk-decision/` | POST | Bulk status update |
| `/api/applications/compare/` | POST | Compare 2–4 candidates |
| `/api/applications/job/{jobId}/reject-all-active/` | POST | Reject all active candidates |
| `/api/applications/job/{jobId}/accept-top/` | POST | Accept top N candidates |

---

## Recruiter Sidebar Navigation

The recruiter sidebar contains:

1. Dashboard
2. My Jobs
3. Candidates
4. Analytics
5. Performance
6. Compare
7. Bulk Decisions
8. Optimize
9. Alerts
10. Messages
11. Profile

---

## Candidate Pipeline Workflow

```
Applied → Pending → Screening → Interview → Offer → Accepted
                                                  ↘ Rejected
```

At each stage the recruiter sees contextually relevant action buttons:
- **Pending**: Move to Screening, Reject
- **Screening**: Move to Interview, Accept, Reject
- **Interview**: Make Offer, Accept, Reject
- **Offer**: Accept, Reject
- **Accepted / Rejected**: Final — no further actions

---

## Recommended Next Actions (Priority Order)

1. **Security Hardening** — Move `SECRET_KEY`, `ALLOWED_HOSTS`, and CORS settings to environment variables before any production deployment.
2. **Frontend Testing** — Add automated tests for key recruiter and jobseeker flows.
3. **AI Feature Testing** — Validate CV generator and career assistant endpoints with real API keys and error handling.
4. **API Documentation** — Add Swagger/OpenAPI schema documentation for all endpoints.
5. **Code Refactoring** — Extract business logic from views into dedicated service modules (start with `jobs/views.py`).
6. **WebSocket Chat** — Decide whether to implement real-time chat or remove WebSocket routing.
7. **Deployment** — Add containerization (Docker) and deployment documentation.

---

## Documentation

See `docs/architecture.md` and `docs/api-reference.md` for additional architecture and API details.

---

## License

This project is licensed under the MIT License.
