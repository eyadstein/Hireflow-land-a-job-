import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { recruiter, jobs as jobsApi } from "@/api/client";
import { Wrench, Loader2, CheckCircle, AlertCircle, XCircle } from "lucide-react";

const gradeColors = { A: "text-green-600", B: "text-blue-600", C: "text-yellow-600", D: "text-orange-600", F: "text-red-600" };
const fieldIcons  = {
  good:      <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />,
  excellent: <CheckCircle className="w-4 h-4 text-green-500 shrink-0" />,
  weak:      <AlertCircle className="w-4 h-4 text-yellow-500 shrink-0" />,
  poor:      <XCircle     className="w-4 h-4 text-red-400 shrink-0" />,
  missing:   <XCircle     className="w-4 h-4 text-red-400 shrink-0" />,
};

export default function Optimize() {
  const [selectedJobId, setSelectedJobId] = useState("");

  const { data: myJobs = [] } = useQuery({ queryKey: ["r-my-jobs"], queryFn: jobsApi.list });

  const { data: report,  isLoading: rLoad } = useQuery({
    queryKey: ["r-opt-report"],
    queryFn: recruiter.optimizationReport,
  });

  const { data: jobDetail, isLoading: jLoad } = useQuery({
    queryKey: ["r-opt-job", selectedJobId],
    queryFn: () => recruiter.jobOptimize(selectedJobId),
    enabled: !!selectedJobId,
  });

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <Wrench className="w-8 h-8 text-primary" />
          Job Performance Optimization
        </h1>
        <p className="text-muted-foreground mt-2">Health scores, field analysis, and improvement suggestions for your jobs.</p>
      </div>

      <div className="space-y-10">

        {/* Overall Report */}
        {rLoad ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : report ? (
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Portfolio Overview</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-card border border-border rounded-xl p-5 text-center">
                <p className="text-3xl font-bold text-primary">{report.average_health_score}</p>
                <p className="text-xs text-muted-foreground mt-1">Avg Health Score</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-5 text-center">
                <p className="text-3xl font-bold">{report.total_jobs}</p>
                <p className="text-xs text-muted-foreground mt-1">Total Jobs</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-5 text-center">
                <p className="text-3xl font-bold text-red-500">{report.critical_jobs_count}</p>
                <p className="text-xs text-muted-foreground mt-1">Critical (D/F)</p>
              </div>
              <div className="bg-card border border-border rounded-xl p-5 text-center">
                <p className="text-3xl font-bold text-green-600">{report.excellent_jobs_count}</p>
                <p className="text-xs text-muted-foreground mt-1">Excellent (A)</p>
              </div>
            </div>

            {report.top_suggestion && (
              <div className="bg-primary/5 border border-primary/20 rounded-xl p-4 text-sm text-primary mb-6">
                💡 {report.top_suggestion}
              </div>
            )}

            <div className="bg-card border border-border rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="p-4 font-medium">Job</th>
                    <th className="p-4 font-medium text-center">Grade</th>
                    <th className="p-4 font-medium text-right">Score</th>
                    <th className="p-4 font-medium text-right">Completeness</th>
                    <th className="p-4 font-medium text-right">Apps</th>
                    <th className="p-4 font-medium text-right">Suggestions</th>
                  </tr>
                </thead>
                <tbody>
                  {report.jobs.map((job) => (
                    <tr
                      key={job.job_id}
                      className="border-b border-border last:border-0 cursor-pointer hover:bg-secondary/30 transition"
                      onClick={() => setSelectedJobId(String(job.job_id))}
                    >
                      <td className="p-4">
                        <p className="font-medium">{job.title}</p>
                        <p className="text-xs text-muted-foreground">{job.company}</p>
                      </td>
                      <td className={`p-4 text-center font-black text-lg ${gradeColors[job.grade]}`}>{job.grade}</td>
                      <td className="p-4 text-right font-semibold">{job.health_score}/100</td>
                      <td className="p-4 text-right">{job.completeness}%</td>
                      <td className="p-4 text-right">{job.applications}</td>
                      <td className="p-4 text-right text-orange-500">{job.suggestions_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ) : null}

        {/* Per-Job Detail */}
        <section>
          <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Detailed Job Analysis</h2>
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm mb-6 max-w-sm"
          >
            <option value="">— Select a job to analyze —</option>
            {myJobs.map((job) => (
              <option key={job.id} value={job.id}>{job.title} · {job.company}</option>
            ))}
          </select>

          {jLoad && <div className="flex items-center gap-2 text-muted-foreground"><Loader2 className="w-5 h-5 animate-spin" /> Analyzing…</div>}

          {jobDetail && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-card border border-border rounded-xl p-5 text-center">
                  <p className={`text-5xl font-black ${gradeColors[jobDetail.grade]}`}>{jobDetail.grade}</p>
                  <p className="text-xs text-muted-foreground mt-1">{jobDetail.status}</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-5 text-center">
                  <p className="text-3xl font-bold text-primary">{jobDetail.health_score}</p>
                  <p className="text-xs text-muted-foreground mt-1">Health Score</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-5 text-center">
                  <p className="text-3xl font-bold">{jobDetail.completeness}%</p>
                  <p className="text-xs text-muted-foreground mt-1">Completeness</p>
                </div>
                <div className="bg-card border border-border rounded-xl p-5 text-center">
                  <p className="text-3xl font-bold">{jobDetail.metrics?.total_applications}</p>
                  <p className="text-xs text-muted-foreground mt-1">Applications</p>
                </div>
              </div>

              {/* Field Status */}
              {jobDetail.fields && (
                <div className="bg-card border border-border rounded-xl p-6">
                  <h3 className="text-sm font-semibold mb-4">Field Status</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {Object.entries(jobDetail.fields).map(([field, status]) => (
                      <div key={field} className="flex items-center gap-2 text-sm capitalize">
                        {fieldIcons[status] || fieldIcons.missing}
                        <span>{field.replace(/_/g, " ")}</span>
                        <span className="text-xs text-muted-foreground ml-auto">{status}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Suggestions */}
              {jobDetail.suggestions?.length > 0 && (
                <div className="bg-card border border-border rounded-xl p-6">
                  <h3 className="text-sm font-semibold mb-3">Improvement Suggestions</h3>
                  <ul className="space-y-2">
                    {jobDetail.suggestions.map((s, i) => (
                      <li key={i} className="flex gap-2 text-sm">
                        <span className="text-primary shrink-0">→</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
