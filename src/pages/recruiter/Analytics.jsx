import React from "react";
import { useQuery } from "@tanstack/react-query";
import { recruiter } from "@/api/client";
import { BarChart3, Loader2 } from "lucide-react";

function StatCard({ label, value, sub, accent }) {
  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">{label}</p>
      <p className={`text-3xl font-bold ${accent ? "text-primary" : ""}`}>{value ?? "—"}</p>
      {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
    </div>
  );
}

function MiniBar({ items, valueKey, labelKey, colorClass = "bg-primary/40 hover:bg-primary/70" }) {
  if (!items?.length) return <p className="text-sm text-muted-foreground">No data yet.</p>;
  const max = Math.max(...items.map((i) => i[valueKey]), 1);
  return (
    <div className="flex items-end gap-1 h-28">
      {items.map((item, i) => {
        const h = Math.round((item[valueKey] / max) * 100);
        return (
          <div key={i} className="flex-1 flex flex-col items-center gap-0.5 group relative min-w-0">
            <div
              className={`w-full ${colorClass} transition-colors rounded-t cursor-default`}
              style={{ height: `${Math.max(h, 2)}%` }}
              title={`${item[labelKey]}: ${item[valueKey]}`}
            />
          </div>
        );
      })}
    </div>
  );
}

export default function Analytics() {
  const { data: trends, isLoading } = useQuery({ queryKey: ["r-trends"],       queryFn: recruiter.trends });
  const { data: dist }              = useQuery({ queryKey: ["r-dist"],          queryFn: recruiter.jobTypeDistribution });
  const { data: topJobs }           = useQuery({ queryKey: ["r-top-jobs"],      queryFn: recruiter.topJobs });
  const { data: status }            = useQuery({ queryKey: ["r-status"],        queryFn: recruiter.statusBreakdown });
  const { data: velocity }          = useQuery({ queryKey: ["r-velocity"],      queryFn: recruiter.hiringVelocity });

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-primary" />
          Hiring Intelligence
        </h1>
        <p className="text-muted-foreground mt-2">Analytics, trends, and hiring velocity across all your jobs.</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <div className="space-y-10">

          {/* Status Breakdown */}
          {status && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Application Status</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Total Applications" value={status.total} accent />
                <StatCard label="Pending"  value={status.pending}  sub={`${status.pending_pct}%`} />
                <StatCard label="Accepted" value={status.accepted} sub={`${status.accepted_pct}%`} />
                <StatCard label="Rejected" value={status.rejected} sub={`${status.rejected_pct}%`} />
              </div>
            </section>
          )}

          {/* Application Trends */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Application Trends — Last 30 Days
            </h2>
            <div className="bg-card border border-border rounded-xl p-6">
              <MiniBar
                items={trends?.data ?? []}
                valueKey="applications"
                labelKey="date"
              />
              <p className="text-xs text-muted-foreground mt-3 text-center">Daily application volume</p>
            </div>
          </section>

          {/* Hiring Velocity */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Hiring Velocity — Last 8 Weeks
            </h2>
            <div className="bg-card border border-border rounded-xl p-6">
              <MiniBar
                items={velocity?.data ?? []}
                valueKey="hires"
                labelKey="week"
                colorClass="bg-green-500/40 hover:bg-green-500/70"
              />
              <p className="text-xs text-muted-foreground mt-3 text-center">Weekly accepted hires</p>
            </div>
          </section>

          {/* Job Type Distribution */}
          {dist?.distribution?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Job Type Distribution</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {dist.distribution.map((item) => (
                  <div key={item.job_type} className="bg-card border border-border rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold">{item.count}</p>
                    <p className="text-xs text-muted-foreground mt-1 capitalize">{item.job_type?.replace(/_/g, " ") || "Unspecified"}</p>
                    <p className="text-xs text-primary mt-1">{item.percentage}%</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Top Performing Jobs */}
          {topJobs?.top_jobs?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Top Performing Jobs</h2>
              <div className="space-y-2">
                {topJobs.top_jobs.map((job, i) => (
                  <div key={job.id} className="bg-card border border-border rounded-xl p-4 flex justify-between items-center gap-4">
                    <div className="flex items-center gap-3">
                      <span className="text-xs font-bold text-muted-foreground w-5">#{i + 1}</span>
                      <div>
                        <p className="font-semibold">{job.title}</p>
                        <p className="text-sm text-muted-foreground">{job.company}{job.location ? ` • ${job.location}` : ""}</p>
                      </div>
                    </div>
                    <span className="shrink-0 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-semibold">
                      {job.applications} apps
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {!status && !trends && (
            <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
              No data yet. Post some jobs and review applications to see analytics here.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
