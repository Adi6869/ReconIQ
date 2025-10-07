import React, { useState } from 'react'
import { 
  Copy, 
  Download, 
  ExternalLink, 
  CheckCircle, 
  AlertCircle,
  Clock,
  Zap,
  Search,
  Globe,
  Shield
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'

const ChatMessage = ({ message }) => {
  const [copied, setCopied] = useState(false)

  const handleCopy = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getToolIcon = (toolName) => {
    const icons = {
      'subfinder': <Search size={14} />,
      'amass': <Globe size={14} />,
      'waybackurls': <Clock size={14} />,
      'httpx': <Zap size={14} />
    }
    return icons[toolName] || <Shield size={14} />
  }

  const getToolColor = (toolName) => {
    const colors = {
      'subfinder': 'bg-blue-500',
      'amass': 'bg-green-500',
      'waybackurls': 'bg-purple-500',
      'httpx': 'bg-orange-500'
    }
    return colors[toolName] || 'bg-gray-500'
  }

  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      {message.type === 'assistant' && (
        <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0 mr-3">
          {message.avatar}
        </div>
      )}
      
      <div className={`rounded-2xl px-4 py-3 max-w-3xl ${
        message.type === 'user' 
          ? 'bg-blue-600 text-white ml-auto' 
          : message.isError 
            ? 'bg-red-900 border border-red-700 text-gray-100' 
            : 'bg-gray-800 text-gray-100'
      }`}>
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">
              {message.type === 'user' ? 'You' : 'ReconIQ'}
            </span>
            <span className="text-xs text-gray-400">
              {formatTimestamp(message.timestamp)}
            </span>
          </div>
          
          <div className="flex items-center space-x-1">
            {message.toolsExecuted && message.toolsExecuted.length > 0 && (
              <div className="flex items-center space-x-1">
                {message.toolsExecuted.map((tool, index) => (
                  <div
                    key={index}
                    className={`flex items-center space-x-1 px-2 py-1 rounded-md text-xs ${getToolColor(tool)} text-white`}
                    title={`Executed ${tool}`}
                  >
                    {getToolIcon(tool)}
                    <span>{tool}</span>
                  </div>
                ))}
              </div>
            )}
            
            <button
              onClick={() => handleCopy(message.content)}
              className="p-1 hover:bg-gray-700 rounded transition-colors"
              title="Copy message"
            >
              {copied ? (
                <CheckCircle size={14} className="text-green-400" />
              ) : (
                <Copy size={14} className="text-gray-400" />
              )}
            </button>
          </div>
        </div>

        <div className="prose prose-invert max-w-none">
          <ReactMarkdown
            components={{
              code: ({ node, inline, className, children, ...props }) => {
                if (inline) {
                  return (
                    <code className="bg-gray-700 px-1 py-0.5 rounded text-sm" {...props}>
                      {children}
                    </code>
                  )
                }
                return (
                  <div className="relative">
                    <pre className="bg-gray-900 p-3 rounded-lg overflow-x-auto">
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                    <button
                      onClick={() => handleCopy(String(children))}
                      className="absolute top-2 right-2 p-1 hover:bg-gray-700 rounded transition-colors"
                    >
                      <Copy size={12} className="text-gray-400" />
                    </button>
                  </div>
                )
              },
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 inline-flex items-center space-x-1"
                >
                  <span>{children}</span>
                  <ExternalLink size={12} />
                </a>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Results Summary */}
        {message.results && message.results.total_findings > 0 && (
          <div className="mt-3 p-3 bg-gray-900 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-green-400">
                📊 Reconnaissance Results
              </h4>
              <span className="text-xs text-gray-400">
                {message.results.total_findings} findings
              </span>
            </div>
            
            {message.results.execution_summary && (
              <div className="space-y-2">
                {Object.entries(message.results.execution_summary).map(([key, summary]) => (
                  <div key={key} className="flex items-center justify-between text-xs">
                    <span className="text-gray-300">{key}</span>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded ${
                        summary.status === 'completed' ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'
                      }`}>
                        {summary.status}
                      </span>
                      {summary.findings_count !== undefined && (
                        <span className="text-gray-400">{summary.findings_count} results</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Clarification Required */}
        {message.requiresClarification && (
          <div className="mt-3 p-3 bg-yellow-900 border border-yellow-700 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle size={16} className="text-yellow-400" />
              <span className="text-sm text-yellow-200">
                Please provide more details to continue
              </span>
            </div>
          </div>
        )}
      </div>

      {message.type === 'user' && (
        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-center flex-shrink-0 ml-3">
          {message.avatar}
        </div>
      )}
    </div>
  )
}

export default ChatMessage