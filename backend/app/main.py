import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.agent.orchestrator import run_agent
from app.config import get_settings
from app.models import ChatRequest, DocumentInfo, UploadResponse
from app.rag import vectorstore
from app.rag.ingestion import SUPPORTED_EXTENSIONS, load_and_chunk

settings = get_settings()

app = FastAPI(title="Agentic RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/config")
async def config():
    """Expose non-secret config so the UI can display which models/components are active."""
    return {
        "llm_provider": "Groq",
        "llm_model": settings.groq_model,
        "embedding_model": settings.embedding_model,
        "vector_store": "ChromaDB",
        "default_top_k": settings.default_top_k,
        "llm_configured": bool(settings.groq_api_key),
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Supported: {sorted(SUPPORTED_EXTENSIONS)}",
        )

    dest = Path(settings.upload_dir) / file.filename
    contents = await file.read()
    dest.write_bytes(contents)

    try:
        chunks = load_and_chunk(dest)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    added = vectorstore.add_chunks(file.filename, chunks)
    return UploadResponse(source=file.filename, chunks_added=added)


@app.get("/api/documents", response_model=list[DocumentInfo])
async def list_documents():
    return vectorstore.list_documents()


@app.delete("/api/documents/{source}")
async def delete_document(source: str):
    deleted = vectorstore.delete_document(source)
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No document found with source '{source}'")

    upload_path = Path(settings.upload_dir) / source
    if upload_path.exists():
        upload_path.unlink()

    return {"source": source, "chunks_deleted": deleted}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    async def event_stream():
        history = [{"role": m.role, "content": m.content} for m in req.history]
        async for event in run_agent(req.message, history):
            yield json.dumps(event, default=str) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
