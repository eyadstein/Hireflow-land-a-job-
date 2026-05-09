import { useMemo, useState } from "react";
import { callAI } from "@/lib/ai";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Loader2, Users, ChevronLeft, ChevronRight, Sparkles, RotateCcw } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { motion, AnimatePresence } from "framer-motion";

const questionBank = {
  "Software Engineer": [
    "Tell me about a project where you solved a difficult technical problem.",
    "How do you debug an issue in production?",
    "Explain the difference between state and props in React.",
    "How do you improve performance in a web application?",
    "Describe a time you worked closely with a product or design team.",
  ],
  "Data Analyst": [
    "Walk me through your data analysis process.",
    "How do you clean messy data before analysis?",
    "Tell me about a dashboard or report you built.",
    "How do you explain data findings to non-technical stakeholders?",
    "Describe a time your analysis influenced a business decision.",
  ],
  "UI/UX Designer": [
    "How do you approach a new product design problem?",
    "Tell me about a time user research changed your design direction.",
    "How do you balance user needs with business goals?",
    "Walk me through your design process from wireframes to final UI.",
    "How do you handle design feedback from developers or product managers?",
  ],
};

export default function Interview() {
  const [selectedRole, setSelectedRole] = useState("Software Engineer");
  const [started, setStarted] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);

  const questions = useMemo(() => questionBank[selectedRole] || [], [selectedRole]);
  const currentQuestion = questions[questionIndex] || "";

  const startSession = () => {
    setStarted(true);
    setQuestionIndex(0);
    setAnswer("");
    setFeedback("");
  };

  const reset = () => {
    setStarted(false);
    setQuestionIndex(0);
    setAnswer("");
    setFeedback("");
  };

  const next = () => {
    if (questionIndex < questions.length - 1) {
      setQuestionIndex((p) => p + 1);
      setAnswer("");
      setFeedback("");
    }
  };

  const prev = () => {
    if (questionIndex > 0) {
      setQuestionIndex((p) => p - 1);
      setAnswer("");
      setFeedback("");
    }
  };

  const getAIFeedback = async () => {
    if (!answer.trim()) return;
    setLoading(true);
    setFeedback("");
    try {
      const prompt = `You are an interview coach.
Target role: ${selectedRole}
Interview question: ${currentQuestion}
Candidate answer: ${answer}

Evaluate the answer and provide:
1. A score out of 10
2. 3 strengths
3. 3 areas to improve
4. A stronger sample answer in 4–6 lines
5. 3 specific improvement tips

Keep it clear, practical, and professional.`;
      setFeedback(await callAI(prompt));
    } catch {
      setFeedback("Could not generate feedback. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-4xl">
      <PageHeader
        eyebrow="AI Tools"
        title="Interview Coach"
        description="Practice real questions for your target role and get instant AI feedback."
      />

      {!started ? (
        <div className="bg-card border border-border rounded-xl p-8 flex flex-col items-center gap-6 text-center">
          <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
            <Users className="w-8 h-8 text-primary" />
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-1">Choose your target role</h2>
            <p className="text-sm text-muted-foreground">You'll get 5 real interview questions with AI-scored feedback.</p>
          </div>
          <Select value={selectedRole} onValueChange={setSelectedRole}>
            <SelectTrigger className="w-64">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.keys(questionBank).map((role) => (
                <SelectItem key={role} value={role}>{role}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button size="lg" onClick={startSession}>
            Start Interview Session
          </Button>
        </div>
      ) : (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          {/* Header row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">{selectedRole}</Badge>
              <span className="text-sm text-muted-foreground">
                Question {questionIndex + 1} of {questions.length}
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={reset}>
              <RotateCcw className="w-4 h-4 mr-1.5" /> Change Role
            </Button>
          </div>

          {/* Progress dots */}
          <div className="flex gap-1.5">
            {questions.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 flex-1 rounded-full transition-all ${
                  i === questionIndex ? "bg-primary" : i < questionIndex ? "bg-primary/40" : "bg-secondary"
                }`}
              />
            ))}
          </div>

          {/* Question */}
          <div className="bg-card border border-border rounded-xl p-6">
            <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Question</p>
            <p className="text-base font-medium leading-relaxed">{currentQuestion}</p>
          </div>

          {/* Answer */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Your Answer</label>
            <Textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Answer naturally, as you would in a real interview..."
              rows={5}
              className="bg-card resize-none"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={prev} disabled={questionIndex === 0 || loading}>
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={next} disabled={questionIndex === questions.length - 1 || loading}>
              <ChevronRight className="w-4 h-4" />
            </Button>
            <Button className="flex-1" onClick={getAIFeedback} disabled={!answer.trim() || loading}>
              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
              {loading ? "Generating feedback…" : "Get AI Feedback"}
            </Button>
          </div>

          {/* Feedback */}
          <AnimatePresence>
            {feedback && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="bg-card border border-border rounded-xl p-6"
              >
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-4 h-4 text-primary" />
                  <span className="text-sm font-semibold">AI Feedback</span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{feedback}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </div>
  );
}
