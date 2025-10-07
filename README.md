# ReconIQ - AI-Powered Reconnaissance Platform

🎯 **ReconIQ** is an advanced reconnaissance platform that combines the power of AI with industry-standard security tools to provide comprehensive target analysis and intelligence gathering.

## 🚀 Quick Start

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

## 🎮 Running ReconIQ

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

## 🛠️ Features

### 🤖 AI-Powered Analysis
- Natural language query processing using Google Gemini
- Intelligent tool selection and configuration
- Automated result analysis and summarization

### 🔍 Comprehensive Tool Integration
- **15+ reconnaissance tools** integrated
- **Custom tool configurations** with validation
- **Preset scan profiles** for different scenarios
- **Real-time execution monitoring**

### 📊 Advanced Capabilities
- **Session management** with conversation history
- **Multi-format exports** (JSON, CSV, TXT)
- **Real-time status updates** during scans
- **Error handling and recovery**

### 🎯 Scan Types
- **Quick Scan:** Fast enumeration with basic tools
- **Comprehensive Scan:** Full reconnaissance with all tools
- **Stealth Scan:** Low-profile reconnaissance
- **Content Discovery:** Directory and file discovery
- **Port Scanning:** Network service discovery
- **Screenshot Capture:** Visual reconnaissance

## 💬 Usage Examples

### Natural Language Queries
```
"Find subdomains for example.com"
"Run a comprehensive scan on target.com"
"Scan ports on discovered subdomains"
"Take screenshots of web services"
"Find parameters on example.com"
"Use nmap to scan top 1000 ports"
```

### Tool-Specific Commands
```
"Run subfinder with 20 threads on example.com"
"Use amass in active mode with brute force"
"Scan with gobuster using custom wordlist"
"Take full page screenshots with gowitness"
```

### Configuration Examples
```
"Configure httpx with custom ports 80,443,8080"
"Set nmap timing to aggressive mode"
"Use ffuf with 50 threads and custom extensions"
```

## 🔧 Configuration

### Tool Paths
Edit `backend/app/config.py` to customize tool paths:
```python
# Tool Configuration
subfinder_path: str = "subfinder"
nmap_path: str = "/usr/bin/nmap"
# ... other tools
```

### API Configuration
Edit `config.env`:
```env
GEMINI_API_KEY=your_api_key_here
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
```

## 📁 Project Structure

```
ReconIQ/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── services/       # Core services
│   │   ├── schemas/        # Data models
│   │   └── config.py       # Configuration
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── App.jsx         # Main app
│   └── package.json
├── .kiro/specs/           # Project specifications
├── sessions/              # Session data storage
├── start-reconiq.py       # Universal startup script (all platforms)
├── test_integration.py    # Integration tests
└── config.env             # Environment configuration
```

## 🧪 Testing

### Integration Tests
```bash
python test_integration.py
```

### API Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello ReconIQ"}'
```

## 🔒 Security Considerations

- **API Keys:** Store securely in `config.env`, never commit to version control
- **Tool Permissions:** Ensure reconnaissance tools have appropriate permissions
- **Network Access:** Configure firewall rules for backend/frontend ports
- **Target Authorization:** Only scan targets you own or have explicit permission to test

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start:**
   - Check if port 8000 is available
   - Verify virtual environment is activated
   - Ensure all dependencies are installed

2. **Frontend won't start:**
   - Check if Node.js and npm are installed
   - Verify package.json exists in frontend directory
   - Run `npm install` in frontend directory

3. **Tools not found:**
   - Install reconnaissance tools in your PATH
   - Update tool paths in `config.py`
   - Check tool permissions

4. **API key issues:**
   - Verify GEMINI_API_KEY is set in config.env
   - Check API key permissions and quotas

### Logs and Debugging

- **Backend logs:** Check terminal running uvicorn
- **Frontend logs:** Check browser developer console
- **Integration tests:** Run `python test_integration.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

ReconIQ is intended for authorized security testing and research purposes only. Users are responsible for ensuring they have proper authorization before scanning any targets. The developers are not responsible for any misuse of this tool.

## 🙏 Acknowledgments

- Google Gemini AI for natural language processing
- All the amazing open-source reconnaissance tools integrated
- The cybersecurity community for continuous innovation

---

**Happy Reconnaissance! 🎯**