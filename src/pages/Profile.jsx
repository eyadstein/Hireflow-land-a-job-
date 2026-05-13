import React, { useEffect, useState } from "react";
import { auth } from "@/api/client";
import { Save, CheckCircle, Loader2, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function Profile() {
  const [form, setForm] = useState({
    bio: "",
    skills: "",
    experience_level: "",
    city: "",
    country: "Egypt",
    linkedin: "",
    portfolio: "",
    desired_roles: "",
    preferred_countries: "",
    prefers_remote: false,
  });

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    auth.me()
      .then((user) => {
        if (user) {
          setForm({
            bio: user.bio || "",
            skills: user.skills || "",
            experience_level: user.experience_level || "",
            city: user.city || "",
            country: user.country || "Egypt",
            linkedin: user.linkedin || "",
            portfolio: user.portfolio || "",
            desired_roles: user.desired_roles || "",
            preferred_countries: user.preferred_countries || "",
            prefers_remote: user.prefers_remote || false,
          });
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const update = (key, value) => setForm((prev) => ({ ...prev, [key]: value }));

  const saveProfile = async () => {
    setSaving(true);
    setError("");
    try {
      await auth.updateProfile(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError("Failed to save profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 lg:p-12 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    );
  }

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Account</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <User className="w-8 h-8 text-primary" />
          My Profile
        </h1>
        <p className="text-muted-foreground mt-2">
          Fill your profile — it pre-fills Cover Letters, Salary Estimator, and more.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Field label="Target Job Title">
            <Input value={form.desired_roles} onChange={(e) => update("desired_roles", e.target.value)} placeholder="e.g. Frontend Developer" />
          </Field>
          <Field label="Experience Level">
            <select
              value={form.experience_level}
              onChange={(e) => update("experience_level", e.target.value)}
              className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Select level</option>
              <option>Junior</option>
              <option>Mid</option>
              <option>Senior</option>
              <option>Lead</option>
            </select>
          </Field>
          <Field label="City">
            <Input value={form.city} onChange={(e) => update("city", e.target.value)} placeholder="e.g. Cairo" />
          </Field>
          <Field label="Country">
            <select
              value={form.country}
              onChange={(e) => update("country", e.target.value)}
              className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              {["Egypt", "UAE", "Saudi Arabia", "Kuwait", "Qatar", "Jordan", "USA", "Germany"].map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </Field>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="LinkedIn">
            <Input value={form.linkedin} onChange={(e) => update("linkedin", e.target.value)} placeholder="linkedin.com/in/yourname" />
          </Field>
          <Field label="GitHub / Portfolio">
            <Input value={form.portfolio} onChange={(e) => update("portfolio", e.target.value)} placeholder="github.com/yourname" />
          </Field>
        </div>

        <Field label="Key Skills">
          <Textarea
            value={form.skills}
            onChange={(e) => update("skills", e.target.value)}
            placeholder="React, Node.js, Python, AWS, Figma, Arabic, English..."
            rows={3}
          />
        </Field>

        <Field label="Bio / Background">
          <Textarea
            value={form.bio}
            onChange={(e) => update("bio", e.target.value)}
            placeholder="Describe your background, years of experience, and biggest achievements..."
            rows={5}
          />
        </Field>

        <div className="flex items-center gap-3">
          <input
            type="checkbox"
            id="remote"
            checked={form.prefers_remote}
            onChange={(e) => update("prefers_remote", e.target.checked)}
            className="w-4 h-4 rounded border-border"
          />
          <label htmlFor="remote" className="text-sm font-medium text-foreground">
            Open to remote work
          </label>
        </div>
      </div>

      {error && (
        <div className="mt-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
          {error}
        </div>
      )}

      <Button onClick={saveProfile} disabled={saving} className="mt-6">
        {saving ? (
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
        ) : saved ? (
          <CheckCircle className="w-4 h-4 mr-2" />
        ) : (
          <Save className="w-4 h-4 mr-2" />
        )}
        {saving ? "Saving..." : saved ? "Saved!" : "Save Profile"}
      </Button>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <label className="text-sm font-medium mb-1.5 block text-foreground">{label}</label>
      {children}
    </div>
  );
}
