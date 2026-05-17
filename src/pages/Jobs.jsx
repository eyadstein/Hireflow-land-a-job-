import React, { useState } from "react";
import {
  jobs as jobsApi,
  jobsLive,
  recruiter as recruiterApi,
  applications as appsApi,
} from "@/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  MapPin,
  Building2,
  ExternalLink,
  Briefcase,
  Filter,
  Globe,
  DollarSign,
  Loader2,
  RefreshCw,
  Plus,
  Trash2,
  WifiOff,
  CheckCircle2,
  Send,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import PageHeader from "@/components/shared/PageHeader";
import { useToast } from "@/components/ui/use-toast";

const COUNTRIES = [
  { key: "uae", name: "UAE" },
  { key: "egypt", name: "Egypt" },
  { key: "saudi", name: "Saudi Arabia" },
  { key: "qatar", name: "Qatar" },
  { key: "kuwait", name: "Kuwait" },
  { key: "jordan", name: "Jordan" },
  { key: "morocco", name: "Morocco" },
  { key: "bahrain", name: "Bahrain" },
  { key: "oman", name: "Oman" },
  { key: "lebanon", name: "Lebanon" },
  { key: "tunisia", name: "Tunisia" },
  { key: "algeria", name: "Algeria" },
];

const LEVELS = [
  { key: "all", label: "All Levels" },
  { key: "student", label: "Student / Intern" },
  { key: "graduate", label: "Fresh Graduate" },
  { key: "junior", label: "Junior (1-3 yrs)" },
  { key: "mid", label: "Mid Level (3-5 yrs)" },
  { key: "senior", label: "Senior (5+ yrs)" },
  { key: "executive", label: "Executive / Manager" },
];

const TYPE_LABELS = {
  full_time: "Full Time",
  part_time: "Part Time",
  contract: "Contract",
  internship: "Internship",
  remote: "Remote",
  on_site: "On-site",
  hybrid: "Hybrid",
};

const JOB_TYPE_OPTIONS = [
  { value: "full_time", label: "Full Time" },
  { value: "part_time", label: "Part Time" },
  { value: "contract", label: "Contract" },
  { value: "internship", label: "Internship" },
  { value: "remote", label: "Remote" },
  { value: "on_site", label: "On-site" },
  { value: "hybrid", label: "Hybrid" },
];

const emptyJobForm = {
  title: "",
  company: "",
  location: "",
  job_type: "full_time",
  salary_min: "",
  salary_max: "",
  description: "",
};

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function stripHtml(html) {
  if (!html) return "";

  try {
    const div = document.createElement("div");
    div.innerHTML = html;
    return (div.textContent || div.innerText || "")
      .replace(/\s{2,}/g, " ")
      .trim();
  } catch {
    return html.replace(/<[^>]*>/g, " ").replace(/\s{2,}/g, " ").trim();
  }
}

function formatSalary(min, max) {
  const fmt = (n) => {
    const value = Number(n);
    if (!value) return null;
    return value >= 1000 ? `$${(value / 1000).toFixed(0)}k` : `$${value}`;
  };

  if (min && max) return `${fmt(min)} – ${fmt(max)}`;
  if (min) return `From ${fmt(min)}`;
  if (max) return `Up to ${fmt(max)}`;
  return null;
}

function timeAgo(dateStr) {
  if (!dateStr) return null;

  const date = new Date(dateStr);
  if (Number.isNaN(date.getTime())) return null;

  const diff = Date.now() - date.getTime();
  const days = Math.floor(diff / 86400000);

  if (days <= 0) return "Today";
  if (days === 1) return "Yesterday";
  if (days < 7) return `${days}d ago`;
  if (days < 30) return `${Math.floor(days / 7)}w ago`;
  return `${Math.floor(days / 30)}mo ago`;
}

function JobSeekerJobs() {
  const { toast } = useToast();
  const qc = useQueryClient();

  const [query, setQuery] = useState("");
  const [inputVal, setInputVal] = useState("");
  const [country, setCountry] = useState("egypt");
  const [level, setLevel] = useState("all");
  const [appliedIds, setAppliedIds] = useState(new Set());

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ["jobs-live", query, country, level],
    queryFn: () =>
      jobsLive.search({
        q: query || "software developer",
        country,
        ...(level && level !== "all" ? { level } : {}),
      }),
    staleTime: 5 * 60 * 1000,
  });

  const { data: internalJobsData } = useQuery({
    queryKey: ["jobs-internal"],
    queryFn: jobsApi.list,
    staleTime: 60 * 1000,
  });

  const internalRaw = normalizeList(internalJobsData);

  const normalizedInternal = internalRaw.map((job) => ({
    id: `int-${job.id}`,
    _internalId: job.id,
    source: "internal",
    title: job.title,
    company: job.company,
    location: job.location,
    description: job.description,
    apply_link: job.url || null,
    salary_min: job.salary_min,
    salary_max: job.salary_max,
    salary_currency: "USD",
    job_type: job.job_type,
    posted_at: job.created_at,
    logo: null,
    is_remote: job.job_type === "remote",
  }));

  const externalJobs = data?.jobs ?? [];
  const jobs = [...normalizedInternal, ...externalJobs];

  const applyMutation = useMutation({
    mutationFn: async (job) => {
      if (job._internalId) {
        return appsApi.apply({
          job: job._internalId,
          job_id: job._internalId,
        });
      }

      return appsApi.create({
        job_title: job.title || "External Job",
        company: job.company || "Unknown Company",
        status: "applied",
        applied_date: new Date().toISOString().split("T")[0],
        notes:
          job.apply_link && job.source
            ? `External job via ${job.source}: ${job.apply_link}`
            : job.apply_link || stripHtml(job.description || ""),
        contact_name: job.source || "",
        contact_email: "",
      });
    },
    onSuccess: (_, job) => {
      setAppliedIds((prev) => new Set([...prev, job.id]));

      toast({
        title: "Application saved!",
        description: `${job.title || "Job"} at ${job.company || "Company"}`,
      });

      qc.invalidateQueries({ queryKey: ["applications"] });
    },
    onError: (error) => {
      toast({
        title: "Failed to save application",
        description: error?.message || "Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSearch = (e) => {
    e.preventDefault();
    setQuery(inputVal.trim() || "software developer");
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <PageHeader
        eyebrow="Discover"
        title="Job Board"
        description="Browse live opportunities from multiple job boards."
      />

      <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Search jobs, titles, skills..."
            className="pl-9 bg-card"
          />
        </div>

        <Select value={country} onValueChange={setCountry}>
          <SelectTrigger className="w-full sm:w-44 bg-card">
            <Globe className="w-4 h-4 mr-2 text-muted-foreground" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {COUNTRIES.map((countryItem) => (
              <SelectItem key={countryItem.key} value={countryItem.key}>
                {countryItem.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={level} onValueChange={setLevel}>
          <SelectTrigger className="w-full sm:w-44 bg-card">
            <Filter className="w-4 h-4 mr-2 text-muted-foreground" />
            <SelectValue placeholder="All Levels" />
          </SelectTrigger>
          <SelectContent>
            {LEVELS.map((levelItem) => (
              <SelectItem key={levelItem.key} value={levelItem.key}>
                {levelItem.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button type="submit" className="shrink-0">
          Search
        </Button>

        <Button type="button" variant="outline" size="icon" onClick={() => refetch()}>
          <RefreshCw className={`w-4 h-4 ${isFetching ? "animate-spin" : ""}`} />
        </Button>
      </form>

      {(data || normalizedInternal.length > 0) && (
        <div className="flex items-center gap-4 text-xs text-muted-foreground mb-6">
          <span className="font-medium text-foreground">{jobs.length} jobs found</span>
          <span>·</span>
          <span>{COUNTRIES.find((item) => item.key === country)?.name}</span>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-12 text-center">
          <WifiOff className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="font-semibold text-lg mb-1">No jobs found</p>
          <p className="text-sm text-muted-foreground mb-4">
            Try a different search term or country.
          </p>
          <Button variant="outline" onClick={() => refetch()}>
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {jobs.map((job, index) => {
              const salary = formatSalary(job.salary_min, job.salary_max);
              const applied = appliedIds.has(job.id);

              return (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.25, delay: Math.min(index * 0.03, 0.3) }}
                  className="group bg-card border border-border rounded-xl p-5 hover:border-primary/20 hover:shadow-md hover:shadow-primary/5 transition-all duration-300"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {job.logo ? (
                        <img
                          src={job.logo}
                          alt=""
                          className="w-10 h-10 rounded-lg object-contain bg-muted shrink-0"
                          onError={(e) => {
                            e.currentTarget.style.display = "none";
                          }}
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                          <Building2 className="w-5 h-5 text-primary" />
                        </div>
                      )}

                      <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <h3 className="text-base font-semibold text-foreground truncate">
                            {job.title}
                          </h3>

                          {job.source === "internal" ? (
                            <Badge variant="secondary" className="text-[11px]">
                              internal
                            </Badge>
                          ) : (
                            <Badge variant="secondary" className="text-[11px]">
                              external
                            </Badge>
                          )}

                          {job.is_remote && (
                            <Badge
                              variant="secondary"
                              className="text-[11px] bg-green-50 text-green-700 border-green-200"
                            >
                              Remote
                            </Badge>
                          )}

                          {job.job_type && (
                            <Badge variant="secondary" className="text-[11px]">
                              {TYPE_LABELS[job.job_type] || job.job_type}
                            </Badge>
                          )}
                        </div>

                        <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1.5 font-medium text-foreground/80">
                            {job.company}
                          </span>

                          {job.location && (
                            <span className="flex items-center gap-1.5">
                              <MapPin className="w-3.5 h-3.5" />
                              {job.location}
                            </span>
                          )}

                          {salary && (
                            <span className="flex items-center gap-1.5">
                              <DollarSign className="w-3.5 h-3.5" />
                              {salary}
                            </span>
                          )}

                          {job.posted_at && (
                            <span className="text-xs">{timeAgo(job.posted_at)}</span>
                          )}

                          {job.source && job.source !== "internal" && (
                            <span className="text-xs text-muted-foreground/60">
                              {job.source}
                            </span>
                          )}
                        </div>

                        {job.description && (
                          <p className="text-sm text-muted-foreground mt-2 line-clamp-2 leading-relaxed">
                            {stripHtml(job.description)}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2 shrink-0">
                      {applied ? (
                        <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-green-50 text-green-700 text-xs font-medium border border-green-200">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Applied
                        </span>
                      ) : (
                        <Button
                          size="sm"
                          className="text-xs h-8"
                          onClick={() => applyMutation.mutate(job)}
                          disabled={applyMutation.isPending}
                        >
                          {applyMutation.isPending ? (
                            <Loader2 className="w-3 h-3 mr-1.5 animate-spin" />
                          ) : (
                            <Send className="w-3 h-3 mr-1.5" />
                          )}
                          Apply
                        </Button>
                      )}

                      {job.apply_link && (
                        <a
                          href={job.apply_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center justify-center gap-1 px-3 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-primary hover:border-primary/30 transition-colors"
                        >
                          <ExternalLink className="w-3 h-3" />
                          View
                        </a>
                      )}
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}

function RecruiterJobs() {
  const qc = useQueryClient();
  const { toast } = useToast();

  const [showForm, setShowForm] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [form, setForm] = useState(emptyJobForm);

  const { data, isLoading: jobsLoading } = useQuery({
    queryKey: ["recruiter-jobs"],
    queryFn: recruiterApi.myJobs,
  });

  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ["recruiter-dashboard"],
    queryFn: recruiterApi.dashboard,
  });

  const jobs = normalizeList(data);

  const createMutation = useMutation({
    mutationFn: (payload) => jobsApi.create(payload),
    onSuccess: () => {
      toast({ title: "Job posted" });
      qc.invalidateQueries({ queryKey: ["recruiter-jobs"] });
      qc.invalidateQueries({ queryKey: ["recruiter-dashboard"] });
      setShowForm(false);
      setSelectedJob(null);
      setForm(emptyJobForm);
    },
    onError: (error) => {
      toast({
        title: "Failed to post job",
        description: error?.message || "Please check the entered data.",
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => jobsApi.update(id, data),
    onSuccess: () => {
      toast({ title: "Job updated" });
      qc.invalidateQueries({ queryKey: ["recruiter-jobs"] });
      qc.invalidateQueries({ queryKey: ["recruiter-dashboard"] });
      setShowForm(false);
      setSelectedJob(null);
      setForm(emptyJobForm);
    },
    onError: (error) => {
      toast({
        title: "Failed to update job",
        description: error?.message || "Please check the entered data.",
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => jobsApi.delete(id),
    onSuccess: () => {
      toast({ title: "Job deleted" });
      qc.invalidateQueries({ queryKey: ["recruiter-jobs"] });
      qc.invalidateQueries({ queryKey: ["recruiter-dashboard"] });
    },
    onError: (error) => {
      toast({
        title: "Failed to delete job",
        description: error?.message || "Please try again.",
        variant: "destructive",
      });
    },
  });

  const setField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const openNewJob = () => {
    setSelectedJob(null);
    setForm(emptyJobForm);
    setShowForm(true);
  };

  const openEditJob = (job) => {
    setSelectedJob(job);
    setForm({
      title: job.title || "",
      company: job.company || "",
      location: job.location || "",
      job_type: job.job_type || "full_time",
      salary_min: job.salary_min ?? "",
      salary_max: job.salary_max ?? "",
      description: job.description || "",
    });
    setShowForm(true);
  };

  const closeForm = () => {
    setSelectedJob(null);
    setForm(emptyJobForm);
    setShowForm(false);
  };

  const saveJob = () => {
    if (!form.title?.trim()) {
      toast({ title: "Job title is required.", variant: "destructive" });
      return;
    }

    if (!form.company?.trim()) {
      toast({ title: "Company is required.", variant: "destructive" });
      return;
    }

    if (!form.description?.trim()) {
      toast({ title: "Job description is required.", variant: "destructive" });
      return;
    }

    const salaryMin = form.salary_min !== "" ? Number(form.salary_min) : null;
    const salaryMax = form.salary_max !== "" ? Number(form.salary_max) : null;

    if (salaryMin !== null && Number.isNaN(salaryMin)) {
      toast({ title: "Minimum salary must be a valid number.", variant: "destructive" });
      return;
    }

    if (salaryMax !== null && Number.isNaN(salaryMax)) {
      toast({ title: "Maximum salary must be a valid number.", variant: "destructive" });
      return;
    }

    if (salaryMin !== null && salaryMax !== null && salaryMin > salaryMax) {
      toast({
        title: "Maximum salary must be greater than minimum salary.",
        variant: "destructive",
      });
      return;
    }

    const allowedJobTypes = JOB_TYPE_OPTIONS.map((option) => option.value);

    if (!allowedJobTypes.includes(form.job_type)) {
      toast({ title: "Invalid job type selected.", variant: "destructive" });
      return;
    }

    const payload = {
      title: form.title.trim(),
      company: form.company.trim(),
      location: form.location?.trim() || "",
      job_type: form.job_type,
      description: form.description.trim(),
      salary_min: salaryMin,
      salary_max: salaryMax,
    };

    if (selectedJob) {
      updateMutation.mutate({ id: selectedJob.id, data: payload });
    } else {
      createMutation.mutate(payload);
    }
  };

  const saving = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="flex items-start justify-between mb-8">
        <PageHeader
          eyebrow="Recruiter Portal"
          title="My Jobs"
          description="Manage your job postings, applications, and recruiting metrics in one place."
        />

        <Button onClick={openNewJob}>
          <Plus className="w-4 h-4 mr-2" />
          Post Job
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-2">
            Posted Jobs
          </p>
          <p className="text-3xl font-bold">
            {dashboardLoading ? "—" : dashboardData?.total_jobs ?? jobs.length}
          </p>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-2">
            Total Applications
          </p>
          <p className="text-3xl font-bold">
            {dashboardLoading ? "—" : dashboardData?.total_applications ?? 0}
          </p>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground mb-2">
            Acceptance Rate
          </p>
          <p className="text-3xl font-bold">
            {dashboardLoading ? "—" : `${dashboardData?.acceptance_rate ?? 0}%`}
          </p>
        </div>
      </div>

      {showForm && (
        <div className="bg-card border border-border rounded-xl p-5 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
            <div>
              <h3 className="font-semibold text-lg">
                {selectedJob ? "Edit Job" : "New Job Posting"}
              </h3>
              <p className="text-sm text-muted-foreground">
                {selectedJob
                  ? "Update your job details and save changes."
                  : "Create a new job posting for candidates to apply."}
              </p>
            </div>

            <Button variant="outline" onClick={closeForm}>
              Cancel
            </Button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
            <Input
              placeholder="Job title *"
              value={form.title}
              onChange={(e) => setField("title", e.target.value)}
              className="bg-background"
            />

            <Input
              placeholder="Company *"
              value={form.company}
              onChange={(e) => setField("company", e.target.value)}
              className="bg-background"
            />

            <Input
              placeholder="Location"
              value={form.location}
              onChange={(e) => setField("location", e.target.value)}
              className="bg-background"
            />

            <select
              value={form.job_type}
              onChange={(e) => setField("job_type", e.target.value)}
              className="h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              {JOB_TYPE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <Input
              placeholder="Minimum salary"
              type="number"
              value={form.salary_min}
              onChange={(e) => setField("salary_min", e.target.value)}
              className="bg-background"
            />

            <Input
              placeholder="Maximum salary"
              type="number"
              value={form.salary_max}
              onChange={(e) => setField("salary_max", e.target.value)}
              className="bg-background"
            />
          </div>

          <Textarea
            placeholder="Job description *"
            value={form.description}
            onChange={(e) => setField("description", e.target.value)}
            className="mb-3"
          />

          <div className="flex flex-wrap gap-2">
            <Button onClick={saveJob} disabled={saving}>
              {saving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Plus className="w-4 h-4 mr-2" />
              )}
              {selectedJob ? "Save Changes" : "Post Job"}
            </Button>

            <Button variant="outline" onClick={closeForm}>
              Close
            </Button>
          </div>
        </div>
      )}

      {jobsLoading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-12 text-center">
          <Briefcase className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="font-semibold text-lg mb-1">No jobs posted yet</p>
          <p className="text-sm text-muted-foreground mb-4">
            Click "Post Job" to create your first listing.
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-card border border-border rounded-xl p-5 flex flex-col gap-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <h3 className="text-lg font-semibold truncate">{job.title}</h3>

                  <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground mt-1">
                    {job.company && (
                      <span className="flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5" />
                        {job.company}
                      </span>
                    )}

                    {job.location && (
                      <span className="flex items-center gap-1.5">
                        <MapPin className="w-3.5 h-3.5" />
                        {job.location}
                      </span>
                    )}

                    {job.application_count > 0 && (
                      <Badge>{job.application_count} apps</Badge>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button size="icon" variant="ghost" onClick={() => openEditJob(job)}>
                    <Plus className="w-4 h-4 rotate-45" />
                  </Button>

                  <Button
                    size="icon"
                    variant="ghost"
                    className="text-muted-foreground hover:text-red-500"
                    onClick={() => deleteMutation.mutate(job.id)}
                    disabled={deleteMutation.isPending}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>

              {job.description && (
                <p className="text-sm text-muted-foreground line-clamp-3">
                  {stripHtml(job.description)}
                </p>
              )}

              <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                {formatSalary(job.salary_min, job.salary_max) && (
                  <span className="px-2 py-1 rounded-full bg-slate-100 text-slate-700">
                    {formatSalary(job.salary_min, job.salary_max)}
                  </span>
                )}

                {job.job_type && (
                  <span className="px-2 py-1 rounded-full bg-slate-100 text-slate-700">
                    {TYPE_LABELS[job.job_type] || job.job_type}
                  </span>
                )}

                {job.created_at && <span>Posted {timeAgo(job.created_at)}</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Jobs() {
  const role = localStorage.getItem("role");
  return role === "recruiter" ? <RecruiterJobs /> : <JobSeekerJobs />;
}