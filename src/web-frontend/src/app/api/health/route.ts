// src/app/api/health/route.ts
export async function GET() {
  return new Response(
    JSON.stringify({ 
      status: 'healthy', 
      service: 'web-frontend', 
      timestamp: new Date().toISOString() 
    }),
    { 
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      }
    }
  );
}