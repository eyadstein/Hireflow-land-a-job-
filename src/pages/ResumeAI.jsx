import React, { useState } from "react";
import { base44 } from "@/api/base44Client";
import { motion } from "framer-motion";
import { Upload, Sparkles, FileText, Loader2, CheckCircle, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import PageHeader from "@/components/shared/PageHeader";

export default function ResumeAI() {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const { file_url } = await base44.integrations.Core.UploadFile({ file });
    const result = await base44.integrations.Core.ExtractDataFromUploadedFile({
      file_url,
      json_schema: { type: "object", properties: { text: { type: "string", description: "Full text content of the resume" } } },
    });
    if (result.status === "success") {
      setResumeText(result.output?.text || "");
    }
    setUploading(false);
  };

  const analyzeResume = async () => {
    if (!resumeText) return;
    setLoading(true);
    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `Analyze this resume against the job description. Provide actionable feedback.

Resume:
${resumeText}

${jobDescription ? `Job Description:\n${jobDescription}` : "No specific job description provided - give general optimization tips."}

Provide analysis in the following format.`,
      response_json_schema: {
        type: "object",
        properties: {
          overall_score: { type: "number", description: "Score 0-100" },
          ats_score: { type: "number", description: "ATS compatibility score 0-100" },
          summary: { type: "string", description: "2-3 sentence summary" },
          strengths: { type: "array", items: { type: "string" }, description: "Top 3 strengths" },
          improvements: { type: "array", items: { type: "string" }, description: "Top 3 improvements" },
          keywords_missing: { type: "array", items: { type: "string" }, description: "Missing keywords from job description" },
          rewritten_summary: { type: "string", description: "Optimized professional summary" },
        },
      },
    });
    setAnalysis(result);
    setLoading(false);
  };

  return (
    <div className="p-8 lg:p-15 w-full max-w-[1600px]">
      <PageHeader
        eyebrow="AI Tools"
        title="Resume Analyzer"
        description="Upload your resume and get AI-powered optimization suggestions."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input */}
        <div className="space-y-4">
          {/* Upload */}
          <div className="bg-card border border-border rounded-xl p-6">
            <label className="flex flex-col items-center justify-center py-8 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-primary/30 transition-colors">
              <input type="file" accept=".pdf,.doc,.docx,.txt" className="hidden" onChange={handleFileUpload} />
              {uploading ? (
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              ) : (
                <>
                  <Upload className="w-8 h-8 text-muted-foreground mb-2" />
                  <p className="text-sm font-medium text-foreground">Upload Resume</p>
                  <p className="text-xs text-muted-foreground mt-1">PDF, DOC, DOCX, or TXT</p>
                </>
              )}
            </label>
          </div>

          {/* Resume text */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Resume Content</label>
            <Textarea
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              placeholder="Paste your resume text here or upload a file..."
              rows={8}
              className="bg-card"
            />
          </div>

          {/* Job Description */}
          <div>
            <label className="text-sm font-medium mb-1.5 block">Target Job Description (optional)</label>
            <Textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description to get tailored analysis..."
              rows={5}
              className="bg-card"
            />
          </div>

          <Button onClick={analyzeResume} disabled={!resumeText || loading} className="w-full">
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
            {loading ? "Analyzing..." : "Analyze Resume"}
          </Button>
        </div>

        {/* Results */}
        <div>
          {!analysis && !loading && (
            <div className="bg-card border border-border rounded-xl p-12 flex flex-col items-center justify-center text-center h-full">
              <FileText className="w-12 h-12 text-muted-foreground/30 mb-4" />
              <p className="text-sm text-muted-foreground">Your analysis will appear here</p>
            </div>
          )}

          {loading && (
            <div className="bg-card border border-border rounded-xl p-12 flex flex-col items-center justify-center h-full">
              <Loader2 className="w-10 h-10 text-primary animate-spin mb-4" />
              <p className="text-sm text-muted-foreground">Analyzing your resume...</p>
            </div>
          )}

          {analysis && !loading && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              {/* Scores */}
              <div className="bg-card border border-border rounded-xl p-6">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">Overall Score</p>
                    <p className="text-3xl font-bold font-display text-foreground">{analysis.overall_score}</p>
                    <Progress value={analysis.overall_score} className="h-1.5 mt-2" />
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wider text-muted-foreground mb-1">ATS Score</p>
                    <p className="text-3xl font-bold font-display text-foreground">{analysis.ats_score}</p>
                    <Progress value={analysis.ats_score} className="h-1.5 mt-2" />
                  </div>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{analysis.summary}</p>
              </div>

              {/* Strengths */}
              <div className="bg-card border border-border rounded-xl p-6">
                <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                  <CheckCircle className="w-4 h-4 text-emerald-600" /> Strengths
                </h3>
                <ul className="space-y-2">
                  {analysis.strengths?.map((s, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex gap-2">
                      <span className="text-emerald-600 mt-0.5">•</span> {s}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Improvements */}
              <div className="bg-card border border-border rounded-xl p-6">
                <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
                  <AlertTriangle className="w-4 h-4 text-amber-600" /> Improvements
                </h3>
                <ul className="space-y-2">
                  {analysis.improvements?.map((s, i) => (
                    <li key={i} className="text-sm text-muted-foreground flex gap-2">
                      <span className="text-amber-600 mt-0.5">•</span> {s}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Rewritten Summary */}
              {analysis.rewritten_summary && (
                <div className="bg-card border border-border rounded-xl p-6">
                  <h3 className="text-sm font-semibold mb-3">Optimized Summary</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed bg-secondary/50 p-4 rounded-lg">
                    {analysis.rewritten_summary}
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}