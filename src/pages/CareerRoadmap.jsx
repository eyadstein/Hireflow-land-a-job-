import React, { useState } from "react";
import { callAI } from "@/lib/ai";
import { motion, AnimatePresence } from "framer-motion";
import {
  Map, Loader2, ChevronRight, Clock, CheckCircle2, BookOpen, TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import PageHeader from "@/components/shared/PageHeader";

export default function CareerRoadmap() {
  const [form, setForm] = useState({
    current_role: "",
    target_role:  "",
    experience:   "",
    skills:       "",
  });
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);
  const [result,  setResult]  = useState(null);

  const set = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }));

  const generate = async () => {
    if (!form.current_role.trim() || !form.target_role.trim()) {
      setError("Current role and target role are required.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const prompt = `You are an expert career coach specializing in the Arab world tech job market.
Create a detailed career roadmap for:
- Current Role: ${form.current_role}
- Target Role: ${form.target_role}
- Experience Level: ${form.experience || "Not specified"}
- Current Skills: ${form.skills || "Not specified"}

Return ONLY a JSON object:
{
  "timeline": "<total estimated timeline>",
  "overview": "<2-3 sentence summary>",
  "phases": [
    {
      "phase": 1,
      "title": "<phase title>",
      "duration": "<e.g. 2 months>",
      "skills": ["<skill1>", "<skill2>"],
      "resources": ["<resource1>", "<resource2>"],
      "milestone": "<what they achieve>"
    }
  ],
  "tips": ["<tip1>", "<tip2>", "<tip3>"],
  "marketInsight": "<1-2 sentences about Arab market demand>"
}
Return ONLY the JSON, no markdown.`;

      const raw = await callAI(prompt);
      const clean = raw.replace(/```json/g, "").replace(/```/g, "").trim();
      const data = JSON.parse(clean);
      setResult(data);
    } catch (e) {
      setError("Generation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 lg:p-12 max-w-4xl">
      <PageHeader
        eyebrow="AI Planning"
        title="Career Roadmap"
        description="Get a personalized step-by-step plan to reach your dream role."
      />

      <div className="bg-card border border-border rounded-xl p-6 mb-8 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Current Role *
            </label>
            <Input
              value={form.current_role}
              onChange={set("current_role")}
              placeholder="e.g. Junior Frontend Developer"
              className="bg-background"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Target Role *
            </label>
            <Input
              value={form.target_role}
              onChange={set("target_role")}
              placeholder="e.g. Senior Full-Stack Engineer"
              className="bg-background"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Experience Level
            </label>
            <Input
              value={form.experience}
              onChange={set("experience")}
              placeholder="e.g. 1 year, Junior, Fresh Graduate"
              className="bg-background"
            />
          </div>
          <div className="space-y-1.5">
            <label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Current Skills
            </label>
            <Input
              value={form.skills}
              onChange={set("skills")}
              placeholder="e.g. React, JavaScript, HTML/CSS"
              className="bg-background"
            />
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
            {error}
          </div>
        )}

        <Button onClick={generate} disabled={loading}>
          {loading ? (
            <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating…</>
          ) : (
            <><Map className="w-4 h-4 mr-2" /> Generate Roadmap</>
          )}
        </Button>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Overview */}
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp className="w-5 h-5 text-primary" />
                <span className="font-semibold">Overview</span>
                {result.timeline && (
                  <span className="ml-auto flex items-center gap-1 text-sm text-muted-foreground">
                    <Clock className="w-3.5 h-3.5" /> {result.timeline}
                  </span>
                )}
              </div>
              {result.overview && (
                <p className="text-sm text-muted-foreground leading-relaxed">{result.overview}</p>
              )}
              {result.marketInsight && (
                <p className="text-sm text-primary/80 mt-2 italic">{result.marketInsight}</p>
              )}
            </div>

            {/* Phases */}
            {result.phases?.length > 0 && (
              <div className="space-y-4">
                <h2 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Learning Phases
                </h2>
                {result.phases.map((phase) => (
                  <motion.div
                    key={phase.phase}
                    initial={{ opacity: 0, x: -12 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: phase.phase * 0.1 }}
                    className="bg-card border border-border rounded-xl p-5"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center shrink-0 text-primary font-bold text-sm">
                        {phase.phase}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-sm">{phase.title}</h3>
                          {phase.duration && (
                            <span className="text-xs text-muted-foreground flex items-center gap-1">
                              <Clock className="w-3 h-3" /> {phase.duration}
                            </span>
                          )}
                        </div>
                        {phase.milestone && (
                          <p className="text-xs text-muted-foreground mb-3 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3 text-green-500 shrink-0" />
                            {phase.milestone}
                          </p>
                        )}
                        {phase.skills?.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 mb-3">
                            {phase.skills.map((s, i) => (
                              <span key={i} className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                                {s}
                              </span>
                            ))}
                          </div>
                        )}
                        {phase.resources?.length > 0 && (
                          <div className="space-y-1">
                            {phase.resources.map((r, i) => (
                              <div key={i} className="flex items-center gap-1.5 text-xs text-muted-foreground">
                                <BookOpen className="w-3 h-3 shrink-0" /> {r}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Tips */}
            {result.tips?.length > 0 && (
              <div className="bg-card border border-border rounded-xl p-5">
                <h3 className="text-sm font-semibold mb-3">Pro Tips</h3>
                <ul className="space-y-2">
                  {result.tips.map((tip, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                      <ChevronRight className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                      {tip}
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
