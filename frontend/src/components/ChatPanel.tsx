import { useEffect, useRef, useState } from "react";
import { Send, Square } from "lucide-react";
import type { ChatMessage } from "../types";
import MessageBubble from "./MessageBubble";

interface Props {
  messages: ChatMessage[];
  streamingContent: string;
  isStreaming: boolean;
  error: string | null;
  onSend: (text: string) => void;
  onStop: () => void;
}

export default function ChatPanel({
  messages,
  streamingContent,
  isStreaming,
  error,
  onSend,
  onStop,
}: Props) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streamingContent]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isStreaming) return;
    onSend(text);
    setInput("");
  };

  return (
    <main className="flex h-full flex-1 flex-col bg-zinc-900">
      <div ref={scrollRef} className="flex-1 overflow-y-auto scrollbar-thin px-6 py-4 space-y-3">
        {messages.length === 0 && (
          <div className="mx-auto mt-12 max-w-md text-center text-sm text-zinc-500">
            <p className="text-base font-medium text-zinc-300">Agentic RAG assistant</p>
            <p className="mt-2">
              Upload documents on the left, then ask a question. The agent will decide
              whether to search your knowledge base, and the right panel will show the
              pipeline trace live, including which model is active at each step.
            </p>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}

        {isStreaming && (
          <MessageBubble message={{ role: "assistant", content: streamingContent }} streaming />
        )}

        {error && (
          <div className="mx-auto max-w-lg rounded-lg border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">
            {error}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-zinc-800 p-3">
        <div className="flex items-end gap-2 rounded-xl border border-zinc-700 bg-zinc-950 p-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask something about your documents..."
            rows={1}
            className="flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none"
          />
          {isStreaming ? (
            <button
              type="button"
              onClick={onStop}
              className="flex items-center gap-1 rounded-lg bg-zinc-700 px-3 py-2 text-sm text-zinc-200 hover:bg-zinc-600"
            >
              <Square size={14} /> Stop
            </button>
          ) : (
            <button
              type="submit"
              disabled={!input.trim()}
              className="flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-2 text-sm text-white transition hover:bg-indigo-500 disabled:opacity-40"
            >
              <Send size={14} /> Send
            </button>
          )}
        </div>
      </form>
    </main>
  );
}
