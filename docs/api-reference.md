# API Reference

All API endpoints are served under `/api/`.
Most endpoints require JWT authorization using the header:

```
Authorization: Bearer <access_token>
```

---

## Authentication

- `POST /api/users/register/` — register a new user.
- `POST /api/users/login/` — obtain JWT access and refresh tokens.
- `POST /api/users/refresh/` — refresh access token.
- `GET /api/users/profile/` — retrieve the authenticated user profile.
- `PATCH /api/users/profile/` — update the authenticated user profile.
- `GET /api/users/all/` — list all users.

## Jobs

- `GET /api/jobs/` — list internal job postings.
- `POST /api/jobs/` — create a new job posting (recruiter use case).
- `GET /api/jobs/<int:pk>/` — retrieve details for a job posting.

## Applications

- `POST /api/applications/apply/` — submit a job application.
- `GET /api/applications/mine/` — retrieve applications from the current user.
- `GET /api/applications/job/<int:job_id>/` — retrieve applications for a specific job.
- `PATCH /api/applications/<int:pk>/status/` — update the status of an existing application.

## Chat

- `GET /api/chat/<int:user_id>/` — retrieve messages for a conversation with the specified user.

## AI Features

- `POST /api/ai/resume-analyzer/` — analyze a resume and return ATS-related insights.
- `POST /api/ai/cover-letter/` — generate a cover letter.
- `POST /api/ai/salary-estimator/` — estimate salary ranges.
- `POST /api/ai/interview-coach/` — provide interview coaching and question suggestions.
- `POST /api/ai/chat/` — converse with the AI agent.
- `GET /api/ai/career-roadmap/` — list generated career roadmaps.
- `GET /api/ai/career-roadmap/<int:pk>/` — retrieve a saved career roadmap.
- `POST /api/ai/cv/` or `POST /api/ai/cv/build/` — build a CV.
- `GET /api/ai/cv/<int:pk>/download/` — download a generated CV.
- `POST /api/ai/mock-interview/start/` — start a mock interview session.
- `POST /api/ai/mock-interview/submit/` — submit mock interview answers.
- `GET /api/ai/mock-interview/history/` — retrieve mock interview history.
- `GET /api/ai/mock-interview/<int:pk>/` — retrieve a specific mock interview.
- `POST /api/ai/linkedin/` or `POST /api/ai/linkedin/optimize/` — optimize LinkedIn profile content.
- `GET /api/ai/linkedin/<int:pk>/` — retrieve a saved LinkedIn optimization result.

## Job Aggregator

- `GET /api/jobs-aggregator/search/` — search aggregated job listings.
- `GET /api/jobs-aggregator/countries/` — list supported countries.
- `GET /api/jobs-aggregator/stats/` — retrieve job level statistics.
- `GET /api/jobs-aggregator/match/` — get job match results for a profile.
