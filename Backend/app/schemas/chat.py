from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, Literal


class MessageBase(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"]


class MessageCreate(MessageBase):
    conversation_id: int
    tool_used: Optional[str] = "none"
    message_metadata: Optional[Dict[str, Any]] = None


class Message(MessageBase):
    id: int
    conversation_id: int
    tool_used: Optional[str] = "none"
    langfuse_trace_id: Optional[str] = None
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    tool_selection: Literal["none", "internet", "auto"] = "auto"
    model: Optional[str] = None


class ChatResponse(BaseModel):
    message: Message
    conversation_id: int
    langfuse_trace_id: Optional[str] = None


class RegenerateRequest(BaseModel):
    message_id: int
    model: Optional[str] = None
