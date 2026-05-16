import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from "@/api/client";
import { Save, CheckCircle, Loader2, User, Trash2, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function Profile() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
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

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  useEffect(() => {
    setLoading(true);
    auth.me()
      .then((user) => {
        if (user) {
          setForm({
            first_name: user.first_name || "",
            last_name: user.last_name || "",
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
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      const msg = err?.message || "Failed to save profile. Please try again.";
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  const deleteAccount = async () => {
    setDeleting(true);
    setDeleteError("");
    try {
      await auth.deleteAccount();
      navigate("/login");
    } catch (err) {
      setDeleteError(err?.message || "Failed to delete account. Please try again.");
      setDeleting(false);
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
        {/* Name row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="First Name">
            <Input value={form.first_name} onChange={(e) => update("first_name", e.target.value)} placeholder="e.g. Ahmed" />
          </Field>
          <Field label="Last Name">
            <Input value={form.last_name} onChange={(e) => update("last_name", e.target.value)} placeholder="e.g. Hassan" />
          </Field>
        </div>

        {/* Role / Level / Location */}
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
              <option value="student">Student</option>
              <option value="intern">Intern</option>
              <option value="junior">Junior</option>
              <option value="mid">Mid-level</option>
              <option value="senior">Senior</option>
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

        {/* Links */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="LinkedIn">
            <Input value={form.linkedin} onChange={(e) => update("linkedin", e.target.value)} placeholder="linkedin.com/in/yourname" />
          </Field>
          <Field label="GitHub / Portfolio">
            <Input value={form.portfolio} onChange={(e) => update("portfolio", e.target.value)} placeholder="github.com/yourname" />
          </Field>
        </div>

        {/* Skills */}
        <Field label="Key Skills">
          <Textarea
            value={form.skills}
            onChange={(e) => update("skills", e.target.value)}
            placeholder="React, Node.js, Python, AWS, Figma, Arabic, English..."
            rows={3}
          />
        </Field>

        {/* Bio */}
        <Field label="Bio / Background">
          <Textarea
            value={form.bio}
            onChange={(e) => update("bio", e.target.value)}
            placeholder="Describe your background, years of experience, and biggest achievements..."
            rows={5}
          />
        </Field>

        {/* Remote */}
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

      {/* ── Delete Account ── */}
      <div className="mt-12 pt-8 border-t border-border">
        <h2 className="text-lg font-bold text-red-600 flex items-center gap-2 mb-1">
          <Trash2 className="w-5 h-5" />
          Delete Account
        </h2>
        <p className="text-sm text-muted-foreground mb-4">
          Permanently delete your account and all associated data. This action cannot be undone.
        </p>

        {!showDeleteConfirm ? (
          <Button
            type="button"
            variant="outline"
            className="border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300"
            onClick={() => setShowDeleteConfirm(true)}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete My Account
          </Button>
        ) : (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5 space-y-3 max-w-md">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
              <p className="text-sm text-red-700 font-medium">
                Are you sure? This will permanently delete your account, applications, and all data.
              </p>
            </div>

            {deleteError && (
              <p className="text-xs text-red-600">{deleteError}</p>
            )}

            <div className="flex gap-2">
              <Button
                type="button"
                variant="destructive"
                onClick={deleteAccount}
                disabled={deleting}
              >
                {deleting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Trash2 className="w-4 h-4 mr-2" />}
                {deleting ? "Deleting..." : "Yes, Delete Account"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => { setShowDeleteConfirm(false); setDeleteError(""); }}
                disabled={deleting}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}
      </div>
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
