// ─────────────────────────────────────────────────────────────────────────────
// AutoStream Frontend – Shared Type Definitions
// ─────────────────────────────────────────────────────────────────────────────

export type Intent = "greeting" | "inquiry" | "high_intent";

export type ConversationStage =
  | "chat"
  | "collecting_name"
  | "collecting_email"
  | "collecting_platform"
  | "complete";

export interface LeadData {
  name?: string;
  email?: string;
  platform?: string;
}

// ── API Contracts ─────────────────────────────────────────────────────────────

export interface ChatRequest {
  message: string;
  session_id: string;
}

export interface ChatResponse {
  message: string;
  intent: Intent;
  session_id: string;
  conversation_stage: ConversationStage;
  lead_captured: boolean;
  lead_data?: LeadData;
  rag_sources?: string[];
}

// ── UI State ──────────────────────────────────────────────────────────────────

export type MessageRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  intent?: Intent;
  timestamp: Date;
  isTyping?: boolean;
}

export interface ChatState {
  messages: ChatMessage[];
  sessionId: string;
  intent: Intent;
  stage: ConversationStage;
  leadData: LeadData;
  leadCaptured: boolean;
  isLoading: boolean;
  error: string | null;
}
