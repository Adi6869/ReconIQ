# ReconIQ - AI-Powered Reconnaissance Platform

 **ReconIQ** is an advanced reconnaissance platform that combines the power of AI with industry-standard security tools to provide comprehensive target analysis and intelligence gathering.

##  Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git**
- **Google Gemini API Key** (for AI features)

### Reconnaissance Tools (Optional but Recommended)

ReconIQ integrates with the following tools. Install them for full functionality:

#### Recon Tools
- `subfinder` - Fast subdomain discovery
- `assetfinder` - Asset discovery tool
- `dnsx` - DNS toolkit
- `httpx` - HTTP probe
- `amass` - In-depth DNS enumeration

#### Port Scan Tools
- `nmap` - Network exploration tool
- `naabu` - Fast port scanner

#### Screenshot Tools
- `gowitness` - Web screenshot utility
- `eyewitness` - Screenshot tool with reports

#### Content Discovery
- `gobuster` - Directory/file bruster

#### Fuzzing & Endpoint Tools
- `ffuf` - Fast web fuzzer
- `katana` - Web crawler
- `waybackurls` - Wayback Machine URLs
- `waymore` - Archive URL extractor

#### Parameter Discovery
- `paramspider` - Parameter discovery tool

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ReconIQ
   ```

2. **Set up environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # Install backend dependencies
   pip install -r backend/requirements.txt
   
   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   ```

3. **Configure API keys:**
   ```bash
   # Copy and edit the configuration file
   cp config.env.example config.env
   # Edit config.env and add your GEMINI_API_KEY
   ```

##  Running ReconIQ

### Option 1: Universal Startup Script (Recommended)

We provide a universal Python startup script that works on all platforms and automatically:
- Checks prerequisites and dependencies
- Cleans up unwanted files
- Installs required dependencies
- Starts both backend and frontend servers
- Runs integration tests
- Opens the application in your browser

#### Universal Script (Windows, macOS, Linux)
```bash
python start-reconiq.py
```

#### Script Options
```bash
# Skip file cleanup
python start-reconiq.py --skip-cleanup

# Don't open browser automatically
python start-reconiq.py --skip-browser

# Skip integration tests
python start-reconiq.py --skip-tests

# Custom ports
python start-reconiq.py --backend-port 8080 --frontend-port 3001

# Show help
python start-reconiq.py --help
```

### Option 2: Manual Startup

#### Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Start Frontend Server (New Terminal)
```bash
cd frontend
npm run dev
```

#### Access the Application
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

##  Features

###  AI-Powered Analysis
- Natural language query processing using Google Gemini
- Intelligent tool selection and configuration
- Automated result analysis and summarization

###  Comprehensive Tool Integration
- **15+ reconnaissance tools** integrated
- **Custom tool configurations** with validation
- **Preset scan profiles** for different scenarios
- **Real-time execution monitoring**

###  Advanced Capabilities
- **Session management** with conversation history
- **Multi-format exports** (JSON, CSV, TXT)
- **Real-time status updates** during scans
- **Error handling and recovery**

###  Scan Types
- **Quick Scan:** Fast enumeration with basic tools
- **Comprehensive Scan:** Full reconnaissance with all tools
- **Stealth Scan:** Low-profile reconnaissance
- **Content Discovery:** Directory and file discovery
- **Port Scanning:** Network service discovery
- **Screenshot Capture:** Visual reconnaissance


### API Configuration
Edit `config.env`:
```env
GEMINI_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```



##  Security Considerations

- **API Keys:** Store securely in `config.env`, never commit to version control
- **Tool Permissions:** Ensure reconnaissance tools have appropriate permissions
- **Network Access:** Configure firewall rules for backend/frontend ports
- **Target Authorization:** Only scan targets you own or have explicit permission to test

##  License

This project is licensed under the MIT License - see the LICENSE file for details.
