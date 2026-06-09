"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { WorkflowLogEntry, WorkflowState, WorkflowStatus } from "@/lib/api";
import { cn } from "@/lib/utils";
import { WorkflowPipeline } from "@/components/workflow-pipeline";

function statusVariant(
  status: WorkflowStatus,
): "default" | "secondary" | "success" | "warning" | "danger" {
  switch (status) {
    case "completed":
      return "success";
    case "failed":
      return "danger";
    case "awaiting_approval":
    case "awaiting_revision":
      return "warning";
    case "running":
    case "queued":
      return "default";
    default:
      return "secondary";
  }
}

function formatTokens(usage?: Record<string, number>) {
  if (!usage || Object.keys(usage).length === 0) return "—";
  const prompt = usage.prompt_tokens ?? 0;
  const completion = usage.completion_tokens ?? 0;
  return `${prompt + completion} total (${prompt} in / ${completion} out)`;
}

export function WorkflowExecutionPanel({
  state,
  logs,
  workflowId,
}: {
  state: WorkflowState;
  logs: WorkflowLogEntry[];
  workflowId: string;
}) {
  const draft =
    (state.state?.draft as string) ||
    (state.state?.writer_output as { markdown?: string })?.markdown ||
    "";
  const plan = state.state?.planner_output as Record<string, unknown> | undefined;
  const isActive = ["queued", "running", "awaiting_revision", "revising"].includes(state.status);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <CardTitle>Execution Progress</CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={statusVariant(state.status)}>{state.status}</Badge>
              {isActive && (
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-primary opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-primary" />
                </span>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <WorkflowPipeline currentStage={state.current_stage || undefined} />
          <div className="grid gap-3 text-sm md:grid-cols-4">
            <div>
              <p className="text-muted-foreground">Iteration</p>
              <p className="font-mono">{state.iteration_count}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Token usage</p>
              <p className="font-mono text-xs">{formatTokens(state.token_usage_total)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Workflow ID</p>
              <p className="font-mono text-xs truncate">{workflowId}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Stage</p>
              <p className="font-mono">{state.current_stage || "—"}</p>
            </div>
          </div>
          {state.error_message && (
            <p className="text-sm text-red-400">Error: {state.error_message}</p>
          )}
        </CardContent>
      </Card>

      {plan && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Planner Output</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-48 overflow-auto rounded-md bg-muted p-3 text-xs">
              {JSON.stringify(plan, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}

      {draft && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Generated Draft</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded-md bg-muted p-4 text-sm">
              {draft}
            </pre>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Execution Log</CardTitle>
        </CardHeader>
        <CardContent>
          {logs.length === 0 ? (
            <p className="text-sm text-muted-foreground">Waiting for orchestration events…</p>
          ) : (
            <ul className="space-y-2">
              {logs.map((log, i) => (
                <li
                  key={`${log.timestamp}-${i}`}
                  className={cn(
                    "rounded-md border border-border px-3 py-2 text-xs",
                    log.error && "border-red-500/40 bg-red-500/5",
                  )}
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-medium text-foreground">
                      [{log.stage}] {log.agent || "system"}
                    </span>
                    {log.duration_ms != null && (
                      <span className="text-muted-foreground">{log.duration_ms}ms</span>
                    )}
                  </div>
                  <p className="mt-1 text-muted-foreground">{log.message}</p>
                  {log.error && <p className="mt-1 text-red-400">{log.error}</p>}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
