# Agentic RAG Pipeline

A full Retrieval-Augmented Generation system with an **agentic**, Groq-powered
(free LLM API) backend and a React UI that visualizes the pipeline live -
showing exactly which step is running and which model/component is active at
each moment.

## Architecture

```
                      ┌─────────────────────────────────────────┐
                      │              FastAPI backend             │
  Documents (PDF/     │  ┌─────────────┐    ┌──────────────────┐ │
  DOCX/TXT/MD)  ───────▶│  Ingestion   │───▶│ ChromaDB vector   │ │
                      │  │  & chunking  │    │ store (local ONNX │ │
                      │  └─────────────┘    │ MiniLM embeddings)│ │
                      │                      └─────────▲────────┘ │
                      │                                │ search    │
  User question ──────▶│  Agent loop (Groq LLM)─────────┘          │
                      │  - decides whether/how to search          │
                      │  - can call search_knowledge_base          │
                      │    multiple times (multi-hop)              │
                      │  - streams a "pipeline trace" of every     │
                      │    step + which model is active            │
                      └─────────────────┬───────────────────────┘
                                         │ NDJSON stream
                                         ▼
                      ┌─────────────────────────────────────────┐
                      │      React + Vite + Tailwind frontend     │
                      │  - Chat UI                                │
                      │  - Document manager (upload/list/delete)  │
                      │  - Live pipeline visualizer                │
                      └─────────────────────────────────────────┘
```

### Why these choices

- **Agentic RAG**: the agent (default `llama-3.3-70b-versatile` on
  [Groq](https://console.groq.com), free) decides for itself whether to call
  the `search_knowledge_base` tool, can issue multiple refined searches
  (multi-hop retrieval), and can also call `list_knowledge_base_documents`.
  This is a real agent loop, not a fixed retrieve-then-generate pipeline.
- **Free LLM**: [Groq](https://console.groq.com) offers a generous free tier
  with fast inference and OpenAI-compatible tool calling - no credit card
  required for an API key.
- **Local embeddings**: Chroma's bundled ONNX MiniLM (`all-MiniLM-L6-v2`) runs
  locally so no separate embeddings provider/key is required.
- **ChromaDB**: a local, file-based vector database - no external service or
  account needed.
- **Pipeline trace streaming**: the backend streams newline-delimited JSON
  events (`pipeline_step`, `tool_call`, `tool_result`, `thinking`, `token`,
  `final`, `done`, `error`) over `/api/chat`. The frontend turns these into a
  live diagram + log so you can see exactly which model and which tool is
  active at every point in the pipeline.

## Project layout

```
backend/
  app/
    main.py            FastAPI app & routes
    config.py          Settings (.env driven)
    models.py          Pydantic schemas
    rag/
      ingestion.py      Document loading + chunking
      vectorstore.py    ChromaDB wrapper (local embeddings)
    agent/
      tools.py          Tool definitions for the agent
      orchestrator.py   Agentic loop + pipeline trace events
  requirements.txt
  .env.example
  run.py
frontend/
  src/
    components/         Chat, DocumentSidebar, PipelineVisualizer, ...
    api.ts               Backend API client (incl. NDJSON streaming)
```

## Setup

### 1. Backend

```powershell
cd backend
python -m venv venv
./venv/Scripts/Activate.ps1      # or venv\Scripts\activate on cmd
pip install -r requirements.txt

cp .env.example .env
# edit .env and set GROQ_API_KEY=gsk_... (free key: https://console.groq.com/keys)

python run.py
```

The API runs at `http://localhost:8000`. The first request that touches the
vector store will download the local embedding model
(`all-MiniLM-L6-v2`, ~80MB) automatically.

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

The UI runs at `http://localhost:5173` and talks to the backend at
`http://localhost:8000`.

## Using the app

1. Open the UI, upload one or more documents (PDF/DOCX/TXT/MD) via the
   sidebar - they're chunked, embedded locally, and stored in ChromaDB.
2. Ask a question in the chat. Watch the **pipeline visualizer**: it lights
   up each stage as it happens - the agent reasoning with the active Groq
   model, tool calls to `search_knowledge_base`, the chunks retrieved from
   ChromaDB, and the final answer generation.
3. The agent decides on its own whether/how many times to search - for
   multi-part questions you'll often see several `search_knowledge_base`
   calls before the final answer.

## Configuration (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | _(required)_ | Your free Groq API key ([console.groq.com/keys](https://console.groq.com/keys)) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Model used by the agent |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Allowed frontend origins |

Embeddings always use Chroma's bundled local ONNX MiniLM model - no extra
variable or key needed.

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/config` | GET | Active model / embedding / vector store info (for the UI) |
| `/api/upload` | POST | Upload + ingest a document (multipart form, field `file`) |
| `/api/documents` | GET | List ingested documents |
| `/api/documents/{source}` | DELETE | Delete a document and its chunks |
| `/api/chat` | POST | `{message, history}` → streamed NDJSON pipeline trace + answer |
