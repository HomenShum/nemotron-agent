"""
Nemotron 3 Ultra Agent — LangGraph + FastAPI
Deployed on GMI Cloud Agentbox

GMI injects at runtime:
  GMI_MAAS_BASE_URL  — OpenAI-compatible base URL
  GMI_MAAS_API_KEY   — MaaS API key
  GMI_MODELS         — model ID (nvidia/nemotron-3-ultra-550b-a55b)
"""

import os
import uuid
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# ── GMI MaaS connection (injected at runtime) ──────────────────────────────
BASE_URL = os.environ.get("GMI_MAAS_BASE_URL", "https://api.gmi-serving.com")
API_KEY  = os.environ.get("GMI_MAAS_API_KEY", "")
MODEL    = os.environ.get("GMI_MODELS", "nvidia/nemotron-3-ultra-550b-a55b")

# ── LangGraph state ─────────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# ── LLM client ──────────────────────────────────────────────────────────────
def get_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        model=MODEL,
        base_url=f"{BASE_URL}/v1",
        api_key=API_KEY,
        streaming=streaming,
        temperature=0.7,
        max_tokens=2048,
    )

# ── LangGraph node ──────────────────────────────────────────────────────────
def call_model(state: AgentState) -> dict:
    llm = get_llm()
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# ── Build graph ─────────────────────────────────────────────────────────────
def build_graph() -> Any:
    builder = StateGraph(AgentState)
    builder.add_node("agent", call_model)
    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)
    return builder.compile()

graph = build_graph()

# ── FastAPI app ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Nemotron 3 Ultra Agent",
    description="LangGraph + FastAPI agent powered by Nemotron 3 Ultra on GMI Cloud",
    version="1.0.0",
)

# ── Request / Response models ───────────────────────────────────────────────
class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]
    session_id: str | None = None
    system_prompt: str | None = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    model: str

# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL,
        "base_url": BASE_URL,
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Single-turn or multi-turn chat with Nemotron 3 Ultra via LangGraph."""
    session_id = req.session_id or str(uuid.uuid4())

    # Build message list
    lc_messages = []
    if req.system_prompt:
        lc_messages.append(SystemMessage(content=req.system_prompt))
    for m in req.messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            lc_messages.append(AIMessage(content=m.content))
        elif m.role == "system":
            lc_messages.append(SystemMessage(content=m.content))

    try:
        result = graph.invoke({"messages": lc_messages})
        reply = result["messages"][-1].content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(session_id=session_id, reply=reply, model=MODEL)


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    """Streaming chat — returns server-sent events."""
    lc_messages = []
    if req.system_prompt:
        lc_messages.append(SystemMessage(content=req.system_prompt))
    for m in req.messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            lc_messages.append(AIMessage(content=m.content))

    def generate():
        llm = get_llm(streaming=True)
        for chunk in llm.stream(lc_messages):
            token = chunk.content
            if token:
                yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/")
def root():
    return {
        "agent": "Nemotron 3 Ultra Agent",
        "model": MODEL,
        "endpoints": ["/health", "/chat", "/chat/stream"],
        "docs": "/docs",
    }
