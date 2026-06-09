"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const STAGES = [
  { id: "planner", label: "Planner" },
  { id: "research", label: "Research" },
  { id: "knowledge_consolidation", label: "Knowledge" },
  { id: "narrative_strategy", label: "Narrative" },
  { id: "draft_writer", label: "Writer" },
  { id: "critique_panel", label: "Critique" },
  { id: "revision_loop", label: "Revision" },
  { id: "approval", label: "Approval" },
];

export function WorkflowPipeline({ currentStage }: { currentStage?: string }) {
  const currentIdx = STAGES.findIndex((s) => s.id === currentStage);

  return (
    <div className="flex flex-wrap items-center gap-2">
      {STAGES.map((stage, idx) => {
        const done = currentIdx > idx;
        const active = stage.id === currentStage;
        return (
          <div key={stage.id} className="flex items-center gap-2">
            <div
              className={cn(
                "flex items-center gap-2 rounded-md border px-3 py-1.5 text-xs",
                active && "border-primary bg-primary/10 text-primary",
                done && !active && "border-emerald-500/30 text-emerald-400",
                !done && !active && "border-border text-muted-foreground",
              )}
            >
              <span
                className={cn(
                  "flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold",
                  active && "bg-primary text-primary-foreground",
                  done && !active && "bg-emerald-500/20",
                  !done && !active && "bg-muted",
                )}
              >
                {idx + 1}
              </span>
              {stage.label}
            </div>
            {idx < STAGES.length - 1 && (
              <span className="text-muted-foreground">→</span>
            )}
          </div>
        );
      })}
      {currentStage && (
        <Badge variant="secondary" className="ml-2">
          {currentStage}
        </Badge>
      )}
    </div>
  );
}
