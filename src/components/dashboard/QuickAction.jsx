import React from "react";
import { Link } from "react-router-dom";
import { ArrowUpRight } from "lucide-react";

export default function QuickAction({ label, path, icon: Icon }) {
  return (
    <Link
      to={path}
      className="group flex items-center gap-3 px-4 py-3 rounded-lg border border-border bg-card hover:border-primary/20 hover:bg-primary/3 transition-all duration-200"
    >
      <Icon className="w-4 h-4 text-primary" strokeWidth={2} />
      <span className="text-sm font-medium text-foreground flex-1">{label}</span>
      <ArrowUpRight className="w-3.5 h-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
    </Link>
  );
}