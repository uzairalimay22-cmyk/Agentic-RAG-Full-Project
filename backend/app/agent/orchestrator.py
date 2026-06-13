"""Agentic RAG orchestrator.

Runs an agent loop against the Groq API (free, OpenAI-compatible) where the
model itself decides whether/when to call the `search_knowledge_base` tool
(and how many times, with which queries) before answering. Every step of the
loop is yielded as a small event dict so the frontend can render a live
"pipeline trace" that shows exactly which model and which component is
active at each moment.
"""

import json
from collections.abc import AsyncIterator
from typing import Any

import groq

from app.config import get_settings
from app.agent.tools import TOOLS, execute_tool

SYSTEM_PROMPT = """You are an Agentic RAG assistant. You help the user by answering \
questions, using a private knowledge base built from documents they have uploaded.

You have access to two tools:
- search_knowledge_base: semantic search over the user's uploaded documents.
- list_knowledge_base_documents: list what documents are available.

Guidelines:
1. For any question that could plausibly be answered from the user's documents, \
call search_knowledge_base BEFORE answering. You may call it more than once with \
different or refined queries (multi-hop retrieval) if the first results are \
insufficient or if the question has multiple parts.
2. If the knowledge base has no relevant information, say so explicitly, and then \
answer from your own general knowledge if it's reasonable to do so - clearly \
distinguish between information from the documents and your own knowledge.
3. When you use information from a retrieved chunk, cite its source filename in \
parentheses, e.g. "(source: report.pdf)".
4. Be concise, accurate, and helpful. If the user asks something unrelated to the \
documents (e.g. general chit-chat), you can answer directly without searching.
"""

MAX_ITERATIONS = 6
MAX_TOKENS = 4096


async def run_agent(
    message: str, history: list[dict[str, str]] | None = None
) -> AsyncIterator[dict]:
    """Run the agentic RAG loop, yielding pipeline trace events as it goes.

    The final event is always either {"type": "done"} or {"type": "error", ...}.
    """
    settings = get_settings()

    if not settings.groq_api_key:
        yield {
            "type": "error",
            "detail": (
                "GROQ_API_KEY is not configured on the server. "
                "Set it in backend/.env and restart the server. "
                "Get a free key at https://console.groq.com/keys"
            ),
        }
        yield {"type": "done"}
        return

    client = groq.AsyncGroq(api_key=settings.groq_api_key)

    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in history or []:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": message})

    yield {
        "type": "pipeline_step",
        "step": "query_received",
        "label": "User query received",
        "detail": message,
    }

    for iteration in range(1, MAX_ITERATIONS + 1):
        yield {
            "type": "pipeline_step",
            "step": "agent_call",
            "label": f"Agent reasoning (iteration {iteration})",
            "model": settings.groq_model,
        }

        content_parts: list[str] = []
        tool_calls: dict[int, dict[str, Any]] = {}
        announced_tools: set[int] = set()
        finish_reason: str | None = None

        try:
            stream = await client.chat.completions.create(
                model=settings.groq_model,
                messages=messages,
                tools=TOOLS,
                max_completion_tokens=MAX_TOKENS,
                stream=True,
            )
            async for chunk in stream:
                choice = chunk.choices[0]
                delta = choice.delta

                if choice.finish_reason:
                    finish_reason = choice.finish_reason

                if delta.content:
                    content_parts.append(delta.content)
                    yield {"type": "token", "text": delta.content}

                reasoning = getattr(delta, "reasoning", None)
                if reasoning:
                    yield {"type": "thinking", "text": reasoning}

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        entry = tool_calls.setdefault(
                            tc.index, {"id": None, "name": None, "arguments": ""}
                        )
                        if tc.id:
                            entry["id"] = tc.id
                        if tc.function:
                            if tc.function.name:
                                entry["name"] = tc.function.name
                            if tc.function.arguments:
                                entry["arguments"] += tc.function.arguments

                        if entry["name"] and tc.index not in announced_tools:
                            announced_tools.add(tc.index)
                            yield {
                                "type": "pipeline_step",
                                "step": "tool_selected",
                                "label": f"Agent selected tool: {entry['name']}",
                                "model": settings.groq_model,
                            }
        except groq.APIStatusError as exc:
            yield {
                "type": "error",
                "detail": f"Groq API error ({exc.status_code}): {exc.message}",
            }
            yield {"type": "done"}
            return
        except groq.GroqError as exc:
            yield {"type": "error", "detail": f"Groq SDK error: {exc}"}
            yield {"type": "done"}
            return

        final_content = "".join(content_parts)

        if finish_reason == "tool_calls" and tool_calls:
            assistant_message: dict[str, Any] = {
                "role": "assistant",
                "content": final_content or None,
                "tool_calls": [
                    {
                        "id": tool_calls[idx]["id"],
                        "type": "function",
                        "function": {
                            "name": tool_calls[idx]["name"],
                            "arguments": tool_calls[idx]["arguments"] or "{}",
                        },
                    }
                    for idx in sorted(tool_calls)
                ],
            }
            messages.append(assistant_message)

            for idx in sorted(tool_calls):
                tc = tool_calls[idx]
                try:
                    tool_input = json.loads(tc["arguments"]) if tc["arguments"] else {}
                except json.JSONDecodeError:
                    tool_input = {}

                yield {
                    "type": "tool_call",
                    "step": "tool_call",
                    "label": f"Calling tool: {tc['name']}",
                    "detail": {"name": tc["name"], "input": tool_input},
                }

                result = execute_tool(tc["name"], tool_input)

                yield {
                    "type": "tool_result",
                    "step": "tool_result",
                    "label": f"Result from: {tc['name']}",
                    "detail": result,
                }

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result, default=str),
                    }
                )

            continue

        yield {
            "type": "pipeline_step",
            "step": "answer_ready",
            "label": "Final answer generated",
            "model": settings.groq_model,
        }
        yield {"type": "final", "text": final_content}
        yield {"type": "done"}
        return

    yield {
        "type": "error",
        "detail": "Reached the maximum number of agent iterations without a final answer.",
    }
    yield {"type": "done"}
