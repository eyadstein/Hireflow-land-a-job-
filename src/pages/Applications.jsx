import React, { useState } from "react";
import { applications as appsApi } from "@/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import {
  Plus, FileText, Building2, Calendar, MoreHorizontal, Pencil,
  Trash2, CheckCircle2, Clock, XCircle, Users, Send, Award,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { format } from "date-fns";
import PageHeader from "@/components/shared/PageHeader";
import EmptyState from "@/components/shared/EmptyState";

const statusConfig = {
  applied:   { label: "Applied",   icon: Send,         color: "bg-primary/10 text-primary border-primary/20" },
  screening: { label: "Screening", icon: Clock,        color: "bg-amber-100 text-amber-700 border-amber-200" },
  interview: { label: "Interview", icon: Users,        color: "bg-violet-100 text-violet-700 border-violet-200" },
  offer:     { label: "Offer",     icon: Award,        color: "bg-emerald-100 text-emerald-700 border-emerald-200" },
  rejected:  { label: "Rejected",  icon: XCircle,      color: "bg-red-100 text-red-600 border-red-200" },
  withdrawn: { label: "Withdrawn", icon: XCircle,      color: "bg-secondary text-muted-foreground border-border" },
};

const emptyForm = {
  job_title: "", company: "", status: "applied",
  applied_date: new Date().toISOString().split("T")[0],
  notes: "", contact_name: "", contact_email: "",
};

export default function Applications() {
  const [showDialog, setShowDialog] = useState(false);
  const [editingApp, setEditingApp] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [statusFilter, setStatusFilter] = useState("all");
  const queryClient = useQueryClient();

  const { data: appsList = [], isLoading } = useQuery({
    queryKey: ["applications"],
    queryFn: () => appsApi.list(),
  });

  const createMutation = useMutation({
    mutationFn: (data) => appsApi.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["applications"] }); closeDialog(); },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => appsApi.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["applications"] }); closeDialog(); },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => appsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applications"] }),
  });

  const closeDialog = () => { setShowDialog(false); setEditingApp(null); setForm(emptyForm); };

  const openEdit = (app) => {
    setEditingApp(app);
    setForm({
      job_title: app.job_title || "",
      company: app.company || "",
      status: app.status || "applied",
      applied_date: app.applied_date || "",
      notes: app.notes || "",
      contact_name: app.contact_name || "",
      contact_email: app.contact_email || "",
    });
    setShowDialog(true);
  };

  const handleSubmit = () => {
    if (!form.job_title || !form.company) return;
    if (editingApp) {
      updateMutation.mutate({ id: editingApp.id, data: form });
    } else {
      createMutation.mutate(form);
    }
  };

  const filtered = statusFilter === "all"
    ? appsList
    : appsList.filter((a) => a.status === statusFilter);

  return (
    <div className="p-8 lg:p-12 w-full max-w-[1600px]">
      <PageHeader
        eyebrow="Manage"
        title="Applications"
        description="Track every opportunity from application to offer."
        actions={
          <Button onClick={() => { setForm(emptyForm); setShowDialog(true); }}>
            <Plus className="w-4 h-4 mr-2" /> Add Application
          </Button>
        }
      />

      <div className="flex flex-wrap gap-2 mb-6">
        <button
          onClick={() => setStatusFilter("all")}
          className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
            statusFilter === "all" ? "bg-foreground text-background" : "bg-secondary text-muted-foreground hover:text-foreground"
          }`}
        >
          All ({appsList.length})
        </button>
        {Object.entries(statusConfig).map(([key, config]) => {
          const count = appsList.filter((a) => a.status === key).length;
          return (
            <button
              key={key}
              onClick={() => setStatusFilter(key)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1.5 ${
                statusFilter === key ? "bg-foreground text-background" : "bg-secondary text-muted-foreground hover:text-foreground"
              }`}
            >
              {config.label} ({count})
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 rounded-xl bg-card border border-border animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon={FileText}
          title="No applications yet"
          description="Start tracking your job applications to stay organized."
          actionLabel="Add Application"
          onAction={() => { setForm(emptyForm); setShowDialog(true); }}
        />
      ) : (
        <div className="space-y-2">
          <AnimatePresence>
            {filtered.map((app, i) => {
              const status = statusConfig[app.status] || statusConfig.applied;
              const StatusIcon = status.icon;
              return (
                <motion.div
                  key={app.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.25, delay: i * 0.02 }}
                  className="group bg-card border border-border rounded-xl p-4 hover:border-primary/20 transition-all duration-200"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-foreground truncate">{app.job_title}</h3>
                        <Badge variant="outline" className={`${status.color} text-[11px] font-medium border shrink-0`}>
                          <StatusIcon className="w-3 h-3 mr-1" />
                          {status.label}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 mt-1 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5" /> {app.company}
                        </span>
                        {app.applied_date && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" /> {format(new Date(app.applied_date), "MMM d, yyyy")}
                          </span>
                        )}
                      </div>
                    </div>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                          <MoreHorizontal className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => openEdit(app)}>
                          <Pencil className="w-4 h-4 mr-2" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive" onClick={() => deleteMutation.mutate(app.id)}>
                          <Trash2 className="w-4 h-4 mr-2" /> Delete
                        </DropdownMenuItem>
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
            <DialogTitle>{editingApp ? "Edit Application" : "New Application"}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Job Title *</label>
              <Input value={form.job_title} onChange={(e) => setForm({ ...form, job_title: e.target.value })} placeholder="e.g. Senior Frontend Engineer" />
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Company *</label>
              <Input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} placeholder="e.g. Google" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Status</label>
                <Select value={form.status} onValueChange={(v) => setForm({ ...form, status: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {Object.entries(statusConfig).map(([k, v]) => (
                      <SelectItem key={k} value={k}>{v.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Applied Date</label>
                <Input type="date" value={form.applied_date} onChange={(e) => setForm({ ...form, applied_date: e.target.value })} />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Notes</label>
              <Textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} placeholder="Add any notes..." rows={3} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1.5 block">Contact Name</label>
                <Input value={form.contact_name} onChange={(e) => setForm({ ...form, contact_name: e.target.value })} placeholder="Recruiter name" />
              </div>
              <div>
                <label className="text-sm font-medium mb-1.5 block">Contact Email</label>
                <Input value={form.contact_email} onChange={(e) => setForm({ ...form, contact_email: e.target.value })} placeholder="recruiter@company.com" />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={closeDialog}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={!form.job_title || !form.company || createMutation.isPending || updateMutation.isPending}>
              {editingApp ? "Save Changes" : "Add Application"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
