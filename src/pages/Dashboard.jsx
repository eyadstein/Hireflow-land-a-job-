import React, { useState, useEffect } from "react";
import { base44 } from "@/api/base44Client";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import {
  Briefcase,
  FileText,
  Sparkles,
  PenLine,
  Users,
  DollarSign,
  MessageSquare,
  Send,
  Target,
  TrendingUp,
} from "lucide-react";
import MetricCard from "@/components/dashboard/MetricCard";
import FeatureCard from "@/components/dashboard/FeatureCard";
import QuickAction from "@/components/dashboard/QuickAction";

const features = [
  { title: "Resume AI", description: "Optimize your resume with AI-powered analysis and ATS scoring.", icon: Sparkles, path: "/resume-ai" },
  { title: "Cover Letter", description: "Generate tailored cover letters for any role in seconds.", icon: PenLine, path: "/cover-letter" },
  { title: "Interview Prep", description: "Practice with AI mock interviews and get instant feedback.", icon: Users, path: "/interview" },
  { title: "Salary Insights", description: "Research market compensation and negotiate with confidence.", icon: DollarSign, path: "/salary" },
  { title: "AI Assistant", description: "Your personal career advisor — ask anything about your job search.", icon: MessageSquare, path: "/chatbot" },
  { title: "Application Tracker", description: "Visualize your pipeline and never lose track of an opportunity.", icon: Target, path: "/tracker" },
];

export default function Dashboard() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    base44.auth.me().then(setUser).catch(() => {});
  }, []);

  const { data: applications = [] } = useQuery({
    queryKey: ["applications"],
    queryFn: () => base44.entities.Application.list(),
  });

  const { data: jobs = [] } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => base44.entities.Job.list(),
  });

  const applied = applications.filter((a) => a.status === "applied").length;
  const interviewing = applications.filter((a) => a.status === "interview").length;
  const offers = applications.filter((a) => a.status === "offer").length;

  const firstName = user?.full_name?.split(" ")[0] || "there";

  return (
    <div className="p-8 lg:p-12 max-w-none">
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-10"
      >
        <p className="text-xs font-semibold uppercase tracking-[0.15em] text-primary mb-2">
          Career Command Center
        </p>
        <h1 className="text-4xl lg:text-5xl font-bold text-foreground tracking-tight leading-[1.1]">
          Welcome back, {firstName}
        </h1>
        <p className="text-muted-foreground mt-2 text-lg max-w-xl">
          Your job search at a glance. Stay organized, stay ahead.
        </p>
      </motion.div>

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <MetricCard label="Total Applications" value={applications.length} icon={Send} delay={0.05} />
        <MetricCard label="Active Pipeline" value={applied} subtitle="Awaiting response" icon={FileText} delay={0.1} />
        <MetricCard label="Interviews" value={interviewing} subtitle="Scheduled" icon={Users} delay={0.15} />
        <MetricCard label="Offers" value={offers} icon={TrendingUp} delay={0.2} />
      </div>

      <div className="horizon-rule mb-10" />

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.25, duration: 0.4 }}
        className="mb-10"
      >
        <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <QuickAction label="Browse Jobs" path="/jobs" icon={Briefcase} />
          <QuickAction label="Track Application" path="/applications" icon={FileText} />
          <QuickAction label="Optimize Resume" path="/resume-ai" icon={Sparkles} />
          <QuickAction label="Prep Interview" path="/interview" icon={Users} />
        </div>
      </motion.div>

      {/* Feature Grid */}
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
          AI-Powered Tools
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature, i) => (
            <FeatureCard key={feature.path} {...feature} delay={0.3 + i * 0.05} />
          ))}
        </div>
      </div>
    </div>
  );
}