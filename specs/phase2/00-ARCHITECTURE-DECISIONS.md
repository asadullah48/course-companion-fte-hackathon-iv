# Architecture Decision Record (ADR)
## Course Companion FTE - Phase 2: Hybrid Intelligence

**Project:** AI Agent Development Digital Tutor
**Architecture:** Hybrid Intelligence (Selective Backend LLM)
**Date:** January 2026
**Team Lead:** Asadullah (@asadullah48)
**Prerequisite:** Phase 1 Complete (Zero-Backend-LLM)

---

## Overview: Hybrid Intelligence Transition

**Status:** PLANNED

### Rationale for Transition

Phase 1's "Zero-Backend-LLM" architecture successfully delivered a cost-effective learning platform where all intelligence resided in the ChatGPT frontend. Phase 2 introduces **selective LLM integration** in the backend for capabilities that cannot be achieved through deterministic logic alone:

1. **Adaptive Learning Paths** - Personalized curriculum sequencing based on learner performance patterns
2. **Intelligent Assessment Grading** - Free-form answer evaluation with partial credit and feedback
3. **Cross-Chapter Synthesis** - AI-generated summaries connecting concepts across modules

### Design Philosophy

```
"Minimal LLM, Maximum Value"

Use LLM calls ONLY when:
- Deterministic logic cannot achieve the goal
- The value clearly exceeds the cost
- Caching can amortize expensive operations
```

---

## Decision 1: Breaking Changes from Phase 1

**Status:** DECIDED

### Constitutional Rules Relaxed

| Phase 1 Rule | Phase 2 Modification | Justification |
|--------------|---------------------|---------------|
| NO backend LLM API calls | SELECTIVE LLM calls allowed | Enable adaptive learning, intelligent grading |
| Exact-match grading only | LLM-based evaluation permitted | Support free-form answers, partial credit |
| Static content serving | Dynamic synthesis allowed | Cross-chapter summaries, personalized recaps |
| Zero LLM cost target | Controlled LLM budget per tier | Premium features require LLM capabilities |

### Rules Preserved (Immutable)

- User progress data stored in PostgreSQL (source of truth)
- Course content served verbatim from R2 (no LLM transformation of source material)
- Freemium access gates enforced deterministically
- Authentication and authorization remain stateless
- All LLM calls logged for cost tracking and debugging

### Migration Path

```
Phase 1 (Current)           Phase 2 (Target)
─────────────────           ────────────────
Backend: 0% LLM      →      Backend: ~5% LLM (selective)
Frontend: 100% LLM   →      Frontend: ~95% LLM (unchanged)
Cost: $0 LLM         →      Cost: $0.05-$0.30/user/month
```

---

## Decision 2: New Capabilities

**Status:** DECIDED

### Capability 1: Adaptive Learning Paths

**Purpose:** Dynamically adjust chapter sequencing and content difficulty based on learner performance.

**Implementation:**
- Claude Sonnet 4 API analyzes learner's quiz scores, time-on-page, and interaction patterns
- Generates personalized "next best action" recommendations
- Suggests remedial content or accelerated paths

**Trigger Conditions:**
- User completes a chapter assessment
- User requests personalized guidance
- Weekly learning plan generation (async, cached)

**API Contract:**
```python
POST /api/v2/learning-path/generate
Request:
{
  "user_id": "uuid",
  "completed_chapters": ["ch1", "ch2"],
  "quiz_scores": {"ch1": 85, "ch2": 62},
  "learning_style": "visual" | "reading" | "hands-on"
}

Response:
{
  "recommended_path": ["ch2-review", "ch3", "ch4"],
  "reasoning": "Chapter 2 score below 70% suggests review...",
  "estimated_completion": "2 weeks",
  "cached_until": "2026-01-20T00:00:00Z"
}
```

**Cost Control:**
- Cache learning paths for 7 days (or until new assessment)
- Maximum 4 path generations per user per month
- Batch processing during off-peak hours

---

### Capability 2: LLM-Based Assessment Grading

**Purpose:** Evaluate free-form answers with nuanced understanding, partial credit, and actionable feedback.

**Implementation:**
- Claude Sonnet 4 grades open-ended responses against rubric
- Provides partial credit (0-100 scale) with explanation
- Suggests specific improvements

**Supported Question Types:**
| Type | Phase 1 Grading | Phase 2 Grading |
|------|-----------------|-----------------|
| Multiple Choice | Exact match | Exact match (unchanged) |
| True/False | Exact match | Exact match (unchanged) |
| Fill-in-the-blank | Keyword match | Semantic similarity + LLM |
| Short Answer | NOT SUPPORTED | LLM rubric evaluation |
| Code Explanation | NOT SUPPORTED | LLM + syntax validation |

**API Contract:**
```python
POST /api/v2/assessment/grade
Request:
{
  "question_id": "q123",
  "question_text": "Explain how MCP servers enable tool discovery...",
  "rubric": ["mentions tool registration", "explains capability advertisement", "..."],
  "user_answer": "MCP servers let agents find available tools by...",
  "max_score": 10
}

Response:
{
  "score": 7,
  "max_score": 10,
  "feedback": "Good explanation of tool discovery. To improve, mention the capability advertisement mechanism and how agents query available tools at runtime.",
  "rubric_breakdown": [
    {"criterion": "mentions tool registration", "met": true, "points": 3},
    {"criterion": "explains capability advertisement", "met": false, "points": 0},
    {"criterion": "practical example", "met": true, "points": 4}
  ],
  "confidence": 0.85
}
```

**Cost Control:**
- LLM grading only for Pro/Team tiers
- Batch grade submissions every 5 minutes
- Cache identical answers (hash-based deduplication)

---

### Capability 3: Cross-Chapter Synthesis

**Purpose:** Generate AI-powered summaries connecting concepts across multiple chapters.

**Implementation:**
- Claude Sonnet 4 synthesizes key themes from completed chapters
- Creates personalized "learning journey" narratives
- Generates spaced-repetition review prompts

**Features:**
| Feature | Description | Trigger |
|---------|-------------|---------|
| Chapter Recap | Summary of key concepts | Chapter completion |
| Connection Map | Links between chapters | Every 3 chapters |
| Knowledge Gaps | Identifies weak areas | Weekly (async) |
| Review Prompts | Spaced repetition questions | Daily (cached) |

**API Contract:**
```python
POST /api/v2/synthesis/generate
Request:
{
  "user_id": "uuid",
  "synthesis_type": "connection_map" | "knowledge_gaps" | "review_prompts",
  "chapter_scope": ["ch1", "ch2", "ch3"]
}

Response:
{
  "synthesis_id": "syn_abc123",
  "content": {
    "title": "Connecting Agent Fundamentals to MCP",
    "connections": [
      {
        "from": "ch1:agent-loop",
        "to": "ch3:mcp-tools",
        "insight": "The agent loop's tool execution phase directly uses MCP..."
      }
    ],
    "key_themes": ["tool abstraction", "capability discovery"],
    "suggested_review": ["q1", "q15", "q23"]
  },
  "generated_at": "2026-01-19T12:00:00Z",
  "cached_until": "2026-01-26T12:00:00Z"
}
```

**Cost Control:**
- Generate syntheses asynchronously (background job)
- Cache for 7 days per user per chapter combination
- Limit to 2 synthesis requests per user per day

---

## Decision 3: Technology Stack Additions

**Status:** DECIDED

### New Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **LLM Provider** | Claude Sonnet 4 API | Primary intelligence layer |
| **LLM Gateway** | Custom middleware | Rate limiting, cost tracking, caching |
| **Cache Layer** | Redis | LLM response caching, token budget tracking |
| **Vector DB** | Qdrant (optional) | Semantic search, similar question detection |
| **Background Jobs** | Celery + Redis | Async synthesis generation |

### Claude Sonnet 4 Integration

**Selection Rationale:**
- Optimal cost/performance balance for educational content
- Strong reasoning for rubric-based grading
- Consistent output formatting for structured responses
- 200K token context window for cross-chapter synthesis

**Configuration:**
```python
CLAUDE_CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,  # Most responses under 500 tokens
    "temperature": 0.3,  # Low variance for grading consistency
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "retry_delay_seconds": 1
}
```

### Vector Database (Optional)

**Use Cases:**
- Semantic search across course content
- Similar question detection (reduce LLM calls)
- Learner clustering for cohort-based recommendations

**Implementation Decision:** Deferred to Phase 2.1 based on demand.

---

## Decision 4: Cost Analysis

**Status:** DECIDED

### LLM Cost Model (Claude Sonnet 4)

| Operation | Input Tokens | Output Tokens | Cost/Call |
|-----------|-------------|---------------|-----------|
| Learning Path Generation | ~2,000 | ~500 | $0.0075 |
| Assessment Grading | ~1,500 | ~300 | $0.0054 |
| Chapter Synthesis | ~4,000 | ~800 | $0.0144 |
| Connection Map | ~6,000 | ~1,000 | $0.0210 |

*Pricing based on Claude Sonnet 4: $3/1M input tokens, $15/1M output tokens*

### Per-User Monthly Cost Estimates

| Tier | Features | Est. LLM Calls/Month | LLM Cost/User/Month |
|------|----------|---------------------|---------------------|
| **Free** | Basic quizzes only | 0 | $0.00 |
| **Premium** | All content, deterministic grading | 0 | $0.00 |
| **Pro** | + Adaptive paths, LLM grading | 10-15 | $0.05-$0.10 |
| **Team** | + Synthesis, analytics | 20-30 | $0.15-$0.30 |

### Infrastructure Cost Projections

| Component | Phase 1 | Phase 2 | Delta |
|-----------|---------|---------|-------|
| Compute (Fly.io) | $20/mo | $35/mo | +$15 |
| Database (Neon) | $0/mo | $0/mo | $0 |
| Storage (R2) | $5/mo | $5/mo | $0 |
| Redis (Upstash) | $0/mo | $10/mo | +$10 |
| Claude API | $0/mo | $50-150/mo | +$50-150 |
| **Total** | **$25/mo** | **$100-200/mo** | +$75-175 |

*Projections based on 1,000 active users (100 Pro, 50 Team)*

### Cost Optimization Strategies

1. **Aggressive Caching** - 7-day TTL for learning paths and syntheses
2. **Batch Processing** - Grade submissions in batches every 5 minutes
3. **Token Budgets** - Hard limits per user per tier per month
4. **Deduplication** - Hash-based caching for identical inputs
5. **Off-Peak Processing** - Async jobs scheduled during low-traffic hours

---

## Decision 5: Architecture Diagram

**Status:** DECIDED

### Phase 2 System Architecture

```
                                    ┌─────────────────────────────────────────────────────┐
                                    │                   USER DEVICES                      │
                                    └─────────────────────────────────────────────────────┘
                                                           │
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND LAYER                                           │
│  ┌─────────────────────────────┐           ┌─────────────────────────────┐                 │
│  │     ChatGPT App (Phase 1)   │           │    Web Frontend (Phase 3)   │                 │
│  │   - Concept explanation     │           │    - Dashboard UI           │                 │
│  │   - Socratic tutoring       │           │    - Progress visualization │                 │
│  │   - Motivation/encouragement│           │    - Direct API access      │                 │
│  │   ~~~~~~~~~~~~~~~~~~~~~~~~  │           │    ~~~~~~~~~~~~~~~~~~~~~~   │                 │
│  │   ALL conversational AI     │           │    Static UI only           │                 │
│  └──────────────┬──────────────┘           └──────────────┬──────────────┘                 │
│                 │                                         │                                │
└─────────────────┼─────────────────────────────────────────┼────────────────────────────────┘
                  │                                         │
                  └─────────────────┬───────────────────────┘
                                    │ HTTPS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    BACKEND LAYER (FastAPI)                                  │
│                                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐    │
│  │                              API Gateway / Router                                   │    │
│  └────────────────────────────────────────────────────────────────────────────────────┘    │
│                 │                          │                           │                   │
│                 ▼                          ▼                           ▼                   │
│  ┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────────────┐       │
│  │ DETERMINISTIC LAYER  │   │   LLM GATEWAY LAYER  │   │   BACKGROUND JOBS LAYER  │       │
│  │ (Phase 1 - Unchanged)│   │   (Phase 2 - NEW)    │   │   (Phase 2 - NEW)        │       │
│  │ ──────────────────── │   │ ──────────────────── │   │ ────────────────────────  │       │
│  │ • Content serving    │   │ • Rate limiter       │   │ • Async synthesis        │       │
│  │ • Progress tracking  │   │ • Token budget mgr   │   │ • Batch grading          │       │
│  │ • Exact-match grading│   │ • Response cache     │   │ • Learning path refresh  │       │
│  │ • Navigation logic   │   │ • Cost tracker       │   │ • Scheduled reports      │       │
│  │ • Access gates       │   │ • Retry handler      │   │                          │       │
│  └──────────┬───────────┘   └──────────┬───────────┘   └────────────┬─────────────┘       │
│             │                          │                            │                      │
└─────────────┼──────────────────────────┼────────────────────────────┼──────────────────────┘
              │                          │                            │
              ▼                          ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA LAYER                                               │
│                                                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────────────┐    │
│  │  PostgreSQL   │   │ Cloudflare R2 │   │    Redis      │   │   Claude Sonnet 4     │    │
│  │  (Neon)       │   │               │   │   (Upstash)   │   │   (Anthropic API)     │    │
│  │ ───────────── │   │ ───────────── │   │ ───────────── │   │ ───────────────────── │    │
│  │ • User data   │   │ • Course JSON │   │ • LLM cache   │   │ • Adaptive paths      │    │
│  │ • Progress    │   │ • Media assets│   │ • Token budget│   │ • Free-form grading   │    │
│  │ • Assessments │   │ • Answer keys │   │ • Session data│   │ • Cross-chapter synth │    │
│  │ • LLM logs    │   │               │   │ • Job queues  │   │                       │    │
│  └───────────────┘   └───────────────┘   └───────────────┘   └───────────────────────┘    │
│                                                                                             │
│  ┌───────────────────────────────────────┐                                                 │
│  │         Qdrant (Optional)             │                                                 │
│  │ ───────────────────────────────────── │                                                 │
│  │ • Semantic search vectors             │                                                 │
│  │ • Similar question detection          │                                                 │
│  └───────────────────────────────────────┘                                                 │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow: LLM-Graded Assessment

```
User submits       API validates      Check cache       Cache miss?         Grade & cache
free-form answer   & authorizes       (Redis)           Call Claude         response
      │                 │                 │                  │                   │
      ▼                 ▼                 ▼                  ▼                   ▼
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Client  │ ───▶ │  FastAPI │ ───▶ │  Redis   │ ───▶ │  Claude  │ ───▶ │  Redis   │
│          │      │          │      │  Cache   │      │  API     │      │  + DB    │
└──────────┘      └──────────┘      └──────────┘      └──────────┘      └──────────┘
                        │                 │                                   │
                        │            Cache hit?                               │
                        │                 │                                   │
                        ◀─────────────────┴───────────────────────────────────┘
                              Return cached or fresh result
```

---

## Decision 6: Risk Mitigation

**Status:** DECIDED

### Risk 1: LLM Cost Overrun

**Probability:** Medium
**Impact:** High

**Mitigations:**
| Control | Implementation | Threshold |
|---------|----------------|-----------|
| Token Budget | Per-user monthly limits | Pro: 50K tokens, Team: 150K tokens |
| Rate Limiting | Per-minute call limits | 10 calls/min per user |
| Circuit Breaker | Auto-disable on spend spike | >200% daily budget triggers alert |
| Cost Dashboard | Real-time monitoring | Alert at 80% monthly budget |

### Risk 2: LLM Latency Impact

**Probability:** Medium
**Impact:** Medium

**Mitigations:**
- Async processing for non-blocking operations
- 30-second timeout with graceful fallback
- Cache warm-up during off-peak hours
- Deterministic fallback for grading (exact-match) if LLM unavailable

### Risk 3: Grading Inconsistency

**Probability:** Low
**Impact:** High (user trust)

**Mitigations:**
- Low temperature (0.3) for consistent outputs
- Rubric-based grading with explicit criteria
- Confidence score threshold (reject < 0.7, flag for human review)
- A/B testing against human graders before launch

### Risk 4: API Provider Outage

**Probability:** Low
**Impact:** High

**Mitigations:**
- 72-hour response cache for learning paths
- Deterministic fallback modes for all features
- Multi-provider support architecture (Claude primary, OpenAI backup)
- Queue-based retry with exponential backoff

### Risk 5: Data Privacy (LLM Data Handling)

**Probability:** Low
**Impact:** Critical

**Mitigations:**
- No PII sent to LLM (user_id only, no names/emails)
- Anthropic's data retention policy (no training on API data)
- Request/response logging for audit trail
- GDPR/CCPA compliant data handling

---

## Decision 7: Directory Structure

**Status:** DECIDED

### Phase 2 Spec File Organization

```
specs/phase2/
├── 00-ARCHITECTURE-DECISIONS.md    # This document
├── 01-llm-gateway/
│   ├── spec.md                     # LLM gateway service specification
│   ├── plan.md                     # Implementation plan
│   └── tasks.md                    # Development tasks
├── 02-adaptive-learning/
│   ├── spec.md                     # Adaptive learning paths feature spec
│   ├── plan.md                     # Algorithm and API design
│   └── tasks.md                    # Implementation tasks
├── 03-intelligent-grading/
│   ├── spec.md                     # LLM-based assessment grading spec
│   ├── plan.md                     # Rubric engine design
│   └── tasks.md                    # Development tasks
├── 04-cross-chapter-synthesis/
│   ├── spec.md                     # Synthesis feature specification
│   ├── plan.md                     # Content analysis pipeline
│   └── tasks.md                    # Implementation tasks
├── 05-cost-management/
│   ├── spec.md                     # Token budgets and rate limiting
│   ├── plan.md                     # Monitoring and alerting design
│   └── tasks.md                    # Dashboard and controls tasks
└── 06-background-jobs/
    ├── spec.md                     # Celery worker specification
    ├── plan.md                     # Job scheduling design
    └── tasks.md                    # Worker implementation tasks
```

### Implementation Order

| Priority | Feature | Dependencies | Est. Effort |
|----------|---------|--------------|-------------|
| 1 | LLM Gateway | None | 3 days |
| 2 | Cost Management | LLM Gateway | 2 days |
| 3 | Intelligent Grading | LLM Gateway, Cost Mgmt | 4 days |
| 4 | Adaptive Learning | LLM Gateway, Cost Mgmt | 5 days |
| 5 | Cross-Chapter Synthesis | All above | 4 days |
| 6 | Background Jobs | Synthesis | 3 days |

**Total Estimated Effort:** 21 days (3 weeks)

---

## Decision 8: Success Criteria

**Status:** DECIDED

### Phase 2 Launch Checklist

- [ ] LLM Gateway deployed with rate limiting and cost tracking
- [ ] Token budgets enforced per tier
- [ ] Adaptive learning paths generating successfully
- [ ] LLM grading achieving >90% agreement with human graders
- [ ] Cross-chapter synthesis cached and serving users
- [ ] Cost per user within projected ranges
- [ ] Latency p95 < 3 seconds for LLM operations
- [ ] Fallback modes tested and operational
- [ ] Privacy compliance verified (no PII to LLM)
- [ ] Monitoring dashboard live with alerts configured

### Metrics to Track

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| LLM cost per user (Pro) | $0.05-$0.10/mo | >$0.15/mo |
| LLM cost per user (Team) | $0.15-$0.30/mo | >$0.40/mo |
| Grading latency (p95) | <3 seconds | >5 seconds |
| Cache hit rate | >70% | <50% |
| Grading accuracy | >90% | <85% |
| API availability | >99.5% | <99% |

---

## Appendix A: API Versioning Strategy

Phase 2 introduces `/api/v2/` endpoints while maintaining backward compatibility:

| Endpoint | v1 (Phase 1) | v2 (Phase 2) |
|----------|--------------|--------------|
| `/content/*` | Unchanged | Unchanged |
| `/progress/*` | Unchanged | Unchanged |
| `/quiz/grade` | Exact-match | Exact-match (unchanged) |
| `/assessment/grade` | N/A | NEW: LLM grading |
| `/learning-path/generate` | N/A | NEW: Adaptive paths |
| `/synthesis/generate` | N/A | NEW: Cross-chapter |

All v1 endpoints remain functional. v2 endpoints require Pro/Team tier authentication.

---

## Appendix B: LLM Prompt Templates

Stored in: `src/backend/prompts/`

```
prompts/
├── grading/
│   ├── short_answer.jinja2
│   ├── code_explanation.jinja2
│   └── rubric_evaluation.jinja2
├── learning_path/
│   ├── path_generation.jinja2
│   └── remediation.jinja2
└── synthesis/
    ├── chapter_recap.jinja2
    ├── connection_map.jinja2
    └── review_prompts.jinja2
```

All prompts version-controlled and reviewed before deployment.

---

**Document Status:** Living Document
**Last Updated:** January 19, 2026
**Next Review:** Before Phase 2 Development Kickoff
