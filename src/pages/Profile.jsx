import React, { useEffect, useState } from "react";
import { Save, CheckCircle, Loader2, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function Profile() {
  const [form, setForm] = useState({
    fullName: "",
    jobTitle: "",
    city: "",
    country: "Egypt",
    linkedin: "",
    portfolio: "",
    skills: "",
    experience: "",
  });

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const savedProfile = localStorage.getItem("profile");
    if (savedProfile) setForm(JSON.parse(savedProfile));
  }, []);

  const update = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const saveProfile = () => {
    setSaving(true);

    setTimeout(() => {
      localStorage.setItem("profile", JSON.stringify(form));
      setSaving(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }, 500);
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
          Account
        </p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <User className="w-8 h-8 text-primary" />
          My Profile
        </h1>
        <p className="text-muted-foreground mt-2">
          Fill once — pre-fills Cover Letters, Salary Estimator, and Auto-Apply automatically.
        </p>
      </div>

      <div className="bg-card border border-border rounded-xl p-6 space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Field label="Full Name">
            <Input
              value={form.fullName}
              onChange={(e) => update("fullName", e.target.value)}
              placeholder="Your name"
            />
          </Field>

          <Field label="Target Job Title">
            <Input
              value={form.jobTitle}
              onChange={(e) => update("jobTitle", e.target.value)}
              placeholder="e.g. Frontend Developer"
            />
          </Field>

          <Field label="City">
            <Input
              value={form.city}
              onChange={(e) => update("city", e.target.value)}
              placeholder="e.g. Cairo"
            />
          </Field>

          <Field label="Country">
            <select
              value={form.country}
              onChange={(e) => update("country", e.target.value)}
              className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option>Egypt</option>
              <option>UAE</option>
              <option>Saudi Arabia</option>
              <option>USA</option>
              <option>Germany</option>
            </select>
          </Field>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="LinkedIn">
            <Input
              value={form.linkedin}
              onChange={(e) => update("linkedin", e.target.value)}
              placeholder="linkedin.com/in/yourname"
            />
          </Field>

          <Field label="GitHub / Portfolio">
            <Input
              value={form.portfolio}
              onChange={(e) => update("portfolio", e.target.value)}
              placeholder="github.com/yourname"
            />
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

        <Field label="Background and Experience">
          <Textarea
            value={form.experience}
            onChange={(e) => update("experience", e.target.value)}
            placeholder="Describe your background, years of experience, and biggest achievements..."
            rows={5}
          />
        </Field>
      </div>

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
      <label className="text-sm font-medium mb-1.5 block text-foreground">
        {label}
      </label>
      {children}
    </div>
  );
}