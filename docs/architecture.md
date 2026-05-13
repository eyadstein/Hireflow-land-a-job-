# HireFlow Architecture

## Project Description
HireFlow is an AI-enabled job discovery and career support platform designed to help job seekers navigate the application process with confidence. The system integrates a Django backend with a modern React + Vite frontend to deliver a seamless experience for job search, profile management, application tracking, and career coaching.

The backend exposes REST APIs for core functionality including user authentication, internal job postings, applications management, real-time chat, AI-driven career tools, and aggregated job search from external providers. Users can register, build verified profiles, search jobs, apply to positions, communicate with contacts, and access AI-powered features such as resume analysis, cover letter generation, salary estimation, interview coaching, career roadmap creation, CV generation, and LinkedIn optimization.

HireFlow is built to support both job seekers and recruiters. The recruiter-facing features include job creation, application review, and status updates, while the job seeker experience focuses on discovering relevant roles, improving application materials, and preparing for interviews. The combination of job aggregation, secure messaging, and intelligent AI guidance makes this project a comprehensive platform for career growth.

## Overview
HireFlow is a full-stack job search and career development platform implemented with a Django backend and a React + Vite frontend. The backend exposes REST APIs for authentication, jobs, applications, chat, AI features, and job aggregation. AI-powered career tools support resume analysis, cover letter generation, salary estimation, interview coaching, and LinkedIn optimization.

## Repository Layout
- `hireflow/` — Django project settings and routing.
- `users/` — custom user model, authentication, registration, login, profile management, and user listing APIs.
- `jobs/` — internal job postings, creation, and detail retrieval.
- `applications/` — job application submission, user application history, recruiter application views, and status updates.
- `chat/` — messaging API for conversations between users.
- `jobs_aggregator/` — aggregated job search, supported countries, statistics, and match scoring.
- `ai_features/` — AI-driven endpoints for resume evaluation, cover letters, salary estimates, interview coaching, AI chat agent, career roadmaps, CV generation, mock interviews, and LinkedIn optimization.
- `src/` — React frontend source code with UI components, pages, hooks, and utilities.

## Backend Architecture

### Django Configuration
- `hireflow/settings.py` configures installed apps, middleware, database, authentication, CORS, channels, and JWT settings.
- `hireflow/urls.py` routes API prefixes:
  - `/api/users/`
  - `/api/jobs/`
  - `/api/applications/`
  - `/api/chat/`
  - `/api/ai/`
  - `/api/jobs-aggregator/`
- `ASGI_APPLICATION` is set to `hireflow.asgi.application` for channel compatibility.

### Installed Apps
- `rest_framework`
- `rest_framework_simplejwt`
- `corsheaders`
- `channels`
- `users`, `jobs`, `applications`, `chat`, `jobs_aggregator`, `ai_features`

### Authentication
- Custom user model via `AUTH_USER_MODEL = 'users.User'`.
- JWT authentication with `rest_framework_simplejwt.authentication.JWTAuthentication`.
- Default permission class is `rest_framework.permissions.IsAuthenticated`.

### Database
- PostgreSQL is configured through environment variables:
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_HOST`
  - `DB_PORT`
- Default values are `hireflow`, `postgres`, `postgres`, `localhost`, `5432`.

### Real-Time Chat
- Django Channels with `InMemoryChannelLayer` in development.
- Chat endpoint mapping is defined in `chat/urls.py`.

## API Modules

### Users
- `users/urls.py` exposes:
  - `register/`
  - `login/`
  - `refresh/`
  - `profile/`
  - `all/`

### Jobs
- `jobs/urls.py` exposes:
  - `/api/jobs/`
  - `/api/jobs/<int:pk>/`

### Applications
- `applications/urls.py` exposes:
  - `apply/`
  - `mine/`
  - `job/<int:job_id>/`
  - `<int:pk>/status/`

### Chat
- `chat/urls.py` exposes:
  - `<int:user_id>/`

### AI Features
- `ai_features/urls.py` exposes multiple AI endpoints, including:
  - `resume-analyzer/`
  - `cover-letter/`
  - `salary-estimator/`
  - `interview-coach/`
  - `chat/`
  - `career-roadmap/`
  - `cv/`
  - `mock-interview/`
  - `linkedin/`

### Job Aggregator
- `jobs_aggregator/urls.py` exposes:
  - `search/`
  - `countries/`
  - `stats/`
  - `match/`

## Frontend Architecture

### Core Stack
- React application in `src/`.
- Vite for fast development and build tooling.
- Tailwind CSS plus Tailwind Animate for styling.
- React Router for SPA routing.
- React Query for server data fetching and caching.
- Radix UI components and Lucide icons for UI primitives.

### Notable Folders
- `src/components/` — reusable UI components and page-specific widgets.
- `src/pages/` — app pages like `Applications`, `Chatbot`, `CoverLetter`, `Dashboard`, `Jobs`, `Profile`, `ResumeAI`, and more.
- `src/hooks/` — custom hooks for device detection and app behavior.
- `src/lib/` — utility functions, query-client setup, shared logic.
- `src/api/` — client modules for API integration.

## AI Features and Integration
- AI services depend on `GEMINI_KEY` environment variable.
- `ai_features/views.py` and `ai_features/agent.py` handle AI-related request processing.
- AI endpoints support career tools like resume analysis, interview prep, and document generation.

## Deployment & Production Considerations
- Set `DEBUG = False` in production.
- Replace the default insecure `SECRET_KEY`.
- Use a production-ready channels backend instead of `InMemoryChannelLayer`.
- Secure environment variables for database credentials and AI keys.
- Configure allowed origins and hosts before deployment.

## Summary
The project combines a Django REST backend, real-time chat via channels, aggregated job search capabilities, and multiple AI-powered career tools, with a React frontend delivering the user experience.