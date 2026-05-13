import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { recruiter } from "@/api/client";
import { CheckSquare, Loader2, CheckCircle2, XCircle, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function Decisions() {
  const qc = useQueryClient();
  const [selectedJobId, setSelectedJobId] = useState("");
  const [selectedIds,   setSelectedIds]   = useState([]);
  const [topN,          setTopN]          = useState(1);
  const [lastResult,    setLastResult]    = useState(null);

  const { data: myJobsData } = useQuery({ queryKey: ["r-my-jobs"], queryFn: recruiter.myJobs });
  const myJobs = Array.isArray(myJobsData) ? myJobsData : (myJobsData?.results ?? []);

  const { data: applications = [], isLoading: appsLoading } = useQuery({
    queryKey: ["r-job-apps", selectedJobId],
    queryFn: () => recruiter.jobApplications(selectedJobId),
    enabled: !!selectedJobId,
    select: (data) => (Array.isArray(data) ? data : data?.results ?? []),
  });

  const pendingApps = applications.filter((a) => a.status === "pending");

  const toggleSelect = (id) =>
    setSelectedIds((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);

  const selectAll   = () => setSelectedIds(pendingApps.map((a) => a.id));
  const clearSelect = () => setSelectedIds([]);

  const bulkMutation = useMutation({
    mutationFn: ({ ids, decision }) => recruiter.bulkDecision(ids, decision),
    onSuccess: (data) => {
      setLastResult({ type: "bulk", data });
      setSelectedIds([]);
      qc.invalidateQueries({ queryKey: ["r-job-apps", selectedJobId] });
    },
  });

  const rejectAllMutation = useMutation({
    mutationFn: () => recruiter.rejectAllPending(selectedJobId),
    onSuccess: (data) => {
      setLastResult({ type: "reject_all", data });
      qc.invalidateQueries({ queryKey: ["r-job-apps", selectedJobId] });
    },
  });

  const acceptTopMutation = useMutation({
    mutationFn: () => recruiter.acceptTop(selectedJobId, parseInt(topN) || 1),
    onSuccess: (data) => {
      setLastResult({ type: "accept_top", data });
      qc.invalidateQueries({ queryKey: ["r-job-apps", selectedJobId] });
    },
  });

  const anyLoading = bulkMutation.isPending || rejectAllMutation.isPending || acceptTopMutation.isPending;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <CheckSquare className="w-8 h-8 text-primary" />
          One-Click Decisions
        </h1>
        <p className="text-muted-foreground mt-2">Bulk accept/reject, reject all pending, or accept top-N candidates.</p>
      </div>

      {/* Job Selector */}
      <div className="bg-card border border-border rounded-xl p-5 mb-6">
        <label className="text-xs font-semibold uppercase tracking-widest text-muted-foreground block mb-2">Select Job</label>
        <select
          value={selectedJobId}
          onChange={(e) => { setSelectedJobId(e.target.value); setSelectedIds([]); setLastResult(null); }}
          className="h-10 rounded-md border border-input bg-background px-3 text-sm w-full max-w-md"
        >
          <option value="">— Choose a job —</option>
          {myJobs.map((job) => (
            <option key={job.id} value={job.id}>{job.title} · {job.company}</option>
          ))}
        </select>
      </div>

      {/* Result Banner */}
      {lastResult && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-6 text-sm text-green-700">
          {lastResult.data?.message ?? "Done!"}
        </div>
      )}

      {selectedJobId && (
        <div className="space-y-6">
          {/* Stats */}
          {!appsLoading && (
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-card border border-border rounded-xl p-4 text-center">
                <p className="text-2xl font-bold">{applications.length}</p>
                <p className="text-xs text-muted-foreground mt-1">Total Applications</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-yellow-600">{pendingApps.length}</p>
                <p className="text-xs text-muted-foreground mt-1">Pending</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-primary">{selectedIds.length}</p>
                <p className="text-xs text-muted-foreground mt-1">Selected</p>
              </div>
            </div>
          )}

          {/* Action Panel */}
          <div className="bg-card border border-border rounded-xl p-6 space-y-4">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">Quick Actions</h2>

            {/* Bulk Decision */}
            <div className="flex flex-wrap gap-2 items-center">
              <Button
                size="sm"
                onClick={() => bulkMutation.mutate({ ids: selectedIds, decision: "accepted" })}
                disabled={anyLoading || selectedIds.length === 0}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                <CheckCircle2 className="w-4 h-4 mr-1" />
                Accept Selected ({selectedIds.length})
              </Button>
              <Button
                size="sm"
                onClick={() => bulkMutation.mutate({ ids: selectedIds, decision: "rejected" })}
                disabled={anyLoading || selectedIds.length === 0}
                variant="destructive"
              >
                <XCircle className="w-4 h-4 mr-1" />
                Reject Selected ({selectedIds.length})
              </Button>
              <button onClick={selectAll}  className="text-xs text-primary hover:underline">Select All Pending</button>
              <button onClick={clearSelect} className="text-xs text-muted-foreground hover:underline">Clear</button>
            </div>

            <div className="border-t border-border pt-4 flex flex-wrap gap-4 items-center">
              <Button
                size="sm"
                variant="destructive"
                onClick={() => rejectAllMutation.mutate()}
                disabled={anyLoading || pendingApps.length === 0}
              >
                {rejectAllMutation.isPending ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <XCircle className="w-4 h-4 mr-1" />}
                Reject All Pending ({pendingApps.length})
              </Button>

              <div className="flex items-center gap-2">
                <label className="text-sm text-muted-foreground whitespace-nowrap">Accept top</label>
                <Input
                  type="number"
                  min={1}
                  value={topN}
                  onChange={(e) => setTopN(e.target.value)}
                  className="w-16 h-8 text-center"
                />
                <Button
                  size="sm"
                  onClick={() => acceptTopMutation.mutate()}
                  disabled={anyLoading || pendingApps.length === 0}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  {acceptTopMutation.isPending ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <CheckCircle2 className="w-4 h-4 mr-1" />}
                  Accept Top N
                </Button>
              </div>
            </div>
          </div>

          {/* Applications List */}
          {appsLoading ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
          ) : applications.length === 0 ? (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
              No applications for this job yet.
            </div>
          ) : (
            <div className="space-y-2">
              {applications.map((app) => {
                const selected = selectedIds.includes(app.id);
                const isPending = app.status === "pending";
                return (
                  <div
                    key={app.id}
                    onClick={() => isPending && toggleSelect(app.id)}
                    className={`bg-card border rounded-xl p-4 flex items-center justify-between gap-4 transition ${
                      isPending ? "cursor-pointer" : "opacity-60 cursor-default"
                    } ${selected ? "border-primary ring-1 ring-primary/20" : "border-border hover:border-primary/30"}`}
                  >
                    <div className="flex items-center gap-3">
                      {isPending && (
                        <div className={`w-4 h-4 rounded border-2 shrink-0 flex items-center justify-center ${
                          selected ? "bg-primary border-primary" : "border-muted-foreground"
                        }`}>
                          {selected && <span className="text-white text-[10px]">✓</span>}
                        </div>
                      )}
                      <div>
                        <p className="font-medium text-sm">
                          {app.applicant_name || app.applicant || `Application #${app.id}`}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(app.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium shrink-0 ${
                      app.status === "accepted" ? "bg-green-100 text-green-700" :
                      app.status === "rejected" ? "bg-red-100 text-red-600" :
                      "bg-secondary text-muted-foreground"
                    }`}>
                      {app.status}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {!selectedJobId && (
        <div className="bg-card border border-border rounded-xl p-10 text-center text-muted-foreground">
          <Users className="w-10 h-10 mx-auto mb-3 opacity-30" />
          Select a job above to manage its applications.
        </div>
      )}
    </div>
  );
}
