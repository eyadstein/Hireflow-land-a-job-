import React from "react";
import { motion } from "framer-motion";

export default function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mb-8"
    >
      {eyebrow && (
        <p className="text-xs font-semibold uppercase tracking-[0.15em] text-primary mb-2">
          {eyebrow}
        </p>
      )}
      <div className="flex items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight">
            {title}
          </h1>
          {description && (
            <p className="text-muted-foreground mt-1.5 max-w-xl leading-relaxed">
              {description}
            </p>
          )}
        </div>
        {actions && <div className="flex items-center gap-3">{actions}</div>}
      </div>
      <div className="horizon-rule mt-6" />
    </motion.div>
  );
}