import type { AppConfig, ChatMessage, DocumentInfo, PipelineEvent } from "./types";

// In production (separate Railway services), VITE_API_URL points to the
// backend's public URL, e.g. https://my-backend.up.railway.app. In dev it's
// unset and requests go through the Vite proxy to /api.
const API_URL = import.meta.env.VITE_API_URL ?? "";
const BASE = `${API_URL}/api`;

export async function getConfig(): Promise<AppConfig> {
  const res = await fetch(`${BASE}/config`);
  if (!res.ok) throw new Error(`Failed to load config: ${res.status}`);
  return res.json();
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${BASE}/documents`);
  if (!res.ok) throw new Error(`Failed to load documents: ${res.status}`);
  return res.json();
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Upload failed: ${res.status}`);
  }
  const data = await res.json();
  return { source: data.source, chunks: data.chunks_added, size_bytes: 0 };
}

export async function deleteDocument(source: string): Promise<void> {
  const res = await fetch(`${BASE}/documents/${encodeURIComponent(source)}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Delete failed: ${res.status}`);
  }
}

/**
 * Stream a chat turn. The backend responds with newline-delimited JSON
 * pipeline events; each parsed event is forwarded to `onEvent` as it
 * arrives so the UI can render the pipeline trace live.
 */
export async function streamChat(
  message: string,
  history: ChatMessage[],
  onEvent: (event: PipelineEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      try {
        onEvent(JSON.parse(trimmed) as PipelineEvent);
      } catch {
        // ignore malformed lines
      }
    }
  }

  const trimmed = buffer.trim();
  if (trimmed) {
    try {
      onEvent(JSON.parse(trimmed) as PipelineEvent);
    } catch {
      // ignore
    }
  }
}
