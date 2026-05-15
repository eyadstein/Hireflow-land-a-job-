import React from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  BarChart3,
  Briefcase,
  CheckCircle,
  Clock,
  Loader2,
  RefreshCw,
  XCircle,
} from "lucide-react";

import { recruiter } from "@/api/client";
import { Button } from "@/components/ui/button";

function StatCard({ label, value, sub, icon: Icon, tone = "default" }) {
  const toneClass = {
    default: "text-foreground",
    primary: "text-primary",
    green: "text-green-600",
    red: "text-red-600",
    yellow: "text-yellow-600",
  }[tone];

  return (
    <div className="bg-card border border-border rounded-xl p-5">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            {label}
          </p>
          <p className={`text-3xl font-black ${toneClass}`}>
            {value ?? "—"}
          </p>
          {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
        </div>

        {Icon && (
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Icon className="w-5 h-5 text-primary" />
          </div>
        )}
      </div>
    </div>
  );
}

function MiniBar({ items = [], valueKey, labelKey, colorClass = "bg-primary/50" }) {
  if (!items.length) {
    return (
      <div className="h-32 flex items-center justify-center text-sm text-muted-foreground">
        No data yet.
      </div>
    );
  }

  const max = Math.max(...items.map((item) => Number(item[valueKey] || 0)), 1);

  return (
    <div className="flex items-end gap-1 h-32">
      {items.map((item, index) => {
        const value = Number(item[valueKey] || 0);
        const height = Math.round((value / max) * 100);

        return (
          <div
            key={`${item[labelKey]}-${index}`}
            className="flex-1 flex flex-col items-center gap-1 group relative min-w-0"
          >
            <div
              className={`w-full ${colorClass} hover:opacity-80 transition rounded-t cursor-default`}
              style={{ height: `${Math.max(height, 3)}%` }}
              title={`${item[labelKey]}: ${value}`}
            />
          </div>
        );
      })}
    </div>
  );
}

function DataTable({ rows = [], columns, emptyText }) {
  if (!rows.length) {
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
                className={`p-4 font-medium ${
                  column.align === "right" ? "text-right" : ""
                }`}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {rows.map((row, index) => (
            <tr
              key={row.id || row.job_id || index}
              className="border-b border-border last:border-0"
            >
              {columns.map((column) => (
                <td
                  key={column.key}
                  className={`p-4 ${
                    column.align === "right" ? "text-right" : ""
                  }`}
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

export default function Analytics() {
  const trendsQuery = useQuery({
    queryKey: ["r-trends"],
    queryFn: recruiter.trends,
    refetchInterval: 15000,
  });

  const distQuery = useQuery({
    queryKey: ["r-dist"],
    queryFn: recruiter.jobTypeDistribution,
    refetchInterval: 15000,
  });

  const topJobsQuery = useQuery({
    queryKey: ["r-top-jobs"],
    queryFn: recruiter.topJobs,
    refetchInterval: 15000,
  });

  const statusQuery = useQuery({
    queryKey: ["r-status"],
    queryFn: recruiter.statusBreakdown,
    refetchInterval: 15000,
  });

  const velocityQuery = useQuery({
    queryKey: ["r-velocity"],
    queryFn: recruiter.hiringVelocity,
    refetchInterval: 15000,
  });

  const isLoading =
    trendsQuery.isLoading ||
    distQuery.isLoading ||
    topJobsQuery.isLoading ||
    statusQuery.isLoading ||
    velocityQuery.isLoading;

  const firstError =
    trendsQuery.error ||
    distQuery.error ||
    topJobsQuery.error ||
    statusQuery.error ||
    velocityQuery.error;

  const refetchAll = () => {
    trendsQuery.refetch();
    distQuery.refetch();
    topJobsQuery.refetch();
    statusQuery.refetch();
    velocityQuery.refetch();
  };

  const status = statusQuery.data || {};
  const trends = trendsQuery.data?.data || [];
  const velocity = velocityQuery.data?.data || [];
  const distribution = distQuery.data?.distribution || [];
  const topJobs = topJobsQuery.data?.top_jobs || topJobsQuery.data?.jobs || [];

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8 flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
            Recruiter Portal
          </p>

          <h1 className="text-4xl font-black flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-primary" />
            Hiring Intelligence
          </h1>

          <p className="text-muted-foreground mt-2">
            Analytics, trends, hiring velocity, and status breakdown across your jobs.
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
          {firstError.message || "Failed to load recruiter analytics."}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <div className="space-y-10">
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Application Status
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard
                label="Total Applications"
                value={status.total || 0}
                icon={Briefcase}
                tone="primary"
              />

              <StatCard
                label="Pending"
                value={status.pending || 0}
                sub={`${status.pending_pct || 0}%`}
                icon={Clock}
                tone="yellow"
              />

              <StatCard
                label="Accepted"
                value={status.accepted || 0}
                sub={`${status.accepted_pct || 0}%`}
                icon={CheckCircle}
                tone="green"
              />

              <StatCard
                label="Rejected"
                value={status.rejected || 0}
                sub={`${status.rejected_pct || 0}%`}
                icon={XCircle}
                tone="red"
              />
            </div>
          </section>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Application Trends — Last 30 Days
            </h2>

            <div className="bg-card border border-border rounded-xl p-6">
              <MiniBar
                items={trends}
                valueKey="applications"
                labelKey="date"
              />
              <p className="text-xs text-muted-foreground mt-3 text-center">
                Daily application volume
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Hiring Velocity — Last 8 Weeks
            </h2>

            <div className="bg-card border border-border rounded-xl p-6">
              <MiniBar
                items={velocity}
                valueKey="hires"
                labelKey="week"
                colorClass="bg-green-500/50"
              />
              <p className="text-xs text-muted-foreground mt-3 text-center">
                Weekly accepted hires
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Job Type Distribution
            </h2>

            {distribution.length === 0 ? (
              <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
                No job type distribution yet.
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {distribution.map((item) => (
                  <div
                    key={item.job_type}
                    className="bg-card border border-border rounded-xl p-4"
                  >
                    <p className="font-bold">{item.job_type}</p>
                    <p className="text-2xl font-black mt-2">{item.count}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {item.percentage || 0}% of jobs
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Top Performing Jobs
            </h2>

            <DataTable
              rows={topJobs}
              emptyText="No job performance data yet."
              columns={[
                {
                  key: "title",
                  label: "Job",
                  render: (row) => (
                    <div>
                      <p className="font-medium">{row.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {row.company}
                      </p>
                    </div>
                  ),
                },
                { key: "location", label: "Location" },
                { key: "job_type", label: "Type" },
                {
                  key: "applications",
                  label: "Applications",
                  align: "right",
                  render: (row) => (
                    <span className="font-bold">
                      {row.applications || row.total_applications || 0}
                    </span>
                  ),
                },
              ]}
            />
          </section>
        </div>
      )}
    </div>
  );
}