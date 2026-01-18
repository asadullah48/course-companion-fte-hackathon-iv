# Backend API Specification: Navigation
## Phase 1 - Zero-Backend-LLM Architecture

**API Version:** 1.0  
**Responsibility:** Deterministic chapter navigation and sequencing  
**Intelligence Level:** ZERO (Rule-Based Only)

---

## Constitutional Compliance

✅ **ALLOWED:** Rule-based next/previous chapter calculation  
✅ **ALLOWED:** Conditional navigation based on completion status  
❌ **FORBIDDEN:** LLM-based "personalized path recommendations"  
❌ **FORBIDDEN:** AI-driven "optimal learning sequence"

---

## Navigation Rules (Hardcoded)

### Course Structure
```
Module 1: Foundations of AI Agents
├── ch1-intro-to-agents
├── ch2-claude-agent-sdk
└── ch3-mcp-integration

Module 2: Agent Skills Development
├── ch4-skill-md-structure
├── ch5-procedural-knowledge
└── ch6-runtime-skills

Module 3: Agentic Workflows
├── ch7-orchestration-patterns
├── ch8-multi-agent-systems
└── ch9-production-deployment

(Total: 9 chapters for Phase 1 MVP)
```

### Navigation Logic
1. **Linear Progression:** Users must complete chapters in order
2. **Module Boundaries:** Cannot skip to next module until current module complete
3. **Freemium Gate:** Free users limited to first 3 chapters
4. **Prerequisites:** Advanced chapters require completion of fundamentals

---

## API Endpoints

### 1. Get Next Chapter

**Endpoint:** `GET /api/v1/chapters/{chapter_id}/next`

**Purpose:** Calculate next chapter based on completion and access rules

**Path Parameters:**
- `chapter_id` (string, required): Current chapter ID

**Query Parameters:**
- `skip_locked` (boolean, optional): Skip locked chapters in sequence
  - Default: `false`

**Request Example:**
```http
GET /api/v1/chapters/ch1-intro-to-agents/next
Authorization: Bearer <user_token>
```

**Response 200 (Next Available):**
```json
{
  "current_chapter": {
    "chapter_id": "ch1-intro-to-agents",
    "title": "Introduction to AI Agents",
    "completed": true,
    "completed_at": "2026-01-14T10:30:00Z"
  },
  "next_chapter": {
    "chapter_id": "ch2-claude-agent-sdk",
    "title": "Claude Agent SDK Fundamentals",
    "module": 1,
    "order": 2,
    "is_locked": false,
    "url": "/api/v1/chapters/ch2-claude-agent-sdk"
  },
  "navigation_allowed": true,
  "reason": "completed_current"
}
```

**Response 200 (Must Complete Current):**
```json
{
  "current_chapter": {
    "chapter_id": "ch1-intro-to-agents",
    "title": "Introduction to AI Agents",
    "completed": false,
    "completed_at": null
  },
  "next_chapter": null,
  "navigation_allowed": false,
  "reason": "complete_current_first",
  "message": "Please complete the current chapter before proceeding"
}
```

**Response 200 (Access Denied):**
```json
{
  "current_chapter": {
    "chapter_id": "ch3-mcp-integration",
    "title": "MCP Integration",
    "completed": true,
    "completed_at": "2026-01-14T12:00:00Z"
  },
  "next_chapter": {
    "chapter_id": "ch4-skill-md-structure",
    "title": "SKILL.md Structure",
    "module": 2,
    "order": 4,
    "is_locked": true,
    "required_tier": "premium"
  },
  "navigation_allowed": false,
  "reason": "premium_required",
  "message": "Upgrade to Premium to access Module 2",
  "upgrade_url": "/api/v1/pricing"
}
```

**Response 200 (Course Complete):**
```json
{
  "current_chapter": {
    "chapter_id": "ch9-production-deployment",
    "title": "Production Deployment",
    "completed": true,
    "completed_at": "2026-01-15T18:00:00Z"
  },
  "next_chapter": null,
  "navigation_allowed": false,
  "reason": "course_complete",
  "message": "Congratulations! You've completed the entire course.",
  "certificate_url": "/api/v1/certificates/generate"
}
```

---

### 2. Get Previous Chapter

**Endpoint:** `GET /api/v1/chapters/{chapter_id}/previous`

**Purpose:** Get previous chapter (always allowed, no completion check)

**Response 200:**
```json
{
  "current_chapter": {
    "chapter_id": "ch2-claude-agent-sdk",
    "title": "Claude Agent SDK Fundamentals"
  },
  "previous_chapter": {
    "chapter_id": "ch1-intro-to-agents",
    "title": "Introduction to AI Agents",
    "module": 1,
    "order": 1,
    "url": "/api/v1/chapters/ch1-intro-to-agents"
  },
  "navigation_allowed": true
}
```

**Response 200 (First Chapter):**
```json
{
  "current_chapter": {
    "chapter_id": "ch1-intro-to-agents",
    "title": "Introduction to AI Agents"
  },
  "previous_chapter": null,
  "navigation_allowed": false,
  "reason": "first_chapter"
}
```

---

### 3. Get Chapter Sequence

**Endpoint:** `GET /api/v1/navigation/sequence`

**Purpose:** Get full chapter sequence with progress overlay

**Query Parameters:**
- `module` (integer, optional): Filter by module

**Response 200:**
```json
{
  "sequence": [
    {
      "chapter_id": "ch1-intro-to-agents",
      "title": "Introduction to AI Agents",
      "module": 1,
      "order": 1,
      "is_locked": false,
      "completed": true,
      "completed_at": "2026-01-14T10:30:00Z",
      "can_access": true
    },
    {
      "chapter_id": "ch2-claude-agent-sdk",
      "title": "Claude Agent SDK Fundamentals",
      "module": 1,
      "order": 2,
      "is_locked": false,
      "completed": false,
      "completed_at": null,
      "can_access": true,
      "is_current": true
    },
    {
      "chapter_id": "ch3-mcp-integration",
      "title": "MCP Integration",
      "module": 1,
      "order": 3,
      "is_locked": false,
      "completed": false,
      "completed_at": null,
      "can_access": false,
      "blocked_reason": "complete_previous_first"
    },
    {
      "chapter_id": "ch4-skill-md-structure",
      "title": "SKILL.md Structure",
      "module": 2,
      "order": 4,
      "is_locked": true,
      "completed": false,
      "completed_at": null,
      "can_access": false,
      "blocked_reason": "premium_required",
      "required_tier": "premium"
    }
  ],
  "total_chapters": 9,
  "completed_count": 1,
  "current_chapter": "ch2-claude-agent-sdk",
  "next_available": "ch2-claude-agent-sdk",
  "progress_percentage": 11
}
```

---

### 4. Get Recommended Next Action

**Endpoint:** `GET /api/v1/navigation/recommend`

**Purpose:** Suggest next action (continue, review, quiz)

**Response 200:**
```json
{
  "recommendation": "continue",
  "action": {
    "type": "continue_chapter",
    "chapter_id": "ch2-claude-agent-sdk",
    "title": "Claude Agent SDK Fundamentals",
    "url": "/api/v1/chapters/ch2-claude-agent-sdk",
    "reason": "in_progress"
  },
  "alternatives": [
    {
      "type": "review_chapter",
      "chapter_id": "ch1-intro-to-agents",
      "title": "Introduction to AI Agents",
      "reason": "recently_completed"
    },
    {
      "type": "take_quiz",
      "quiz_id": "quiz-module-1",
      "title": "Module 1 Assessment",
      "reason": "module_complete"
    }
  ]
}
```

---

## Implementation Requirements

### Navigation State Machine
```python
from enum import Enum
from typing import Optional, Dict, List
from pydantic import BaseModel

class NavigationReason(str, Enum):
    COMPLETED_CURRENT = "completed_current"
    COMPLETE_CURRENT_FIRST = "complete_current_first"
    PREMIUM_REQUIRED = "premium_required"
    COURSE_COMPLETE = "course_complete"
    FIRST_CHAPTER = "first_chapter"
    MODULE_LOCKED = "module_locked"

# Hardcoded chapter sequence (immutable)
CHAPTER_SEQUENCE = [
    {"id": "ch1-intro-to-agents", "module": 1, "order": 1, "tier": "free"},
    {"id": "ch2-claude-agent-sdk", "module": 1, "order": 2, "tier": "free"},
    {"id": "ch3-mcp-integration", "module": 1, "order": 3, "tier": "free"},
    {"id": "ch4-skill-md-structure", "module": 2, "order": 4, "tier": "premium"},
    {"id": "ch5-procedural-knowledge", "module": 2, "order": 5, "tier": "premium"},
    {"id": "ch6-runtime-skills", "module": 2, "order": 6, "tier": "premium"},
    {"id": "ch7-orchestration-patterns", "module": 3, "order": 7, "tier": "premium"},
    {"id": "ch8-multi-agent-systems", "module": 3, "order": 8, "tier": "premium"},
    {"id": "ch9-production-deployment", "module": 3, "order": 9, "tier": "premium"},
]

class NavigationService:
    """
    Deterministic navigation logic.
    
    CONSTITUTIONAL COMPLIANCE:
    - ✅ Rule-based next/previous calculation
    - ❌ NO LLM-based recommendations
    - ❌ NO AI-driven personalization
    """
    
    @staticmethod
    def get_chapter_index(chapter_id: str) -> int:
        """Find chapter position in sequence"""
        for i, ch in enumerate(CHAPTER_SEQUENCE):
            if ch["id"] == chapter_id:
                return i
        raise ValueError(f"Unknown chapter: {chapter_id}")
    
    @staticmethod
    async def get_next_chapter(
        chapter_id: str,
        user_id: str,
        user_tier: str
    ) -> Dict:
        """
        Calculate next chapter deterministically.
        
        Rules:
        1. Must complete current chapter first
        2. Must have access to next chapter (tier check)
        3. Cannot skip chapters
        """
        current_index = NavigationService.get_chapter_index(chapter_id)
        
        # Check if current chapter is completed
        completed = await db.is_chapter_completed(user_id, chapter_id)
        
        if not completed:
            return {
                "next_chapter": None,
                "navigation_allowed": False,
                "reason": NavigationReason.COMPLETE_CURRENT_FIRST
            }
        
        # Check if course is complete
        if current_index == len(CHAPTER_SEQUENCE) - 1:
            return {
                "next_chapter": None,
                "navigation_allowed": False,
                "reason": NavigationReason.COURSE_COMPLETE
            }
        
        # Get next chapter
        next_index = current_index + 1
        next_chapter = CHAPTER_SEQUENCE[next_index]
        
        # Check tier access
        if next_chapter["tier"] == "premium" and user_tier == "free":
            return {
                "next_chapter": {
                    "chapter_id": next_chapter["id"],
                    "is_locked": True,
                    "required_tier": "premium"
                },
                "navigation_allowed": False,
                "reason": NavigationReason.PREMIUM_REQUIRED
            }
        
        return {
            "next_chapter": {
                "chapter_id": next_chapter["id"],
                "module": next_chapter["module"],
                "order": next_chapter["order"],
                "is_locked": False
            },
            "navigation_allowed": True,
            "reason": NavigationReason.COMPLETED_CURRENT
        }
```

---

## FastAPI Route Implementation
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/v1")

@router.get("/chapters/{chapter_id}/next")
async def get_next_chapter(
    chapter_id: str,
    user: dict = Depends(get_current_user)
):
    """Get next chapter in sequence"""
    
    # Get current chapter metadata
    current = await get_chapter_metadata(chapter_id)
    
    # Calculate next chapter using deterministic logic
    nav_service = NavigationService()
    result = await nav_service.get_next_chapter(
        chapter_id=chapter_id,
        user_id=user.id,
        user_tier=user.subscription_tier
    )
    
    return {
        "current_chapter": {
            "chapter_id": chapter_id,
            "title": current["title"],
            "completed": await db.is_chapter_completed(user.id, chapter_id),
            "completed_at": await db.get_completion_time(user.id, chapter_id)
        },
        **result
    }

@router.get("/chapters/{chapter_id}/previous")
async def get_previous_chapter(chapter_id: str):
    """Get previous chapter (always allowed)"""
    
    current_index = NavigationService.get_chapter_index(chapter_id)
    
    if current_index == 0:
        return {
            "current_chapter": {"chapter_id": chapter_id},
            "previous_chapter": None,
            "navigation_allowed": False,
            "reason": "first_chapter"
        }
    
    prev_chapter = CHAPTER_SEQUENCE[current_index - 1]
    
    return {
        "current_chapter": {"chapter_id": chapter_id},
        "previous_chapter": {
            "chapter_id": prev_chapter["id"],
            "module": prev_chapter["module"],
            "order": prev_chapter["order"],
            "url": f"/api/v1/chapters/{prev_chapter['id']}"
        },
        "navigation_allowed": True
    }
```

---

## Performance Requirements

- **Response Time:** < 50ms (all navigation endpoints)
- **Cache:** Navigation rules cached in-memory
- **Database Queries:** Single query for completion check

---

## Testing Requirements
```python
def test_next_chapter_completed():
    """Test next chapter when current is completed"""
    # Mark ch1 as completed
    db.mark_completed(user_id="test_user", chapter_id="ch1-intro-to-agents")
    
    response = client.get("/api/v1/chapters/ch1-intro-to-agents/next")
    assert response.status_code == 200
    assert response.json()["navigation_allowed"] == True
    assert response.json()["next_chapter"]["chapter_id"] == "ch2-claude-agent-sdk"

def test_next_chapter_not_completed():
    """Test next chapter when current not completed"""
    response = client.get("/api/v1/chapters/ch1-intro-to-agents/next")
    assert response.status_code == 200
    assert response.json()["navigation_allowed"] == False
    assert response.json()["reason"] == "complete_current_first"

def test_next_chapter_premium_required():
    """Test premium gate"""
    # Free tier user, completed ch3
    db.mark_completed(user_id="free_user", chapter_id="ch3-mcp-integration")
    
    response = client.get(
        "/api/v1/chapters/ch3-mcp-integration/next",
        headers={"Authorization": f"Bearer {free_tier_token}"}
    )
    assert response.status_code == 200
    assert response.json()["navigation_allowed"] == False
    assert response.json()["reason"] == "premium_required"

def test_course_complete():
    """Test last chapter next navigation"""
    response = client.get("/api/v1/chapters/ch9-production-deployment/next")
    assert response.json()["reason"] == "course_complete"
```

---

## Success Criteria

✅ **Constitutional Compliance:**
- No LLM-based navigation
- Pure rule-based logic

✅ **Functionality:**
- Linear progression enforced
- Premium gates working
- Previous navigation always available

✅ **Performance:**
- Sub-50ms response time
- In-memory rule caching

---

**Spec Version:** 1.0  
**Last Updated:** January 15, 2026  
**Status:** Ready for Implementation
