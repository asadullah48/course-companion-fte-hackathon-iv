# Backend API Specification: Main Application & Health Checks
## Phase 1 - Zero-Backend-LLM Architecture

**API Version:** 1.0
**Responsibility:** Application entrypoint, health checks, API documentation
**Intelligence Level:** ZERO (Deterministic Only)

---

## Constitutional Compliance

✅ **ALLOWED:** Application framework and health monitoring
✅ **ALLOWED:** API documentation generation
✅ **ALLOWED:** Basic system status reporting
❌ **FORBIDDEN:** ANY content transformation via LLM
❌ **FORBIDDEN:** Dynamic content generation
❌ **FORBIDDEN:** AI-powered diagnostics

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Purpose:** Verify application and dependent services health

**Request Example:**
```http
GET /health
```

**Response 200 (Healthy):**
```json
{
  "status": "healthy",
  "app": "course-companion",
  "version": "1.0.0",
  "timestamp": "2026-01-15T14:30:00Z",
  "environment": "production",
  "dependencies": {
    "database": {
      "status": "connected",
      "latency_ms": 12
    },
    "r2_storage": {
      "status": "accessible",
      "latency_ms": 45
    },
    "redis_cache": {
      "status": "connected",
      "latency_ms": 3
    }
  },
  "constitutional_compliance": {
    "zero_backend_llm": true,
    "content_verbatim": true,
    "deterministic_only": true
  }
}
```

**Response 503 (Unhealthy):**
```json
{
  "status": "unhealthy",
  "app": "course-companion",
  "version": "1.0.0",
  "timestamp": "2026-01-15T14:30:00Z",
  "errors": [
    {
      "service": "database",
      "error": "connection_failed",
      "message": "Unable to connect to PostgreSQL"
    }
  ],
  "dependencies": {
    "database": {
      "status": "disconnected",
      "error": "connection_failed"
    },
    "r2_storage": {
      "status": "accessible",
      "latency_ms": 45
    }
  }
}
```

---

### 2. API Documentation

**Endpoint:** `GET /docs`

**Purpose:** Interactive API documentation (Swagger UI)

**Request Example:**
```http
GET /docs
```

**Response 200:**
- Returns Swagger UI interface
- Lists all available endpoints
- Shows request/response schemas
- Provides interactive testing capabilities

---

### 3. API Schema

**Endpoint:** `GET /openapi.json`

**Purpose:** Machine-readable API schema

**Response 200:**
```json
{
  "openapi": "3.0.2",
  "info": {
    "title": "Course Companion API",
    "version": "1.0.0",
    "description": "Zero-Backend-LLM API for AI Agent Development Course"
  },
  "paths": {
    "/api/v1/chapters/{chapter_id}": {
      "get": {
        "summary": "Get Chapter Content",
        "parameters": [...],
        "responses": {...}
      }
    }
    // All other API endpoints defined here
  }
}
```

---

### 4. Root Endpoint

**Endpoint:** `GET /`

**Purpose:** Application welcome message and API discovery

**Response 200:**
```json
{
  "app": "Course Companion Backend",
  "version": "1.0.0",
  "description": "Zero-Backend-LLM API for AI Agent Development Course",
  "constitutional_compliance": {
    "zero_backend_llm": true,
    "deterministic_only": true,
    "content_verbatim": true
  },
  "api_version": "v1",
  "endpoints": {
    "health": "/health",
    "docs": "/docs",
    "api_base": "/api/v1",
    "chapters": "/api/v1/chapters",
    "quizzes": "/api/v1/quizzes",
    "progress": "/api/v1/progress",
    "search": "/api/v1/search",
    "navigation": "/api/v1/navigation"
  },
  "documentation": {
    "swagger_ui": "/docs",
    "redoc": "/redoc",
    "openapi_schema": "/openapi.json"
  }
}
```

---

### 5. ChatGPT Plugin Manifest

**Endpoint:** `GET /.well-known/ai-plugin.json`

**Purpose:** ChatGPT plugin manifest for integration

**Response 200:**
```json
{
  "schema_version": "v1",
  "name_for_human": "Course Companion",
  "name_for_model": "course_companion",
  "description_for_human": "Access AI Agent Development course content and track progress",
  "description_for_model": "Plugin for accessing AI Agent Development course materials. Provides access to chapters, quizzes, progress tracking, and navigation. All content is served verbatim from the course database without any AI processing on the backend.",
  "auth": {
    "type": "none"
  },
  "api": {
    "type": "openapi",
    "url": "https://your-domain.com/openapi.json",
    "is_user_authenticated": false
  },
  "logo_url": "https://your-domain.com/logo.png",
  "contact_email": "support@course-companion.com",
  "legal_info_url": "https://your-domain.com/legal"
}
```

---

## Implementation Requirements

### FastAPI Application Structure

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import os
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Course Companion API",
    description="Zero-Backend-LLM API for AI Agent Development Course",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Dependency: Health check helpers
async def check_database_health():
    """Check database connectivity"""
    try:
        # Perform a simple query to verify connection
        result = await db.fetchval("SELECT 1")
        return {"status": "connected", "latency_ms": 0}  # Actual latency measurement needed
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

async def check_r2_health():
    """Check R2 storage accessibility"""
    try:
        # Attempt to list objects in a known path
        response = r2_client.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=1)
        return {"status": "accessible", "latency_ms": 0}  # Actual latency measurement needed
    except Exception as e:
        return {"status": "inaccessible", "error": str(e)}

async def check_redis_health():
    """Check Redis cache connectivity"""
    try:
        # Ping Redis
        await redis.ping()
        return {"status": "connected", "latency_ms": 0}  # Actual latency measurement needed
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    timestamp: str
    environment: str
    dependencies: Dict[str, Any]
    constitutional_compliance: Dict[str, bool]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify application and dependencies status.
    
    CONSTITUTIONAL COMPLIANCE:
    - ✅ Deterministic health checks
    - ✅ No LLM processing
    - ✅ Verifiable system status
    """
    # Check all dependencies
    db_status = await check_database_health()
    r2_status = await check_r2_health()
    redis_status = await check_redis_health()
    
    # Determine overall status
    all_connected = all([
        db_status["status"] == "connected",
        r2_status["status"] == "accessible",
        redis_status["status"] == "connected"
    ])
    
    overall_status = "healthy" if all_connected else "unhealthy"
    
    response_data = {
        "status": overall_status,
        "app": "course-companion",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("APP_ENV", "development"),
        "dependencies": {
            "database": db_status,
            "r2_storage": r2_status,
            "redis_cache": redis_status
        },
        "constitutional_compliance": {
            "zero_backend_llm": True,
            "content_verbatim": True,
            "deterministic_only": True
        }
    }
    
    if not all_connected:
        errors = []
        if db_status["status"] != "connected":
            errors.append({
                "service": "database",
                "error": db_status.get("error", "connection_failed"),
                "message": "Unable to connect to PostgreSQL"
            })
        
        response_data["errors"] = errors
    
    status_code = 200 if overall_status == "healthy" else 503
    raise HTTPException(status_code=status_code, detail=response_data)

class RootResponse(BaseModel):
    app: str
    version: str
    description: str
    constitutional_compliance: Dict[str, bool]
    api_version: str
    endpoints: Dict[str, str]
    documentation: Dict[str, str]

@app.get("/", response_model=RootResponse)
async def root():
    """
    Root endpoint for API discovery.
    
    CONSTITUTIONAL COMPLIANCE:
    - ✅ Static information only
    - ✅ No dynamic content generation
    - ✅ Deterministic response
    """
    return {
        "app": "Course Companion Backend",
        "version": "1.0.0",
        "description": "Zero-Backend-LLM API for AI Agent Development Course",
        "constitutional_compliance": {
            "zero_backend_llm": True,
            "deterministic_only": True,
            "content_verbatim": True
        },
        "api_version": "v1",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api_base": "/api/v1",
            "chapters": "/api/v1/chapters",
            "quizzes": "/api/v1/quizzes",
            "progress": "/api/v1/progress",
            "search": "/api/v1/search",
            "navigation": "/api/v1/navigation"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_schema": "/openapi.json"
        }
    }

# Include all API routers
from .routers import (
    content_delivery, 
    navigation, 
    quiz_assessment, 
    progress_tracking, 
    search,
    access_control
)

app.include_router(content_delivery.router)
app.include_router(navigation.router)
app.include_router(quiz_assessment.router)
app.include_router(progress_tracking.router)
app.include_router(search.router)
app.include_router(access_control.router)

# Custom OpenAPI schema to include constitutional compliance
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Course Companion API",
        version="1.0.0",
        description="Zero-Backend-LLM API for AI Agent Development Course",
        routes=app.routes,
    )
    openapi_schema["info"]["x-constitutional-compliance"] = {
        "zero_backend_llm": True,
        "deterministic_only": True,
        "content_verbatim": True
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## Middleware & Security

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

# CORS settings (configured via environment)
cors_origins = os.getenv("CORS_ORIGINS", '["http://localhost:3000", "http://localhost:5173"]').strip('"')
origins = eval(cors_origins)  # In production, use proper JSON parsing

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose headers for client-side debugging
    expose_headers=["X-Constitutional-Compliance", "X-Content-Source"]
)
```

### Request/Response Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    """Log incoming requests for monitoring"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"process_time={process_time:.3f}s"
    )
    
    return response
```

---

## Performance Requirements

- **Response Time:** < 50ms for health checks (p95)
- **Throughput:** 1000 requests/second for root endpoint
- **Availability:** 99.9% uptime
- **Health Check Speed:** < 100ms for complete dependency check

---

## Security Requirements

1. **Authentication:** JWT Bearer tokens for protected endpoints
2. **Rate Limiting:** 1000 requests/minute per IP for public endpoints
3. **Input Validation:** All inputs validated using Pydantic models
4. **Logging:** All requests logged for security monitoring

---

## Testing Requirements

### Unit Tests
```python
def test_health_check_healthy():
    """Test health endpoint returns healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "course-companion"

def test_root_endpoint():
    """Test root endpoint returns expected structure"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "endpoints" in data
    assert "health" in data["endpoints"]

def test_cors_headers():
    """Test CORS headers are properly set"""
    response = client.get("/", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in response.headers
```

---

## Monitoring & Observability

### Metrics to Track
- Health check success/failure rates
- Response times for all endpoints
- Error rates by endpoint
- Dependency health status over time

### Health Dashboard Integration
```python
@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    # Return metrics in Prometheus format
    # Track: request counts, response times, error rates, dependency status
    pass
```

---

## Constitutional Compliance Verification

### Automated Checks
```python
def verify_constitutional_compliance():
    """Verify the application meets constitutional requirements"""
    # Check that no LLM libraries are imported
    import sys
    llm_packages = ["openai", "anthropic", "transformers", "llama_index", "langchain"]
    for package in llm_packages:
        if package in sys.modules:
            raise AssertionError(f"Constitutional violation: {package} is imported")
    
    # Check that no LLM API calls are made in the codebase
    # This would be part of the CI/CD pipeline
    pass
```

---

## Success Criteria

✅ **Zero-Backend-LLM Compliance:**
- No LLM imports in module
- No LLM API calls
- All responses deterministic

✅ **Performance:**
- Health checks < 50ms
- Root endpoint < 100ms

✅ **Functionality:**
- All endpoints implemented
- Proper error handling
- Security measures in place

✅ **Documentation:**
- OpenAPI schema generated
- Interactive documentation available
- Plugin manifest for ChatGPT

---

**Spec Version:** 1.0
**Last Updated:** January 17, 2026
**Status:** Ready for Implementation