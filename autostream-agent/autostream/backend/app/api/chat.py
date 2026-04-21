"""
Chat API router.

Endpoints
---------
POST /api/chat          – Send a user message, receive agent response
POST /api/reset         – Clear session memory
GET  /api/health        – Health check
"""

from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, Request

from ..agent.graph import AutoStreamAgent
from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationStage,
    HealthResponse,
    Intent,
    LeadData,
    SessionResetRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


# ---------------------------------------------------------------------------
# Dependency injection – single agent instance per process
# ---------------------------------------------------------------------------

def get_agent(request: Request) -> AutoStreamAgent:
    """Retrieve the AutoStreamAgent singleton from app state."""
    return request.app.state.agent


# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse, summary="Send a chat message")
async def chat(body: ChatRequest, agent: AutoStreamAgent = Depends(get_agent)):
    """
    Process one conversational turn.

    The agent:
    1. Retrieves relevant KB context (RAG)
    2. Classifies intent and generates a response
    3. Manages the lead-collection state machine
    4. Invokes mock_lead_capture when all fields are gathered
    """
    try:
        result = agent.chat(message=body.message, session_id=body.session_id)
    except Exception as exc:
        logger.exception("Agent error: %s", exc)
        raise HTTPException(status_code=500, detail="Agent processing failed") from exc

    # Extract last AI message
    from langchain_core.messages import AIMessage
    ai_messages = [m for m in result.get("messages", []) if isinstance(m, AIMessage)]
    response_text = ai_messages[-1].content if ai_messages else "I'm sorry, something went wrong."

    # Build lead data if captured
    lead_info = result.get("lead_info", {})
    lead_data = None
    if result.get("lead_captured") or lead_info:
        lead_data = LeadData(
            name=lead_info.get("name"),
            email=lead_info.get("email"),
            platform=lead_info.get("platform"),
        )

    return ChatResponse(
        message=response_text,
        intent=Intent(result.get("intent", "inquiry")),
        session_id=body.session_id,
        conversation_stage=ConversationStage(result.get("conversation_stage", "chat")),
        lead_captured=result.get("lead_captured", False),
        lead_data=lead_data,
        rag_sources=result.get("rag_sources", []),
    )


# ---------------------------------------------------------------------------
# POST /api/reset
# ---------------------------------------------------------------------------

@router.post("/reset", summary="Reset a conversation session")
async def reset_session(body: SessionResetRequest, agent: AutoStreamAgent = Depends(get_agent)):
    """Clear all persisted memory for the given session_id."""
    try:
        agent.reset_session(body.session_id)
    except Exception as exc:
        logger.warning("Could not reset session %s: %s", body.session_id, exc)

    return {"status": "ok", "session_id": body.session_id, "message": "Session cleared."}


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------

@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health():
    import os
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
    )
