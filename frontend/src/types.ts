export type Role = "user" | "assistant";

export interface ChatMessage {
  role: Role;
  content: string;
}

export interface DocumentInfo {
  source: string;
  chunks: number;
  size_bytes: number;
}

export type PipelineEventType =
  | "pipeline_step"
  | "tool_call"
  | "tool_result"
  | "thinking"
  | "token"
  | "final"
  | "done"
  | "error";

export interface PipelineEvent {
  type: PipelineEventType;
  step?: string;
  label?: string;
  model?: string;
  detail?: unknown;
  text?: string;
}

export interface AppConfig {
  llm_provider: string;
  llm_model: string;
  embedding_model: string;
  vector_store: string;
  default_top_k: number;
  llm_configured: boolean;
}

export interface RetrievedChunk {
  id: string;
  text: string;
  source: string;
  chunk_index: number;
  score: number;
}
