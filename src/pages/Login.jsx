import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Mail,
  Lock,
  ArrowRight,
  Briefcase,
  User,
  Sparkles,
  Loader2,
} from "lucide-react";
import { auth } from "@/api/client";

function isValidEmail(email) {
  return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test(
    email.trim()
  );
}

export default function Login() {
  const navigate = useNavigate();

  const [mode, setMode] = useState("login");
  const [role, setRole] = useState("jobseeker");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const resetError = () => setError("");

  const handleSubmit = async () => {
    const cleanEmail = email.trim().toLowerCase();

    if (!cleanEmail || !password) {
      setError("Please enter your email and password.");
      return;
    }

    if (!isValidEmail(cleanEmail)) {
      setError("Please enter a valid email address, for example name@example.com.");
      return;
    }

    if (mode === "register" && password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      let data;

      if (mode === "register") {
        data = await auth.register(cleanEmail, password, role);
      } else {
        data = await auth.login(cleanEmail, password);
      }

      const userRole = data?.user?.role || role || "jobseeker";

      localStorage.setItem("role", userRole);

      if (userRole === "recruiter" || userRole === "company") {
        navigate("/recruiter");
      } else {
        navigate("/");
      }
    } catch (err) {
      setError(err?.message || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  const switchMode = (nextMode) => {
    setMode(nextMode);
    setError("");
    setPassword("");
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

              <h2 className="text-4xl font-extrabold mb-3">
                {mode === "login" ? "Sign in" : "Create account"}
              </h2>

              <p className="text-muted-foreground">
                {mode === "login"
                  ? "Enter your credentials to continue."
                  : "Choose your role and sign up."}
              </p>
            </div>

            {mode === "register" && (
              <div className="grid grid-cols-2 gap-3 mb-6">
                <button
                  type="button"
                  onClick={() => setRole("jobseeker")}
                  className={`p-4 rounded-2xl border flex items-center gap-3 transition ${
                    role === "jobseeker"
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border bg-background text-foreground"
                  }`}
                >
                  <User className="w-5 h-5" />
                  <span className="font-semibold">Job Seeker</span>
                </button>

                <button
                  type="button"
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
            )}

            {error && (
              <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    resetError();
                  }}
                  onKeyDown={handleKey}
                  className="login-input"
                />
              </div>

              <div className="relative">
                <Lock className="w-4 h-4 absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    resetError();
                  }}
                  onKeyDown={handleKey}
                  className="login-input"
                />
              </div>

              <button
                type="button"
                onClick={handleSubmit}
                disabled={loading}
                className="w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold flex items-center justify-center gap-2 hover:opacity-90 transition disabled:opacity-60"
              >
                {loading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    {mode === "login" ? "Sign In" : "Create Account"}
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>

            <p className="text-center text-sm text-muted-foreground mt-6">
              {mode === "login" ? (
                <>
                  Don&apos;t have an account?{" "}
                  <button
                    type="button"
                    onClick={() => switchMode("register")}
                    className="text-primary font-semibold hover:underline"
                  >
                    Sign up
                  </button>
                </>
              ) : (
                <>
                  Already have an account?{" "}
                  <button
                    type="button"
                    onClick={() => switchMode("login")}
                    className="text-primary font-semibold hover:underline"
                  >
                    Sign in
                  </button>
                </>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}