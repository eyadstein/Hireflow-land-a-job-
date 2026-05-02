import React, { useEffect, useState } from "react";
import { Briefcase, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function Recruiter() {
  const [jobs, setJobs] = useState([]);
  const [form, setForm] = useState({
    title: "",
    company: "",
    location: "",
    type: "Full-time",
    salary: "",
    description: "",
  });

  useEffect(() => {
    const saved = localStorage.getItem("postedJobs");
    if (saved) setJobs(JSON.parse(saved));
  }, []);

  const update = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const postJob = () => {
    if (!form.title || !form.company || !form.description) {
      alert("Please fill job title, company, and description.");
      return;
    }

    const newJob = {
      id: Date.now(),
      ...form,
      createdAt: new Date().toLocaleDateString(),
    };

    const updatedJobs = [newJob, ...jobs];
    setJobs(updatedJobs);
    localStorage.setItem("postedJobs", JSON.stringify(updatedJobs));

    setForm({
      title: "",
      company: "",
      location: "",
      type: "Full-time",
      salary: "",
      description: "",
    });
  };

  const deleteJob = (id) => {
    const updatedJobs = jobs.filter((job) => job.id !== id);
    setJobs(updatedJobs);
    localStorage.setItem("postedJobs", JSON.stringify(updatedJobs));
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
          Recruiter Portal
        </p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <Briefcase className="w-8 h-8 text-primary" />
          Recruiter Dashboard
        </h1>
        <p className="text-muted-foreground mt-2">
          Post jobs and manage your opportunities.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 space-y-5 mb-8">
        <h2 className="text-xl font-bold">Post a New Job</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            placeholder="Job Title"
            value={form.title}
            onChange={(e) => update("title", e.target.value)}
          />

          <Input
            placeholder="Company Name"
            value={form.company}
            onChange={(e) => update("company", e.target.value)}
          />

          <Input
            placeholder="Location"
            value={form.location}
            onChange={(e) => update("location", e.target.value)}
          />

          <select
            value={form.type}
            onChange={(e) => update("type", e.target.value)}
            className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          >
            <option>Full-time</option>
            <option>Part-time</option>
            <option>Internship</option>
            <option>Remote</option>
            <option>Hybrid</option>
          </select>

          <Input
            placeholder="Salary / Range"
            value={form.salary}
            onChange={(e) => update("salary", e.target.value)}
          />
        </div>

        <Textarea
          placeholder="Job Description"
          rows={5}
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
        />

        <Button onClick={postJob}>
          <Plus className="w-4 h-4 mr-2" />
          Post Job
        </Button>
      </div>

      <div>
        <h2 className="text-xl font-bold mb-4">Posted Jobs</h2>

        {jobs.length === 0 ? (
          <div className="bg-card border border-border rounded-xl p-6 text-muted-foreground">
            No jobs posted yet.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="bg-card border border-border rounded-xl p-5"
              >
                <div className="flex justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-bold">{job.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {job.company} • {job.location || "No location"}
                    </p>
                  </div>

                  <button
                    onClick={() => deleteJob(job.id)}
                    className="text-muted-foreground hover:text-red-500"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="flex gap-2 mt-4 text-xs">
                  <span className="px-3 py-1 rounded-full bg-primary/10 text-primary">
                    {job.type}
                  </span>
                  {job.salary && (
                    <span className="px-3 py-1 rounded-full bg-secondary">
                      {job.salary}
                    </span>
                  )}
                </div>

                <p className="text-sm text-muted-foreground mt-4 line-clamp-3">
                  {job.description}
                </p>

                <p className="text-xs text-muted-foreground mt-4">
                  Posted: {job.createdAt}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}