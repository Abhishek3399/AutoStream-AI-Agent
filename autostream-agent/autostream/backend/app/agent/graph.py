"""
AutoStream LangGraph conversation graph.

Architecture
────────────

  START
    │
  [retrieve]  ← BM25 RAG over knowledge base
    │
  [agent]     ← Claude Haiku (intent + response + lead state machine)
    │
  [conditional edge: should_capture?]
    ├── yes → [capture]  ← mock_lead_capture()
    └── no  → END

MemorySaver persists the full ConversationState per session_id (thread_id),
enabling seamless multi-turn conversations across HTTP requests.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from .nodes import agent_node, capture_node, retrieve_node, should_capture
from .state import ConversationState
from ..rag.loader import KnowledgeBaseLoader
from ..rag.retriever import BM25Retriever

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default knowledge-base path (resolved relative to this file)
# ---------------------------------------------------------------------------
_DEFAULT_KB_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "knowledge_base"
    / "autostream_kb.json"
)


class AutoStreamAgent:
    """
    Encapsulates the full LangGraph pipeline for the AutoStream
    conversational sales agent.

    Usage
    -----
    agent = AutoStreamAgent()
    result = await agent.chat("Tell me about the Pro plan", session_id="abc123")
    """

    def __init__(self, kb_path: Optional[str] = None):
        kb_path = kb_path or str(_DEFAULT_KB_PATH)

        # ── Knowledge base + retriever ────────────────────────────────────
        loader = KnowledgeBaseLoader(kb_path)
        self._retriever = BM25Retriever(loader.get_all_documents())

        # ── LLM ──────────────────────────────────────────────────────────
        self._llm = ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
            temperature=0.25,
            max_tokens=1024,
        )

        # ── Memory (persists across HTTP calls per session) ───────────────
        self._memory = MemorySaver()

        # ── Build graph ───────────────────────────────────────────────────
        self._graph = self._build_graph()
        logger.info("AutoStreamAgent initialised successfully")

    # ------------------------------------------------------------------
    # Graph construction
    # ------------------------------------------------------------------

    def _build_graph(self):
        graph = StateGraph(ConversationState)

        # Nodes
        graph.add_node("retrieve", retrieve_node(self._retriever))
        graph.add_node("agent", agent_node(self._llm))
        graph.add_node("capture", capture_node)

        # Edges
        graph.set_entry_point("retrieve")
        graph.add_edge("retrieve", "agent")
        graph.add_conditional_edges(
            "agent",
            should_capture,
            {"capture": "capture", "__end__": END},
        )
        graph.add_edge("capture", END)

        return graph.compile(checkpointer=self._memory)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, message: str, session_id: str) -> Dict[str, Any]:
        """
        Process one user turn and return the updated state.

        Returns the full ConversationState dict so the API layer can
        extract intent, stage, lead_data, etc.
        """
        config = {"configurable": {"thread_id": session_id}}

        # Fetch existing state to preserve stage + lead_info across turns
        snapshot = self._graph.get_state(config)
        prior = snapshot.values if snapshot else {}

        input_state: ConversationState = {
            "messages": [HumanMessage(content=message)],
            "session_id": session_id,
            "intent": prior.get("intent", "greeting"),
            "conversation_stage": prior.get("conversation_stage", "chat"),
            "lead_info": prior.get("lead_info", {}),
            "lead_captured": prior.get("lead_captured", False),
            "rag_context": "",
            "rag_sources": [],
        }

        result = self._graph.invoke(input_state, config=config)
        logger.info(
            "chat | session=%s intent=%s stage=%s lead_captured=%s",
            session_id,
            result.get("intent"),
            result.get("conversation_stage"),
            result.get("lead_captured"),
        )
        return result

    def reset_session(self, session_id: str) -> None:
        """Clear persisted memory for a given session (useful for testing)."""
        config = {"configurable": {"thread_id": session_id}}
        self._memory.delete(config)
        logger.info("Session %s reset", session_id)
