import { useMemo } from "react";
import {
  ArrowDown,
  Bot,
  Brain,
  CheckCircle2,
  CircleDashed,
  Database,
  MessageSquare,
  Search,
  User,
  XCircle,
} from "lucide-react";
import type { AppConfig, PipelineEvent, RetrievedChunk } from "../types";

interface Props {
  events: PipelineEvent[];
  running: boolean;
  config: AppConfig | null;
}

type NodeId = "user" | "agent" | "tools" | "knowledge_base" | "response";

const NODES: { id: NodeId; label: string }[] = [
  { id: "user", label: "User query" },
  { id: "agent", label: "Agent reasoning" },
  { id: "tools", label: "Tool call" },
  { id: "knowledge_base", label: "Knowledge base (ChromaDB)" },
  { id: "response", label: "Response" },
];

function activeNodeFor(event: PipelineEvent | undefined): NodeId | null {
  if (!event) return null;
  switch (event.type) {
    case "pipeline_step":
      if (event.step === "query_received") return "user";
      if (event.step === "agent_call" || event.step === "tool_selected") return "agent";
      if (event.step === "answer_ready") return "response";
      return "agent";
    case "tool_call":
      return "tools";
    case "tool_result":
      return "knowledge_base";
    case "thinking":
      return "agent";
    case "token":
    case "final":
      return "response";
    default:
      return null;
  }
}

function NodeIcon({ id }: { id: NodeId }) {
  const cls = "h-4 w-4";
  switch (id) {
    case "user":
      return <User className={cls} />;
    case "agent":
      return <Bot className={cls} />;
    case "tools":
      return <Search className={cls} />;
    case "knowledge_base":
      return <Database className={cls} />;
    case "response":
      return <MessageSquare className={cls} />;
  }
}

function EventIcon({ type }: { type: PipelineEvent["type"] }) {
  switch (type) {
    case "pipeline_step":
      return <CircleDashed className="h-3.5 w-3.5 text-indigo-400" />;
    case "tool_call":
      return <Search className="h-3.5 w-3.5 text-amber-400" />;
    case "tool_result":
      return <Database className="h-3.5 w-3.5 text-emerald-400" />;
    case "thinking":
      return <Brain className="h-3.5 w-3.5 text-purple-400" />;
    case "final":
      return <MessageSquare className="h-3.5 w-3.5 text-sky-400" />;
    case "done":
      return <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />;
    case "error":
      return <XCircle className="h-3.5 w-3.5 text-red-500" />;
    default:
      return <CircleDashed className="h-3.5 w-3.5 text-zinc-500" />;
  }
}

function ToolResultDetail({ detail }: { detail: unknown }) {
  const d = detail as { results?: RetrievedChunk[]; message?: string; documents?: unknown[] };
  if (d?.message && !d.results?.length) {
    return <p className="text-zinc-500">{d.message}</p>;
  }
  if (d?.results) {
    return (
      <ul className="mt-1 space-y-1">
        {d.results.map((chunk) => (
          <li key={chunk.id} className="rounded border border-zinc-800 bg-zinc-950 p-2">
            <div className="flex items-center justify-between text-[10px] text-zinc-500">
              <span className="font-mono truncate">{chunk.source} · chunk {chunk.chunk_index}</span>
              <span className="text-emerald-400">score {chunk.score?.toFixed(3)}</span>
            </div>
            <p className="mt-1 line-clamp-3 text-zinc-400">{chunk.text}</p>
          </li>
        ))}
      </ul>
    );
  }
  if (d?.documents) {
    return <p className="text-zinc-500">{d.documents.length} document(s) in knowledge base</p>;
  }
  return null;
}

function EventDetail({ event }: { event: PipelineEvent }) {
  switch (event.type) {
    case "pipeline_step":
      return event.detail ? (
        <p className="line-clamp-2 text-zinc-500">{String(event.detail)}</p>
      ) : null;
    case "tool_call": {
      const d = event.detail as { name?: string; input?: Record<string, unknown> };
      return (
        <p className="font-mono text-zinc-500">
          {d?.input ? JSON.stringify(d.input) : null}
        </p>
      );
    }
    case "tool_result":
      return <ToolResultDetail detail={event.detail} />;
    case "thinking":
      return <p className="italic text-purple-300/80 line-clamp-3">{event.text}</p>;
    case "error":
      return <p className="text-red-400">{event.detail ? String(event.detail) : "An error occurred."}</p>;
    default:
      return null;
  }
}

export default function PipelineVisualizer({ events, running, config }: Props) {
  const activeNode = useMemo(() => {
    const last = [...events].reverse().find((e) => e.type !== "token" && e.type !== "done");
    return activeNodeFor(last);
  }, [events]);

  // Collapse consecutive thinking deltas into a single rolling entry, and drop token events.
  const traceEvents = useMemo(() => {
    const out: PipelineEvent[] = [];
    for (const e of events) {
      if (e.type === "token") continue;
      if (e.type === "thinking" && out.length && out[out.length - 1].type === "thinking") {
        out[out.length - 1] = {
          ...out[out.length - 1],
          text: (out[out.length - 1].text ?? "") + (e.text ?? ""),
        };
        continue;
      }
      out.push(e);
    }
    return out;
  }, [events]);

  return (
    <aside className="flex h-full w-80 flex-col gap-4 border-l border-zinc-800 bg-zinc-950 p-4">
      <div>
        <h2 className="text-sm font-semibold text-zinc-100">Pipeline trace</h2>
        <p className="text-xs text-zinc-500">Live view of the agentic RAG loop</p>
      </div>

      {/* Flow diagram */}
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-3">
        <div className="flex flex-col items-stretch gap-1">
          {NODES.map((node, i) => {
            const isActive = running && activeNode === node.id;
            return (
              <div key={node.id} className="flex flex-col items-center">
                <div
                  className={`flex w-full items-center gap-2 rounded-md border px-2.5 py-1.5 text-xs transition-all ${
                    isActive
                      ? "border-indigo-500 bg-indigo-500/10 text-indigo-200 shadow-[0_0_12px_rgba(99,102,241,0.35)]"
                      : "border-zinc-800 bg-zinc-950 text-zinc-400"
                  }`}
                >
                  <NodeIcon id={node.id} />
                  <span className="flex-1">{node.label}</span>
                  {node.id === "agent" && config && (
                    <span className="font-mono text-[10px] text-indigo-300">{config.llm_model}</span>
                  )}
                  {node.id === "knowledge_base" && config && (
                    <span className="font-mono text-[10px] text-emerald-300">{config.embedding_model}</span>
                  )}
                  {isActive && (
                    <span className="relative flex h-2 w-2">
                      <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75" />
                      <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-500" />
                    </span>
                  )}
                </div>
                {i < NODES.length - 1 && <ArrowDown className="my-0.5 h-3 w-3 text-zinc-700" />}
              </div>
            );
          })}
        </div>
        <p className="mt-2 text-[10px] text-zinc-600">
          The agent can loop between "Agent reasoning" and "Tool call" / "Knowledge base"
          multiple times before producing a response (multi-hop retrieval).
        </p>
      </div>

      {/* Trace log */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
          Step-by-step log
        </h3>
        {traceEvents.length === 0 && (
          <p className="text-xs text-zinc-600">
            Send a message to see the pipeline steps appear here in real time.
          </p>
        )}
        <ol className="space-y-2">
          {traceEvents.map((event, idx) => (
            <li key={idx} className="rounded-lg border border-zinc-800 bg-zinc-900 p-2 text-xs">
              <div className="flex items-center gap-1.5">
                <EventIcon type={event.type} />
                <span className="font-medium text-zinc-200">
                  {event.label ?? event.type}
                </span>
                {event.model && (
                  <span className="ml-auto font-mono text-[10px] text-indigo-300">{event.model}</span>
                )}
              </div>
              <div className="mt-1 pl-5 text-[11px]">
                <EventDetail event={event} />
              </div>
            </li>
          ))}
        </ol>
      </div>
    </aside>
  );
}
