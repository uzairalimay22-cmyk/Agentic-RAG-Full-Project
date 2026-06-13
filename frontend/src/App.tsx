import { useEffect, useRef, useState } from "react";
import ChatPanel from "./components/ChatPanel";
import DocumentSidebar from "./components/DocumentSidebar";
import PipelineVisualizer from "./components/PipelineVisualizer";
import { deleteDocument, getConfig, listDocuments, streamChat, uploadDocument } from "./api";
import type { AppConfig, ChatMessage, DocumentInfo, PipelineEvent } from "./types";

export default function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [streamingContent, setStreamingContent] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const refreshDocuments = async () => {
    try {
      setDocuments(await listDocuments());
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    getConfig().then(setConfig).catch((err) => console.error(err));
    refreshDocuments();
  }, []);

  const handleUpload = async (file: File) => {
    await uploadDocument(file);
    await refreshDocuments();
  };

  const handleDelete = async (source: string) => {
    await deleteDocument(source);
    await refreshDocuments();
  };

  const handleStop = () => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsStreaming(false);
  };

  const handleSend = async (text: string) => {
    const history = messages;
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setEvents([]);
    setStreamingContent("");
    setError(null);
    setIsStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    let finalText = "";
    let hadError = false;

    try {
      await streamChat(
        text,
        history,
        (event) => {
          switch (event.type) {
            case "token":
              setStreamingContent((prev) => prev + (event.text ?? ""));
              break;
            case "final":
              finalText = event.text ?? "";
              setStreamingContent(finalText);
              setEvents((prev) => [...prev, event]);
              break;
            case "error":
              hadError = true;
              setError(typeof event.detail === "string" ? event.detail : "Something went wrong.");
              setEvents((prev) => [...prev, event]);
              break;
            case "done":
              break;
            default:
              setEvents((prev) => [...prev, event]);
          }
        },
        controller.signal,
      );
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        finalText = finalText || streamingContent;
      } else {
        hadError = true;
        setError(err instanceof Error ? err.message : String(err));
      }
    } finally {
      setIsStreaming(false);
      abortRef.current = null;
      if (finalText && !hadError) {
        setMessages((prev) => [...prev, { role: "assistant", content: finalText }]);
      }
      setStreamingContent("");
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-zinc-900 text-zinc-100">
      <DocumentSidebar
        documents={documents}
        config={config}
        onUpload={handleUpload}
        onDelete={handleDelete}
      />
      <ChatPanel
        messages={messages}
        streamingContent={streamingContent}
        isStreaming={isStreaming}
        error={error}
        onSend={handleSend}
        onStop={handleStop}
      />
      <PipelineVisualizer events={events} running={isStreaming} config={config} />
    </div>
  );
}
