import React, { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { GitCompare, Loader2, Trophy, User, Search } from "lucide-react";

import { recruiter } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

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

const tierStyles = {
  star: "bg-yellow-100 text-yellow-800 border-yellow-200",
  strong: "bg-blue-100 text-blue-800 border-blue-200",
  average: "bg-gray-100 text-gray-800 border-gray-200",
  below_average: "bg-red-50 text-red-700 border-red-200",
};

export default function Compare() {
  const navigate = useNavigate();

  const [selectedJobId, setSelectedJobId] = useState("");
  const [selectedApplicationIds, setSelectedApplicationIds] = useState([]);
  const [search, setSearch] = useState("");

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
    queryKey: ["recruiter-compare-applications", selectedJobId],
    queryFn: () => recruiter.jobApplications(selectedJobId),
    enabled: !!selectedJobId,
  });

  const applications = normalizeList(applicationsData);

  const filteredApplications = useMemo(() => {
    const cleanSearch = search.trim().toLowerCase();

    return applications.filter((app) => {
      const name = getCandidateName(app).toLowerCase();
      const email = (app.applicant_email || "").toLowerCase();

      return (
        !cleanSearch ||
        name.includes(cleanSearch) ||
        email.includes(cleanSearch) ||
        String(app.id).includes(cleanSearch)
      );
    });
  }, [applications, search]);

  const compareMutation = useMutation({
    mutationFn: (applicationIds) => recruiter.compareApplications(applicationIds),
  });

  const toggleApplication = (id) => {
    setSelectedApplicationIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((item) => item !== id);
      }

      if (prev.length >= 4) {
        return prev;
      }

      return [...prev, id];
    });
  };

  const runCompare = () => {
    if (selectedApplicationIds.length < 2) return;
    compareMutation.mutate(selectedApplicationIds);
  };

  const resetComparison = () => {
    compareMutation.reset();
  };

  const selectedJob = jobs.find((job) => String(job.id) === String(selectedJobId));
  const loading = jobsLoading || applicationsLoading;
  const result = compareMutation.data;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
          Recruiter Portal
        </p>

        <h1 className="text-4xl font-black flex items-center gap-3">
          <GitCompare className="w-8 h-8 text-primary" />
          Candidate Compare
        </h1>

        <p className="text-muted-foreground mt-2">
          Select candidates visually from a job. No manual candidate IDs.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          <div>
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Job
            </label>

            <select
              value={selectedJobId}
              onChange={(event) => {
                setSelectedJobId(event.target.value);
                setSelectedApplicationIds([]);
                compareMutation.reset();
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
                placeholder="Candidate name, email, or application ID"
                className="pl-9"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Selected
            </label>

            <div className="flex gap-2">
              <div className="h-10 rounded-md border border-input bg-background px-3 text-sm flex items-center flex-1">
                {selectedApplicationIds.length}/4 selected
              </div>

              <Button
                type="button"
                onClick={runCompare}
                disabled={compareMutation.isPending || selectedApplicationIds.length < 2}
              >
                {compareMutation.isPending ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : null}
                Compare
              </Button>
            </div>
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

      {compareMutation.error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {compareMutation.error.message || "Failed to compare candidates."}
        </div>
      )}

      {!selectedJobId ? (
        <div className="bg-card border border-border rounded-xl p-10 text-center">
          <p className="font-semibold">Select a job first</p>
          <p className="text-sm text-muted-foreground mt-1">
            Candidate cards will appear here.
          </p>
        </div>
      ) : loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : result ? (
        <div className="space-y-6">
          {result.recommended && (
            <div className="bg-primary/5 border border-primary/20 rounded-xl p-5 flex gap-4">
              <Trophy className="w-6 h-6 text-primary shrink-0 mt-1" />
              <div>
                <p className="font-bold">Recommended Candidate</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {result.recommended.username || result.recommended.email} has the strongest comparison profile in this group.
                </p>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {result.candidates.map((candidate) => (
              <div key={candidate.user_id} className="bg-card border border-border rounded-xl p-5">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mb-3">
                  <User className="w-5 h-5 text-primary" />
                </div>

                <h3 className="font-bold truncate">
                  {candidate.username || candidate.email}
                </h3>

                <p className="text-xs text-muted-foreground truncate mb-4">
                  {candidate.email}
                </p>

                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm text-muted-foreground">Score</span>
                  <span className="text-3xl font-black">{candidate.score}</span>
                </div>

                <span className={`inline-block px-3 py-1 rounded-full border text-xs font-semibold ${tierStyles[candidate.tier] || tierStyles.average}`}>
                  {candidate.tier}
                </span>

                <div className="mt-4 space-y-1 text-sm">
                  <p>Total applications: {candidate.stats?.total_applications ?? 0}</p>
                  <p>Accepted: {candidate.stats?.accepted ?? 0}</p>
                  <p>Rejected: {candidate.stats?.rejected ?? 0}</p>
                  <p>Interview: {candidate.stats?.interview ?? 0}</p>
                </div>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="w-full mt-4"
                  onClick={() => navigate(`/recruiter/candidates/${candidate.user_id}`)}
                >
                  View Profile
                </Button>
              </div>
            ))}
          </div>

          <Button type="button" variant="outline" onClick={resetComparison}>
            Back to selection
          </Button>
        </div>
      ) : filteredApplications.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-10 text-center">
          <p className="font-semibold">No candidates found</p>
          <p className="text-sm text-muted-foreground mt-1">
            {selectedJob ? `No applications found for ${selectedJob.title}.` : "Try changing your filters."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredApplications.map((app) => {
            const selected = selectedApplicationIds.includes(app.id);
            const disabled = !selected && selectedApplicationIds.length >= 4;

            return (
              <button
                key={app.id}
                type="button"
                onClick={() => toggleApplication(app.id)}
                disabled={disabled}
                className={`text-left bg-card border rounded-xl p-5 transition ${
                  selected
                    ? "border-primary shadow-sm"
                    : "border-border hover:border-primary/40"
                } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
              >
                <div className="flex items-start gap-3">
                  <input type="checkbox" checked={selected} readOnly />

                  <div>
                    <p className="font-bold">{getCandidateName(app)}</p>
                    <p className="text-sm text-muted-foreground">
                      {app.applicant_email}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Application ID: {app.id}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Status: {app.status}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}