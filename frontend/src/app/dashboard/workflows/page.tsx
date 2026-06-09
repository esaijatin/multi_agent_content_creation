"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { WorkflowExecutionPanel } from "@/components/workflow-execution-panel";
import {
  apiFetch,
  type WorkflowLogEntry,
  type WorkflowState,
} from "@/lib/api";

function WorkflowsContent() {
  const params = useSearchParams();
  const projectId = params.get("project") || "";
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [state, setState] = useState<WorkflowState | null>(null);
  const [logs, setLogs] = useState<WorkflowLogEntry[]>([]);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [prompt, setPrompt] = useState(
    "Create a 10-minute YouTube video script about building secure multi-agent AI systems for enterprise teams.",
  );
  const token = typeof window !== "undefined" ? localStorage.getItem("astraos_token") : null;

  const poll = useCallback(async () => {
    if (!token || !workflowId) return;
    try {
      const [st, lg] = await Promise.all([
        apiFetch<WorkflowState>(`/api/v1/workflow/${workflowId}/state`, token),
        apiFetch<WorkflowLogEntry[]>(`/api/v1/workflow/${workflowId}/logs`, token),
      ]);
      setState(st);
      setLogs(lg);
    } catch {
      /* ignore transient poll errors */
    }
  }, [token, workflowId]);

  async function startWorkflow() {
    if (!token || !projectId) return;
    setStarting(true);
    setError(null);
    try {
      const wf = await apiFetch<{ id: string }>("/api/v1/workflow/start", token, {
        method: "POST",
        body: JSON.stringify({
          project_id: projectId,
          content_request: {
            prompt,
            platform: "youtube",
            audience: "engineering leaders",
            tone: "authoritative",
            complexity: "high",
          },
        }),
      });
      setWorkflowId(wf.id);
      setState(null);
      setLogs([]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start workflow");
    } finally {
      setStarting(false);
    }
  }

  useEffect(() => {
    if (!workflowId) return;
    poll();
    const interval = setInterval(poll, 2000);
    return () => clearInterval(interval);
  }, [workflowId, poll]);

  const terminal = state && ["completed", "failed", "cancelled"].includes(state.status);

  return (
    <div className="p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Workflow Execution</h1>
        <p className="text-muted-foreground mt-1">
          Async orchestration with Ollama-powered planner and writer agents. State persists in
          Redis checkpoints.
        </p>
      </header>

      {!projectId && (
        <p className="text-amber-400 text-sm">
          Select a project from the dashboard to start a workflow.
        </p>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Start Content Workflow</CardTitle>
          <CardDescription>
            Returns immediately with workflow ID — execution runs in the background.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={4}
            className="w-full rounded-md border border-input bg-background p-3 text-sm"
          />
          <Button onClick={startWorkflow} disabled={!projectId || starting}>
            {starting ? "Queuing…" : "Execute Workflow"}
          </Button>
          {error && <p className="text-sm text-red-400">{error}</p>}
        </CardContent>
      </Card>

      {workflowId && state && (
        <WorkflowExecutionPanel state={state} logs={logs} workflowId={workflowId} />
      )}

      {workflowId && !state && (
        <p className="text-sm text-muted-foreground animate-pulse">
          Workflow queued — polling for execution state…
        </p>
      )}

      {terminal && (
        <p className="text-sm text-muted-foreground">
          Workflow reached terminal state. Polling slowed; refresh page to inspect final snapshot.
        </p>
      )}
    </div>
  );
}

export default function WorkflowsPage() {
  return (
    <Suspense fallback={<div className="p-8">Loading…</div>}>
      <WorkflowsContent />
    </Suspense>
  );
}
