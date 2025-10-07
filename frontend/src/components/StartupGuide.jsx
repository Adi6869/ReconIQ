import React, { useState } from 'react'
import { X, Terminal, Play, CheckCircle, AlertCircle, Copy } from 'lucide-react'

const StartupGuide = ({ isOpen, onClose }) => {
  const [copiedStep, setCopiedStep] = useState(null)

  const copyToClipboard = async (text, step) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedStep(step)
      setTimeout(() => setCopiedStep(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  if (!isOpen) return null

  const steps = [
    {
      id: 1,
      title: 'Start ReconIQ Backend',
      description: 'Navigate to backend directory and start the server',
      command: 'cd backend && uvicorn app.main:app --reload',
      note: 'This starts the API server on http://localhost:8000'
    },
    {
      id: 2,
      title: 'Verify Backend is Running',
      description: 'Check if the backend is responding',
      command: 'curl http://localhost:8000/health',
      note: 'Should return: {"status": "healthy", "service": "ReconIQ API"}'
    },
    {
      id: 3,
      title: 'Install Reconnaissance Tools (Optional)',
      description: 'Install the actual recon tools for full functionality',
      command: `go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/owasp-amass/amass/v4/...@master
go install github.com/tomnomnom/waybackurls@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest`,
      note: 'These tools are needed for actual reconnaissance. Without them, you\'ll get simulated responses.'
    },
    {
      id: 4,
      title: 'Configure Gemini API Key',
      description: 'Set your Google Gemini API key in the backend configuration',
      command: 'GEMINI_API_KEY=your_api_key_here',
      note: 'Add this to your config.env file in the project root'
    }
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div>
            <h2 className="text-xl font-semibold text-white">🚀 ReconIQ Setup Guide</h2>
            <p className="text-gray-400 text-sm mt-1">Get your reconnaissance assistant up and running</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {steps.map((step) => (
            <div key={step.id} className="border border-gray-800 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-white text-sm font-medium">{step.id}</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-medium mb-1">{step.title}</h3>
                  <p className="text-gray-400 text-sm mb-3">{step.description}</p>
                  
                  <div className="bg-gray-950 rounded-lg p-3 mb-2">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Terminal size={14} className="text-gray-400" />
                        <span className="text-xs text-gray-400">Command</span>
                      </div>
                      <button
                        onClick={() => copyToClipboard(step.command, step.id)}
                        className="flex items-center space-x-1 px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs transition-colors"
                      >
                        {copiedStep === step.id ? (
                          <>
                            <CheckCircle size={12} className="text-green-400" />
                            <span className="text-green-400">Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy size={12} className="text-gray-400" />
                            <span className="text-gray-400">Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap">
                      {step.command}
                    </pre>
                  </div>
                  
                  <div className="flex items-start space-x-2">
                    <AlertCircle size={14} className="text-yellow-400 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-yellow-200">{step.note}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}

          <div className="bg-green-900 border border-green-700 rounded-lg p-4">
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle size={16} className="text-green-400" />
              <h3 className="text-green-200 font-medium">Ready to Go!</h3>
            </div>
            <p className="text-green-200 text-sm">
              Once the backend is running (step 1), you can start using ReconIQ immediately. 
              The connection status in the header will show green when everything is connected properly.
            </p>
          </div>
        </div>

        <div className="p-6 border-t border-gray-800">
          <button
            onClick={onClose}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
          >
            Got it, let's start!
          </button>
        </div>
      </div>
    </div>
  )
}

export default StartupGuide