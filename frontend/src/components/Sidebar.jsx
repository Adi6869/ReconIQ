import React, { useState, useEffect } from 'react'
import { 
  X, 
  MessageSquare, 
  Download, 
  Trash2, 
  Settings, 
  History,
  FileText,
  Shield,
  Plus,
  Search
} from 'lucide-react'
import { getSessions, exportSession, deleteSession } from '../services/api.jsx'

const Sidebar = ({ isOpen, onClose, sessionId, messages }) => {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    if (isOpen) {
      loadSessions()
    }
  }, [isOpen])

  const loadSessions = async () => {
    try {
      setLoading(true)
      const response = await getSessions()
      setSessions(response.sessions || [])
    } catch (error) {
      console.error('Failed to load sessions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExportSession = async (sessionId, format = 'json') => {
    try {
      const response = await exportSession(sessionId, format)
      
      // Create download link
      const blob = new Blob([response.content], { 
        type: format === 'json' ? 'application/json' : 'text/plain' 
      })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = response.filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to export session:', error)
    }
  }

  const handleDeleteSession = async (sessionId) => {
    if (window.confirm('Are you sure you want to delete this session?')) {
      try {
        await deleteSession(sessionId)
        setSessions(sessions.filter(s => s.session_id !== sessionId))
      } catch (error) {
        console.error('Failed to delete session:', error)
      }
    }
  }

  const filteredSessions = sessions.filter(session =>
    session.session_id.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!isOpen) return null

  return (
    <>
      {/* Overlay */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
        onClick={onClose}
      />
      
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-80 bg-gray-900 border-r border-gray-800 z-50 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <div className="flex items-center space-x-2">
            <Shield size={20} className="text-blue-500" />
            <h2 className="text-lg font-semibold">ReconIQ</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Current Session Info */}
        {sessionId && (
          <div className="p-4 border-b border-gray-800">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-300">Current Session</h3>
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => handleExportSession(sessionId, 'json')}
                  className="p-1 hover:bg-gray-800 rounded transition-colors"
                  title="Export as JSON"
                >
                  <Download size={14} />
                </button>
                <button
                  onClick={() => handleExportSession(sessionId, 'txt')}
                  className="p-1 hover:bg-gray-800 rounded transition-colors"
                  title="Export as TXT"
                >
                  <FileText size={14} />
                </button>
              </div>
            </div>
            <div className="text-xs text-gray-400">
              <p>Session ID: {sessionId.slice(0, 8)}...</p>
              <p>Messages: {messages.length}</p>
            </div>
          </div>
        )}

        {/* Sessions List */}
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-300">Chat History</h3>
              <button
                onClick={loadSessions}
                className="p-1 hover:bg-gray-800 rounded transition-colors"
                title="Refresh"
              >
                <History size={14} />
              </button>
            </div>
            
            <div className="relative">
              <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search sessions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-3 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center text-gray-400">
                <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                Loading sessions...
              </div>
            ) : filteredSessions.length === 0 ? (
              <div className="p-4 text-center text-gray-400">
                <MessageSquare size={24} className="mx-auto mb-2 opacity-50" />
                <p className="text-sm">No sessions found</p>
              </div>
            ) : (
              <div className="space-y-1 p-2">
                {filteredSessions.map((session) => (
                  <div
                    key={session.session_id}
                    className={`p-3 rounded-lg hover:bg-gray-800 transition-colors ${
                      session.session_id === sessionId ? 'bg-gray-800 border border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <MessageSquare size={14} className="text-gray-400 flex-shrink-0" />
                          <span className="text-sm font-medium text-white truncate">
                            Session {session.session_id.slice(0, 8)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-400 space-y-1">
                          <p>Started: {formatDate(session.start_time)}</p>
                          <p>Messages: {session.message_count}</p>
                          <p>Last: {formatDate(session.last_activity)}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-1 ml-2">
                        <button
                          onClick={() => handleExportSession(session.session_id, 'json')}
                          className="p-1 hover:bg-gray-700 rounded transition-colors"
                          title="Export"
                        >
                          <Download size={12} />
                        </button>
                        <button
                          onClick={() => handleDeleteSession(session.session_id)}
                          className="p-1 hover:bg-red-900 rounded transition-colors text-red-400"
                          title="Delete"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800">
          <button className="w-full flex items-center justify-center space-x-2 p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
            <Settings size={16} />
            <span className="text-sm">Settings</span>
          </button>
        </div>
      </div>
    </>
  )
}

export default Sidebar