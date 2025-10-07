import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from ..schemas.chat import ChatMessage, MessageType, SessionInfo
from ..config import settings
import aiofiles

class SessionManager:
    def __init__(self):
        self.sessions_dir = settings.sessions_dir
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def create_session(self) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        return session_id
    
    async def add_message(self, session_id: str, message_type: str, content: str, results: Optional[Dict[str, Any]] = None):
        """Add a message to the session history"""
        message = ChatMessage(
            timestamp=datetime.now(),
            type=MessageType(message_type),
            content=content,
            results=results
        )
        
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        # Load existing session or create new
        session_data = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": []
        }
        
        if os.path.exists(session_file):
            async with aiofiles.open(session_file, 'r') as f:
                content_str = await f.read()
                if content_str.strip():
                    session_data = json.loads(content_str)
        
        # Add new message
        session_data["messages"].append({
            "timestamp": message.timestamp.isoformat(),
            "type": message.type.value,
            "content": message.content,
            "results": message.results
        })
        session_data["last_activity"] = datetime.now().isoformat()
        
        # Save session
        async with aiofiles.open(session_file, 'w') as f:
            await f.write(json.dumps(session_data, indent=2))
    
    async def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """Get conversation history for a session"""
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            return []
        
        async with aiofiles.open(session_file, 'r') as f:
            content = await f.read()
            if not content.strip():
                return []
            
            session_data = json.loads(content)
            messages = []
            
            for msg_data in session_data.get("messages", []):
                messages.append(ChatMessage(
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    type=MessageType(msg_data["type"]),
                    content=msg_data["content"],
                    results=msg_data.get("results")
                ))
            
            return messages
    
    async def list_sessions(self) -> List[SessionInfo]:
        """List all available sessions"""
        sessions = []
        
        if not os.path.exists(self.sessions_dir):
            return sessions
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json extension
                session_file = os.path.join(self.sessions_dir, filename)
                
                try:
                    async with aiofiles.open(session_file, 'r') as f:
                        content = await f.read()
                        if content.strip():
                            session_data = json.loads(content)
                            
                            sessions.append(SessionInfo(
                                session_id=session_id,
                                start_time=datetime.fromisoformat(session_data["start_time"]),
                                last_activity=datetime.fromisoformat(session_data["last_activity"]),
                                message_count=len(session_data.get("messages", []))
                            ))
                except Exception as e:
                    print(f"Error reading session {session_id}: {e}")
                    continue
        
        # Sort by last activity (most recent first)
        sessions.sort(key=lambda x: x.last_activity, reverse=True)
        return sessions
    
    async def delete_session(self, session_id: str):
        """Delete a session"""
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if os.path.exists(session_file):
            os.remove(session_file)
    
    async def cleanup_old_sessions(self):
        """Clean up sessions older than max_session_age_days"""
        cutoff_date = datetime.now() - timedelta(days=settings.max_session_age_days)
        
        sessions = await self.list_sessions()
        for session in sessions:
            if session.last_activity < cutoff_date:
                await self.delete_session(session.session_id)
    
    async def export_session(self, session_id: str, format: str = "json") -> Dict[str, Any]:
        """Export session data in specified format"""
        session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
        
        if not os.path.exists(session_file):
            raise FileNotFoundError(f"Session {session_id} not found")
        
        async with aiofiles.open(session_file, 'r') as f:
            session_data = json.loads(await f.read())
        
        if format.lower() == "json":
            return {
                "filename": f"session_{session_id}.json",
                "content": json.dumps(session_data, indent=2),
                "format": "json"
            }
        elif format.lower() == "txt":
            # Convert to readable text format
            content_lines = [f"ReconIQ Session Export - {session_id}"]
            content_lines.append(f"Start Time: {session_data['start_time']}")
            content_lines.append(f"Last Activity: {session_data['last_activity']}")
            content_lines.append("=" * 50)
            
            for msg in session_data.get("messages", []):
                content_lines.append(f"\n[{msg['timestamp']}] {msg['type'].upper()}")
                content_lines.append(msg['content'])
                if msg.get('results'):
                    content_lines.append(f"Results: {json.dumps(msg['results'], indent=2)}")
            
            return {
                "filename": f"session_{session_id}.txt",
                "content": "\n".join(content_lines),
                "format": "txt"
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")