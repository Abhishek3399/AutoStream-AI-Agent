from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from enum import Enum


class Intent(str, Enum):
    GREETING = "greeting"
    INQUIRY = "inquiry"
    HIGH_INTENT = "high_intent"


class ConversationStage(str, Enum):
    CHAT = "chat"
    COLLECTING_NAME = "collecting_name"
    COLLECTING_EMAIL = "collecting_email"
    COLLECTING_PLATFORM = "collecting_platform"
    COMPLETE = "complete"


class LeadData(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    platform: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's chat message")
    session_id: str = Field(..., description="Unique session ID for conversation continuity")


class ChatResponse(BaseModel):
    message: str = Field(..., description="Agent's response message")
    intent: Intent = Field(..., description="Classified user intent")
    session_id: str
    conversation_stage: ConversationStage = Field(default=ConversationStage.CHAT)
    lead_captured: bool = Field(default=False)
    lead_data: Optional[LeadData] = None
    rag_sources: Optional[list[str]] = Field(default=None, description="Knowledge base sources used")


class HealthResponse(BaseModel):
    status: str
    version: str
    model: str


class SessionResetRequest(BaseModel):
    session_id: str
