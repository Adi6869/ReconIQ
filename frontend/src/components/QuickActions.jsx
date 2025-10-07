import React from 'react'
import { 
  Search, 
  Zap, 
  Code, 
  FileText, 
  Shield, 
  BookOpen,
  Clock,
  Globe,
  Target,
  Activity,
  Camera,
  Folder,
  Wifi,
  Layers
} from 'lucide-react'

const QuickActions = ({ onAction, compact = false }) => {
  const quickActions = [
    {
      id: 'research',
      icon: <Search size={16} />,
      label: 'Subdomain',
      message: 'Find subdomains using subfinder and assetfinder',
      color: 'bg-blue-600 hover:bg-blue-700',
      description: 'Subdomain enumeration'
    },
    {
      id: 'comprehensive',
      icon: <Shield size={16} />,
      label: 'Full Scan',
      message: 'Run comprehensive scan with all tools',
      color: 'bg-green-600 hover:bg-green-700',
      description: 'Complete reconnaissance'
    },
    {
      id: 'quick',
      icon: <Zap size={16} />,
      label: 'Quick',
      message: 'Quick scan with basic tools',
      color: 'bg-yellow-600 hover:bg-yellow-700',
      description: 'Fast enumeration'
    },
    {
      id: 'ports',
      icon: <Wifi size={16} />,
      label: 'Port Scan',
      message: 'Scan ports using nmap and naabu',
      color: 'bg-red-600 hover:bg-red-700',
      description: 'Port discovery'
    },
    {
      id: 'content',
      icon: <Folder size={16} />,
      label: 'Content',
      message: 'Discover content using gobuster and ffuf',
      color: 'bg-purple-600 hover:bg-purple-700',
      description: 'Directory discovery'
    },
    {
      id: 'screenshot',
      icon: <Camera size={16} />,
      label: 'Screenshot',
      message: 'Take screenshots of web services using gowitness',
      color: 'bg-pink-600 hover:bg-pink-700',
      description: 'Visual reconnaissance'
    },
    {
      id: 'crawl',
      icon: <Layers size={16} />,
      label: 'Crawl',
      message: 'Crawl and spider using katana',
      color: 'bg-indigo-600 hover:bg-indigo-700',
      description: 'Web crawling'
    },
    {
      id: 'wayback',
      icon: <Clock size={16} />,
      label: 'Historical',
      message: 'Find historical URLs using waybackurls and waymore',
      color: 'bg-teal-600 hover:bg-teal-700',
      description: 'Archive analysis'
    }
  ]

  const learningActions = [
    {
      id: 'learn',
      icon: <BookOpen size={16} />,
      label: 'Learn',
      message: 'Explain reconnaissance techniques and best practices',
      color: 'bg-teal-600 hover:bg-teal-700'
    },
    {
      id: 'tools',
      icon: <Code size={16} />,
      label: 'Tools',
      message: 'Show me available tools and their capabilities',
      color: 'bg-pink-600 hover:bg-pink-700'
    },
    {
      id: 'custom_config',
      icon: <Target size={16} />,
      label: 'Custom Config',
      message: '',
      color: 'bg-gray-600 hover:bg-gray-700'
    }
  ]

  if (compact) {
    return (
      <div className="flex flex-wrap gap-2">
        {quickActions.slice(0, 4).map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action)}
            className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 ${action.color} text-white`}
          >
            {action.icon}
            <span className="ml-1">{action.label}</span>
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Main Actions - Smaller Grid */}
      <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
        {quickActions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action)}
            className={`inline-flex items-center px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 hover:scale-105 ${action.color} text-white flex-col p-3 h-16 justify-center`}
          >
            <div className="flex items-center justify-center mb-1">
              {action.icon}
            </div>
            <span className="font-medium text-xs">{action.label}</span>
          </button>
        ))}
      </div>

      {/* Learning Actions - Smaller */}
      <div className="grid grid-cols-3 gap-2">
        {learningActions.map((action) => (
          <button
            key={action.id}
            onClick={() => onAction(action)}
            className={`inline-flex items-center px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 hover:scale-105 ${action.color} text-white flex-col p-3 h-14 justify-center`}
          >
            <div className="flex items-center justify-center mb-1">
              {action.icon}
            </div>
            <span className="font-medium text-xs">{action.label}</span>
          </button>
        ))}
      </div>

      {/* Custom Examples - Smaller */}
      <div className="text-center">
        <p className="text-xs text-gray-400 mb-2">Or try these examples:</p>
        <div className="flex flex-wrap justify-center gap-1">
          {[
            'Find subdomains for google.com',
            'Scan ports on 192.168.1.1',
            'Take screenshots of github.com',
            'Find directories on tesla.com',
            'Crawl and spider reddit.com'
          ].map((example, index) => (
            <button
              key={index}
              onClick={() => onAction({ message: example })}
              className="px-2 py-1 bg-gray-800 hover:bg-gray-700 rounded-full text-xs text-gray-300 transition-colors"
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default QuickActions