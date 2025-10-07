import google.generativeai as genai
from typing import List, Dict, Any, Optional
from ..config import settings
from ..schemas.chat import ChatMessage
import json
import re

class GeminiClient:
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=settings.gemini_api_key)
        
        # Try different model names in order of preference (using the latest available models)
        model_names = [
            'gemini-2.5-flash', 
            'gemini-2.0-flash', 
            'gemini-flash-latest',
            'gemini-pro-latest',
            'gemini-2.5-pro'
        ]
        
        self.model = None
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                # Test the model with a simple query
                test_response = self.model.generate_content("Hello")
                print(f"✅ Using Gemini model: {model_name}")
                break
            except Exception as e:
                print(f"❌ Model {model_name} failed: {e}")
                continue
        
        if not self.model:
            raise ValueError("No working Gemini model found. Please check your API key and model availability.")
        
    def parse_query(self, query: str, context: Optional[List[ChatMessage]] = None) -> Dict[str, Any]:
        """Parse natural language query to extract reconnaissance intent"""
        
        # Build context from previous messages
        context_str = ""
        if context:
            recent_context = context[-5:]  # Last 5 messages for context
            context_parts = []
            for msg in recent_context:
                # Safely format the context to avoid f-string issues
                context_parts.append(f"{msg.type}: {str(msg.content).replace('{', '{{').replace('}', '}}')}")
            context_str = "\n".join(context_parts)
        
        prompt = """
You are ReconIQ, an AI assistant that helps with cybersecurity reconnaissance. 
Analyze the user's query and extract the reconnaissance intent, including any tool customization requests.

Context from previous conversation:
{}

Current user query: "{}"

Respond with a JSON object containing:
{{
    "action": "subdomain_enumeration|url_discovery|http_probe|historical_search|full_reconnaissance|custom_scan|port_scan|content_discovery|screenshot|crawling|parameter_discovery",
    "targets": ["domain1.com", "domain2.com"],
    "tools": ["subfinder", "amass", "waybackurls", "httpx"],
    "confidence": 0.95,
    "clarification_needed": false,
    "clarification_question": "optional question if clarification needed",
    "tool_configs": {{
        "subfinder": {{"threads": 20, "max_time": 10}},
        "amass": {{"mode": "passive", "timeout": 15}}
    }},
    "preset": "quick_scan|comprehensive_scan|stealth_scan|active_scan|content_discovery|screenshot_scan"
}}

Rules:
- ALWAYS extract domain targets from the query (look for domains, IPs, URLs)
- If NO target is found in the query, set clarification_needed=true and ask for target
- Map the intent to appropriate reconnaissance tools based on these patterns:
  * Subdomain enumeration: ["subfinder", "assetfinder", "amass"]
  * Port scanning: ["nmap", "naabu"] 
  * HTTP probing: ["httpx"]
  * URL/endpoint discovery: ["waybackurls", "waymore", "katana"]
  * Content discovery: ["gobuster", "ffuf"]
  * Screenshots: ["gowitness", "eyewitness"]
  * Parameter discovery: ["paramspider"]
  * DNS enumeration: ["dnsx"]
- Use high confidence (>0.8) for clear queries with valid targets
- ALWAYS set clarification_needed=true if NO target domain/IP is specified in the query
- If clarification_needed=true, set clarification_question to ask for the target domain
- If user mentions specific tool names, include those tools
- If user mentions specific tool options (threads, timeout, ports, etc.), include them in tool_configs
- If user mentions scan types like "quick", "fast", "comprehensive", "stealth", "active", set appropriate preset
- Available presets: quick_scan, comprehensive_scan, stealth_scan, active_scan, content_discovery, screenshot_scan
- Tool configuration options:
  * subfinder: threads, max_time, sources, recursive, wordlist
  * assetfinder: timeout, subs_only
  * amass: mode, timeout, brute_force, alterations, wordlist
  * nmap: scan_type, ports, top_ports, timing, version_detection, os_detection, script_scan, aggressive
  * naabu: ports, top_ports, rate, threads, timeout
  * waybackurls: limit, get_versions, dates, no_subs
  * httpx: threads, timeout, tech_detect, ports, method, status_code, title
  * gobuster: mode, wordlist, threads, extensions, status_codes
  * ffuf: wordlist, threads, match_codes, filter_codes, extensions
  * gowitness: timeout, threads, resolution, fullpage
  * katana: depth, js_crawl, crawl_duration, concurrency
  * paramspider: level, exclude, subs
  * dnsx: a, aaaa, cname, mx, ns, txt, threads, timeout

Examples:
- "Find subdomains for google.com" -> action: "subdomain_enumeration", tools: ["subfinder", "assetfinder"], targets: ["google.com"]
- "Scan ports on 192.168.1.1" -> action: "port_scan", tools: ["nmap", "naabu"], targets: ["192.168.1.1"]
- "Run nmap scan on tesla.com" -> action: "port_scan", tools: ["nmap"], targets: ["tesla.com"]
- "Nmap top 100 ports on google.com" -> action: "port_scan", tools: ["nmap"], targets: ["google.com"], tool_configs: {{"nmap": {{"top_ports": 100}}}}
- "Fast nmap scan with version detection" -> action: "port_scan", tools: ["nmap"], tool_configs: {{"nmap": {{"timing": "4", "version_detection": true}}}}
- "Take screenshots of github.com" -> action: "screenshot", tools: ["gowitness"], targets: ["github.com"]
- "Find directories on microsoft.com" -> action: "content_discovery", tools: ["gobuster"], targets: ["microsoft.com"]
- "Find subdomains" -> clarification_needed: true, clarification_question: "Please specify the target domain you want to scan for subdomains."
- "Scan ports" -> clarification_needed: true, clarification_question: "Please specify the target domain or IP address you want to scan."

Respond only with valid JSON.
""".format(context_str, query)

        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return self._fallback_parse(query)
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return self._fallback_parse(query)
    
    def generate_response(self, results: Dict[str, Any], query: str) -> str:
        """Generate natural language response for reconnaissance results"""
        
        findings_summary = ""
        if "findings" in results:
            findings_count = len(results["findings"])
            findings_summary = f"Found {findings_count} results"
        
        tools_used = results.get("tools_executed", [])
        
        # Safely escape dynamic content
        safe_query = str(query).replace('{', '{{').replace('}', '}}')
        safe_results = json.dumps(results, indent=2).replace('{', '{{').replace('}', '}}')
        
        prompt = f"""
You are ReconIQ, a friendly cybersecurity reconnaissance assistant.
Generate a natural, conversational response about the reconnaissance results.

Original query: "{safe_query}"
Tools executed: {tools_used}
Results summary: {findings_summary}
Raw results: {safe_results}

Guidelines:
- Be conversational and helpful
- Summarize the key findings
- Suggest logical next steps
- Keep it concise but informative
- Use security professional language
- If no results found, suggest alternatives

Generate a helpful response:
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"Found {len(results.get('findings', []))} results from {', '.join(tools_used)}. The reconnaissance completed successfully."
    
    def ask_clarification(self, ambiguous_query: str) -> str:
        """Generate clarification question for ambiguous queries"""
        
        # Safely escape the query
        safe_query = str(ambiguous_query).replace('{', '{{').replace('}', '}}')
        
        prompt = f"""
The user asked: "{safe_query}"

This query is ambiguous for reconnaissance purposes. Generate a helpful clarification question to understand what they want to do.

Examples:
- If they mention a domain without specifying the type of scan
- If they use vague terms like "check" or "scan"
- If the target is unclear

Generate a single, clear question to clarify their intent:
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return "Could you please specify what type of reconnaissance you'd like to perform and on which target domain?"
    
    def _fallback_parse(self, query: str) -> Dict[str, Any]:
        """Fallback parsing when Gemini API fails"""
        
        # Simple regex-based parsing
        domains = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', query)
        
        # Determine action based on keywords
        query_lower = query.lower()
        if any(word in query_lower for word in ["subdomain", "subs", "enumerate"]):
            action = "subdomain_enumeration"
            tools = ["subfinder", "assetfinder"]
        elif any(word in query_lower for word in ["port", "nmap", "naabu", "scan"]):
            action = "port_scan"
            tools = ["nmap"] if "nmap" in query_lower else ["naabu"]
        elif any(word in query_lower for word in ["url", "endpoint", "wayback", "historical"]):
            action = "url_discovery"
            tools = ["waybackurls"]
        elif any(word in query_lower for word in ["http", "probe", "web", "service"]):
            action = "http_probe"
            tools = ["httpx"]
        elif any(word in query_lower for word in ["screenshot", "visual", "gowitness"]):
            action = "screenshot"
            tools = ["gowitness"]
        elif any(word in query_lower for word in ["directory", "content", "gobuster", "ffuf"]):
            action = "content_discovery"
            tools = ["gobuster"]
        elif any(word in query_lower for word in ["crawl", "spider", "katana"]):
            action = "crawling"
            tools = ["katana"]
        elif any(word in query_lower for word in ["parameter", "param", "paramspider"]):
            action = "parameter_discovery"
            tools = ["paramspider"]
        else:
            action = "subdomain_enumeration"  # Default
            tools = ["subfinder"]
        
        # Generate appropriate clarification question based on action
        clarification_questions = {
            "subdomain_enumeration": "Please specify the target domain you want to scan for subdomains (e.g., 'Find subdomains for google.com').",
            "port_scan": "Please specify the target domain or IP address you want to scan for open ports (e.g., 'Scan ports on 192.168.1.1').",
            "url_discovery": "Please specify the target domain to search for historical URLs (e.g., 'Find URLs for tesla.com').",
            "http_probe": "Please specify the target domain to probe HTTP services (e.g., 'Probe HTTP services on github.com').",
            "screenshot": "Please specify the target domain to take screenshots (e.g., 'Take screenshots of microsoft.com').",
            "content_discovery": "Please specify the target domain to discover content (e.g., 'Find directories on example.org').",
            "crawling": "Please specify the target domain to crawl (e.g., 'Crawl and spider reddit.com').",
            "parameter_discovery": "Please specify the target domain to find parameters (e.g., 'Find parameters on facebook.com')."
        }
        
        return {
            "action": action,
            "targets": domains,
            "tools": tools,
            "confidence": 0.7 if len(domains) > 0 else 0.3,
            "clarification_needed": len(domains) == 0,
            "clarification_question": clarification_questions.get(action, "Please specify the target domain or IP address for reconnaissance.")
        }