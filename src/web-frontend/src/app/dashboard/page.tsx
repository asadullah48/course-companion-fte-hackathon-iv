// src/app/dashboard/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Trophy, Flame, Clock, Star, Award, ChevronRight, Brain, MessageCircle, Users, Search } from 'lucide-react';
import { useAuth } from '@/lib/auth';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [mcpData, setMcpData] = useState<any>(null);
  const [skillSuggestions, setSkillSuggestions] = useState<any[]>([]);

  // Mock recent activity data
  const mockActivity = [
    {
      id: 1,
      type: 'chapter_complete',
      title: 'Introduction to AI Agents',
      module: 'Module 1',
      date: '2026-01-15',
      time: '15 min read',
    },
    {
      id: 2,
      type: 'quiz_pass',
      title: 'AI Agents Fundamentals Quiz',
      module: 'Module 1',
      date: '2026-01-14',
      score: '90%',
    },
    {
      id: 3,
      type: 'achievement',
      title: 'First Steps',
      description: 'Completed your first chapter',
      date: '2026-01-13',
    },
    {
      id: 4,
      type: 'streak',
      title: '3-Day Streak',
      description: 'Learning for 3 consecutive days',
      date: '2026-01-12',
    },
  ];

  // Mock MCP data (simulating what would come from MCP server)
  const mockMcpData = {
    overall: {
      percentage: 45,
      completed_chapters: 4,
      total_chapters: 9,
      current_streak: 5,
      achievements: 6
    },
    modules: [
      {
        id: 1,
        title: 'Foundations of AI Agents',
        completed: true,
        chapters_completed: 3,
        total_chapters: 3
      },
      {
        id: 2,
        title: 'Skills Development',
        completed: false,
        chapters_completed: 1,
        total_chapters: 3
      }
    ],
    chapters: [
      { id: 'ch1-intro-to-agents', completed: true },
      { id: 'ch2-claude-agent-sdk', completed: true },
      { id: 'ch3-mcp-fundamentals', completed: true },
      { id: 'ch4-skill-md-structure', completed: false }
    ]
  };

  // Mock skill suggestions
  const mockSkillSuggestions = [
    {
      id: 'concept-explainer',
      title: 'Explain MCP Integration',
      description: 'Get a detailed explanation of Model Context Protocol',
      icon: Brain,
      color: 'blue'
    },
    {
      id: 'quiz-master',
      title: 'Quiz on Chapter 2',
      description: 'Test your knowledge of Claude Agent SDK',
      icon: MessageCircle,
      color: 'green'
    },
    {
      id: 'socratic-tutor',
      title: 'Understand Agents',
      description: 'Explore AI Agent concepts through guided questions',
      icon: BookOpen,
      color: 'purple'
    },
    {
      id: 'progress-motivator',
      title: 'Check Progress',
      description: 'See your learning achievements and streak',
      icon: Trophy,
      color: 'orange'
    }
  ];

  useEffect(() => {
    if (!authLoading) {
      // Simulate API calls to get user data
      setTimeout(() => {
        setRecentActivity(mockActivity);
        setMcpData(mockMcpData);
        setSkillSuggestions(mockSkillSuggestions);
        setIsLoading(false);
      }, 500);
    }
  }, [authLoading]);

  if (authLoading || isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map((item) => (
              <div key={item} className="bg-white p-6 rounded-xl shadow-sm border">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((item) => (
              <div key={item} className="bg-white p-4 rounded-lg shadow-sm border">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/3"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    router.push('/login');
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome back, {user.name || user.email.split('@')[0]}!</h1>
        <p className="text-gray-600">Here's your learning progress and AI-powered recommendations.</p>
      </div>

      {/* Stats Overview */}
      <div className="bg-white rounded-xl shadow-sm border p-6 mb-8">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Your Learning Journey</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="flex justify-center mb-2">
              <Award className="h-8 w-8 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{mcpData?.overall.percentage || 0}%</p>
            <p className="text-sm text-gray-600">Overall</p>
          </div>
          
          <div className="text-center">
            <div className="flex justify-center mb-2">
              <Clock className="h-8 w-8 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {mcpData?.overall.completed_chapters || 0}/{mcpData?.overall.total_chapters || 9}
            </p>
            <p className="text-sm text-gray-600">Chapters</p>
          </div>
          
          <div className="text-center">
            <div className="flex justify-center mb-2">
              <Flame className="h-8 w-8 text-orange-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{mcpData?.overall.current_streak || 0}</p>
            <p className="text-sm text-gray-600">Day Streak</p>
          </div>
          
          <div className="text-center">
            <div className="flex justify-center mb-2">
              <Trophy className="h-8 w-8 text-purple-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{mcpData?.overall.achievements || 0}</p>
            <p className="text-sm text-gray-600">Achievements</p>
          </div>
        </div>
        
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Course Progress</span>
            <span>{mcpData?.overall.percentage || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all"
              style={{ width: `${mcpData?.overall.percentage || 0}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* AI Skill Suggestions */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">AI-Powered Learning</h2>
          <button 
            onClick={() => router.push('/skills')}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View all skills
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {skillSuggestions.map((suggestion) => {
            const Icon = suggestion.icon;
            return (
              <div 
                key={suggestion.id}
                className="bg-white p-4 rounded-xl shadow-sm border flex items-center justify-between hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => router.push(`/skills#${suggestion.id}`)}
              >
                <div className="flex items-center">
                  <div className={`bg-${suggestion.color}-100 p-2 rounded-lg mr-3`}>
                    <Icon className={`h-5 w-5 text-${suggestion.color}-600`} />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{suggestion.title}</h3>
                    <p className="text-gray-600 text-sm">{suggestion.description}</p>
                  </div>
                </div>
                <ChevronRight className="h-5 w-5 text-gray-400" />
              </div>
            );
          })}
        </div>
      </div>

      {/* MCP Integration Showcase */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">MCP Server Integration</h2>
          <button 
            onClick={() => router.push('/mcp')}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            Explore MCP tools
          </button>
        </div>
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
          <div className="flex items-start">
            <div className="bg-blue-100 p-3 rounded-lg mr-4">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Direct MCP Server Connection</h3>
              <p className="text-gray-700 mb-3">
                This dashboard connects directly to the MCP server that powers the ChatGPT app.
                All your progress data, content access, and quiz results come through the same MCP tools.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <div className="bg-white p-3 rounded-lg border">
                  <h4 className="font-medium text-gray-900 mb-1">Same Data</h4>
                  <p className="text-sm text-gray-600">Progress synced across all interfaces</p>
                </div>
                <div className="bg-white p-3 rounded-lg border">
                  <h4 className="font-medium text-gray-900 mb-1">Same Tools</h4>
                  <p className="text-sm text-gray-600">Using identical MCP endpoints</p>
                </div>
                <div className="bg-white p-3 rounded-lg border">
                  <h4 className="font-medium text-gray-900 mb-1">Same AI</h4>
                  <p className="text-sm text-gray-600">Powered by Claude's intelligence</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
          <button 
            onClick={() => router.push('/activity')} 
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            View all
          </button>
        </div>
        <div className="space-y-4">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="bg-white p-4 rounded-lg shadow-sm border">
              <div className="flex items-start">
                <div className="mr-4">
                  {activity.type === 'chapter_complete' && (
                    <div className="bg-blue-100 p-2 rounded-full">
                      <BookOpen className="h-5 w-5 text-blue-600" />
                    </div>
                  )}
                  {activity.type === 'quiz_pass' && (
                    <div className="bg-green-100 p-2 rounded-full">
                      <Star className="h-5 w-5 text-green-600" />
                    </div>
                  )}
                  {activity.type === 'achievement' && (
                    <div className="bg-yellow-100 p-2 rounded-full">
                      <Trophy className="h-5 w-5 text-yellow-600" />
                    </div>
                  )}
                  {activity.type === 'streak' && (
                    <div className="bg-orange-100 p-2 rounded-full">
                      <Flame className="h-5 w-5 text-orange-600" />
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{activity.title}</h3>
                  {activity.module && (
                    <p className="text-gray-600 text-sm">{activity.module}</p>
                  )}
                  {activity.description && (
                    <p className="text-gray-600 text-sm">{activity.description}</p>
                  )}
                  {activity.score && (
                    <p className="text-green-600 text-sm font-medium">Score: {activity.score}</p>
                  )}
                  {activity.time && (
                    <p className="text-gray-500 text-sm">{activity.time}</p>
                  )}
                </div>
                <div className="text-right text-sm text-gray-500">
                  {new Date(activity.date).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommended Next Steps */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recommended Next Steps</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
            <h3 className="font-bold text-gray-900 mb-2">Continue Module 2</h3>
            <p className="text-gray-700 mb-4">
              You're 33% through the Skills Development module. Complete Chapter 4 to unlock more advanced content.
            </p>
            <button 
              onClick={() => router.push('/modules/2')}
              className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
            >
              Continue learning
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border border-green-100">
            <h3 className="font-bold text-gray-900 mb-2">Try a Quiz</h3>
            <p className="text-gray-700 mb-4">
              Test your knowledge of Claude Agent SDK fundamentals with the Module 2 quiz.
            </p>
            <button 
              onClick={() => router.push('/quizzes/module-2')}
              className="inline-flex items-center text-green-600 hover:text-green-700 font-medium"
            >
              Start quiz
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>
        </div>
      </div>

      {/* MCP Tools Quick Access */}
      <div>
        <h2 className="text-xl font-bold text-gray-900 mb-4">MCP Tools Quick Access</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button 
            onClick={() => router.push('/mcp#get_chapter')}
            className="bg-white p-4 rounded-xl shadow-sm border text-left hover:shadow-md transition-shadow"
          >
            <div className="flex items-center mb-2">
              <BookOpen className="h-5 w-5 text-blue-600 mr-2" />
              <h3 className="font-medium text-gray-900">Get Chapter</h3>
            </div>
            <p className="text-gray-600 text-sm">Access course content directly</p>
          </button>
          <button 
            onClick={() => router.push('/mcp#search_content')}
            className="bg-white p-4 rounded-xl shadow-sm border text-left hover:shadow-md transition-shadow"
          >
            <div className="flex items-center mb-2">
              <Search className="h-5 w-5 text-indigo-600 mr-2" />
              <h3 className="font-medium text-gray-900">Search Content</h3>
            </div>
            <p className="text-gray-600 text-sm">Find specific topics in course</p>
          </button>
          <button 
            onClick={() => router.push('/mcp#get_progress')}
            className="bg-white p-4 rounded-xl shadow-sm border text-left hover:shadow-md transition-shadow"
          >
            <div className="flex items-center mb-2">
              <TrendingUp className="h-5 w-5 text-orange-600 mr-2" />
              <h3 className="font-medium text-gray-900">View Progress</h3>
            </div>
            <p className="text-gray-600 text-sm">Track your learning journey</p>
          </button>
        </div>
      </div>
    </div>
  );
}