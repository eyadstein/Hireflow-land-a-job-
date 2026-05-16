import React, { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle, CheckSquare, Loader2, Search, XCircle } from "lucide-react";

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
  const fullName = `${app.applicant_first_name || ""} ${app.applicant_last_name || ""}`.trim();

  return (
    fullName ||
    app.applicant_name ||
    app.applicant_email ||
    `Candidate #${app.applicant}`
  );
}

export default function Decisions() {
  const queryClient = useQueryClient();

  const [selectedJobId, setSelectedJobId] = useState("");
  const [selectedIds, setSelectedIds] = useState([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("active");
  const [topN, setTopN] = useState(1);
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
    queryKey: ["recruiter-decision-applications", selectedJobId],
    queryFn: () => recruiter.jobApplications(selectedJobId),
    enabled: !!selectedJobId,
    refetchInterval: 10000,
  });

  const applications = normalizeList(applicationsData);

  const selectedJob = jobs.find((job) => String(job.id) === String(selectedJobId));

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

  const actionableApplications = filteredApplications.filter((app) =>
    ACTIVE_STATUSES.includes(app.status)
  );

  const invalidateAll = () => {
    queryClient.invalidateQueries({
      queryKey: ["recruiter-decision-applications", selectedJobId],
    });
    queryClient.invalidateQueries({
      queryKey: ["recruiter-job-applications", selectedJobId],
    });
    queryClient.invalidateQueries({ queryKey: ["recruiter-my-jobs"] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-performance"] });
    queryClient.invalidateQueries({ queryKey: ["applications"] });
  };

  const bulkMutation = useMutation({
    mutationFn: ({ ids, decision }) => recruiter.bulkDecision(ids, decision),
    onSuccess: (data) => {
      setMessage(data?.message || "Decision saved successfully.");
      setSelectedIds([]);
      invalidateAll();
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to save decision.");
    },
  });

  const rejectAllMutation = useMutation({
    mutationFn: () => recruiter.rejectAllActive(selectedJobId),
    onSuccess: (data) => {
      setMessage(data?.message || "Active candidates rejected.");
      setSelectedIds([]);
      invalidateAll();
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to reject active candidates.");
    },
  });

  const acceptTopMutation = useMutation({
    mutationFn: () => recruiter.acceptTop(selectedJobId, Number(topN) || 1),
    onSuccess: (data) => {
      setMessage(data?.message || "Top candidates processed.");
      setSelectedIds([]);
      invalidateAll();
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to accept top candidates.");
    },
  });

  const anyLoading =
    jobsLoading ||
    applicationsLoading ||
    bulkMutation.isPending ||
    rejectAllMutation.isPending ||
    acceptTopMutation.isPending;

  const toggleSelect = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const selectAllActive = () => {
    setSelectedIds(actionableApplications.map((app) => app.id));
  };

  const clearSelection = () => {
    setSelectedIds([]);
  };

  const runBulkDecision = (decision) => {
    if (selectedIds.length === 0) {
      setMessage("Select at least one candidate first.");
      return;
    }

    setMessage("");
    bulkMutation.mutate({
      ids: selectedIds,
      decision,
    });
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
          Recruiter Portal
        </p>

        <h1 className="text-4xl font-black flex items-center gap-3">
          <CheckSquare className="w-8 h-8 text-primary" />
          Bulk Decisions
        </h1>

        <p className="text-muted-foreground mt-2">
          Use this page only for bulk actions. For normal decisions, use Candidates.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <div className="grid grid-cols-1 xl:grid-cols-4 gap-4">
          <div>
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Job
            </label>

            <select
              value={selectedJobId}
              onChange={(event) => {
                setSelectedJobId(event.target.value);
                setSelectedIds([]);
                setMessage("");
              }}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm w-full"
            >
              <option value="">— Choose a job —</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title} · {job.company}
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
                placeholder="Candidate name, email, or app ID"
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
              <option value="active">Active only</option>
              <option value="all">All statuses</option>
              <option value="pending">Pending</option>
              <option value="screening">Screening</option>
              <option value="interview">Interview</option>
              <option value="offer">Offer</option>
              <option value="accepted">Accepted</option>
              <option value="rejected">Rejected</option>
              <option value="withdrawn">Withdrawn</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Accept Top N
            </label>

            <div className="flex gap-2">
              <Input
                type="number"
                min="1"
                value={topN}
                onChange={(event) => setTopN(event.target.value)}
              />

              <Button
                type="button"
                onClick={() => acceptTopMutation.mutate()}
                disabled={!selectedJobId || anyLoading || actionableApplications.length === 0}
              >
                Apply
              </Button>
            </div>
          </div>
        </div>
      </div>

      {(jobsError || applicationsError) && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {jobsError?.message ||
            applicationsError?.message ||
            "Failed to load decision data."}
        </div>
      )}

      {message && (
        <div className="bg-secondary border border-border rounded-xl p-4 mb-6 text-sm">
          {message}
        </div>
      )}

      {!selectedJobId ? (
        <div className="bg-card border border-border rounded-xl p-10 text-center">
          <p className="font-semibold">Choose a job first</p>
          <p className="text-sm text-muted-foreground mt-1">
            Candidates and bulk actions will appear here.
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black">{applications.length}</p>
              <p className="text-xs text-muted-foreground mt-1">Total</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-blue-600">
                {actionableApplications.length}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Actionable</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-primary">
                {selectedIds.length}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Selected</p>
            </div>

            <div className="bg-card border border-border rounded-xl p-4 text-center">
              <p className="text-2xl font-black text-green-600">
                {applications.filter((app) => app.status === "accepted").length}
              </p>
              <p className="text-xs text-muted-foreground mt-1">Accepted</p>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-5 mb-6">
            <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-4">
              <div>
                <h2 className="font-bold">
                  {selectedJob?.title || "Selected Job"}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {selectedJob?.company || ""}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={selectAllActive}
                  disabled={actionableApplications.length === 0}
                >
                  Select Active
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  onClick={clearSelection}
                  disabled={selectedIds.length === 0}
                >
                  Clear
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  onClick={() => runBulkDecision("screening")}
                  disabled={selectedIds.length === 0 || anyLoading}
                  title="Move selected to Screening"
                >
                  → Screening
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  onClick={() => runBulkDecision("interview")}
                  disabled={selectedIds.length === 0 || anyLoading}
                  title="Move selected to Interview"
                >
                  → Interview
                </Button>

                <Button
                  type="button"
                  className="bg-green-600 hover:bg-green-700"
                  onClick={() => runBulkDecision("accepted")}
                  disabled={selectedIds.length === 0 || anyLoading}
                >
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Accept
                </Button>

                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => runBulkDecision("rejected")}
                  disabled={selectedIds.length === 0 || anyLoading}
                >
                  <XCircle className="w-4 h-4 mr-1" />
                  Reject
                </Button>

                <Button
                  type="button"
                  variant="destructive"
                  onClick={() => rejectAllMutation.mutate()}
                  disabled={!selectedJobId || anyLoading || actionableApplications.length === 0}
                >
                  Reject All Active
                </Button>
              </div>
            </div>
          </div>

          {anyLoading && filteredApplications.length === 0 ? (
            <div className="flex justify-center py-20">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
          ) : filteredApplications.length === 0 ? (
            <div className="bg-card border border-border rounded-xl p-10 text-center">
              <p className="font-semibold">No candidates found</p>
              <p className="text-sm text-muted-foreground mt-1">
                Try changing the filters.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredApplications.map((app) => {
                const selected = selectedIds.includes(app.id);
                const locked = ["accepted", "rejected", "withdrawn"].includes(app.status);

                return (
                  <div
                    key={app.id}
                    className={`bg-card border rounded-xl p-4 ${
                      selected ? "border-primary" : "border-border"
                    }`}
                  >
                    <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                      <div className="flex items-start gap-3">
                        <input
                          type="checkbox"
                          checked={selected}
                          disabled={locked}
                          onChange={() => toggleSelect(app.id)}
                          className="mt-1"
                        />

                        <div>
                          <p className="font-semibold">{getCandidateName(app)}</p>
                          <p className="text-sm text-muted-foreground">
                            {app.applicant_email || "No email"}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Application ID: {app.id}
                          </p>
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <span className={`px-3 py-1 rounded-full border text-xs font-semibold ${statusStyles[app.status] || statusStyles.pending}`}>
                          {statusLabels[app.status] || app.status}
                        </span>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            bulkMutation.mutate({ ids: [app.id], decision: "screening" })
                          }
                          disabled={anyLoading || app.status === "screening"}
                        >
                          Screening
                        </Button>

                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            bulkMutation.mutate({ ids: [app.id], decision: "interview" })
                          }
                          disabled={anyLoading || app.status === "interview"}
                        >
                          Interview
                        </Button>

                        <Button
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() =>
                            bulkMutation.mutate({ ids: [app.id], decision: "accepted" })
                          }
                          disabled={anyLoading || app.status === "accepted"}
                        >
                          Accept
                        </Button>

                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() =>
                            bulkMutation.mutate({ ids: [app.id], decision: "rejected" })
                          }
                          disabled={anyLoading || app.status === "rejected"}
                        >
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