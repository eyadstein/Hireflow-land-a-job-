import { Toaster } from "@/components/ui/toaster";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClientInstance } from "@/lib/query-client";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import PageNotFound from "./lib/PageNotFound";
import AppLayout from "@/components/layout/AppLayout";

import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import Jobs from "@/pages/Jobs";
import Applications from "@/pages/Applications";
import Tracker from "@/pages/Tracker";
import ResumeAI from "@/pages/ResumeAI";
import CoverLetter from "@/pages/CoverLetter";
import Interview from "@/pages/Interview";
import Salary from "@/pages/Salary";
import Chatbot from "@/pages/Chatbot";
import Profile from "@/pages/Profile";
import Recruiter from "@/pages/Recruiter";
import RecruiterAnalytics from "@/pages/recruiter/Analytics";
import SkillGap from "@/pages/SkillGap";
import CareerRoadmap from "@/pages/CareerRoadmap";
import ATSCheck from "@/pages/ATSCheck";

function App() {
  return (
    <QueryClientProvider client={queryClientInstance}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<AppLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/applications" element={<Applications />} />
            <Route path="/tracker" element={<Tracker />} />
            <Route path="/resume-ai" element={<ResumeAI />} />
            <Route path="/cover-letter" element={<CoverLetter />} />
            <Route path="/interview" element={<Interview />} />
            <Route path="/salary" element={<Salary />} />
            <Route path="/chatbot" element={<Chatbot />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/recruiter" element={<Recruiter />} />
            <Route path="/recruiter/analytics" element={<RecruiterAnalytics />} />
            <Route path="/skill-gap" element={<SkillGap />} />
            <Route path="/career-roadmap" element={<CareerRoadmap />} />
            <Route path="/ats-check" element={<ATSCheck />} />
          </Route>

          <Route path="*" element={<PageNotFound />} />
        </Routes>

        <Toaster />
      </Router>
    </QueryClientProvider>
  );
}

export default App;