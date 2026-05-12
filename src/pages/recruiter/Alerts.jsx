import React from "react";
import { useQuery } from "@tanstack/react-query";
import { recruiter } from "@/api/client";
import { AlertTriangle, Loader2, AlertCircle, Info, ShieldAlert } from "lucide-react";

const severityConfig = {
  high:   { bg: "bg-red-50   border-red-200",   icon: <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />,    badge: "bg-red-100   text-red-700"   },
  medium: { bg: "bg-yellow-50 border-yellow-200",icon: <AlertCircle  className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" />, badge: "bg-yellow-100 text-yellow-700" },
  low:    { bg: "bg-blue-50   border-blue-200",  icon: <Info          className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />,  badge: "bg-blue-100   text-blue-700"   },
};

const typeLabels = {
  stale_job:           "Stale Job",
  low_application_rate:"Low Application Rate",
  pending_backlog:     "Pending Backlog",
  high_rejection_rate: "High Rejection Rate",
  old_job:             "Old Job",
  incomplete_posting:  "Incomplete Posting",
  frequent_applicant:  "Frequent Applicant",
};

export default function Alerts() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["r-alerts"],
    queryFn: recruiter.alerts,
  });

  const alerts = data?.alerts ?? [];

  const high   = alerts.filter((a) => a.severity === "high");
  const medium = alerts.filter((a) => a.severity === "medium");
  const low    = alerts.filter((a) => a.severity === "low");

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <AlertTriangle className="w-8 h-8 text-primary" />
          Risk & Behaviour Alerts
        </h1>
        <p className="text-muted-foreground mt-2">Stale jobs, pending backlogs, high rejection rates, and more.</p>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : alerts.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-10 text-center">
          <p className="text-2xl mb-2">✅</p>
          <p className="font-semibold">No alerts — everything looks healthy!</p>
          <p className="text-sm text-muted-foreground mt-1">We'll flag issues here as they arise.</p>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Summary */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-red-600">{high.length}</p>
              <p className="text-xs text-red-600 mt-1 font-medium uppercase tracking-wider">High</p>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-yellow-600">{medium.length}</p>
              <p className="text-xs text-yellow-600 mt-1 font-medium uppercase tracking-wider">Medium</p>
            </div>
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
              <p className="text-3xl font-bold text-blue-600">{low.length}</p>
              <p className="text-xs text-blue-600 mt-1 font-medium uppercase tracking-wider">Low</p>
            </div>
          </div>

          {/* Alert groups */}
          {[
            { label: "High Priority", list: high },
            { label: "Medium Priority", list: medium },
            { label: "Low Priority", list: low },
          ].map(({ label, list }) =>
            list.length > 0 ? (
              <section key={label}>
                <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-3">{label}</h2>
                <div className="space-y-3">
                  {list.map((alert, i) => {
                    const cfg = severityConfig[alert.severity] || severityConfig.low;
                    return (
                      <div key={i} className={`border rounded-xl p-4 ${cfg.bg}`}>
                        <div className="flex gap-3">
                          {cfg.icon}
                          <div className="flex-1 min-w-0">
                            <div className="flex flex-wrap items-center gap-2 mb-1">
                              <p className="font-semibold text-sm">{alert.title}</p>
                              <span className={`px-2 py-0.5 rounded-full text-xs ${cfg.badge}`}>
                                {typeLabels[alert.type] || alert.type}
                              </span>
                              {alert.job_title && (
                                <span className="text-xs text-muted-foreground">· {alert.job_title}</span>
                              )}
                            </div>
                            <p className="text-sm text-muted-foreground">{alert.message}</p>
                            {alert.action && (
                              <p className="text-xs mt-2 font-medium text-foreground/80">
                                💡 {alert.action}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            ) : null
          )}
        </div>
      )}
    </div>
  );
}
