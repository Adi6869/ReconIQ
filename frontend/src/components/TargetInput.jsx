import React, { useState } from 'react'
import { Target, Send, AlertCircle } from 'lucide-react'

const TargetInput = ({ isOpen, onClose, onSubmit, scanType = "reconnaissance" }) => {
  const [target, setTarget] = useState('')
  const [isValid, setIsValid] = useState(true)

  const validateTarget = (value) => {
    // Basic validation for domain or IP
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})$/
    const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
    const urlRegex = /^https?:\/\/[^\s/$.?#].[^\s]*$/i
    
    return domainRegex.test(value) || ipRegex.test(value) || urlRegex.test(value)
  }

  const handleInputChange = (e) => {
    const value = e.target.value.trim()
    setTarget(value)
    setIsValid(value === '' || validateTarget(value))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (target.trim() && isValid) {
      onSubmit(target.trim())
      setTarget('')
      onClose()
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-900 rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Target className="text-blue-400" size={24} />
            <h2 className="text-xl font-semibold text-white">Specify Target</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-gray-300 mb-4">
            Please specify the target domain or IP address for {scanType}:
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Target Domain or IP Address
              </label>
              <input
                type="text"
                value={target}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="e.g., google.com, 192.168.1.1, https://example.com"
                className={`w-full px-4 py-3 bg-gray-800 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors ${
                  isValid ? 'border-gray-600' : 'border-red-500'
                }`}
                autoFocus
              />
              {!isValid && (
                <div className="flex items-center space-x-2 mt-2 text-red-400">
                  <AlertCircle size={16} />
                  <span className="text-sm">Please enter a valid domain, IP address, or URL</span>
                </div>
              )}
            </div>

            <div className="bg-gray-800 rounded-lg p-4">
              <h4 className="text-sm font-medium text-gray-300 mb-2">Valid formats:</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• Domain: <code className="text-blue-400">google.com</code></li>
                <li>• Subdomain: <code className="text-blue-400">mail.google.com</code></li>
                <li>• IP Address: <code className="text-blue-400">192.168.1.1</code></li>
                <li>• URL: <code className="text-blue-400">https://example.com</code></li>
              </ul>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-700 p-4 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!target.trim() || !isValid}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            <Send size={16} />
            <span>Start Scan</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default TargetInput