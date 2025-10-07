import React, { useState, useEffect } from 'react'
import { 
  Settings, 
  Play, 
  Save, 
  RotateCcw, 
  Info, 
  ChevronDown, 
  ChevronRight,
  Zap,
  Shield,
  Search,
  Globe,
  Camera,
  Folder,
  Wifi,
  Clock
} from 'lucide-react'
import { getToolCapabilities, executeCustomScan, getToolPresets } from '../services/api.jsx'

const ToolConfig = ({ isOpen, onClose, onExecute }) => {
  const [selectedTools, setSelectedTools] = useState([])
  const [toolConfigs, setToolConfigs] = useState({})
  const [toolCapabilities, setToolCapabilities] = useState({})
  const [presets, setPresets] = useState({})
  const [target, setTarget] = useState('')
  const [expandedTools, setExpandedTools] = useState({})
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('tools')

  const toolCategories = {
    'Recon Tools': {
      tools: ['subfinder', 'assetfinder', 'dnsx', 'httpx', 'amass'],
      icon: <Search size={16} />,
      color: 'bg-blue-500'
    },
    'Port Scan': {
      tools: ['nmap', 'naabu'],
      icon: <Wifi size={16} />,
      color: 'bg-red-500'
    },
    'Screenshots': {
      tools: ['gowitness', 'eyewitness'],
      icon: <Camera size={16} />,
      color: 'bg-pink-500'
    },
    'Content Discovery': {
      tools: ['gobuster'],
      icon: <Folder size={16} />,
      color: 'bg-purple-500'
    },
    'Fuzzing & Crawling': {
      tools: ['ffuf', 'katana', 'waybackurls', 'waymore'],
      icon: <Globe size={16} />,
      color: 'bg-indigo-500'
    },
    'Parameter Discovery': {
      tools: ['paramspider'],
      icon: <Settings size={16} />,
      color: 'bg-teal-500'
    }
  }

  useEffect(() => {
    if (isOpen) {
      loadToolCapabilities()
      loadPresets()
    }
  }, [isOpen])

  const loadToolCapabilities = async () => {
    try {
      const response = await getToolCapabilities()
      setToolCapabilities(response.tools || {})
    } catch (error) {
      console.error('Failed to load tool capabilities:', error)
    }
  }

  const loadPresets = async () => {
    try {
      const response = await getToolPresets()
      setPresets(response.presets || {})
    } catch (error) {
      console.error('Failed to load presets:', error)
    }
  }

  const handleToolToggle = (toolName) => {
    setSelectedTools(prev => {
      if (prev.includes(toolName)) {
        return prev.filter(t => t !== toolName)
      } else {
        return [...prev, toolName]
      }
    })
  }

  const handleConfigChange = (toolName, configKey, value) => {
    setToolConfigs(prev => ({
      ...prev,
      [toolName]: {
        ...prev[toolName],
        [configKey]: value
      }
    }))
  }

  const toggleToolExpanded = (toolName) => {
    setExpandedTools(prev => ({
      ...prev,
      [toolName]: !prev[toolName]
    }))
  }

  const handlePresetSelect = (presetName) => {
    const preset = presets[presetName]
    if (preset) {
      setSelectedTools(preset.tools)
      setToolConfigs(preset.configs || {})
    }
  }

  const handleExecute = async () => {
    if (!target.trim() || selectedTools.length === 0) {
      alert('Please specify a target and select at least one tool')
      return
    }

    setLoading(true)
    try {
      const result = await executeCustomScan(target, selectedTools, toolConfigs)
      onExecute(result)
      onClose()
    } catch (error) {
      console.error('Scan execution failed:', error)
      alert('Scan execution failed: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  const resetConfig = () => {
    setSelectedTools([])
    setToolConfigs({})
    setTarget('')
    setExpandedTools({})
  }

  const renderToolOption = (toolName, option, config) => {
    const value = toolConfigs[toolName]?.[option.name] ?? option.default
    
    switch (option.type) {
      case 'boolean':
        return (
          <label key={option.name} className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => handleConfigChange(toolName, option.name, e.target.checked)}
              className="rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500"
            />
            <span className="text-sm">{option.description}</span>
          </label>
        )
      
      case 'integer':
        return (
          <div key={option.name} className="space-y-1">
            <label className="text-sm font-medium">{option.description}</label>
            <input
              type="number"
              value={value}
              min={option.min}
              max={option.max}
              onChange={(e) => handleConfigChange(toolName, option.name, parseInt(e.target.value))}
              className="w-full px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm focus:ring-2 focus:ring-blue-500"
            />
            {option.min !== undefined && option.max !== undefined && (
              <span className="text-xs text-gray-400">Range: {option.min} - {option.max}</span>
            )}
          </div>
        )
      
      case 'string':
        if (option.allowed_values) {
          return (
            <div key={option.name} className="space-y-1">
              <label className="text-sm font-medium">{option.description}</label>
              <select
                value={value}
                onChange={(e) => handleConfigChange(toolName, option.name, e.target.value)}
                className="w-full px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm focus:ring-2 focus:ring-blue-500"
              >
                {option.allowed_values.map(val => (
                  <option key={val} value={val}>{val}</option>
                ))}
              </select>
            </div>
          )
        } else {
          return (
            <div key={option.name} className="space-y-1">
              <label className="text-sm font-medium">{option.description}</label>
              <input
                type="text"
                value={value}
                onChange={(e) => handleConfigChange(toolName, option.name, e.target.value)}
                className="w-full px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm focus:ring-2 focus:ring-blue-500"
                placeholder={option.default}
              />
            </div>
          )
        }
      
      case 'list':
        return (
          <div key={option.name} className="space-y-1">
            <label className="text-sm font-medium">{option.description}</label>
            <input
              type="text"
              value={Array.isArray(value) ? value.join(', ') : value}
              onChange={(e) => handleConfigChange(toolName, option.name, e.target.value.split(',').map(s => s.trim()))}
              className="w-full px-3 py-1 bg-gray-700 border border-gray-600 rounded text-sm focus:ring-2 focus:ring-blue-500"
              placeholder="Comma-separated values"
            />
            {option.allowed_values && (
              <span className="text-xs text-gray-400">
                Available: {option.allowed_values.join(', ')}
              </span>
            )}
          </div>
        )
      
      default:
        return null
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg shadow-xl w-full max-w-6xl h-5/6 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Settings className="text-blue-400" size={24} />
            <h2 className="text-xl font-semibold text-white">Tool Configuration</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-700">
          <button
            onClick={() => setActiveTab('tools')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'tools' 
                ? 'text-blue-400 border-b-2 border-blue-400' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Tools & Configuration
          </button>
          <button
            onClick={() => setActiveTab('presets')}
            className={`px-6 py-3 font-medium transition-colors ${
              activeTab === 'presets' 
                ? 'text-blue-400 border-b-2 border-blue-400' 
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Presets
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {activeTab === 'tools' && (
            <div className="h-full flex">
              {/* Tool Selection */}
              <div className="w-1/3 border-r border-gray-700 p-4 overflow-y-auto">
                <h3 className="text-lg font-medium text-white mb-4">Select Tools</h3>
                
                {Object.entries(toolCategories).map(([category, info]) => (
                  <div key={category} className="mb-6">
                    <div className="flex items-center space-x-2 mb-3">
                      <div className={`p-1 rounded ${info.color}`}>
                        {info.icon}
                      </div>
                      <h4 className="font-medium text-gray-300">{category}</h4>
                    </div>
                    
                    <div className="space-y-2 ml-6">
                      {info.tools.map(toolName => {
                        const capabilities = toolCapabilities[toolName]
                        const isSelected = selectedTools.includes(toolName)
                        const isAvailable = capabilities?.available !== false
                        
                        return (
                          <div key={toolName} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => handleToolToggle(toolName)}
                              disabled={!isAvailable}
                              className="rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-blue-500 disabled:opacity-50"
                            />
                            <span className={`text-sm ${isAvailable ? 'text-white' : 'text-gray-500'}`}>
                              {toolName}
                            </span>
                            {!isAvailable && (
                              <span className="text-xs text-red-400">(not available)</span>
                            )}
                            {capabilities?.description && (
                              <Info size={12} className="text-gray-400" title={capabilities.description} />
                            )}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>

              {/* Tool Configuration */}
              <div className="flex-1 p-4 overflow-y-auto">
                <h3 className="text-lg font-medium text-white mb-4">Configuration</h3>
                
                {selectedTools.length === 0 ? (
                  <div className="text-center text-gray-400 mt-8">
                    <Settings size={48} className="mx-auto mb-4 opacity-50" />
                    <p>Select tools from the left panel to configure them</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {selectedTools.map(toolName => {
                      const capabilities = toolCapabilities[toolName]
                      const isExpanded = expandedTools[toolName]
                      
                      return (
                        <div key={toolName} className="bg-gray-800 rounded-lg p-4">
                          <button
                            onClick={() => toggleToolExpanded(toolName)}
                            className="flex items-center justify-between w-full text-left"
                          >
                            <div className="flex items-center space-x-2">
                              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                              <span className="font-medium text-white">{toolName}</span>
                              {capabilities?.version && (
                                <span className="text-xs text-gray-400">v{capabilities.version}</span>
                              )}
                            </div>
                          </button>
                          
                          {isExpanded && capabilities?.supported_options && (
                            <div className="mt-4 space-y-3">
                              {Object.entries(capabilities.supported_options).map(([optionName, option]) =>
                                renderToolOption(toolName, { name: optionName, ...option }, toolConfigs[toolName])
                              )}
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'presets' && (
            <div className="p-6 overflow-y-auto">
              <h3 className="text-lg font-medium text-white mb-4">Scan Presets</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(presets).map(([presetName, preset]) => (
                  <div key={presetName} className="bg-gray-800 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-white capitalize">
                        {presetName.replace('_', ' ')}
                      </h4>
                      <button
                        onClick={() => handlePresetSelect(presetName)}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors"
                      >
                        Use Preset
                      </button>
                    </div>
                    
                    <p className="text-gray-300 text-sm mb-3">{preset.description}</p>
                    
                    <div className="space-y-2">
                      <div>
                        <span className="text-xs text-gray-400">Tools:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {preset.tools.map(tool => (
                            <span key={tool} className="px-2 py-1 bg-gray-700 rounded text-xs">
                              {tool}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-gray-700 p-4">
          <div className="flex items-center space-x-4 mb-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-300 mb-1">Target</label>
              <input
                type="text"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="example.com"
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={resetConfig}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
              >
                <RotateCcw size={16} />
                <span>Reset</span>
              </button>
              
              <span className="text-sm text-gray-400">
                {selectedTools.length} tools selected
              </span>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded transition-colors"
              >
                Cancel
              </button>
              
              <button
                onClick={handleExecute}
                disabled={loading || !target.trim() || selectedTools.length === 0}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded transition-colors"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Executing...</span>
                  </>
                ) : (
                  <>
                    <Play size={16} />
                    <span>Execute Scan</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ToolConfig