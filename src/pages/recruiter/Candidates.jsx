import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { recruiter, jobs as jobsApi } from "@/api/client";
import { UserSearch, Star, Loader2, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

const tierColors = {
  star:          "bg-yellow-100 text-yellow-700 border-yellow-200",
  strong:        "bg-blue-100   text-blue-700   border-blue-200",
  average:       "bg-gray-100   text-gray-600   border-gray-200",
  below_average: "bg-red-50     text-red-600    border-red-200",
};

const tierLabels = {
  star: "⭐ Star", strong: "Strong", average: "Average", below_average: "Below Avg",
};

export default function Candidates() {
  const navigate = useNavigate();
  const [selectedJobId, setSelectedJobId] = useState("");
  const [activeTab, setActiveTab] = useState("ranked");

  const { data: myJobs = [] } = useQuery({
    queryKey: ["r-my-jobs"],
    queryFn: jobsApi.list,
  });

  const { data: ranked, isLoading: rankLoading } = useQuery({
    queryKey: ["r-ranked", selectedJobId],
    queryFn: () => recruiter.rankedCandidates(selectedJobId),
    enabled: !!selectedJobId && activeTab === "ranked",
  });

  const { data: stars, isLoading: starLoading } = useQuery({
    queryKey: ["r-stars"],
    queryFn: recruiter.starCandidates,
    enabled: activeTab === "stars",
  });

  const loading = activeTab === "ranked" ? rankLoading : starLoading;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <UserSearch className="w-8 h-8 text-primary" />
          Top Candidates
        </h1>
        <p className="text-muted-foreground mt-2">Ranked applicants per job and your star candidates across all postings.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {[
          { id: "ranked", label: "Ranked by Job" },
          { id: "stars",  label: "Star Candidates" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              activeTab === tab.id
                ? "bg-primary text-primary-foreground"
                : "bg-card border border-border text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Ranked by Job */}
      {activeTab === "ranked" && (
        <div className="space-y-6">
          <div className="flex flex-col sm:flex-row gap-3">
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm flex-1 max-w-sm"
            >
              <option value="">— Select a job —</option>
              {myJobs.map((job) => (
                <option key={job.id} value={job.id}>{job.title} · {job.company}</option>
              ))}
            </select>
          </div>

          {!selectedJobId && (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
              Select a job above to see its ranked candidates.
            </div>
          )}

          {selectedJobId && loading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
          )}

          {ranked && (
            <>
              <div className="flex gap-4 text-sm text-muted-foreground">
                <span>{ranked.total_candidates} candidates</span>
                <span>·</span>
                <span className="text-yellow-600 font-medium">{ranked.star_count} ⭐ star</span>
              </div>

              <div className="space-y-2">
                {ranked.candidates.map((c) => (
                  <div
                    key={c.application_id}
                    className="bg-card border border-border rounded-xl p-4 flex items-center justify-between gap-4 cursor-pointer hover:border-primary/40 transition"
                    onClick={() => navigate(`/recruiter/candidates/${c.user_id}`)}
                  >
                    <div className="flex items-center gap-4">
                      <span className="text-xs font-bold text-muted-foreground w-6 text-center">#{c.rank}</span>
                      <div>
                        <p className="font-semibold">{c.first_name || c.last_name ? `${c.first_name} ${c.last_name}`.trim() : c.username}</p>
                        <p className="text-xs text-muted-foreground">{c.email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className={`px-2 py-0.5 rounded-full text-xs border ${tierColors[c.tier]}`}>
                        {tierLabels[c.tier]}
                      </span>
                      <span className="text-sm font-bold">{c.score}/100</span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Star Candidates */}
      {activeTab === "stars" && (
        <div className="space-y-4">
          {starLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
          )}

          {stars && (
            <>
              <div className="flex gap-4 text-sm text-muted-foreground mb-2">
                <span className="text-yellow-600 font-medium">⭐ {stars.total_star_candidates} star</span>
                <span>·</span>
                <span>{stars.total_strong_candidates} strong</span>
              </div>

              {stars.candidates.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
                  No star or strong candidates yet.
                </div>
              ) : (
                <div className="space-y-2">
                  {stars.candidates.map((c) => (
                    <div
                      key={c.user_id}
                      className="bg-card border border-border rounded-xl p-4 flex items-center justify-between gap-4 cursor-pointer hover:border-primary/40 transition"
                      onClick={() => navigate(`/recruiter/candidates/${c.user_id}`)}
                    >
                      <div className="flex items-center gap-3">
                        {c.is_star && <Star className="w-4 h-4 text-yellow-500 fill-yellow-400" />}
                        <div>
                          <p className="font-semibold">
                            {c.first_name || c.last_name ? `${c.first_name} ${c.last_name}`.trim() : c.username}
                          </p>
                          <p className="text-xs text-muted-foreground">Applied to: {c.applied_to_job}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 shrink-0">
                        <span className={`px-2 py-0.5 rounded-full text-xs border ${tierColors[c.tier]}`}>
                          {tierLabels[c.tier]}
                        </span>
                        <span className="text-sm font-bold">{c.score}/100</span>
                        <ChevronRight className="w-4 h-4 text-muted-foreground" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
