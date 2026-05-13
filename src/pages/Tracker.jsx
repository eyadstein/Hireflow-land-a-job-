import React from "react";
import { applications as appsApi } from "@/api/client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { motion } from "framer-motion";
import { Building2, Calendar, GripVertical, KanbanSquare } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { format } from "date-fns";
import PageHeader from "@/components/shared/PageHeader";
import EmptyState from "@/components/shared/EmptyState";

const columns = [
  { id: "applied",   label: "Applied",   accent: "bg-primary" },
  { id: "screening", label: "Screening", accent: "bg-amber-500" },
  { id: "interview", label: "Interview", accent: "bg-violet-500" },
  { id: "offer",     label: "Offer",     accent: "bg-emerald-500" },
  { id: "accepted",  label: "Accepted",  accent: "bg-green-500" },
  { id: "rejected",  label: "Rejected",  accent: "bg-red-500" },
];

export default function Tracker() {
  const queryClient = useQueryClient();

  const { data: appsList = [], isLoading } = useQuery({
    queryKey: ["applications"],
    queryFn: appsApi.mine,
    refetchInterval: 30000,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => appsApi.update(id, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["applications"] }),
  });

  const onDragEnd = (result) => {
    if (!result.destination) return;
    const { draggableId, destination } = result;
    const newStatus = destination.droppableId;
    updateMutation.mutate({ id: parseInt(draggableId), data: { status: newStatus } });
  };

  if (isLoading) {
    return (
      <div className="p-8 lg:p-12">
        <PageHeader eyebrow="Pipeline" title="Application Tracker" />
        <div className="grid grid-cols-6 gap-4">
          {columns.map((col) => (
            <div key={col.id} className="h-64 bg-secondary/50 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (appsList.length === 0) {
    return (
      <div className="p-8 lg:p-12">
        <PageHeader eyebrow="Pipeline" title="Application Tracker" description="Visualize your job search pipeline with drag-and-drop cards." />
        <EmptyState
          icon={KanbanSquare}
          title="No applications to track"
          description="Add applications from the Applications page to see them here."
        />
      </div>
    );
  }

  return (
    <div className="p-8 lg:p-12">
      <PageHeader
        eyebrow="Pipeline"
        title="Application Tracker"
        description="Drag and drop to update application status."
      />

      <DragDropContext onDragEnd={onDragEnd}>
        <div className="grid grid-cols-2 lg:grid-cols-6 gap-4 overflow-x-auto">
          {columns.map((col) => {
            const items = appsList.filter((a) => (a.status || "applied") === col.id);
            return (
              <Droppable key={col.id} droppableId={col.id}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`rounded-xl p-3 min-h-[320px] transition-colors duration-200 ${
                      snapshot.isDraggingOver ? "bg-primary/5" : "bg-secondary/40"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-3 px-1">
                      <div className={`w-2 h-2 rounded-full ${col.accent}`} />
                      <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        {col.label}
                      </span>
                      <Badge variant="secondary" className="ml-auto text-[10px] h-5">
                        {items.length}
                      </Badge>
                    </div>

                    <div className="space-y-2">
                      {items.map((app, index) => (
                        <Draggable key={app.id} draggableId={String(app.id)} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`bg-card border border-border rounded-lg p-3 transition-shadow ${
                                snapshot.isDragging ? "shadow-lg shadow-primary/10 border-primary/30" : "hover:shadow-sm"
                              }`}
                            >
                              <div className="flex items-start gap-2">
                                <GripVertical className="w-3.5 h-3.5 text-muted-foreground/40 mt-0.5 shrink-0" />
                                <div className="min-w-0 flex-1">
                                  <p className="text-sm font-medium text-foreground truncate">{app.job_title}</p>
                                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                                    <Building2 className="w-3 h-3" /> {app.company}
                                  </p>
                                  {app.applied_date && (
                                    <p className="text-[11px] text-muted-foreground/60 mt-1 flex items-center gap-1">
                                      <Calendar className="w-3 h-3" />
                                      {format(new Date(app.applied_date), "MMM d")}
                                    </p>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}
                        </Draggable>
                      ))}
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
