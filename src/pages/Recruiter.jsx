import React, { useState } from "react";
import { jobs as jobsApi } from "@/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Briefcase, Plus, Trash2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const emptyForm = {
  title: "", company: "", location: "", job_type: "full_time",
  salary_min: "", salary_max: "", description: "",
};

const typeLabels = {
  full_time: "Full-time", part_time: "Part-time",
  contract: "Contract", internship: "Internship", remote: "Remote",
};

export default function Recruiter() {
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState("");
  const queryClient = useQueryClient();

  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => jobsApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: (data) => jobsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setForm(emptyForm);
      setError("");
    },
    onError: (err) => {
      setError(err?.detail || err?.title?.[0] || "Failed to post job. Please try again.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => jobsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
  });

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const postJob = () => {
    if (!form.title || !form.company || !form.description) {
      setError("Please fill job title, company, and description.");
      return;
    }
    setError("");
    const payload = {
      title: form.title,
      company: form.company,
      location: form.location,
      job_type: form.job_type,
      description: form.description,
      ...(form.salary_min && { salary_min: parseInt(form.salary_min) }),
      ...(form.salary_max && { salary_max: parseInt(form.salary_max) }),
    };
    createMutation.mutate(payload);
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Recruiter Portal</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <Briefcase className="w-8 h-8 text-primary" />
          Recruiter Dashboard
        </h1>
        <p className="text-muted-foreground mt-2">Post jobs and manage your opportunities.</p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 space-y-5 mb-8">
        <h2 className="text-xl font-bold">Post a New Job</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
          <Input
            placeholder="Min Salary (USD/month)"
            value={form.salary_min}
            onChange={(e) => update("salary_min", e.target.value)}
            type="number"
            min="0"
          />
          <Input
            placeholder="Max Salary (USD/month)"
            value={form.salary_max}
            onChange={(e) => update("salary_max", e.target.value)}
            type="number"
            min="0"
          />
        </div>

        <Textarea
          placeholder="Job Description *"
          rows={5}
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
        />

        {error && (
          <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        <Button onClick={postJob} disabled={createMutation.isPending}>
          {createMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
          {createMutation.isPending ? "Posting..." : "Post Job"}
        </Button>
      </div>

      <div>
        <h2 className="text-xl font-bold mb-4">Posted Jobs</h2>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
        ) : jobs.length === 0 ? (
          <div className="bg-card border border-border rounded-xl p-6 text-muted-foreground">
            No jobs posted yet.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job) => (
              <div key={job.id} className="bg-card border border-border rounded-xl p-5">
                <div className="flex justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-bold">{job.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {job.company} {job.location ? `• ${job.location}` : ""}
                    </p>
                  </div>
                  <button
                    onClick={() => deleteMutation.mutate(job.id)}
                    className="text-muted-foreground hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex gap-2 mt-4 text-xs">
                  <span className="px-3 py-1 rounded-full bg-primary/10 text-primary">
                    {typeLabels[job.job_type] || job.job_type}
                  </span>
                  {(job.salary_min || job.salary_max) && (
                    <span className="px-3 py-1 rounded-full bg-secondary">
                      {job.salary_min && job.salary_max
                        ? `$${job.salary_min}–$${job.salary_max}/mo`
                        : job.salary_min
                        ? `From $${job.salary_min}/mo`
                        : `Up to $${job.salary_max}/mo`}
                    </span>
                  )}
                </div>

                <p className="text-sm text-muted-foreground mt-4 line-clamp-3">{job.description}</p>
                <p className="text-xs text-muted-foreground mt-4">
                  Posted: {new Date(job.created_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
