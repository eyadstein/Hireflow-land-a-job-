import { useState } from "react";
import { callAI } from "@/lib/ai";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Loader2, DollarSign, Sparkles } from "lucide-react";
import PageHeader from "@/components/shared/PageHeader";
import { motion, AnimatePresence } from "framer-motion";

export default function Salary() {
  const [jobRole, setJobRole] = useState("");
  const [country, setCountry] = useState("Egypt");
  const [experience, setExperience] = useState("mid");
  const [aiAdvice, setAiAdvice] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleEstimate = async () => {
    if (!jobRole.trim()) return;
    setLoading(true);
    setDone(false);
    setAiAdvice("");
    try {
      const prompt = `You are an expert salary advisor for the Arab world job market.

Job: ${jobRole}
Country: ${country}
Experience: ${experience}

Provide:
1. Estimated monthly salary range (min, average, max) in both USD and local currency
2. Key market factors affecting this salary
3. 3–4 practical salary negotiation tips for this role

Be specific, realistic, and professional.`;
      setAiAdvice(await callAI(prompt));
      setDone(true);
    } catch {
      setAiAdvice("Could not generate estimate. Please try again.");
      setDone(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-3xl">
      <PageHeader
        eyebrow="Research"
        title="Salary Estimator"
        description="Get AI-powered salary estimates and negotiation tips for any role in the Arab world."
      />

      <div className="bg-card border border-border rounded-xl p-6 space-y-5">
        <div className="space-y-1.5">
          <label className="text-sm font-medium">Job Role *</label>
          <Input
            value={jobRole}
            onChange={(e) => setJobRole(e.target.value)}
            placeholder="e.g. Senior React Developer"
            onKeyDown={(e) => e.key === "Enter" && handleEstimate()}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="text-sm font-medium">Country</label>
            <Select value={country} onValueChange={setCountry}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                {["Egypt", "UAE", "Saudi Arabia", "Jordan", "Kuwait", "Qatar", "Bahrain", "Oman"].map((c) => (
                  <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Experience Level</label>
            <Select value={experience} onValueChange={setExperience}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="junior">Junior (0–2 yrs)</SelectItem>
                <SelectItem value="mid">Mid (2–5 yrs)</SelectItem>
                <SelectItem value="senior">Senior (5+ yrs)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <Button onClick={handleEstimate} disabled={!jobRole.trim() || loading} className="w-full">
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <DollarSign className="w-4 h-4 mr-2" />}
          {loading ? "Estimating…" : "Get Salary Estimate"}
        </Button>
      </div>

      <AnimatePresence>
        {done && aiAdvice && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 bg-card border border-border rounded-xl p-6"
          >
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-4 h-4 text-primary" />
              <h3 className="font-semibold">
                {jobRole} · {country} · {experience}
              </h3>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">{aiAdvice}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
