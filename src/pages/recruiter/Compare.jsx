import React, { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import {
  GitCompare,
  Loader2,
  Trophy,
  User,
  Search,
  Medal,
} from "lucide-react";

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

const tierLabels = {
  star: "⭐ Top",
  strong: "Strong",
  average: "Average",
  below_average: "Needs Review",
};

const rankIcons = ["🥇", "🥈", "🥉", "4️⃣"];

function ScoreBar({ value, label, color = "bg-primary" }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-muted-foreground mb-1">
        <span>{label}</span>
        <span className="font-semibold">{Math.round(value)}%</span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all duration-500`}
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}

function StatRow({ label, value, highlight }) {
  return (
    <div className={`flex justify-between text-sm py-1 border-b border-border last:border-0 ${highlight ? "font-semibold" : ""}`}>
      <span className="text-muted-foreground">{label}</span>
      <span>{value}</span>
    </div>
  );
}

export default function Compare() {
  const navigate = useNavigate();

  const [selectedJobId, setSelectedJobId] = useState("");
  const [selectedApplicationIds, setSelectedApplicationIds] = useState([]);
  const [search, setSearch] = useState("");

  const { data: jobsData, isLoading: jobsLoading, error: jobsError } = useQuery({
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
      if (prev.includes(id)) return prev.filter((item) => item !== id);
      if (prev.length >= 4) return prev;
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
          Select 2–4 candidates from the same job to compare them side-by-side.
          Scores are relative — the strongest candidate in this group scores 100%.
        </p>
      </div>

      {/* Controls */}
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
              Search candidates
            </label>
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Name, email, or application ID"
                className="pl-9"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">
              Selected ({selectedApplicationIds.length}/4)
            </label>
            <div className="flex gap-2">
              <div className="h-10 rounded-md border border-input bg-background px-3 text-sm flex items-center flex-1">
                {selectedApplicationIds.length < 2
                  ? `Select ${2 - selectedApplicationIds.length} more`
                  : `${selectedApplicationIds.length} candidates ready`}
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

      {/* Errors */}
      {jobsError && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {jobsError.message || "Failed to load jobs."}
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

      {/* State views */}
      {!selectedJobId ? (
        <div className="bg-card border border-border rounded-xl p-10 text-center">
          <GitCompare className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
          <p className="font-semibold">Select a job to begin</p>
          <p className="text-sm text-muted-foreground mt-1">
            Candidate cards will appear here.
          </p>
        </div>
      ) : loading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : result ? (
        /* ── COMPARISON RESULTS ── */
        <div className="space-y-6">
          {/* Recommended banner */}
          {result.recommended && (
            <div className="bg-primary/5 border border-primary/20 rounded-xl p-5 flex gap-4 items-start">
              <Trophy className="w-6 h-6 text-primary shrink-0 mt-0.5" />
              <div>
                <p className="font-bold">
                  Recommended: {result.recommended.username || result.recommended.email}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  This candidate scored highest relative to the other{" "}
                  {result.total_compared - 1} candidate
                  {result.total_compared !== 2 ? "s" : ""} in this comparison.
                  Scores are normalized — 100% = best in this group.
                </p>
              </div>
            </div>
          )}

          {/* Candidate cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {result.candidates.map((candidate, idx) => (
              <div
                key={candidate.user_id}
                className={`bg-card border rounded-xl p-5 flex flex-col gap-4 ${
                  candidate.rank === 1
                    ? "border-primary shadow-sm"
                    : "border-border"
                }`}
              >
                {/* Header */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl">{rankIcons[idx] || `#${candidate.rank}`}</span>
                    <span
                      className={`px-2 py-0.5 rounded-full border text-xs font-semibold ${
                        tierStyles[candidate.tier] || tierStyles.average
                      }`}
                    >
                      {tierLabels[candidate.tier] || candidate.tier}
                    </span>
                  </div>

                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                    <User className="w-5 h-5 text-primary" />
                  </div>

                  <h3 className="font-bold truncate">
                    {candidate.username || candidate.email}
                  </h3>
                  <p className="text-xs text-muted-foreground truncate">
                    {candidate.email}
                  </p>
                </div>

                {/* Relative score bar */}
                <ScoreBar
                  value={candidate.score}
                  label="Relative Score"
                  color={
                    candidate.rank === 1
                      ? "bg-primary"
                      : candidate.rank === 2
                      ? "bg-blue-500"
                      : "bg-muted-foreground/40"
                  }
                />

                {/* Stats */}
                <div className="space-y-0">
                  <StatRow label="Total Applications" value={candidate.stats?.total_applications ?? 0} />
                  <StatRow label="Screening" value={candidate.stats?.screening ?? 0} />
                  <StatRow label="Interview" value={candidate.stats?.interview ?? 0} />
                  <StatRow label="Offer" value={candidate.stats?.offer ?? 0} />
                  <StatRow
                    label="Accepted"
                    value={candidate.stats?.accepted ?? 0}
                    highlight={(candidate.stats?.accepted ?? 0) > 0}
                  />
                  <StatRow label="Rejected" value={candidate.stats?.rejected ?? 0} />
                </div>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="w-full mt-auto"
                  onClick={() => navigate(`/recruiter/candidates/${candidate.user_id}`)}
                >
                  View Full Profile
                </Button>
              </div>
            ))}
          </div>

          <Button type="button" variant="outline" onClick={resetComparison}>
            ← Back to selection
          </Button>
        </div>
      ) : filteredApplications.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-10 text-center">
          <p className="font-semibold">No candidates found</p>
          <p className="text-sm text-muted-foreground mt-1">
            {selectedJob
              ? `No applications found for "${selectedJob.title}".`
              : "Try changing your filters."}
          </p>
        </div>
      ) : (
        /* ── CANDIDATE SELECTION ── */
        <div>
          <p className="text-sm text-muted-foreground mb-4">
            Click candidates to select them for comparison (2–4). Selected candidates
            are highlighted.
          </p>
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
                      ? "border-primary shadow-sm bg-primary/5"
                      : "border-border hover:border-primary/40"
                  } ${disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
                >
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={selected}
                      readOnly
                      className="mt-1 accent-primary"
                    />
                    <div className="min-w-0">
                      <p className="font-bold truncate">{getCandidateName(app)}</p>
                      <p className="text-sm text-muted-foreground truncate">
                        {app.applicant_email}
                      </p>
                      <div className="flex gap-3 mt-1 text-xs text-muted-foreground">
                        <span>App #{app.id}</span>
                        <span
                          className={`px-2 py-0.5 rounded-full border font-medium ${
                            {
                              pending: "bg-yellow-50 text-yellow-700 border-yellow-200",
                              screening: "bg-blue-50 text-blue-700 border-blue-200",
                              interview: "bg-purple-50 text-purple-700 border-purple-200",
                              offer: "bg-emerald-50 text-emerald-700 border-emerald-200",
                              accepted: "bg-green-50 text-green-700 border-green-200",
                              rejected: "bg-red-50 text-red-700 border-red-200",
                            }[app.status] || "bg-gray-50 text-gray-700 border-gray-200"
                          }`}
                        >
                          {app.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
