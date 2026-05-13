import React, { useState } from "react";
import { Link } from "react-router-dom";
import { jobs as jobsApi, recruiter as recruiterApi } from "@/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Briefcase, Plus, Trash2, Loader2, BarChart3, TrendingUp,
  UserSearch, GitCompare, Wrench, AlertTriangle, CheckSquare,
  GitMerge, Database, Users, ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/use-toast";

const typeLabels = {
  full_time: "Full-time", part_time: "Part-time",
  contract: "Contract", internship: "Internship", remote: "Remote",
};

const emptyForm = {
  title: "", company: "", location: "", job_type: "full_time",
  salary_min: "", salary_max: "", description: "",
};

const quickLinks = [
  { icon: BarChart3,     label: "Analytics",     desc: "Hiring trends & metrics",      path: "/recruiter/analytics",   color: "text-blue-500",   bg: "bg-blue-50" },
  { icon: TrendingUp,    label: "Performance",   desc: "Recruiter KPIs & activity",    path: "/recruiter/performance", color: "text-green-500",  bg: "bg-green-50" },
  { icon: UserSearch,    label: "Candidates",    desc: "Browse & profile candidates",  path: "/recruiter/candidates",  color: "text-purple-500", bg: "bg-purple-50" },
  { icon: GitCompare,    label: "Compare",       desc: "Side-by-side comparison",      path: "/recruiter/compare",     color: "text-orange-500", bg: "bg-orange-50" },
  { icon: Wrench,        label: "Optimize",      desc: "Job posting optimization",     path: "/recruiter/optimize",    color: "text-cyan-500",   bg: "bg-cyan-50" },
  { icon: AlertTriangle, label: "Alerts",        desc: "Risk & behaviour alerts",      path: "/recruiter/alerts",      color: "text-red-500",    bg: "bg-red-50" },
  { icon: CheckSquare,   label: "Decisions",     desc: "One-click bulk decisions",     path: "/recruiter/decisions",   color: "text-indigo-500", bg: "bg-indigo-50" },
  { icon: GitMerge,      label: "Matching",      desc: "AI candidate matching",        path: "/recruiter/matching",    color: "text-pink-500",   bg: "bg-pink-50" },
  { icon: Database,      label: "CRM",           desc: "Candidate relationship mgmt",  path: "/recruiter/crm",         color: "text-teal-500",   bg: "bg-teal-50" },
];

export default function Recruiter() {
  const [form, setForm] = useState(emptyForm);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: jobsData, isLoading } = useQuery({
    queryKey: ["recruiter-jobs"],
    queryFn: recruiterApi.myJobs,
  });

  const { data: dashData } = useQuery({
    queryKey: ["recruiter-dashboard"],
    queryFn: recruiterApi.dashboard,
  });

  const jobs = Array.isArray(jobsData) ? jobsData : (jobsData?.results ?? []);

  const createMutation = useMutation({
    mutationFn: (data) => jobsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recruiter-jobs"] });
      setForm(emptyForm);
      setShowForm(false);
      setError("");
      toast({ title: "Job posted successfully" });
    },
    onError: (err) => {
      setError(err?.detail || err?.title?.[0] || "Failed to post job.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => jobsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recruiter-jobs"] });
      toast({ title: "Job deleted" });
    },
  });

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const postJob = () => {
    if (!form.title || !form.company || !form.description) {
      setError("Please fill job title, company, and description.");
      return;
    }
    setError("");
    createMutation.mutate({
      title: form.title,
      company: form.company,
      location: form.location,
      job_type: form.job_type,
      description: form.description,
      ...(form.salary_min && { salary_min: parseInt(form.salary_min) }),
      ...(form.salary_max && { salary_max: parseInt(form.salary_max) }),
    });
  };

  const totalApps = dashData?.total_applications ?? jobs.reduce((s, j) => s + (j.application_count ?? 0), 0);

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      {/* Header */}
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <Briefcase className="w-8 h-8 text-primary" />
          Dashboard
        </h1>
        <p className="text-muted-foreground mt-2">Manage your hiring pipeline end-to-end.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Posted Jobs",      value: isLoading ? "—" : jobs.length },
          { label: "Total Applications",value: isLoading ? "—" : totalApps },
          { label: "Active Positions",  value: isLoading ? "—" : jobs.filter(j => j.status === "active" || !j.status).length },
          { label: "Tools Available",   value: quickLinks.length },
        ].map(({ label, value }) => (
          <div key={label} className="bg-card border border-border rounded-xl p-5">
            <p className="text-3xl font-bold">{value}</p>
            <p className="text-xs text-muted-foreground mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Quick links grid */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Recruiter Tools</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
          {quickLinks.map(({ icon: Icon, label, desc, path, color, bg }) => (
            <Link
              key={path}
              to={path}
              className="group bg-card border border-border rounded-xl p-4 hover:border-primary/30 hover:shadow-md transition-all duration-200 flex flex-col gap-2"
            >
              <div className={`w-9 h-9 rounded-lg ${bg} flex items-center justify-center`}>
                <Icon className={`w-5 h-5 ${color}`} />
              </div>
              <div>
                <p className="font-semibold text-sm group-hover:text-primary transition-colors">{label}</p>
                <p className="text-[11px] text-muted-foreground leading-tight mt-0.5">{desc}</p>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/50 group-hover:text-primary/60 mt-auto self-end transition-colors" />
            </Link>
          ))}
        </div>
      </div>

      {/* Posted Jobs */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Posted Jobs</h2>
          <Button size="sm" onClick={() => setShowForm((v) => !v)}>
            <Plus className="w-4 h-4 mr-2" /> Post Job
          </Button>
        </div>

        {showForm && (
          <div className="bg-card border border-border rounded-xl p-5 mb-5">
            <h3 className="font-semibold mb-4">New Job Posting</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
              <Input placeholder="Job Title *" value={form.title} onChange={(e) => update("title", e.target.value)} />
              <Input placeholder="Company Name *" value={form.company} onChange={(e) => update("company", e.target.value)} />
              <Input placeholder="Location" value={form.location} onChange={(e) => update("location", e.target.value)} />
              <select
                value={form.job_type}
                onChange={(e) => update("job_type", e.target.value)}
                className="h-10 rounded-md border border-input bg-background px-3 text-sm"
              >
                {Object.entries(typeLabels).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
              <Input placeholder="Min Salary (USD/mo)" type="number" min="0" value={form.salary_min} onChange={(e) => update("salary_min", e.target.value)} />
              <Input placeholder="Max Salary (USD/mo)" type="number" min="0" value={form.salary_max} onChange={(e) => update("salary_max", e.target.value)} />
            </div>
            <Textarea placeholder="Job Description *" rows={4} value={form.description} onChange={(e) => update("description", e.target.value)} className="mb-3" />
            {error && (
              <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm mb-3">{error}</div>
            )}
            <div className="flex gap-2">
              <Button onClick={postJob} disabled={createMutation.isPending}>
                {createMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
                {createMutation.isPending ? "Posting…" : "Post Job"}
              </Button>
              <Button variant="outline" onClick={() => { setShowForm(false); setError(""); }}>Cancel</Button>
            </div>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-card border border-border rounded-xl p-8 text-center">
            <Briefcase className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="font-semibold mb-1">No jobs posted yet</p>
            <p className="text-sm text-muted-foreground">Click "Post Job" to create your first listing.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job) => (
              <div key={job.id} className="bg-card border border-border rounded-xl p-5">
                <div className="flex justify-between gap-4">
                  <div className="min-w-0">
                    <h3 className="text-base font-bold truncate">{job.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {job.company}{job.location ? ` · ${job.location}` : ""}
                    </p>
                  </div>
                  <button
                    onClick={() => deleteMutation.mutate(job.id)}
                    disabled={deleteMutation.isPending}
                    className="text-muted-foreground hover:text-red-500 transition-colors shrink-0"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <div className="flex flex-wrap gap-2 mt-3 text-xs">
                  <span className="px-2.5 py-1 rounded-full bg-primary/10 text-primary font-medium">
                    {typeLabels[job.job_type] || job.job_type || "Full-time"}
                  </span>
                  {(job.salary_min || job.salary_max) && (
                    <span className="px-2.5 py-1 rounded-full bg-secondary">
                      {job.salary_min && job.salary_max
                        ? `$${job.salary_min}–$${job.salary_max}/mo`
                        : job.salary_min ? `From $${job.salary_min}/mo`
                        : `Up to $${job.salary_max}/mo`}
                    </span>
                  )}
                  {job.application_count > 0 && (
                    <span className="px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 font-medium flex items-center gap-1">
                      <Users className="w-3 h-3" />{job.application_count} applicants
                    </span>
                  )}
                </div>
                {job.description && (
                  <p className="text-sm text-muted-foreground mt-3 line-clamp-2">{job.description}</p>
                )}
                {job.created_at && (
                  <p className="text-xs text-muted-foreground mt-3">
                    Posted {new Date(job.created_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
