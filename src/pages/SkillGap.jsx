import { useState } from "react";
import { callAI } from "@/lib/ai";
import { motion, AnimatePresence } from "framer-motion";
import { Target, CheckCircle2, XCircle, AlertCircle, BookOpen, Loader2, ChevronRight, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import PageHeader from "@/components/shared/PageHeader";

function ScoreRing({ score }) {
  const color = score >= 75 ? "text-green-500" : score >= 50 ? "text-yellow-500" : "text-red-500";
  const label = score >= 75 ? "Strong Match" : score >= 50 ? "Partial Match" : "Weak Match";
  return (
    <div className="flex flex-col items-center gap-1">
      <div className={`text-6xl font-bold ${color}`}>{score}</div>
      <div className="text-sm text-muted-foreground">/ 100</div>
      <div className={`text-sm font-semibold mt-1 ${color}`}>{label}</div>
    </div>
  );
}

function TagList({ items, variant }) {
  const styles = {
    green:  "bg-green-500/10 text-green-600 border-green-500/20",
    red:    "bg-red-500/10 text-red-600 border-red-500/20",
    yellow: "bg-yellow-500/10 text-yellow-600 border-yellow-500/20",
  };
  if (!items?.length) return <p className="text-sm text-muted-foreground">None identified.</p>;
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item, i) => (
        <span key={i} className={`text-xs font-medium px-2.5 py-1 rounded-full border ${styles[variant]}`}>{item}</span>
      ))}
    </div>
  );
}

export default function SkillGap() {
  const [resumeTab, setResumeTab] = useState("paste");
  const [resumeText, setResumeText] = useState("");
  const [jobDesc, setJobDesc]       = useState("");
  const [loading, setLoading]       = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [error, setError]           = useState("");
  const [result, setResult]         = useState(null);

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
      if (!res.ok) throw new Error();
      const data = await res.json();
      setResumeText(data.text || "");
    } catch {
      setError("Could not extract text. Make sure Django backend is running.");
    } finally {
      setExtracting(false);
    }
  };

  const analyze = async () => {
    if (!resumeText.trim() || !jobDesc.trim()) {
      setError("Both resume and job description are required.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const prompt = `You are an expert skill gap analyst.
Compare the candidate's resume against the job description and return ONLY a JSON object:
{
  "matchScore": <0-100>,
  "matchedSkills": ["<skill1>", "<skill2>"],
  "missingSkills": ["<skill1>", "<skill2>"],
  "weakSkills": ["<skill1>"],
  "recommendations": ["<tip1>", "<tip2>", "<tip3>"],
  "summary": "<2-3 sentence assessment>"
}

Resume:
${resumeText}

Job Description:
${jobDesc}

Return ONLY the JSON, no markdown.`;

      const raw = await callAI(prompt);
      const clean = raw.replace(/```json/g, "").replace(/```/g, "").trim();
      setResult(JSON.parse(clean));
    } catch {
      setError("Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 lg:p-12 max-w-5xl">
      <PageHeader
        eyebrow="AI Analysis"
        title="Skill Gap Analyzer"
        description="Upload or paste your resume and a job description to see exactly which skills you're missing."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Resume side */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Your Resume</label>
            <div className="flex gap-1">
              {["paste", "file"].map((t) => (
                <button
                  key={t}
                  onClick={() => setResumeTab(t)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all capitalize ${
                    resumeTab === t ? "bg-foreground text-background" : "bg-secondary text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {resumeTab === "paste" ? (
            <Textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your full resume text here..."
              rows={12}
              className="bg-card resize-none font-mono text-xs"
            />
          ) : (
            <div className="bg-card border border-border rounded-xl p-8 flex flex-col items-center justify-center gap-3 min-h-[280px]">
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

        {/* Job description side */}
        <div className="space-y-2">
          <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Job Description</label>
          <Textarea
            value={jobDesc}
            onChange={(e) => setJobDesc(e.target.value)}
            placeholder="Paste the target job description here..."
            rows={12}
            className="bg-card resize-none font-mono text-xs"
          />
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">{error}</div>
      )}

      <Button onClick={analyze} disabled={loading || extracting} className="mb-10">
        {loading ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Analyzing…</> : <><Target className="w-4 h-4 mr-2" /> Analyze Skill Gap</>}
      </Button>

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <div className="bg-card border border-border rounded-xl p-8 flex flex-col items-center gap-4">
              <ScoreRing score={result.matchScore} />
              {result.summary && (
                <p className="text-sm text-muted-foreground text-center max-w-xl mt-2">{result.summary}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                  <span className="text-sm font-semibold">Matched</span>
                  <span className="ml-auto text-xs text-muted-foreground">{result.matchedSkills?.length || 0}</span>
                </div>
                <TagList items={result.matchedSkills} variant="green" />
              </div>
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <XCircle className="w-4 h-4 text-red-500" />
                  <span className="text-sm font-semibold">Missing</span>
                  <span className="ml-auto text-xs text-muted-foreground">{result.missingSkills?.length || 0}</span>
                </div>
                <TagList items={result.missingSkills} variant="red" />
              </div>
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <AlertCircle className="w-4 h-4 text-yellow-500" />
                  <span className="text-sm font-semibold">Needs Work</span>
                  <span className="ml-auto text-xs text-muted-foreground">{result.weakSkills?.length || 0}</span>
                </div>
                <TagList items={result.weakSkills} variant="yellow" />
              </div>
            </div>

            {result.recommendations?.length > 0 && (
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center gap-2 mb-4">
                  <BookOpen className="w-4 h-4 text-primary" />
                  <span className="text-sm font-semibold">Recommendations</span>
                </div>
                <ul className="space-y-2">
                  {result.recommendations.map((rec, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <ChevronRight className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
