# HireFlow — Complete LLM Handoff Document

> **Purpose**: This document gives any LLM a full picture of the project — every app, model, endpoint, page, known issue, and what to do next. Read this before touching any file.

---

## 1. PROJECT OVERVIEW

HireFlow is a full-stack job platform built with **Django 6 (backend) + React 19 (frontend)**.
It serves two user roles:
- **Job Seekers** — apply to jobs, track applications, use AI career tools
- **Recruiters** — post jobs, manage candidates, see analytics, make bulk decisions

The frontend is **compiled and served by Django** — there is no separate frontend server.
One command starts everything: `.\start.ps1` (or `.\start.bat`) → opens at `http://localhost:8000`.

---

## 2. HOW TO RUN

```powershell
# First time only — install Python packages into venv:
.\venv\Scripts\pip.exe install -r requirements.txt
.\venv\Scripts\pip.exe install scikit-learn pdfplumber

# Every time — builds frontend, applies migrations, starts server:
.\start.ps1
```

Then open `http://localhost:8000`.

**DO NOT** use `npm run dev` separately unless debugging frontend only. The project is set up to run as a single server.

---

## 3. DIRECTORY STRUCTURE

```
Hireflow-land-a-job-/
│
├── hireflow/                   ← Django project config
│   ├── settings.py             ← All config: DB, JWT, API keys, installed apps
│   ├── urls.py                 ← Main URL router (API + catch-all → React SPA)
│   ├── asgi.py                 ← ASGI entry (Channels/WebSockets)
│   └── wsgi.py
│
├── users/                      ← Auth, profiles, roles
├── jobs/                       ← Job posts + full recruiter analytics (1057-line views.py)
├── applications/               ← Applications, candidate insights, bulk decisions
├── chat/                       ← Encrypted messaging + WebSocket consumers
├── ai_features/                ← All AI career tools (resume, CV, salary, interview, etc.)
├── jobs_aggregator/            ← External job search (JSearch + Adzuna APIs)
├── candidate_matching/         ← ML-based job↔candidate matching (sklearn TF-IDF)
├── candidate_crm/              ← Full CRM (pipelines, interactions, tasks, docs, emails)
│
├── src/                        ← React frontend
│   ├── App.jsx                 ← All routes defined here
│   ├── api/client.js           ← Every API call the frontend makes (8 export groups)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppSidebar.jsx  ← Collapsible sidebar (13 jobseeker + 10 recruiter items)
│   │   │   └── AppLayout.jsx   ← Auth guard + role-based redirect
│   │   ├── ui/                 ← 60+ shadcn/Radix UI components (DO NOT EDIT)
│   │   └── shared/             ← Reusable: PageHeader, EmptyState
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Jobs.jsx
│   │   ├── Applications.jsx
│   │   ├── Tracker.jsx         ← Kanban board
│   │   ├── ResumeAI.jsx
│   │   ├── SkillGap.jsx
│   │   ├── ATSCheck.jsx
│   │   ├── CoverLetter.jsx
│   │   ├── Interview.jsx
│   │   ├── Salary.jsx
│   │   ├── CareerRoadmap.jsx
│   │   ├── Chatbot.jsx
│   │   ├── Profile.jsx
│   │   ├── Recruiter.jsx       ← Recruiter dashboard (main landing)
│   │   └── recruiter/          ← 8 recruiter sub-pages (all built, all wired)
│   │       ├── Analytics.jsx
│   │       ├── Performance.jsx
│   │       ├── Candidates.jsx
│   │       ├── CandidateProfile.jsx
│   │       ├── Compare.jsx
│   │       ├── Optimize.jsx
│   │       ├── Alerts.jsx
│   │       └── Decisions.jsx
│   └── lib/
│       ├── ai.js               ← Client-side AI helpers
│       ├── atsEngine.js        ← ATS scoring logic
│       ├── jobProcessor.js
│       ├── jobRecommender.js
│       └── query-client.js     ← TanStack React Query setup
│
├── dist/                       ← Built React app (auto-generated, do not edit)
├── db.sqlite3                  ← Local dev database (do not commit)
├── requirements.txt            ← Python dependencies (67 packages)
├── package.json
├── vite.config.js              ← base: '/static/', proxies /api → :8000
├── start.ps1                   ← THE startup script (build + migrate + serve)
├── start.bat                   ← Same as above but .bat format
└── .env.local                  ← API keys (see section 10)
```

---

## 4. DJANGO APPS — MODELS & ENDPOINTS

### 4.1 `users` — Auth & Profiles

**Model: `User` (extends AbstractUser)**
| Field | Type | Notes |
|---|---|---|
| email | CharField | login identifier |
| role | CharField | `jobseeker` / `recruiter` |
| plan | CharField | `free` / `pro` |
| bio | TextField | |
| skills | TextField | comma-separated |
| experience_level | CharField | |
| desired_roles | TextField | |
| preferred_countries | TextField | |
| prefers_remote | BooleanField | default False |
| city, country | CharField | country default 'Egypt' |
| linkedin, portfolio | URLField | |
| public_key | TextField | for E2E encryption (not implemented) |
| fcm_token | TextField | for push notifications (not implemented) |

**Endpoints** (`/api/users/`):
```
POST   /register/    ← returns access + refresh tokens
POST   /login/       ← returns access + refresh tokens
POST   /refresh/     ← returns new access token
GET    /profile/     ← current user's profile
PATCH  /profile/     ← update profile fields
GET    /all/         ← list all users (admin use)
```

---

### 4.2 `jobs` — Job Posts + Recruiter Analytics

**Model: `Job`**
| Field | Type | Notes |
|---|---|---|
| title, company, location | CharField | |
| job_type | CharField | full_time/part_time/contract/internship/remote/on_site/hybrid |
| department | CharField | engineering/design/marketing/sales/operations/hr/finance/product |
| description | TextField | |
| salary_min, salary_max | PositiveIntegerField | nullable |
| url | URLField | |
| posted_by | FK → User | recruiter who created it |
| career_level | CharField | Entry Level/Mid Level/Senior/Lead/Manager |
| category | CharField | |
| requirements | TextField | ← name clashes with candidate_matching.JobRequirement reverse accessor (fixed with `related_name='matching_requirement'`) |
| years_experience | CharField | |
| education | CharField | |
| source | CharField | recruiter/seed/scraped |
| is_filled, filled_at | Boolean, DateTime | |

**Endpoints** (`/api/jobs/`, 22 total):
```
GET/POST   /                           ← list / create jobs
GET/PUT/DELETE  /<id>/                 ← job detail
GET        /my-jobs/                   ← recruiter's own jobs
GET        /dashboard/                 ← recruiter dashboard stats
GET        /analytics/trends/          ← 30-day application trends
GET        /analytics/job-type-distribution/
GET        /analytics/top-jobs/
GET        /analytics/status-breakdown/
GET        /analytics/hiring-velocity/
GET        /performance/summary/
GET        /performance/activity-log/
GET        /performance/decision-patterns/
GET        /performance/busiest-periods/
GET        /performance/response-times/
GET        /<job_id>/ranked-candidates/
GET        /star-candidates/
GET        /<job_id>/optimize/
GET        /optimization-report/
GET        /alerts/
```

---

### 4.3 `applications` — Applications & Candidate Insights

**Models:**
- `Application`: job(FK nullable), applicant(FK), job_title, company, status(pending/accepted/rejected/applied/screening/interview/offer/withdrawn), applied_date, notes, contact_name/email, reviewed_at
- `CandidateNote`: candidate(FK User), recruiter(FK User), content, timestamps

**Endpoints** (`/api/applications/`, 13 total):
```
POST   /apply/                              ← submit application
GET    /mine/                               ← user's own applications
GET    /job/<job_id>/                       ← all apps for a job
PATCH  /<pk>/status/                        ← update status
GET    /candidate/<user_id>/profile/        ← candidate stats for recruiter
GET    /candidate/<user_id>/timeline/       ← candidate's application history
GET    /candidate/<user_id>/notes/          ← recruiter notes on candidate
POST   /candidate/<user_id>/notes/         ← add note
PUT    /notes/<note_id>/                    ← edit note
DELETE /notes/<note_id>/                    ← delete note
POST   /compare/                            ← side-by-side candidate comparison
POST   /bulk-decision/                      ← bulk accept/reject {application_ids, decision}
POST   /job/<job_id>/reject-all-pending/    ← reject everyone pending
POST   /job/<job_id>/accept-top/            ← accept top N candidates
```

---

### 4.4 `chat` — Messaging

**Model: `Message`**: sender(FK), recipient(FK), encrypted_text(TextField), timestamp

> ⚠️ **Issue**: `encrypted_text` is just a TextField — no actual encryption is implemented despite the field name. The public_key on User model is also unused.

**Endpoints** (`/api/chat/`):
```
GET/POST  /<user_id>/   ← list or send messages with a specific user
```
WebSocket routing configured in `chat/routing.py` via Django Channels but not verified working.

---

### 4.5 `ai_features` — All AI Career Tools

**Models**: CareerRoadmap, CVProfile, MockInterviewSession, MockInterviewAnswer, LinkedInOptimization

**Endpoints** (`/api/ai/`, 20 total):
```
POST  /resume-analyzer/       ← analyze resume text
POST  /skill-gap/             ← identify skill gaps vs target role
POST  /cover-letter/          ← generate cover letter
POST  /salary-estimator/      ← estimate salary range
POST  /interview-coach/       ← interview coaching
POST  /chat/                  ← AI assistant chat
GET/POST  /career-roadmap/    ← create or list roadmaps
GET   /career-roadmap/<pk>/
POST  /cv/build/              ← build/enhance CV
GET   /cv/                    ← list CVs
GET   /cv/<pk>/download/
POST  /mock-interview/start/  ← start mock interview session
POST  /mock-interview/submit/ ← submit answers
GET   /mock-interview/history/
GET   /mock-interview/<pk>/
POST/GET  /linkedin/          ← LinkedIn profile optimization
GET   /linkedin/<pk>/
POST  /extract-text/          ← OCR / text extraction from PDF (uses pdfplumber)
```

**AI providers used**: Groq (GROQ_API_KEY), Google Gemini (GEMINI_KEY)

---

### 4.6 `jobs_aggregator` — External Job Search

Pulls live jobs from JSearch + Adzuna external APIs. Requires JSEARCH_KEY, ADZUNA_APP_ID, ADZUNA_APP_KEY in `.env.local`.

**Model**: `JobSeekerProfile` (mirrors user profile fields for matching)

**Endpoints** (`/api/jobs-aggregator/`):
```
GET  /search/?<params>    ← search external jobs
GET  /countries/          ← available countries
GET  /stats/?<params>     ← job market statistics
GET  /match/?<params>     ← match jobs to user profile
```

---

### 4.7 `candidate_matching` — ML Job↔Candidate Matching

Uses **scikit-learn TF-IDF + cosine similarity** for matching candidates to jobs.

**Models**: CandidateProfile, JobRequirement (O2O with Job, `related_name='matching_requirement'`), CandidateMatch, MatchingAlgorithm, MatchHistory

**Endpoints** (`/api/candidate-matching/`, DRF ViewSet pattern):
```
GET/POST   /profiles/
GET/POST   /requirements/
POST       /requirements/<id>/trigger_matching/
GET/POST   /matches/
GET        /matches/top_matches/
POST       /matches/<id>/shortlist/
GET/POST   /algorithms/
GET        /history/
```

---

### 4.8 `candidate_crm` — Full CRM

10 models: CandidateProfile, CandidateInteraction, CandidateTask, CandidateDocument, CandidatePipeline, CandidatePipelineStage, CandidateTag, CandidateEmail, CandidateActivity, CandidateRelationship

**Endpoints** (`/api/candidate-crm/`, DRF ViewSet pattern):
```
/profiles/         /interactions/     /tasks/        /documents/
/pipelines/        /pipeline-stages/  /tags/         /emails/
/activities/       /relationships/    /search/       /analytics/
```

---

## 5. REACT FRONTEND

### 5.1 Routes (App.jsx)

```jsx
/login                          → Login
/                               → Dashboard
/jobs                           → Job board (both roles)
/applications                   → Application list
/tracker                        → Kanban tracker
/resume-ai                      → Resume analyzer
/skill-gap                      → Skill gap analysis
/ats-check                      → ATS score checker
/cover-letter                   → Cover letter generator
/interview                      → Interview prep
/salary                         → Salary estimator
/career-roadmap                 → Career roadmap
/chatbot                        → AI chat assistant
/profile                        → User profile
/recruiter                      → Recruiter dashboard
/recruiter/analytics            → Hiring trends & insights
/recruiter/performance          → Recruiter performance metrics
/recruiter/candidates           → Top & star candidates
/recruiter/candidates/:userId   → Individual candidate profile
/recruiter/compare              → Side-by-side comparison
/recruiter/optimize             → Job health scores
/recruiter/alerts               → Risk & behavior alerts
/recruiter/decisions            → Bulk accept/reject
```

**Role guards** in `AppLayout.jsx`:
- Recruiter visiting `/resume-ai`, `/skill-gap`, `/ats-check` etc. → redirected to `/recruiter`
- Job seeker visiting `/recruiter*` → redirected to `/`

### 5.2 API Client (src/api/client.js)

Eight export groups:
```javascript
export const auth             // login, register, me, updateProfile, logout, isLoggedIn
export const jobs             // list, create, update, delete
export const applications     // list, create, update, delete
export const ai               // analyzeResume, skillGap, coverLetter, salary, interview,
                              // chat, careerRoadmap, getCareerRoadmaps, buildCV, getCVs,
                              // mockInterviewStart/Submit/History, linkedinOptimize, getLinkedinHistory
export const recruiter        // dashboard, myJobs, trends, jobTypeDistribution, topJobs,
                              // statusBreakdown, hiringVelocity, performanceSummary, activityLog,
                              // decisionPatterns, busiestPeriods, responseTimes,
                              // rankedCandidates, starCandidates,
                              // candidateProfile, candidateTimeline, candidateNotes, addNote,
                              // updateNote, deleteNote, compareCandidates,
                              // jobOptimize, optimizationReport, alerts,
                              // jobApplications, bulkDecision, rejectAllPending, acceptTop
export const jobsLive         // search, countries, stats, match
export const candidateMatching // profiles, createProfile, updateProfile, requirements,
                              // createRequirement, triggerMatching, matches, topMatches,
                              // shortlistCandidate, history
export const candidateCRM     // profiles, createProfile, updateStatus, pipelines, createPipeline,
                              // pipelineStages, interactions, createInteraction, tasks, createTask,
                              // search, analytics
```

All calls go through a shared `request()` function that:
- Attaches `Authorization: Bearer <token>` from localStorage
- Auto-refreshes the token on 401 and retries once
- Redirects to `/login` if refresh fails
- Handles 204 No Content responses

### 5.3 Authentication Flow

1. `POST /api/users/login/` → returns `{access, refresh}`
2. Stored in `localStorage` as `access_token`, `refresh_token`, `role`
3. `AppLayout.jsx` checks `localStorage.access_token` on every route change
4. `client.js` attaches token to every request header

---

## 6. CONFIGURATION FILES

### hireflow/settings.py (key values)
```python
DEBUG = True                     # ← CHANGE TO FALSE FOR PRODUCTION
SECRET_KEY = 'django-insecure-...'  # ← CHANGE BEFORE DEPLOYING
ALLOWED_HOSTS = ['*']            # ← RESTRICT IN PRODUCTION
CORS_ALLOW_ALL_ORIGINS = True    # ← RESTRICT IN PRODUCTION
AUTH_USER_MODEL = 'users.User'
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'dist']  # ← Vite build output
TEMPLATES[0]['DIRS'] = [BASE_DIR / 'dist']  # ← Serves index.html

# Database: SQLite locally, PostgreSQL if DB_NAME env var is set
# JWT: access=1 day, refresh=7 days
# Channels: in-memory layer (not suitable for multi-process production)
```

### hireflow/urls.py
```python
urlpatterns = [
    /admin/
    /api/users/          → users.urls
    /api/jobs/           → jobs.urls
    /api/applications/   → applications.urls
    /api/chat/           → chat.urls
    /api/ai/             → ai_features.urls
    /api/jobs-aggregator/ → jobs_aggregator.urls
    /api/candidate-matching/ → candidate_matching.urls
    /api/candidate-crm/  → candidate_crm.urls
    re_path(r'^.*$')     → TemplateView(index.html)  ← React SPA catch-all
]
```

### vite.config.js
```javascript
base: '/static/'          // ← assets referenced as /static/assets/...
build.outDir: 'dist'
server.proxy['/api']: 'http://127.0.0.1:8000'  // dev mode only
```

### .env.local (required keys)
```
GROQ_API_KEY=...          ← present (AI chat, interview, salary features)
GEMINI_KEY=...            ← MISSING — needed for resume analyzer, CV builder
JSEARCH_KEY=...           ← MISSING — needed for external job search
ADZUNA_APP_ID=...         ← MISSING — needed for external job search
ADZUNA_APP_KEY=...        ← MISSING — needed for external job search
```

---

## 7. GIT BRANCH STRUCTURE

**Current branch**: `integration/recruiter`

**Local branches**:
```
main
integration/frontend-backend
integration/recruiter                    ← working branch (most complete)
feature/frontend-hiring-intelligence-insights
feature/frontend-recruiter-performance-analytics
feature/frontend-candidate-insight-panel
feature/frontend-top-candidate-identification
feature/frontend-candidate-comparison-tool
feature/frontend-job-performance-optimization
feature/frontend-risk-behavior-alerts
feature/frontend-one-click-decision-actions
```

**Important remote branches on GitHub**:
```
origin/main                              ← Django-only backend (no frontend)
origin/integration/frontend-backend     ← Frontend base merged with backend
origin/integration/recruiter            ← MOST COMPLETE — all features merged here
origin/feature/candidate_matching       ← Source of candidate_crm + candidate_matching apps
origin/feature/hiring-intelligence-insights  ← Backend for analytics
origin/feature/recruiter-performance-analytics
origin/feature/candidate-insight-panel
origin/feature/top-candidate-identification
origin/feature/candidate-comparison-tool
origin/feature/job-performance-optimization
origin/feature/risk-behavior-alerts
origin/feature/one-click-decision-actions
```

**What was merged into `integration/recruiter`** (in order):
1. `feature/recruiter-performance-analytics` (backend)
2. `feature/candidate-insight-panel` (backend)
3. `feature/top-candidate-identification` (backend)
4. `feature/candidate-comparison-tool` (backend)
5. `feature/job-performance-optimization` (backend)
6. `feature/risk-behavior-alerts` (backend)
7. `feature/one-click-decision-actions` (backend)
8. `integration/frontend-backend` (frontend base)
9. `feature/frontend-hiring-intelligence-insights` (Analytics.jsx partial merge)
10. All 8 recruiter frontend pages (committed directly after stash resolution)
11. `candidate_matching` apps (cherry-picked — unrelated git history)

---

## 8. KNOWN ISSUES & WHAT NEEDS FIXING

### 🔴 Critical (must fix before production)

| Issue | Location | Fix |
|---|---|---|
| `DEBUG = True` | `hireflow/settings.py:12` | Set to `False`, set `ALLOWED_HOSTS` properly |
| `SECRET_KEY` hardcoded | `hireflow/settings.py:10` | Move to env var |
| `CORS_ALLOW_ALL_ORIGINS = True` | `hireflow/settings.py:105` | Restrict to actual domain |
| GEMINI_KEY missing | `.env.local` | Add key — resume analyzer, CV builder will fail without it |
| JSearch + Adzuna keys missing | `.env.local` | Add keys — `/jobs` page external search will fail |

### 🟡 Medium (should fix)

| Issue | Location | Notes |
|---|---|---|
| No actual encryption in chat | `chat/models.py` — `encrypted_text` field | It's just a plain TextField — implement real E2E encryption or rename field |
| `jobs/views.py` is 1057 lines | `jobs/views.py` | Split into service layer or separate files |
| `candidate_crm/views.py` is 521 lines | `candidate_crm/views.py` | Same — refactor to services |
| Duplicate `CandidateProfile` model | `candidate_matching/models.py` + `candidate_crm/models.py` | Two separate models for candidate profile — should be consolidated or clearly distinguished |
| No rate limiting | All API views | Add `django-ratelimit` or DRF throttling for auth endpoints |
| No transaction boundaries | `applications/views.py` bulk-decision | Wrap bulk DB writes in `transaction.atomic()` |
| `dist/` not in `.gitignore` | `.gitignore` | Built files should not be committed — add `dist/` to gitignore and rebuild on each deploy |
| `db.sqlite3` being committed | `.gitignore` | Should be in gitignore |

### 🟢 Minor / Future

| Issue | Notes |
|---|---|
| No tests | All `tests.py` files are empty stubs — add at minimum auth + job + application tests |
| No API documentation | No Swagger/OpenAPI spec — consider `drf-spectacular` |
| `public_key` + `fcm_token` on User | Added but unused — either implement push notifications + E2E encryption or remove |
| `Messages.jsx` page | Exists but has no route in `App.jsx` — dead file |
| `jobs_aggregator.JobSeekerProfile` | Duplicates fields from `users.User` — consider using User model directly |
| Large JS bundle | ~864KB bundle — consider code splitting with `React.lazy()` and dynamic imports |
| Channels in-memory | `CHANNEL_LAYERS` uses InMemoryChannelLayer — must switch to Redis for production multi-process |

---

## 9. WHAT SHOULD BE DONE NEXT

### Immediate (to make the app fully functional)
1. **Add missing API keys** to `.env.local`:
   ```
   GEMINI_KEY=your_key
   JSEARCH_KEY=your_key
   ADZUNA_APP_ID=your_id
   ADZUNA_APP_KEY=your_key
   ```
2. **Run migrations** (currently 3 unapplied for `applications` + `jobs`):
   ```powershell
   .\venv\Scripts\python.exe manage.py migrate
   ```
3. **Create a superuser** to access Django admin:
   ```powershell
   .\venv\Scripts\python.exe manage.py createsuperuser
   ```
4. **Add `dist/` to `.gitignore`** — built files should not be tracked in git
5. **Test each recruiter page** — verify all 8 pages load data correctly from backend

### Short Term (quality)
6. Add `GEMINI_KEY`, `SECRET_KEY`, `DEBUG` to environment variables instead of hardcoding
7. Write at least basic tests for auth endpoints (`users/tests.py`)
8. Add Swagger docs with `pip install drf-spectacular` and configure in `settings.py`
9. Restrict CORS to actual domain once deployed

### Medium Term (features)
10. **Candidate Matching UI** — `candidateMatching` API exists in `client.js` but no frontend page for it yet — build `src/pages/recruiter/Matching.jsx`
11. **CRM UI** — `candidateCRM` API exists but no frontend page — build `src/pages/recruiter/CRM.jsx`
12. **Chat UI** — `Messages.jsx` exists but has no route in `App.jsx` — add route and wire WebSocket
13. **Real encryption** for chat — implement actual E2E using the `public_key` field on User
14. **Push notifications** using `fcm_token` on User

### What Should Be Deleted / Cleaned Up
- `dist/` from git tracking (add to `.gitignore`)
- `db.sqlite3` from git tracking (add to `.gitignore`)
- `users/migrations/0002_user_bio_...` — this migration was deleted in a recent commit; make sure this is intentional and that the fields still exist in `0001_initial.py`
- `Messages.jsx` — either add a route or delete the file

---

## 10. TECHNOLOGY STACK

| Layer | Technology | Version |
|---|---|---|
| Backend framework | Django | 6.0.4 |
| REST API | Django REST Framework | 3.17.1 |
| WebSockets | Django Channels | 4.3.2 |
| Auth | djangorestframework-simplejwt | 5.5.1 |
| Database (dev) | SQLite | built-in |
| Database (prod) | PostgreSQL | via psycopg2-binary |
| AI (LLM) | Groq API | groq 1.2.0 |
| AI (Google) | Google Generative AI | 0.8.6 |
| ML matching | scikit-learn | 1.8.0 |
| PDF parsing | pdfplumber | 0.11.9 |
| Frontend | React | 19.2.5 |
| Routing | React Router | 7.14.2 |
| Build tool | Vite | 8.0.10 |
| Styling | Tailwind CSS | 3.4.19 |
| Components | Radix UI + shadcn/ui | — |
| Data fetching | TanStack React Query | 5.100.6 |
| Animations | Framer Motion | 12.38.0 |
| Icons | Lucide React | 1.14.0 |

---

## 11. DATA FLOW EXAMPLE (end-to-end)

**Recruiter posts a job and reviews applications:**

```
1. Recruiter logs in → POST /api/users/login/ → JWT stored in localStorage
2. Opens /jobs → GET /api/jobs/my-jobs/ → sees their posted jobs
3. Creates job → POST /api/jobs/ → job saved with posted_by=current_user
4. Opens /recruiter/candidates → GET /api/jobs/star-candidates/ → sees top applicants
5. Clicks candidate → GET /api/applications/candidate/<id>/profile/ + /timeline/ + /notes/
6. Adds note → POST /api/applications/candidate/<id>/notes/
7. Opens /recruiter/decisions → GET /api/jobs/my-jobs/ → selects a job
8. Gets applications → GET /api/applications/job/<job_id>/
9. Bulk rejects → POST /api/applications/bulk-decision/ {application_ids, decision: 'rejected'}
```

**Job seeker uses AI tools:**
```
1. Seeker logs in → role='jobseeker' → sees jobseeker sidebar
2. Opens /resume-ai → pastes resume text → POST /api/ai/resume-analyzer/
3. Backend calls Groq/Gemini → returns structured feedback
4. Opens /skill-gap → POST /api/ai/skill-gap/ {resume, target_role}
5. Opens /ats-check → client-side ATS scoring via src/lib/atsEngine.js (no API call)
6. Opens /cover-letter → POST /api/ai/cover-letter/
7. Applies to job → POST /api/applications/apply/ {job_id}
```

---

## 12. ENVIRONMENT SETUP FOR NEW MACHINE

```powershell
# 1. Clone the repo
git clone <repo-url>
cd Hireflow-land-a-job-

# 2. Create and activate venv
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1

# 3. Install Python dependencies
pip install -r requirements.txt
pip install scikit-learn pdfplumber  # currently missing from requirements.txt

# 4. Install Node dependencies
npm install

# 5. Create .env.local with required keys
# (see section 6 for which keys are needed)

# 6. Start the project
.\start.ps1
```

> **Note**: `scikit-learn` and `pdfplumber` are missing from `requirements.txt` — they need to be added:
> ```
> scikit-learn==1.8.0
> pdfplumber==0.11.9
> ```

---

## 13. PROJECT STATISTICS

- **Python files**: ~99 (views, models, serializers, migrations)
- **React/JS files**: ~90 (pages, components, utilities)
- **Django apps**: 8
- **React pages**: 24 (16 main + 8 recruiter)
- **API endpoints**: 100+
- **Database models**: 30+
- **Frontend components**: 70+ (mostly shadcn/ui)
- **Lines of code**: ~6,000+ backend, ~4,000+ frontend

---

*Last updated: 2026-05-12 | Branch: integration/recruiter | Author: Claude*
