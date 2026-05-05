import React, { useState } from "react";
import { base44 } from "@/api/base44Client";
import { motion } from "framer-motion";
import { DollarSign, Loader2, Search, TrendingUp, Building2, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import PageHeader from "@/components/shared/PageHeader";

export default function Salary() {
  const [role, setRole] = useState("");
  const [location, setLocation] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const research = async () => {
    if (!role) return;
    setLoading(true);
    const result = await base44.integrations.Core.InvokeLLM({
      prompt: `Provide salary insights for the role: ${role}${location ? ` in ${location}` : ""}. Include market data, compensation ranges, and negotiation tips.`,
      add_context_from_internet: true,
      response_json_schema: {
        type: "object",
        properties: {
          role_title: { type: "string" },
          location: { type: "string" },
          salary_low: { type: "number", description: "Low end annual salary in USD" },
          salary_mid: { type: "number", description: "Median annual salary in USD" },
          salary_high: { type: "number", description: "High end annual salary in USD" },
          factors: { type: "array", items: { type: "string" }, description: "Key factors affecting salary" },
          negotiation_tips: { type: "array", items: { type: "string" }, description: "Top 3 negotiation tips" },
          market_outlook: { type: "string", description: "Brief market outlook for this role" },
        },
      },
    });
    setData(result);
    setLoading(false);
  };

  const formatSalary = (n) => {
    if (!n) return "N/A";
    return `$${(n / 1000).toFixed(0)}k`;
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <PageHeader
        eyebrow="Research"
        title="Salary Insights"
        description="Research market compensation and negotiate with confidence."
      />

      {/* Search */}
      <div className="flex flex-col sm:flex-row gap-3 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input value={role} onChange={(e) => setRole(e.target.value)} placeholder="Job title (e.g. Senior Software Engineer)" className="pl-9 bg-card" />
        </div>
        <div className="relative sm:w-48">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Location" className="pl-9 bg-card" />
        </div>
        <Button onClick={research} disabled={!role || loading}>
          {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <DollarSign className="w-4 h-4 mr-2" />}
          Research
        </Button>
      </div>

      {/* Results */}
      {loading && (
        <div className="bg-card border border-border rounded-xl p-16 flex flex-col items-center justify-center">
          <Loader2 className="w-10 h-10 text-primary animate-spin mb-4" />
          <p className="text-sm text-muted-foreground">Researching salary data...</p>
        </div>
      )}

      {data && !loading && (
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          {/* Salary Range */}
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="text-xs uppercase tracking-wider text-muted-foreground mb-4">Annual Compensation Range</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-xs text-muted-foreground mb-1">Entry Level</p>
                <p className="text-2xl font-bold font-display text-foreground">{formatSalary(data.salary_low)}</p>
              </div>
              <div className="text-center border-x border-border">
                <p className="text-xs text-primary font-medium mb-1">Median</p>
                <p className="text-3xl font-bold font-display text-primary">{formatSalary(data.salary_mid)}</p>
              </div>
              <div className="text-center">
                <p className="text-xs text-muted-foreground mb-1">Senior Level</p>
                <p className="text-2xl font-bold font-display text-foreground">{formatSalary(data.salary_high)}</p>
              </div>
            </div>
            {/* Visual bar */}
            <div className="mt-6 relative">
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-primary/30 via-primary to-primary/30 rounded-full" style={{ width: "100%" }} />
              </div>
            </div>
          </div>

          {/* Market Outlook */}
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-primary" /> Market Outlook
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{data.market_outlook}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Factors */}
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-sm font-semibold mb-3">Key Salary Factors</h3>
              <ul className="space-y-2">
                {data.factors?.map((f, i) => (
                  <li key={i} className="text-sm text-muted-foreground flex gap-2">
                    <span className="text-primary mt-0.5">•</span> {f}
                  </li>
                ))}
              </ul>
            </div>

            {/* Tips */}
            <div className="bg-card border border-border rounded-xl p-6">
              <h3 className="text-sm font-semibold mb-3">Negotiation Tips</h3>
              <ul className="space-y-2">
                {data.negotiation_tips?.map((t, i) => (
                  <li key={i} className="text-sm text-muted-foreground flex gap-2">
                    <span className="font-semibold text-foreground shrink-0">{i + 1}.</span> {t}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}