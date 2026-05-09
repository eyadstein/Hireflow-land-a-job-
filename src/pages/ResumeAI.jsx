import { useState } from "react";
import { callAI } from "@/lib/ai";
import { loadJobs } from "@/lib/loadJobs";
import { recommendJobs } from "@/lib/jobRecommender";
import { calculateATS } from "@/lib/atsEngine";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Loader2, Upload, Sparkles, FileText, CheckCircle2, XCircle } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { motion, AnimatePresence } from "framer-motion";

export default function ResumeAI() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const extractText = async () => {
    if (!file) throw new Error("No file selected");
    const formData = new FormData();
    formData.append("file", file);
    const token = localStorage.getItem("access_token");
    const res = await fetch("/api/ai/extract-text/", {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || "File extraction failed");
    }
    const data = await res.json();
    return data.text || "";
  };

  const analyze = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const resumeText = await extractText();
      if (!resumeText.trim()) throw new Error("Could not extract text from file");

      const jobs = await loadJobs();
      if (!Array.isArray(jobs) || jobs.length === 0) throw new Error("Jobs dataset unavailable");

      const topJobs = recommendJobs(resumeText, jobs);
      const scoredJobs = topJobs.map((job) => {
        const ats = calculateATS(resumeText, job);
        return { ...job, atsScore: ats.score, matchedSkills: ats.matched, missingSkills: ats.missing };
      });

      const advice = await callAI(`You are an ATS recruiter expert.

Resume:
${resumeText}

Top job matches:
${JSON.stringify(scoredJobs.map(j => ({ title: j.title, atsScore: j.atsScore, matchedSkills: j.matchedSkills, missingSkills: j.missingSkills })), null, 2)}

Tasks:
1. Explain the ATS scores briefly.
2. Why these jobs match this resume.
3. Give 5 practical resume improvement tips.
Keep it structured and concise.`);

      setResult({ jobs: scoredJobs, advice });
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score) =>
    score >= 70 ? "text-emerald-500" : score >= 40 ? "text-amber-500" : "text-red-500";

  return (
    <div className="p-8 lg:p-12 w-full max-w-4xl">
      <PageHeader
        eyebrow="AI Tools"
        title="Resume Analyzer"
        description="Upload your CV to get ATS scores, job matches, and AI improvement tips."
      />

      {/* Upload card */}
      <div className="bg-card border border-border rounded-xl p-8 flex flex-col items-center gap-5 text-center mb-6">
        <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
          <FileText className="w-8 h-8 text-primary" />
        </div>
        <div>
          <h2 className="font-semibold mb-1">Upload your resume</h2>
          <p className="text-sm text-muted-foreground">Supports PDF, DOCX, and TXT files</p>
        </div>

        <label className="cursor-pointer w-full max-w-xs">
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => { setFile(e.target.files[0] || null); setResult(null); setError(""); }}
            className="hidden"
          />
          <div className={`border-2 border-dashed rounded-xl px-6 py-4 transition-colors ${
            file ? "border-primary/40 bg-primary/5" : "border-border hover:border-primary/30"
          }`}>
            {file ? (
              <div className="flex items-center gap-2 justify-center text-sm">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span className="font-medium truncate max-w-[200px]">{file.name}</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 justify-center text-sm text-muted-foreground">
                <Upload className="w-4 h-4" />
                <span>Click to choose file</span>
              </div>
            )}
          </div>
        </label>

        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}

        <Button onClick={analyze} disabled={!file || loading} className="w-full max-w-xs">
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
          {loading ? "Analyzing…" : "Analyze Resume"}
        </Button>
      </div>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            {/* Job matches */}
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-sm font-semibold mb-4">Top Job Matches</h3>
              <div className="space-y-3">
                {result.jobs.map((job, i) => (
                  <div key={i} className="flex items-start justify-between gap-4 p-4 bg-secondary/30 rounded-lg">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">{job.title}</p>
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {job.matchedSkills?.slice(0, 4).map((s, j) => (
                          <Badge key={j} className="bg-emerald-500/10 text-emerald-600 border-emerald-500/20 text-[10px]">{s}</Badge>
                        ))}
                        {job.missingSkills?.slice(0, 3).map((s, j) => (
                          <Badge key={j} className="bg-red-500/10 text-red-600 border-red-500/20 text-[10px]">{s}</Badge>
                        ))}
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <p className={`text-xl font-bold ${scoreColor(job.atsScore)}`}>{job.atsScore}</p>
                      <p className="text-[10px] text-muted-foreground">ATS Score</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Feedback */}
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <Sparkles className="w-4 h-4 text-primary" />
                <span className="text-sm font-semibold">AI Analysis & Tips</span>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{result.advice}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
