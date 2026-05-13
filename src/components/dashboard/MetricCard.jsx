import React from "react";
import { motion } from "framer-motion";

export default function MetricCard({ label, value, subtitle, icon: Icon, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="group relative bg-card rounded-xl border border-border p-6 hover:border-primary/20 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground mb-2">
            {label}
          </p>
          <p className="text-4xl font-bold text-foreground tracking-tight font-display">
            {value}
          </p>
          {subtitle && (
            <p className="text-sm text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
        {Icon && (
          <div className="w-10 h-10 rounded-lg bg-primary/8 flex items-center justify-center group-hover:bg-primary/12 transition-colors">
            <Icon className="w-5 h-5 text-primary" strokeWidth={1.8} />
          </div>
        )}
      </div>
    </motion.div>
  );
}