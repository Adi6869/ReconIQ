import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Google Gemini API Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Tool Configuration - Recon Tools
    subfinder_path: str = "subfinder"
    assetfinder_path: str = "assetfinder"
    dnsx_path: str = "dnsx"
    httpx_path: str = "httpx"
    amass_path: str = "amass"
    
    # Port Scan Tools
    nmap_path: str = "nmap"
    naabu_path: str = "naabu"
    
    # Screenshot Tools
    gowitness_path: str = "gowitness"
    eyewitness_path: str = "eyewitness"
    
    # Content Discovery Tools
    gobuster_path: str = "gobuster"
    
    # Fuzzing & Endpoint Tools
    ffuf_path: str = "ffuf"
    katana_path: str = "katana"
    waybackurls_path: str = "waybackurls"
    waymore_path: str = "waymore"
    
    # Parameter Discovery Tools
    paramspider_path: str = "paramspider"
    
    # Session Configuration
    sessions_dir: str = "sessions"
    max_session_age_days: int = 30
    
    # Execution Configuration
    default_timeout: int = 300  # 5 minutes
    max_concurrent_tools: int = 3
    
    class Config:
        env_file = "config.env"

settings = Settings()