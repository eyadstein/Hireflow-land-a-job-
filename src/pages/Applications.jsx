import React, { useState } from "react";
import { applications as appsApi } from "@/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus,
  FileText,
  Building2,
  Calendar,
  MoreHorizontal,
  Pencil,
  Trash2,
  Clock,
  XCircle,
  Users,
  Send,
  Award,
  CheckCircle2,
  ShieldCheck,
  Eye,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { format } from "date-fns";
import PageHeader from "@/components/shared/PageHeader";
import EmptyState from "@/components/shared/EmptyState";

const statusConfig = {
  pending: {
    label: "Pending",
    icon: Clock,
    color: "bg-yellow-100 text-yellow-700 border-yellow-200",
  },
  applied: {
    label: "Applied",
    icon: Send,
    color: "bg-primary/10 text-primary border-primary/20",
  },
  screening: {
    label: "Screening",
    icon: Eye,
    color: "bg-blue-100 text-blue-700 border-blue-200",
  },
  interview: {
    label: "Interview",
    icon: Users,
    color: "bg-violet-100 text-violet-700 border-violet-200",
  },
  offer: {
    label: "Offer",
    icon: Award,
    color: "bg-emerald-100 text-emerald-700 border-emerald-200",
  },
  accepted: {
    label: "Accepted",
    icon: CheckCircle2,
    color: "bg-green-100 text-green-700 border-green-200",
  },
  rejected: {
    label: "Rejected",
    icon: XCircle,
    color: "bg-red-100 text-red-600 border-red-200",
  },
  withdrawn: {
    label: "Withdrawn",
    icon: XCircle,
    color: "bg-secondary text-muted-foreground border-border",
  },
};

const emptyForm = {
  job_title: "",
  company: "",
  status: "applied",
  applied_date: new Date().toISOString().split("T")[0],
  notes: "",
  contact_name: "",
  contact_email: "",
};

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function getJobTitle(app) {
  return app.job_display_title || app.job_title || "Untitled Job";
}

function getCompany(app) {
  return app.company_display_name || app.company || "Unknown Company";
}

function getStatus(app) {
  return statusConfig[app.status] || statusConfig.pending;
}

function isRecruiterControlled(app) {
  return !!app.job;
}

function safeFormatDate(dateValue, formatString) {
  if (!dateValue) return null;

  try {
    return format(new Date(dateValue), formatString);
  } catch {
    return dateValue;
  }
}

export default function Applications() {
  const [showDialog, setShowDialog] = useState(false);
  const [editingApp, setEditingApp] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [statusFilter, setStatusFilter] = useState("all");
  const [message, setMessage] = useState("");

  const queryClient = useQueryClient();

  const {
    data,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["applications"],
    queryFn: appsApi.mine,
    refetchInterval: 10000,
  });

  const appsList = normalizeList(data);

  const createMutation = useMutation({
    mutationFn: (payload) => appsApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      setMessage("Application added successfully.");
      closeDialog();
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to add application.");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data: payload }) => appsApi.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      setMessage("Application updated successfully.");
      closeDialog();
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to update application.");
    },
  });

  const withdrawMutation = useMutation({
    mutationFn: (id) => appsApi.update(id, { status: "withdrawn" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      setMessage("Application withdrawn.");
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to withdraw application.");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => appsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
      setMessage("Manual application deleted.");
    },
    onError: (err) => {
      setMessage(err?.message || "Failed to delete application.");
    },
  });

  const closeDialog = () => {
    setShowDialog(false);
    setEditingApp(null);
    setForm(emptyForm);
  };

  const openAdd = () => {
    setEditingApp(null);
    setForm(emptyForm);
    setMessage("");
    setShowDialog(true);
  };

  const openEdit = (app) => {
    setEditingApp(app);
    setMessage("");

    setForm({
      job_title: getJobTitle(app),
      company: getCompany(app),
      status: app.status || "applied",
      applied_date:
        app.applied_date ||
        (app.created_at ? app.created_at.split("T")[0] : ""),
      notes: app.notes || "",
      contact_name: app.contact_name || "",
      contact_email: app.contact_email || "",
    });

    setShowDialog(true);
  };

  const handleSubmit = () => {
    if (!form.job_title || !form.company) return;

    if (editingApp) {
      const payload = isRecruiterControlled(editingApp)
        ? {
            notes: form.notes,
            contact_name: form.contact_name,
            contact_email: form.contact_email,
          }
        : form;

      updateMutation.mutate({
        id: editingApp.id,
        data: payload,
      });
    } else {
      createMutation.mutate(form);
    }
  };

  const filtered =
    statusFilter === "all"
      ? appsList
      : appsList.filter((app) => app.status === statusFilter);

  const counts = {
    total: appsList.length,
    active: appsList.filter((app) =>
      ["pending", "applied", "screening", "interview", "offer"].includes(
        app.status
      )
    ).length,
    accepted: appsList.filter((app) => app.status === "accepted").length,
    rejected: appsList.filter((app) => app.status === "rejected").length,
    withdrawn: appsList.filter((app) => app.status === "withdrawn").length,
  };

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <PageHeader
        eyebrow="Manage"
        title="Applications"
        description="Track every opportunity. Recruiter decisions update here automatically."
        actions={
          <Button onClick={openAdd}>
            <Plus className="w-4 h-4 mr-2" />
            Add Manual Application
          </Button>
        }
      />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {error.message || "Failed to load applications."}
        </div>
      )}

      {message && (
        <div className="bg-secondary border border-border rounded-xl p-4 mb-6 text-sm">
          {message}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-black">{counts.total}</p>
          <p className="text-xs text-muted-foreground mt-1">Total</p>
        </div>

        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-black text-blue-600">{counts.active}</p>
          <p className="text-xs text-muted-foreground mt-1">Active</p>
        </div>

        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-black text-green-600">
            {counts.accepted}
          </p>
          <p className="text-xs text-muted-foreground mt-1">Accepted</p>
        </div>

        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-black text-red-600">{counts.rejected}</p>
          <p className="text-xs text-muted-foreground mt-1">Rejected</p>
        </div>

        <div className="bg-card border border-border rounded-xl p-4 text-center">
          <p className="text-2xl font-black">{counts.withdrawn}</p>
          <p className="text-xs text-muted-foreground mt-1">Withdrawn</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        <button
          type="button"
          onClick={() => setStatusFilter("all")}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
            statusFilter === "all"
              ? "bg-foreground text-background"
              : "bg-secondary text-muted-foreground hover:text-foreground"
          }`}
        >
          All ({appsList.length})
        </button>

        {Object.entries(statusConfig).map(([key, config]) => {
          const count = appsList.filter((app) => app.status === key).length;

          return (
            <button
              key={key}
              type="button"
              onClick={() => setStatusFilter(key)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1.5 ${
                statusFilter === key
                  ? "bg-foreground text-background"
                  : "bg-secondary text-muted-foreground hover:text-foreground"
              }`}
            >
              {config.label} ({count})
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="h-24 rounded-xl bg-card border border-border animate-pulse"
            />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No applications found"
          description="Apply to a platform job or add a manual application."
          actionLabel="Add Manual Application"
          onAction={openAdd}
        />
      ) : (
        <div className="space-y-3">
          <AnimatePresence>
            {filtered.map((app, index) => {
              const status = getStatus(app);
              const StatusIcon = status.icon;
              const recruiterControlled = isRecruiterControlled(app);

              return (
                <motion.div
                  key={app.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.25, delay: index * 0.02 }}
                  className="group bg-card border border-border rounded-xl p-4 hover:border-primary/20 transition-all duration-200"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-semibold text-foreground truncate">
                          {getJobTitle(app)}
                        </h3>

                        <Badge
                          variant="outline"
                          className={`${status.color} text-[11px] font-medium border shrink-0`}
                        >
                          <StatusIcon className="w-3 h-3 mr-1" />
                          {status.label}
                        </Badge>

                        {recruiterControlled && (
                          <Badge
                            variant="outline"
                            className="bg-blue-50 text-blue-700 border-blue-200 text-[11px]"
                          >
                            <ShieldCheck className="w-3 h-3 mr-1" />
                            Recruiter controlled
                          </Badge>
                        )}
                      </div>

                      <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5" />
                          {getCompany(app)}
                        </span>

                        {app.applied_date && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {safeFormatDate(app.applied_date, "MMM d, yyyy")}
                          </span>
                        )}
                      </div>

                      {app.reviewed_at && (
                        <p className="text-xs text-muted-foreground mt-2">
                          Recruiter updated this application on{" "}
                          {safeFormatDate(app.reviewed_at, "MMM d, yyyy h:mm a")}
                        </p>
                      )}

                      {app.notes && (
                        <div className="mt-3 text-sm bg-secondary/60 border border-border rounded-lg p-3">
                          {app.notes}
                        </div>
                      )}
                    </div>

                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="shrink-0 opacity-100 md:opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>

                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => openEdit(app)}>
                          <Pencil className="w-4 h-4 mr-2" />
                          Edit notes
                        </DropdownMenuItem>

                        {recruiterControlled ? (
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => withdrawMutation.mutate(app.id)}
                            disabled={app.status === "withdrawn"}
                          >
                            <XCircle className="w-4 h-4 mr-2" />
                            Withdraw
                          </DropdownMenuItem>
                        ) : (
                          <DropdownMenuItem
                            className="text-destructive"
                            onClick={() => deleteMutation.mutate(app.id)}
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      )}

      <Dialog open={showDialog} onOpenChange={closeDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingApp
                ? isRecruiterControlled(editingApp)
                  ? "Edit Application Notes"
                  : "Edit Manual Application"
                : "New Manual Application"}
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2">
            {editingApp && isRecruiterControlled(editingApp) && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 rounded-xl p-3 text-sm">
                This application is linked to a platform job. The recruiter
                controls the hiring status. You can edit your notes/contact
                fields only.
              </div>
            )}

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Job Title *
              </label>
              <Input
                value={form.job_title}
                disabled={editingApp && isRecruiterControlled(editingApp)}
                onChange={(event) =>
                  setForm({ ...form, job_title: event.target.value })
                }
                placeholder="e.g. Senior Frontend Engineer"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">
                Company *
              </label>
              <Input
                value={form.company}
                disabled={editingApp && isRecruiterControlled(editingApp)}
                onChange={(event) =>
                  setForm({ ...form, company: event.target.value })
                }
                placeholder="e.g. Google"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Status
                </label>

                <Select
                  value={form.status}
                  disabled={editingApp && isRecruiterControlled(editingApp)}
                  onValueChange={(value) =>
                    setForm({ ...form, status: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>

                  <SelectContent>
                    {Object.entries(statusConfig).map(([key, config]) => (
                      <SelectItem key={key} value={key}>
                        {config.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Applied Date
                </label>

                <Input
                  type="date"
                  value={form.applied_date}
                  disabled={editingApp && isRecruiterControlled(editingApp)}
                  onChange={(event) =>
                    setForm({ ...form, applied_date: event.target.value })
                  }
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-1.5 block">Notes</label>
              <Textarea
                value={form.notes}
                onChange={(event) =>
                  setForm({ ...form, notes: event.target.value })
                }
                placeholder="Add your notes..."
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Contact Name
                </label>
                <Input
                  value={form.contact_name}
                  onChange={(event) =>
                    setForm({ ...form, contact_name: event.target.value })
                  }
                  placeholder="Recruiter name"
                />
              </div>

              <div>
                <label className="text-sm font-medium mb-1.5 block">
                  Contact Email
                </label>
                <Input
                  value={form.contact_email}
                  onChange={(event) =>
                    setForm({ ...form, contact_email: event.target.value })
                  }
                  placeholder="recruiter@company.com"
                />
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>
              Cancel
            </Button>

            <Button
              onClick={handleSubmit}
              disabled={
                !form.job_title ||
                !form.company ||
                createMutation.isPending ||
                updateMutation.isPending
              }
            >
              {editingApp ? "Save Changes" : "Add Application"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}