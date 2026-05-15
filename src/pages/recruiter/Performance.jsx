import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  TrendingUp,
  Loader2,
  Zap,
  RefreshCw,
  AlertCircle,
  Clock,
  CheckCircle,
  XCircle,
  Briefcase,
} from "lucide-react";

import { recruiter } from "@/api/client";
import { Button } from "@/components/ui/button";

function ScoreRing({ value, label }) {
  const numeric = Number(value || 0);
  const color =
    numeric >= 75
      ? "text-green-500"
      : numeric >= 50
        ? "text-yellow-500"
        : "text-red-500";

  return (
    <div className="flex flex-col items-center gap-1">
      <span className={`text-5xl font-black ${color}`}>{numeric}</span>
      <span className="text-xs text-muted-foreground uppercase tracking-wider">
        {label}
      </span>
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

function MiniStat({ label, value, icon: Icon, tone = "primary" }) {
  const color = {
    primary: "text-primary",
    green: "text-green-600",
    red: "text-red-600",
    yellow: "text-yellow-600",
  }[tone];

  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider">
            {label}
          </p>
          <p className={`text-2xl font-black mt-1 ${color}`}>{value ?? "—"}</p>
        </div>

        {Icon && <Icon className="w-5 h-5 text-muted-foreground" />}
      </div>
    </div>
  );
}

function DataTable({ rows, columns, emptyText }) {
  if (!rows || rows.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
        {emptyText || "No data yet."}
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-muted-foreground border-b border-border">
            {columns.map((column) => (
              <th
                key={column.key}
                className={`p-4 font-medium ${column.align === "right" ? "text-right" : ""}`}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.map((row, index) => (
            <tr key={row.job_id || row.week || index} className="border-b border-border last:border-0">
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={`p-4 ${column.align === "right" ? "text-right" : ""}`}
                >
                  {column.render ? column.render(row) : row[column.key] ?? "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function Performance() {
  const summaryQuery = useQuery({
    queryKey: ["r-perf-summary"],
    queryFn: recruiter.performanceSummary,
    refetchInterval: 15000,
  });

  const activityQuery = useQuery({
    queryKey: ["r-activity"],
    queryFn: recruiter.activityLog,
    refetchInterval: 15000,
  });

  const patternsQuery = useQuery({
    queryKey: ["r-patterns"],
    queryFn: recruiter.decisionPatterns,
    refetchInterval: 15000,
  });

  const busiestQuery = useQuery({
    queryKey: ["r-busiest"],
    queryFn: recruiter.busiestPeriods,
    refetchInterval: 15000,
  });

  const timesQuery = useQuery({
    queryKey: ["r-response-times"],
    queryFn: recruiter.responseTimes,
    refetchInterval: 15000,
  });

  const isLoading =
    summaryQuery.isLoading ||
    activityQuery.isLoading ||
    patternsQuery.isLoading ||
    busiestQuery.isLoading ||
    timesQuery.isLoading;

  const firstError =
    summaryQuery.error ||
    activityQuery.error ||
    patternsQuery.error ||
    busiestQuery.error ||
    timesQuery.error;

  const summary = summaryQuery.data || {};
  const activity = activityQuery.data?.data || [];
  const patterns = patternsQuery.data?.data || [];
  const busiest = busiestQuery.data || {};
  const responseJobs = timesQuery.data?.jobs || [];

  const refetchAll = () => {
    summaryQuery.refetch();
    activityQuery.refetch();
    patternsQuery.refetch();
    busiestQuery.refetch();
    timesQuery.refetch();
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8 flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
            Recruiter Portal
          </p>

          <h1 className="text-4xl font-black flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-primary" />
            Recruiter Performance
          </h1>

          <p className="text-muted-foreground mt-2">
            Efficiency score, decision patterns, review speed, and response metrics.
          </p>
        </div>

        <Button variant="outline" onClick={refetchAll}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {firstError && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm flex gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
          {firstError.message || "Failed to load recruiter performance data."}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-card border border-border rounded-xl p-6 flex flex-col items-center justify-center gap-2">
              <Zap className="w-6 h-6 text-primary mb-1" />
              <ScoreRing value={summary.efficiency_score || 0} label="Efficiency Score" />
              <p className="text-xs text-muted-foreground text-center mt-2">
                Based on review rate and response speed.
              </p>
            </div>

            <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6">
              <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2">
                Summary
              </h2>

              <MetricRow label="Total Jobs Posted" value={summary.total_jobs_posted || 0} />
              <MetricRow label="Total Applications" value={summary.total_applications || 0} />
              <MetricRow
                label="Reviewed"
                value={summary.reviewed || 0}
                sub={`${summary.review_rate || 0}% review rate`}
              />
              <MetricRow label="Pending" value={summary.pending || 0} />
              <MetricRow label="Acceptance Rate" value={`${summary.acceptance_rate || 0}%`} />
              <MetricRow
                label="Avg Response Time"
                value={
                  summary.avg_response_hours > 0
                    ? `${summary.avg_response_hours}h`
                    : "No data"
                }
              />
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MiniStat label="Jobs" value={summary.total_jobs_posted || 0} icon={Briefcase} />
            <MiniStat label="Reviewed" value={summary.reviewed || 0} icon={CheckCircle} tone="green" />
            <MiniStat label="Pending" value={summary.pending || 0} icon={Clock} tone="yellow" />
            <MiniStat label="Acceptance %" value={`${summary.acceptance_rate || 0}%`} icon={CheckCircle} tone="green" />
          </div>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Decision Patterns — Last 8 Weeks
            </h2>

            <DataTable
              rows={patterns}
              emptyText="No decision data yet."
              columns={[
                {
                  key: "week",
                  label: "Week",
                  render: (row) => row.week?.slice(0, 10) || "—",
                },
                { key: "total_decisions", label: "Decisions", align: "right" },
                {
                  key: "accepted",
                  label: "Accepted",
                  align: "right",
                  render: (row) => <span className="text-green-600">{row.accepted || 0}</span>,
                },
                {
                  key: "rejected",
                  label: "Rejected",
                  align: "right",
                  render: (row) => <span className="text-red-500">{row.rejected || 0}</span>,
                },
                {
                  key: "accept_ratio",
                  label: "Accept %",
                  align: "right",
                  render: (row) => <span className="font-semibold">{row.accept_ratio || 0}%</span>,
                },
              ]}
            />
          </section>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <section className="bg-card border border-border rounded-xl p-6">
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
                Busiest Days
              </h2>

              {busiest.busiest_days?.length > 0 ? (
                <div className="space-y-2">
                  {busiest.busiest_days.map((item, index) => (
                    <div key={index} className="flex justify-between items-center py-1">
                      <span className="text-sm">{item.day}</span>
                      <span className="text-sm font-semibold">{item.reviews} reviews</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No data yet.</p>
              )}
            </section>

            <section className="bg-card border border-border rounded-xl p-6">
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
                Peak Hours
              </h2>

              {busiest.busiest_hours?.length > 0 ? (
                <div className="space-y-2">
                  {busiest.busiest_hours.map((item, index) => (
                    <div key={index} className="flex justify-between items-center py-1">
                      <span className="text-sm">{item.hour}</span>
                      <span className="text-sm font-semibold">{item.reviews} reviews</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No data yet.</p>
              )}
            </section>
          </div>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Response Time by Job
            </h2>

            <DataTable
              rows={responseJobs}
              emptyText="No response-time data yet."
              columns={[
                {
                  key: "title",
                  label: "Job",
                  render: (row) => (
                    <div>
                      <p className="font-medium">{row.title}</p>
                      <p className="text-xs text-muted-foreground">{row.company}</p>
                    </div>
                  ),
                },
                { key: "total_applications", label: "Applications", align: "right" },
                { key: "pending", label: "Pending", align: "right" },
                {
                  key: "avg_response_hours",
                  label: "Avg Response",
                  align: "right",
                  render: (row) =>
                    row.avg_response_hours != null
                      ? `${row.avg_response_hours}h`
                      : "No data",
                },
              ]}
            />
          </section>

          {activity.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
                Recent Activity
              </h2>

              <DataTable
                rows={activity.slice(-10).reverse()}
                columns={[
                  { key: "date", label: "Date" },
                  { key: "jobs_posted", label: "Jobs Posted", align: "right" },
                  { key: "reviews", label: "Reviews", align: "right" },
                  { key: "accepts", label: "Accepts", align: "right" },
                  { key: "rejects", label: "Rejects", align: "right" },
                ]}
              />
            </section>
          )}
        </div>
      )}
    </div>
  );
}