const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export interface Critique {
  note: string;
  timestamp_seconds: number;
}

export interface Axis {
  name: string;
  score: number;
  critiques: Critique[];
  rewrite_suggestion: string;
}

export interface Scorecard {
  axes: Axis[];
  overall_summary: string;
}

export async function analyzeFile(file: File): Promise<{ session_id: string; scorecard: Scorecard }> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/analyze`, { method: "POST", body: form });
  if (!res.ok) throw new Error((await res.json()).detail || "Analysis failed");
  return res.json();
}

export async function getSession(sessionId: string) {
  const res = await fetch(`${API_BASE}/session/${sessionId}`);
  if (!res.ok) throw new Error("Session not found");
  return res.json();
}

export async function getSharedSession(sessionId: string) {
  const res = await fetch(`${API_BASE}/share/${sessionId}`);
  if (!res.ok) throw new Error("Session not found");
  return res.json();
}

export async function askPitch(sessionId: string, question: string): Promise<{ answer: string }> {
  const res = await fetch(`${API_BASE}/chat/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error("Chat failed");
  return res.json();
}
