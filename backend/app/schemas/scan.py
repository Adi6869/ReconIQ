from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class FindingType(str, Enum):
    SUBDOMAIN = "subdomain"
    URL = "url"
    HISTORICAL_URL = "historical_url"
    HTTP_SERVICE = "http_service"
    DNS_RECORD = "dns_record"
    TECHNOLOGY = "technology"
    OPEN_PORT = "open_port"
    SCREENSHOT = "screenshot"
    DIRECTORY = "directory"
    CRAWLED_URL = "crawled_url"
    PARAMETER = "parameter"
    VULNERABILITY = "vulnerability"

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class Finding(BaseModel):
    type: FindingType
    value: str
    source: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None

class ToolExecution(BaseModel):
    tool_name: str
    status: ExecutionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    findings: List[Finding] = []
    errors: List[str] = []

class ScanRequest(BaseModel):
    target: str
    tools: Optional[List[str]] = None
    session_id: Optional[str] = None

class ScanResponse(BaseModel):
    scan_id: str
    target: str
    status: ExecutionStatus
    tools_executed: List[ToolExecution]
    total_findings: int
    session_id: str

class ExportRequest(BaseModel):
    session_id: str
    format: str = "json"  # json, csv, txt

class ExportResponse(BaseModel):
    filename: str
    content: str
    format: str