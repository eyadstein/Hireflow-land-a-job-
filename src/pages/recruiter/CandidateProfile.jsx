import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft,
  Briefcase,
  CheckCircle,
  Clock,
  FileText,
  Globe,
  Loader2,
  Mail,
  MapPin,
  Pencil,
  Plus,
  Trash2,
  User,
  Wifi,
  XCircle,
  ExternalLink,
  Star,
} from "lucide-react";

import { recruiter } from "@/api/client";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const statusLabels = {
  pending: "Pending",
  applied: "Applied",
  screening: "Screening",
  interview: "Interview",
  offer: "Offer",
  accepted: "Accepted",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

const statusStyles = {
  pending: "bg-yellow-50 text-yellow-700 border-yellow-200",
  applied: "bg-yellow-50 text-yellow-700 border-yellow-200",
  screening: "bg-blue-50 text-blue-700 border-blue-200",
  interview: "bg-purple-50 text-purple-700 border-purple-200",
  offer: "bg-emerald-50 text-emerald-700 border-emerald-200",
  accepted: "bg-green-50 text-green-700 border-green-200",
  rejected: "bg-red-50 text-red-700 border-red-200",
  withdrawn: "bg-gray-50 text-gray-700 border-gray-200",
};

const levelLabels = {
  student: "Student",
  intern: "Intern",
  junior: "Junior",
  mid: "Mid-level",
  senior: "Senior",
};

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function getCandidateDisplayName(profile) {
  if (!profile) return "Candidate Profile";
  const fullName = `${profile.first_name || ""} ${profile.last_name || ""}`.trim();
  return fullName || profile.username || profile.email || `Candidate #${profile.user_id}`;
}

function getApplicationTitle(app) {
  return app.job_display_title || app.job_title || `Job #${app.job}`;
}

function getCompany(app) {
  return app.company_display_name || app.company || "Unknown Company";
}

function ensureUrl(val) {
  if (!val) return null;
  return val.startsWith("http") ? val : `https://${val}`;
}

export default function CandidateProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [noteText, setNoteText] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState("");
  const [message, setMessage] = useState("");

  const { data: profile, isLoading: profileLoading, error: profileError } = useQuery({
    queryKey: ["recruiter-candidate-profile", userId],
    queryFn: () => recruiter.candidateProfile(userId),
    enabled: !!userId,
  });

  const { data: timelineData, isLoading: timelineLoading, error: timelineError } = useQuery({
    queryKey: ["recruiter-candidate-timeline", userId],
    queryFn: () => recruiter.candidateTimeline(userId),
    enabled: !!userId,
  });

  const { data: notesData, isLoading: notesLoading, error: notesError } = useQuery({
    queryKey: ["recruiter-candidate-notes", userId],
    queryFn: () => recruiter.candidateNotes(userId),
    enabled: !!userId,
  });

  const notes = normalizeList(notesData);
  const timeline = timelineData?.timeline || [];
  const applications = profile?.applications || [];

  const invalidateCandidateData = () => {
    queryClient.invalidateQueries({ queryKey: ["recruiter-candidate-profile", userId] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-candidate-timeline", userId] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-candidate-notes", userId] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-my-jobs"] });
    queryClient.invalidateQueries({ queryKey: ["recruiter-dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["applications"] });
  };

  const statusMutation = useMutation({
    mutationFn: ({ applicationId, status }) =>
      recruiter.updateApplicationStatus(applicationId, status),
    onSuccess: (data) => {
      setMessage(`Status updated to ${statusLabels[data?.status] || data?.status}.`);
      invalidateCandidateData();
    },
    onError: (err) => setMessage(err?.message || "Failed to update status."),
  });

  const addNoteMutation = useMutation({
    mutationFn: (text) => recruiter.addNote(userId, text),
    onSuccess: () => { setNoteText(""); setMessage("Note added."); invalidateCandidateData(); },
    onError: (err) => setMessage(err?.message || "Failed to add note."),
  });

  const updateNoteMutation = useMutation({
    mutationFn: ({ id, text }) => recruiter.updateNote(id, text),
    onSuccess: () => { setEditingId(null); setEditText(""); setMessage("Note updated."); invalidateCandidateData(); },
    onError: (err) => setMessage(err?.message || "Failed to update note."),
  });

  const deleteNoteMutation = useMutation({
    mutationFn: (id) => recruiter.deleteNote(id),
    onSuccess: () => { setMessage("Note deleted."); invalidateCandidateData(); },
    onError: (err) => setMessage(err?.message || "Failed to delete note."),
  });

  const updateStatus = (applicationId, status) => {
    setMessage("");
    statusMutation.mutate({ applicationId, status });
  };

  const addNote = () => {
    const clean = noteText.trim();
    if (!clean) { setMessage("Write a note first."); return; }
    setMessage("");
    addNoteMutation.mutate(clean);
  };

  const saveEditedNote = (id) => {
    const clean = editText.trim();
    if (!clean) { setMessage("Note cannot be empty."); return; }
    setMessage("");
    updateNoteMutation.mutate({ id, text: clean });
  };

  const loading = profileLoading || timelineLoading || notesLoading;
  const hasError = profileError || timelineError || notesError;

  // Parse skills into an array for display
  const skillsList = profile?.skills
    ? profile.skills.split(/[,\n]+/).map((s) => s.trim()).filter(Boolean)
    : [];

  const linkedinUrl = ensureUrl(profile?.linkedin);
  const portfolioUrl = ensureUrl(profile?.portfolio);

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition"
      >
        <ArrowLeft className="w-4 h-4" />
        Back
      </button>

      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">
          Candidate Insight
        </p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <User className="w-8 h-8 text-primary" />
          {getCandidateDisplayName(profile)}
        </h1>
        {profile?.email && (
          <p className="text-muted-foreground mt-2 flex items-center gap-2">
            <Mail className="w-4 h-4" />
            {profile.email}
          </p>
        )}
      </div>

      {hasError && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {profileError?.message || timelineError?.message || notesError?.message || "Failed to load candidate profile."}
        </div>
      )}

      {message && (
        <div className="bg-secondary border border-border rounded-xl p-4 mb-6 text-sm">
          {message}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <div className="space-y-8">

          {/* ── Stats ── */}
          {profile && (
            <div className="grid grid-cols-2 md:grid-cols-5 xl:grid-cols-9 gap-3">
              {[
                { label: "Total", value: profile.total_applications },
                { label: "Pending", value: profile.pending },
                { label: "Applied", value: profile.applied },
                { label: "Screening", value: profile.screening },
                { label: "Interview", value: profile.interview },
                { label: "Offer", value: profile.offer },
                { label: "Accepted", value: profile.accepted },
                { label: "Rejected", value: profile.rejected },
                { label: "Notes", value: profile.notes_count },
              ].map((item) => (
                <div key={item.label} className="bg-card border border-border rounded-xl p-4 text-center">
                  <p className="text-2xl font-black">{item.value ?? 0}</p>
                  <p className="text-xs text-muted-foreground mt-1">{item.label}</p>
                </div>
              ))}
            </div>
          )}

          {/* ── Candidate Profile Info ── */}
          {profile && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
                Candidate Profile
              </h2>

              <div className="bg-card border border-border rounded-xl p-6 space-y-5">
                {/* Meta row */}
                <div className="flex flex-wrap gap-4 text-sm">
                  {profile.experience_level && (
                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary font-medium">
                      <Star className="w-3.5 h-3.5" />
                      {levelLabels[profile.experience_level] || profile.experience_level}
                    </span>
                  )}
                  {profile.desired_roles && (
                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-secondary border border-border font-medium">
                      <Briefcase className="w-3.5 h-3.5 text-muted-foreground" />
                      {profile.desired_roles}
                    </span>
                  )}
                  {(profile.city || profile.country) && (
                    <span className="flex items-center gap-2 text-muted-foreground">
                      <MapPin className="w-3.5 h-3.5" />
                      {[profile.city, profile.country].filter(Boolean).join(", ")}
                    </span>
                  )}
                  {profile.prefers_remote && (
                    <span className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-50 text-green-700 border border-green-200 text-xs font-medium">
                      <Wifi className="w-3.5 h-3.5" />
                      Open to Remote
                    </span>
                  )}
                </div>

                {/* Links */}
                {(linkedinUrl || portfolioUrl) && (
                  <div className="flex flex-wrap gap-3">
                    {linkedinUrl && (
                      <a
                        href={linkedinUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 text-sm text-primary hover:underline"
                      >
                        <Globe className="w-3.5 h-3.5" />
                        LinkedIn
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    {portfolioUrl && (
                      <a
                        href={portfolioUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1.5 text-sm text-primary hover:underline"
                      >
                        <Globe className="w-3.5 h-3.5" />
                        Portfolio / GitHub
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                )}

                {/* Skills */}
                {skillsList.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">Skills</p>
                    <div className="flex flex-wrap gap-2">
                      {skillsList.map((skill) => (
                        <span
                          key={skill}
                          className="px-2.5 py-1 rounded-full bg-secondary border border-border text-xs font-medium"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Bio */}
                {profile.bio && (
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-2">Bio</p>
                    <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                      {profile.bio}
                    </p>
                  </div>
                )}

                {/* Empty state if no profile data at all */}
                {!profile.bio && skillsList.length === 0 && !profile.experience_level && !profile.desired_roles && (
                  <p className="text-sm text-muted-foreground italic">
                    This candidate has not filled in their profile yet.
                  </p>
                )}
              </div>
            </section>
          )}

          {/* ── Applications to Your Jobs ── */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Applications to Your Jobs
            </h2>

            {applications.length === 0 ? (
              <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
                This candidate has not applied to your jobs.
              </div>
            ) : (
              <div className="space-y-3">
                {applications.map((app) => {
                  const locked = ["accepted", "rejected", "withdrawn"].includes(app.status);

                  return (
                    <div key={app.id} className="bg-card border border-border rounded-xl p-5">
                      <div className="flex flex-col xl:flex-row xl:items-start xl:justify-between gap-5">
                        <div className="min-w-0">
                          <div className="flex items-center gap-3 flex-wrap">
                            <FileText className="w-5 h-5 text-primary" />
                            <h3 className="font-bold">{getApplicationTitle(app)}</h3>
                            <span className={`px-3 py-1 rounded-full border text-xs font-semibold ${statusStyles[app.status] || statusStyles.pending}`}>
                              {statusLabels[app.status] || app.status}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mt-2 flex items-center gap-2">
                            <Briefcase className="w-4 h-4" />
                            {getCompany(app)}
                          </p>
                          {app.created_at && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Applied {new Date(app.created_at).toLocaleString()}
                            </p>
                          )}
                          {app.reviewed_at && (
                            <p className="text-xs text-muted-foreground mt-1">
                              Last reviewed {new Date(app.reviewed_at).toLocaleString()}
                            </p>
                          )}
                          {app.notes && (
                            <div className="mt-3 text-sm bg-secondary/60 border border-border rounded-lg p-3">
                              {app.notes}
                            </div>
                          )}
                        </div>

                        {!locked ? (
                          <div className="flex flex-wrap gap-2 xl:justify-end">
                            <Button size="sm" variant="outline"
                              onClick={() => updateStatus(app.id, "screening")}
                              disabled={statusMutation.isPending || app.status === "screening"}>
                              Screening
                            </Button>
                            <Button size="sm" variant="outline"
                              onClick={() => updateStatus(app.id, "interview")}
                              disabled={statusMutation.isPending || app.status === "interview"}>
                              Interview
                            </Button>
                            <Button size="sm" variant="outline"
                              onClick={() => updateStatus(app.id, "offer")}
                              disabled={statusMutation.isPending || app.status === "offer"}>
                              Offer
                            </Button>
                            <Button size="sm" className="bg-green-600 hover:bg-green-700"
                              onClick={() => updateStatus(app.id, "accepted")}
                              disabled={statusMutation.isPending || app.status === "accepted"}>
                              <CheckCircle className="w-4 h-4 mr-1" /> Accept
                            </Button>
                            <Button size="sm" variant="destructive"
                              onClick={() => updateStatus(app.id, "rejected")}
                              disabled={statusMutation.isPending || app.status === "rejected"}>
                              <XCircle className="w-4 h-4 mr-1" /> Reject
                            </Button>
                          </div>
                        ) : (
                          <span className="text-xs text-muted-foreground italic self-center">
                            Decision finalized
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </section>

          {/* ── Timeline ── */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Interaction Timeline
            </h2>

            {timeline.length === 0 ? (
              <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
                No timeline activity yet.
              </div>
            ) : (
              <div className="relative pl-6 border-l-2 border-border space-y-4">
                {timeline.map((item, index) => (
                  <div key={`${item.type}-${index}`} className="relative">
                    <span className="absolute -left-[1.45rem] top-1 w-3 h-3 rounded-full bg-primary/60 border-2 border-background" />
                    <div className="bg-card border border-border rounded-xl p-4">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                        <Clock className="w-3 h-3" />
                        {item.date ? new Date(item.date).toLocaleString() : "—"}
                        <span className="ml-1 px-2 py-0.5 rounded-full bg-secondary text-xs capitalize">
                          {item.type}
                        </span>
                      </div>
                      <p className="text-sm">{item.description}</p>
                      {item.status && (
                        <span className={`mt-2 inline-block px-2 py-0.5 rounded-full border text-xs font-medium ${statusStyles[item.status] || statusStyles.pending}`}>
                          {statusLabels[item.status] || item.status}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* ── Recruiter Notes ── */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">
              Recruiter Notes
            </h2>

            <div className="bg-card border border-border rounded-xl p-5 mb-4">
              <Textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Write a private recruiter note about this candidate..."
                rows={4}
                className="mb-3"
              />
              <Button type="button" onClick={addNote} disabled={addNoteMutation.isPending}>
                {addNoteMutation.isPending
                  ? <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  : <Plus className="w-4 h-4 mr-2" />}
                Add Note
              </Button>
            </div>

            {notes.length === 0 ? (
              <div className="bg-card border border-border rounded-xl p-8 text-center text-muted-foreground">
                No notes yet.
              </div>
            ) : (
              <div className="space-y-3">
                {notes.map((note) => (
                  <div key={note.id} className="bg-card border border-border rounded-xl p-4">
                    {editingId === note.id ? (
                      <div>
                        <Textarea
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                          rows={3}
                          className="mb-3"
                        />
                        <div className="flex gap-2">
                          <Button size="sm" onClick={() => saveEditedNote(note.id)} disabled={updateNoteMutation.isPending}>Save</Button>
                          <Button size="sm" variant="outline" onClick={() => { setEditingId(null); setEditText(""); }}>Cancel</Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <p className="text-sm whitespace-pre-wrap">{note.content}</p>
                          <p className="text-xs text-muted-foreground mt-2">
                            {note.created_at ? new Date(note.created_at).toLocaleString() : ""}
                          </p>
                        </div>
                        <div className="flex gap-2 shrink-0">
                          <button type="button"
                            onClick={() => { setEditingId(note.id); setEditText(note.content || ""); }}
                            className="text-muted-foreground hover:text-primary">
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button type="button"
                            onClick={() => deleteNoteMutation.mutate(note.id)}
                            className="text-muted-foreground hover:text-red-500">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

        </div>
      )}
    </div>
  );
}
