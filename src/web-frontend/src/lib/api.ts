// src/lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

interface ApiOptions {
  method?: string;
  body?: any;
  headers?: Record<string, string>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async request<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options;

    const config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
    };

    if (body) {
      config.body = JSON.stringify(body);
    }

    // In a real app, we would include the auth token
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    const response = await fetch(`${this.baseUrl}${endpoint}`, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `API request failed: ${response.status}`);
    }

    if (response.status === 204) {
      return {} as T; // No content
    }

    return response.json();
  }

  // Content API
  getContent = {
    getChapter: (chapterId: string) => this.request(`/chapters/${chapterId}`),
    listChapters: (moduleId?: string) => {
      const params = moduleId ? `?module=${moduleId}` : '';
      return this.request(`/chapters${params}`);
    },
    getModule: (moduleId: string) => this.request(`/modules/${moduleId}`),
    listModules: () => this.request('/modules'),
  };

  // Quiz API
  quiz = {
    listQuizzes: (moduleId?: string) => {
      const params = moduleId ? `?module_id=${moduleId}` : '';
      return this.request(`/quizzes${params}`);
    },
    getQuiz: (quizId: string) => this.request(`/quizzes/${quizId}`),
    startQuiz: (quizId: string) => this.request(`/quizzes/${quizId}/start`, { method: 'POST' }),
    submitQuiz: (quizId: string, attemptId: string, answers: Record<string, string>) =>
      this.request(`/quizzes/${quizId}/submit`, {
        method: 'POST',
        body: { attempt_id: attemptId, answers },
      }),
  };

  // Progress API
  progress = {
    getUserProgress: (userId: string) => this.request(`/progress/${userId}`),
    getStreak: (userId: string) => this.request(`/progress/${userId}/streak`),
    getAchievements: (userId: string) => this.request(`/progress/${userId}/achievements`),
    markChapterComplete: (
      userId: string,
      chapterId: string,
      completionType: string,
      timeSpentMinutes: number
    ) =>
      this.request(`/progress/${userId}/chapters/${chapterId}`, {
        method: 'PUT',
        body: {
          completion_type: completionType,
          time_spent_minutes: timeSpentMinutes,
        },
      }),
  };

  // Search API
  search = {
    searchContent: (query: string, limit?: number) => {
      const params = limit ? `?q=${encodeURIComponent(query)}&limit=${limit}` : `?q=${encodeURIComponent(query)}`;
      return this.request(`/search${params}`);
    },
  };

  // Navigation API
  navigation = {
    getNavigationContext: (chapterId: string) => this.request(`/navigation/context/${chapterId}`),
    getCourseStructure: () => this.request('/navigation/structure'),
  };
}

export const apiClient = new ApiClient(API_BASE_URL);