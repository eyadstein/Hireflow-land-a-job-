import React, { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  Briefcase,
  CheckCircle,
  ChevronRight,
  Clock,
  Loader2,
  Mail,
  Search,
  UserSearch,
  XCircle,
} from "lucide-react";

import { recruiter } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const ACTIVE_STATUSES = ["pending", "applied", "screening", "interview", "offer"];

const statusLabels = {
  pending: "Pending",
  applied: "Applied",
  screening: "Screening",
  interview: "Interview",
  offer: "Offer",
  accepted: "Accepted",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

const statusStyles = {
  pending: "bg-yellow-50 text-yellow-700 border-yellow-200",
  applied: "bg-yellow-50 text-yellow-700 border-yellow-200",
  screening: "bg-blue-50 text-blue-700 border-blue-200",
  interview: "bg-purple-50 text-purple-700 border-purple-200",
  offer: "bg-emerald-50 text-emerald-700 border-emerald-200",
  accepted: "bg-green-50 text-green-700 border-green-200",
  rejected: "bg-red-50 text-red-700 border-red-200",
  withdrawn: "bg-gray-50 text-gray-700 border-gray-200",
};

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function getCandidateName(app) {
  const fullName = `${app.applicant_first_name || ""} ${
    app.applicant_last_name || ""
  }`.trim();

  return (
    fullName ||
    app.applicant_name ||
    app.applicant_email ||
    `Candidate #${app.applicant}`
  );
}

function getJobLabel(job) {
  if (!job) return "";
  return `${job.title || "Untitled Job"} · ${job.company || "Unknown Company"}`;
}

function getApplicationDate(app) {
  const date = app.created_at || app.applied_date;
  if (!date) return "—";

  try {
    return new Date(date).toLocaleString();
  } catch {
    return date;
  }
}

export default function Candidates() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [selectedJobId, setSelectedJobId] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [message, setMessage] = useState("");

  const {
    data: jobsData,
    isLoading: jobsLoading,
    error: jobsError,
  } = useQuery({
    queryKey: ["recruiter-my-jobs"],
    queryFn: recruiter.myJobs,
  });

  const jobs = normalizeList(jobsData);

  const {
    data: applicationsData,
    isLoading: applicationsLoading,
    error: applicationsError,
  } = useQuery({
    queryKey: ["recruiter-job-applications", selectedJobId],
    queryFn: () => recruiter.jobApplications(selectedJobId),
    enabled: !!selectedJobId,
    refetchInterval: 10000,
  });

  const applications = normalizeList(applicationsData);

  const selectedJob = jobs.find(
    (job) => String(job.id) === String(selectedJobId)
  );

  const filteredApplications = useMemo(() => {
    const cleanSearch = search.trim().toLowerCase();

    return applications.filter((app) => {
      const name = getCandidateName(app).toLowerCase();
      const email = (app.applicant_email || "").toLowerCase();

      const matchesSearch =
        !cleanSearch ||
        name.includes(cleanSearch) ||
        email.includes(cleanSearch) ||
        String(app.id).includes(cleanSearch);

      const matchesStatus =
        statusFilter === "all" ||
        app.status === statusFilter ||
        (statusFilter === "active" && ACTIVE_STATUSES.includes(app.status));

      return matchesSearch && matchesStatus;
    });
  }, [applications, search, statusFilter]);

  const counts = useMemo(() => {
    return {
      total: applications.length,
      active: applications.filter((app) => ACTIVE_STATUSES.includes(app.status))
        .length,
      accepted: applications.filter((app) => app.status === "accepted").length,
      rejected: applications.filter((app) => app.status === "rejected").length,
      interview: applications.filter((app) => app.status === "interview").length,
      offer: applications.filter((app) => app.status === "offer").length,
    };
  }, [applications]);

  const invalidateRecruiterData = () => {
    queryClient.invalidateQueries({
      queryKey: ["recruiter-job-applications", selectedJobId],
    });
    queryClient.invalidateQueries({ queryKey: ["recruiter-my-jobs"] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-performance"] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-status-breakdown"] });
    queryClient.invalidateQueries({ queryKey: ["applications"] });
  };

  const decisionMutation = useMutation({
    mutationFn: ({ applicationId, status }) =>
      recruiter.updateApplicationStatus(applicationId, status),
    onSuccess: (data) => {
      setMessage(
        `Candidate status updated to ${
          statusLabels[data?.status] || data?.status || "new status"
        }.`
      );
      invalidateRecruiterData();
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to update candidate status.");
    },
  });

  const updateStatus = (applicationId, status) => {
    setMessage("");
    decisionMutation.mutate({ applicationId, status });
  };

  const loading = jobsLoading || applicationsLoading || decisionMutation.isPending;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
          Recruiter Portal
        </p>

        <h1 className="text-4xl font-black flex items-center gap-3">
          <UserSearch className="w-8 h-8 text-primary" />
          Candidates
        </h1>

        <p className="text-muted-foreground mt-2">
          Select a job, review applicants, and update candidate status.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          <div className="xl:col-span-1">
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Job
            </label>

            <select
              value={selectedJobId}
              onChange={(event) => {
                setSelectedJobId(event.target.value);
                setMessage("");
              }}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm w-full"
            >
              <option value="">— Choose a job —</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {getJobLabel(job)}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Search
            </label>

            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Candidate name, email, or application ID"
                className="pl-9"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Status
            </label>

            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm w-full"
            >
              <option value="all">All statuses</option>
              <option value="active">Active only</option>
              <option value="pending">Pending</option>
              <option value="screening">Screening</option>
              <option value="interview">Interview</option>
              <option value="offer">Offer</option>
              <option value="accepted">Accepted</option>
              <option value="rejected">Rejected</option>
              <option value="withdrawn">Withdrawn</option>
            </select>
          </div>
        </div>
      </div>

      {jobsError && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {jobsError.message || "Failed to load recruiter jobs."}
        </div>
      )}

      {applicationsError && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {applicationsError.message || "Failed to load candidates."}
        </div>
      )}

      {message && (
        <div className="bg-secondary border border-border rounded-xl p-4 mb-6 text-sm">
          {message}
        </div>
      )}

      {!selectedJobId && (
        <div className="bg-card border border-border rounded-xl p-10 text-center">
          <Briefcase className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
          <p className="font-semibold mb-1">Select a job first</p>
          <p className="text-sm text-muted-foreground">
            Candidates will appear after you choose one of your posted jobs.
          </p>
        </div>
      )}

      {selectedJobId && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black">{counts.total}</p>
              <p className="text-xs text-muted-foreground mt-1">Total</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-blue-600">{counts.active}</p>
              <p className="text-xs text-muted-foreground mt-1">Active</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-purple-600">
                {counts.interview}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Interview</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-emerald-600">
                {counts.offer}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Offer</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-green-600">
                {counts.accepted}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Accepted</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-red-600">
                {counts.rejected}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Rejected</p>
            </div>
          </div>

          {selectedJob && (
            <div className="bg-card border border-border rounded-xl p-5 mb-6">
              <p className="text-xs text-muted-foreground uppercase tracking-widest mb-1">
                Selected Job
              </p>
              <h2 className="font-bold text-lg">{selectedJob.title}</h2>
              <p className="text-sm text-muted-foreground">
                {selectedJob.company}
                {selectedJob.location ? ` · ${selectedJob.location}` : ""}
              </p>
            </div>
          )}

          {loading && filteredApplications.length === 0 ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
          ) : filteredApplications.length === 0 ? (
            <div className="bg-card border border-border rounded-xl p-10 text-center">
              <p className="font-semibold mb-1">No candidates found</p>
              <p className="text-sm text-muted-foreground">
                There are no candidates matching the current filters.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredApplications.map((app) => {
                const currentStatus = app.status || "pending";

                return (
                  <div
                    key={app.id}
                    className="bg-card border border-border rounded-xl p-5"
                  >
                    <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-5">
                      <div className="min-w-0">
                        <div className="flex items-center flex-wrap gap-3">
                          <h3 className="text-lg font-bold">
                            {getCandidateName(app)}
                          </h3>

                          <span
                            className={`px-3 py-1 rounded-full border text-xs font-semibold ${
                              statusStyles[currentStatus] || statusStyles.pending
                            }`}
                          >
                            {statusLabels[currentStatus] || currentStatus}
                          </span>
                        </div>

                        <div className="mt-3 space-y-1 text-sm text-muted-foreground">
                          <p className="flex items-center gap-2">
                            <Mail className="w-4 h-4" />
                            {app.applicant_email || "No email"}
                          </p>

                          <p className="flex items-center gap-2">
                            <Briefcase className="w-4 h-4" />
                            {app.job_display_title ||
                              app.job_title ||
                              selectedJob?.title}
                            {" · "}
                            {app.company_display_name ||
                              app.company ||
                              selectedJob?.company}
                          </p>

                          <p className="flex items-center gap-2">
                            <Clock className="w-4 h-4" />
                            Applied {getApplicationDate(app)}
                          </p>
                        </div>

                        {app.reviewed_at && (
                          <p className="text-xs text-muted-foreground mt-2">
                            Last reviewed{" "}
                            {new Date(app.reviewed_at).toLocaleString()}
                          </p>
                        )}

                        {app.notes && (
                          <div className="mt-3 text-sm bg-secondary/60 border border-border rounded-lg p-3">
                            {app.notes}
                          </div>
                        )}
                      </div>

                      <div className="flex flex-wrap gap-2 xl:justify-end">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            navigate(`/recruiter/candidates/${app.applicant}`)
                          }
                        >
                          Profile
                          <ChevronRight className="w-4 h-4 ml-1" />
                        </Button>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updateStatus(app.id, "screening")}
                          disabled={
                            decisionMutation.isPending ||
                            currentStatus === "screening"
                          }
                        >
                          Screening
                        </Button>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updateStatus(app.id, "interview")}
                          disabled={
                            decisionMutation.isPending ||
                            currentStatus === "interview"
                          }
                        >
                          Interview
                        </Button>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updateStatus(app.id, "offer")}
                          disabled={
                            decisionMutation.isPending ||
                            currentStatus === "offer"
                          }
                        >
                          Offer
                        </Button>

                        <Button
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => updateStatus(app.id, "accepted")}
                          disabled={
                            decisionMutation.isPending ||
                            currentStatus === "accepted"
                          }
                        >
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Accept
                        </Button>

                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => updateStatus(app.id, "rejected")}
                          disabled={
                            decisionMutation.isPending ||
                            currentStatus === "rejected"
                          }
                        >
                          <XCircle className="w-4 h-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}