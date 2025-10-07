import React, { useState, useEffect } from 'react'
import { Wifi, WifiOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import { testConnection, healthCheck } from '../services/api.jsx'

const ConnectionStatus = () => {
  const [status, setStatus] = useState('checking') // checking, connected, disconnected, error
  const [lastCheck, setLastCheck] = useState(null)
  const [backendInfo, setBackendInfo] = useState(null)

  const checkConnection = async () => {
    setStatus('checking')
    try {
      const result = await testConnection()
      if (result.connected) {
        setStatus('connected')
        setBackendInfo(result.data)
      } else {
        setStatus('disconnected')
        setBackendInfo(null)
      }
    } catch (error) {
      setStatus('error')
      setBackendInfo(null)
    }
    setLastCheck(new Date())
  }

  useEffect(() => {
    checkConnection()
    // Check connection every 30 seconds
    const interval = setInterval(checkConnection, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = () => {
    switch (status) {
      case 'checking':
        return <Loader2 size={16} className="animate-spin text-yellow-400" />
      case 'connected':
        return <CheckCircle size={16} className="text-green-400" />
      case 'disconnected':
        return <WifiOff size={16} className="text-red-400" />
      case 'error':
        return <AlertCircle size={16} className="text-red-400" />
      default:
        return <Wifi size={16} className="text-gray-400" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'checking':
        return 'Checking...'
      case 'connected':
        return 'Backend Connected'
      case 'disconnected':
        return 'Backend Offline'
      case 'error':
        return 'Connection Error'
      default:
        return 'Unknown'
    }
  }

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return 'text-green-400'
      case 'disconnected':
      case 'error':
        return 'text-red-400'
      case 'checking':
        return 'text-yellow-400'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={checkConnection}
        className="flex items-center space-x-2 px-3 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
        title={`Last checked: ${lastCheck ? lastCheck.toLocaleTimeString() : 'Never'}`}
      >
        {getStatusIcon()}
        <span className={`text-xs ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </button>
      
      {status === 'disconnected' && (
        <div className="text-xs text-red-400">
          Make sure backend is running: uvicorn app.main:app --reload
        </div>
      )}
    </div>
  )
}

export default ConnectionStatus