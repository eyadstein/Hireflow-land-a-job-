import React from "react";
import { useQuery } from "@tanstack/react-query";
import { recruiter } from "@/api/client";
import { TrendingUp, Loader2, Zap } from "lucide-react";

function ScoreRing({ value, label }) {
  const color = value >= 75 ? "text-green-500" : value >= 50 ? "text-yellow-500" : "text-red-500";
  return (
    <div className="flex flex-col items-center gap-1">
      <span className={`text-5xl font-black ${color}`}>{value}</span>
      <span className="text-xs text-muted-foreground uppercase tracking-wider">{label}</span>
    </div>
  );
}

function MetricRow({ label, value, sub }) {
  return (
    <div className="flex justify-between items-center py-3 border-b border-border last:border-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <div className="text-right">
        <span className="font-semibold">{value ?? "—"}</span>
        {sub && <p className="text-xs text-muted-foreground">{sub}</p>}
      </div>
    </div>
  );
}

export default function Performance() {
  const { data: summary, isLoading } = useQuery({ queryKey: ["r-perf-summary"],   queryFn: recruiter.performanceSummary });
  const { data: activity }           = useQuery({ queryKey: ["r-activity"],        queryFn: recruiter.activityLog });
  const { data: patterns }           = useQuery({ queryKey: ["r-patterns"],        queryFn: recruiter.decisionPatterns });
  const { data: busiest }            = useQuery({ queryKey: ["r-busiest"],         queryFn: recruiter.busiestPeriods });
  const { data: times }              = useQuery({ queryKey: ["r-response-times"],  queryFn: recruiter.responseTimes });

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <TrendingUp className="w-8 h-8 text-primary" />
          Recruiter Performance
        </h1>
        <p className="text-muted-foreground mt-2">Your efficiency score, decision patterns, and response metrics.</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <div className="space-y-8">

          {/* Summary + Efficiency Score */}
          {summary && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-card border border-border rounded-xl p-6 flex flex-col items-center justify-center gap-2">
                <Zap className="w-6 h-6 text-primary mb-1" />
                <ScoreRing value={summary.efficiency_score} label="Efficiency Score" />
                <p className="text-xs text-muted-foreground text-center mt-2">
                  Based on review rate and response speed
                </p>
              </div>

              <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6">
                <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">Summary</h2>
                <MetricRow label="Total Jobs Posted"   value={summary.total_jobs_posted} />
                <MetricRow label="Total Applications"  value={summary.total_applications} />
                <MetricRow label="Reviewed"            value={summary.reviewed}          sub={`${summary.review_rate}% review rate`} />
                <MetricRow label="Pending"             value={summary.pending} />
                <MetricRow label="Acceptance Rate"     value={`${summary.acceptance_rate}%`} />
                <MetricRow
                  label="Avg Response Time"
                  value={summary.avg_response_hours > 0 ? `${summary.avg_response_hours}h` : "No data"}
                />
              </div>
            </div>
          )}

          {/* Decision Patterns */}
          {patterns?.data?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Decision Patterns — Last 8 Weeks</h2>
              <div className="bg-card border border-border rounded-xl p-6 overflow-x-auto">
                <table className="w-full text-sm min-w-[500px]">
                  <thead>
                    <tr className="text-left text-muted-foreground border-b border-border">
                      <th className="pb-2 font-medium">Week</th>
                      <th className="pb-2 font-medium text-right">Decisions</th>
                      <th className="pb-2 font-medium text-right">Accepted</th>
                      <th className="pb-2 font-medium text-right">Rejected</th>
                      <th className="pb-2 font-medium text-right">Accept %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patterns.data.map((row, i) => (
                      <tr key={i} className="border-b border-border last:border-0">
                        <td className="py-2 text-muted-foreground">{row.week?.slice(0, 10)}</td>
                        <td className="py-2 text-right">{row.total_decisions}</td>
                        <td className="py-2 text-right text-green-600">{row.accepted}</td>
                        <td className="py-2 text-right text-red-500">{row.rejected}</td>
                        <td className="py-2 text-right font-semibold">{row.accept_ratio}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {/* Busiest Periods */}
          {busiest && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-card border border-border rounded-xl p-6">
                <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Busiest Days</h2>
                {busiest.busiest_days?.length > 0 ? (
                  <div className="space-y-2">
                    {busiest.busiest_days.map((d, i) => (
                      <div key={i} className="flex justify-between items-center py-1">
                        <span className="text-sm">{d.day}</span>
                        <span className="text-sm font-semibold">{d.reviews} reviews</span>
                      </div>
                    ))}
                  </div>
                ) : <p className="text-sm text-muted-foreground">No data yet.</p>}
              </div>

              <div className="bg-card border border-border rounded-xl p-6">
                <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Peak Hours</h2>
                {busiest.busiest_hours?.length > 0 ? (
                  <div className="space-y-2">
                    {busiest.busiest_hours.map((h, i) => (
                      <div key={i} className="flex justify-between items-center py-1">
                        <span className="text-sm">{h.hour}</span>
                        <span className="text-sm font-semibold">{h.reviews} reviews</span>
                      </div>
                    ))}
                  </div>
                ) : <p className="text-sm text-muted-foreground">No data yet.</p>}
              </div>
            </div>
          )}

          {/* Response Times per Job */}
          {times?.jobs?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Response Times by Job</h2>
              <div className="bg-card border border-border rounded-xl p-6 overflow-x-auto">
                <table className="w-full text-sm min-w-[500px]">
                  <thead>
                    <tr className="text-left text-muted-foreground border-b border-border">
                      <th className="pb-2 font-medium">Job</th>
                      <th className="pb-2 font-medium text-right">Applications</th>
                      <th className="pb-2 font-medium text-right">Pending</th>
                      <th className="pb-2 font-medium text-right">Avg Response</th>
                    </tr>
                  </thead>
                  <tbody>
                    {times.jobs.map((job) => (
                      <tr key={job.job_id} className="border-b border-border last:border-0">
                        <td className="py-2">
                          <p className="font-medium">{job.title}</p>
                          <p className="text-xs text-muted-foreground">{job.company}</p>
                        </td>
                        <td className="py-2 text-right">{job.total_applications}</td>
                        <td className="py-2 text-right">{job.pending}</td>
                        <td className="py-2 text-right">
                          {job.avg_response_hours != null ? `${job.avg_response_hours}h` : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          )}

          {!summary && (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
              Post jobs and review applications to see your performance metrics.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
