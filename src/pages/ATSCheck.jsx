import { useState } from "react";
import { calculateATS } from "@/lib/atsEngine";
import { callAI } from "@/lib/ai";
import { processJob } from "@/lib/jobProcessor";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Loader2, ScanSearch, Sparkles, CheckCircle2, XCircle, Upload } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { motion, AnimatePresence } from "framer-motion";

export default function ATSCheck() {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [tab, setTab] = useState("paste");
  const [atsResult, setAtsResult] = useState(null);
  const [aiFeedback, setAiFeedback] = useState("");
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState("");

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      setExtracting(true);
      setError("");
      const token = localStorage.getItem("access_token");
      const res = await fetch("/api/ai/extract-text/", {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });
      if (!res.ok) throw new Error("Extraction failed");
      const data = await res.json();
      setResumeText(data.text || "");
    } catch {
      setError("Could not extract text. Make sure Django backend is running.");
    } finally {
      setExtracting(false);
    }
  };

  const handleCheck = async () => {
    if (!resumeText.trim() || !jobDescription.trim()) {
      setError("Please provide both resume text and job description.");
      return;
    }
    setLoading(true);
    setError("");
    setAiFeedback("");
    try {
      const processedJob = processJob({
        job_title: "Target Job",
        job_description: jobDescription,
        requirements: jobDescription,
      });
      const result = calculateATS(resumeText, processedJob);
      setAtsResult(result);

      const prompt = `You are an ATS resume advisor.

Resume:
${resumeText}

Job Description:
${jobDescription}

ATS Score: ${result.score}/100
Matched Skills: ${result.matched.join(", ") || "None"}
Missing Skills: ${result.missing.join(", ") || "None"}

Give:
1. A short evaluation of the fit
2. The most important missing skills
3. 5 practical improvements to increase the ATS score

Keep it concise, clear, and professional.`;

      setAiFeedback(await callAI(prompt));
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor =
    atsResult?.score >= 70 ? "text-emerald-500" :
    atsResult?.score >= 40 ? "text-amber-500" :
    "text-red-500";

  return (
    <div className="p-8 lg:p-12 w-full max-w-5xl">
      <PageHeader
        eyebrow="AI Tools"
        title="ATS Score Checker"
        description="Check how well your resume matches a job description before you apply."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">Your Resume</label>
            <div className="flex gap-1">
              {["paste", "file"].map((t) => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all capitalize ${
                    tab === t ? "bg-foreground text-background" : "bg-secondary text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {tab === "paste" ? (
            <Textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your full resume text here..."
              rows={12}
              className="bg-card resize-none font-mono text-xs"
            />
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 flex flex-col items-center justify-center gap-3 min-h-[200px]">
              <Upload className="w-8 h-8 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">Upload PDF, DOCX, or TXT</p>
              <label className="cursor-pointer">
                <input type="file" accept=".pdf,.txt,.docx" onChange={handleFileUpload} className="hidden" />
                <span className="text-xs bg-secondary hover:bg-secondary/80 text-foreground px-4 py-2 rounded-lg transition-colors">
                  {extracting ? "Extracting…" : "Choose File"}
                </span>
              </label>
              {resumeText && (
                <p className="text-xs text-emerald-500">✓ Text extracted ({resumeText.length} chars)</p>
              )}
            </div>
          )}
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium">Job Description</label>
          <Textarea
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
            placeholder="Paste the job description here..."
            rows={12}
            className="bg-card resize-none font-mono text-xs"
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
          {error}
        </div>
      )}

      <Button onClick={handleCheck} disabled={loading || extracting} className="w-full mb-8">
        {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <ScanSearch className="w-4 h-4 mr-2" />}
        {loading ? "Checking…" : "Check ATS Score"}
      </Button>

      <AnimatePresence>
        {atsResult && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
            <div className="bg-card border border-border rounded-xl p-8 flex flex-col items-center gap-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">ATS Match Score</p>
              <p className={`text-7xl font-bold ${scoreColor}`}>{atsResult.score}</p>
              <p className="text-muted-foreground text-sm">/ 100</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                  <span className="text-sm font-semibold">Matched Skills</span>
                  <span className="ml-auto text-xs text-muted-foreground">{atsResult.matched.length}</span>
                </div>
                {atsResult.matched.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {atsResult.matched.map((s, i) => (
                      <Badge key={i} className="bg-emerald-500/10 text-emerald-600 border-emerald-500/20 text-xs">{s}</Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">No matched skills found.</p>
                )}
              </div>

              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <XCircle className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-semibold">Missing Skills</span>
                  <span className="ml-auto text-xs text-muted-foreground">{atsResult.missing.length}</span>
                </div>
                {atsResult.missing.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {atsResult.missing.map((s, i) => (
                      <Badge key={i} className="bg-red-500/10 text-red-600 border-red-500/20 text-xs">{s}</Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">No missing skills found.</p>
                )}
              </div>
            </div>

            {aiFeedback && (
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-4 h-4 text-primary" />
                  <span className="text-sm font-semibold">AI Feedback</span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{aiFeedback}</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
