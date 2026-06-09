"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function PromptWorkspacePage() {
  return (
    <div className="p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Prompt Workspace</h1>
        <p className="text-muted-foreground mt-1">
          Version-controlled prompts per agent role (Phase 2+).
        </p>
      </header>
      <Card>
        <CardHeader>
          <CardTitle>Agent Prompt Registry</CardTitle>
          <CardDescription>
            Centralized, permission-scoped prompts — no monolithic system prompts.
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Planner, Research, Writer, and Critique agents will each maintain isolated prompt
          templates with schema-validated variables. Coming in Phase 2.
        </CardContent>
      </Card>
    </div>
  );
}
