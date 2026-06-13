import ReactMarkdown from "react-markdown";
import type { ChatMessage } from "../types";

interface Props {
  message: ChatMessage;
  streaming?: boolean;
}

export default function MessageBubble({ message, streaming }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm ${
          isUser
            ? "bg-indigo-600 text-white rounded-br-sm"
            : "bg-zinc-800 text-zinc-100 rounded-bl-sm border border-zinc-700"
        }`}
      >
        {message.content ? (
          <div className="prose prose-invert prose-sm max-w-none [&_p]:my-1 [&_ul]:my-1 [&_ol]:my-1 [&_pre]:bg-zinc-900 [&_pre]:rounded-lg [&_code]:text-indigo-300">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        ) : (
          <span className="text-zinc-500 italic">Thinking…</span>
        )}
        {streaming && (
          <span className="inline-block w-1.5 h-4 ml-1 align-middle bg-indigo-400 animate-pulse" />
        )}
      </div>
    </div>
  );
}
