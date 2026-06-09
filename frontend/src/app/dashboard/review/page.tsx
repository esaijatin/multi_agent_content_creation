"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ScriptReviewPage() {
  return (
    <div className="p-8 space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Script Review Panel</h1>
        <p className="text-muted-foreground mt-1">
          Human-in-the-loop approval and revision for generated content.
        </p>
      </header>
      <Card>
        <CardHeader>
          <CardTitle>Draft Review</CardTitle>
          <CardDescription>
            Approve or request revisions via POST /workflow/&#123;id&#125;/approve
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Connects to critique scores and revision loop thresholds. Full UI in Phase 4.
        </CardContent>
      </Card>
    </div>
  );
}
