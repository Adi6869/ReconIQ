from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER_QUERY = "user_query"
    SYSTEM_RESPONSE = "system_response"
    TOOL_EXECUTION = "tool_execution"
    ERROR = "error"

class ChatMessage(BaseModel):
    timestamp: datetime
    type: MessageType
    content: str
    results: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tools_executed: Optional[List[str]] = None
    results: Optional[Dict[str, Any]] = None
    suggested_actions: Optional[List[str]] = None
    requires_clarification: bool = False

class SessionInfo(BaseModel):
    session_id: str
    start_time: datetime
    last_activity: datetime
    message_count: int
    
class SessionListResponse(BaseModel):
    sessions: List[SessionInfo]