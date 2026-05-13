import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { recruiter } from "@/api/client";
import { GitCompare, Loader2, Plus, X, Trophy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const tierColors = {
  star:          "bg-yellow-100 text-yellow-700",
  strong:        "bg-blue-100   text-blue-700",
  average:       "bg-gray-100   text-gray-600",
  below_average: "bg-red-50     text-red-600",
};

export default function Compare() {
  const navigate    = useNavigate();
  const [ids, setIds]    = useState(["", ""]);
  const [newId, setNewId] = useState("");

  const compareMutation = useMutation({
    mutationFn: (candidateIds) => recruiter.compareCandidates(candidateIds.map(Number).filter(Boolean)),
  });

  const addId = () => {
    if (newId.trim() && !ids.includes(newId.trim()) && ids.length < 4) {
      setIds([...ids, newId.trim()]);
      setNewId("");
    }
  };

  const removeId = (i) => setIds(ids.filter((_, idx) => idx !== i));

  const updateId = (i, val) => setIds(ids.map((id, idx) => (idx === i ? val : id)));

  const run = () => {
    const valid = ids.map(Number).filter(Boolean);
    if (valid.length >= 2) compareMutation.mutate(valid);
  };

  const result = compareMutation.data;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <GitCompare className="w-8 h-8 text-primary" />
          Candidate Comparison
        </h1>
        <p className="text-muted-foreground mt-2">Compare 2–4 candidates side by side with a recommendation.</p>
      </div>

      {/* Input */}
      <div className="bg-card border border-border rounded-xl p-6 mb-8 space-y-4">
        <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Enter Candidate User IDs</h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
          {ids.map((id, i) => (
            <div key={i} className="relative">
              <Input
                placeholder={`Candidate ${i + 1} ID`}
                value={id}
                type="number"
                onChange={(e) => updateId(i, e.target.value)}
              />
              {ids.length > 2 && (
                <button
                  onClick={() => removeId(i)}
                  className="absolute right-2 top-2.5 text-muted-foreground hover:text-red-500 transition"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>

        {ids.length < 4 && (
          <div className="flex gap-2">
            <Input
              placeholder="Add another candidate ID"
              value={newId}
              type="number"
              onChange={(e) => setNewId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && addId()}
              className="max-w-48"
            />
            <Button variant="outline" size="sm" onClick={addId}>
              <Plus className="w-4 h-4 mr-1" /> Add
            </Button>
          </div>
        )}

        <p className="text-xs text-muted-foreground">
          Tip: You can find candidate IDs on the Candidates page.
        </p>

        {compareMutation.error && (
          <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {compareMutation.error?.error || "Could not compare. Check IDs and try again."}
          </div>
        )}

        <Button onClick={run} disabled={compareMutation.isPending || ids.filter(Boolean).length < 2}>
          {compareMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <GitCompare className="w-4 h-4 mr-2" />}
          Compare Candidates
        </Button>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-6">
          {/* Recommendation */}
          <div className="bg-primary/5 border border-primary/20 rounded-xl p-5 flex gap-4 items-start">
            <Trophy className="w-6 h-6 text-primary shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-primary">Recommended: {result.recommendation.recommended_candidate}</p>
              <p className="text-sm text-muted-foreground mt-1">{result.recommendation.reason}</p>
              <button
                onClick={() => navigate(`/recruiter/candidates/${result.recommendation.user_id}`)}
                className="text-xs text-primary hover:underline mt-2 inline-block"
              >
                View full profile →
              </button>
            </div>
          </div>

          {/* Side by side */}
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            {result.candidates.map((c) => (
              <div
                key={c.user_id}
                className={`bg-card border rounded-xl p-5 space-y-4 ${
                  c.rank === 1 ? "border-primary/40 ring-1 ring-primary/20" : "border-border"
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-bold">{c.first_name || c.last_name ? `${c.first_name} ${c.last_name}`.trim() : c.username}</p>
                    <p className="text-xs text-muted-foreground">{c.email}</p>
                  </div>
                  <span className="text-xs font-bold text-muted-foreground">#{c.rank}</span>
                </div>

                <div className="text-center">
                  <span className="text-4xl font-black text-primary">{c.score}</span>
                  <p className="text-xs text-muted-foreground">/100</p>
                  <span className={`mt-1 inline-block px-2 py-0.5 rounded-full text-xs ${tierColors[c.tier]}`}>
                    {c.tier?.replace(/_/g, " ")}
                  </span>
                </div>

                <div className="space-y-1 text-sm">
                  <p className="text-muted-foreground">Applications: <span className="font-medium text-foreground">{c.stats?.total_applications}</span></p>
                  <p className="text-muted-foreground">Pending: <span className="font-medium text-foreground">{c.stats?.pending}</span></p>
                  <p className="text-muted-foreground">Accepted: <span className="font-medium text-green-600">{c.stats?.accepted}</span></p>
                  <p className="text-muted-foreground">Rejected: <span className="font-medium text-red-500">{c.stats?.rejected}</span></p>
                </div>

                {c.strengths?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-green-600 mb-1">Strengths</p>
                    <ul className="space-y-0.5">
                      {c.strengths.map((s, i) => (
                        <li key={i} className="text-xs text-muted-foreground">✓ {s}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {c.weaknesses?.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-red-500 mb-1">Weaknesses</p>
                    <ul className="space-y-0.5">
                      {c.weaknesses.map((w, i) => (
                        <li key={i} className="text-xs text-muted-foreground">✗ {w}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <button
                  onClick={() => navigate(`/recruiter/candidates/${c.user_id}`)}
                  className="text-xs text-primary hover:underline"
                >
                  View profile →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
