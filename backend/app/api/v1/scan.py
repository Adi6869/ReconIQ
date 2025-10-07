from fastapi import APIRouter, HTTPException
from ...schemas.scan import ScanRequest, ScanResponse, ExportRequest, ExportResponse
from ...services.enhanced_tool_orchestrator import EnhancedToolOrchestrator
from ...services.session_manager import SessionManager
import uuid

router = APIRouter()
tool_orchestrator = EnhancedToolOrchestrator()
session_manager = SessionManager()

@router.post("/execute", response_model=ScanResponse)
async def execute_scan(request: ScanRequest):
    """Execute a reconnaissance scan"""
    try:
        scan_id = str(uuid.uuid4())
        session_id = request.session_id or session_manager.create_session()
        
        # Default tools if none specified
        tools = request.tools or ["subfinder", "assetfinder", "httpx"]
        
        # Create parsed intent for tool orchestrator
        parsed_intent = {
            "targets": [request.target],
            "tools": tools,
            "action": "subdomain_enumeration"
        }
        
        # Execute the scan
        results = await tool_orchestrator.execute_workflow(parsed_intent)
        
        # Save scan results to session
        await session_manager.add_message(
            session_id, 
            "tool_execution", 
            f"Executed scan on {request.target}",
            results
        )
        
        return ScanResponse(
            scan_id=scan_id,
            target=request.target,
            status="completed",
            tools_executed=[],  # Will be populated from results
            total_findings=results.get("total_findings", 0),
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan execution failed: {str(e)}")

@router.get("/tools")
async def list_available_tools():
    """List available reconnaissance tools"""
    return {
        "tools": [
            # Recon Tools
            {
                "name": "subfinder",
                "description": "Fast subdomain discovery tool",
                "type": "subdomain_enumeration"
            },
            {
                "name": "assetfinder",
                "description": "Fast subdomain discovery using various techniques",
                "type": "subdomain_enumeration"
            },
            {
                "name": "dnsx",
                "description": "Fast and multi-purpose DNS toolkit",
                "type": "dns_enumeration"
            },
            {
                "name": "httpx",
                "description": "Fast HTTP probe and web technology detection",
                "type": "http_probe"
            },
            {
                "name": "amass",
                "description": "In-depth DNS enumeration and network mapping",
                "type": "subdomain_enumeration"
            },
            # Port Scan Tools
            {
                "name": "nmap",
                "description": "Network exploration and security auditing tool",
                "type": "port_scan"
            },
            {
                "name": "naabu",
                "description": "Fast port scanner written in Go",
                "type": "port_scan"
            },
            # Screenshot Tools
            {
                "name": "gowitness",
                "description": "Web screenshot utility using Chrome Headless",
                "type": "screenshot"
            },
            {
                "name": "eyewitness",
                "description": "Web application screenshot tool with report generation",
                "type": "screenshot"
            },
            # Content Discovery
            {
                "name": "gobuster",
                "description": "Directory/file & DNS busting tool written in Go",
                "type": "content_discovery"
            },
            # Fuzzing & Endpoint Tools
            {
                "name": "ffuf",
                "description": "Fast web fuzzer written in Go",
                "type": "fuzzing"
            },
            {
                "name": "katana",
                "description": "Next-generation crawling and spidering framework",
                "type": "crawling"
            },
            {
                "name": "waybackurls",
                "description": "Fetch URLs from Wayback Machine archives",
                "type": "url_discovery"
            },
            {
                "name": "waymore",
                "description": "Tool for downloading archived web pages and extracting URLs",
                "type": "url_discovery"
            },
            # Parameter Discovery
            {
                "name": "paramspider",
                "description": "Parameter discovery tool for web applications",
                "type": "parameter_discovery"
            }
        ]
    }

@router.post("/export", response_model=ExportResponse)
async def export_session(request: ExportRequest):
    """Export session data in specified format"""
    try:
        export_data = await session_manager.export_session(
            request.session_id, 
            request.format
        )
        
        return ExportResponse(
            filename=export_data["filename"],
            content=export_data["content"],
            format=export_data["format"]
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")