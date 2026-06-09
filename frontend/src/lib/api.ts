const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type TokenResponse = { access_token: string; token_type: string };

export type WorkflowStatus =
  | "pending"
  | "queued"
  | "running"
  | "awaiting_approval"
  | "awaiting_revision"
  | "revising"
  | "completed"
  | "failed"
  | "cancelled";

export type WorkflowState = {
  workflow_id: string;
  status: WorkflowStatus;
  current_stage: string | null;
  iteration_count: number;
  token_usage_total?: Record<string, number>;
  started_at?: string | null;
  completed_at?: string | null;
  error_message?: string | null;
  state: Record<string, unknown> | null;
};

export type WorkflowLogEntry = {
  timestamp: string;
  stage: string;
  agent: string | null;
  message: string;
  duration_ms?: number | null;
  token_usage?: Record<string, number>;
  error?: string | null;
  metadata?: Record<string, unknown>;
};

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}

export async function apiFetch<T>(
  path: string,
  token: string,
  options: RequestInit = {},
): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json();
}
