# 🚀 HireFlow - AI-Powered Job Search & Career Development Platform

> An intelligent job discovery and career support platform that combines AI-driven tools with comprehensive job search and application management capabilities.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-green)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-19.2.5-blue)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.0+-purple)](https://vitejs.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 Table of Contents

- [About](#about)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Architecture Overview](#architecture-overview)
- [Modules & Apps](#modules--apps)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

### Current Development Status
- **Core Backend APIs** — In progress (auth, jobs, applications, chat APIs functional)
- **Frontend UI** — In progress (React components being built with Tailwind CSS and Radix UI)
- **AI Features** — In development (CV generator, career assistant agent framework ready)
- **Job Aggregation** — Partially implemented (external job fetching framework in place)
- **Candidate Matching & CRM** — Architecture defined, integration in progress

---

## 📖 About

**HireFlow** is a full-stack, AI-enabled job discovery and career support platform designed to empower job seekers throughout their career journey. The system integrates a robust Django backend with a modern React + Vite frontend to deliver a seamless experience for job search, profile management, application tracking, and AI-powered career coaching.

### For Job Seekers:
- Discover job opportunities from internal postings and aggregated external job boards
- Track applications and manage communication with recruiters
- Access AI-powered tools to improve resumes, generate cover letters, estimate salaries, and prepare for interviews
- Real-time messaging with contacts and recruiters
- Career roadmap generation and LinkedIn profile optimization

### For Recruiters:
- Post internal job openings and manage applications
- Review candidate profiles and applications
- Track application status and communicate with candidates
- Build and manage candidate pools

---

## ✨ Key Features

### 🔍 **Job Search & Discovery**
- Internal job posting system for recruiters
- Multi-source job aggregation from external APIs (JSearch, Adzuna)
- Advanced job filtering and search capabilities
- Job matching algorithm to recommend relevant positions
- Support for multiple countries and job levels

### 💼 **Application Management**
- One-click job application submission
- Application tracking system (ATS) with status management
- Application history and analytics
- Recruiter dashboard for reviewing applications
- Candidate notes and status tracking

### 🤖 **AI-Powered Career Tools**
- **Resume Analyzer**: ATS-score evaluation and optimization suggestions
- **Cover Letter Generator**: AI-generated, personalized cover letters
- **Salary Estimator**: Market-based salary range predictions
- **Interview Coach**: Interview question suggestions and preparation guidance
- **CV Builder**: Generate professional CVs with downloadable exports
- **Mock Interviews**: Practice interview sessions with AI evaluation
- **LinkedIn Optimizer**: Suggestions for optimizing LinkedIn profiles
- **Career Roadmap**: Personalized career development paths
- **AI Chat Agent**: General career guidance and Q&A

### 💬 **Real-Time Communication**
- WebSocket-based messaging system
- Direct messaging with other users and recruiters
- Real-time chat interface

### 👤 **User Management**
- User registration and authentication
- JWT-based secure authentication
- Comprehensive user profiles with skill tracking
- Profile management and updates

---

## 🛠 Technology Stack

### Backend
- **Framework**: Django 6.0 with Django REST Framework
- **Authentication**: JWT (djangorestframework_simplejwt)
- **Real-Time**: Django Channels (WebSocket support)
- **CORS**: django-cors-headers
- **Database**: SQLite (development) / PostgreSQL (production)

### Frontend
- **Framework**: React 19.2.5
- **Build Tool**: Vite 8.0
- **Styling**: Tailwind CSS 3.4 + PostCSS
- **UI Components**: Radix UI
- **State Management**: React Query (TanStack)
- **Routing**: React Router 7
- **Drag & Drop**: @hello-pangea/dnd
- **Markdown**: react-markdown
- **Icons**: Lucide React
- **Animations**: Framer Motion

### AI & ML
- **Google Generative AI**: `google-generativeai` (Gemini models)
- **Groq**: `groq` (fast LLM inference)
- **PDF Processing**: `pdfplumber`
- **Machine Learning**: `scikit-learn`

### External APIs
- **JSearch**: Job aggregation API
- **Adzuna**: Job listings and salary data
- **Google Generative AI**: Advanced AI features
- **Groq API**: Fast inference for real-time features

---

## 📁 Project Structure

```
hireflow-land-a-job-/
├── hireflow/                    # Django project configuration
│   ├── settings.py             # Project settings and middleware
│   ├── urls.py                 # URL routing
│   ├── asgi.py                 # ASGI configuration (Channels)
│   └── wsgi.py                 # WSGI configuration
│
├── users/                       # User management app
│   ├── models.py               # Custom User model
│   ├── serializers.py          # User serializers
│   ├── views.py                # Authentication and profile endpoints
│   ├── urls.py                 # User routes
│   └── migrations/             # Database migrations
│
├── jobs/                        # Job management app
│   ├── models.py               # Job posting model
│   ├── serializers.py          # Job serializers
│   ├── views.py                # Job CRUD endpoints
│   ├── urls.py                 # Job routes
│   └── migrations/             # Database migrations
│
├── applications/               # Application management app
│   ├── models.py               # Application model
│   ├── serializers.py          # Application serializers
│   ├── views.py                # Application endpoints (ATS)
│   ├── urls.py                 # Application routes
│   └── migrations/             # Database migrations
│
├── chat/                        # Real-time messaging app
│   ├── models.py               # Message model
│   ├── consumers.py            # WebSocket consumers (Channels)
│   ├── routing.py              # WebSocket routing
│   ├── serializers.py          # Message serializers
│   ├── views.py                # Chat endpoints
│   ├── urls.py                 # Chat routes
│   └── migrations/             # Database migrations
│
├── jobs_aggregator/            # External job aggregation app
│   ├── models.py               # Aggregated job model
│   ├── services.py             # Job aggregation service
│   ├── filters.py              # Job filtering logic
│   ├── matcher.py              # Job matching algorithm
│   ├── serializers.py          # Aggregated job serializers
│   ├── views.py                # Aggregation endpoints
│   ├── urls.py                 # Aggregator routes
│   └── migrations/             # Database migrations
│
├── ai_features/                # AI-powered tools app
│   ├── models.py               # AI feature models (CareerRoadmap, etc.)
│   ├── agent.py                # AI agent logic
│   ├── cv_generator.py         # CV generation logic
│   ├── serializers.py          # AI feature serializers
│   ├── views.py                # AI endpoints
│   ├── urls.py                 # AI routes
│   └── migrations/             # Database migrations
│
├── candidate_matching/         # Candidate matching app
│   ├── models.py               # Matching models
│   ├── services.py             # Matching algorithms
│   ├── serializers.py          # Matching serializers
│   ├── views.py                # Matching endpoints
│   ├── urls.py                 # Matching routes
│   └── migrations/             # Database migrations
│
├── candidate_crm/              # CRM app for recruiters
│   ├── models.py               # CRM models
│   ├── services.py             # CRM services
│   ├── serializers.py          # CRM serializers
│   ├── views.py                # CRM endpoints
│   ├── urls.py                 # CRM routes
│   └── migrations/             # Database migrations
│
├── src/                         # React frontend
│   ├── App.jsx                 # Main App component
│   ├── main.jsx                # Entry point
│   ├── index.css               # Global styles
│   ├── api/                    # API client utilities
│   │   └── client.js           # Axios/Fetch configuration
│   ├── components/             # React components
│   │   ├── dashboard/          # Dashboard components
│   │   ├── layout/             # Layout components (Header, Sidebar, etc.)
│   │   ├── shared/             # Shared/Reusable components
│   │   └── ui/                 # UI primitives (Button, Input, etc.)
│   ├── pages/                  # Page components
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utility libraries
│   │   ├── ai.js               # AI integration utilities
│   │   ├── atsEngine.js        # ATS scoring logic
│   │   ├── jobProcessor.js     # Job data processing
│   │   ├── jobRecommender.js   # Job recommendation logic
│   │   └── loadJobs.js         # Job loading utilities
│   └── utils/                  # Utility functions
│
├── docs/                        # Documentation
│   ├── api-reference.md        # API endpoint documentation
│   └── architecture.md         # Architecture details
│
├── public/                      # Static assets
│   └── job_descriptions.csv    # Sample job data
│
├── db.sqlite3                  # SQLite database (development)
├── manage.py                   # Django management script
├── package.json                # Node.js dependencies
├── requirements.txt            # Python dependencies
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── postcss.config.js           # PostCSS configuration
├── index.html                  # HTML entry point
├── start.bat                   # Windows batch start script
├── start.ps1                   # PowerShell start script
└── README.md                   # This file
```

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or newer** - [Download](https://python.org/downloads)
- **Node.js 18+ and npm** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)
- **PowerShell 5.1+** (for Windows) or **Bash** (for macOS/Linux)
- **PostgreSQL 14+** (optional, for production database)

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```powershell
git clone <repository-url>
cd "Hireflow-land-a-job-"
```

### Step 2: Create Virtual Environment

```powershell
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Install Frontend Dependencies

```powershell
npm install
```

### Step 5: Create Environment Configuration

Create a `.env.local` file in the root directory and add the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# For PostgreSQL in production:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=hireflow
# DB_USER=postgres
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=5432

# AI & API Keys
GEMINI_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key

# Job Aggregation APIs
JSEARCH_KEY=your-jsearch-api-key
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://localhost:5173
```

### Step 6: Apply Database Migrations

```powershell
python manage.py migrate
```

### Step 7: Create Superuser (Optional)

```powershell
python manage.py createsuperuser
```

---

## 🔑 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key for security | `django-insecure-...` |
| `DEBUG` | Enable debug mode | `True` or `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `localhost,127.0.0.1` |
| `DB_ENGINE` | Database engine | `django.db.backends.postgresql` |
| `DB_NAME` | Database name | `hireflow` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `your-password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `GEMINI_KEY` | Google Generative AI key | Your API key |
| `GROQ_API_KEY` | Groq API key | Your API key |
| `JSEARCH_KEY` | JSearch API key | Your API key |
| `ADZUNA_APP_ID` | Adzuna App ID | Your app ID |
| `ADZUNA_APP_KEY` | Adzuna API key | Your API key |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:8000` |

---

## ▶️ Running the Application

### Option 1: Using PowerShell Start Script (Windows)

```powershell
.\start.ps1
```

This script will:
1. Activate the virtual environment
2. Run Django migrations
3. Build the React frontend with Vite
4. Start the Django development server on `http://localhost:8000`

### Option 2: Using Batch Script (Windows)

```cmd
.\start.bat
```

### Option 3: Manual Setup

**Terminal 1 - Backend Server:**

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start Django development server
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

**Terminal 2 - Frontend Development Server:**

```powershell
# Build or develop with Vite
npm run dev        # Development server with hot reload
# or
npm run build      # Production build
```

The frontend will be available at `http://localhost:5173` (if using Vite dev server)

### Accessing the Application

- **Frontend**: `http://localhost:8000` (served by Django)
- **Admin Panel**: `http://localhost:8000/admin/` (Django admin)
- **API**: `http://localhost:8000/api/`

---

## 🔌 API Endpoints

All API endpoints are prefixed with `/api/` and require JWT authentication (except for registration/login).

### **Authentication Endpoints**
```
POST   /api/users/register/          → Register new user
POST   /api/users/login/             → Get JWT tokens
POST   /api/users/refresh/           → Refresh access token
GET    /api/users/profile/           → Get current user profile
PATCH  /api/users/profile/           → Update user profile
GET    /api/users/all/               → List all users
```

### **Job Management Endpoints**
```
GET    /api/jobs/                    → List internal jobs
POST   /api/jobs/                    → Create new job (recruiter)
GET    /api/jobs/<id>/               → Get job details
```

### **Application Management Endpoints**
```
POST   /api/applications/apply/      → Submit application
GET    /api/applications/mine/       → Get user's applications
GET    /api/applications/job/<id>/   → Get applications for a job
PATCH  /api/applications/<id>/status/  → Update application status
```

### **Chat Endpoints**
```
GET    /api/chat/<user_id>/          → Get conversation messages
POST   /api/chat/<user_id>/          → Send message (WebSocket)
```

### **AI Features Endpoints**
```
POST   /api/ai/resume-analyzer/      → Analyze resume and get ATS score
POST   /api/ai/cover-letter/         → Generate cover letter
POST   /api/ai/salary-estimator/     → Estimate salary range
POST   /api/ai/interview-coach/      → Get interview coaching
POST   /api/ai/chat/                 → Chat with AI agent
GET    /api/ai/career-roadmap/       → List career roadmaps
POST   /api/ai/cv/                   → Build CV
GET    /api/ai/cv/<id>/download/     → Download CV
POST   /api/ai/mock-interview/start/ → Start mock interview
POST   /api/ai/mock-interview/submit/  → Submit interview answers
GET    /api/ai/mock-interview/history/  → Get interview history
POST   /api/ai/linkedin/              → Optimize LinkedIn profile
```

### **Job Aggregation Endpoints**
```
GET    /api/jobs-aggregator/search/  → Search aggregated jobs
GET    /api/jobs-aggregator/countries/  → List supported countries
GET    /api/jobs-aggregator/stats/   → Get job statistics
GET    /api/jobs-aggregator/match/   → Get job recommendations
```

For detailed endpoint documentation, see [API Reference](docs/api-reference.md)

---

## 🏗 Architecture Overview

HireFlow follows a modern, scalable architecture with clear separation of concerns:

### Backend Architecture
- **REST API Server**: Django REST Framework serves all API endpoints
- **Real-Time Server**: Django Channels handles WebSocket connections for messaging
- **Database Layer**: SQLite (dev) / PostgreSQL (prod) with Django ORM
- **Authentication**: JWT-based token authentication
- **AI Integration**: Integration with Google Generative AI (Gemini) and Groq

### Frontend Architecture
- **Single Page Application**: React with client-side routing
- **Component-Based UI**: Modular, reusable components with Radix UI
- **State Management**: React Query for server state, React hooks for local state
- **API Communication**: Axios/Fetch with JWT token handling
- **Build Pipeline**: Vite for fast development and production builds

### Data Flow
1. User authenticates via JWT tokens
2. Frontend sends API requests with Authorization header
3. Backend processes requests, validates JWT tokens
4. Backend communicates with AI services and external APIs
5. Response is returned to frontend
6. Frontend updates UI reactively

For detailed architecture information, see [Architecture Documentation](docs/architecture.md)

---

## 📱 Modules & Apps

### **users**
User management, authentication, and profile functionality.
- Custom User model with profile information
- JWT-based authentication
- User registration, login, and profile management

### **jobs**
Internal job posting management for recruiters.
- Job creation and management
- Job listing and search
- Job detail retrieval

### **applications**
Application tracking system (ATS) for both job seekers and recruiters.
- Application submission
- Application status tracking
- Recruiter application review

### **chat**
Real-time messaging between users using WebSockets.
- Message storage
- WebSocket-based real-time communication
- Conversation history

### **jobs_aggregator**
Aggregates jobs from external sources (JSearch, Adzuna).
- Multi-source job search
- Country-specific filtering
- Job level statistics
- Job matching and recommendations

### **ai_features**
AI-powered career development tools.
- Resume analysis with ATS scoring
- Cover letter generation
- Salary estimation
- Interview coaching
- CV generation
- Mock interviews
- LinkedIn optimization
- Career roadmap generation
- AI chat agent

### **candidate_matching**
Matching algorithms to recommend jobs to candidates.
- Profile-job matching
- Skill-based recommendations
- Location-based filtering

### **candidate_crm**
CRM tools for recruiters to manage candidates.
- Candidate pool management
- Candidate notes and history
- Pipeline management

---

## 🛠 Development

### Code Structure
- **Modular Design**: Each Django app is self-contained with models, serializers, views, and URLs
- **DRY Principle**: Reusable components and utilities
- **Type Hints**: Python type hints for better code clarity
- **Component-Based**: React components follow single responsibility principle

### Running Tests

```powershell
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test ai_features

# Run tests with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Development Workflow

1. **Backend Development**:
   ```powershell
   python manage.py runserver
   ```

2. **Frontend Development**:
   ```powershell
   npm run dev
   ```

3. **Database Migrations**:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **API Testing**:
   - Use Postman, Insomnia, or VS Code REST Client
   - Include `Authorization: Bearer <token>` header

### Database Management

```powershell
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Revert to specific migration
python manage.py migrate [app_label] [migration_name]

# Create superuser
python manage.py createsuperuser

# Shell access
python manage.py shell
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch:
   ```powershell
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and test them thoroughly

3. **Write clear commit messages**:
   ```
   git commit -m "Add feature: brief description of changes"
   ```

4. **Push to your branch**:
   ```powershell
   git push origin feature/your-feature-name
   ```

5. **Submit a Pull Request** with a detailed description

### Code Style Guidelines
- **Python**: Follow PEP 8
- **JavaScript/React**: Use ESLint and Prettier configuration
- **Commit Messages**: Use descriptive, present-tense messages
- **Branch Names**: Use lowercase with hyphens (e.g., `feature/resume-analyzer`)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

For issues, questions, or feature requests:
- Open an issue on the GitHub repository
- Check existing documentation in the `docs/` folder
- Review API reference for endpoint details

---

## 🎯 Roadmap

Planned features and improvements:
- [ ] Mobile application
- [ ] Advanced analytics dashboard
- [ ] Integration with more job boards
- [ ] Video interview support
- [ ] Enhanced AI coaching with personalization
- [ ] Salary negotiation assistant
- [ ] Employer reviews and insights

---

## 🙏 Acknowledgments

- Django and Django REST Framework communities
- React and Vite communities
- Google Generative AI and Groq for AI capabilities
- All contributors and users

---

**Made with ❤️ for job seekers and recruiters worldwide.**

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