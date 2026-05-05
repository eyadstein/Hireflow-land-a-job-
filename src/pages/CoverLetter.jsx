import React, { useState } from "react";
import { base44 } from "@/api/base44Client";
import { motion } from "framer-motion";
import { PenLine, Loader2, Copy, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import PageHeader from "@/components/shared/PageHeader";

export default function CoverLetter() {
  const [form, setForm] = useState({
    jobTitle: "",
    company: "",
    jobDescription: "",
    experience: "",
    tone: "professional",
  });
  const [letter, setLetter] = useState("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const generate = async () => {
    if (!form.jobTitle || !form.company) return;
    setLoading(true);
    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `Write a compelling cover letter for the following:
Job Title: ${form.jobTitle}
Company: ${form.company}
Tone: ${form.tone}
${form.jobDescription ? `Job Description: ${form.jobDescription}` : ""}
${form.experience ? `Candidate Background: ${form.experience}` : ""}

Write a professional, personalized cover letter. Do not use placeholders like [Your Name]. Keep it concise (3-4 paragraphs).`,
    });
    setLetter(result);
    setLoading(false);
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
              <label className="text-sm font-medium mb-1.5 block">Job Title *</label>
              <Input value={form.jobTitle} onChange={(e) => setForm({ ...form, jobTitle: e.target.value })} placeholder="e.g. Product Designer" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Company *</label>
              <Input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} placeholder="e.g. Stripe" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Tone</label>
              <Select value={form.tone} onValueChange={(v) => setForm({ ...form, tone: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="professional">Professional</SelectItem>
                  <SelectItem value="friendly">Friendly</SelectItem>
                  <SelectItem value="confident">Confident</SelectItem>
                  <SelectItem value="creative">Creative</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Job Description</label>
              <Textarea value={form.jobDescription} onChange={(e) => setForm({ ...form, jobDescription: e.target.value })} placeholder="Paste the job listing..." rows={4} />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Your Background</label>
              <Textarea value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} placeholder="Briefly describe your experience..." rows={3} />
            </div>
          </div>

          <Button onClick={generate} disabled={!form.jobTitle || !form.company || loading} className="w-full">
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