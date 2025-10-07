import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000, // 60 seconds timeout for long-running reconnaissance tasks
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message)
    
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout - the reconnaissance task is taking longer than expected')
    }
    
    if (error.response?.status === 500) {
      throw new Error(error.response.data?.detail || 'Internal server error')
    }
    
    if (error.response?.status === 404) {
      throw new Error('API endpoint not found - make sure ReconIQ backend is running')
    }
    
    if (!error.response) {
      throw new Error('Cannot connect to ReconIQ backend - please check if the server is running')
    }
    
    throw new Error(error.response.data?.detail || error.message)
  }
)

// Chat API functions
export const sendMessage = async (message, sessionId = null) => {
  const response = await api.post('/api/v1/chat/message', {
    message,
    session_id: sessionId,
  })
  return response.data
}

export const getSessions = async () => {
  const response = await api.get('/api/v1/chat/sessions')
  return response.data
}

export const getSessionHistory = async (sessionId) => {
  const response = await api.get(`/api/v1/chat/sessions/${sessionId}/history`)
  return response.data
}

export const deleteSession = async (sessionId) => {
  const response = await api.delete(`/api/v1/chat/sessions/${sessionId}`)
  return response.data
}

// Tools API functions
export const getToolCapabilities = async (toolName = null) => {
  const url = toolName 
    ? `/api/v1/tools/capabilities/${toolName}`
    : '/api/v1/tools/capabilities'
  const response = await api.get(url)
  return response.data
}

export const validateToolConfig = async (toolName, config) => {
  const response = await api.post('/api/v1/tools/validate-config', {
    tool_name: toolName,
    config,
  })
  return response.data
}

export const executeCustomScan = async (target, tools, toolConfigs = {}, sessionId = null) => {
  const response = await api.post('/api/v1/tools/custom-scan', {
    target,
    tools,
    tool_configs: toolConfigs,
    session_id: sessionId,
  })
  return response.data
}

export const executePresetScan = async (presetName, target, sessionId = null) => {
  const params = new URLSearchParams({ target })
  if (sessionId) params.append('session_id', sessionId)
  
  const response = await api.post(`/api/v1/tools/preset-scan/${presetName}?${params}`)
  return response.data
}

export const getToolPresets = async () => {
  const response = await api.get('/api/v1/tools/presets')
  return response.data
}

export const getToolExamples = async () => {
  const response = await api.get('/api/v1/tools/examples')
  return response.data
}

export const getToolsStatus = async () => {
  const response = await api.get('/api/v1/tools/status')
  return response.data
}

// Scan API functions
export const executeScan = async (target, tools = null, sessionId = null) => {
  const response = await api.post('/api/v1/scan/execute', {
    target,
    tools,
    session_id: sessionId,
  })
  return response.data
}

export const getAvailableTools = async () => {
  const response = await api.get('/api/v1/scan/tools')
  return response.data
}

export const exportSession = async (sessionId, format = 'json') => {
  const response = await api.post('/api/v1/scan/export', {
    session_id: sessionId,
    format,
  })
  return response.data
}

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health')
  return response.data
}

// Test connection
export const testConnection = async () => {
  try {
    const response = await healthCheck()
    return { connected: true, data: response }
  } catch (error) {
    return { connected: false, error: error.message }
  }
}

export default api