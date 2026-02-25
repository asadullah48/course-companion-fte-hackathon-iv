// src/lib/auth-server.ts
// Server-side auth helper for API routes (mock implementation)

export async function getAuth() {
  // In production, this would validate JWT/session tokens
  // For demo purposes, return a mock authenticated user
  return {
    user: {
      id: 'user-123',
      email: 'demo@example.com',
      tier: 'free' as const,
    },
  };
}
