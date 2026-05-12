import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { recruiter } from "@/api/client";
import { User, Loader2, ArrowLeft, Plus, Pencil, Trash2, Clock, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export default function CandidateProfile() {
  const { userId } = useParams();
  const navigate   = useNavigate();
  const qc         = useQueryClient();

  const [noteText,    setNoteText]    = useState("");
  const [editingId,   setEditingId]   = useState(null);
  const [editText,    setEditText]    = useState("");

  const { data: profile,  isLoading: pLoad } = useQuery({ queryKey: ["r-cprofile",   userId], queryFn: () => recruiter.candidateProfile(userId) });
  const { data: timeline, isLoading: tLoad } = useQuery({ queryKey: ["r-ctimeline",  userId], queryFn: () => recruiter.candidateTimeline(userId) });
  const { data: notes,    isLoading: nLoad } = useQuery({ queryKey: ["r-cnotes",     userId], queryFn: () => recruiter.candidateNotes(userId) });

  const addMutation = useMutation({
    mutationFn: (text) => recruiter.addNote(userId, text),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["r-cnotes", userId] }); setNoteText(""); },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, text }) => recruiter.updateNote(id, text),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["r-cnotes", userId] }); setEditingId(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => recruiter.deleteNote(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["r-cnotes", userId] }),
  });

  const loading = pLoad || tLoad || nLoad;

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-6 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back
      </button>

      <div className="mb-8">
        <p className="text-primary font-semibold tracking-[0.25em] text-xs uppercase mb-3">Candidate Insight</p>
        <h1 className="text-4xl font-black flex items-center gap-3">
          <User className="w-8 h-8 text-primary" />
          {profile ? (profile.username) : "Candidate Profile"}
        </h1>
        {profile && <p className="text-muted-foreground mt-2">{profile.email}</p>}
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      ) : (
        <div className="space-y-8">

          {/* Stats */}
          {profile && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { label: "Total Applications", value: profile.total_applications },
                { label: "Pending",   value: profile.pending },
                { label: "Accepted",  value: profile.accepted },
                { label: "Rejected",  value: profile.rejected },
                { label: "Notes",     value: profile.notes_count },
              ].map((s) => (
                <div key={s.label} className="bg-card border border-border rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold">{s.value}</p>
                  <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
                </div>
              ))}
            </div>
          )}

          {/* Applications list */}
          {profile?.applications?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Applications to Your Jobs</h2>
              <div className="space-y-2">
                {profile.applications.map((app) => (
                  <div key={app.id} className="bg-card border border-border rounded-xl p-4 flex justify-between items-center gap-4">
                    <div className="flex items-center gap-3">
                      <FileText className="w-4 h-4 text-muted-foreground shrink-0" />
                      <div>
                        <p className="font-medium text-sm">{app.job_title || `Job #${app.job}`}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(app.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      app.status === "accepted" ? "bg-green-100 text-green-700" :
                      app.status === "rejected" ? "bg-red-100 text-red-600" :
                      "bg-secondary text-muted-foreground"
                    }`}>
                      {app.status}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Timeline */}
          {timeline?.timeline?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Interaction Timeline</h2>
              <div className="relative pl-6 border-l-2 border-border space-y-4">
                {timeline.timeline.map((item, i) => (
                  <div key={i} className="relative">
                    <span className="absolute -left-[1.45rem] top-1 w-3 h-3 rounded-full bg-primary/60 border-2 border-background" />
                    <div className="bg-card border border-border rounded-xl p-4">
                      <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                        <Clock className="w-3 h-3" />
                        {new Date(item.date).toLocaleString()}
                        <span className="ml-1 px-2 py-0.5 rounded-full bg-secondary text-xs capitalize">{item.type}</span>
                      </div>
                      <p className="text-sm">{item.description}</p>
                      {item.status && (
                        <span className="mt-1 inline-block text-xs text-primary">{item.status}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Notes */}
          <section>
            <h2 className="text-xs font-semibold uppercase tracking-[0.15em] text-muted-foreground mb-4">Your Notes</h2>

            <div className="bg-card border border-border rounded-xl p-5 mb-4 space-y-3">
              <Textarea
                placeholder="Add a private note about this candidate…"
                rows={3}
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
              />
              <Button
                onClick={() => { if (noteText.trim()) addMutation.mutate(noteText.trim()); }}
                disabled={addMutation.isPending || !noteText.trim()}
                size="sm"
              >
                {addMutation.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
                Add Note
              </Button>
            </div>

            {nLoad ? (
              <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
            ) : notes?.length === 0 ? (
              <p className="text-sm text-muted-foreground">No notes yet.</p>
            ) : (
              <div className="space-y-3">
                {notes.map((note) => (
                  <div key={note.id} className="bg-card border border-border rounded-xl p-4">
                    {editingId === note.id ? (
                      <div className="space-y-2">
                        <Textarea
                          rows={3}
                          value={editText}
                          onChange={(e) => setEditText(e.target.value)}
                        />
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => updateMutation.mutate({ id: note.id, text: editText })}
                            disabled={updateMutation.isPending}
                          >
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setEditingId(null)}>Cancel</Button>
                        </div>
                      </div>
                    ) : (
                      <div className="flex justify-between gap-3">
                        <p className="text-sm">{note.content}</p>
                        <div className="flex gap-2 shrink-0">
                          <button
                            onClick={() => { setEditingId(note.id); setEditText(note.content); }}
                            className="text-muted-foreground hover:text-primary transition"
                          >
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => deleteMutation.mutate(note.id)}
                            className="text-muted-foreground hover:text-red-500 transition"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-2">
                      {new Date(note.created_at).toLocaleString()}
                    </p>
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
