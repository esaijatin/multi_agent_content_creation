"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function ObservabilityPage() {
  return (
    <div className="p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Observability Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Metrics, traces, and centralized logging (Phase 6).
        </p>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Prometheus</CardTitle>
            <CardDescription>API metrics at /metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">Phase 6</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>OpenTelemetry</CardTitle>
            <CardDescription>Distributed tracing across services</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">Phase 6</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Grafana</CardTitle>
            <CardDescription>Workflow timing, agent latency, queue depth</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">Phase 6</Badge>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Loki / ELK</CardTitle>
            <CardDescription>Structured audit and orchestration logs</CardDescription>
          </CardHeader>
          <CardContent>
            <Badge variant="outline">Phase 6</Badge>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
