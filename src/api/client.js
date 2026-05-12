const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('access_token');
}

async function tryRefresh() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_BASE}/users/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('access_token', data.access);
      return true;
    }
  } catch {}
  return false;
}

async function request(method, path, data = null, isRetry = false) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const options = { method, headers };
  if (data !== null) options.body = JSON.stringify(data);

  const res = await fetch(`${API_BASE}${path}`, options);

  if (res.status === 401 && !isRetry) {
    const refreshed = await tryRefresh();
    if (refreshed) return request(method, path, data, true);
    localStorage.clear();
    window.location.href = '/login';
    return null;
  }

  if (res.status === 204) return null;

  const json = await res.json();
  if (!res.ok) throw json;
  return json;
}

export const auth = {
  login: async (email, password) => {
    const data = await request('POST', '/users/login/', { username: email, password });
    if (data?.access) {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
    }
    return data;
  },
  register: async (email, password, role = 'jobseeker') => {
    const data = await request('POST', '/users/register/', { email, password, role });
    if (data?.access) {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
    }
    return data;
  },
  me: () => request('GET', '/users/profile/'),
  updateProfile: (data) => request('PATCH', '/users/profile/', data),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('role');
  },
  isLoggedIn: () => !!localStorage.getItem('access_token'),
};

export const jobs = {
  list: () => request('GET', '/jobs/'),
  create: (data) => request('POST', '/jobs/', data),
  update: (id, data) => request('PUT', `/jobs/${id}/`, data),
  delete: (id) => request('DELETE', `/jobs/${id}/`),
};

export const applications = {
  list: () => request('GET', '/applications/'),
  create: (data) => request('POST', '/applications/', data),
  update: (id, data) => request('PATCH', `/applications/${id}/`, data),
  delete: (id) => request('DELETE', `/applications/${id}/`),
};

export const ai = {
  analyzeResume:   (data) => request('POST', '/ai/resume-analyzer/', data),
  skillGap:        (data) => request('POST', '/ai/skill-gap/', data),
  coverLetter:     (data) => request('POST', '/ai/cover-letter/', data),
  salary:          (data) => request('POST', '/ai/salary-estimator/', data),
  interview:       (data) => request('POST', '/ai/interview-coach/', data),
  chat:            (data) => request('POST', '/ai/chat/', data),
  careerRoadmap:   (data) => request('POST', '/ai/career-roadmap/', data),
  getCareerRoadmaps: ()   => request('GET',  '/ai/career-roadmap/'),
  buildCV:         (data) => request('POST', '/ai/cv/build/', data),
  getCVs:          ()     => request('GET',  '/ai/cv/'),
  mockInterviewStart:  (data) => request('POST', '/ai/mock-interview/start/', data),
  mockInterviewSubmit: (data) => request('POST', '/ai/mock-interview/submit/', data),
  mockInterviewHistory: ()    => request('GET',  '/ai/mock-interview/history/'),
  linkedinOptimize: (data)   => request('POST', '/ai/linkedin/optimize/', data),
  getLinkedinHistory: ()     => request('GET',  '/ai/linkedin/'),
};

export const recruiter = {
  // Dashboard
  dashboard:            ()          => request('GET',  '/jobs/dashboard/'),
  myJobs:               ()          => request('GET',  '/jobs/my-jobs/'),

  // Hiring Intelligence
  trends:               ()          => request('GET',  '/jobs/analytics/trends/'),
  jobTypeDistribution:  ()          => request('GET',  '/jobs/analytics/job-type-distribution/'),
  topJobs:              ()          => request('GET',  '/jobs/analytics/top-jobs/'),
  statusBreakdown:      ()          => request('GET',  '/jobs/analytics/status-breakdown/'),
  hiringVelocity:       ()          => request('GET',  '/jobs/analytics/hiring-velocity/'),

  // Recruiter Performance
  performanceSummary:   ()          => request('GET',  '/jobs/performance/summary/'),
  activityLog:          ()          => request('GET',  '/jobs/performance/activity-log/'),
  decisionPatterns:     ()          => request('GET',  '/jobs/performance/decision-patterns/'),
  busiestPeriods:       ()          => request('GET',  '/jobs/performance/busiest-periods/'),
  responseTimes:        ()          => request('GET',  '/jobs/performance/response-times/'),

  // Top Candidate Identification
  rankedCandidates:     (jobId)     => request('GET',  `/jobs/${jobId}/ranked-candidates/`),
  starCandidates:       ()          => request('GET',  '/jobs/star-candidates/'),

  // Candidate Insight Panel
  candidateProfile:     (uid)       => request('GET',  `/applications/candidate/${uid}/profile/`),
  candidateTimeline:    (uid)       => request('GET',  `/applications/candidate/${uid}/timeline/`),
  candidateNotes:       (uid)       => request('GET',  `/applications/candidate/${uid}/notes/`),
  addNote:              (uid, text) => request('POST', `/applications/candidate/${uid}/notes/`, { content: text }),
  updateNote:           (nid, text) => request('PUT',  `/applications/notes/${nid}/`,           { content: text }),
  deleteNote:           (nid)       => request('DELETE',`/applications/notes/${nid}/`),

  // Candidate Comparison
  compareCandidates:    (ids)       => request('POST', '/applications/compare/',              { candidate_ids: ids }),

  // Job Performance Optimization
  jobOptimize:          (jobId)     => request('GET',  `/jobs/${jobId}/optimize/`),
  optimizationReport:   ()          => request('GET',  '/jobs/optimization-report/'),

  // Risk & Behaviour Alerts
  alerts:               ()          => request('GET',  '/jobs/alerts/'),

  // One-Click Decisions
  jobApplications:      (jobId)     => request('GET',  `/applications/job/${jobId}/`),
  bulkDecision:         (ids, dec)  => request('POST', '/applications/bulk-decision/',         { application_ids: ids, decision: dec }),
  rejectAllPending:     (jobId)     => request('POST', `/applications/job/${jobId}/reject-all-pending/`),
  acceptTop:            (jobId, n)  => request('POST', `/applications/job/${jobId}/accept-top/`, { top_n: n }),
};

export const jobsLive = {
  search:    (params) => request('GET', `/jobs-aggregator/search/?${new URLSearchParams(params)}`),
  countries: ()       => request('GET', '/jobs-aggregator/countries/'),
  stats:     (params) => request('GET', `/jobs-aggregator/stats/?${new URLSearchParams(params)}`),
  match:     (params) => request('GET', `/jobs-aggregator/match/?${new URLSearchParams(params)}`),
};

export const candidateMatching = {
  // Candidate profiles for matching
  profiles:           ()          => request('GET',  '/candidate-matching/profiles/'),
  createProfile:      (data)      => request('POST', '/candidate-matching/profiles/', data),
  updateProfile:      (id, data)  => request('PUT',  `/candidate-matching/profiles/${id}/`, data),

  // Job requirements
  requirements:       ()          => request('GET',  '/candidate-matching/requirements/'),
  createRequirement:  (data)      => request('POST', '/candidate-matching/requirements/', data),
  triggerMatching:    (id)        => request('POST', `/candidate-matching/requirements/${id}/trigger_matching/`),

  // Matches
  matches:            ()          => request('GET',  '/candidate-matching/matches/'),
  topMatches:         ()          => request('GET',  '/candidate-matching/matches/top_matches/'),
  shortlistCandidate: (id)        => request('POST', `/candidate-matching/matches/${id}/shortlist/`),

  // History
  history:            ()          => request('GET',  '/candidate-matching/history/'),
};

export const candidateCRM = {
  // Profiles
  profiles:           ()          => request('GET',  '/candidate-crm/profiles/'),
  createProfile:      (data)      => request('POST', '/candidate-crm/profiles/', data),
  updateStatus:       (id, data)  => request('POST', `/candidate-crm/profiles/${id}/update_status/`, data),

  // Pipelines
  pipelines:          ()          => request('GET',  '/candidate-crm/pipelines/'),
  createPipeline:     (data)      => request('POST', '/candidate-crm/pipelines/', data),
  pipelineStages:     ()          => request('GET',  '/candidate-crm/pipeline-stages/'),

  // Interactions & tasks
  interactions:       (params)    => request('GET',  `/candidate-crm/interactions/?${new URLSearchParams(params || {})}`),
  createInteraction:  (data)      => request('POST', '/candidate-crm/interactions/', data),
  tasks:              ()          => request('GET',  '/candidate-crm/tasks/'),
  createTask:         (data)      => request('POST', '/candidate-crm/tasks/', data),

  // Search & analytics
  search:             (params)    => request('GET',  `/candidate-crm/search/?${new URLSearchParams(params || {})}`),
  analytics:          ()          => request('GET',  '/candidate-crm/analytics/'),
};
