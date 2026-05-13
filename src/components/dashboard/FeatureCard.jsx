import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

export default function FeatureCard({ title, description, icon: Icon, path, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay }}
    >
      <Link
        to={path}
        className="group block bg-card border border-border rounded-xl p-6 hover:border-primary/20 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
      >
        <div className="flex items-start justify-between mb-4">
          <div className="w-11 h-11 rounded-xl bg-primary/8 flex items-center justify-center group-hover:bg-primary/12 transition-colors">
            <Icon className="w-5 h-5 text-primary" strokeWidth={1.8} />
          </div>
          <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300" />
        </div>
        <h3 className="text-[15px] font-semibold text-foreground mb-1">{title}</h3>
        <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
      </Link>
    </motion.div>
  );
}