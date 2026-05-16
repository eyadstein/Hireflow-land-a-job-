const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

function getToken() {
  return localStorage.getItem("access_token");
}

function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}

function saveAuthData(data) {
  if (data?.access) {
    localStorage.setItem("access_token", data.access);
  }

  if (data?.refresh) {
    localStorage.setItem("refresh_token", data.refresh);
  }

  if (data?.user) {
    localStorage.setItem("user", JSON.stringify(data.user));
    localStorage.setItem("role", data.user.role || "jobseeker");
  }
}

function clearAuthData() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  localStorage.removeItem("role");
}

function isPublicAuthPath(path) {
  return path === "/users/login/" || path === "/users/register/";
}

function extractErrorMessage(data) {
  if (!data) return "Something went wrong.";
  if (typeof data === "string") return data;

  if (data.detail) return data.detail;
  if (data.error) return data.error;
  if (data.message) return data.message;

  const firstKey = Object.keys(data)[0];

  if (firstKey) {
    const value = data[firstKey];

    if (Array.isArray(value)) {
      return value[0] || "Something went wrong.";
    }

    if (typeof value === "string") {
      return value;
    }

    if (value && typeof value === "object") {
      return extractErrorMessage(value);
    }
  }

  return "Something went wrong.";
}

async function tryRefresh() {
  const refresh = getRefreshToken();

  if (!refresh) return false;

  try {
    const res = await fetch(`${API_BASE}/users/refresh/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh }),
    });

    const data = await res.json().catch(() => null);

    if (res.ok && data?.access) {
      localStorage.setItem("access_token", data.access);
      return true;
    }
  } catch {
    return false;
  }

  return false;
}

async function parseResponse(res) {
  if (res.status === 204) return null;

  const contentType = res.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    return res.json().catch(() => null);
  }

  return res.text().catch(() => null);
}

async function request(method, path, data = null, isRetry = false) {
  const token = getToken();

  const isFormData = data instanceof FormData;

  const headers = isFormData
    ? {}
    : {
        "Content-Type": "application/json",
      };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const options = {
    method,
    headers,
  };

  if (data !== null) {
    options.body = isFormData ? data : JSON.stringify(data);
  }

  const res = await fetch(`${API_BASE}${path}`, options);
  const responseData = await parseResponse(res);

  if (res.status === 401 && !isRetry && !isPublicAuthPath(path)) {
    const refreshed = await tryRefresh();

    if (refreshed) {
      return request(method, path, data, true);
    }

    clearAuthData();
    window.location.href = "/login";
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) {
    const error = new Error(extractErrorMessage(responseData));
    error.status = res.status;
    error.data = responseData;
    throw error;
  }

  return responseData;
}

function buildQuery(params = {}) {
  return new URLSearchParams(params || {}).toString();
}

export const auth = {
  login: async (email, password) => {
    const data = await request("POST", "/users/login/", {
      email,
      username: email,
      password,
    });

    saveAuthData(data);
    return data;
  },

  register: async (email, password, role = "jobseeker") => {
    const data = await request("POST", "/users/register/", {
      email,
      password,
      role,
    });

    saveAuthData(data);
    return data;
  },

  me: () => request("GET", "/users/profile/"),

  updateProfile: (data) => request("PATCH", "/users/profile/", data),

  logout: () => {
    clearAuthData();
    window.location.href = "/login";
  },

  deleteAccount: async () => {
    await request("DELETE", "/users/delete/");
    clearAuthData();
  },

  isLoggedIn: () => !!getToken(),
};

export const jobs = {
  list: () => request("GET", "/jobs/"),
  create: (data) => request("POST", "/jobs/", data),
  update: (id, data) => request("PUT", `/jobs/${id}/`, data),
  delete: (id) => request("DELETE", `/jobs/${id}/`),
};

export const applications = {
  list: () => request("GET", "/applications/"),
  mine: () => request("GET", "/applications/mine/"),
  apply: (data) => request("POST", "/applications/apply/", data),
  create: (data) => request("POST", "/applications/", data),
  update: (id, data) => request("PATCH", `/applications/${id}/`, data),
  updateStatus: (id, data) =>
    request("PATCH", `/applications/${id}/status/`, data),
  delete: (id) => request("DELETE", `/applications/${id}/`),
};

export const recruiter = {
  dashboard: () => request("GET", "/jobs/dashboard/"),
  myJobs: () => request("GET", "/jobs/my-jobs/"),

  trends: () => request("GET", "/jobs/analytics/trends/"),
  jobTypeDistribution: () =>
    request("GET", "/jobs/analytics/job-type-distribution/"),
  topJobs: () => request("GET", "/jobs/analytics/top-jobs/"),
  statusBreakdown: () => request("GET", "/jobs/analytics/status-breakdown/"),
  hiringVelocity: () => request("GET", "/jobs/analytics/hiring-velocity/"),

  performanceSummary: () => request("GET", "/jobs/performance/summary/"),
  activityLog: () => request("GET", "/jobs/performance/activity-log/"),
  decisionPatterns: () =>
    request("GET", "/jobs/performance/decision-patterns/"),
  busiestPeriods: () => request("GET", "/jobs/performance/busiest-periods/"),
  responseTimes: () => request("GET", "/jobs/performance/response-times/"),

  rankedCandidates: (jobId) =>
    request("GET", `/jobs/${jobId}/ranked-candidates/`),
  starCandidates: () => request("GET", "/jobs/star-candidates/"),

  jobApplications: (jobId) =>
    request("GET", `/applications/job/${jobId}/`),

  updateApplicationStatus: (applicationId, status) =>
    request("PATCH", `/applications/${applicationId}/status/`, { status }),

  bulkDecision: (applicationIds, decision) =>
    request("POST", "/applications/bulk-decision/", {
      application_ids: applicationIds,
      decision,
    }),

  rejectAllPending: (jobId) =>
    request("POST", `/applications/job/${jobId}/reject-all-pending/`),

  rejectAllActive: (jobId) =>
    request("POST", `/applications/job/${jobId}/reject-all-active/`),

  acceptTop: (jobId, topN) =>
    request("POST", `/applications/job/${jobId}/accept-top/`, {
      top_n: topN,
    }),

  candidateProfile: (userId) =>
    request("GET", `/applications/candidate/${userId}/profile/`),

  candidateTimeline: (userId) =>
    request("GET", `/applications/candidate/${userId}/timeline/`),

  candidateNotes: (userId) =>
    request("GET", `/applications/candidate/${userId}/notes/`),

  addNote: (userId, text) =>
    request("POST", `/applications/candidate/${userId}/notes/`, {
      content: text,
    }),

  updateNote: (noteId, text) =>
    request("PUT", `/applications/notes/${noteId}/`, {
      content: text,
    }),

  deleteNote: (noteId) => request("DELETE", `/applications/notes/${noteId}/`),

  compareCandidates: (candidateIds) =>
    request("POST", "/applications/compare/", {
      candidate_ids: candidateIds,
    }),

  compareApplications: (applicationIds) =>
    request("POST", "/applications/compare/", {
      application_ids: applicationIds,
    }),

  jobOptimize: (jobId) => request("GET", `/jobs/${jobId}/optimize/`),
  optimizationReport: () => request("GET", "/jobs/optimization-report/"),
  alerts: () => request("GET", "/jobs/alerts/"),
};

export const ai = {
  analyzeResume: (data) => request("POST", "/ai/resume-analyzer/", data),
  skillGap: (data) => request("POST", "/ai/skill-gap/", data),
  coverLetter: (data) => request("POST", "/ai/cover-letter/", data),
  salary: (data) => request("POST", "/ai/salary-estimator/", data),
  interview: (data) => request("POST", "/ai/interview-coach/", data),
  chat: (data) => request("POST", "/ai/chat/", data),
  careerRoadmap: (data) => request("POST", "/ai/career-roadmap/", data),
  getCareerRoadmaps: () => request("GET", "/ai/career-roadmap/"),
  buildCV: (data) => request("POST", "/ai/cv/build/", data),
  getCVs: () => request("GET", "/ai/cv/"),
  mockInterviewStart: (data) =>
    request("POST", "/ai/mock-interview/start/", data),
  mockInterviewSubmit: (data) =>
    request("POST", "/ai/mock-interview/submit/", data),
  mockInterviewHistory: () => request("GET", "/ai/mock-interview/history/"),
  linkedinOptimize: (data) =>
    request("POST", "/ai/linkedin/optimize/", data),
  getLinkedinHistory: () => request("GET", "/ai/linkedin/"),
};

export const jobsLive = {
  search: (params) =>
    request("GET", `/jobs-aggregator/search/?${buildQuery(params)}`),
  countries: () => request("GET", "/jobs-aggregator/countries/"),
  stats: (params) =>
    request("GET", `/jobs-aggregator/stats/?${buildQuery(params)}`),
  match: (params) =>
    request("GET", `/jobs-aggregator/match/?${buildQuery(params)}`),
};

export const chat = {
  listUsers: () => request("GET", "/users/all/"),
  listMessages: (userId) => request("GET", `/chat/${userId}/`),
  sendMessage: (userId, text) =>
    request("POST", `/chat/${userId}/`, {
      encrypted_text: text,
    }),
};

export const candidateMatching = {
  profiles: () => request("GET", "/candidate-matching/profiles/"),
  createProfile: (data) =>
    request("POST", "/candidate-matching/profiles/", data),
  updateProfile: (id, data) =>
    request("PUT", `/candidate-matching/profiles/${id}/`, data),

  requirements: () => request("GET", "/candidate-matching/requirements/"),
  createRequirement: (data) =>
    request("POST", "/candidate-matching/requirements/", data),
  triggerMatching: (id) =>
    request(
      "POST",
      `/candidate-matching/requirements/${id}/trigger_matching/`
    ),

  matches: () => request("GET", "/candidate-matching/matches/"),
  topMatches: () => request("GET", "/candidate-matching/matches/top_matches/"),
  shortlistCandidate: (id) =>
    request("POST", `/candidate-matching/matches/${id}/shortlist/`),

  history: () => request("GET", "/candidate-matching/history/"),
};

export const candidateCRM = {
  profiles: () => request("GET", "/candidate-crm/profiles/"),
  createProfile: (data) => request("POST", "/candidate-crm/profiles/", data),
  updateStatus: (id, data) =>
    request("POST", `/candidate-crm/profiles/${id}/update_status/`, data),

  pipelines: () => request("GET", "/candidate-crm/pipelines/"),
  createPipeline: (data) =>
    request("POST", "/candidate-crm/pipelines/", data),
  pipelineStages: () => request("GET", "/candidate-crm/pipeline-stages/"),

  interactions: (params) =>
    request("GET", `/candidate-crm/interactions/?${buildQuery(params)}`),
  createInteraction: (data) =>
    request("POST", "/candidate-crm/interactions/", data),

  tasks: () => request("GET", "/candidate-crm/tasks/"),
  createTask: (data) => request("POST", "/candidate-crm/tasks/", data),

  search: (params) =>
    request("GET", `/candidate-crm/search/?${buildQuery(params)}`),
  analytics: () => request("GET", "/candidate-crm/analytics/"),
};

export default request;