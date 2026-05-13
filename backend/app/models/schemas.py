from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: list[ChatMessage] = Field(default_factory=list)
    uploaded_file_id: Optional[str] = None


class FileAction(str, Enum):
    GENERATE = "generate"
    WALKTHROUGH = "walkthrough"
    MODIFY = "modify"


class ChatResponse(BaseModel):
    message: str
    action: FileAction
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    conversation_id: str
    walkthrough_steps: Optional[list[str]] = None


class FileUploadResponse(BaseModel):
    file_id: str
    file_name: str
    sheet_names: list[str]
    summary: str


class FileModifyRequest(BaseModel):
    file_id: str
    instructions: str
    history: list[ChatMessage] = Field(default_factory=list)


class FileModifyResponse(BaseModel):
    message: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    walkthrough_steps: Optional[list[str]] = None


class HealthResponse(BaseModel):
    status: str
    version: str
