# Backend API Specification: Content Delivery
## Phase 1 - Zero-Backend-LLM Architecture

**API Version:** 1.0  
**Responsibility:** Serve course content verbatim from storage  
**Intelligence Level:** ZERO (Deterministic Only)

---

## Constitutional Compliance

✅ **ALLOWED:** Serve content byte-for-byte as stored  
❌ **FORBIDDEN:** ANY content transformation via LLM  
❌ **FORBIDDEN:** Summarization, paraphrasing, enhancement  

---

## API Endpoints

### 1. Get Chapter Content

**Endpoint:** `GET /api/v1/chapters/{chapter_id}`

**Purpose:** Retrieve chapter content verbatim from Cloudflare R2

**Path Parameters:**
- `chapter_id` (string, required): Unique chapter identifier (e.g., "ch1-intro-to-agents")

**Query Parameters:**
- `format` (string, optional): Response format
  - `markdown` (default): Return raw markdown
  - `json`: Return structured JSON with metadata
  - `html`: Return pre-rendered HTML (if available)

**Request Example:**
```http
GET /api/v1/chapters/ch1-intro-to-agents?format=markdown
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "chapter_id": "ch1-intro-to-agents",
  "title": "Introduction to AI Agents",
  "content": "# Introduction to AI Agents\n\nAI Agents are...",
  "content_type": "markdown",
  "word_count": 1250,
  "estimated_read_time": 5,
  "metadata": {
    "module": 1,
    "order": 1,
    "tags": ["fundamentals", "intro"],
    "difficulty": "beginner"
  },
  "created_at": "2026-01-10T00:00:00Z",
  "updated_at": "2026-01-12T15:30:00Z"
}
```

**Response 404 (Not Found):**
```json
{
  "error": "chapter_not_found",
  "message": "Chapter 'ch1-intro-to-agents' does not exist",
  "chapter_id": "ch1-intro-to-agents"
}
```

**Response 403 (Access Denied):**
```json
{
  "error": "access_denied",
  "message": "Premium subscription required for this chapter",
  "chapter_id": "ch1-intro-to-agents",
  "required_tier": "premium",
  "upgrade_url": "/api/v1/pricing"
}
```

---

### 2. List All Chapters

**Endpoint:** `GET /api/v1/chapters`

**Purpose:** Get chapter list with metadata (NO content)

**Query Parameters:**
- `module` (integer, optional): Filter by module number
- `include_locked` (boolean, optional): Include chapters user doesn't have access to
  - Default: `false`
- `sort` (string, optional): Sort order
  - `order` (default): By chapter order
  - `recent`: By last updated
  - `difficulty`: By difficulty level

**Request Example:**
```http
GET /api/v1/chapters?module=1&include_locked=true
Authorization: Bearer <user_token>
```

**Response 200:**
```json
{
  "chapters": [
    {
      "chapter_id": "ch1-intro-to-agents",
      "title": "Introduction to AI Agents",
      "module": 1,
      "order": 1,
      "difficulty": "beginner",
      "word_count": 1250,
      "estimated_read_time": 5,
      "is_locked": false,
      "completed": true,
      "completed_at": "2026-01-14T10:30:00Z"
    },
    {
      "chapter_id": "ch2-claude-agent-sdk",
      "title": "Claude Agent SDK Fundamentals",
      "module": 1,
      "order": 2,
      "difficulty": "beginner",
      "word_count": 2100,
      "estimated_read_time": 8,
      "is_locked": false,
      "completed": false,
      "completed_at": null
    },
    {
      "chapter_id": "ch4-advanced-workflows",
      "title": "Advanced Agentic Workflows",
      "module": 2,
      "order": 4,
      "difficulty": "advanced",
      "word_count": 3500,
      "estimated_read_time": 14,
      "is_locked": true,
      "required_tier": "premium",
      "completed": false,
      "completed_at": null
    }
  ],
  "total_chapters": 18,
  "completed_count": 1,
  "locked_count": 12
}
```

---

### 3. Get Chapter Media Assets

**Endpoint:** `GET /api/v1/chapters/{chapter_id}/media`

**Purpose:** List media assets (images, diagrams) for a chapter

**Response 200:**
```json
{
  "chapter_id": "ch1-intro-to-agents",
  "media": [
    {
      "asset_id": "img-agent-architecture",
      "type": "image",
      "url": "https://r2.example.com/media/ch1/agent-architecture.png",
      "alt_text": "Agent Factory Architecture Diagram",
      "caption": "The 8-layer Agent Factory architecture",
      "size_bytes": 125840,
      "width": 1200,
      "height": 800
    },
    {
      "asset_id": "vid-demo-mcp",
      "type": "video",
      "url": "https://r2.example.com/media/ch1/mcp-demo.mp4",
      "thumbnail": "https://r2.example.com/media/ch1/mcp-demo-thumb.jpg",
      "duration_seconds": 180,
      "size_bytes": 8450000
    }
  ]
}
```

---

### 4. Get Module Overview

**Endpoint:** `GET /api/v1/modules/{module_id}`

**Purpose:** Get module metadata and chapter list

**Response 200:**
```json
{
  "module_id": 1,
  "title": "Foundations of AI Agents",
  "description": "Learn the core concepts of AI Agents and the Agent Factory Architecture",
  "order": 1,
  "chapters": [
    {
      "chapter_id": "ch1-intro-to-agents",
      "title": "Introduction to AI Agents",
      "order": 1
    },
    {
      "chapter_id": "ch2-claude-agent-sdk",
      "title": "Claude Agent SDK Fundamentals",
      "order": 2
    }
  ],
  "total_chapters": 3,
  "estimated_duration_minutes": 45,
  "difficulty": "beginner",
  "prerequisites": []
}
```

---

## Implementation Requirements

### Storage Architecture
```python
# R2 Bucket Structure
r2://course-content/
├── chapters/
│   ├── ch1-intro-to-agents.md
│   ├── ch2-claude-agent-sdk.md
│   └── ...
├── media/
│   ├── ch1/
│   │   ├── agent-architecture.png
│   │   └── mcp-demo.mp4
│   └── ch2/
│       └── ...
└── metadata/
    ├── chapters.json
    └── modules.json
```

### FastAPI Implementation Pattern
```python
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Literal
import boto3
from datetime import datetime

router = APIRouter(prefix="/api/v1")

# R2 Client (S3-compatible)
r2_client = boto3.client(
    's3',
    endpoint_url=os.getenv('R2_ENDPOINT'),
    aws_access_key_id=os.getenv('R2_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('R2_SECRET_KEY')
)

BUCKET_NAME = "course-content"

@router.get("/chapters/{chapter_id}")
async def get_chapter(
    chapter_id: str,
    format: Literal["markdown", "json", "html"] = "markdown",
    user: dict = Depends(get_current_user)
):
    """
    Serve chapter content verbatim from R2.
    
    CONSTITUTIONAL COMPLIANCE:
    - ✅ Content served byte-for-byte as stored
    - ❌ NO LLM processing
    - ❌ NO summarization
    - ❌ NO content transformation
    """
    
    # 1. Check access control (separate API)
    access = await check_chapter_access(user.id, chapter_id)
    if not access["allowed"]:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "access_denied",
                "message": access["reason"],
                "required_tier": access.get("required_tier"),
                "upgrade_url": "/api/v1/pricing"
            }
        )
    
    # 2. Fetch content from R2 (verbatim)
    try:
        obj = r2_client.get_object(
            Bucket=BUCKET_NAME,
            Key=f"chapters/{chapter_id}.md"
        )
        content = obj['Body'].read().decode('utf-8')
    except r2_client.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "chapter_not_found",
                "message": f"Chapter '{chapter_id}' does not exist",
                "chapter_id": chapter_id
            }
        )
    
    # 3. Get metadata (from separate metadata file or database)
    metadata = await get_chapter_metadata(chapter_id)
    
    # 4. Calculate derived fields (deterministic only)
    word_count = len(content.split())
    estimated_read_time = max(1, word_count // 250)  # 250 words/min
    
    # 5. Return response
    return {
        "chapter_id": chapter_id,
        "title": metadata["title"],
        "content": content,  # ✅ Verbatim, no LLM processing
        "content_type": format,
        "word_count": word_count,
        "estimated_read_time": estimated_read_time,
        "metadata": metadata,
        "created_at": metadata["created_at"],
        "updated_at": metadata["updated_at"]
    }
```

---

## Caching Strategy

### Edge Caching (Cloudflare)
```python
@router.get("/chapters/{chapter_id}")
@cache(expire=3600)  # 1 hour cache
async def get_chapter(...):
    # Content rarely changes, aggressive caching is safe
    pass
```

### Cache Headers
```http
Cache-Control: public, max-age=3600
ETag: "abc123-ch1-intro-to-agents"
Last-Modified: Mon, 12 Jan 2026 15:30:00 GMT
```

---

## Performance Requirements

- **Response Time:** < 100ms (p95)
- **Throughput:** 1000 requests/second
- **Availability:** 99.9% uptime
- **Cache Hit Rate:** > 95%

---

## Security Requirements

1. **Authentication:** JWT Bearer tokens required
2. **Authorization:** Check user tier before content delivery
3. **Rate Limiting:** 100 requests/minute per user
4. **Content Validation:** Ensure chapter_id doesn't contain path traversal

---

## Testing Requirements

### Unit Tests
```python
def test_get_chapter_success():
    """Test successful chapter retrieval"""
    response = client.get("/api/v1/chapters/ch1-intro-to-agents")
    assert response.status_code == 200
    assert "content" in response.json()
    assert response.json()["chapter_id"] == "ch1-intro-to-agents"

def test_get_chapter_not_found():
    """Test 404 for non-existent chapter"""
    response = client.get("/api/v1/chapters/invalid-chapter")
    assert response.status_code == 404

def test_get_chapter_access_denied():
    """Test 403 for locked chapter"""
    # Use free tier user token
    response = client.get(
        "/api/v1/chapters/ch10-advanced",
        headers={"Authorization": f"Bearer {free_tier_token}"}
    )
    assert response.status_code == 403
```

### Integration Tests
- R2 connection verification
- Metadata consistency checks
- Cache behavior validation

---

## Monitoring & Observability

### Metrics to Track
- Request count by chapter_id
- Response time percentiles
- Cache hit rate
- Error rate by type (404, 403, 500)
- R2 read latency

### Logging
```python
logger.info(
    "chapter_delivered",
    chapter_id=chapter_id,
    user_id=user.id,
    format=format,
    cache_hit=cache_hit,
    duration_ms=duration
)
```

---

## Cost Analysis

### Per Request Cost (10K users, 50 chapters/user/month)
```
R2 Operations:
- Class A (GET): $0.36 per million reads
- 500K reads/month = $0.18

R2 Storage:
- 500MB course content = $0.0075/month

Cache Savings:
- 95% cache hit rate = 5% actual R2 reads
- Effective cost: ~$0.01/month

Total: ~$0.02/month for content delivery
```

---

## Success Criteria

✅ **Zero-Backend-LLM Compliance:**
- No LLM imports in module
- No LLM API calls
- Content served verbatim

✅ **Performance:**
- P95 latency < 100ms
- Cache hit rate > 95%

✅ **Functionality:**
- All endpoints implemented
- Proper error handling
- Access control enforced

---

**Spec Version:** 1.0  
**Last Updated:** January 15, 2026  
**Status:** Ready for Implementation
