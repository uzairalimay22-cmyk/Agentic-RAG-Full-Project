"""Tool definitions exposed to the agent for retrieval (OpenAI-style function schema, used by Groq)."""

from app.config import get_settings
from app.rag import vectorstore

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "Search the user's uploaded document collection (vector knowledge base) "
                "for passages relevant to a query. Use this whenever the user's question "
                "might be answered by their documents. You may call this tool multiple "
                "times with different/refined queries to gather more complete context "
                "(multi-hop retrieval) before answering."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query. Can be a rephrased or more specific version of the user's question.",
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of chunks to retrieve (default 5).",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_knowledge_base_documents",
            "description": (
                "List all documents currently stored in the knowledge base, including "
                "how many chunks each document has. Use this to check what information "
                "is available before searching, or when the user asks what documents "
                "they have uploaded."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def execute_tool(name: str, tool_input: dict) -> dict | list:
    """Dispatch a tool call from the agent to the underlying RAG implementation."""
    settings = get_settings()

    if name == "search_knowledge_base":
        query_text = tool_input.get("query", "")
        n_results = tool_input.get("n_results") or settings.default_top_k
        results = vectorstore.query(query_text, n_results=n_results)
        if not results:
            return {"results": [], "message": "No documents found in the knowledge base yet."}
        return {"results": results}

    if name == "list_knowledge_base_documents":
        return {"documents": vectorstore.list_documents()}

    return {"error": f"Unknown tool '{name}'"}
