"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  FileText,
  LayoutDashboard,
  Network,
  ScrollText,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/dashboard", label: "Projects", icon: LayoutDashboard },
  { href: "/dashboard/workflows", label: "Workflows", icon: Network },
  { href: "/dashboard/prompts", label: "Prompt Workspace", icon: ScrollText },
  { href: "/dashboard/review", label: "Script Review", icon: FileText },
  { href: "/dashboard/observability", label: "Observability", icon: Activity },
  { href: "/dashboard/agents", label: "Agent Activity", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-border bg-card">
      <div className="flex h-16 items-center gap-2 border-b border-border px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary text-primary-foreground text-sm font-bold">
          A
        </div>
        <div>
          <p className="text-sm font-semibold">AstraOS</p>
          <p className="text-xs text-muted-foreground">Content Orchestration</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-4">
        {nav.map((item) => {
          const active = pathname === item.href || pathname.startsWith(item.href + "/");
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-primary/15 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-border p-4 text-xs text-muted-foreground">
        Phase 2 · Orchestration
      </div>
    </aside>
  );
}
