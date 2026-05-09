# HireFlow

> AI-powered job search and career development platform.

[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Table of Contents

- [About](#about)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Backend Environment Variables](#backend-environment-variables)
- [Frontend Development](#frontend-development)
- [API Reference](#api-reference)
- [Documentation](#documentation)

---

## About

HireFlow is a full-stack job marketplace and career assistant platform that combines job aggregation, AI-powered career tools, profile verification, and real-time chat.

The repository contains:
- Django backend with REST API and WebSocket support.
- React + Vite frontend.
- AI features for resume analysis, cover letters, salary estimation, mock interviews, and more.
- Job aggregation and matching services.

---

## Project Structure

- `hireflow/` — Django project configuration and routing.
- `users/` — authentication, profile management, and user API.
- `jobs/` — internal job posting and job detail APIs.
- `applications/` — application submission and status updates.
- `chat/` — conversation and messaging APIs.
- `jobs_aggregator/` — external job aggregation, search, and matching.
- `ai_features/` — AI-powered career tools and document generation.
- `src/` — React frontend app built with Vite.
- `requirements.txt` — Python dependencies.
- `package.json` — frontend dependencies and scripts.

---

## Getting Started

### Prerequisites
- Python 3.10 or newer
- Node.js 18+ / npm
- PostgreSQL 14+
- Git

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/eyadstein/Hireflow-land-a-job-.git
cd 'd:\Semester 6\Software\Project\Hireflow-land-a-job-'
```

2. Create and activate a Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the repository root with the values described below.

5. Create the PostgreSQL database:
```bash
psql -U postgres -c "CREATE DATABASE hireflow;"
```

6. Apply Django migrations:
```bash
python manage.py migrate
```

7. Create an admin user:
```bash
python manage.py createsuperuser
```

8. Run the backend server:
```bash
python manage.py runserver
```

The backend will be available at `http://127.0.0.1:8000`.

---

## Backend Environment Variables

The backend currently reads these values from the environment:

- `SECRET_KEY` — Django secret key.
- `DEBUG` — set to `False` in production.
- `DB_NAME` — database name (`hireflow` by default).
- `DB_USER` — database user (`postgres` by default).
- `DB_PASSWORD` — database password (`postgres` by default).
- `DB_HOST` — database host (`localhost` by default).
- `DB_PORT` — database port (`5432` by default).
- `GEMINI_KEY` — AI service key used by the AI feature endpoints.

> Note: The repository includes a local `db.sqlite3` file, but the Django settings are configured for PostgreSQL by default.

---

## Frontend Development

Install frontend dependencies and run the React app:

```bash
npm install
npm run dev
```

The frontend will be served by Vite, typically at `http://127.0.0.1:5173`.

---

## API Reference

Most API endpoints live under the `/api/` namespace.

### Authentication
- `POST /api/users/register/`
- `POST /api/users/login/`
- `POST /api/users/refresh/`
- `GET /api/users/profile/`
- `PATCH /api/users/profile/`
- `GET /api/users/all/`

### Jobs
- `GET /api/jobs/`
- `POST /api/jobs/`
- `GET /api/jobs/<id>/`

### Applications
- `POST /api/applications/apply/`
- `GET /api/applications/mine/`
- `GET /api/applications/job/<job_id>/`
- `PATCH /api/applications/<id>/status/`

### Chat
- `GET /api/chat/<user_id>/`

### AI Features
- `POST /api/ai/resume-analyzer/`
- `POST /api/ai/cover-letter/`
- `POST /api/ai/salary-estimator/`
- `POST /api/ai/interview-coach/`
- `POST /api/ai/chat/`
- `GET /api/ai/career-roadmap/`
- `GET /api/ai/career-roadmap/<id>/`
- `POST /api/ai/cv/`
- `POST /api/ai/cv/build/`
- `GET /api/ai/cv/<id>/download/`
- `POST /api/ai/mock-interview/start/`
- `POST /api/ai/mock-interview/submit/`
- `GET /api/ai/mock-interview/history/`
- `GET /api/ai/mock-interview/<id>/`
- `POST /api/ai/linkedin/`
- `POST /api/ai/linkedin/optimize/`
- `GET /api/ai/linkedin/<id>/`

### Job Aggregator
- `GET /api/jobs-aggregator/search/`
- `GET /api/jobs-aggregator/countries/`
- `GET /api/jobs-aggregator/stats/`
- `GET /api/jobs-aggregator/match/`

---

## Documentation

Expanded documentation is available in the `docs/` folder:
- `docs/architecture.md` — architecture and component overview.
- `docs/api-reference.md` — endpoint reference.

---

## Notes

- This repository combines both backend and frontend code in the same root.
- For production, set `DEBUG=False`, configure allowed hosts, and use secure secrets management.
- Review any third-party API keys or external integration settings before deploying.
