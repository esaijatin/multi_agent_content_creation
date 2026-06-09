"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import Link from "next/link";

type Project = {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
};

export default function ProjectsDashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("astraos_token") : null;

  useEffect(() => {
    if (!token) return;
    apiFetch<Project[]>("/api/v1/projects", token)
      .then(setProjects)
      .catch(() => setProjects([]));
  }, [token]);

  async function createProject() {
    if (!token || !name.trim()) return;
    const project = await apiFetch<Project>("/api/v1/projects", token, {
      method: "POST",
      body: JSON.stringify({ name, description: "" }),
    });
    setProjects((p) => [project, ...p]);
    setName("");
  }

  return (
    <div className="p-8 space-y-8">
      <header>
        <h1 className="text-2xl font-bold tracking-tight">Project Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Manage content creation projects and orchestrated workflows.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Projects</CardDescription>
            <CardTitle className="text-3xl">{projects.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Platform</CardDescription>
            <CardTitle className="text-lg">AstraOS v0.1</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="success">Phase 2</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Orchestrator</CardDescription>
            <CardTitle className="text-lg">LangGraph</CardTitle>
          </CardHeader>
          <CardContent>
            <Badge variant="secondary">Deterministic DAG</Badge>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New Project</CardTitle>
          <CardDescription>Create a project to attach content workflows.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Project name"
            className="flex h-10 flex-1 rounded-md border border-input bg-background px-3 text-sm"
          />
          <Button onClick={createProject}>Create</Button>
        </CardContent>
      </Card>

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Projects</h2>
        {projects.length === 0 ? (
          <p className="text-sm text-muted-foreground">No projects yet.</p>
        ) : (
          projects.map((p) => (
            <Card key={p.id}>
              <CardContent className="flex items-center justify-between py-4">
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-xs text-muted-foreground font-mono">{p.id}</p>
                </div>
                <Link href={`/dashboard/workflows?project=${p.id}`}>
                  <Button variant="outline" size="sm">
                    Start Workflow
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
