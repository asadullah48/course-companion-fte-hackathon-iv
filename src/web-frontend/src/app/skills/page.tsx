// src/app/skills/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Brain, MessageCircle, Trophy, Play, Search, Users } from 'lucide-react';
import { useAuth } from '@/lib/auth';

export default function SkillsPage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [skillInput, setSkillInput] = useState('');
  const [skillResult, setSkillResult] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const skills = [
    {
      id: 'concept-explainer',
      name: 'Concept Explainer',
      description: 'Get detailed explanations of AI Agent concepts',
      icon: Brain,
      color: 'blue',
      example: 'Explain MCP to me like I\'m a beginner'
    },
    {
      id: 'quiz-master',
      name: 'Quiz Master',
      description: 'Test your knowledge with interactive quizzes',
      icon: MessageCircle,
      color: 'green',
      example: 'Quiz me on Chapter 1'
    },
    {
      id: 'socratic-tutor',
      name: 'Socratic Tutor',
      description: 'Learn through guided questioning without direct answers',
      icon: BookOpen,
      color: 'purple',
      example: 'Help me understand agents without giving me the answer'
    },
    {
      id: 'progress-motivator',
      name: 'Progress Motivator',
      description: 'Track your achievements and stay motivated',
      icon: Trophy,
      color: 'orange',
      example: 'How\'s my progress?'
    }
  ];

  const handleSkillExecution = async () => {
    if (!selectedSkill || !skillInput.trim()) return;

    setIsProcessing(true);
    setSkillResult(null);

    try {
      const response = await fetch('/api/v3/skills', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skill: selectedSkill,
          input: { query: skillInput }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to execute skill');
      }

      const result = await response.json();
      setSkillResult(result);
    } catch (error) {
      console.error('Error executing skill:', error);
      setSkillResult({
        error: 'Failed to execute skill. Please try again.',
        status: 'error'
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExampleClick = (example: string) => {
    setSkillInput(example);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Skills Integration</h1>
        <p className="text-gray-600">
          Interact with our AI-powered skills that connect to the MCP server, just like in ChatGPT.
          These skills provide the same intelligent tutoring experience in a web interface.
        </p>
      </div>

      {/* Skills Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {skills.map((skill) => {
          const Icon = skill.icon;
          const isSelected = selectedSkill === skill.id;
          
          return (
            <div
              key={skill.id}
              className={`bg-white rounded-xl shadow-sm border p-6 cursor-pointer transition-all hover:shadow-md ${
                isSelected ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
              }`}
              onClick={() => {
                setSelectedSkill(skill.id);
                setSkillInput('');
                setSkillResult(null);
              }}
            >
              <div className={`w-12 h-12 rounded-lg bg-${skill.color}-100 flex items-center justify-center mb-4`}>
                <Icon className={`h-6 w-6 text-${skill.color}-600`} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{skill.name}</h3>
              <p className="text-gray-600 text-sm mb-3">{skill.description}</p>
              <div className="text-xs text-gray-500 italic">
                Example: "{skill.example}"
              </div>
            </div>
          );
        })}
      </div>

      {/* Skill Execution Area */}
      {selectedSkill && (
        <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
          <div className="mb-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {skills.find(s => s.id === selectedSkill)?.name}
            </h2>
            <p className="text-gray-600">
              {skills.find(s => s.id === selectedSkill)?.description}
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label htmlFor="skill-input" className="block text-sm font-medium text-gray-700 mb-2">
                Enter your request:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  id="skill-input"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  placeholder={skills.find(s => s.id === selectedSkill)?.example}
                  className="flex-1 min-w-0 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleSkillExecution();
                    }
                  }}
                />
                <button
                  onClick={handleSkillExecution}
                  disabled={isProcessing || !skillInput.trim()}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  {isProcessing ? 'Processing...' : 'Execute'}
                </button>
              </div>
            </div>

            {/* Example buttons */}
            <div className="flex flex-wrap gap-2">
              {skills.find(s => s.id === selectedSkill)?.example && (
                <button
                  onClick={() => handleExampleClick(skills.find(s => s.id === selectedSkill)!.example)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-800 px-3 py-1 rounded-md"
                >
                  Use example
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Skill Result Display */}
      {skillResult && (
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Skill Result</h3>
          
          {skillResult.error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{skillResult.error}</p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">Response:</h4>
                <p className="text-blue-800 whitespace-pre-line">{skillResult.result}</p>
              </div>
              
              {skillResult.sources && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-2">Sources:</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {skillResult.sources.map((source: string, idx: number) => (
                      <li key={idx} className="text-gray-700">{source}</li>
                    ))}
                  </ul>
                </div>
              )}
              
              {skillResult.nextSteps && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 className="font-medium text-green-900 mb-2">Next Steps:</h4>
                  <ul className="list-disc pl-5 space-y-1">
                    {skillResult.nextSteps.map((step: string, idx: number) => (
                      <li key={idx} className="text-green-800">{step}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* MCP Integration Info */}
      <div className="mt-8 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-6 border border-indigo-100">
        <div className="flex items-start">
          <div className="bg-indigo-100 p-3 rounded-lg mr-4">
            <Users className="h-6 w-6 text-indigo-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">MCP Server Integration</h3>
            <p className="text-gray-700 mb-3">
              This web interface connects to the same MCP (Model Context Protocol) server that powers the ChatGPT app.
              The skills you interact with here use the same underlying tools and content as the ChatGPT experience.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-1">Same Skills</h4>
                <p className="text-sm text-gray-600">All 4 core skills work identically</p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-1">Same Content</h4>
                <p className="text-sm text-gray-600">Access to identical course materials</p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h4 className="font-medium text-gray-900 mb-1">Same Intelligence</h4>
                <p className="text-sm text-gray-600">Powered by Claude's reasoning</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}