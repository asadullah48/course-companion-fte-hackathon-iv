// src/app/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Play, Trophy, TrendingUp, Users, Clock } from 'lucide-react';
import { CourseCard } from '@/components/CourseCard';
import { ProgressOverview } from '@/components/ProgressOverview';
import { useAuth } from '@/lib/auth';

export default function HomePage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();
  const [modules, setModules] = useState<any[]>([]);
  const [isLoadingModules, setIsLoadingModules] = useState(true);

  // Mock data for modules
  const mockModules = [
    {
      id: 1,
      title: 'Foundations of AI Agents',
      description: 'Learn the core concepts of AI Agents, the Agent Factory Architecture, and Model Context Protocol',
      chapters: 3,
      completed: user?.progress?.module1?.completed || 0,
      difficulty: 'Beginner',
      estimatedDuration: '2 hours',
      progress: user?.progress?.module1?.percentage || 0,
    },
    {
      id: 2,
      title: 'Skills Development',
      description: 'Master the Claude Agent SDK, create effective SKILL.md files, and integrate external tools',
      chapters: 3,
      completed: user?.progress?.module2?.completed || 0,
      difficulty: 'Intermediate',
      estimatedDuration: '2.5 hours',
      progress: user?.progress?.module2?.percentage || 0,
    },
    {
      id: 3,
      title: 'Agentic Workflows',
      description: 'Design workflow patterns, build multi-agent systems, and deploy to production',
      chapters: 3,
      completed: user?.progress?.module3?.completed || 0,
      difficulty: 'Advanced',
      estimatedDuration: '2 hours',
      progress: user?.progress?.module3?.percentage || 0,
    },
  ];

  useEffect(() => {
    // In a real app, this would fetch from the API
    setTimeout(() => {
      setModules(mockModules);
      setIsLoadingModules(false);
    }, 500);
  }, []);

  const handleStartLearning = () => {
    if (user) {
      router.push('/modules');
    } else {
      router.push('/login');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Hero Section */}
      <section className="mb-16 text-center">
        <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Master AI Agent Development
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Build autonomous AI agents using Claude Agent SDK, MCP integration, and production deployment patterns.
          Learn from fundamentals to advanced agentic workflows.
        </p>
        <div className="flex justify-center gap-4">
          <button
            onClick={handleStartLearning}
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg text-lg transition-colors"
          >
            Start Learning
          </button>
          <button
            onClick={() => router.push('/modules')}
            className="border border-gray-300 hover:border-gray-400 text-gray-700 font-semibold py-3 px-8 rounded-lg text-lg transition-colors"
          >
            Browse Modules
          </button>
        </div>
      </section>

      {/* Stats Section */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
          <BookOpen className="mx-auto h-8 w-8 text-blue-600 mb-2" />
          <h3 className="font-bold text-2xl">9</h3>
          <p className="text-gray-600">Chapters</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
          <Trophy className="mx-auto h-8 w-8 text-green-600 mb-2" />
          <h3 className="font-bold text-2xl">15+</h3>
          <p className="text-gray-600">Achievements</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
          <Users className="mx-auto h-8 w-8 text-purple-600 mb-2" />
          <h3 className="font-bold text-2xl">10k+</h3>
          <p className="text-gray-600">Students</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 text-center">
          <Clock className="mx-auto h-8 w-8 text-orange-600 mb-2" />
          <h3 className="font-bold text-2xl">6-8h</h3>
          <p className="text-gray-600">Duration</p>
        </div>
      </section>

      {/* Progress Overview (for logged in users) */}
      {user && (
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">Your Progress</h2>
          <ProgressOverview user={user} />
        </section>
      )}

      {/* Modules Section */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Course Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module) => (
            <CourseCard key={module.id} module={module} />
          ))}
        </div>
      </section>
    </div>
  );
}