import React, { useState, useEffect, useRef } from 'react'
import { 
  Search, 
  Zap, 
  Code, 
  FileText, 
  Shield, 
  BookOpen,
  Send,
  Menu,
  Settings,
  History,
  Download,
  Loader2,
  ArrowLeft,
  Home,
  Sliders
} from 'lucide-react'
import ChatMessage from './components/ChatMessage'
import QuickActions from './components/QuickActions'
import Sidebar from './components/Sidebar'
import ConnectionStatus from './components/ConnectionStatus'
import StartupGuide from './components/StartupGuide'
import ToolConfig from './components/ToolConfig'
import TargetInput from './components/TargetInput'
import { sendMessage, getToolCapabilities, testConnection } from './services/api.jsx'

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "Hello! I'm ReconIQ, your AI-powered reconnaissance assistant. I'd be happy to help you with cybersecurity reconnaissance. What would you like to explore today?",
      timestamp: new Date(),
      avatar: '🤖'
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [toolCapabilities, setToolCapabilities] = useState({})
  const [showStartupGuide, setShowStartupGuide] = useState(false)
  const [showToolConfig, setShowToolConfig] = useState(false)
  const [showTargetInput, setShowTargetInput] = useState(false)
  const [pendingAction, setPendingAction] = useState(null)
  const [backendConnected, setBackendConnected] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Test backend connection and load capabilities on startup
    const initializeApp = async () => {
      try {
        const connectionTest = await testConnection()
        setBackendConnected(connectionTest.connected)
        
        if (connectionTest.connected) {
          const capabilities = await getToolCapabilities()
          setToolCapabilities(capabilities)
        } else {
          // Show startup guide if backend is not connected
          setTimeout(() => setShowStartupGuide(true), 2000)
        }
      } catch (error) {
        console.error('Failed to initialize app:', error)
        setBackendConnected(false)
        setTimeout(() => setShowStartupGuide(true), 2000)
      }
    }
    initializeApp()
  }, [])

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      avatar: '👤'
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await sendMessage(message, sessionId)
      
      if (!sessionId && response.session_id) {
        setSessionId(response.session_id)
      }

      const assistantMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.reply,
        timestamp: new Date(),
        avatar: '🤖',
        toolsExecuted: response.tools_executed,
        results: response.results,
        requiresClarification: response.requires_clarification
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Chat error:', error)
      
      let errorContent = `Sorry, I encountered an error: ${error.message}`
      
      // Provide specific guidance based on error type
      if (error.message.includes('Cannot connect')) {
        errorContent += '\n\n**To fix this:**\n1. Start the ReconIQ backend: `uvicorn app.main:app --reload`\n2. Make sure it\'s running on http://localhost:8000\n3. Check the connection status in the header'
      } else if (error.message.includes('timeout')) {
        errorContent += '\n\n**This usually means:**\n- The reconnaissance task is taking longer than expected\n- Try a simpler query or check if the tools are properly installed'
      } else if (error.message.includes('API key')) {
        errorContent += '\n\n**API Configuration Issue:**\n- Make sure your Gemini API key is set in the backend config.env file'
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: errorContent,
        timestamp: new Date(),
        avatar: '❌',
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleQuickAction = (action) => {
    if (action.id === 'custom_config') {
      setShowToolConfig(true)
    } else {
      // Check if the action message needs a target
      if (action.message && !containsTarget(action.message)) {
        setPendingAction(action)
        setShowTargetInput(true)
      } else {
        handleSendMessage(action.message)
      }
    }
  }

  const containsTarget = (message) => {
    // Check if message contains a domain, IP, or URL
    const domainRegex = /\b[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})\b/
    const ipRegex = /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/
    const urlRegex = /https?:\/\/[^\s/$.?#].[^\s]*/i
    
    return domainRegex.test(message) || ipRegex.test(message) || urlRegex.test(message)
  }

  const handleTargetSubmit = (target) => {
    if (pendingAction) {
      const messageWithTarget = `${pendingAction.message} for ${target}`
      handleSendMessage(messageWithTarget)
      setPendingAction(null)
    }
  }

  const handleToolConfigExecute = (result) => {
    // Add the scan result as a message
    const resultMessage = {
      id: Date.now(),
      type: 'assistant',
      content: `Custom scan completed! Found ${result.total_findings || 0} results using ${result.tools_executed?.join(', ') || 'selected tools'}.`,
      timestamp: new Date(),
      avatar: '🔧',
      toolsExecuted: result.tools_executed,
      results: result
    }
    setMessages(prev => [...prev, resultMessage])
  }

  const handleBackToHome = () => {
    setMessages([
      {
        id: 1,
        type: 'assistant',
        content: "Hello! I'm ReconIQ, your AI-powered reconnaissance assistant. I'd be happy to help you with cybersecurity reconnaissance. What would you like to explore today?",
        timestamp: new Date(),
        avatar: '🤖'
      }
    ])
    setSessionId(null)
    setInputMessage('')
  }

  return (
    <div className="flex h-screen bg-gray-950 text-white">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)}
        sessionId={sessionId}
        messages={messages}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <Menu size={20} />
            </button>
            {messages.length > 1 && (
              <button
                onClick={handleBackToHome}
                className="p-2 hover:bg-gray-800 rounded-lg transition-colors flex items-center space-x-2 text-blue-400 hover:text-blue-300"
                title="Back to Home"
              >
                <ArrowLeft size={16} />
                <span className="text-sm">Back</span>
              </button>
            )}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <Shield size={16} className="text-white" />
              </div>
              <h1 className="text-xl font-semibold">ReconIQ</h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <ConnectionStatus />
            <button 
              onClick={() => setShowToolConfig(true)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="Tool Configuration"
            >
              <Sliders size={20} />
            </button>
            <button 
              onClick={() => setShowStartupGuide(true)}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
              title="Setup Guide"
            >
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Welcome Screen */}
        {messages.length === 1 && (
          <div className="flex-1 flex flex-col">
            {/* Welcome Header */}
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Shield size={32} className="text-white" />
              </div>
              <h2 className="text-2xl font-bold mb-2">🎯 What's new, Security Researcher?</h2>
              <p className="text-gray-400 mb-6">Ready to start your reconnaissance journey?</p>
            </div>

            {/* Chat Input at Top */}
            <div className="px-8 mb-6">
              <div className="flex items-end space-x-3 max-w-4xl mx-auto">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask ReconIQ anything about reconnaissance..."
                    className="w-full bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3 pr-12 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="1"
                    style={{ minHeight: '48px', maxHeight: '120px' }}
                    disabled={isLoading}
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputMessage.trim() || isLoading}
                    className="absolute right-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-xl transition-colors"
                  >
                    {isLoading ? (
                      <Loader2 size={16} className="animate-spin" />
                    ) : (
                      <Send size={16} />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Quick Actions Below - Smaller */}
            <div className="flex-1 px-8 pb-8">
              <div className="max-w-4xl mx-auto">
                <QuickActions onAction={handleQuickAction} />
              </div>
            </div>
          </div>
        )}

        {/* Chat Messages */}
        {messages.length > 1 && (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}

            {isLoading && (
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0">
                  🤖
                </div>
                <div className="bg-gray-800 rounded-2xl px-4 py-3 max-w-3xl">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-sm text-gray-400">ReconIQ is thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input Area - Only show when in chat mode */}
        {messages.length > 1 && (
          <div className="p-4 border-t border-gray-800">
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Message ReconIQ..."
                  className="w-full bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3 pr-12 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows="1"
                  style={{ minHeight: '48px', maxHeight: '120px' }}
                  disabled={isLoading}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!inputMessage.trim() || isLoading}
                  className="absolute right-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-xl transition-colors"
                >
                  {isLoading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Send size={16} />
                  )}
                </button>
              </div>
            </div>
            
            <div className="mt-3">
              <QuickActions onAction={handleQuickAction} compact />
            </div>
          </div>
        )}
      </div>

      {/* Tool Configuration Modal */}
      <ToolConfig 
        isOpen={showToolConfig} 
        onClose={() => setShowToolConfig(false)}
        onExecute={handleToolConfigExecute}
      />

      {/* Target Input Modal */}
      <TargetInput 
        isOpen={showTargetInput} 
        onClose={() => {
          setShowTargetInput(false)
          setPendingAction(null)
        }}
        onSubmit={handleTargetSubmit}
        scanType={pendingAction?.description || "reconnaissance"}
      />

      {/* Startup Guide Modal */}
      <StartupGuide 
        isOpen={showStartupGuide} 
        onClose={() => setShowStartupGuide(false)} 
      />
    </div>
  )
}

export default App