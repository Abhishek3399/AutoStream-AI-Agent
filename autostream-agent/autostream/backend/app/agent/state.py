from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from langchain_core.messages import BaseMessage


class LeadInfo(TypedDict, total=False):
    name: Optional[str]
    email: Optional[str]
    platform: Optional[str]


class ConversationState(TypedDict):
    """
    The shared mutable state that flows through every node in the
    AutoStream LangGraph conversation graph.

    Fields
    ------
    messages          – Full conversation history.  LangGraph appends to this
                        list automatically via the Annotated[…, operator.add] hint.
    session_id        – Unique identifier that maps to a MemorySaver thread.
    intent            – Most recently classified user intent.
    conversation_stage– Where we are in the lead-collection flow.
    lead_info         – Incrementally collected lead fields.
    lead_captured     – True once mock_lead_capture has been invoked.
    rag_context       – Formatted KB snippets injected into the agent prompt.
    rag_sources       – Titles of KB documents used (for API metadata).
    """

    messages: Annotated[List[BaseMessage], operator.add]
    session_id: str
    intent: str                   # "greeting" | "inquiry" | "high_intent"
    conversation_stage: str       # "chat" | "collecting_name" | "collecting_email" | "collecting_platform" | "complete"
    lead_info: LeadInfo
    lead_captured: bool
    rag_context: str
    rag_sources: List[str]
