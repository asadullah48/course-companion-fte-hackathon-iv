# INTEGRATION SPECIFICATION: Course Companion System
## Phase 1 - Zero-Backend-LLM Architecture

**Version:** 1.0
**Purpose:** Define how all components work together in the complete system
**Constitutional Compliance:** Zero-Backend-LLM Architecture

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERACTION                         │
├─────────────────────────────────────────────────────────────┤
│  ChatGPT App (Intelligence Layer)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Concept Explainer Skill                         │   │
│  │ • Quiz Master Skill                               │   │
│  │ • Socratic Tutor Skill                          │   │
│  │ • Progress Motivator Skill                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                MODEL CONTEXT PROTOCOL (MCP)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Course Companion MCP Server                       │   │
│  │ • Proxies requests to backend API                  │   │
│  │ • No LLM processing (constitutional)            │   │
│  │ • Translates MCP to REST calls                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                 BACKEND API (Deterministic)                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ FastAPI Application                               │   │
│  │ • Content Delivery (verbatim)                    │   │
│  │ • Quiz Assessment (exact matching)              │   │
│  │ • Progress Tracking (database ops)              │   │
│  │ • Search (keyword/pre-computed)                 │   │
│  │ • Navigation (rule-based)                       │   │
│  │ • Access Control (tier-based)                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA STORAGE LAYER                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Cloudflare R2 (Content)                           │   │
│  │ • Course chapters (markdown)                      │   │
│  │ • Media assets (images, videos)                  │   │
│  │ • Pre-computed embeddings (if needed)           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PostgreSQL Database                              │   │
│  │ • User accounts & progress                       │   │
│  │ • Quiz questions & answer keys                   │   │
│  │ • Chapter metadata & navigation                  │   │
│  │ • Achievements & streaks                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Integration Flows

### Flow 1: Concept Explanation Request

**Trigger:** User asks "Explain MCP to me"

**System Flow:**
```
1. ChatGPT App receives: "Explain MCP to me"
2. Skill Detection: Matches "explain" trigger → Concept Explainer skill
3. MCP Server receives: CallTool("get_chapter", {"chapter_id": "ch3-mcp-fundamentals"})
4. Backend API: GET /api/v1/chapters/ch3-mcp-fundamentals
5. Backend retrieves from R2: ch3-mcp-fundamentals.md (verbatim)
6. Backend returns: {"content": "...MCP chapter content..."}
7. MCP Server forwards response to ChatGPT
8. Concept Explainer skill uses content to generate explanation
9. ChatGPT responds to user with explanation
```

**Constitutional Compliance Check:**
- ✅ Content served verbatim from R2 (no LLM processing)
- ✅ MCP server only acts as proxy (no LLM processing)
- ✅ All intelligence in ChatGPT (user's subscription)

### Flow 2: Quiz Session

**Trigger:** User asks "Quiz me on Chapter 1"

**System Flow:**
```
1. ChatGPT App receives: "Quiz me on Chapter 1"
2. Skill Detection: Matches "quiz" trigger → Quiz Master skill
3. MCP Server: CallTool("list_quizzes", {"chapter_id": "ch1-intro-to-agents"})
4. Backend API: GET /api/v1/quizzes?chapter_id=ch1-intro-to-agents
5. Backend returns: Available quizzes for Chapter 1
6. User selects quiz
7. MCP Server: CallTool("get_quiz", {"quiz_id": "quiz-ch1-intro-001"})
8. Backend API: GET /api/v1/quizzes/quiz-ch1-intro-001
9. Backend returns: Questions (without correct answers)
10. Quiz Master skill presents questions one at a time
11. User answers questions
12. MCP Server: CallTool("submit_quiz", {"quiz_id": "...", "answers": [...]})
13. Backend API: POST /api/v1/quizzes/quiz-ch1-intro-001/submit
14. Backend grades using exact answer key matching
15. Backend returns: Results with explanations
16. Quiz Master skill presents results to user
```

**Constitutional Compliance Check:**
- ✅ Quiz grading uses exact answer key matching (no LLM)
- ✅ Explanations from pre-stored content (no LLM generation)
- ✅ MCP server only acts as proxy (no LLM processing)

### Flow 3: Progress Tracking

**Trigger:** User completes a chapter

**System Flow:**
```
1. User indicates chapter completion
2. ChatGPT App: MCP Server → CallTool("mark_chapter_complete", {...})
3. Backend API: PUT /api/v1/progress/{user_id}/chapters/{chapter_id}
4. Backend updates PostgreSQL: Sets completion timestamp
5. Backend calculates streak using deterministic algorithm
6. Backend returns: Success + streak information
7. MCP Server forwards to ChatGPT
8. Progress Motivator skill creates celebratory response
9. User sees progress update
```

**Constitutional Compliance Check:**
- ✅ Progress tracking uses database operations (no LLM)
- ✅ Streak calculation is deterministic (no LLM)
- ✅ MCP server only acts as proxy (no LLM processing)

---

## API Integration Points

### MCP Server Integration

**Tool Definitions (in MCP server):**
```python
# Content Delivery Tools
"get_chapter": {
    "name": "get_chapter",
    "description": "Get chapter content for explaining concepts",
    "inputSchema": {"chapter_id": "string"}
}
"list_chapters": {
    "name": "list_chapters", 
    "description": "List all available chapters",
    "inputSchema": {"module_id": "string"}
}

# Quiz Tools
"start_quiz": {
    "name": "start_quiz",
    "description": "Start a new quiz attempt",
    "inputSchema": {"quiz_id": "string"}
}
"submit_quiz": {
    "name": "submit_quiz", 
    "description": "Submit quiz answers and get results",
    "inputSchema": {"quiz_id": "string", "attempt_id": "string", "answers": "object"}
}

# Progress Tools  
"get_progress": {
    "name": "get_progress",
    "description": "Get user's overall progress",
    "inputSchema": {"user_id": "string"}
}
"mark_chapter_complete": {
    "name": "mark_chapter_complete",
    "description": "Mark a chapter as completed",
    "inputSchema": {"user_id": "string", "chapter_id": "string"}
}
```

**API Mapping (in MCP server):**
```python
# Example mapping for get_chapter
if name == "get_chapter":
    return await api_request("GET", f"/chapters/{args['chapter_id']}")

# Example mapping for submit_quiz  
elif name == "submit_quiz":
    return await api_request(
        "POST", 
        f"/quizzes/{args['quiz_id']}/submit",
        params={"attempt_id": args["attempt_id"]},
        json={"answers": args["answers"]}
    )
```

### Backend API Endpoints

**Content Delivery Endpoints:**
```
GET /api/v1/chapters/{chapter_id}     → Fetch from R2 (verbatim)
GET /api/v1/chapters                  → List chapters from DB
GET /api/v1/modules/{module_id}       → Fetch module from DB
GET /api/v1/modules                   → List modules from DB
GET /api/v1/chapters/{chapter_id}/media → Fetch media assets from R2
```

**Quiz Endpoints:**
```
GET /api/v1/quizzes                   → List available quizzes
GET /api/v1/quizzes/{quiz_id}         → Get quiz questions (no answers)
POST /api/v1/quizzes/{quiz_id}/submit → Grade using answer key matching
GET /api/v1/quizzes/{quiz_id}/results/{attempt_id} → Get results from DB
```

**Progress Endpoints:**
```
GET /api/v1/progress/{user_id}        → Get progress from DB
GET /api/v1/progress/{user_id}/streak → Calculate streak from DB
GET /api/v1/progress/{user_id}/achievements → Get achievements from DB
PUT /api/v1/progress/{user_id}/chapters/{chapter_id} → Update completion in DB
POST /api/v1/progress/{user_id}/time  → Log time in DB
```

**Search & Navigation Endpoints:**
```
GET /api/v1/search                    → Keyword search in DB
GET /api/v1/navigation/context/{chapter_id} → Get prev/next from DB
GET /api/v1/navigation/structure      → Get full structure from DB
```

---

## Authentication & Authorization Flow

### JWT Token Flow
```
1. User authenticates with external identity provider
2. Backend generates JWT with user_id and tier
3. JWT sent to ChatGPT App via MCP
4. MCP server adds JWT to all API requests
5. Backend validates JWT on each request
6. Backend checks user tier for access control
```

### Access Control Integration
```
Content Access:
- Free tier: Chapters 1-3 only
- Premium: All chapters
- API validates tier before serving content

Quiz Access:
- Free tier: Module 1 quizzes only  
- Premium: All quizzes
- API validates tier before allowing quiz access

Feature Access:
- Streak freezes: Premium+ only
- Certificate: Premium+ only
- API validates tier before enabling features
```

---

## Error Handling Integration

### Error Propagation Flow
```
1. Backend encounters error → Formats as structured JSON
2. MCP server receives error → Passes through unchanged
3. ChatGPT App receives error → Skill handles appropriately
4. User sees friendly error message
```

### Common Error Scenarios
```
404 (Content Not Found):
- Backend: {"error": "chapter_not_found", "chapter_id": "xyz"}
- MCP: Passes error to ChatGPT
- Skill: "I couldn't find that chapter. Let me suggest alternatives..."

403 (Access Denied):
- Backend: {"error": "access_denied", "required_tier": "premium"}
- MCP: Passes error to ChatGPT  
- Skill: "This content requires a Premium subscription..."

500 (Server Error):
- Backend: {"error": "internal_error", "message": "Please try again"}
- MCP: Passes error to ChatGPT
- Skill: "I'm having trouble accessing the content right now..."
```

---

## Performance Integration

### Caching Strategy Integration
```
R2 Level: Cloudflare CDN caches static content
API Level: Redis caches frequently accessed data
MCP Level: Minimal caching (requests proxied through)
Client Level: ChatGPT may cache responses
```

### Rate Limiting Integration
```
API Layer: 1000 requests/minute per IP
MCP Layer: Inherits backend rate limits
Client Layer: Subject to ChatGPT rate limits
```

### Monitoring Integration
```
Backend: Logs all requests with timing
MCP: Logs all tool calls with timing  
ChatGPT: May provide usage metrics
Monitoring: Aggregate metrics across all layers
```

---

## Constitutional Compliance Verification

### Integration-Level Checks
```
✓ No LLM imports in backend code
✓ No LLM API calls in backend code
✓ MCP server acts as pure proxy (no processing)
✓ Content delivered verbatim from storage
✓ Quiz grading uses exact answer matching
✓ All intelligence in ChatGPT (user's subscription)
✓ Pre-computed embeddings used for search (not real-time)
✓ Deterministic algorithms for progress/streak calculation
```

### Automated Compliance Testing
```python
def test_zero_backend_llm_integrity():
    """Verify the integrated system maintains constitutional compliance"""
    
    # Test content delivery is verbatim
    stored_content = get_content_from_r2("ch1-intro-to-agents.md")
    api_response = client.get("/api/v1/chapters/ch1-intro-to-agents")
    assert api_response.json()["content"] == stored_content
    
    # Test quiz grading is exact matching
    submission = {"answers": {"q1": "b"}}
    result = client.post("/api/v1/quizzes/test-quiz/submit", json=submission)
    # Verify grading used answer key, not LLM
    
    # Test no LLM calls in backend logs
    # Verify MCP server only proxies requests
```

---

## Deployment Integration

### Environment Configuration
```
Backend Environment Variables:
- DATABASE_URL: PostgreSQL connection
- R2_ENDPOINT: Cloudflare R2 endpoint  
- R2_ACCESS_KEY: R2 credentials
- R2_SECRET_KEY: R2 credentials
- R2_BUCKET_NAME: Content bucket
- REDIS_URL: Cache connection
- JWT_SECRET_KEY: Token signing

MCP Server Environment Variables:
- COURSE_COMPANION_API_URL: Backend API URL
- COURSE_COMPANION_API_TOKEN: Backend API token (if needed)
```

### Health Check Integration
```
Backend Health: /health endpoint checks DB, R2, Redis
MCP Health: Validates connection to backend API
Overall: Both must be healthy for system to function
```

---

## Testing Integration

### End-to-End Test Scenarios
```python
def test_full_concept_explanation_flow():
    """Test complete flow from user request to explanation"""
    # Simulate user asking for explanation
    # Verify MCP server proxies to backend
    # Verify content delivered verbatim
    # Verify ChatGPT generates explanation from content

def test_full_quiz_session_flow(): 
    """Test complete quiz flow"""
    # Start quiz via MCP
    # Answer questions
    # Submit via MCP
    # Verify grading with answer key
    # Verify results delivered

def test_progress_tracking_flow():
    """Test progress tracking integration"""
    # Complete chapter
    # Verify progress updated in DB
    # Verify streak calculated correctly
    # Verify achievements awarded
```

---

## Success Criteria

### Functional Integration
- [ ] All MCP tools map correctly to backend endpoints
- [ ] Content flows from R2 → Backend → MCP → ChatGPT → User
- [ ] Quiz flow works end-to-end with proper grading
- [ ] Progress tracking updates correctly across all systems
- [ ] Authentication/authorization works throughout

### Constitutional Compliance
- [ ] Zero LLM processing in backend
- [ ] Zero LLM processing in MCP server
- [ ] Content delivered verbatim
- [ ] Quiz grading uses exact matching
- [ ] All intelligence in ChatGPT

### Performance
- [ ] End-to-end response time < 2 seconds
- [ ] Backend API response time < 100ms
- [ ] MCP server adds < 50ms overhead
- [ ] Caching reduces R2 load by >90%

### Reliability
- [ ] 99.9% uptime across all components
- [ ] Graceful error handling throughout
- [ ] Proper fallback mechanisms
- [ ] Monitoring and alerting in place

---

**Spec Version:** 1.0
**Last Updated:** January 17, 2026
**Status:** Ready for Implementation