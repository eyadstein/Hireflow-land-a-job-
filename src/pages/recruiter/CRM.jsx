import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { candidateCRM } from "@/api/client";
import { Database, Loader2, User, BarChart2, Layers, Clock, CheckCircle, XCircle, Activity } from "lucide-react";

const statusColors = {
  new:          "bg-gray-100   text-gray-700",
  active:       "bg-blue-100   text-blue-700",
  engaged:      "bg-indigo-100 text-indigo-700",
  interviewing: "bg-yellow-100 text-yellow-700",
  offered:      "bg-green-100  text-green-700",
  hired:        "bg-emerald-100 text-emerald-700",
  rejected:     "bg-red-100    text-red-700",
  inactive:     "bg-muted      text-muted-foreground",
};

const sourceLabels = {
  website: "Website", referral: "Referral", linkedin: "LinkedIn",
  job_board: "Job Board", recruiter: "Recruiter", event: "Event",
  cold_email: "Cold Email", other: "Other",
};

export default function CRM() {
  const [activeTab, setActiveTab] = useState("profiles");

  const { data: profilesData, isLoading: loadingProfiles } = useQuery({
    queryKey: ["crm-profiles"],
    queryFn: candidateCRM.profiles,
  });

  const { data: analyticsData, isLoading: loadingAnalytics } = useQuery({
    queryKey: ["crm-analytics"],
    queryFn: candidateCRM.analytics,
  });

  const { data: pipelinesData, isLoading: loadingPipelines } = useQuery({
    queryKey: ["crm-pipelines"],
    queryFn: candidateCRM.pipelines,
  });

  const { data: tasksData, isLoading: loadingTasks } = useQuery({
    queryKey: ["crm-tasks"],
    queryFn: candidateCRM.tasks,
  });

  const profiles  = Array.isArray(profilesData)  ? profilesData  : (profilesData?.results  ?? []);
  const pipelines = Array.isArray(pipelinesData)  ? pipelinesData : (pipelinesData?.results ?? []);
  const tasks     = Array.isArray(tasksData)       ? tasksData     : (tasksData?.results     ?? []);
  const analytics = analyticsData ?? {};

  const isLoading = loadingProfiles || loadingAnalytics;

  const tabs = [
    { key: "profiles",  label: "Candidates", icon: <User className="w-4 h-4" /> },
    { key: "pipelines", label: "Pipelines",  icon: <Layers className="w-4 h-4" /> },
    { key: "tasks",     label: "Tasks",      icon: <CheckCircle className="w-4 h-4" /> },
    { key: "analytics", label: "Analytics",  icon: <BarChart2 className="w-4 h-4" /> },
  ];

  const statusGroups = profiles.reduce((acc, p) => {
    const s = p.status || "new";
    acc[s] = (acc[s] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      {/* Header */}
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <Database className="w-8 h-8 text-primary" />
          Candidate CRM
        </h1>
        <p className="text-muted-foreground mt-2">Manage your candidate relationships, pipelines, and tasks.</p>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "Total Candidates", value: profiles.length, icon: <User className="w-5 h-5 text-primary" /> },
          { label: "Pipelines",        value: pipelines.length, icon: <Layers className="w-5 h-5 text-blue-500" /> },
          { label: "Open Tasks",       value: tasks.filter(t => t.status !== "completed" && t.status !== "cancelled").length, icon: <Clock className="w-5 h-5 text-yellow-500" /> },
          { label: "Hired",            value: statusGroups["hired"] ?? 0, icon: <CheckCircle className="w-5 h-5 text-green-500" /> },
        ].map(({ label, value, icon }) => (
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
            className={`flex items-center gap-1.5 px-4 py-2 rounded-md text-sm font-medium transition ${
              activeTab === t.key ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.icon}{t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <>
          {/* Candidates */}
          {activeTab === "profiles" && (
            <div className="space-y-3">
              {profiles.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-10 text-center">
                  <p className="text-2xl mb-2">👥</p>
                  <p className="font-semibold">No candidates in CRM yet</p>
                  <p className="text-sm text-muted-foreground mt-1">Candidates are added when they apply or are imported.</p>
                </div>
              ) : (
                profiles.map((p) => (
                  <div key={p.id} className="bg-card border border-border rounded-xl p-5 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <User className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="font-semibold">{p.user?.username ?? `Candidate #${p.id}`}</p>
                        <p className="text-xs text-muted-foreground">
                          {p.user?.email} · Source: {sourceLabels[p.source] ?? p.source}
                          {p.assigned_to && ` · Assigned to: ${p.assigned_to.username ?? p.assigned_to}`}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {p.rating > 0 && (
                        <div className="flex gap-0.5">
                          {[1,2,3,4,5].map((s) => (
                            <span key={s} className={`text-xs ${s <= p.rating ? "text-yellow-500" : "text-muted"}`}>★</span>
                          ))}
                        </div>
                      )}
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${statusColors[p.status] ?? statusColors.new}`}>
                        {p.status}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Pipelines */}
          {activeTab === "pipelines" && (
            <div className="space-y-4">
              {loadingPipelines ? (
                <div className="flex items-center justify-center py-10"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
              ) : pipelines.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-10 text-center">
                  <p className="text-2xl mb-2">📊</p>
                  <p className="font-semibold">No pipelines created yet</p>
                  <p className="text-sm text-muted-foreground mt-1">Create a pipeline to track candidate stages.</p>
                </div>
              ) : (
                pipelines.map((pipeline) => (
                  <div key={pipeline.id} className="bg-card border border-border rounded-xl p-5">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="font-semibold">{pipeline.name}</p>
                        <p className="text-xs text-muted-foreground">{pipeline.description}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-xs ${pipeline.is_active ? "bg-green-100 text-green-700" : "bg-muted text-muted-foreground"}`}>
                        {pipeline.is_active ? "Active" : "Inactive"}
                      </span>
                    </div>
                    {pipeline.stages?.length > 0 && (
                      <div className="flex gap-2 flex-wrap">
                        {pipeline.stages.map((stage, i) => (
                          <div key={i} className="flex items-center gap-1">
                            <span className="px-3 py-1 bg-muted rounded-full text-xs">{stage}</span>
                            {i < pipeline.stages.length - 1 && <span className="text-muted-foreground text-xs">→</span>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Tasks */}
          {activeTab === "tasks" && (
            <div className="space-y-3">
              {loadingTasks ? (
                <div className="flex items-center justify-center py-10"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
              ) : tasks.length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-10 text-center">
                  <p className="text-2xl mb-2">✅</p>
                  <p className="font-semibold">No tasks yet</p>
                  <p className="text-sm text-muted-foreground mt-1">Tasks are created from candidate profiles.</p>
                </div>
              ) : (
                tasks.map((task) => {
                  const priorityColor = { low: "bg-blue-100 text-blue-700", medium: "bg-yellow-100 text-yellow-700", high: "bg-orange-100 text-orange-700", urgent: "bg-red-100 text-red-700" };
                  const statusIcon = task.status === "completed" ? <CheckCircle className="w-4 h-4 text-green-500" /> : task.status === "cancelled" ? <XCircle className="w-4 h-4 text-red-500" /> : <Clock className="w-4 h-4 text-yellow-500" />;
                  return (
                    <div key={task.id} className="bg-card border border-border rounded-xl p-4 flex items-center gap-4">
                      {statusIcon}
                      <div className="flex-1">
                        <p className="font-medium text-sm">{task.title}</p>
                        {task.description && <p className="text-xs text-muted-foreground">{task.description}</p>}
                        {task.due_date && <p className="text-xs text-muted-foreground mt-0.5">Due: {new Date(task.due_date).toLocaleDateString()}</p>}
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${priorityColor[task.priority] ?? "bg-muted text-muted-foreground"}`}>
                        {task.priority}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          )}

          {/* Analytics */}
          {activeTab === "analytics" && (
            <div>
              {loadingAnalytics ? (
                <div className="flex items-center justify-center py-10"><Loader2 className="w-6 h-6 animate-spin text-primary" /></div>
              ) : Object.keys(analytics).length === 0 ? (
                <div className="bg-card border border-border rounded-xl p-10 text-center">
                  <p className="text-2xl mb-2">📈</p>
                  <p className="font-semibold">No analytics data yet</p>
                  <p className="text-sm text-muted-foreground mt-1">Analytics will populate as you manage more candidates.</p>
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4">
                  {/* Status breakdown */}
                  {Object.keys(statusGroups).length > 0 && (
                    <div className="bg-card border border-border rounded-xl p-5 col-span-2">
                      <h3 className="font-semibold mb-4 flex items-center gap-2"><Activity className="w-4 h-4" /> Status Breakdown</h3>
                      <div className="grid grid-cols-4 gap-3">
                        {Object.entries(statusGroups).map(([status, count]) => (
                          <div key={status} className="text-center p-3 bg-muted/50 rounded-lg">
                            <p className="text-2xl font-bold">{count}</p>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium capitalize ${statusColors[status] ?? statusColors.new}`}>{status}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {/* Raw analytics data */}
                  {Object.entries(analytics).map(([key, val]) => (
                    <div key={key} className="bg-card border border-border rounded-xl p-5">
                      <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">{key.replace(/_/g, " ")}</p>
                      <p className="text-2xl font-bold">{typeof val === "object" ? JSON.stringify(val) : String(val)}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
