// src/app/integration/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Brain, MessageCircle, BookOpen, Trophy, Users, Server, Zap, ArrowRight } from 'lucide-react';
import { useAuth } from '@/lib/auth';

export default function IntegrationPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [integrationStatus, setIntegrationStatus] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'mcp' | 'architecture'>('overview');

  // Mock integration status data
  useEffect(() => {
    const mockStatus = {
      webFrontend: { status: 'connected', lastSync: new Date().toISOString() },
      mcpServer: { status: 'running', version: '1.0.0', connections: 12 },
      skillsSystem: { status: 'active', activeSkills: 4, lastExecution: new Date().toISOString() },
      backendApi: { status: 'healthy', responseTime: '45ms' },
      chatGptApp: { status: 'synced', lastUpdate: new Date().toISOString() }
    };
    setIntegrationStatus(mockStatus);
  }, []);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Brain },
    { id: 'skills', label: 'Skills', icon: MessageCircle },
    { id: 'mcp', label: 'MCP Server', icon: Server },
    { id: 'architecture', label: 'Architecture', icon: Users }
  ];

  const architectureDiagram = [
    {
      layer: 'User Interface',
      components: [
        { name: 'Web Frontend', description: 'Next.js application with React components', status: 'active' },
        { name: 'ChatGPT App', description: 'OpenAI ChatGPT integration', status: 'active' },
        { name: 'Mobile App', description: 'Future mobile interface', status: 'planned' }
      ]
    },
    {
      layer: 'Integration Layer',
      components: [
        { name: 'MCP Server', description: 'Model Context Protocol server', status: 'active' },
        { name: 'Skills System', description: '4 core AI skills', status: 'active' },
        { name: 'API Gateway', description: 'Request routing and authentication', status: 'active' }
      ]
    },
    {
      layer: 'Backend Services',
      components: [
        { name: 'Content API', description: 'Serves course content verbatim', status: 'active' },
        { name: 'Progress API', description: 'Tracks user progress', status: 'active' },
        { name: 'Quiz API', description: 'Manages assessments', status: 'active' }
      ]
    },
    {
      layer: 'Data Layer',
      components: [
        { name: 'PostgreSQL', description: 'User data and progress', status: 'active' },
        { name: 'Cloudflare R2', description: 'Course content storage', status: 'active' },
        { name: 'Redis', description: 'Caching and sessions', status: 'active' }
      ]
    }
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">System Integration</h1>
        <p className="text-gray-600">
          Complete integration between web frontend, AI skills, MCP server, and backend services.
          All components work together to provide a unified learning experience.
        </p>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
        {integrationStatus && Object.entries(integrationStatus).map(([system, status]: [string, any]) => {
          const statusColor = status.status === 'connected' || status.status === 'running' || status.status === 'active' || status.status === 'healthy' || status.status === 'synced' 
            ? 'bg-green-100 text-green-800' 
            : status.status === 'disconnected' || status.status === 'stopped' || status.status === 'inactive' || status.status === 'error' 
              ? 'bg-red-100 text-red-800' 
              : 'bg-yellow-100 text-yellow-800';
          
          return (
            <div key={system} className="bg-white rounded-lg shadow-sm border p-4">
              <h3 className="font-medium text-gray-900 capitalize mb-1">{system.replace(/([A-Z])/g, ' $1')}</h3>
              <span className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${statusColor}`}>
                {status.status}
              </span>
              {status.responseTime && (
                <p className="text-xs text-gray-500 mt-1">{status.responseTime}</p>
              )}
              {status.connections && (
                <p className="text-xs text-gray-500 mt-1">{status.connections} connections</p>
              )}
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Integration Overview</h2>
            <p className="text-gray-600 mb-4">
              The Course Companion system integrates multiple components to provide a seamless learning experience.
              The web frontend, MCP server, and skills system work together to deliver the same intelligent tutoring
              experience across different interfaces.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h3 className="font-semibold text-blue-900 mb-2">Unified Experience</h3>
                <p className="text-blue-800 text-sm">
                  Whether you're using the web interface, ChatGPT app, or Claude Desktop, 
                  you get the same content, progress tracking, and AI-powered tutoring.
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border border-green-100">
                <h3 className="font-semibold text-green-900 mb-2">Shared Intelligence</h3>
                <p className="text-green-800 text-sm">
                  The same Claude-powered skills provide explanations, quizzes, and guidance 
                  across all interfaces through the MCP server.
                </p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg border border-purple-100">
                <h3 className="font-semibold text-purple-900 mb-2">Consistent Data</h3>
                <p className="text-purple-800 text-sm">
                  Progress, achievements, and learning history are synchronized across 
                  all platforms through the shared backend API.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'skills' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">AI Skills System</h2>
            <p className="text-gray-600 mb-4">
              The skills system provides the core AI-powered tutoring capabilities that work across all interfaces.
              Each skill connects to the same backend API through the MCP server.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <Brain className="h-5 w-5 text-blue-600 mr-2" />
                  <h3 className="font-medium text-gray-900">Concept Explainer</h3>
                </div>
                <p className="text-sm text-gray-600 mb-2">Provides detailed explanations of AI Agent concepts</p>
                <div className="text-xs text-gray-500">Connects to: Content API → Chapter retrieval</div>
              </div>
              
              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <MessageCircle className="h-5 w-5 text-green-600 mr-2" />
                  <h3 className="font-medium text-gray-900">Quiz Master</h3>
                </div>
                <p className="text-sm text-gray-600 mb-2">Administers interactive quizzes with immediate feedback</p>
                <div className="text-xs text-gray-500">Connects to: Quiz API → Grading</div>
              </div>
              
              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <BookOpen className="h-5 w-5 text-purple-600 mr-2" />
                  <h3 className="font-medium text-gray-900">Socratic Tutor</h3>
                </div>
                <p className="text-sm text-gray-600 mb-2">Guides learning through strategic questioning</p>
                <div className="text-xs text-gray-500">Connects to: Content API → Concept exploration</div>
              </div>
              
              <div className="border rounded-lg p-4">
                <div className="flex items-center mb-3">
                  <Trophy className="h-5 w-5 text-orange-600 mr-2" />
                  <h3 className="font-medium text-gray-900">Progress Motivator</h3>
                </div>
                <p className="text-sm text-gray-600 mb-2">Tracks achievements and motivates continued learning</p>
                <div className="text-xs text-gray-500">Connects to: Progress API → Achievement tracking</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'mcp' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">MCP Server Integration</h2>
            <p className="text-gray-600 mb-4">
              The Model Context Protocol (MCP) server acts as a bridge between the user interfaces 
              (web, ChatGPT) and the backend API. It translates MCP tool calls into REST API requests.
            </p>
            
            <div className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-3">MCP Tool Flow</h3>
              <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
                <div className="text-center">
                  <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Users className="h-8 w-8 text-blue-600" />
                  </div>
                  <p className="font-medium">User Interface</p>
                  <p className="text-sm text-gray-600">(Web/ChatGPT)</p>
                </div>
                
                <ArrowRight className="h-6 w-6 text-gray-400 hidden md:block" />
                <div className="h-0.5 w-12 bg-gray-300 md:hidden"></div>
                
                <div className="text-center">
                  <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Server className="h-8 w-8 text-indigo-600" />
                  </div>
                  <p className="font-medium">MCP Server</p>
                  <p className="text-sm text-gray-600">(Proxy)</p>
                </div>
                
                <ArrowRight className="h-6 w-6 text-gray-400 hidden md:block" />
                <div className="h-0.5 w-12 bg-gray-300 md:hidden"></div>
                
                <div className="text-center">
                  <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Zap className="h-8 w-8 text-green-600" />
                  </div>
                  <p className="font-medium">Backend API</p>
                  <p className="text-sm text-gray-600">(FastAPI)</p>
                </div>
              </div>
            </div>
            
            <div className="mt-6 bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Key Benefits</h4>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-700">
                <li>Single point of integration for multiple interfaces</li>
                <li>Standardized tool interface across platforms</li>
                <li>Centralized authentication and rate limiting</li>
                <li>Consistent data access patterns</li>
                <li>Easy to add new tools and capabilities</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'architecture' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">System Architecture</h2>
            <p className="text-gray-600 mb-4">
              The Course Companion architecture is designed for scalability, consistency, and 
              seamless integration across multiple user interfaces.
            </p>
            
            <div className="space-y-6">
              {architectureDiagram.map((layer, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-3">{layer.layer}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {layer.components.map((component, compIndex) => {
                      const statusColor = component.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : component.status === 'planned'
                          ? 'bg-gray-100 text-gray-800'
                          : 'bg-yellow-100 text-yellow-800';
                      
                      return (
                        <div key={compIndex} className="border rounded p-3">
                          <div className="flex justify-between items-start">
                            <h4 className="font-medium text-gray-900">{component.name}</h4>
                            <span className={`text-xs px-2 py-1 rounded-full ${statusColor}`}>
                              {component.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">{component.description}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Integration Benefits */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Integration Benefits</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium text-gray-900 mb-1">Consistent UX</h3>
            <p className="text-sm text-gray-600">Same experience across web, ChatGPT, and Claude Desktop</p>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium text-gray-900 mb-1">Shared Progress</h3>
            <p className="text-sm text-gray-600">Learning history synced across all platforms</p>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium text-gray-900 mb-1">Unified AI</h3>
            <p className="text-sm text-gray-600">Same Claude-powered skills work everywhere</p>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium text-gray-900 mb-1">Scalable</h3>
            <p className="text-sm text-gray-600">MCP server enables easy addition of new interfaces</p>
          </div>
        </div>
      </div>
    </div>
  );
}