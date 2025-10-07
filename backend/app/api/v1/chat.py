from fastapi import APIRouter, HTTPException
from typing import List
import asyncio
from ...schemas.chat import ChatRequest, ChatResponse, SessionInfo, SessionListResponse
from ...services.gemini_client import GeminiClient
from ...services.session_manager import SessionManager
from ...services.enhanced_tool_orchestrator import EnhancedToolOrchestrator

router = APIRouter()
gemini_client = GeminiClient()
session_manager = SessionManager()
tool_orchestrator = EnhancedToolOrchestrator()

@router.post("/message", response_model=ChatResponse)
async def process_message(request: ChatRequest):
    """Process a chat message and execute reconnaissance if needed"""
    try:
        # Safely log the message
        safe_message = str(request.message)[:50].replace('{', '{{').replace('}', '}}')
        print(f"📨 Processing message: {safe_message}...")
        
        # Get or create session
        session_id = request.session_id or session_manager.create_session()
        
        # Get conversation context
        context = await session_manager.get_conversation_history(session_id)
        
        # Parse the query using Gemini (run in thread pool to avoid blocking)
        print("🤖 Calling Gemini API for query parsing...")
        parsed_intent = await asyncio.to_thread(gemini_client.parse_query, request.message, context)
        print("✅ Gemini response received")
        
        # Save user message
        await session_manager.add_message(session_id, "user_query", request.message)
        
        # Check if clarification is needed
        if parsed_intent.get("clarification_needed", False):
            clarification = parsed_intent.get("clarification_question")
            if not clarification:
                clarification = await asyncio.to_thread(gemini_client.ask_clarification, request.message)
            
            # Add helpful suggestions based on the action type
            action = parsed_intent.get("action", "")
            if "subdomain" in action:
                clarification += "\n\n**Examples:**\n• Find subdomains for google.com\n• Enumerate subdomains on tesla.com\n• Discover assets for microsoft.com"
            elif "port" in action:
                clarification += "\n\n**Examples:**\n• Scan ports on 192.168.1.1\n• Run nmap on github.com\n• Check open ports on example.org"
            elif "screenshot" in action:
                clarification += "\n\n**Examples:**\n• Take screenshots of reddit.com\n• Capture visuals for facebook.com"
            elif "content" in action:
                clarification += "\n\n**Examples:**\n• Find directories on tesla.com\n• Discover content on github.com"
            
            await session_manager.add_message(session_id, "system_response", clarification)
            
            return ChatResponse(
                reply=clarification,
                session_id=session_id,
                requires_clarification=True
            )
        
        # Execute reconnaissance tools if targets are identified
        results = {}
        tools_executed = []
        
        targets = parsed_intent.get("targets", [])
        tools = parsed_intent.get("tools", [])
        
        if targets and tools:
            # Extract tool configurations from parsed intent
            tool_configs = parsed_intent.get("tool_configs", {})
            
            # Check if user requested a preset
            preset = parsed_intent.get("preset")
            if preset:
                print(f"🎯 Using preset: {preset}")
                # You could load preset configs here if needed
            
            results = await tool_orchestrator.execute_workflow(parsed_intent, tool_configs)
            tools_executed = tools
            
            # Save tool execution message
            targets_str = ', '.join(str(target) for target in targets)
            tools_str = ', '.join(str(tool) for tool in tools_executed)
            execution_msg = f"Executed {tools_str} on {targets_str}"
            await session_manager.add_message(session_id, "tool_execution", execution_msg)
        
        # Generate natural language response (run in thread pool to avoid blocking)
        reply = await asyncio.to_thread(gemini_client.generate_response, results, request.message)
        
        # Save system response
        await session_manager.add_message(session_id, "system_response", reply)
        
        return ChatResponse(
            reply=reply,
            session_id=session_id,
            tools_executed=tools_executed,
            results=results,
            requires_clarification=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """List all available sessions"""
    try:
        sessions = await session_manager.list_sessions()
        return SessionListResponse(sessions=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing sessions: {str(e)}")

@router.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    try:
        history = await session_manager.get_conversation_history(session_id)
        return {"session_id": session_id, "messages": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session history: {str(e)}")

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        await session_manager.delete_session(session_id)
        return {"message": f"Session {session_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.post("/test")
async def test_endpoint(request: ChatRequest):
    """Simple test endpoint without Gemini integration"""
    return ChatResponse(
        reply=f"Echo: {request.message}",
        session_id="test-session",
        tools_executed=[],
        results={},
        requires_clarification=False
    )
