from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from ...services.enhanced_tool_orchestrator import EnhancedToolOrchestrator
from ...schemas.scan import ScanRequest, ScanResponse
from pydantic import BaseModel

router = APIRouter()
orchestrator = EnhancedToolOrchestrator()

class ToolConfigRequest(BaseModel):
    tool_name: str
    config: Dict[str, Any]

class CustomScanRequest(BaseModel):
    target: str
    tools: List[str]
    tool_configs: Dict[str, Dict[str, Any]] = {}
    session_id: str = None

class ToolCapabilitiesResponse(BaseModel):
    name: str
    available: bool
    version: str
    supported_options: Dict[str, Any]
    default_config: Dict[str, Any]
    description: str

@router.get("/capabilities/{tool_name}", response_model=ToolCapabilitiesResponse)
async def get_tool_capabilities(tool_name: str):
    """Get detailed capabilities and configuration options for a specific tool"""
    try:
        capabilities = await orchestrator.get_tool_capabilities(tool_name)
        
        if not capabilities:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        return ToolCapabilitiesResponse(**capabilities)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tool capabilities: {str(e)}")

@router.get("/capabilities")
async def get_all_tool_capabilities():
    """Get capabilities for all available tools"""
    try:
        all_capabilities = {}
        
        for tool_name in [
            "subfinder", "assetfinder", "dnsx", "httpx", "amass",
            "nmap", "naabu", "gowitness", "eyewitness", "gobuster",
            "ffuf", "katana", "waybackurls", "waymore", "paramspider"
        ]:
            capabilities = await orchestrator.get_tool_capabilities(tool_name)
            if capabilities:
                all_capabilities[tool_name] = capabilities
        
        return {"tools": all_capabilities}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tool capabilities: {str(e)}")

@router.post("/validate-config")
async def validate_tool_config(request: ToolConfigRequest):
    """Validate configuration for a specific tool"""
    try:
        validation_result = await orchestrator.validate_tool_config(
            request.tool_name, 
            request.config
        )
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating config: {str(e)}")

@router.post("/custom-scan")
async def execute_custom_scan(request: CustomScanRequest):
    """Execute a reconnaissance scan with custom tool configurations"""
    try:
        # Create parsed intent for the orchestrator
        parsed_intent = {
            "targets": [request.target],
            "tools": request.tools,
            "action": "custom_reconnaissance"
        }
        
        # Execute with custom configurations
        results = await orchestrator.execute_workflow(parsed_intent, request.tool_configs)
        
        return {
            "scan_id": f"custom_{request.target}_{len(request.tools)}",
            "target": request.target,
            "tools_executed": results.get("tools_executed", []),
            "total_findings": results.get("total_findings", 0),
            "execution_summary": results.get("execution_summary", {}),
            "findings": results.get("findings", []),
            "session_id": request.session_id or "custom-session"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom scan failed: {str(e)}")

@router.get("/presets")
async def get_tool_presets():
    """Get predefined tool configuration presets"""
    return {
        "presets": {
            "quick_scan": {
                "description": "Fast reconnaissance with minimal resource usage",
                "tools": ["subfinder", "assetfinder", "httpx"],
                "configs": {
                    "subfinder": {
                        "max_time": 2,
                        "threads": 5,
                        "sources": ["shodan", "censys"]
                    },
                    "assetfinder": {
                        "timeout": 30
                    },
                    "httpx": {
                        "threads": 25,
                        "timeout": 5,
                        "ports": ["80", "443"]
                    }
                }
            },
            "comprehensive_scan": {
                "description": "Thorough reconnaissance with all core tools",
                "tools": ["subfinder", "assetfinder", "amass", "dnsx", "httpx", "naabu", "waybackurls", "katana"],
                "configs": {
                    "subfinder": {
                        "max_time": 10,
                        "threads": 20,
                        "recursive": True
                    },
                    "assetfinder": {
                        "timeout": 60
                    },
                    "amass": {
                        "mode": "passive",
                        "timeout": 15,
                        "alterations": True
                    },
                    "dnsx": {
                        "a": True,
                        "cname": True,
                        "threads": 25
                    },
                    "httpx": {
                        "threads": 100,
                        "tech_detect": True,
                        "ports": ["80", "443", "8080", "8443", "3000", "5000"]
                    },
                    "naabu": {
                        "top_ports": "1000",
                        "rate": 1000,
                        "threads": 25
                    },
                    "waybackurls": {
                        "get_versions": True,
                        "limit": 2000
                    },
                    "katana": {
                        "depth": 3,
                        "js_crawl": True,
                        "crawl_duration": 5
                    }
                }
            },
            "stealth_scan": {
                "description": "Low-profile reconnaissance to avoid detection",
                "tools": ["subfinder", "waybackurls"],
                "configs": {
                    "subfinder": {
                        "max_time": 5,
                        "threads": 3,
                        "sources": ["dnsdumpster", "hackertarget"]
                    },
                    "waybackurls": {
                        "limit": 500
                    }
                }
            },
            "active_scan": {
                "description": "Active reconnaissance with brute force",
                "tools": ["subfinder", "amass", "httpx", "nmap"],
                "configs": {
                    "subfinder": {
                        "max_time": 15,
                        "threads": 30,
                        "recursive": True
                    },
                    "amass": {
                        "mode": "active",
                        "timeout": 30,
                        "brute_force": True,
                        "alterations": True
                    },
                    "httpx": {
                        "threads": 150,
                        "tech_detect": True,
                        "follow_redirects": True,
                        "ports": ["80", "443", "8080", "8443", "3000", "5000", "8000", "9000"]
                    },
                    "nmap": {
                        "scan_type": "syn",
                        "top_ports": 1000,
                        "timing": "4",
                        "version_detection": True
                    }
                }
            },
            "content_discovery": {
                "description": "Content and directory discovery scan",
                "tools": ["gobuster", "ffuf", "katana", "paramspider"],
                "configs": {
                    "gobuster": {
                        "mode": "dir",
                        "threads": 20,
                        "extensions": ["php", "html", "js", "txt", "xml", "asp", "aspx"]
                    },
                    "ffuf": {
                        "threads": 40,
                        "extensions": ["php", "html", "js", "txt"]
                    },
                    "katana": {
                        "depth": 4,
                        "js_crawl": True,
                        "crawl_duration": 10
                    },
                    "paramspider": {
                        "level": "high",
                        "subs": True
                    }
                }
            },
            "screenshot_scan": {
                "description": "Visual reconnaissance with screenshots",
                "tools": ["httpx", "gowitness"],
                "configs": {
                    "httpx": {
                        "threads": 50,
                        "tech_detect": True,
                        "title": True,
                        "ports": ["80", "443", "8080", "8443"]
                    },
                    "gowitness": {
                        "threads": 10,
                        "timeout": 15,
                        "resolution": "1920,1080",
                        "fullpage": True
                    }
                }
            }
        }
    }

@router.post("/preset-scan/{preset_name}")
async def execute_preset_scan(preset_name: str, target: str, session_id: str = None):
    """Execute a scan using a predefined preset"""
    try:
        presets_response = await get_tool_presets()
        presets = presets_response["presets"]
        
        if preset_name not in presets:
            raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")
        
        preset = presets[preset_name]
        
        # Create custom scan request
        custom_request = CustomScanRequest(
            target=target,
            tools=preset["tools"],
            tool_configs=preset["configs"],
            session_id=session_id
        )
        
        return await execute_custom_scan(custom_request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preset scan failed: {str(e)}")

@router.get("/status")
async def get_tools_status():
    """Get real-time status of all reconnaissance tools"""
    try:
        status = {}
        
        for tool_name in [
            "subfinder", "assetfinder", "dnsx", "httpx", "amass",
            "nmap", "naabu", "gowitness", "eyewitness", "gobuster",
            "ffuf", "katana", "waybackurls", "waymore", "paramspider"
        ]:
            capabilities = await orchestrator.get_tool_capabilities(tool_name)
            if capabilities:
                status[tool_name] = {
                    "available": capabilities["available"],
                    "version": capabilities["version"],
                    "path": capabilities.get("path", "unknown")
                }
            else:
                status[tool_name] = {
                    "available": False,
                    "version": "unknown",
                    "path": "not found"
                }
        
        return {"tools_status": status}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tools status: {str(e)}")

@router.get("/examples")
async def get_configuration_examples():
    """Get example configurations for each tool"""
    return {
        "examples": {
            "subfinder": {
                "basic": {
                    "max_time": 5,
                    "threads": 10
                },
                "advanced": {
                    "max_time": 15,
                    "threads": 25,
                    "sources": ["shodan", "censys", "fofa"],
                    "recursive": True,
                    "output_format": "json"
                },
                "custom_wordlist": {
                    "max_time": 20,
                    "threads": 15,
                    "wordlist": "/path/to/custom/wordlist.txt",
                    "recursive": True
                }
            },
            "amass": {
                "passive_only": {
                    "mode": "passive",
                    "timeout": 10,
                    "max_dns_queries": 500
                },
                "active_with_brute": {
                    "mode": "active",
                    "timeout": 30,
                    "brute_force": True,
                    "alterations": True,
                    "wordlist": "/path/to/wordlist.txt"
                },
                "intel_gathering": {
                    "mode": "intel",
                    "timeout": 15
                }
            },
            "waybackurls": {
                "basic": {
                    "limit": 1000
                },
                "detailed": {
                    "get_versions": True,
                    "dates": True,
                    "limit": 5000
                },
                "domain_only": {
                    "no_subs": True,
                    "limit": 500
                }
            },
            "httpx": {
                "fast_probe": {
                    "threads": 100,
                    "timeout": 5,
                    "ports": ["80", "443"]
                },
                "comprehensive": {
                    "threads": 50,
                    "timeout": 15,
                    "tech_detect": True,
                    "title": True,
                    "content_length": True,
                    "ports": ["80", "443", "8080", "8443", "3000", "5000", "8000", "9000"]
                },
                "custom_method": {
                    "method": "HEAD",
                    "threads": 75,
                    "follow_redirects": False
                }
            }
        }
    }