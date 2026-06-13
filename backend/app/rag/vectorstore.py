"""Chroma-backed vector store for the knowledge base.

Embeddings are generated locally with Chroma's bundled ONNX MiniLM model
(via onnxruntime) so no extra API key or heavy ML framework (e.g. torch)
is required beyond the Groq key used by the agent.
"""

import hashlib
import threading

import chromadb
from chromadb.utils import embedding_functions

from app.config import get_settings

_lock = threading.Lock()
_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is not None:
        return _collection

    with _lock:
        if _collection is not None:
            return _collection

        settings = get_settings()
        _client = chromadb.PersistentClient(path=settings.chroma_dir)
        embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        _collection = _client.get_or_create_collection(
            name=settings.collection_name,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
        return _collection


def add_chunks(source: str, chunks: list[str]) -> int:
    """Embed and store chunks for a given source document."""
    if not chunks:
        return 0

    collection = _get_collection()
    ids = [
        f"{source}::{i}::{hashlib.sha1(chunk.encode('utf-8')).hexdigest()[:8]}"
        for i, chunk in enumerate(chunks)
    ]
    metadatas = [{"source": source, "chunk_index": i} for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, metadatas=metadatas)
    return len(chunks)


def query(query_text: str, n_results: int = 5) -> list[dict]:
    """Run a similarity search and return ranked chunks with metadata."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    n_results = max(1, min(n_results, collection.count()))
    results = collection.query(query_texts=[query_text], n_results=n_results)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    out = []
    for doc_id, doc, meta, dist in zip(ids, documents, metadatas, distances):
        out.append(
            {
                "id": doc_id,
                "text": doc,
                "source": meta.get("source", "unknown"),
                "chunk_index": meta.get("chunk_index", -1),
                # cosine distance -> similarity score in [0, 1]
                "score": round(1 - dist, 4),
            }
        )
    return out


def list_documents() -> list[dict]:
    """Return aggregate stats for each ingested source document."""
    collection = _get_collection()
    if collection.count() == 0:
        return []

    data = collection.get(include=["metadatas", "documents"])
    stats: dict[str, dict] = {}
    for meta, doc in zip(data["metadatas"], data["documents"]):
        source = meta.get("source", "unknown")
        entry = stats.setdefault(source, {"source": source, "chunks": 0, "size_bytes": 0})
        entry["chunks"] += 1
        entry["size_bytes"] += len(doc.encode("utf-8"))
    return sorted(stats.values(), key=lambda d: d["source"])


def delete_document(source: str) -> int:
    """Delete all chunks belonging to a source document."""
    collection = _get_collection()
    matches = collection.get(where={"source": source}, include=[])
    ids = matches.get("ids", [])
    if ids:
        collection.delete(ids=ids)
    return len(ids)


def reset() -> None:
    """Remove every chunk from the knowledge base."""
    collection = _get_collection()
    all_ids = collection.get(include=[]).get("ids", [])
    if all_ids:
        collection.delete(ids=all_ids)
