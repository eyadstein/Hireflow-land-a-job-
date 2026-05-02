import React, { useState } from "react";
import { base44 } from "@/api/base44Client";
import { motion, AnimatePresence } from "framer-motion";
import { Users, Loader2, MessageSquare, ChevronRight, RotateCcw, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import PageHeader from "@/components/shared/PageHeader";

export default function Interview() {
  const [role, setRole] = useState("");
  const [questions, setQuestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeQuestion, setActiveQuestion] = useState(null);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [feedbackLoading, setFeedbackLoading] = useState(false);

  const generateQuestions = async () => {
    if (!role) return;
    setLoading(true);
    setQuestions(null);
    setActiveQuestion(null);
    setFeedback(null);
    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `Generate 6 realistic interview questions for a ${role} position. Include a mix of behavioral, technical, and situational questions.`,
      response_json_schema: {
        type: "object",
        properties: {
          questions: {
            type: "array",
            items: {
              type: "object",
              properties: {
                question: { type: "string" },
                category: { type: "string", description: "behavioral, technical, or situational" },
                difficulty: { type: "string", description: "easy, medium, or hard" },
              },
            },
          },
        },
      },
    });
    setQuestions(result.questions || []);
    setLoading(false);
  };

  const getFeedback = async (question) => {
    if (!answer.trim()) return;
    setFeedbackLoading(true);
    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `Evaluate this interview answer:
Question: ${question}
Role: ${role}
Answer: ${answer}

Provide constructive feedback.`,
      response_json_schema: {
        type: "object",
        properties: {
          score: { type: "number", description: "Score 1-10" },
          feedback: { type: "string" },
          improved_answer: { type: "string", description: "A stronger version of the answer" },
        },
      },
    });
    setFeedback(result);
    setFeedbackLoading(false);
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1400px]">
      <PageHeader
        eyebrow="AI Tools"
        title="Interview Prep"
        description="Practice with AI-generated questions and get instant feedback."
      />

      {/* Role Input */}
      <div className="flex gap-3 mb-8">
        <Input
          value={role}
          onChange={(e) => setRole(e.target.value)}
          placeholder="Enter the role you're preparing for..."
          className="bg-card flex-1"
        />
        <Button onClick={generateQuestions} disabled={!role || loading}>
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Users className="w-4 h-4 mr-2" />}
          Generate
        </Button>
      </div>

      {/* Questions */}
      {questions && (
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Question List */}
          <div className="lg:col-span-2 space-y-2">
            {questions.map((q, i) => (
              <motion.button
                key={i}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => { setActiveQuestion(q); setAnswer(""); setFeedback(null); }}
                className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${
                  activeQuestion === q
                    ? "border-primary/30 bg-primary/5"
                    : "border-border bg-card hover:border-primary/15"
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-xs font-mono text-muted-foreground mt-0.5">{String(i + 1).padStart(2, "0")}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground line-clamp-2">{q.question}</p>
                    <div className="flex gap-2 mt-1.5">
                      <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-secondary px-1.5 py-0.5 rounded">
                        {q.category}
                      </span>
                      <span className="text-[10px] uppercase tracking-wider text-muted-foreground bg-secondary px-1.5 py-0.5 rounded">
                        {q.difficulty}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0 mt-0.5" />
                </div>
              </motion.button>
            ))}
          </div>

          {/* Answer & Feedback */}
          <div className="lg:col-span-3">
            {!activeQuestion ? (
              <div className="bg-card border border-border rounded-xl p-12 text-center h-full flex flex-col items-center justify-center">
                <MessageSquare className="w-10 h-10 text-muted-foreground/30 mb-3" />
                <p className="text-sm text-muted-foreground">Select a question to practice</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-card border border-border rounded-xl p-6">
                  <p className="text-base font-medium text-foreground leading-relaxed mb-4">{activeQuestion.question}</p>
                  <Textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="Type your answer here..."
                    rows={6}
                    className="mb-3"
                  />
                  <Button onClick={() => getFeedback(activeQuestion.question)} disabled={!answer.trim() || feedbackLoading} className="w-full">
                    {feedbackLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
                    {feedbackLoading ? "Evaluating..." : "Get Feedback"}
                  </Button>
                </div>

                <AnimatePresence>
                  {feedback && (
                    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="bg-card border border-border rounded-xl p-6 space-y-4">
                      <div className="flex items-center gap-3">
                        <div className="text-3xl font-bold font-display text-foreground">{feedback.score}<span className="text-lg text-muted-foreground">/10</span></div>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed">{feedback.feedback}</p>
                      {feedback.improved_answer && (
                        <div>
                          <h4 className="text-sm font-semibold mb-2">Stronger Answer</h4>
                          <p className="text-sm text-muted-foreground bg-secondary/50 p-4 rounded-lg leading-relaxed">{feedback.improved_answer}</p>
                        </div>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}