import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Mail,
  Lock,
  ArrowRight,
  Briefcase,
  User,
  Sparkles,
} from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [role, setRole] = useState("user");

  const login = () => {
    localStorage.setItem("role", role);

    if (role === "recruiter") {
      navigate("/recruiter");
    } else {
      navigate("/");
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-6 py-10">
      <div className="w-full max-w-6xl grid lg:grid-cols-2 bg-card border border-border rounded-3xl overflow-hidden shadow-2xl">
        <div className="p-10 lg:p-14 bg-foreground text-background flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-xl bg-primary flex items-center justify-center mb-10">
              <span className="font-bold text-white">H</span>
            </div>

            <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-4">
              Career Command Center
            </p>

            <h1 className="text-5xl font-black leading-tight mb-6">
              Welcome to HireFlow
            </h1>

            <p className="text-background/70 text-lg max-w-md">
              Login as a candidate or recruiter and manage your career workflow.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-3 gap-4 text-sm">
            <div className="border border-white/10 rounded-2xl p-4">
              <p className="text-2xl font-bold">AI</p>
              <p className="text-background/60">Tools</p>
            </div>
            <div className="border border-white/10 rounded-2xl p-4">
              <p className="text-2xl font-bold">Pro</p>
              <p className="text-background/60">Tracking</p>
            </div>
            <div className="border border-white/10 rounded-2xl p-4">
              <p className="text-2xl font-bold">Jobs</p>
              <p className="text-background/60">Board</p>
            </div>
          </div>
        </div>

        <div className="p-10 lg:p-14 flex items-center">
          <div className="w-full max-w-md mx-auto">
            <div className="mb-8">
              <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center mb-5">
                <Sparkles className="w-5 h-5 text-primary" />
              </div>

              <h2 className="text-4xl font-extrabold mb-3">Sign in</h2>
              <p className="text-muted-foreground">
                Choose your role before entering the platform.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 mb-6">
              <button
                onClick={() => setRole("user")}
                className={`p-4 rounded-2xl border flex items-center gap-3 transition ${
                  role === "user"
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border bg-background text-foreground"
                }`}
              >
                <User className="w-5 h-5" />
                <span className="font-semibold">User</span>
              </button>

              <button
                onClick={() => setRole("recruiter")}
                className={`p-4 rounded-2xl border flex items-center gap-3 transition ${
                  role === "recruiter"
                    ? "border-primary bg-primary/10 text-primary"
                    : "border-border bg-background text-foreground"
                }`}
              >
                <Briefcase className="w-5 h-5" />
                <span className="font-semibold">Recruiter</span>
              </button>
            </div>

            <div className="space-y-3">
              <button onClick={login} className="social-btn">
                <span className="text-lg font-bold">G</span>
                Continue with Gmail
              </button>

              <button onClick={login} className="social-btn">
                <span className="text-lg font-black">M</span>
                Continue with Microsoft
              </button>

              <button onClick={login} className="social-btn">
                <span className="text-lg font-bold">f</span>
                Continue with Facebook
              </button>
            </div>

            <div className="flex items-center gap-3 my-6">
              <div className="h-px bg-border flex-1" />
              <span className="text-xs text-muted-foreground uppercase">
                or email
              </span>
              <div className="h-px bg-border flex-1" />
            </div>

            <div className="space-y-4">
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="email"
                  placeholder="Email"
                  className="login-input"
                />
              </div>

              <div className="relative">
                <Lock className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="password"
                  placeholder="Password"
                  className="login-input"
                />
              </div>

              <button
                onClick={login}
                className="w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition"
              >
                Login as {role === "recruiter" ? "Recruiter" : "User"}
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}