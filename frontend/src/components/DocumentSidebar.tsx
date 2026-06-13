import { useRef, useState } from "react";
import { FileText, Trash2, UploadCloud, Loader2 } from "lucide-react";
import type { AppConfig, DocumentInfo } from "../types";

interface Props {
  documents: DocumentInfo[];
  config: AppConfig | null;
  onUpload: (file: File) => Promise<void>;
  onDelete: (source: string) => Promise<void>;
}

function formatBytes(bytes: number): string {
  if (bytes <= 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentSidebar({ documents, config, onUpload, onDelete }: Props) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setBusy(true);
    setError(null);
    try {
      for (const file of Array.from(files)) {
        await onUpload(file);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  };

  return (
    <aside className="flex h-full w-72 flex-col gap-4 border-r border-zinc-800 bg-zinc-950 p-4">
      <div>
        <h1 className="text-lg font-semibold text-zinc-100">Agentic RAG</h1>
        <p className="text-xs text-zinc-500">Knowledge base &amp; pipeline config</p>
      </div>

      {config && (
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-xs space-y-1.5">
          <div className="flex justify-between">
            <span className="text-zinc-500">Agent model</span>
            <span className="font-mono text-indigo-300">{config.llm_model}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-500">Provider</span>
            <span className="font-mono text-indigo-300">{config.llm_provider}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-500">Embeddings</span>
            <span className="font-mono text-emerald-300">{config.embedding_model}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-500">Vector store</span>
            <span className="font-mono text-amber-300">{config.vector_store}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-zinc-500">API key</span>
            <span className={config.llm_configured ? "text-emerald-400" : "text-red-400"}>
              {config.llm_configured ? "configured" : "missing"}
            </span>
          </div>
        </div>
      )}

      <div>
        <input
          ref={fileInput}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <button
          onClick={() => fileInput.current?.click()}
          disabled={busy}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-dashed border-zinc-700 bg-zinc-900 px-3 py-3 text-sm text-zinc-300 transition hover:border-indigo-500 hover:text-indigo-300 disabled:opacity-50"
        >
          {busy ? <Loader2 size={16} className="animate-spin" /> : <UploadCloud size={16} />}
          {busy ? "Ingesting…" : "Upload document"}
        </button>
        <p className="mt-1 text-[11px] text-zinc-500">PDF, DOCX, TXT, MD</p>
        {error && <p className="mt-1 text-[11px] text-red-400">{error}</p>}
      </div>

      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-zinc-500">
          Documents ({documents.length})
        </h2>
        {documents.length === 0 && (
          <p className="text-xs text-zinc-600">No documents yet. Upload one to build the knowledge base.</p>
        )}
        <ul className="space-y-2">
          {documents.map((doc) => (
            <li
              key={doc.source}
              className="group flex items-start gap-2 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-xs"
            >
              <FileText size={14} className="mt-0.5 shrink-0 text-zinc-500" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-zinc-200" title={doc.source}>
                  {doc.source}
                </p>
                <p className="text-zinc-500">
                  {doc.chunks} chunk{doc.chunks === 1 ? "" : "s"}
                  {doc.size_bytes ? ` · ${formatBytes(doc.size_bytes)}` : ""}
                </p>
              </div>
              <button
                onClick={() => onDelete(doc.source)}
                className="shrink-0 text-zinc-600 opacity-0 transition group-hover:opacity-100 hover:text-red-400"
                title="Delete document"
              >
                <Trash2 size={14} />
              </button>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
