// src/components/CourseCard.tsx
import Link from 'next/link';
import { BookOpen, CheckCircle, Clock, User, Lock } from 'lucide-react';

interface CourseCardProps {
  module: {
    id: number;
    title: string;
    description: string;
    chapters: number;
    completed: number;
    difficulty: string;
    estimatedDuration: string;
    progress: number;
    isLocked?: boolean;
  };
}

export const CourseCard = ({ module }: CourseCardProps) => {
  const isFree = module.id === 1; // First module is free
  const isCompleted = module.completed === module.chapters;

  return (
    <div className={`bg-white rounded-xl shadow-sm border overflow-hidden transition-all hover:shadow-md ${module.isLocked ? 'opacity-70' : ''}`}>
      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{module.title}</h3>
            <div className="flex items-center mt-1 space-x-4 text-sm text-gray-600">
              <span className="flex items-center">
                <BookOpen className="h-4 w-4 mr-1" />
                {module.chapters} chapters
              </span>
              <span className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                {module.estimatedDuration}
              </span>
            </div>
          </div>
          {isCompleted && (
            <CheckCircle className="h-6 w-6 text-green-500" />
          )}
        </div>

        <p className="text-gray-600 mb-4">{module.description}</p>

        <div className="flex justify-between items-center mb-4">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            module.difficulty === 'Beginner' 
              ? 'bg-green-100 text-green-800' 
              : module.difficulty === 'Intermediate' 
                ? 'bg-yellow-100 text-yellow-800' 
                : 'bg-red-100 text-red-800'
          }`}>
            {module.difficulty}
          </span>
          {!isFree && (
            <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
              Premium
            </span>
          )}
        </div>

        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{Math.round(module.progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${module.progress}%` }}
            ></div>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {module.completed}/{module.chapters} chapters completed
          </div>
        </div>

        <div className="flex justify-between items-center">
          {module.isLocked ? (
            <div className="flex items-center text-gray-500">
              <Lock className="h-4 w-4 mr-1" />
              <span className="text-sm">Unlock with Premium</span>
            </div>
          ) : (
            <Link
              href={`/modules/${module.id}`}
              className="w-full text-center bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg text-sm font-medium transition-colors"
            >
              {isCompleted ? 'Review' : 'Start Learning'}
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};