// src/app/dashboard/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BookOpen, Trophy, Flame, Clock, Star, Award, ChevronRight } from 'lucide-react';
import { ProgressOverview } from '@/components/ProgressOverview';
import { useAuth } from '@/lib/auth';
import Link from 'next/link';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading } = useAuth();
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

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

  useEffect(() => {
    if (!authLoading) {
      // Simulate API call to get recent activity
      setTimeout(() => {
        setRecentActivity(mockActivity);
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
        <p className="text-gray-600">Here's your learning progress and recent activity.</p>
      </div>

      {/* Stats Overview */}
      <ProgressOverview user={user} />

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Continue Learning</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Next Chapter</h3>
              <p className="text-gray-600 text-sm">MCP Integration</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400" />
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Pending Quiz</h3>
              <p className="text-gray-600 text-sm">Module 1 Quiz</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400" />
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900">Achievement</h3>
              <p className="text-gray-600 text-sm">Next milestone</p>
            </div>
            <ChevronRight className="h-5 w-5 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-900">Recent Activity</h2>
          <Link href="/activity" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
            View all
          </Link>
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
      <div className="mt-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Recommended Next Steps</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
            <h3 className="font-bold text-gray-900 mb-2">Complete Module 1</h3>
            <p className="text-gray-700 mb-4">
              You're 67% through the Foundations module. Finish it to unlock the next module.
            </p>
            <Link 
              href="/modules/1" 
              className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
            >
              Continue learning
              <ChevronRight className="h-4 w-4 ml-1" />
            </Link>
          </div>
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-xl border border-green-100">
            <h3 className="font-bold text-gray-900 mb-2">Take the Quiz</h3>
            <p className="text-gray-700 mb-4">
              Test your knowledge of AI Agent fundamentals with the Module 1 quiz.
            </p>
            <Link 
              href="/quizzes/module-1" 
              className="inline-flex items-center text-green-600 hover:text-green-700 font-medium"
            >
              Start quiz
              <ChevronRight className="h-4 w-4 ml-1" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}