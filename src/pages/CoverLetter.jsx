import React, { useState } from "react";
import { callAI } from "@/lib/ai";
import { motion } from "framer-motion";
import { PenLine, Loader2, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import PageHeader from "@/components/shared/PageHeader";

export default function CoverLetter() {
  const [form, setForm] = useState({
    name: "",
    job_title: "",
    company: "",
    skills: "",
    job_description: "",
  });
  const [letter, setLetter] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const generate = async () => {
    if (!form.name || !form.job_title || !form.company) return;
    setLoading(true);
    setError("");
    try {
      const prompt = `Write a professional cover letter for the following:

Name: ${form.name}
Job Title: ${form.job_title}
Company: ${form.company}
Skills: ${form.skills || "Not specified"}
Job Description: ${form.job_description || "Not provided"}

Write a compelling, personalized cover letter that highlights the candidate's skills and fit for the role. Keep it concise (3-4 paragraphs), professional, and tailored to the company. Do not include placeholder text — write it as a complete, ready-to-send letter.`;

      const result = await callAI(prompt);
      setLetter(result);
    } catch (err) {
      setError("Generation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(letter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <PageHeader
        eyebrow="AI Tools"
        title="Cover Letter Generator"
        description="Create tailored cover letters in seconds."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <div className="space-y-4">
          <div className="bg-card border border-border rounded-xl p-6 space-y-4">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Your Name *</label>
              <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Ahmed Hassan" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Job Title *</label>
              <Input value={form.job_title} onChange={(e) => setForm({ ...form, job_title: e.target.value })} placeholder="e.g. Product Designer" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Company *</label>
              <Input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} placeholder="e.g. Stripe" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Your Skills</label>
              <Input value={form.skills} onChange={(e) => setForm({ ...form, skills: e.target.value })} placeholder="e.g. React, Node.js, Figma..." />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Job Description</label>
              <Textarea value={form.job_description} onChange={(e) => setForm({ ...form, job_description: e.target.value })} placeholder="Paste the job listing..." rows={4} />
            </div>
          </div>

          {error && (
            <div className="px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {error}
            </div>
          )}

          <Button onClick={generate} disabled={!form.name || !form.job_title || !form.company || loading} className="w-full">
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <PenLine className="w-4 h-4 mr-2" />}
            {loading ? "Generating..." : "Generate Cover Letter"}
          </Button>
        </div>

        {/* Output */}
        <div>
          {!letter && !loading && (
            <div className="bg-card border border-border rounded-xl p-12 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
              <PenLine className="w-12 h-12 text-muted-foreground/30 mb-4" />
              <p className="text-sm text-muted-foreground">Your cover letter will appear here</p>
            </div>
          )}

          {loading && (
            <div className="bg-card border border-border rounded-xl p-12 flex flex-col items-center justify-center h-full min-h-[400px]">
              <Loader2 className="w-10 h-10 text-primary animate-spin mb-4" />
              <p className="text-sm text-muted-foreground">Crafting your cover letter...</p>
            </div>
          )}

          {letter && !loading && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold">Generated Cover Letter</h3>
                  <Button variant="outline" size="sm" onClick={copyToClipboard}>
                    {copied ? <Check className="w-3.5 h-3.5 mr-1.5" /> : <Copy className="w-3.5 h-3.5 mr-1.5" />}
                    {copied ? "Copied" : "Copy"}
                  </Button>
                </div>
                <div className="prose prose-sm max-w-none text-muted-foreground leading-relaxed whitespace-pre-wrap bg-secondary/30 p-5 rounded-lg">
                  {letter}
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
