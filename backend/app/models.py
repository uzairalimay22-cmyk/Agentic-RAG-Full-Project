from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)
    top_k: int | None = None


class DocumentChunk(BaseModel):
    id: str
    text: str
    source: str
    chunk_index: int
    score: float | None = None


class DocumentInfo(BaseModel):
    source: str
    chunks: int
    size_bytes: int


class UploadResponse(BaseModel):
    source: str
    chunks_added: int


class PipelineEvent(BaseModel):
    """A single step emitted while the agentic RAG pipeline runs.

    Streamed to the frontend as newline-delimited JSON so the UI can
    render a live trace of which component / model is active.
    """

    type: str
    step: str | None = None
    label: str | None = None
    model: str | None = None
    detail: Any | None = None
    text: str | None = None
