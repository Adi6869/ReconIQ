import asyncio
import subprocess
import json
import os
import tempfile
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from ..schemas.scan import Finding, FindingType, ToolExecution, ExecutionStatus
from ..config import settings

class EnhancedToolOrchestrator:
    def __init__(self):
        self.available_tools = {
            # Recon Tools
            "subfinder": EnhancedSubfinderPlugin(),
            "assetfinder": EnhancedAssetfinderPlugin(),
            "dnsx": EnhancedDnsxPlugin(),
            "httpx": EnhancedHttpxPlugin(),
            "amass": EnhancedAmassPlugin(),
            
            # Port Scan Tools
            "nmap": EnhancedNmapPlugin(),
            "naabu": EnhancedNaabuPlugin(),
            
            # Screenshot Tools
            "gowitness": EnhancedGoWitnessPlugin(),
            "eyewitness": EnhancedEyeWitnessPlugin(),
            
            # Content Discovery
            "gobuster": EnhancedGobusterPlugin(),
            
            # Fuzzing & Endpoint Tools
            "ffuf": EnhancedFfufPlugin(),
            "katana": EnhancedKatanaPlugin(),
            "waybackurls": EnhancedWaybackurlsPlugin(),
            "waymore": EnhancedWaymorePlugin(),
            
            # Parameter Discovery
            "paramspider": EnhancedParamSpiderPlugin()
        }
        self.tool_configs = {}
    
    async def execute_workflow(self, parsed_intent: Dict[str, Any], user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute reconnaissance workflow with user customization"""
        targets = parsed_intent.get("targets", [])
        tools = parsed_intent.get("tools", [])
        custom_params = user_config or {}
        
        if not targets:
            return {"error": "No targets specified", "findings": []}
        
        results = {
            "targets": targets,
            "tools_executed": [],
            "findings": [],
            "execution_summary": {},
            "start_time": datetime.now().isoformat(),
            "user_config": custom_params
        }
        
        # Execute tools for each target
        for target in targets:
            for tool_name in tools:
                if tool_name in self.available_tools:
                    try:
                        tool = self.available_tools[tool_name]
                        
                        # Apply user-specific configuration
                        tool_config = custom_params.get(tool_name, {})
                        
                        print(f"🔧 Executing {tool_name} on {target} with config: {tool_config}")
                        tool_results = await tool.execute(target, tool_config)
                        
                        results["tools_executed"].append(tool_name)
                        results["findings"].extend(tool_results.get("findings", []))
                        results["execution_summary"][f"{tool_name}_{target}"] = {
                            "status": "completed",
                            "findings_count": len(tool_results.get("findings", [])),
                            "execution_time": tool_results.get("execution_time", 0),
                            "config_used": tool_config
                        }
                        
                    except Exception as e:
                        print(f"❌ Error executing {tool_name}: {e}")
                        results["execution_summary"][f"{tool_name}_{target}"] = {
                            "status": "failed",
                            "error": str(e),
                            "findings_count": 0
                        }
        
        results["end_time"] = datetime.now().isoformat()
        results["total_findings"] = len(results["findings"])
        
        return results
    
    async def get_tool_capabilities(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed capabilities and configuration options for a tool"""
        if tool_name in self.available_tools:
            return await self.available_tools[tool_name].get_capabilities()
        return {}
    
    async def validate_tool_config(self, tool_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user configuration for a specific tool"""
        if tool_name in self.available_tools:
            return await self.available_tools[tool_name].validate_config(config)
        return {"valid": False, "errors": ["Tool not found"]}

class EnhancedBaseToolPlugin:
    """Enhanced base class for reconnaissance tool plugins with full customization"""
    
    def __init__(self, tool_name: str, tool_path: str):
        self.tool_name = tool_name
        self.tool_path = tool_path
        self.default_config = {}
        self.supported_options = {}
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the tool with user customization"""
        raise NotImplementedError
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Get tool capabilities and configuration options"""
        return {
            "name": self.tool_name,
            "path": self.tool_path,
            "available": await self._check_tool_availability(),
            "version": await self._get_tool_version(),
            "supported_options": self.supported_options,
            "default_config": self.default_config,
            "description": self._get_description()
        }
    
    async def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user configuration"""
        errors = []
        warnings = []
        
        for key, value in config.items():
            if key not in self.supported_options:
                warnings.append(f"Unknown option: {key}")
            else:
                option_info = self.supported_options[key]
                if not self._validate_option_value(key, value, option_info):
                    errors.append(f"Invalid value for {key}: {value}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _validate_option_value(self, key: str, value: Any, option_info: Dict[str, Any]) -> bool:
        """Validate a specific option value"""
        expected_type = option_info.get("type", "string")
        
        if expected_type == "integer" and not isinstance(value, int):
            return False
        elif expected_type == "boolean" and not isinstance(value, bool):
            return False
        elif expected_type == "list" and not isinstance(value, list):
            return False
        elif expected_type == "string" and not isinstance(value, str):
            return False
        
        # Check allowed values
        allowed_values = option_info.get("allowed_values")
        if allowed_values and value not in allowed_values:
            return False
        
        # Check ranges for integers
        if expected_type == "integer":
            min_val = option_info.get("min")
            max_val = option_info.get("max")
            if min_val is not None and value < min_val:
                return False
            if max_val is not None and value > max_val:
                return False
        
        return True
    
    async def _check_tool_availability(self) -> bool:
        """Check if the tool is available on the system"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.tool_path, "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(process.communicate(), timeout=5)
            return process.returncode == 0
        except:
            return False
    
    async def _get_tool_version(self) -> str:
        """Get tool version"""
        try:
            process = await asyncio.create_subprocess_exec(
                self.tool_path, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=5)
            version_output = stdout.decode('utf-8', errors='ignore') + stderr.decode('utf-8', errors='ignore')
            return version_output.strip().split('\n')[0] if version_output else "Unknown"
        except:
            return "Unknown"
    
    def _get_description(self) -> str:
        """Get tool description"""
        return f"{self.tool_name} reconnaissance tool"
    
    async def _run_command(self, command: List[str], timeout: int = None, input_data: str = None) -> Dict[str, Any]:
        """Run a command with enhanced options"""
        timeout = timeout or settings.default_timeout
        start_time = datetime.now()
        
        try:
            print(f"🚀 Running command: {' '.join(command)}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if input_data else None
            )
            
            if input_data:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=input_data.encode()), 
                    timeout=timeout
                )
            else:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": process.returncode == 0,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "returncode": process.returncode,
                "execution_time": execution_time,
                "command": ' '.join(command)
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "returncode": -1,
                "execution_time": timeout,
                "command": ' '.join(command)
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "command": ' '.join(command)
            }

class EnhancedSubfinderPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("subfinder", settings.subfinder_path)
        self.supported_options = {
            "sources": {
                "type": "list",
                "description": "Specific sources to use for enumeration",
                "allowed_values": ["shodan", "censys", "fofa", "spyse", "recon", "dnsdumpster", "hackertarget"],
                "default": []
            },
            "exclude_sources": {
                "type": "list", 
                "description": "Sources to exclude from enumeration",
                "default": []
            },
            "max_time": {
                "type": "integer",
                "description": "Maximum time in minutes for enumeration",
                "min": 1,
                "max": 60,
                "default": 10
            },
            "threads": {
                "type": "integer",
                "description": "Number of concurrent threads",
                "min": 1,
                "max": 100,
                "default": 10
            },
            "recursive": {
                "type": "boolean",
                "description": "Enable recursive subdomain enumeration",
                "default": False
            },
            "wordlist": {
                "type": "string",
                "description": "Path to custom wordlist file",
                "default": ""
            },
            "output_format": {
                "type": "string",
                "description": "Output format",
                "allowed_values": ["txt", "json"],
                "default": "txt"
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Fast passive subdomain discovery tool with multiple data sources"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute subfinder with advanced configuration"""
        config = {**self.default_config, **(user_config or {})}
        
        command = [self.tool_path, "-d", target, "-silent"]
        
        # Add sources
        if config.get("sources"):
            command.extend(["-sources", ",".join(config["sources"])])
        
        # Add excluded sources
        if config.get("exclude_sources"):
            command.extend(["-exclude-sources", ",".join(config["exclude_sources"])])
        
        # Add max time
        if config.get("max_time"):
            command.extend(["-timeout", str(config["max_time"])])
        
        # Add threads
        if config.get("threads"):
            command.extend(["-t", str(config["threads"])])
        
        # Add recursive
        if config.get("recursive"):
            command.append("-recursive")
        
        # Add wordlist
        if config.get("wordlist") and os.path.exists(config["wordlist"]):
            command.extend(["-w", config["wordlist"]])
        
        # Add output format
        if config.get("output_format") == "json":
            command.append("-json")
        
        result = await self._run_command(command, timeout=config.get("max_time", 10) * 60)
        findings = []
        
        if result["success"] and result["stdout"]:
            if config.get("output_format") == "json":
                # Parse JSON output
                for line in result["stdout"].strip().split('\n'):
                    try:
                        data = json.loads(line)
                        subdomain = data.get("host", "")
                        if subdomain and subdomain != target:
                            findings.append({
                                "type": FindingType.SUBDOMAIN.value,
                                "value": subdomain,
                                "source": "subfinder",
                                "confidence": 0.9,
                                "metadata": {
                                    "target": target,
                                    "source_name": data.get("source", "unknown"),
                                    "config": config
                                }
                            })
                    except json.JSONDecodeError:
                        continue
            else:
                # Parse text output
                subdomains = result["stdout"].strip().split('\n')
                for subdomain in subdomains:
                    subdomain = subdomain.strip()
                    if subdomain and subdomain != target:
                        findings.append({
                            "type": FindingType.SUBDOMAIN.value,
                            "value": subdomain,
                            "source": "subfinder",
                            "confidence": 0.9,
                            "metadata": {"target": target, "config": config}
                        })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

class EnhancedAmassPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("amass", settings.amass_path)
        self.supported_options = {
            "mode": {
                "type": "string",
                "description": "Enumeration mode",
                "allowed_values": ["passive", "active", "intel"],
                "default": "passive"
            },
            "sources": {
                "type": "list",
                "description": "Specific data sources to use",
                "default": []
            },
            "exclude_sources": {
                "type": "list",
                "description": "Data sources to exclude",
                "default": []
            },
            "max_dns_queries": {
                "type": "integer",
                "description": "Maximum DNS queries per minute",
                "min": 100,
                "max": 10000,
                "default": 1000
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in minutes",
                "min": 1,
                "max": 120,
                "default": 30
            },
            "wordlist": {
                "type": "string",
                "description": "Path to custom wordlist",
                "default": ""
            },
            "brute_force": {
                "type": "boolean",
                "description": "Enable brute force enumeration",
                "default": False
            },
            "alterations": {
                "type": "boolean",
                "description": "Enable subdomain alterations",
                "default": False
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "In-depth DNS enumeration and network mapping with multiple modes"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute amass with advanced configuration"""
        config = {**self.default_config, **(user_config or {})}
        
        mode = config.get("mode", "passive")
        
        if mode == "intel":
            command = [self.tool_path, "intel", "-d", target]
        else:
            command = [self.tool_path, "enum", "-d", target]
            
            if mode == "passive":
                command.append("-passive")
        
        # Add sources
        if config.get("sources"):
            command.extend(["-src", ",".join(config["sources"])])
        
        # Add excluded sources  
        if config.get("exclude_sources"):
            command.extend(["-exclude", ",".join(config["exclude_sources"])])
        
        # Add DNS query limit
        if config.get("max_dns_queries"):
            command.extend(["-max-dns-queries", str(config["max_dns_queries"])])
        
        # Add wordlist for brute force
        if config.get("brute_force") and config.get("wordlist") and os.path.exists(config["wordlist"]):
            command.extend(["-brute", "-w", config["wordlist"]])
        
        # Add alterations
        if config.get("alterations"):
            command.append("-alts")
        
        # Always use silent mode for API
        command.append("-silent")
        
        timeout_minutes = config.get("timeout", 30)
        result = await self._run_command(command, timeout=timeout_minutes * 60)
        findings = []
        
        if result["success"] and result["stdout"]:
            subdomains = result["stdout"].strip().split('\n')
            for subdomain in subdomains:
                subdomain = subdomain.strip()
                if subdomain and subdomain != target:
                    findings.append({
                        "type": FindingType.SUBDOMAIN.value,
                        "value": subdomain,
                        "source": "amass",
                        "confidence": 0.95,
                        "metadata": {
                            "target": target,
                            "mode": mode,
                            "config": config
                        }
                    })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

class EnhancedWaybackurlsPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("waybackurls", settings.waybackurls_path)
        self.supported_options = {
            "get_versions": {
                "type": "boolean",
                "description": "Get all versions of URLs",
                "default": False
            },
            "no_subs": {
                "type": "boolean", 
                "description": "Don't include subdomains",
                "default": False
            },
            "dates": {
                "type": "boolean",
                "description": "Show dates in output",
                "default": False
            },
            "limit": {
                "type": "integer",
                "description": "Limit number of URLs returned",
                "min": 1,
                "max": 10000,
                "default": 1000
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Fetch URLs from Wayback Machine archives with filtering options"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute waybackurls with configuration"""
        config = {**self.default_config, **(user_config or {})}
        
        command = [self.tool_path]
        
        # Add options
        if config.get("get_versions"):
            command.append("-get-versions")
        
        if config.get("no_subs"):
            command.append("-no-subs")
        
        if config.get("dates"):
            command.append("-dates")
        
        # Use stdin for target
        result = await self._run_command(command, input_data=target)
        findings = []
        
        if result["success"] and result["stdout"]:
            urls = result["stdout"].strip().split('\n')
            limit = config.get("limit", 1000)
            
            for url in urls[:limit]:
                url = url.strip()
                if url and url.startswith(('http://', 'https://')):
                    # Parse date if available
                    date_info = None
                    if config.get("dates") and " " in url:
                        parts = url.split(" ", 1)
                        if len(parts) == 2:
                            date_info = parts[0]
                            url = parts[1]
                    
                    findings.append({
                        "type": FindingType.HISTORICAL_URL.value,
                        "value": url,
                        "source": "waybackurls",
                        "confidence": 0.8,
                        "metadata": {
                            "target": target,
                            "date": date_info,
                            "config": config
                        }
                    })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

class EnhancedHttpxPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("httpx", settings.httpx_path)
        self.supported_options = {
            "threads": {
                "type": "integer",
                "description": "Number of threads",
                "min": 1,
                "max": 300,
                "default": 50
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "min": 1,
                "max": 300,
                "default": 10
            },
            "retries": {
                "type": "integer",
                "description": "Number of retries",
                "min": 0,
                "max": 10,
                "default": 1
            },
            "status_code": {
                "type": "boolean",
                "description": "Display status code",
                "default": True
            },
            "title": {
                "type": "boolean",
                "description": "Display page title",
                "default": True
            },
            "content_length": {
                "type": "boolean",
                "description": "Display content length",
                "default": True
            },
            "tech_detect": {
                "type": "boolean",
                "description": "Display technology stack",
                "default": True
            },
            "follow_redirects": {
                "type": "boolean",
                "description": "Follow HTTP redirects",
                "default": True
            },
            "method": {
                "type": "string",
                "description": "HTTP method to use",
                "allowed_values": ["GET", "POST", "HEAD"],
                "default": "GET"
            },
            "ports": {
                "type": "list",
                "description": "Ports to probe",
                "default": ["80", "443", "8080", "8443"]
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Fast HTTP probe with technology detection and customizable options"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute httpx with advanced configuration"""
        config = {**self.default_config, **(user_config or {})}
        
        command = [self.tool_path, "-u", target, "-silent", "-json"]
        
        # Add threads
        if config.get("threads"):
            command.extend(["-threads", str(config["threads"])])
        
        # Add timeout
        if config.get("timeout"):
            command.extend(["-timeout", str(config["timeout"])])
        
        # Add retries
        if config.get("retries"):
            command.extend(["-retries", str(config["retries"])])
        
        # Add status code
        if config.get("status_code"):
            command.append("-status-code")
        
        # Add title
        if config.get("title"):
            command.append("-title")
        
        # Add content length
        if config.get("content_length"):
            command.append("-content-length")
        
        # Add tech detection
        if config.get("tech_detect"):
            command.append("-tech-detect")
        
        # Add follow redirects
        if config.get("follow_redirects"):
            command.append("-follow-redirects")
        
        # Add method
        if config.get("method") and config["method"] != "GET":
            command.extend(["-method", config["method"]])
        
        # Add ports
        if config.get("ports"):
            command.extend(["-ports", ",".join(map(str, config["ports"]))])
        
        result = await self._run_command(command, timeout=config.get("timeout", 10) * 2)
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get("url"):
                        findings.append({
                            "type": FindingType.HTTP_SERVICE.value,
                            "value": data["url"],
                            "source": "httpx",
                            "confidence": 0.9,
                            "metadata": {
                                "status_code": data.get("status_code"),
                                "content_length": data.get("content_length"),
                                "technology": data.get("tech", []),
                                "title": data.get("title"),
                                "method": data.get("method"),
                                "config": config
                            }
                        })
                except json.JSONDecodeError:
                    continue
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

# ============================================================================
# NEW TOOL PLUGINS - RECON TOOLS
# ============================================================================

class EnhancedAssetfinderPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("assetfinder", settings.assetfinder_path)
        self.supported_options = {
            "subs_only": {
                "type": "boolean",
                "description": "Find only subdomains",
                "default": True
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "min": 10,
                "max": 300,
                "default": 60
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Fast subdomain discovery tool using various techniques"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        command = [self.tool_path]
        
        if config.get("subs_only"):
            command.append("--subs-only")
        
        command.append(target)
        
        result = await self._run_command(command, timeout=config.get("timeout", 60))
        findings = []
        
        if result["success"] and result["stdout"]:
            subdomains = result["stdout"].strip().split('\n')
            for subdomain in subdomains:
                subdomain = subdomain.strip()
                if subdomain and subdomain != target:
                    findings.append({
                        "type": FindingType.SUBDOMAIN.value,
                        "value": subdomain,
                        "source": "assetfinder",
                        "confidence": 0.85,
                        "metadata": {"target": target, "config": config}
                    })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

class EnhancedDnsxPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("dnsx", settings.dnsx_path)
        self.supported_options = {
            "a": {
                "type": "boolean",
                "description": "Query A records",
                "default": True
            },
            "aaaa": {
                "type": "boolean",
                "description": "Query AAAA records",
                "default": False
            },
            "cname": {
                "type": "boolean",
                "description": "Query CNAME records",
                "default": True
            },
            "mx": {
                "type": "boolean",
                "description": "Query MX records",
                "default": False
            },
            "ns": {
                "type": "boolean",
                "description": "Query NS records",
                "default": False
            },
            "txt": {
                "type": "boolean",
                "description": "Query TXT records",
                "default": False
            },
            "ptr": {
                "type": "boolean",
                "description": "Query PTR records",
                "default": False
            },
            "srv": {
                "type": "boolean",
                "description": "Query SRV records",
                "default": False
            },
            "threads": {
                "type": "integer",
                "description": "Number of threads",
                "min": 1,
                "max": 100,
                "default": 25
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "min": 1,
                "max": 60,
                "default": 10
            },
            "retries": {
                "type": "integer",
                "description": "Number of retries",
                "min": 0,
                "max": 10,
                "default": 2
            },
            "resolver": {
                "type": "string",
                "description": "Custom DNS resolver",
                "default": ""
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Fast and multi-purpose DNS toolkit for DNS resolution and enumeration"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        command = [self.tool_path, "-silent", "-json"]
        
        # Add record types
        record_types = []
        if config.get("a"): record_types.append("a")
        if config.get("aaaa"): record_types.append("aaaa")
        if config.get("cname"): record_types.append("cname")
        if config.get("mx"): record_types.append("mx")
        if config.get("ns"): record_types.append("ns")
        if config.get("txt"): record_types.append("txt")
        if config.get("ptr"): record_types.append("ptr")
        if config.get("srv"): record_types.append("srv")
        
        if record_types:
            command.extend(["-" + ",".join(record_types)])
        
        # Add threads
        if config.get("threads"):
            command.extend(["-t", str(config["threads"])])
        
        # Add timeout
        if config.get("timeout"):
            command.extend(["-timeout", str(config["timeout"])])
        
        # Add retries
        if config.get("retries"):
            command.extend(["-retry", str(config["retries"])])
        
        # Add resolver
        if config.get("resolver"):
            command.extend(["-r", config["resolver"]])
        
        # Use stdin for target
        result = await self._run_command(command, input_data=target, timeout=config.get("timeout", 10) * 2)
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get("host") and data.get("a"):
                        findings.append({
                            "type": FindingType.DNS_RECORD.value,
                            "value": f"{data['host']} -> {', '.join(data['a'])}",
                            "source": "dnsx",
                            "confidence": 0.95,
                            "metadata": {
                                "host": data["host"],
                                "records": data,
                                "config": config
                            }
                        })
                except json.JSONDecodeError:
                    continue
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

# ============================================================================
# PORT SCAN TOOLS
# ============================================================================

class EnhancedNmapPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("nmap", settings.nmap_path)
        self.supported_options = {
            "scan_type": {
                "type": "string",
                "description": "Type of scan to perform",
                "allowed_values": ["syn", "tcp", "udp", "ping", "version", "os"],
                "default": "syn"
            },
            "ports": {
                "type": "string",
                "description": "Ports to scan (e.g., '80,443,1000-2000')",
                "default": "21,22,23,25,53,80,110,111,135,139,143,443,993,995,1723,3306,3389,5432,5900,8080"
            },
            "top_ports": {
                "type": "integer",
                "description": "Scan top N ports",
                "min": 10,
                "max": 65535,
                "default": 100
            },
            "timing": {
                "type": "string",
                "description": "Timing template",
                "allowed_values": ["0", "1", "2", "3", "4", "5"],
                "default": "3"
            },
            "threads": {
                "type": "integer",
                "description": "Parallel host scan groups",
                "min": 1,
                "max": 100,
                "default": 10
            },
            "version_detection": {
                "type": "boolean",
                "description": "Enable version detection",
                "default": True
            },
            "os_detection": {
                "type": "boolean",
                "description": "Enable OS detection",
                "default": False
            },
            "script_scan": {
                "type": "boolean",
                "description": "Enable default script scan",
                "default": False
            },
            "aggressive": {
                "type": "boolean",
                "description": "Enable aggressive scan",
                "default": False
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Network exploration and security auditing tool"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        # Use normal output format instead of XML for better parsing
        command = [self.tool_path, target]
        
        # Add scan type
        scan_type = config.get("scan_type", "syn")
        if scan_type == "syn":
            command.append("-sS")
        elif scan_type == "tcp":
            command.append("-sT")
        elif scan_type == "udp":
            command.append("-sU")
        elif scan_type == "ping":
            command.append("-sn")
        
        # Add ports - use more common ports by default
        if config.get("top_ports"):
            command.extend(["--top-ports", str(config["top_ports"])])
        elif config.get("ports"):
            command.extend(["-p", config["ports"]])
        else:
            # Default to common ports for better results
            command.extend(["-p", "21,22,23,25,53,80,110,111,135,139,143,443,993,995,1723,3306,3389,5432,5900,8080"])
        
        # Add timing
        if config.get("timing"):
            command.extend([f"-T{config['timing']}"])
        
        # Add version detection by default for better results
        if config.get("version_detection") or scan_type != "ping":
            command.append("-sV")
        
        # Add OS detection
        if config.get("os_detection"):
            command.append("-O")
        
        # Add script scan
        if config.get("script_scan"):
            command.append("-sC")
        
        # Add aggressive
        if config.get("aggressive"):
            command.append("-A")
        
        # Skip host discovery for better results
        command.append("-Pn")
        
        # Add verbose output
        command.append("-v")
        
        result = await self._run_command(command, timeout=300)  # 5 minute timeout
        findings = []
        
        if result["success"] and result["stdout"]:
            # Parse nmap output - look for open ports
            lines = result["stdout"].split('\n')
            
            for line in lines:
                line = line.strip()
                # Look for lines like "22/tcp   open  ssh"
                if '/tcp' in line and 'open' in line:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] == 'open':
                        port_info = parts[0]  # e.g., "22/tcp"
                        service = parts[2] if len(parts) > 2 else "unknown"
                        
                        port_num = port_info.split('/')[0]
                        protocol = port_info.split('/')[1] if '/' in port_info else "tcp"
                        
                        findings.append({
                            "type": FindingType.OPEN_PORT.value,
                            "value": f"{target}:{port_num}/{protocol}",
                            "source": "nmap",
                            "confidence": 0.95,
                            "metadata": {
                                "host": target,
                                "port": port_num,
                                "protocol": protocol,
                                "service": service,
                                "state": "open",
                                "config": config
                            }
                        })
                
                # Also look for UDP ports
                elif '/udp' in line and 'open' in line:
                    parts = line.split()
                    if len(parts) >= 3 and parts[1] == 'open':
                        port_info = parts[0]
                        service = parts[2] if len(parts) > 2 else "unknown"
                        
                        port_num = port_info.split('/')[0]
                        
                        findings.append({
                            "type": FindingType.OPEN_PORT.value,
                            "value": f"{target}:{port_num}/udp",
                            "source": "nmap",
                            "confidence": 0.95,
                            "metadata": {
                                "host": target,
                                "port": port_num,
                                "protocol": "udp",
                                "service": service,
                                "state": "open",
                                "config": config
                            }
                        })
        
        # If no findings but scan was successful, add informational message
        if result["success"] and len(findings) == 0:
            findings.append({
                "type": FindingType.OPEN_PORT.value,
                "value": f"No open ports found on {target}",
                "source": "nmap",
                "confidence": 0.8,
                "metadata": {
                    "host": target,
                    "message": "Scan completed but no open ports detected",
                    "config": config,
                    "suggestion": "Try scanning more ports or check if host is reachable"
                }
            })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

class EnhancedNaabuPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("naabu", settings.naabu_path)
        self.supported_options = {
            "ports": {
                "type": "string",
                "description": "Ports to scan",
                "default": "1-1000"
            },
            "top_ports": {
                "type": "string",
                "description": "Top ports to scan",
                "allowed_values": ["100", "1000", "full"],
                "default": "1000"
            },
            "rate": {
                "type": "integer",
                "description": "Rate of packets per second",
                "min": 100,
                "max": 50000,
                "default": 1000
            },
            "threads": {
                "type": "integer",
                "description": "Number of threads",
                "min": 1,
                "max": 100,
                "default": 25
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in milliseconds",
                "min": 100,
                "max": 10000,
                "default": 1000
            },
            "retries": {
                "type": "integer",
                "description": "Number of retries",
                "min": 0,
                "max": 10,
                "default": 3
            },
            "scan_type": {
                "type": "string",
                "description": "Scan type",
                "allowed_values": ["s", "c"],
                "default": "s"
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Fast port scanner written in Go with focus on reliability and simplicity"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        command = [self.tool_path, "-host", target, "-silent", "-json"]
        
        # Add ports
        if config.get("top_ports") and config["top_ports"] != "full":
            command.extend(["-top-ports", config["top_ports"]])
        elif config.get("ports"):
            command.extend(["-p", config["ports"]])
        
        # Add rate
        if config.get("rate"):
            command.extend(["-rate", str(config["rate"])])
        
        # Add threads
        if config.get("threads"):
            command.extend(["-c", str(config["threads"])])
        
        # Add timeout
        if config.get("timeout"):
            command.extend(["-timeout", str(config["timeout"])])
        
        # Add retries
        if config.get("retries"):
            command.extend(["-retries", str(config["retries"])])
        
        # Add scan type
        if config.get("scan_type"):
            command.extend(["-s", config["scan_type"]])
        
        result = await self._run_command(command, timeout=120)
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get("port") and data.get("host"):
                        findings.append({
                            "type": FindingType.OPEN_PORT.value,
                            "value": f"{data['host']}:{data['port']}",
                            "source": "naabu",
                            "confidence": 0.9,
                            "metadata": {
                                "host": data["host"],
                                "port": data["port"],
                                "config": config
                            }
                        })
                except json.JSONDecodeError:
                    continue
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

# ============================================================================
# SCREENSHOT TOOLS
# ============================================================================

class EnhancedGoWitnessPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("gowitness", settings.gowitness_path)
        self.supported_options = {
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "min": 5,
                "max": 120,
                "default": 10
            },
            "threads": {
                "type": "integer",
                "description": "Number of threads",
                "min": 1,
                "max": 50,
                "default": 5
            },
            "resolution": {
                "type": "string",
                "description": "Screenshot resolution",
                "allowed_values": ["1440,900", "1920,1080", "1366,768"],
                "default": "1440,900"
            },
            "fullpage": {
                "type": "boolean",
                "description": "Take full page screenshot",
                "default": False
            },
            "delay": {
                "type": "integer",
                "description": "Delay before screenshot in seconds",
                "min": 0,
                "max": 30,
                "default": 3
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Web screenshot utility using Chrome Headless"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        # Create temporary directory for screenshots
        with tempfile.TemporaryDirectory() as temp_dir:
            command = [
                self.tool_path, "single", 
                "--url", target,
                "--screenshot-path", temp_dir,
                "--disable-logging"
            ]
            
            # Add timeout
            if config.get("timeout"):
                command.extend(["--timeout", str(config["timeout"])])
            
            # Add resolution
            if config.get("resolution"):
                command.extend(["--resolution", config["resolution"]])
            
            # Add fullpage
            if config.get("fullpage"):
                command.append("--fullpage")
            
            # Add delay
            if config.get("delay"):
                command.extend(["--delay", str(config["delay"])])
            
            result = await self._run_command(command, timeout=config.get("timeout", 10) + 30)
            findings = []
            
            if result["success"]:
                # Check if screenshot was created
                screenshot_files = list(Path(temp_dir).glob("*.png"))
                if screenshot_files:
                    findings.append({
                        "type": FindingType.SCREENSHOT.value,
                        "value": f"Screenshot captured for {target}",
                        "source": "gowitness",
                        "confidence": 0.9,
                        "metadata": {
                            "target": target,
                            "screenshot_path": str(screenshot_files[0]),
                            "config": config
                        }
                    })
            
            return {
                "findings": findings,
                "execution_time": result["execution_time"],
                "success": result["success"],
                "errors": [result["stderr"]] if result["stderr"] else [],
                "command_executed": result["command"],
                "config_used": config
            }

class EnhancedEyeWitnessPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("eyewitness", settings.eyewitness_path)
        self.supported_options = {
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "min": 5,
                "max": 120,
                "default": 7
            },
            "threads": {
                "type": "integer",
                "description": "Number of threads",
                "min": 1,
                "max": 25,
                "default": 5
            },
            "delay": {
                "type": "integer",
                "description": "Delay between requests in seconds",
                "min": 0,
                "max": 10,
                "default": 1
            },
            "user_agent": {
                "type": "string",
                "description": "Custom user agent",
                "default": ""
            },
            "resolution": {
                "type": "string",
                "description": "Screenshot resolution",
                "allowed_values": ["1440x900", "1920x1080", "1366x768"],
                "default": "1440x900"
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Web application screenshot tool with report generation"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            command = [
                "python3", self.tool_path,
                "--single", target,
                "-d", temp_dir,
                "--no-prompt"
            ]
            
            # Add timeout
            if config.get("timeout"):
                command.extend(["--timeout", str(config["timeout"])])
            
            # Add threads
            if config.get("threads"):
                command.extend(["--threads", str(config["threads"])])
            
            # Add delay
            if config.get("delay"):
                command.extend(["--delay", str(config["delay"])])
            
            # Add user agent
            if config.get("user_agent"):
                command.extend(["--user-agent", config["user_agent"]])
            
            # Add resolution
            if config.get("resolution"):
                command.extend(["--resolution", config["resolution"]])
            
            result = await self._run_command(command, timeout=config.get("timeout", 7) + 60)
            findings = []
            
            if result["success"]:
                # Check if screenshots were created
                screenshot_dir = Path(temp_dir) / "screens"
                if screenshot_dir.exists():
                    screenshot_files = list(screenshot_dir.glob("*.png"))
                    if screenshot_files:
                        findings.append({
                            "type": FindingType.SCREENSHOT.value,
                            "value": f"Screenshot captured for {target}",
                            "source": "eyewitness",
                            "confidence": 0.9,
                            "metadata": {
                                "target": target,
                                "screenshot_count": len(screenshot_files),
                                "config": config
                            }
                        })
            
            return {
                "findings": findings,
                "execution_time": result["execution_time"],
                "success": result["success"],
                "errors": [result["stderr"]] if result["stderr"] else [],
                "command_executed": result["command"],
                "config_used": config
            }

# ============================================================================
# CONTENT DISCOVERY TOOLS
# ============================================================================

class EnhancedGobusterPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("gobuster", settings.gobuster_path)
        self.supported_options = {
            "mode": {
                "type": "string",
                "description": "Gobuster mode",
                "allowed_values": ["dir", "dns", "vhost"],
                "default": "dir"
            },
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist file",
                "default": "/usr/share/wordlists/dirb/common.txt"
            },
            "threads": {
                "type": "integer",
                "description": "Number of threads",
                "min": 1,
                "max": 100,
                "default": 10
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "min": 1,
                "max": 60,
                "default": 10
            },
            "extensions": {
                "type": "list",
                "description": "File extensions to search for",
                "default": ["php", "html", "js", "txt", "xml"]
            },
            "status_codes": {
                "type": "list",
                "description": "Status codes to include",
                "default": ["200", "204", "301", "302", "307", "401", "403"]
            },
            "follow_redirects": {
                "type": "boolean",
                "description": "Follow redirects",
                "default": False
            },
            "include_length": {
                "type": "boolean",
                "description": "Include response length",
                "default": True
            },
            "user_agent": {
                "type": "string",
                "description": "Custom user agent",
                "default": ""
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Directory/file & DNS busting tool written in Go"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        mode = config.get("mode", "dir")
        command = [self.tool_path, mode, "-q"]
        
        if mode == "dir":
            command.extend(["-u", target])
        elif mode == "dns":
            command.extend(["-d", target])
        elif mode == "vhost":
            command.extend(["-u", target])
        
        # Add wordlist
        wordlist = config.get("wordlist")
        if wordlist and os.path.exists(wordlist):
            command.extend(["-w", wordlist])
        
        # Add threads
        if config.get("threads"):
            command.extend(["-t", str(config["threads"])])
        
        # Add timeout
        if config.get("timeout"):
            command.extend(["--timeout", str(config["timeout"]) + "s"])
        
        # Add extensions for dir mode
        if mode == "dir" and config.get("extensions"):
            command.extend(["-x", ",".join(config["extensions"])])
        
        # Add status codes
        if config.get("status_codes"):
            command.extend(["-s", ",".join(config["status_codes"])])
        
        # Add follow redirects
        if config.get("follow_redirects"):
            command.append("-r")
        
        # Add include length
        if config.get("include_length"):
            command.append("-l")
        
        # Add user agent
        if config.get("user_agent"):
            command.extend(["-a", config["user_agent"]])
        
        result = await self._run_command(command, timeout=300)  # 5 minute timeout
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('='):
                    # Parse gobuster output
                    parts = line.split()
                    if len(parts) >= 2:
                        path = parts[0]
                        status = parts[1] if len(parts) > 1 else "200"
                        
                        findings.append({
                            "type": FindingType.DIRECTORY.value if mode == "dir" else FindingType.SUBDOMAIN.value,
                            "value": path,
                            "source": "gobuster",
                            "confidence": 0.8,
                            "metadata": {
                                "status_code": status,
                                "mode": mode,
                                "target": target,
                                "config": config
                            }
                        })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

# ============================================================================
# FUZZING & ENDPOINT TOOLS
# ============================================================================

class EnhancedFfufPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("ffuf", settings.ffuf_path)
        self.supported_options = {
            "wordlist": {
                "type": "string",
                "description": "Path to wordlist file",
                "default": "/usr/share/wordlists/dirb/common.txt"
            },
            "threads": {
                "type": "integer",
                "description": "Number of threads",
                "min": 1,
                "max": 100,
                "default": 40
            },
            "delay": {
                "type": "string",
                "description": "Delay between requests (e.g., '0.1s')",
                "default": "0"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds",
                "min": 1,
                "max": 60,
                "default": 10
            },
            "match_codes": {
                "type": "list",
                "description": "Match HTTP status codes",
                "default": ["200", "204", "301", "302", "307", "401", "403"]
            },
            "filter_codes": {
                "type": "list",
                "description": "Filter HTTP status codes",
                "default": ["404"]
            },
            "filter_size": {
                "type": "list",
                "description": "Filter response sizes",
                "default": []
            },
            "extensions": {
                "type": "list",
                "description": "File extensions to fuzz",
                "default": ["php", "html", "js", "txt"]
            },
            "method": {
                "type": "string",
                "description": "HTTP method",
                "allowed_values": ["GET", "POST", "PUT", "DELETE", "HEAD"],
                "default": "GET"
            },
            "data": {
                "type": "string",
                "description": "POST data",
                "default": ""
            },
            "headers": {
                "type": "list",
                "description": "Custom headers",
                "default": []
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Fast web fuzzer written in Go"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        # Prepare URL with FUZZ keyword
        if "FUZZ" not in target:
            target = target.rstrip('/') + "/FUZZ"
        
        command = [self.tool_path, "-u", target, "-o", "json"]
        
        # Add wordlist
        wordlist = config.get("wordlist")
        if wordlist and os.path.exists(wordlist):
            command.extend(["-w", wordlist])
        
        # Add threads
        if config.get("threads"):
            command.extend(["-t", str(config["threads"])])
        
        # Add delay
        if config.get("delay") and config["delay"] != "0":
            command.extend(["-p", config["delay"]])
        
        # Add timeout
        if config.get("timeout"):
            command.extend(["-timeout", str(config["timeout"])])
        
        # Add match codes
        if config.get("match_codes"):
            command.extend(["-mc", ",".join(config["match_codes"])])
        
        # Add filter codes
        if config.get("filter_codes"):
            command.extend(["-fc", ",".join(config["filter_codes"])])
        
        # Add filter size
        if config.get("filter_size"):
            command.extend(["-fs", ",".join(map(str, config["filter_size"]))])
        
        # Add extensions
        if config.get("extensions"):
            command.extend(["-e", ",".join(config["extensions"])])
        
        # Add method
        if config.get("method") and config["method"] != "GET":
            command.extend(["-X", config["method"]])
        
        # Add POST data
        if config.get("data"):
            command.extend(["-d", config["data"]])
        
        # Add headers
        if config.get("headers"):
            for header in config["headers"]:
                command.extend(["-H", header])
        
        # Add silent mode
        command.append("-s")
        
        result = await self._run_command(command, timeout=300)  # 5 minute timeout
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get("url") and data.get("status"):
                        findings.append({
                            "type": FindingType.DIRECTORY.value,
                            "value": data["url"],
                            "source": "ffuf",
                            "confidence": 0.85,
                            "metadata": {
                                "status_code": data["status"],
                                "length": data.get("length", 0),
                                "words": data.get("words", 0),
                                "lines": data.get("lines", 0),
                                "config": config
                            }
                        })
                except json.JSONDecodeError:
                    continue
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

class EnhancedKatanaPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("katana", settings.katana_path)
        self.supported_options = {
            "depth": {
                "type": "integer",
                "description": "Maximum crawl depth",
                "min": 1,
                "max": 10,
                "default": 3
            },
            "js_crawl": {
                "type": "boolean",
                "description": "Enable JavaScript crawling",
                "default": True
            },
            "crawl_duration": {
                "type": "integer",
                "description": "Maximum crawl duration in minutes",
                "min": 1,
                "max": 60,
                "default": 10
            },
            "concurrency": {
                "type": "integer",
                "description": "Number of concurrent crawlers",
                "min": 1,
                "max": 50,
                "default": 10
            },
            "delay": {
                "type": "integer",
                "description": "Delay between requests in seconds",
                "min": 0,
                "max": 10,
                "default": 0
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds",
                "min": 1,
                "max": 60,
                "default": 10
            },
            "retries": {
                "type": "integer",
                "description": "Number of retries",
                "min": 0,
                "max": 5,
                "default": 1
            },
            "scope": {
                "type": "list",
                "description": "Crawling scope patterns",
                "default": []
            },
            "exclude": {
                "type": "list",
                "description": "Exclude patterns",
                "default": []
            },
            "extensions": {
                "type": "list",
                "description": "File extensions to crawl",
                "default": ["php", "asp", "aspx", "jsp", "js"]
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Next-generation crawling and spidering framework"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        command = [self.tool_path, "-u", target, "-silent", "-jsonl"]
        
        # Add depth
        if config.get("depth"):
            command.extend(["-d", str(config["depth"])])
        
        # Add JS crawling
        if config.get("js_crawl"):
            command.append("-js-crawl")
        
        # Add crawl duration
        if config.get("crawl_duration"):
            command.extend(["-crawl-duration", str(config["crawl_duration"]) + "m"])
        
        # Add concurrency
        if config.get("concurrency"):
            command.extend(["-c", str(config["concurrency"])])
        
        # Add delay
        if config.get("delay"):
            command.extend(["-delay", str(config["delay"]) + "s"])
        
        # Add timeout
        if config.get("timeout"):
            command.extend(["-timeout", str(config["timeout"])])
        
        # Add retries
        if config.get("retries"):
            command.extend(["-retries", str(config["retries"])])
        
        # Add scope
        if config.get("scope"):
            for scope_pattern in config["scope"]:
                command.extend(["-scope", scope_pattern])
        
        # Add exclude
        if config.get("exclude"):
            for exclude_pattern in config["exclude"]:
                command.extend(["-exclude", exclude_pattern])
        
        # Add extensions
        if config.get("extensions"):
            command.extend(["-extension", ",".join(config["extensions"])])
        
        result = await self._run_command(command, timeout=config.get("crawl_duration", 10) * 60 + 60)
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                try:
                    data = json.loads(line)
                    if data.get("request") and data["request"].get("url"):
                        url = data["request"]["url"]
                        findings.append({
                            "type": FindingType.CRAWLED_URL.value,
                            "value": url,
                            "source": "katana",
                            "confidence": 0.8,
                            "metadata": {
                                "method": data["request"].get("method", "GET"),
                                "status_code": data.get("response", {}).get("status_code"),
                                "content_length": data.get("response", {}).get("content_length"),
                                "config": config
                            }
                        })
                except json.JSONDecodeError:
                    continue
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

class EnhancedWaymorePlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("waymore", settings.waymore_path)
        self.supported_options = {
            "mode": {
                "type": "string",
                "description": "Waymore mode",
                "allowed_values": ["U", "R"],
                "default": "U"
            },
            "limit": {
                "type": "integer",
                "description": "Limit number of URLs",
                "min": 100,
                "max": 50000,
                "default": 5000
            },
            "from_date": {
                "type": "string",
                "description": "From date (YYYYMMDD)",
                "default": ""
            },
            "to_date": {
                "type": "string",
                "description": "To date (YYYYMMDD)",
                "default": ""
            },
            "filter_responses_only": {
                "type": "boolean",
                "description": "Filter responses only",
                "default": False
            },
            "capture_interval": {
                "type": "integer",
                "description": "Capture interval in days",
                "min": 1,
                "max": 365,
                "default": 30
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Tool for downloading archived web pages and extracting URLs"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        command = ["python3", self.tool_path, "-i", target]
        
        # Add mode
        if config.get("mode"):
            command.extend(["-mode", config["mode"]])
        
        # Add limit
        if config.get("limit"):
            command.extend(["-limit", str(config["limit"])])
        
        # Add date range
        if config.get("from_date"):
            command.extend(["-from", config["from_date"]])
        
        if config.get("to_date"):
            command.extend(["-to", config["to_date"]])
        
        # Add filter responses only
        if config.get("filter_responses_only"):
            command.append("-filter-responses-only")
        
        # Add capture interval
        if config.get("capture_interval"):
            command.extend(["-ci", str(config["capture_interval"])])
        
        result = await self._run_command(command, timeout=300)  # 5 minute timeout
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and line.startswith(('http://', 'https://')):
                    findings.append({
                        "type": FindingType.HISTORICAL_URL.value,
                        "value": line,
                        "source": "waymore",
                        "confidence": 0.8,
                        "metadata": {
                            "target": target,
                            "config": config
                        }
                    })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }

# ============================================================================
# PARAMETER DISCOVERY TOOLS
# ============================================================================

class EnhancedParamSpiderPlugin(EnhancedBaseToolPlugin):
    def __init__(self):
        super().__init__("paramspider", settings.paramspider_path)
        self.supported_options = {
            "level": {
                "type": "string",
                "description": "Crawling level",
                "allowed_values": ["high", "medium", "low"],
                "default": "medium"
            },
            "exclude": {
                "type": "list",
                "description": "Extensions to exclude",
                "default": ["png", "jpg", "jpeg", "gif", "svg", "css", "ico"]
            },
            "output": {
                "type": "string",
                "description": "Output format",
                "allowed_values": ["txt", "json"],
                "default": "txt"
            },
            "placeholder": {
                "type": "string",
                "description": "Placeholder for parameter values",
                "default": "FUZZ"
            },
            "subs": {
                "type": "boolean",
                "description": "Include subdomains",
                "default": True
            }
        }
        self.default_config = {key: info["default"] for key, info in self.supported_options.items()}
    
    def _get_description(self) -> str:
        return "Parameter discovery tool for web applications"
    
    async def execute(self, target: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        config = {**self.default_config, **(user_config or {})}
        
        command = ["python3", self.tool_path, "-d", target]
        
        # Add level
        if config.get("level"):
            command.extend(["-l", config["level"]])
        
        # Add exclude
        if config.get("exclude"):
            command.extend(["-e", ",".join(config["exclude"])])
        
        # Add output format
        if config.get("output"):
            command.extend(["-o", config["output"]])
        
        # Add placeholder
        if config.get("placeholder"):
            command.extend(["-p", config["placeholder"]])
        
        # Add subs
        if config.get("subs"):
            command.append("--subs")
        
        result = await self._run_command(command, timeout=300)  # 5 minute timeout
        findings = []
        
        if result["success"] and result["stdout"]:
            lines = result["stdout"].strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and ('?' in line or '&' in line):
                    findings.append({
                        "type": FindingType.PARAMETER.value,
                        "value": line,
                        "source": "paramspider",
                        "confidence": 0.8,
                        "metadata": {
                            "target": target,
                            "config": config
                        }
                    })
        
        return {
            "findings": findings,
            "execution_time": result["execution_time"],
            "success": result["success"],
            "errors": [result["stderr"]] if result["stderr"] else [],
            "command_executed": result["command"],
            "config_used": config
        }