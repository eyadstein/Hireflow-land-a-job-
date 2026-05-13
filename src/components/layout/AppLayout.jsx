import React, { useEffect } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import AppSidebar from "./AppSidebar";

const JOBSEEKER_ONLY = [
  "/resume-ai", "/skill-gap", "/ats-check", "/cover-letter",
  "/interview", "/salary", "/career-roadmap", "/chatbot",
  "/applications", "/tracker",
];

const RECRUITER_ONLY = [
  "/recruiter",
];

export default function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    const role = localStorage.getItem("role");
    const path = location.pathname;
    if (role === "recruiter" && JOBSEEKER_ONLY.some((p) => path.startsWith(p))) {
      navigate("/recruiter", { replace: true });
    } else if (role !== "recruiter" && RECRUITER_ONLY.some((p) => path.startsWith(p))) {
      navigate("/", { replace: true });
    }
  }, [navigate, location.pathname]);

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar />
      <main className="ml-16 min-h-screen">
        <Outlet />
      </main>
    </div>
  );
}