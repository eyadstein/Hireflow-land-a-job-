import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { candidateMatching } from "@/api/client";
import {
  GitMerge, Loader2, User, Briefcase, Star, Zap, Target, RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";

const ScoreBar = ({ value, color = "bg-primary" }) => (
  <div className="flex items-center gap-2">
    <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
      <div className={`h-full ${color} rounded-full`} style={{ width: `${Math.min(100, value)}%` }} />
    </div>
    <span className="text-xs text-muted-foreground w-8 text-right">{Math.round(value)}%</span>
  </div>
);

export default function CandidateMatching() {
  const { toast } = useToast();
  const qc = useQueryClient();
  const [activeTab, setActiveTab] = useState("matches");

  const { data: matchesData, isLoading: loadingMatches } = useQuery({
    queryKey: ["cm-top-matches"],
    queryFn: candidateMatching.topMatches,
  });

  const { data: reqData, isLoading: loadingReqs } = useQuery({
    queryKey: ["cm-requirements"],
    queryFn: candidateMatching.requirements,
  });

  const { data: profilesData, isLoading: loadingProfiles } = useQuery({
    queryKey: ["cm-profiles"],
    queryFn: candidateMatching.profiles,
  });

  const triggerMutation = useMutation({
    mutationFn: (id) => candidateMatching.triggerMatching(id),
    onSuccess: () => {
      toast({ title: "Matching triggered", description: "Results will appear shortly." });
      qc.invalidateQueries({ queryKey: ["cm-top-matches"] });
    },
    onError: () => toast({ title: "Failed to trigger matching", variant: "destructive" }),
  });

  const shortlistMutation = useMutation({
    mutationFn: (id) => candidateMatching.shortlistCandidate(id),
    onSuccess: () => {
      toast({ title: "Candidate shortlisted" });
      qc.invalidateQueries({ queryKey: ["cm-top-matches"] });
    },
    onError: () => toast({ title: "Failed to shortlist", variant: "destructive" }),
  });

  const matches  = Array.isArray(matchesData)  ? matchesData  : (matchesData?.results  ?? []);
  const reqs     = Array.isArray(reqData)       ? reqData      : (reqData?.results      ?? []);
  const profiles = Array.isArray(profilesData)  ? profilesData : (profilesData?.results ?? []);

  const tabs = [
    { key: "matches",  label: "Top Matches" },
    { key: "reqs",     label: "Job Requirements" },
    { key: "profiles", label: "Candidate Profiles" },
  ];

  const isLoading = loadingMatches || loadingReqs || loadingProfiles;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <GitMerge className="w-8 h-8 text-primary" />
          Candidate Matching
        </h1>
        <p className="text-muted-foreground mt-2">AI-powered matching of candidates to job requirements.</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { icon: <GitMerge className="w-5 h-5 text-primary" />, label: "Total Matches", value: matches.length },
          { icon: <Briefcase className="w-5 h-5 text-blue-500" />, label: "Job Requirements", value: reqs.length },
          { icon: <User className="w-5 h-5 text-green-500" />, label: "Candidate Profiles", value: profiles.length },
        ].map(({ icon, label, value }) => (
          <div key={label} className="bg-card border border-border rounded-xl p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center">{icon}</div>
            <div>
              <p className="text-2xl font-bold">{isLoading ? "—" : value}</p>
              <p className="text-xs text-muted-foreground">{label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-muted/50 rounded-lg p-1 w-fit">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition ${
              activeTab === t.key ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <>
          {/* Top Matches */}
          {activeTab === "matches" && (
            <div className="space-y-4">
              {matches.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-10 text-center">
                  <p className="text-2xl mb-2">🔍</p>
                  <p className="font-semibold">No matches yet</p>
                  <p className="text-sm text-muted-foreground mt-1">Add job requirements and trigger matching to see results.</p>
                </div>
              ) : (
                matches.map((m) => (
                  <div key={m.id} className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <User className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <p className="font-semibold">{m.candidate?.user?.username ?? `Candidate #${m.candidate}`}</p>
                          <p className="text-xs text-muted-foreground">{m.job?.title ?? `Job #${m.job}`}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <p className="text-2xl font-bold text-primary">{Math.round(m.overall_score ?? m.match_score ?? 0)}%</p>
                          <p className="text-xs text-muted-foreground">Overall</p>
                        </div>
                        {m.is_recommended && (
                          <span className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-medium flex items-center gap-1">
                            <Star className="w-3 h-3" /> Recommended
                          </span>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => shortlistMutation.mutate(m.id)}
                          disabled={shortlistMutation.isPending}
                        >
                          <Target className="w-3.5 h-3.5 mr-1.5" /> Shortlist
                        </Button>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-x-8 gap-y-2">
                      {[
                        { label: "Skills", value: m.skill_match_score, color: "bg-blue-500" },
                        { label: "Experience", value: m.experience_match_score, color: "bg-green-500" },
                        { label: "Education", value: m.education_match_score, color: "bg-purple-500" },
                        { label: "Salary", value: m.salary_match_score, color: "bg-orange-500" },
                      ].map(({ label, value, color }) => value != null && (
                        <div key={label}>
                          <p className="text-xs text-muted-foreground mb-1">{label}</p>
                          <ScoreBar value={value} color={color} />
                        </div>
                      ))}
                    </div>

                    {m.match_reasons?.length > 0 && (
                      <div className="mt-3 flex flex-wrap gap-1">
                        {m.match_reasons.map((r, i) => (
                          <span key={i} className="px-2 py-0.5 bg-green-50 border border-green-200 text-green-700 rounded-full text-xs">{r}</span>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Job Requirements */}
          {activeTab === "reqs" && (
            <div className="space-y-4">
              {reqs.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-10 text-center">
                  <p className="text-2xl mb-2">📋</p>
                  <p className="font-semibold">No job requirements set</p>
                  <p className="text-sm text-muted-foreground mt-1">Requirements are linked to your posted jobs.</p>
                </div>
              ) : (
                reqs.map((r) => (
                  <div key={r.id} className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="font-semibold">{r.job?.title ?? `Job #${r.job}`}</p>
                        <p className="text-xs text-muted-foreground">{r.industry} · {r.experience_required}+ yrs · {r.education_required}</p>
                      </div>
                      <Button
                        size="sm"
                        onClick={() => triggerMutation.mutate(r.id)}
                        disabled={triggerMutation.isPending}
                      >
                        <Zap className="w-3.5 h-3.5 mr-1.5" />
                        {triggerMutation.isPending ? "Running…" : "Trigger Matching"}
                      </Button>
                    </div>
                    {r.required_skills?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {r.required_skills.map((s, i) => (
                          <span key={i} className="px-2 py-0.5 bg-primary/10 text-primary rounded-full text-xs">{s}</span>
                        ))}
                      </div>
                    )}
                    {r.salary_min && r.salary_max && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Salary: ${r.salary_min.toLocaleString()} – ${r.salary_max.toLocaleString()}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Candidate Profiles */}
          {activeTab === "profiles" && (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {profiles.length === 0 ? (
                <div className="col-span-3 bg-card border border-border rounded-xl p-10 text-center">
                  <p className="text-2xl mb-2">👤</p>
                  <p className="font-semibold">No candidate profiles</p>
                  <p className="text-sm text-muted-foreground mt-1">Candidates create profiles through their account settings.</p>
                </div>
              ) : (
                profiles.map((p) => (
                  <div key={p.id} className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-semibold">{p.user?.username ?? `Profile #${p.id}`}</p>
                        <p className="text-xs text-muted-foreground">{p.experience_years} yrs · {p.education_level}</p>
                      </div>
                    </div>
                    {p.skills?.length > 0 && (
                      <div className="flex flex-wrap gap-1">
                        {p.skills.slice(0, 5).map((s, i) => (
                          <span key={i} className="px-2 py-0.5 bg-muted text-muted-foreground rounded-full text-xs">{s}</span>
                        ))}
                        {p.skills.length > 5 && (
                          <span className="px-2 py-0.5 bg-muted text-muted-foreground rounded-full text-xs">+{p.skills.length - 5}</span>
                        )}
                      </div>
                    )}
                    {p.expected_salary_min && p.expected_salary_max && (
                      <p className="text-xs text-muted-foreground mt-2">
                        Expected: ${p.expected_salary_min.toLocaleString()} – ${p.expected_salary_max.toLocaleString()}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
