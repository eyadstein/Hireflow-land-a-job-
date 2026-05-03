# HireFlow Backend

> AI-Powered Job Search Platform for the Arab World

[![Python](https://img.shields.io/badge/Python-3.14-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://djangoproject.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Roadmap](#roadmap)
- [Team](#team)

---

## About

HireFlow is an AI-powered job search and career development platform built specifically for the Arab world. It aggregates job listings from multiple sources across 12+ Arab countries, provides AI-powered career tools, and helps job seekers land their dream jobs faster.

---

## Features

### Authentication & Security
- JWT-based authentication (register, login, refresh)
- Email & Phone OTP verification
- Profile verification with badge system
- Rate limiting & brute force protection
- End-to-end encrypted chat

### User Profiles
- Complete profile builder
- Verification badges (🔵 Blue / 🌸 Pink / 👑 Gold)
- Profile completion tracker
- Skills, experience, education management
- Cannot apply to jobs without verified profile

### Jobs
- Live job aggregation from 4 sources (JSearch, Adzuna, Remotive, The Muse)
- 12+ Arab countries supported
- Smart filtering by level (Student → Executive)
- Job type filtering (Full-time, Part-time, Remote, Internship, Freelance)
- Save & bookmark jobs with notes
- Job alerts with frequency settings (instant, daily, weekly)
- Job match score based on user profile

### AI Features
- Resume ATS analyzer with score & suggestions
- AI cover letter generator
- Salary estimator for Arab countries
- Interview coach with Q&A
- HireBot AI agent (multi-tool conversational AI)
- Career roadmap generator

### Communication
- End-to-end encrypted messaging
- WebRTC voice & video calls
- Django Channels WebSocket support
- Push notifications (FCM)

### Plans & Monetization
- Free plan (5 AI uses/day, 10 saved jobs, 2 alerts)
- Pro plan (unlimited everything)
- Referral system (3 referrals = Pro upgrade)
- Plan usage tracking

### Notifications
- Email OTP via Gmail SMTP
- SMS OTP via Africa's Talking
- Push notifications via FCM

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.14 |
| Framework | Django 6.0 + Django REST Framework |
| Database | PostgreSQL 18 |
| Real-time | Django Channels + Daphne |
| AI | Google Gemini 2.0 Flash + Groq (Llama 3) |
| Auth | JWT (SimpleJWT) |
| SMS | Africa's Talking |
| Email | Gmail SMTP |
| Jobs | JSearch + Adzuna + Remotive + The Muse |
| Deployment | Render.com |

---

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/eyadstein/Hireflow-land-a-job-.git
cd Hireflow-land-a-job-/hireflow-backend
```

**2. Create virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Create `.env` file:**
```bash
cp .env.example .env
# Fill in your values (see Environment Variables section)
```

**5. Create PostgreSQL database:**
```bash
psql -U postgres -c "CREATE DATABASE hireflow;"
```

**6. Run migrations:**
```bash
python manage.py migrate
```

**7. Create superuser:**
```bash
python manage.py createsuperuser
```

**8. Run the server:**
```bash
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

---

## API Endpoints

### Authentication
```
POST   /api/users/register/     Register new user
POST   /api/users/login/        Login (get JWT tokens)
POST   /api/users/refresh/      Refresh JWT token
GET    /api/users/profile/      Get current user profile
PATCH  /api/users/profile/      Update profile
GET    /api/users/all/          List all users
```

### OTP Verification
```
POST   /api/otp/send/email/     Send email OTP
POST   /api/otp/send/phone/     Send phone OTP
POST   /api/otp/verify/email/   Verify email OTP
POST   /api/otp/verify/phone/   Verify phone OTP
GET    /api/otp/status/         Check verification status
```

### Profile Verification & Badges
```
GET    /api/verification/completion/   Profile completion %
POST   /api/verification/verify/       Trigger verification
GET    /api/verification/badges/       Badge info
GET    /api/verification/can-apply/    Check if can apply
```

### Jobs
```
GET    /api/jobs/                      List internal jobs
POST   /api/jobs/                      Post a job (recruiter)
GET    /api/jobs/<id>/                 Job details
POST   /api/jobs/saved/toggle/         Save/unsave job
GET    /api/jobs/saved/                List saved jobs
GET    /api/jobs/saved/stats/          Saved jobs stats
GET    /api/jobs/saved/check/<id>/     Check if saved
PATCH  /api/jobs/saved/notes/<id>/     Update job notes
POST   /api/jobs/alerts/               Create job alert
GET    /api/jobs/alerts/               List my alerts
PATCH  /api/jobs/alerts/<id>/          Update alert
DELETE /api/jobs/alerts/<id>/          Delete alert
POST   /api/jobs/alerts/<id>/toggle/   Activate/deactivate
POST   /api/jobs/alerts/check/         Check for new matches
GET    /api/jobs/alerts/matches/       Get unseen matches
```

### Live Job Aggregator
```
GET    /api/jobs-live/search/      Search jobs from all sources
GET    /api/jobs-live/countries/   List Arab countries + filters
GET    /api/jobs-live/stats/       Job counts by level
GET    /api/jobs-live/match/       Jobs ranked by match score
```

Query params for search:
```
?q=flutter developer    Search query
&country=egypt          Country (egypt, uae, saudi, qatar...)
&level=junior           Level (student, graduate, junior, mid, senior, executive)
&job_type=full_time     Type (full_time, part_time, internship, remote, freelance)
&salary_min=1000        Minimum salary (USD)
&salary_max=5000        Maximum salary (USD)
&remote_only=true       Remote jobs only
&page=1                 Page number
```

### Applications
```
POST   /api/applications/apply/         Apply to a job
GET    /api/applications/mine/          My applications
GET    /api/applications/job/<id>/      Applications for a job
PATCH  /api/applications/<id>/status/   Update status (recruiter)
```

### AI Features
```
POST   /api/ai/resume/          Analyze resume (ATS score)
POST   /api/ai/cover-letter/    Generate cover letter
POST   /api/ai/salary/          Estimate salary
POST   /api/ai/interview/       Generate interview questions
POST   /api/ai/agent/           HireBot AI agent (chat)
```

### Chat
```
GET    /api/chat/<user_id>/     Get messages with user
POST   /api/chat/<user_id>/     Send message
POST   /api/chat/signal/<id>/   WebRTC signal
GET    /api/chat/signal/<id>/   Get signals
DELETE /api/chat/signal/<id>/   Clear signals
POST   /api/chat/invite/<id>/   Send call invite
GET    /api/chat/invite/<id>/   Get incoming call
DELETE /api/chat/invite/<id>/   Decline call
```

### Plans
```
GET    /api/plans/status/                    Current plan status
GET    /api/plans/compare/                   Free vs Pro comparison
POST   /api/plans/upgrade/                   Request upgrade
POST   /api/plans/upgrade/<id>/approve/      Admin approve upgrade
```

### Referrals
```
GET    /api/referrals/my-code/      Get my referral code
GET    /api/referrals/stats/        Referral stats
GET    /api/referrals/my-referrals/ List my referrals
POST   /api/referrals/validate/     Validate a code
POST   /api/referrals/apply/        Apply a referral code
```

---

## Environment Variables

Create a `.env` file in the backend root:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DB_NAME=hireflow
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# AI
GEMINI_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key

# Job APIs
JSEARCH_KEY=your-jsearch-rapidapi-key
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key

# Email
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password

# SMS
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your-africastalking-key
```

---

## Project Structure

```
hireflow-backend/
├── hireflow/               ← Project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── users/                  ← Auth & user profiles
├── jobs/                   ← Job listings, saved jobs, alerts
├── jobs_aggregator/        ← Live job aggregation (4 APIs)
├── applications/           ← Job applications
├── chat/                   ← Messaging & WebRTC
├── ai_features/            ← AI tools & HireBot agent
├── verification/           ← Profile verification & badges
├── otp/                    ← Email & phone OTP
├── plans/                  ← Free vs Pro plan logic
├── referrals/              ← Referral system
├── Procfile                ← Render deployment
├── build.sh                ← Build script
├── requirements.txt        ← Dependencies
└── manage.py
```

---

## Roadmap

- [x] JWT Authentication
- [x] User Profiles
- [x] Job Aggregation (4 sources, 12 countries)
- [x] AI Features (Resume, Cover Letter, Salary, Interview)
- [x] HireBot AI Agent
- [x] E2E Encrypted Chat
- [x] WebRTC Voice & Video Calls
- [x] Push Notifications (FCM)
- [x] Save Jobs & Bookmarks
- [x] Job Alerts System
- [x] Job Match Score
- [x] Company Reviews
- [x] Referral System
- [x] Free vs Pro Plans
- [x] Profile Verification & Badges
- [x] Email & Phone OTP
- [ ] Swipe to Apply
- [ ] Quick Apply with AI
- [ ] Docker + CI/CD
- [ ] Cybersecurity Hardening
- [ ] AI Career Intelligence
- [ ] Deploy to Render

---

## Team

| Name | Role |
|------|------|
| **Eyad Ahmed** | Backend Lead & Security |
| **Mohanad** | AI Features & Frontend |
| **Jana Abdelfattah** | Frontend & UI |
| **Jana Farouk** | Job Data & Search |
| **Omar** | Recruiter Portal |

---

## License

This project is licensed under the MIT License.

---

<p align="center">Built with ❤️ for the Arab world 🌍</p>
