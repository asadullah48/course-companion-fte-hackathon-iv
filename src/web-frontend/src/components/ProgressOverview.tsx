// src/components/ProgressOverview.tsx
import { Calendar, Trophy, Flame, Award } from 'lucide-react';

interface ProgressOverviewProps {
  user: {
    name?: string;
    email?: string;
    progress?: {
      overall: number;
      completedChapters: number;
      totalChapters: number;
      currentStreak: number;
      achievements: number;
    };
  };
}

export const ProgressOverview = ({ user }: ProgressOverviewProps) => {
  const progress = user.progress || {
    overall: 0,
    completedChapters: 0,
    totalChapters: 9,
    currentStreak: 0,
    achievements: 0,
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Your Learning Journey</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="flex justify-center mb-2">
            <Award className="h-8 w-8 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{progress.overall}%</p>
          <p className="text-sm text-gray-600">Overall</p>
        </div>
        
        <div className="text-center">
          <div className="flex justify-center mb-2">
            <Calendar className="h-8 w-8 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {progress.completedChapters}/{progress.totalChapters}
          </p>
          <p className="text-sm text-gray-600">Chapters</p>
        </div>
        
        <div className="text-center">
          <div className="flex justify-center mb-2">
            <Flame className="h-8 w-8 text-orange-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{progress.currentStreak}</p>
          <p className="text-sm text-gray-600">Day Streak</p>
        </div>
        
        <div className="text-center">
          <div className="flex justify-center mb-2">
            <Trophy className="h-8 w-8 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{progress.achievements}</p>
          <p className="text-sm text-gray-600">Achievements</p>
        </div>
      </div>
      
      <div className="mt-6">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Course Progress</span>
          <span>{progress.overall}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all"
            style={{ width: `${progress.overall}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};