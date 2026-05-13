import { useState, useEffect, useMemo } from "react";
import { ai, jobsLive, jobs as jobsApi } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Loader2, Upload, Sparkles, FileText, CheckCircle2, XCircle,
  AlertTriangle, Lightbulb, Target, User, TrendingUp,
  MapPin, Building2, ExternalLink, Briefcase,
} from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { motion, AnimatePresence } from "framer-motion";

const ratingColor = {
  Excellent: "text-emerald-600 bg-emerald-50 border-emerald-200",
  Good:      "text-blue-600   bg-blue-50   border-blue-200",
  Average:   "text-amber-600  bg-amber-50  border-amber-200",
  Poor:      "text-red-600    bg-red-50    border-red-200",
};

const priorityColor = {
  High:   "bg-red-50 border-red-200 text-red-700",
  Medium: "bg-amber-50 border-amber-200 text-amber-700",
  Low:    "bg-blue-50 border-blue-200 text-blue-700",
};

async function extractText(file) {
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
}

function scoreJob(job, keywords) {
  if (!keywords.length) return 50;
  const haystack = `${job.title ?? ""} ${job.description ?? ""}`.toLowerCase();
  const hits = keywords.filter((k) => haystack.includes(k.toLowerCase())).length;
  const raw = Math.round((hits / keywords.length) * 100);
  return Math.min(Math.max(raw + 30, 20), 98);
}

function MatchBar({ score }) {
  const bar   = score >= 70 ? "bg-emerald-500" : score >= 45 ? "bg-amber-500" : "bg-red-400";
  const label = score >= 70 ? "text-emerald-600" : score >= 45 ? "text-amber-600" : "text-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className={`h-full ${bar} rounded-full`}
        />
      </div>
      <span className={`text-xs font-semibold ${label} w-9 text-right`}>{score}%</span>
    </div>
  );
}

export default function ResumeAI() {
  const [file, setFile]           = useState(null);
  const [result, setResult]       = useState(null);
  const [loading, setLoading]     = useState(false);
  const [error, setError]         = useState("");

  const [topJobs, setTopJobs]         = useState([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [jobsError, setJobsError]     = useState("");

  // Fetch live jobs as soon as analysis result is ready
  useEffect(() => {
    if (!result) return;

    let cancelled = false;
    setJobsLoading(true);
    setJobsError("");
    setTopJobs([]);

    const keywords = [
      ...(result.missingKeywords ?? []),
      ...(result.strengths ?? []).flatMap((s) => s.split(/[\s,]+/)),
      ...(result.estimatedRole ?? "").split(/[\s,/]+/),
    ].map((k) => k.trim()).filter((k) => k.length > 2);

    async function fetchJobs() {
      try {
        // Fetch live external jobs + DB recruiter jobs in parallel
        const [liveRes, dbRes] = await Promise.allSettled([
          jobsLive.search({ q: "software developer", country: "egypt" }),
          jobsApi.list(),
        ]);

        if (cancelled) return;

        const liveJobs = liveRes.status === "fulfilled"
          ? (liveRes.value?.jobs ?? [])
          : [];

        const dbJobs = dbRes.status === "fulfilled"
          ? (dbRes.value ?? []).map((j) => ({
              id: `db-${j.id}`,
              title: j.title,
              company: j.company,
              location: j.location,
              description: j.description,
              apply_link: j.url || null,
              job_type: j.job_type,
              is_remote: j.job_type === "remote",
            }))
          : [];

        const all = [...liveJobs, ...dbJobs];

        if (all.length === 0) {
          setJobsError("No live jobs found. Make sure the Django server is running.");
          return;
        }

        const scored = all
          .map((job) => ({ ...job, matchScore: scoreJob(job, keywords) }))
          .sort((a, b) => b.matchScore - a.matchScore)
          .slice(0, 5);

        setTopJobs(scored);
      } catch (e) {
        if (!cancelled) setJobsError("Failed to load jobs: " + (e?.message || "server error"));
      } finally {
        if (!cancelled) setJobsLoading(false);
      }
    }

    fetchJobs();
    return () => { cancelled = true; };
  }, [result]);

  const analyze = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    setTopJobs([]);
    setJobsError("");
    try {
      const resumeText = await extractText(file);
      if (!resumeText.trim()) throw new Error("Could not extract text from file. Make sure it's a readable PDF or DOCX.");
      const data = await ai.analyzeResume({ resume_text: resumeText });
      if (data?.error) throw new Error(data.error);
      setResult(data);
    } catch (err) {
      setError(err.message || "Analysis failed. Check your GROQ_API_KEY in .env.local.");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (s) => s >= 70 ? "text-emerald-600" : s >= 40 ? "text-amber-600" : "text-red-600";
  const scoreBg    = (s) => s >= 70 ? "bg-emerald-500"   : s >= 40 ? "bg-amber-500"   : "bg-red-500";

  return (
    <div className="p-8 lg:p-12 w-full max-w-4xl">
      <PageHeader
        eyebrow="AI Tools"
        title="Resume Analyzer"
        description="Upload your CV to get an ATS score, keyword gaps, and top matching live jobs."
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
            onChange={(e) => { setFile(e.target.files[0] || null); setResult(null); setError(""); setTopJobs([]); setJobsError(""); }}
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

        {error && <p className="text-sm text-destructive max-w-xs">{error}</p>}

        <Button onClick={analyze} disabled={!file || loading} className="w-full max-w-xs">
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
          {loading ? "Analyzing…" : "Analyze Resume"}
        </Button>
      </div>

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">

            {/* Score banner */}
            <div className="bg-card border border-border rounded-xl p-6 flex flex-col sm:flex-row items-center gap-6">
              <div className="text-center shrink-0">
                <p className={`text-6xl font-black ${scoreColor(result.atsScore ?? 0)}`}>{result.atsScore ?? "—"}</p>
                <p className="text-xs text-muted-foreground mt-1">ATS Score</p>
                <div className="w-24 h-2 bg-muted rounded-full mt-2 overflow-hidden">
                  <div className={`h-full ${scoreBg(result.atsScore ?? 0)} rounded-full`} style={{ width: `${result.atsScore ?? 0}%` }} />
                </div>
              </div>
              <div className="flex-1">
                {result.overallRating && (
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border mb-2 ${ratingColor[result.overallRating] ?? "bg-secondary text-muted-foreground"}`}>
                    {result.overallRating}
                  </span>
                )}
                {result.summary && <p className="text-sm text-muted-foreground leading-relaxed">{result.summary}</p>}
                <div className="flex flex-wrap gap-3 mt-3 text-xs text-muted-foreground">
                  {result.estimatedRole && (
                    <span className="flex items-center gap-1"><Target className="w-3 h-3" /> {result.estimatedRole}</span>
                  )}
                  {result.experienceLevel && (
                    <span className="flex items-center gap-1"><User className="w-3 h-3" /> {result.experienceLevel}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Strengths & Weaknesses */}
            {(result.strengths?.length > 0 || result.weaknesses?.length > 0) && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {result.strengths?.length > 0 && (
                  <div className="bg-card border border-border rounded-xl p-5">
                    <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Strengths
                    </h3>
                    <ul className="space-y-2">
                      {result.strengths.map((s, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                          {s}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {result.weaknesses?.length > 0 && (
                  <div className="bg-card border border-border rounded-xl p-5">
                    <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                      <XCircle className="w-4 h-4 text-red-500" /> Weaknesses
                    </h3>
                    <ul className="space-y-2">
                      {result.weaknesses.map((w, i) => (
                        <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-400 mt-1.5 shrink-0" />
                          {w}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Missing Keywords */}
            {result.missingKeywords?.length > 0 && (
              <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-4 h-4 text-amber-500" /> Missing Keywords
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.missingKeywords.map((k, i) => (
                    <Badge key={i} variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 text-xs">{k}</Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            {result.suggestions?.length > 0 && (
              <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                  <Lightbulb className="w-4 h-4 text-primary" /> Improvement Suggestions
                </h3>
                <div className="space-y-3">
                  {result.suggestions.map((s, i) => (
                    <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border text-sm ${priorityColor[s.priority] ?? "bg-secondary border-border text-foreground"}`}>
                      <span className="font-semibold text-xs shrink-0 mt-0.5">{s.priority}</span>
                      <span>{s.tip}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── Top 5 Live Job Matches ── */}
            <div className="bg-card border border-border rounded-xl p-5">
              <h3 className="text-sm font-semibold flex items-center gap-2 mb-4">
                <TrendingUp className="w-4 h-4 text-primary" />
                Top 5 Live Job Matches
                {result.estimatedRole && (
                  <Badge variant="secondary" className="ml-1 text-[10px]">{result.estimatedRole}</Badge>
                )}
              </h3>

              {jobsLoading && (
                <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground py-6">
                  <Loader2 className="w-4 h-4 animate-spin" /> Matching against live jobs…
                </div>
              )}

              {!jobsLoading && jobsError && (
                <p className="text-sm text-destructive text-center py-6">{jobsError}</p>
              )}

              {!jobsLoading && !jobsError && topJobs.length === 0 && (
                <p className="text-sm text-muted-foreground text-center py-6">No jobs found.</p>
              )}

              {!jobsLoading && !jobsError && topJobs.length > 0 && (
                <div className="space-y-3">
                  {topJobs.map((job, i) => (
                    <motion.div
                      key={job.id ?? i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.07 }}
                      className="flex flex-col gap-2 p-4 rounded-lg border border-border bg-secondary/30 hover:bg-secondary/60 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2">
                            <span className="w-5 h-5 rounded-full bg-primary/10 text-primary text-[10px] font-bold flex items-center justify-center shrink-0">
                              {i + 1}
                            </span>
                            <p className="text-sm font-semibold truncate">{job.title}</p>
                          </div>
                          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1.5 text-xs text-muted-foreground">
                            {job.company && (
                              <span className="flex items-center gap-1"><Building2 className="w-3 h-3" /> {job.company}</span>
                            )}
                            {job.location && (
                              <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {job.location}</span>
                            )}
                            {job.job_type && (
                              <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" /> {job.job_type}</span>
                            )}
                            {job.is_remote && (
                              <Badge variant="outline" className="text-[10px] h-4 px-1.5 border-emerald-300 text-emerald-600">Remote</Badge>
                            )}
                          </div>
                        </div>
                        {job.apply_link && (
                          <a href={job.apply_link} target="_blank" rel="noopener noreferrer" className="shrink-0">
                            <Button size="sm" variant="outline" className="h-7 text-xs gap-1">
                              Apply <ExternalLink className="w-3 h-3" />
                            </Button>
                          </a>
                        )}
                      </div>
                      <MatchBar score={job.matchScore} />
                    </motion.div>
                  ))}
                </div>
              )}
            </div>

          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
