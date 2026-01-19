// src/app/modules/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, CheckCircle, Clock, User, Lock } from 'lucide-react';
import { CourseCard } from '@/components/CourseCard';
import { useAuth } from '@/lib/auth';

export default function ModulesPage() {
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
      isLocked: false, // First module is always free
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
      isLocked: user?.tier === 'free', // Locked for free users
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
      isLocked: user?.tier === 'free', // Locked for free users
    },
  ];

  useEffect(() => {
    // In a real app, this would fetch from the API
    setTimeout(() => {
      setModules(mockModules);
      setIsLoadingModules(false);
    }, 500);
  }, [user]);

  if (isLoadingModules) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-8"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((item) => (
              <div key={item} className="bg-white rounded-xl shadow-sm border p-6">
                <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded-full w-3/4 mb-4"></div>
                <div className="h-10 bg-gray-200 rounded w-full"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Course Modules</h1>
        <p className="text-gray-600">
          Explore our comprehensive curriculum designed to take you from AI agent fundamentals to advanced production deployment.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules.map((module) => (
          <CourseCard key={module.id} module={module} />
        ))}
      </div>

      {/* Premium Benefits Section */}
      {user?.tier === 'free' && (
        <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
          <div className="flex items-start">
            <div className="bg-blue-100 p-3 rounded-lg mr-4">
              <Lock className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Unlock Premium Content</h3>
              <p className="text-gray-700 mb-4">
                Upgrade to Premium to access Modules 2 and 3, advanced quizzes, and exclusive content.
              </p>
              <button
                onClick={() => router.push('/pricing')}
                className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
              >
                Upgrade to Premium
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}