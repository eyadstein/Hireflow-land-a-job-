import React from "react";
import { applications as appsApi } from "@/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import {
  Building2,
  Calendar,
  GripVertical,
  KanbanSquare,
  Lock,
  ShieldCheck,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import PageHeader from "@/components/shared/PageHeader";
import EmptyState from "@/components/shared/EmptyState";

const columns = [
  { id: "pending", label: "Pending", accent: "bg-yellow-500" },
  { id: "applied", label: "Applied", accent: "bg-primary" },
  { id: "screening", label: "Screening", accent: "bg-blue-500" },
  { id: "interview", label: "Interview", accent: "bg-violet-500" },
  { id: "offer", label: "Offer", accent: "bg-emerald-500" },
  { id: "accepted", label: "Accepted", accent: "bg-green-500" },
  { id: "rejected", label: "Rejected", accent: "bg-red-500" },
  { id: "withdrawn", label: "Withdrawn", accent: "bg-gray-500" },
];

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

export default function Tracker() {
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

  const updateMutation = useMutation({
    mutationFn: ({ id, data: payload }) => appsApi.update(id, payload),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["applications"] }),
  });

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const applicationId = Number(result.draggableId);
    const application = appsList.find((app) => app.id === applicationId);

    if (!application) return;

    if (isRecruiterControlled(application)) {
      return;
    }

    const newStatus = result.destination.droppableId;

    if (application.status === newStatus) return;

    updateMutation.mutate({
      id: applicationId,
      data: { status: newStatus },
    });
  };

  if (isLoading) {
    return (
      <div className="p-8 lg:p-12">
        <PageHeader
          eyebrow="Pipeline"
          title="Application Tracker"
          description="Recruiter-controlled applications are locked and updated by recruiters."
        />

        <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-4">
          {columns.map((column) => (
            <div
              key={column.id}
              className="h-64 bg-secondary/50 rounded-xl animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (appsList.length === 0) {
    return (
      <div className="p-8 lg:p-12">
        <PageHeader
          eyebrow="Pipeline"
          title="Application Tracker"
          description="Visualize your job search pipeline. Recruiter decisions appear here automatically."
        />

        <EmptyState
          icon={KanbanSquare}
          title="No applications to track"
          description="Apply to a job or add a manual application to see it here."
        />
      </div>
    );
  }

  return (
    <div className="p-8 lg:p-12">
      <PageHeader
        eyebrow="Pipeline"
        title="Application Tracker"
        description="Drag manual applications to update them. Platform job applications are locked and updated by recruiters."
      />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-6 text-sm">
          {error.message || "Failed to load tracker data."}
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 text-blue-700 rounded-xl p-4 mb-6 text-sm flex gap-2">
        <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
        Recruiter-controlled applications are locked here so the candidate
        cannot overwrite the recruiter decision.
      </div>

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-4 overflow-x-auto">
          {columns.map((column) => {
            const items = appsList.filter(
              (app) => (app.status || "pending") === column.id
            );

            return (
              <Droppable key={column.id} droppableId={column.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`rounded-xl p-3 min-h-[340px] transition-colors duration-200 ${
                      snapshot.isDraggingOver
                        ? "bg-primary/5"
                        : "bg-secondary/40"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-3 px-1">
                      <div className={`w-2 h-2 rounded-full ${column.accent}`} />

                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        {column.label}
                      </span>

                      <Badge
                        variant="secondary"
                        className="ml-auto text-[10px] h-5"
                      >
                        {items.length}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      {items.map((app, index) => {
                        const locked = isRecruiterControlled(app);

                        return (
                          <Draggable
                            key={app.id}
                            draggableId={String(app.id)}
                            index={index}
                            isDragDisabled={locked}
                          >
                            {(dragProvided, dragSnapshot) => (
                              <div
                                ref={dragProvided.innerRef}
                                {...dragProvided.draggableProps}
                                {...dragProvided.dragHandleProps}
                                className={`bg-card border rounded-lg p-3 transition-shadow ${
                                  locked
                                    ? "border-blue-200 bg-blue-50/30"
                                    : "border-border"
                                } ${
                                  dragSnapshot.isDragging
                                    ? "shadow-lg shadow-primary/10 border-primary/30"
                                    : "hover:shadow-sm"
                                }`}
                              >
                                <div className="flex items-start gap-2">
                                  {locked ? (
                                    <Lock className="w-3.5 h-3.5 text-blue-500 mt-0.5 shrink-0" />
                                  ) : (
                                    <GripVertical className="w-3.5 h-3.5 text-muted-foreground/40 mt-0.5 shrink-0" />
                                  )}

                                  <div className="min-w-0 flex-1">
                                    <p className="text-sm font-medium text-foreground truncate">
                                      {getJobTitle(app)}
                                    </p>

                                    <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                                      <Building2 className="w-3 h-3" />
                                      {getCompany(app)}
                                    </p>

                                    {app.applied_date && (
                                      <p className="text-[11px] text-muted-foreground/60 mt-1 flex items-center gap-1">
                                        <Calendar className="w-3 h-3" />
                                        {safeFormatDate(app.applied_date, "MMM d")}
                                      </p>
                                    )}

                                    {app.reviewed_at && (
                                      <p className="text-[11px] text-blue-600 mt-1">
                                        Updated by recruiter{" "}
                                        {safeFormatDate(
                                          app.reviewed_at,
                                          "MMM d"
                                        )}
                                      </p>
                                    )}

                                    {locked && (
                                      <Badge
                                        variant="outline"
                                        className="mt-2 bg-blue-50 text-blue-700 border-blue-200 text-[10px]"
                                      >
                                        Recruiter controlled
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )}
                          </Draggable>
                        );
                      })}

                      {provided.placeholder}
                    </div>
                  </div>
                )}
              </Droppable>
            );
          })}
        </div>
      </DragDropContext>
    </div>
  );
}