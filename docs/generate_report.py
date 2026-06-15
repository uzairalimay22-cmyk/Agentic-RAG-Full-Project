"""Generate a polished PDF project report for the Agentic RAG Pipeline project.

Run with:  python docs/generate_report.py
Produces:  Agentic_RAG_Project_Report.pdf  (in the project root)
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate,
    PageTemplate,
    Frame,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
    NextPageTemplate,
    ListFlowable,
    ListItem,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

# ----------------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------------
INDIGO = colors.HexColor("#6366F1")
INDIGO_DARK = colors.HexColor("#4338CA")
SLATE_900 = colors.HexColor("#0F172A")
SLATE_700 = colors.HexColor("#334155")
SLATE_400 = colors.HexColor("#94A3B8")
SLATE_100 = colors.HexColor("#F1F5F9")
SLATE_200 = colors.HexColor("#E2E8F0")
EMERALD = colors.HexColor("#10B981")
AMBER = colors.HexColor("#F59E0B")
WHITE = colors.white
INK = colors.HexColor("#1E293B")

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "Agentic_RAG_Project_Report.pdf"

PAGE_W, PAGE_H = LETTER
MARGIN = 0.75 * inch

# ----------------------------------------------------------------------------
# Styles
# ----------------------------------------------------------------------------
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    "CoverTitle", fontName="Helvetica-Bold", fontSize=34, leading=40,
    textColor=WHITE, alignment=TA_CENTER, spaceAfter=10,
))
styles.add(ParagraphStyle(
    "CoverSubtitle", fontName="Helvetica", fontSize=14, leading=20,
    textColor=SLATE_400, alignment=TA_CENTER, spaceAfter=4,
))
styles.add(ParagraphStyle(
    "CoverTag", fontName="Helvetica-Bold", fontSize=11, leading=16,
    textColor=INDIGO, alignment=TA_CENTER, spaceAfter=2,
))
styles.add(ParagraphStyle(
    "CoverMeta", fontName="Helvetica", fontSize=10, leading=15,
    textColor=SLATE_400, alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "H1", fontName="Helvetica-Bold", fontSize=18, leading=22,
    textColor=INDIGO_DARK, spaceBefore=4, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "H2", fontName="Helvetica-Bold", fontSize=12.5, leading=16,
    textColor=SLATE_900, spaceBefore=12, spaceAfter=4,
))
styles.add(ParagraphStyle(
    "Body", fontName="Helvetica", fontSize=10, leading=14.5,
    textColor=INK, alignment=TA_LEFT, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "BodySmall", fontName="Helvetica", fontSize=8.5, leading=12,
    textColor=SLATE_700, alignment=TA_LEFT,
))
styles.add(ParagraphStyle(
    "CodeBlock", fontName="Courier", fontSize=8.5, leading=12,
    textColor=INK, backColor=SLATE_100, borderPadding=6,
))
styles.add(ParagraphStyle(
    "TocEntry", fontName="Helvetica", fontSize=11, leading=22,
    textColor=INK,
))
styles.add(ParagraphStyle(
    "TocNum", fontName="Helvetica-Bold", fontSize=11, leading=22,
    textColor=INDIGO,
))
styles.add(ParagraphStyle(
    "Caption", fontName="Helvetica-Oblique", fontSize=8.5, leading=12,
    textColor=SLATE_700, alignment=TA_CENTER, spaceBefore=4, spaceAfter=10,
))

TABLE_HEADER_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
    ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, SLATE_100]),
    ("GRID", (0, 0), (-1, -1), 0.5, SLATE_200),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
])


def p(text, style="Body"):
    return Paragraph(text, styles[style])


def rule():
    return HRFlowable(width="100%", thickness=1.2, color=INDIGO, spaceAfter=10)


def heading(num, title):
    return [p(f"{num}&nbsp;&nbsp; {title}", "H1"), rule()]


def code_block(lines):
    text = "<br/>".join(lines)
    return Paragraph(text, styles["CodeBlock"])


# ----------------------------------------------------------------------------
# Page decorations
# ----------------------------------------------------------------------------

def draw_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(SLATE_900)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    # Accent stripes
    canvas.setFillColor(INDIGO)
    canvas.rect(0, PAGE_H - 0.18 * inch, PAGE_W, 0.18 * inch, fill=1, stroke=0)
    canvas.setFillColor(EMERALD)
    canvas.rect(0, 0, PAGE_W, 0.10 * inch, fill=1, stroke=0)

    # Decorative node/graph motif (suggesting RAG / vector space)
    canvas.setStrokeColor(SLATE_700)
    canvas.setLineWidth(0.8)
    pts = [
        (1.2 * inch, 2.0 * inch), (2.4 * inch, 1.6 * inch),
        (1.8 * inch, 1.0 * inch), (3.2 * inch, 1.2 * inch),
        (5.0 * inch, 1.8 * inch), (6.0 * inch, 1.1 * inch),
        (6.6 * inch, 2.1 * inch), (4.4 * inch, 2.4 * inch),
    ]
    for i in range(len(pts) - 1):
        canvas.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
    canvas.setFillColor(INDIGO)
    for (x, y) in pts:
        canvas.circle(x, y, 2.4, fill=1, stroke=0)

    canvas.restoreState()


def draw_later(canvas, doc):
    canvas.saveState()
    # Header rule
    canvas.setStrokeColor(SLATE_200)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN, PAGE_H - 0.55 * inch, PAGE_W - MARGIN, PAGE_H - 0.55 * inch)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(SLATE_700)
    canvas.drawString(MARGIN, PAGE_H - 0.45 * inch, "AGENTIC RAG PIPELINE")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 0.45 * inch, "Project Documentation")

    # Footer
    canvas.setStrokeColor(SLATE_200)
    canvas.line(MARGIN, 0.55 * inch, PAGE_W - MARGIN, 0.55 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE_700)
    canvas.drawString(MARGIN, 0.38 * inch, "github.com/uzairalimay22-cmyk/Agentic-RAG-Full-Project")
    canvas.drawRightString(PAGE_W - MARGIN, 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


# ----------------------------------------------------------------------------
# Architecture diagram
# ----------------------------------------------------------------------------

def arrow_head(x, y, direction="down", color=SLATE_700):
    """Return a small triangular arrowhead Polygon pointing in `direction`, tip at (x, y)."""
    s = 5
    if direction == "down":
        pts = [x, y, x - s, y + s * 1.6, x + s, y + s * 1.6]
    elif direction == "up":
        pts = [x, y, x - s, y - s * 1.6, x + s, y - s * 1.6]
    elif direction == "left":
        pts = [x, y, x + s * 1.6, y + s, x + s * 1.6, y - s]
    else:  # right
        pts = [x, y, x - s * 1.6, y + s, x - s * 1.6, y - s]
    return Polygon(points=pts, fillColor=color, strokeColor=color)


def box(d, x, y, w, h, lines, fill, text_color=WHITE, font_size=9, title_line=0):
    d.add(Rect(x, y, w, h, rx=8, ry=8, fillColor=fill, strokeColor=fill))
    n = len(lines)
    line_h = font_size + 3
    total_h = n * line_h
    start_y = y + h / 2 + total_h / 2 - font_size
    for i, line in enumerate(lines):
        fname = "Helvetica-Bold" if i == title_line else "Helvetica"
        d.add(String(
            x + w / 2, start_y - i * line_h, line,
            textAnchor="middle", fontName=fname, fontSize=font_size,
            fillColor=text_color,
        ))


def build_architecture_diagram():
    W, H = 500, 600
    d = Drawing(W, H)

    col_x, col_w = 30, 350

    # Box geometry (x, y, w, h)
    b_docs = (col_x, 520, col_w, 56)
    b_ingest = (col_x, 432, col_w, 56)
    b_vector = (col_x, 344, col_w, 56)
    b_agent = (col_x, 226, col_w, 78)
    b_stream = (col_x, 140, col_w, 56)
    b_frontend = (col_x, 30, col_w, 78)
    b_query = (410, 240, 80, 50)

    d.add(Rect(0, 0, W, H, fillColor=WHITE, strokeColor=WHITE))

    box(d, *b_docs, lines=["Uploaded Documents", "PDF · DOCX · TXT · MD"],
        fill=SLATE_700, title_line=0)
    box(d, *b_ingest, lines=["Ingestion & Chunking",
                              "RecursiveCharacterTextSplitter",
                              "chunk_size=1000  overlap=200"], fill=INDIGO_DARK)
    box(d, *b_vector, lines=["ChromaDB Vector Store",
                              "Local ONNX embeddings",
                              "all-MiniLM-L6-v2  ·  cosine"], fill=EMERALD)
    box(d, *b_agent, lines=["Agentic Loop — Groq LLM",
                             "llama-3.3-70b-versatile",
                             "decides tool calls; up to 6",
                             "iterations; multi-hop retrieval"], fill=INDIGO)
    box(d, *b_stream, lines=["NDJSON Pipeline Trace",
                              "/api/chat  (streamed events)"], fill=INDIGO_DARK)
    box(d, *b_frontend, lines=["React + Vite + Tailwind UI",
                                "Chat · Document Sidebar",
                                "Live Pipeline Visualizer"], fill=SLATE_700)
    box(d, *b_query, lines=["User", "Query"], fill=AMBER, text_color=INK, font_size=8)

    cx = col_x + col_w / 2

    def vert_arrow(top_box, bottom_box, color=SLATE_700, both=False):
        x = cx
        y1 = top_box[1]
        y2 = bottom_box[1] + bottom_box[3]
        d.add(Line(x, y1, x, y2, strokeColor=color, strokeWidth=1.4))
        d.add(arrow_head(x, y2, "down", color))
        if both:
            d.add(arrow_head(x, y1, "up", color))

    vert_arrow(b_docs, b_ingest)
    vert_arrow(b_ingest, b_vector)
    vert_arrow(b_vector, b_agent, color=EMERALD, both=True)
    vert_arrow(b_agent, b_stream)
    vert_arrow(b_stream, b_frontend)

    # User query -> agent loop (horizontal arrow, pointing left)
    qx = b_query[0]
    qy = b_query[1] + b_query[3] / 2
    ax = b_agent[0] + b_agent[2]
    d.add(Line(qx, qy, ax, qy, strokeColor=AMBER, strokeWidth=1.4))
    d.add(arrow_head(ax, qy, "left", AMBER))

    # Label for the bidirectional retrieval arrow
    d.add(String(cx + 14, (b_vector[1] + b_agent[1] + b_agent[3]) / 2, "search_knowledge_base()",
                  fontName="Helvetica-Oblique", fontSize=7.5, fillColor=SLATE_700))

    return d


# ----------------------------------------------------------------------------
# Document content
# ----------------------------------------------------------------------------

def build_story():
    story = []

    # ---------------- Cover page ----------------
    story.append(Spacer(1, 2.6 * inch))
    story.append(p("AGENTIC RAG PIPELINE", "CoverTitle"))
    story.append(p("An Autonomous, Multi-Hop Retrieval-Augmented Generation System", "CoverSubtitle"))
    story.append(Spacer(1, 0.35 * inch))
    story.append(p("FastAPI &nbsp;•&nbsp; Groq LLM &nbsp;•&nbsp; ChromaDB &nbsp;•&nbsp; React + Vite + Tailwind", "CoverTag"))
    story.append(Spacer(1, 1.6 * inch))
    story.append(p("Project Documentation &amp; Technical Report", "CoverMeta"))
    story.append(p("Author: Uzair Ali", "CoverMeta"))
    story.append(p("Repository: github.com/uzairalimay22-cmyk/Agentic-RAG-Full-Project", "CoverMeta"))
    story.append(p("June 2026", "CoverMeta"))

    story.append(NextPageTemplate("later"))
    story.append(PageBreak())

    # ---------------- Table of contents ----------------
    story.append(p("Contents", "H1"))
    story.append(rule())
    toc_items = [
        "1.  Executive Summary",
        "2.  System Architecture",
        "3.  Technology Stack",
        "4.  Key Features",
        "5.  The Agentic Pipeline & Event Trace",
        "6.  Project Structure",
        "7.  REST API Reference",
        "8.  Configuration Reference",
        "9.  Setup & Installation Guide",
        "10. Using the Application",
        "11. Conclusion & Future Work",
    ]
    for item in toc_items:
        story.append(p(item, "TocEntry"))
    story.append(Spacer(1, 0.3 * inch))
    story.append(p(
        "This document describes the design, architecture, and usage of the "
        "Agentic RAG Pipeline — a Retrieval-Augmented Generation system built "
        "around an autonomous LLM agent that decides for itself when and how to "
        "search a private document knowledge base, with a live, streaming "
        "visualization of every step in the pipeline.",
        "Body",
    ))
    story.append(PageBreak())

    # ---------------- 1. Executive Summary ----------------
    story += heading("1.", "Executive Summary")
    story.append(p(
        "The <b>Agentic RAG Pipeline</b> is a full-stack Retrieval-Augmented "
        "Generation (RAG) application that goes beyond the conventional "
        "“retrieve-then-generate” pattern. Instead of always running a fixed "
        "retrieval step before generation, the system gives a large language "
        "model (LLM) <b>agency</b>: the model itself decides whether a question "
        "requires searching the user's documents, issues one or more refined "
        "searches (multi-hop retrieval), and only then produces a final answer.",
        "Body",
    ))
    story.append(p(
        "The backend is a Python <b>FastAPI</b> service that exposes document "
        "ingestion, knowledge-base management, and a streaming chat endpoint. "
        "Documents (PDF, DOCX, TXT, MD) are chunked and embedded locally using "
        "Chroma's bundled ONNX MiniLM model, then stored in a persistent "
        "<b>ChromaDB</b> vector database — no external embedding API or key is "
        "required. Reasoning is delegated to <b>Groq</b>, a free, "
        "OpenAI-compatible LLM API with very fast inference and native tool "
        "(function) calling, running the <b>llama-3.3-70b-versatile</b> model "
        "by default.",
        "Body",
    ))
    story.append(p(
        "The frontend is a <b>React 19 + Vite + Tailwind CSS 4</b> single-page "
        "application. Its centerpiece is a <b>live pipeline visualizer</b> that "
        "consumes a stream of newline-delimited JSON (NDJSON) events from the "
        "backend and renders, in real time, exactly which stage of the pipeline "
        "is active — agent reasoning, tool selection, knowledge-base search, "
        "tool results, and final answer generation — along with which model "
        "and component is responsible for each step.",
        "Body",
    ))
    story.append(p(
        "This makes the system useful both as a practical document Q&amp;A tool "
        "and as an educational demonstration of how agentic RAG systems work "
        "internally.",
        "Body",
    ))
    story.append(PageBreak())

    # ---------------- 2. Architecture ----------------
    story += heading("2.", "System Architecture")
    story.append(p(
        "The diagram below shows the end-to-end data flow, from document "
        "ingestion on the left/top path to the live pipeline trace consumed by "
        "the frontend.",
        "Body",
    ))
    story.append(Spacer(1, 6))
    story.append(build_architecture_diagram())
    story.append(p(
        "Figure 1. Data flow through the ingestion pipeline (top), the agentic "
        "query loop (middle), and the streamed pipeline trace consumed by the UI (bottom).",
        "Caption",
    ))

    story.append(p("Design rationale", "H2"))
    story.append(ListFlowable([
        ListItem(p(
            "<b>Agentic, not fixed, RAG</b> &mdash; the agent (default "
            "<font face='Courier'>llama-3.3-70b-versatile</font> on Groq) decides "
            "for itself whether to call <font face='Courier'>search_knowledge_base</font>, "
            "can issue multiple refined searches (multi-hop retrieval), and can "
            "also call <font face='Courier'>list_knowledge_base_documents</font>. "
            "This is a real agent loop, not a fixed retrieve-then-generate pipeline.",
            "Body")),
        ListItem(p(
            "<b>Free LLM provider</b> &mdash; Groq offers a generous free tier "
            "with fast inference and OpenAI-compatible tool calling, requiring "
            "only a free API key (no credit card).",
            "Body")),
        ListItem(p(
            "<b>Local embeddings</b> &mdash; Chroma's bundled ONNX MiniLM model "
            "(<font face='Courier'>all-MiniLM-L6-v2</font>) runs locally via "
            "onnxruntime, so no separate embeddings provider or API key is needed.",
            "Body")),
        ListItem(p(
            "<b>ChromaDB</b> &mdash; a local, file-based, persistent vector "
            "database requiring no external service or account.",
            "Body")),
        ListItem(p(
            "<b>Streamed pipeline trace</b> &mdash; the backend streams NDJSON "
            "events (<font face='Courier'>pipeline_step</font>, "
            "<font face='Courier'>tool_call</font>, <font face='Courier'>tool_result</font>, "
            "<font face='Courier'>thinking</font>, <font face='Courier'>token</font>, "
            "<font face='Courier'>final</font>, <font face='Courier'>done</font>, "
            "<font face='Courier'>error</font>) over <font face='Courier'>/api/chat</font>. "
            "The frontend turns these into a live diagram and step-by-step log.",
            "Body")),
    ], bulletType="bullet", start="•", leftIndent=14, bulletFontSize=9))
    story.append(PageBreak())

    # ---------------- 3. Technology Stack ----------------
    story += heading("3.", "Technology Stack")

    story.append(p("Backend", "H2"))
    backend_table = Table([
        ["Component", "Technology", "Purpose"],
        ["Web framework", "FastAPI + Uvicorn", "REST API and NDJSON streaming endpoint"],
        ["LLM provider", "Groq SDK (groq>=1.4.0)", "Agentic reasoning & tool calling (llama-3.3-70b-versatile)"],
        ["Vector database", "ChromaDB 0.5.23", "Persistent local vector store for document chunks"],
        ["Embeddings", "ONNX MiniLM (all-MiniLM-L6-v2)", "Local, free text embeddings via onnxruntime 1.18.1"],
        ["Document parsing", "pypdf, python-docx", "Extract text from PDF / DOCX files"],
        ["Chunking", "langchain-text-splitters", "RecursiveCharacterTextSplitter for overlap-aware chunks"],
        ["Settings", "pydantic-settings", "Typed configuration loaded from backend/.env"],
    ], colWidths=[1.3 * inch, 1.9 * inch, 3.1 * inch])
    backend_table.setStyle(TABLE_HEADER_STYLE)
    story.append(backend_table)

    story.append(p("Frontend", "H2"))
    frontend_table = Table([
        ["Component", "Technology", "Purpose"],
        ["UI library", "React 19", "Component-based single-page application"],
        ["Build tool", "Vite 8", "Dev server & production bundling"],
        ["Styling", "Tailwind CSS 4", "Utility-first styling, dark themed UI"],
        ["Markdown", "react-markdown", "Render assistant answers with formatting"],
        ["Icons", "lucide-react", "Icon set used across the UI"],
        ["Language", "TypeScript", "Type-safe components and API client"],
    ], colWidths=[1.3 * inch, 1.9 * inch, 3.1 * inch])
    frontend_table.setStyle(TABLE_HEADER_STYLE)
    story.append(frontend_table)
    story.append(PageBreak())

    # ---------------- 4. Key Features ----------------
    story += heading("4.", "Key Features")
    features = [
        ("Agentic multi-hop retrieval", "The LLM decides whether to search at all, and may issue multiple, progressively refined searches before answering — useful for multi-part questions."),
        ("Live pipeline visualizer", "A real-time diagram on the right side of the UI highlights the active stage (user query, agent reasoning, tool call, knowledge base, response) and shows which model/component is running."),
        ("Step-by-step trace log", "Every event (tool selected, tool call, tool result, final answer, errors) is logged in a scrollable panel so the entire reasoning process is auditable."),
        ("Document management", "Upload PDF/DOCX/TXT/MD files via the sidebar; documents are chunked, embedded, and stored automatically. List and delete documents (and their chunks) at any time."),
        ("Source-cited answers", "The system prompt instructs the agent to cite the source filename for any information drawn from the knowledge base."),
        ("Zero-cost local embeddings", "Embeddings run fully locally via ONNX — only the LLM call requires an external (free) API."),
        ("Streaming responses", "Both reasoning tokens and the final answer are streamed to the client over NDJSON for a responsive chat experience."),
    ]
    rows = [["Feature", "Description"]] + [[p(f"<b>{t}</b>", "BodySmall"), p(d, "BodySmall")] for t, d in features]
    feat_table = Table(rows, colWidths=[1.7 * inch, 4.6 * inch])
    feat_table.setStyle(TABLE_HEADER_STYLE)
    story.append(feat_table)
    story.append(PageBreak())

    # ---------------- 5. Agentic pipeline & event trace ----------------
    story += heading("5.", "The Agentic Pipeline & Event Trace")
    story.append(p(
        "The core of the system is <font face='Courier'>run_agent()</font> in "
        "<font face='Courier'>backend/app/agent/orchestrator.py</font>. It runs "
        "an iterative loop (up to <b>6 iterations</b>) against the Groq chat "
        "completions API with two tools available to the model:",
        "Body",
    ))
    tools_table = Table([
        ["Tool", "Description"],
        ["search_knowledge_base", "Semantic search over the user's uploaded documents. May be called multiple times with different/refined queries (multi-hop retrieval)."],
        ["list_knowledge_base_documents", "Lists all documents currently stored, including chunk counts — used to check what information is available."],
    ], colWidths=[2.0 * inch, 4.3 * inch])
    tools_table.setStyle(TABLE_HEADER_STYLE)
    story.append(tools_table)

    story.append(p("Agent loop, step by step", "H2"))
    steps = [
        "The system prompt instructs the agent on when to search, how to cite sources, and how to handle questions unrelated to the documents.",
        "The user's message (plus prior conversation history) is sent to the Groq model as a streaming chat-completion request, with both tools registered.",
        "If the model responds with <font face='Courier'>tool_calls</font>, each call is executed locally (against ChromaDB), the result is appended to the conversation as a <font face='Courier'>tool</font> message, and the loop repeats — enabling multi-hop retrieval.",
        "If the model responds with plain content and no further tool calls, that content is streamed back as the final answer and the loop ends.",
        "If neither happens within 6 iterations, an error event is emitted.",
    ]
    story.append(ListFlowable(
        [ListItem(p(s, "Body")) for s in steps],
        bulletType="1", leftIndent=16, bulletFontSize=9,
    ))

    story.append(p("Pipeline trace event types", "H2"))
    story.append(p(
        "Every step of the loop yields a small JSON event over "
        "<font face='Courier'>/api/chat</font>, allowing the frontend to render "
        "a live trace:",
        "Body",
    ))
    events_table = Table([
        ["Event type", "Meaning"],
        ["pipeline_step", "A named stage change, e.g. query received, agent reasoning (with active model), tool selected, or answer ready."],
        ["tool_call", "The agent is invoking a tool, with its name and parsed arguments."],
        ["tool_result", "The result returned from executing that tool (e.g. retrieved chunks)."],
        ["thinking", "Optional model reasoning tokens, if provided by the API."],
        ["token", "A streamed fragment of the assistant's response text."],
        ["final", "The complete final answer text."],
        ["done", "Marks the end of the stream (success or after an error)."],
        ["error", "A fatal error (e.g. missing API key, Groq API error, iteration limit reached)."],
    ], colWidths=[1.4 * inch, 4.9 * inch])
    events_table.setStyle(TABLE_HEADER_STYLE)
    story.append(events_table)
    story.append(PageBreak())

    # ---------------- 6. Project structure ----------------
    story += heading("6.", "Project Structure")
    tree_lines = [
        "Agentic-RAG-Full-Project/",
        "&nbsp;&nbsp;backend/",
        "&nbsp;&nbsp;&nbsp;&nbsp;app/",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;main.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# FastAPI app & routes",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;config.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Settings (.env driven)",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;models.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Pydantic schemas",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;rag/",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ingestion.py&nbsp;&nbsp;# Document loading + chunking",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;vectorstore.py&nbsp;# ChromaDB wrapper (local embeddings)",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;agent/",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tools.py&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Tool definitions for the agent",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;orchestrator.py&nbsp;# Agentic loop + pipeline trace events",
        "&nbsp;&nbsp;&nbsp;&nbsp;requirements.txt",
        "&nbsp;&nbsp;&nbsp;&nbsp;.env.example",
        "&nbsp;&nbsp;&nbsp;&nbsp;run.py",
        "&nbsp;&nbsp;frontend/",
        "&nbsp;&nbsp;&nbsp;&nbsp;src/",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;components/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Chat, DocumentSidebar, PipelineVisualizer, ...",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;api.ts&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Backend API client (incl. NDJSON streaming)",
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;types.ts&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Shared TypeScript types",
    ]
    story.append(code_block(tree_lines))
    story.append(PageBreak())

    # ---------------- 7. API reference ----------------
    story += heading("7.", "REST API Reference")
    api_table = Table([
        ["Endpoint", "Method", "Description"],
        ["/api/health", "GET", "Health check."],
        ["/api/config", "GET", "Active model / embedding / vector-store info for the UI (incl. whether the Groq key is configured)."],
        ["/api/upload", "POST", "Upload + ingest a document (multipart form, field ‘file’)."],
        ["/api/documents", "GET", "List ingested documents with chunk counts and sizes."],
        ["/api/documents/{source}", "DELETE", "Delete a document and all of its chunks."],
        ["/api/chat", "POST", "Body: { message, history }. Returns a streamed NDJSON pipeline trace + final answer."],
    ], colWidths=[1.7 * inch, 0.8 * inch, 3.8 * inch])
    api_table.setStyle(TABLE_HEADER_STYLE)
    story.append(api_table)

    story.append(p("Example: streaming chat request", "H2"))
    story.append(code_block([
        "POST /api/chat",
        "Content-Type: application/json",
        "",
        "{",
        '&nbsp;&nbsp;"message": "What does the report say about Q3 revenue?",',
        '&nbsp;&nbsp;"history": []',
        "}",
        "",
        "Response (application/x-ndjson, one JSON object per line):",
        '{"type": "pipeline_step", "step": "query_received", ...}',
        '{"type": "pipeline_step", "step": "agent_call", "model": "llama-3.3-70b-versatile"}',
        '{"type": "tool_call", "detail": {"name": "search_knowledge_base", ...}}',
        '{"type": "tool_result", "detail": {"results": [...]}}',
        '{"type": "token", "text": "Based on the report (source: q3.pdf), ..."}',
        '{"type": "final", "text": "..."}',
        '{"type": "done"}',
    ]))
    story.append(PageBreak())

    # ---------------- 8. Configuration ----------------
    story += heading("8.", "Configuration Reference")
    story.append(p(
        "All configuration is supplied via <font face='Courier'>backend/.env</font> "
        "(see <font face='Courier'>backend/.env.example</font>):",
        "Body",
    ))
    config_table = Table([
        ["Variable", "Default", "Description"],
        ["GROQ_API_KEY", "(required)", "Free Groq API key from console.groq.com/keys."],
        ["GROQ_MODEL", "llama-3.3-70b-versatile", "Model used by the agent."],
        ["CORS_ORIGINS", p("http://localhost:5173,<br/>http://127.0.0.1:5173", "BodySmall"), "Comma-separated list of allowed frontend origins."],
        ["CHUNK_SIZE / CHUNK_OVERLAP", "1000 / 200", "Text-splitter chunk size and overlap (characters)."],
        ["DEFAULT_TOP_K", "5", "Default number of chunks retrieved per search."],
        ["COLLECTION_NAME", "knowledge_base", "Name of the ChromaDB collection."],
    ], colWidths=[1.7 * inch, 1.6 * inch, 3.0 * inch])
    config_table.setStyle(TABLE_HEADER_STYLE)
    story.append(config_table)
    story.append(p(
        "Embeddings always use Chroma's bundled local ONNX MiniLM model "
        "(<font face='Courier'>all-MiniLM-L6-v2</font>) — no extra variable or "
        "key is needed for embeddings.",
        "Body",
    ))
    story.append(PageBreak())

    # ---------------- 9. Setup ----------------
    story += heading("9.", "Setup & Installation Guide")

    story.append(p("1. Backend", "H2"))
    story.append(code_block([
        "cd backend",
        "python -m venv venv",
        "./venv/Scripts/Activate.ps1      # or venv\\Scripts\\activate on cmd",
        "pip install -r requirements.txt",
        "",
        "cp .env.example .env",
        "# edit .env and set GROQ_API_KEY=gsk_...",
        "#   (free key: https://console.groq.com/keys)",
        "",
        "python run.py",
    ]))
    story.append(p(
        "The API runs at <font face='Courier'>http://localhost:8000</font>. The "
        "first request that touches the vector store automatically downloads "
        "the local embedding model (~80&nbsp;MB).",
        "Body",
    ))

    story.append(p("2. Frontend", "H2"))
    story.append(code_block([
        "cd frontend",
        "npm install",
        "npm run dev",
    ]))
    story.append(p(
        "The UI runs at <font face='Courier'>http://localhost:5173</font> and "
        "talks to the backend at <font face='Courier'>http://localhost:8000</font>.",
        "Body",
    ))
    story.append(PageBreak())

    # ---------------- 10. Using the application ----------------
    story += heading("10.", "Using the Application")
    usage_steps = [
        "Open the UI and upload one or more documents (PDF, DOCX, TXT, MD) via the sidebar — they are chunked, embedded locally, and stored in ChromaDB.",
        "Ask a question in the chat box. Watch the pipeline visualizer light up each stage as it happens: agent reasoning with the active Groq model, tool calls to search_knowledge_base, chunks retrieved from ChromaDB, and final answer generation.",
        "For multi-part questions, the agent decides on its own whether and how many times to search — you'll often see several search_knowledge_base calls before the final answer (multi-hop retrieval).",
        "Review the step-by-step log on the right for a full audit trail of every reasoning step, tool call, and tool result in the conversation.",
        "Manage the knowledge base from the sidebar: view document counts and sizes, or delete a document (and its chunks) when it's no longer needed.",
    ]
    story.append(ListFlowable(
        [ListItem(p(s, "Body")) for s in usage_steps],
        bulletType="1", leftIndent=16, bulletFontSize=9,
    ))
    story.append(PageBreak())

    # ---------------- 11. Conclusion ----------------
    story += heading("11.", "Conclusion & Future Work")
    story.append(p(
        "The Agentic RAG Pipeline demonstrates a practical, low-cost (free LLM "
        "tier, local embeddings, local vector store) implementation of an "
        "agent-driven RAG system with full transparency into its reasoning "
        "process via a live pipeline trace. It serves both as a usable "
        "document-Q&amp;A tool and as a teaching aid for how modern agentic RAG "
        "architectures work.",
        "Body",
    ))
    story.append(p("Potential future enhancements", "H2"))
    future = [
        "Support for additional LLM providers (e.g. OpenAI, Anthropic) via a pluggable provider layer.",
        "Persisted chat history / multi-conversation support with a lightweight database.",
        "Re-ranking of retrieved chunks before they are passed to the agent.",
        "Inline citation highlighting in the UI, linking answers back to source chunks.",
        "Authentication and per-user knowledge bases for multi-tenant deployments.",
        "Automated evaluation harness for retrieval quality and answer faithfulness.",
    ]
    story.append(ListFlowable(
        [ListItem(p(s, "Body")) for s in future],
        bulletType="bullet", start="•", leftIndent=14, bulletFontSize=9,
    ))

    return story


def main():
    doc = BaseDocTemplate(
        str(OUT_PATH),
        pagesize=LETTER,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Agentic RAG Pipeline - Project Documentation",
        author="Uzair Ali",
    )

    cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover")
    body_frame = Frame(
        MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN - 0.3 * inch, id="body"
    )

    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
        PageTemplate(id="later", frames=[body_frame], onPage=draw_later),
    ])

    doc.build(build_story())
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
