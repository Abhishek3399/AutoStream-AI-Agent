"""
LangGraph node implementations for the AutoStream conversational agent.

Graph topology
--------------

  ┌─────────────┐
  │  retrieve   │   Pull relevant KB chunks via BM25
  └──────┬──────┘
         │
  ┌──────▼──────┐
  │    agent    │   Classify intent + generate response (Claude)
  └──────┬──────┘
         │  (conditional)
  ┌──────▼──────┐
  │   capture   │   Execute mock_lead_capture when all fields collected
  └─────────────┘
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .state import ConversationState
from .tools import mock_lead_capture
from ..rag.retriever import BM25Retriever

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

def _build_system_prompt(
    stage: str,
    lead_info: Dict[str, Any],
    rag_context: str,
) -> str:
    lead_summary = json.dumps({k: v for k, v in lead_info.items() if v}, indent=2) or "{}"

    return f"""You are AutoStream's intelligent AI sales assistant.
AutoStream is a SaaS platform that automates video editing for content creators.

━━━ KNOWLEDGE BASE ━━━
{rag_context}

━━━ CONVERSATION RULES ━━━
1. Answer ONLY from the knowledge base above – never invent features, prices, or policies.
2. Classify every user message into one intent:
   • greeting      – hello, hi, how are you, casual openers
   • inquiry       – questions about features, pricing, plans, policies, comparisons
   • high_intent   – wants to sign up / start a trial / says "I want to try" / asks "how do I start"

3. Lead collection flow (follow EXACTLY):
   • When intent == high_intent AND stage == "chat"  → warmly acknowledge interest, set stage to "collecting_name", ask for their first name.
   • When stage == "collecting_name"                 → extract the name the user just gave, set stage to "collecting_email", ask for their email address.
   • When stage == "collecting_email"                → extract the email, set stage to "collecting_platform", ask which creator platform they use.
   • When stage == "collecting_platform"             → extract the platform, set stage to "complete".
   • NEVER ask for all fields at once.
   • NEVER set stage to "complete" before all three fields are extracted.

━━━ CURRENT STATE ━━━
Stage         : {stage}
Collected so far: {lead_summary}

━━━ RESPONSE FORMAT ━━━
Respond ONLY with a single valid JSON object – no markdown fences, no extra text.

{{
  "intent": "greeting|inquiry|high_intent",
  "message": "<your conversational reply to the user>",
  "stage": "chat|collecting_name|collecting_email|collecting_platform|complete",
  "extracted_value": "<the specific value the user just provided (name/email/platform), or null>"
}}
"""


# ---------------------------------------------------------------------------
# Node: retrieve
# ---------------------------------------------------------------------------

def retrieve_node(retriever: BM25Retriever):
    """Factory – returns a node function bound to the provided retriever."""

    def _retrieve(state: ConversationState) -> Dict[str, Any]:
        # Use the last human message as the query
        last_human = next(
            (m for m in reversed(state["messages"]) if isinstance(m, HumanMessage)),
            None,
        )
        if last_human is None:
            return {"rag_context": "", "rag_sources": []}

        query = last_human.content
        rag_context = retriever.get_context_string(query)
        rag_sources = retriever.get_source_titles(query)

        logger.debug("Retrieved %d KB sources for query: %s", len(rag_sources), query)
        return {"rag_context": rag_context, "rag_sources": rag_sources}

    return _retrieve


# ---------------------------------------------------------------------------
# Node: agent
# ---------------------------------------------------------------------------

def agent_node(llm: ChatAnthropic):
    """Factory – returns a node function bound to the provided LLM."""

    def _agent(state: ConversationState) -> Dict[str, Any]:
        stage = state.get("conversation_stage", "chat")
        lead_info = state.get("lead_info", {})
        rag_context = state.get("rag_context", "")

        system_prompt = _build_system_prompt(stage, lead_info, rag_context)

        # Build message list: system + full conversation history
        lc_messages = [SystemMessage(content=system_prompt)] + list(state["messages"])

        # ── LLM call ──────────────────────────────────────────────────────
        response = llm.invoke(lc_messages)
        raw_content = response.content.strip()

        # ── Parse JSON ────────────────────────────────────────────────────
        parsed = _safe_parse_json(raw_content, stage)

        new_intent = parsed.get("intent", "inquiry")
        new_stage = parsed.get("stage", stage)
        extracted = parsed.get("extracted_value")
        agent_message = parsed.get("message", raw_content)

        # ── Update lead_info incrementally ────────────────────────────────
        updated_lead_info = dict(lead_info)
        if extracted:
            if stage == "collecting_name":
                updated_lead_info["name"] = extracted
            elif stage == "collecting_email":
                updated_lead_info["email"] = extracted
            elif stage == "collecting_platform":
                updated_lead_info["platform"] = extracted

        logger.info(
            "agent_node | intent=%s stage=%s→%s extracted=%s",
            new_intent,
            stage,
            new_stage,
            extracted,
        )

        return {
            "messages": [AIMessage(content=agent_message)],
            "intent": new_intent,
            "conversation_stage": new_stage,
            "lead_info": updated_lead_info,
            "lead_captured": state.get("lead_captured", False),
        }

    return _agent


# ---------------------------------------------------------------------------
# Node: capture
# ---------------------------------------------------------------------------

def capture_node(state: ConversationState) -> Dict[str, Any]:
    """
    Invokes mock_lead_capture once all three fields are present.
    Only reached when conversation_stage == 'complete' and lead not yet captured.
    """
    lead_info = state.get("lead_info", {})
    name = lead_info.get("name", "")
    email = lead_info.get("email", "")
    platform = lead_info.get("platform", "")

    confirmation = mock_lead_capture(name=name, email=email, platform=platform)

    # Craft a warm closing message
    closing = (
        f"🎉 You're all set, {name}! "
        f"I've registered your interest and our team will reach out to {email} within 24 hours. "
        f"We're excited to help you supercharge your {platform} content with AutoStream. "
        f"In the meantime, you can start your free 14-day trial at autostream.io/start 🚀"
    )

    logger.info("capture_node executed | %s", confirmation)

    return {
        "messages": [AIMessage(content=closing)],
        "lead_captured": True,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_parse_json(raw: str, fallback_stage: str) -> Dict[str, Any]:
    """Extract and parse JSON from the LLM output, with graceful fallback."""
    # Try direct parse first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block from the string
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Last-resort fallback
    logger.warning("LLM returned non-JSON response; using fallback")
    return {
        "intent": "inquiry",
        "message": raw,
        "stage": fallback_stage,
        "extracted_value": None,
    }


# ---------------------------------------------------------------------------
# Conditional edge functions
# ---------------------------------------------------------------------------

def should_capture(state: ConversationState) -> str:
    """Route to 'capture' node if all lead fields are ready; else END."""
    if (
        state.get("conversation_stage") == "complete"
        and not state.get("lead_captured", False)
    ):
        lead = state.get("lead_info", {})
        if lead.get("name") and lead.get("email") and lead.get("platform"):
            return "capture"
    return "__end__"
