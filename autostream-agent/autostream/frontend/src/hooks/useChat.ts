"use client";

import { useCallback, useRef, useState } from "react";
import { v4 as uuidv4 } from "uuid";

import { sendMessage, resetSession } from "@/lib/api";
import type { ChatMessage, ChatState, ConversationStage, Intent, LeadData } from "@/types";

// ─────────────────────────────────────────────────────────────────────────────
// Initial state helpers
// ─────────────────────────────────────────────────────────────────────────────

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Hey there! 👋 I'm Stream, AutoStream's AI assistant. I can help you discover the best plan for your content creation workflow, answer questions about features, or get you started with a free trial. What's on your mind?",
  intent: "greeting",
  timestamp: new Date(),
};

function makeInitialState(): ChatState {
  return {
    messages: [WELCOME_MESSAGE],
    sessionId: uuidv4(),
    intent: "greeting",
    stage: "chat",
    leadData: {},
    leadCaptured: false,
    isLoading: false,
    error: null,
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────────

export function useChat() {
  const [state, setState] = useState<ChatState>(makeInitialState);
  const abortRef = useRef<AbortController | null>(null);

  // ── Send a user message ───────────────────────────────────────────────────
  const sendUserMessage = useCallback(async (text: string) => {
    if (!text.trim() || state.isLoading) return;

    const userMsg: ChatMessage = {
      id: uuidv4(),
      role: "user",
      content: text.trim(),
      timestamp: new Date(),
    };

    const typingMsg: ChatMessage = {
      id: "typing",
      role: "assistant",
      content: "",
      isTyping: true,
      timestamp: new Date(),
    };

    // Optimistically add user message + typing indicator
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, userMsg, typingMsg],
      isLoading: true,
      error: null,
    }));

    try {
      const response = await sendMessage({
        message: text.trim(),
        session_id: state.sessionId,
      });

      const assistantMsg: ChatMessage = {
        id: uuidv4(),
        role: "assistant",
        content: response.message,
        intent: response.intent,
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        // Replace typing indicator with real response
        messages: [
          ...prev.messages.filter((m) => m.id !== "typing"),
          assistantMsg,
        ],
        intent: response.intent,
        stage: response.conversation_stage,
        leadData: response.lead_data ?? prev.leadData,
        leadCaptured: response.lead_captured,
        isLoading: false,
      }));
    } catch (err) {
      const errorMsg: ChatMessage = {
        id: uuidv4(),
        role: "assistant",
        content: "I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
      };

      setState((prev) => ({
        ...prev,
        messages: [
          ...prev.messages.filter((m) => m.id !== "typing"),
          errorMsg,
        ],
        isLoading: false,
        error: err instanceof Error ? err.message : "Unknown error",
      }));
    }
  }, [state.isLoading, state.sessionId]);

  // ── Reset conversation ────────────────────────────────────────────────────
  const reset = useCallback(async () => {
    await resetSession(state.sessionId).catch(() => {});
    setState(makeInitialState());
  }, [state.sessionId]);

  return { state, sendUserMessage, reset };
}
