// src/lib/auth.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  name?: string;
  email: string;
  tier: 'free' | 'premium' | 'pro' | 'team';
  progress?: {
    overall: number;
    completedChapters: number;
    totalChapters: number;
    currentStreak: number;
    achievements: number;
    module1?: {
      completed: number;
      percentage: number;
    };
    module2?: {
      completed: number;
      percentage: number;
    };
    module3?: {
      completed: number;
      percentage: number;
    };
  };
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored user session on initial load
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error('Failed to parse stored user:', e);
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    // In a real app, this would make an API call to authenticate
    // For now, we'll simulate a successful login
    setIsLoading(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const mockUser: User = {
      id: 'user-123',
      email,
      tier: email.includes('premium') ? 'premium' : 'free',
      name: email.split('@')[0],
      progress: {
        overall: 25,
        completedChapters: 2,
        totalChapters: 9,
        currentStreak: 3,
        achievements: 2,
        module1: {
          completed: 2,
          percentage: 67
        },
        module2: {
          completed: 0,
          percentage: 0
        },
        module3: {
          completed: 0,
          percentage: 0
        }
      }
    };
    
    setUser(mockUser);
    localStorage.setItem('user', JSON.stringify(mockUser));
    setIsLoading(false);
  };

  const signup = async (name: string, email: string, password: string) => {
    // In a real app, this would make an API call to register
    // For now, we'll simulate a successful signup
    setIsLoading(true);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const mockUser: User = {
      id: 'user-123',
      name,
      email,
      tier: 'free',
      progress: {
        overall: 0,
        completedChapters: 0,
        totalChapters: 9,
        currentStreak: 0,
        achievements: 0,
        module1: {
          completed: 0,
          percentage: 0
        },
        module2: {
          completed: 0,
          percentage: 0
        },
        module3: {
          completed: 0,
          percentage: 0
        }
      }
    };
    
    setUser(mockUser);
    localStorage.setItem('user', JSON.stringify(mockUser));
    setIsLoading(false);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    login,
    signup,
    logout,
    isLoading,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}