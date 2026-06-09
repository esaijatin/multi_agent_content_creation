"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const AGENTS = [
  { name: "Planner", permissions: "read workflow", status: "active" },
  { name: "Research", permissions: "internet, RAG", status: "stub" },
  { name: "Knowledge Consolidation", permissions: "read research", status: "stub" },
  { name: "Narrative Strategist", permissions: "read knowledge", status: "stub" },
  { name: "Draft Writer", permissions: "retrieval only", status: "stub" },
  { name: "Fact Checker", permissions: "read-only", status: "stub" },
  { name: "Engagement Critic", permissions: "read-only", status: "stub" },
  { name: "Style Critic", permissions: "read-only", status: "stub" },
  { name: "Platform Optimizer", permissions: "read-only", status: "stub" },
];

export default function AgentActivityPage() {
  return (
    <div className="p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Agent Activity Monitoring</h1>
        <p className="text-muted-foreground mt-1">
          Isolated microservice-style agents with explicit permission scopes.
        </p>
      </header>
      <div className="grid gap-3">
        {AGENTS.map((agent) => (
          <Card key={agent.name}>
            <CardContent className="flex items-center justify-between py-4">
              <div>
                <CardTitle className="text-base">{agent.name}</CardTitle>
                <p className="text-xs text-muted-foreground mt-1">{agent.permissions}</p>
              </div>
              <Badge variant={agent.status === "active" ? "success" : "secondary"}>
                {agent.status}
              </Badge>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
