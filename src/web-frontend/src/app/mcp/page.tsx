// src/app/mcp/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Play, Search, TrendingUp, Clock, User } from 'lucide-react';
import { useAuth } from '@/lib/auth';

export default function MCPPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [mcpTool, setMcpTool] = useState<string | null>(null);
  const [toolArgs, setToolArgs] = useState<any>({});
  const [toolResult, setToolResult] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const mcpTools = [
    {
      id: 'get_chapter',
      name: 'Get Chapter',
      description: 'Retrieve chapter content from the course',
      icon: BookOpen,
      color: 'blue',
      args: { chapter_id: 'ch1-intro-to-agents' }
    },
    {
      id: 'list_chapters',
      name: 'List Chapters',
      description: 'Get list of all available chapters',
      icon: BookOpen,
      color: 'green',
      args: {}
    },
    {
      id: 'start_quiz',
      name: 'Start Quiz',
      description: 'Begin a new quiz attempt',
      icon: Play,
      color: 'purple',
      args: { quiz_id: 'quiz-ch1-intro-001' }
    },
    {
      id: 'get_progress',
      name: 'Get Progress',
      description: 'View user progress across modules',
      icon: TrendingUp,
      color: 'orange',
      args: { user_id: user?.id || 'user-123' }
    },
    {
      id: 'search_content',
      name: 'Search Content',
      description: 'Search course content by keyword',
      icon: Search,
      color: 'indigo',
      args: { query: 'AI Agents' }
    }
  ];

  const handleToolExecution = async () => {
    if (!mcpTool) return;

    setIsProcessing(true);
    setToolResult(null);

    try {
      const response = await fetch('/api/v3/mcp', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tool: mcpTool,
          arguments: { ...toolArgs, user_id: user?.id || 'user-123' }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to execute MCP tool');
      }

      const result = await response.json();
      setToolResult(result);
    } catch (error) {
      console.error('Error executing MCP tool:', error);
      setToolResult({
        error: 'Failed to execute MCP tool. Please try again.',
        status: 'error'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleArgChange = (key: string, value: any) => {
    setToolArgs(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">MCP Server Integration</h1>
        <p className="text-gray-600">
          Direct integration with the Model Context Protocol (MCP) server that powers the ChatGPT app.
          These tools connect to the same backend API as the ChatGPT experience.
        </p>
      </div>

      {/* MCP Tools Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {mcpTools.map((tool) => {
          const Icon = tool.icon;
          const isSelected = mcpTool === tool.id;
          
          return (
            <div
              key={tool.id}
              className={`bg-white rounded-xl shadow-sm border p-6 cursor-pointer transition-all hover:shadow-md ${
                isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
              }`}
              onClick={() => {
                setMcpTool(tool.id);
                setToolArgs(tool.args);
                setToolResult(null);
              }}
            >
              <div className={`w-12 h-12 rounded-lg bg-${tool.color}-100 flex items-center justify-center mb-4`}>
                <Icon className={`h-6 w-6 text-${tool.color}-600`} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{tool.name}</h3>
              <p className="text-gray-600 text-sm">{tool.description}</p>
              <div className="mt-3 text-xs text-gray-500">
                <code className="bg-gray-100 px-2 py-1 rounded">
                  {tool.id}
                </code>
              </div>
            </div>
          );
        })}
      </div>

      {/* Tool Execution Area */}
      {mcpTool && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
          <div className="mb-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {mcpTools.find(t => t.id === mcpTool)?.name}
            </h2>
            <p className="text-gray-600">
              {mcpTools.find(t => t.id === mcpTool)?.description}
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tool Arguments:
              </label>
              
              {/* Dynamic argument inputs based on selected tool */}
              {mcpTool === 'get_chapter' && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Chapter ID</label>
                    <input
                      type="text"
                      value={toolArgs.chapter_id || ''}
                      onChange={(e) => handleArgChange('chapter_id', e.target.value)}
                      placeholder="e.g., ch1-intro-to-agents"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Format (optional)</label>
                    <select
                      value={toolArgs.format || ''}
                      onChange={(e) => handleArgChange('format', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    >
                      <option value="">Default</option>
                      <option value="markdown">Markdown</option>
                      <option value="json">JSON</option>
                      <option value="html">HTML</option>
                    </select>
                  </div>
                </div>
              )}

              {mcpTool === 'list_chapters' && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Module ID (optional)</label>
                    <input
                      type="text"
                      value={toolArgs.module_id || ''}
                      onChange={(e) => handleArgChange('module_id', e.target.value)}
                      placeholder="e.g., mod-1-foundations"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="include_locked"
                      checked={toolArgs.include_locked || false}
                      onChange={(e) => handleArgChange('include_locked', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="include_locked" className="ml-2 block text-sm text-gray-700">
                      Include Locked Chapters
                    </label>
                  </div>
                </div>
              )}

              {mcpTool === 'start_quiz' && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Quiz ID</label>
                    <input
                      type="text"
                      value={toolArgs.quiz_id || ''}
                      onChange={(e) => handleArgChange('quiz_id', e.target.value)}
                      placeholder="e.g., quiz-ch1-intro-001"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              )}

              {mcpTool === 'get_progress' && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">User ID</label>
                    <input
                      type="text"
                      value={toolArgs.user_id || user?.id || ''}
                      onChange={(e) => handleArgChange('user_id', e.target.value)}
                      placeholder="User ID"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="include_chapters"
                      checked={toolArgs.include_chapters || false}
                      onChange={(e) => handleArgChange('include_chapters', e.target.checked)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="include_chapters" className="ml-2 block text-sm text-gray-700">
                      Include Chapter Details
                    </label>
                  </div>
                </div>
              )}

              {mcpTool === 'search_content' && (
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Search Query</label>
                    <input
                      type="text"
                      value={toolArgs.query || ''}
                      onChange={(e) => handleArgChange('query', e.target.value)}
                      placeholder="Enter search term"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Limit (optional)</label>
                    <input
                      type="number"
                      value={toolArgs.limit || ''}
                      onChange={(e) => handleArgChange('limit', parseInt(e.target.value))}
                      placeholder="Max results"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
              )}

              <button
                onClick={handleToolExecution}
                disabled={isProcessing}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {isProcessing ? 'Executing...' : 'Execute Tool'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tool Result Display */}
      {toolResult && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">MCP Tool Result</h3>
          
          {toolResult.error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{toolResult.error}</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Tool Executed:</h4>
                <p className="text-blue-800"><code>{toolResult.tool}</code></p>
              </div>
              
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-2">Result:</h4>
                <pre className="text-sm text-gray-700 whitespace-pre-wrap overflow-x-auto">
                  {JSON.stringify(toolResult.result, null, 2)}
                </pre>
              </div>
              
              {toolResult.status === 'simulated' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-medium text-yellow-900 mb-2">Note:</h4>
                  <p className="text-yellow-800">
                    This is a simulated result. In a real implementation, this would connect to the MCP server 
                    to execute the tool and return actual data from the backend API.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* MCP Architecture Info */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
        <div className="flex items-start">
          <div className="bg-blue-100 p-3 rounded-lg mr-4">
            <User className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">MCP Server Architecture</h3>
            <p className="text-gray-700 mb-3">
              The Model Context Protocol (MCP) server acts as a bridge between this web interface and the backend API,
              providing the same functionality that powers the ChatGPT app.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-1">Web Interface</h4>
                <p className="text-sm text-gray-600">This page connects to MCP server</p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-1">MCP Server</h4>
                <p className="text-sm text-gray-600">Acts as proxy to backend API</p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-1">Backend API</h4>
                <p className="text-sm text-gray-600">Serves content deterministically</p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-1">ChatGPT App</h4>
                <p className="text-sm text-gray-600">Uses same MCP server as web</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}