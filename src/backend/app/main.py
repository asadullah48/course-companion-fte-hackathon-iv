"""
Course Companion Backend
Zero-Backend-LLM Architecture - FastAPI Application

CONSTITUTIONAL COMPLIANCE:
- ✅ Content served verbatim from R2
- ✅ Deterministic calculations only
- ✅ Rule-based access control
- ❌ NO LLM imports or API calls
- ❌ NO content transformation
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import api_router
from app.config import get_settings
from app.core.exceptions import CourseCompanionException
from app.database import init_db, close_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database on startup and closes on shutdown.
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Course Companion API",
    description="""
## Course Companion - AI Agent Development Course

### Constitutional Compliance (Zero-Backend-LLM)
This API serves course content **verbatim** from Cloudflare R2 storage.
- ✅ Content delivered byte-for-byte as stored
- ✅ Deterministic calculations for progress/streaks
- ✅ Rule-based access control and achievements
- ❌ **NO LLM processing** of any content
- ❌ **NO AI-generated** responses or recommendations

### Key Features
- **Content Delivery**: Chapters and modules served from R2
- **Progress Tracking**: SQL-based progress and streak calculations
- **Quiz Assessment**: Exact-match grading (deterministic)
- **Achievement System**: Rule-based unlocking
- **Access Control**: Tier-based content gating

### Authentication
All endpoints require JWT Bearer token authentication.
Free users get access to Module 1 (Chapters 1-3).
Premium/Pro/Team users get full course access.

### ChatGPT Integration
This API is designed to work as a ChatGPT App backend.
All LLM intelligence is provided by ChatGPT (user's subscription).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware for ChatGPT App integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(CourseCompanionException)
async def course_companion_exception_handler(
    request: Request, exc: CourseCompanionException
):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format."""
    detail = exc.detail
    if isinstance(detail, dict):
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": str(detail)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": str(exc),
                "type": type(exc).__name__,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred",
        },
    )


# Include API router
app.include_router(api_router, prefix="/api")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status of the application
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
        "environment": settings.app_env,
        "constitutional_compliance": {
            "zero_backend_llm": True,
            "content_verbatim": True,
            "deterministic_only": True,
        },
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Course Companion API",
        "version": "1.0.0",
        "description": "AI Agent Development Course - Zero-Backend-LLM Architecture",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "chatgpt_manifest": "/.well-known/ai-plugin.json",
    }


# ChatGPT App plugin manifest location
@app.get("/.well-known/ai-plugin.json", tags=["ChatGPT"])
async def get_ai_plugin_manifest():
    """
    ChatGPT App plugin manifest.

    Returns:
        AI plugin manifest for ChatGPT integration following OpenAI schema.
    """
    base_url = settings.api_base_url.rstrip("/")

    return {
        "schema_version": "v1",
        "name_for_human": "AI Agent Development Tutor",
        "name_for_model": "course_companion",
        "description_for_human": (
            "Your personal tutor for mastering AI Agent development. "
            "Learn to build autonomous agents using Claude Agent SDK, "
            "MCP integration, and production deployment patterns."
        ),
        "description_for_model": (
            "This plugin provides access to an AI Agent Development course. "
            "Use it to retrieve course content, track user progress, administer quizzes, "
            "and check achievements. Content is served verbatim from storage - apply your "
            "intelligence as ChatGPT to explain, summarize, teach, and guide the student "
            "through the material. Available skills: Concept Explainer (explain topics using "
            "course content), Quiz Master (administer quizzes and provide feedback), "
            "Socratic Tutor (guide without giving answers), Progress Motivator (encourage "
            "with progress/streak/achievements)."
        ),
        "auth": {
            "type": "user_http",
            "authorization_type": "bearer",
        },
        "api": {
            "type": "openapi",
            "url": f"{base_url}/openapi.json",
        },
        "logo_url": f"{base_url}/static/logo.png",
        "contact_email": "support@coursecompanion.ai",
        "legal_info_url": "https://coursecompanion.ai/legal",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
