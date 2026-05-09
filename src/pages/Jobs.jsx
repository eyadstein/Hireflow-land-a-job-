import React, { useState } from "react";
import { jobs as jobsApi } from "@/api/client";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Search, MapPin, Building2, Clock, DollarSign, ExternalLink, Briefcase, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import PageHeader from "@/components/shared/PageHeader";
import EmptyState from "@/components/shared/EmptyState";

const typeLabels = {
  full_time: "Full Time",
  part_time: "Part Time",
  contract: "Contract",
  internship: "Internship",
  remote: "Remote",
};

const deptLabels = {
  engineering: "Engineering",
  design: "Design",
  marketing: "Marketing",
  sales: "Sales",
  operations: "Operations",
  hr: "HR",
  finance: "Finance",
  product: "Product",
};

export default function Jobs() {
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("all");

  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => jobsApi.list(),
  });

  const filtered = jobs.filter((job) => {
    const matchesSearch =
      !search ||
      job.title?.toLowerCase().includes(search.toLowerCase()) ||
      job.company?.toLowerCase().includes(search.toLowerCase());
    const matchesDept = deptFilter === "all" || job.department === deptFilter;
    return matchesSearch && matchesDept;
  });

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <PageHeader
        eyebrow="Discover"
        title="Job Board"
        description="Browse opportunities and find your perfect role."
      />

      <div className="flex flex-col sm:flex-row gap-3 mb-8">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or company..."
            className="pl-9 bg-card"
          />
        </div>
        <Select value={deptFilter} onValueChange={setDeptFilter}>
          <SelectTrigger className="w-full sm:w-44 bg-card">
            <Filter className="w-4 h-4 mr-2 text-muted-foreground" />
            <SelectValue placeholder="Department" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Departments</SelectItem>
            {Object.entries(deptLabels).map(([k, v]) => (
              <SelectItem key={k} value={k}>{v}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-28 rounded-xl bg-card border border-border animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={Briefcase}
          title="No jobs found"
          description="Try adjusting your search or filters, or check back later for new opportunities."
        />
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {filtered.map((job, i) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -12 }}
                transition={{ duration: 0.3, delay: i * 0.03 }}
                className="group bg-card border border-border rounded-xl p-5 hover:border-primary/20 hover:shadow-md hover:shadow-primary/5 transition-all duration-300"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-base font-semibold text-foreground truncate">
                        {job.title}
                      </h3>
                      {job.job_type && (
                        <Badge variant="secondary" className="text-[11px] font-medium shrink-0">
                          {typeLabels[job.job_type] || job.job_type}
                        </Badge>
                      )}
                    </div>
                    <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5" /> {job.company}
                      </span>
                      {job.location && (
                        <span className="flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5" /> {job.location}
                        </span>
                      )}
                      {job.department && (
                        <Badge variant="outline" className="text-[11px]">
                          {deptLabels[job.department] || job.department}
                        </Badge>
                      )}
                      {(job.salary_min || job.salary_max) && (
                        <span className="flex items-center gap-1.5">
                          <DollarSign className="w-3.5 h-3.5" />
                          {job.salary_min && job.salary_max
                            ? `$${(job.salary_min / 1000).toFixed(0)}k – $${(job.salary_max / 1000).toFixed(0)}k`
                            : job.salary_min
                            ? `From $${(job.salary_min / 1000).toFixed(0)}k`
                            : `Up to $${(job.salary_max / 1000).toFixed(0)}k`}
                        </span>
                      )}
                    </div>
                    {job.description && (
                      <p className="text-sm text-muted-foreground mt-2 line-clamp-2 leading-relaxed">
                        {job.description}
                      </p>
                    )}
                  </div>
                  {job.url && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 w-9 h-9 rounded-lg border border-border flex items-center justify-center text-muted-foreground hover:text-primary hover:border-primary/30 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
