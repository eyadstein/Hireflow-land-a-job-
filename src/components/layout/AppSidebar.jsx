import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { auth } from "@/api/client";
import {
  LayoutDashboard,
  Briefcase,
  FileText,
  KanbanSquare,
  Sparkles,
  PenLine,
  MessageSquare,
  Users,
  DollarSign,
  User,
  LogOut,
  Building2,
  Target,
  Map,
  ScanSearch,
  Wrench,
} from "lucide-react";

const jobseekerNavItems = [
  { icon: LayoutDashboard, label: "Dashboard",    path: "/" },
  { icon: Briefcase,       label: "Job Board",    path: "/jobs" },
  { icon: FileText,        label: "Applications", path: "/applications" },
  { icon: KanbanSquare,    label: "Tracker",      path: "/tracker" },
  { icon: Sparkles,        label: "Resume AI",    path: "/resume-ai" },
  { icon: Target,          label: "Skill Gap",    path: "/skill-gap" },
  { icon: ScanSearch,      label: "ATS Check",    path: "/ats-check" },
  { icon: PenLine,         label: "Cover Letter", path: "/cover-letter" },
  { icon: Users,           label: "Interview",    path: "/interview" },
  { icon: DollarSign,      label: "Salary",       path: "/salary" },
  { icon: Map,             label: "Career Plan",  path: "/career-roadmap" },
  { icon: MessageSquare,   label: "AI Assistant", path: "/chatbot" },
  { icon: User,            label: "Profile",      path: "/profile" },
];

const recruiterNavItems = [
  { icon: Building2,       label: "Dashboard",    path: "/recruiter" },
  { icon: Briefcase,       label: "Job Board",    path: "/jobs" },
  { icon: Wrench,          label: "Optimize",     path: "/recruiter/optimize" },
  { icon: User,            label: "Profile",      path: "/profile" },
];

export default function AppSidebar() {
  const [expanded, setExpanded] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const role = localStorage.getItem("role");
  const navItems = role === "recruiter" ? recruiterNavItems : jobseekerNavItems;

  const handleLogout = () => {
    auth.logout();
    navigate("/login");
  };

  return (
    <motion.aside
      onMouseEnter={() => setExpanded(true)}
      onMouseLeave={() => setExpanded(false)}
      animate={{ width: expanded ? 240 : 64 }}
      transition={{ duration: 0.25 }}
      className="fixed left-0 top-0 h-screen bg-card border-r border-border z-50 flex flex-col overflow-hidden"
    >
      <div className="h-16 flex items-center px-4 border-b border-border">
        <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
          <span className="text-primary-foreground font-bold text-sm">H</span>
        </div>

        <AnimatePresence>
          {expanded && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              className="ml-3"
            >
              <p className="font-semibold text-sm">HireFlow</p>
              <p className="text-[10px] text-muted-foreground uppercase">
                Career Platform
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center h-10 rounded-lg px-3 transition relative ${
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              }`}
            >
              <item.icon className="w-[18px] h-[18px] flex-shrink-0" />

              <AnimatePresence>
                {expanded && (
                  <motion.span
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -8 }}
                    className="ml-3 text-sm font-medium whitespace-nowrap"
                  >
                    {item.label}
                  </motion.span>
                )}
              </AnimatePresence>
            </Link>
          );
        })}
      </nav>

      <div className="p-2 border-t border-border">
        <button
          onClick={handleLogout}
          className="flex items-center h-10 rounded-lg px-3 w-full text-muted-foreground hover:bg-secondary hover:text-red-500 transition"
        >
          <LogOut className="w-[18px] h-[18px] flex-shrink-0" />

          <AnimatePresence>
            {expanded && (
              <motion.span
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                className="ml-3 text-sm font-medium whitespace-nowrap"
              >
                Sign Out
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
}