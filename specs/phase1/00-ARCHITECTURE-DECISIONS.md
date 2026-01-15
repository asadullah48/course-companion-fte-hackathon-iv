# Architecture Decision Record (ADR)
## Course Companion FTE - Hackathon IV

**Project:** AI Agent Development Digital Tutor  
**Architecture:** Zero-Backend-LLM → Hybrid Intelligence → Full Web App  
**Date:** January 2026  
**Team Lead:** Asadullah (@asadullah48)

---

## Decision 1: Course Topic Selection

**Status:** ✅ DECIDED  
**Choice:** AI Agent Development  

**Rationale:**
- Aligns with team's proven expertise (LearnFlow, Agent Factory experience)
- Leverages existing 39-skill marketplace knowledge
- Self-referential learning opportunity (Digital FTE teaching AI Agents)
- Highest market demand among hackathon options
- Rich content pipeline from existing projects

**Content Modules:**
1. Introduction to AI Agents & Agent Factory Architecture
2. Claude Agent SDK Fundamentals
3. Model Context Protocol (MCP) Integration
4. Agent Skills Development & SKILL.md Structure
5. Agentic Workflows & Orchestration Patterns
6. Production Deployment & Cloud-Native Patterns

---

## Decision 2: Phase 1 Architecture - Zero-Backend-LLM

**Status:** ✅ DECIDED  
**Architecture Type:** Deterministic Backend + Intelligent Frontend

### System Flow
```
User → ChatGPT App (OpenAI Apps SDK) → FastAPI Backend → Cloudflare R2
                    ↓                          ↓
              (ALL Intelligence)      (ZERO Intelligence)
                                              ↓
                                       PostgreSQL (Progress)
```

### Backend Responsibilities (Deterministic ONLY)
✅ **ALLOWED:**
- Serve course content verbatim from R2
- Track user progress, streaks, completion
- Grade quizzes using answer-key matching
- Keyword/semantic search (pre-computed embeddings)
- Enforce freemium access gates
- Return navigation paths (next/previous chapter)

❌ **FORBIDDEN (Disqualification Risk):**
- ANY LLM API calls (OpenAI, Anthropic, Google)
- RAG summarization or content generation
- Prompt orchestration or agent loops
- Dynamic content transformation via LLM
- Evaluation beyond exact-match comparison

### ChatGPT App Responsibilities (ALL Intelligence)
✅ **ChatGPT Handles:**
- Explain concepts at learner's comprehension level
- Answer questions using provided content
- Provide examples, analogies, metaphors
- Motivate and encourage students
- Adapt tone and complexity
- Guide Socratic learning

**Cost Implications:**
- Backend Cost: $0.002-$0.004 per user/month
- ChatGPT Cost: $0 (user's existing subscription)
- Total Phase 1 Target: $16-$41/month for 10K users

---

## Decision 3: Technology Stack

**Status:** ✅ DECIDED

### Phase 1 Stack
| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | OpenAI Apps SDK | 800M+ user reach, conversational UI |
| **Backend** | FastAPI (Python) | High performance, type safety, async support |
| **Database** | PostgreSQL (Neon/Supabase) | Free tier, reliable, SQL for progress tracking |
| **Storage** | Cloudflare R2 | S3-compatible, $0.015/GB, zero egress fees |
| **Compute** | Fly.io / Railway | Low-cost, auto-scaling, global edge |
| **Search** | Pre-computed embeddings | Avoid real-time LLM inference |

### Phase 2 Additions (Hybrid Intelligence)
- Claude Sonnet 4 API for adaptive learning paths
- LLM-based assessment grading
- Cross-chapter synthesis

### Phase 3 Additions (Web Frontend)
- Next.js 14 (App Router)
- Tailwind CSS + shadcn/ui
- Recharts for progress visualization

---

## Decision 4: Development Methodology

**Status:** ✅ DECIDED  
**Methodology:** Spec-Driven Development (Specification-First Principles)

### Workflow
```
1. Write Comprehensive Spec (Markdown)
   ↓
2. Review & Validate Spec
   ↓
3. Claude Code Reads Spec → Generates Code
   ↓
4. Test Generated Code
   ↓
5. If Issues → Refine Spec (NOT code) → Regenerate
   ↓
6. Deploy
```

**Key Principles:**
- ❌ NO manual coding ("vibe coding")
- ✅ ALL code generated from specs
- ✅ Specs are source of truth
- ✅ Iterative spec refinement until correct output

---

## Decision 5: Agent Skills Strategy

**Status:** ✅ DECIDED  
**Required Skills:** 4 Educational Agent Skills

| Skill Name | Purpose | Trigger Keywords |
|------------|---------|------------------|
| concept-explainer | Multi-level explanations | "explain", "what is", "how does" |
| quiz-master | Guided quiz sessions | "quiz", "test me", "practice" |
| socratic-tutor | Question-based learning | "help me think", "I'm stuck" |
| progress-motivator | Achievement celebration | "my progress", "streak" |

**Implementation:**
- Each skill = 1 SKILL.md file
- Stored in ChatGPT App manifest
- Contains procedural knowledge, not code

---

## Decision 6: Cost Optimization Strategy

**Status:** ✅ DECIDED

### Phase 1 Cost Targets
- **Infrastructure:** $16-$41/month (10K users)
- **Per User:** $0.002-$0.004/month
- **Zero LLM costs** in backend

### Monetization Model
| Tier | Price | Features | LLM Cost |
|------|-------|----------|----------|
| Free | $0 | 3 chapters, basic quizzes | $0 |
| Premium | $9.99/mo | All content, progress tracking | $0 |
| Pro | $19.99/mo | + Adaptive paths, LLM grading | $0.05-0.10/user |
| Team | $49.99/mo | + Analytics, multi-seat | $0.15-0.30/user |

---

## Decision 7: Quality Assurance Strategy

**Status:** ✅ DECIDED

### Phase 1 Checkpoints
- [ ] Backend contains ZERO LLM API calls
- [ ] All 6 required features implemented
- [ ] ChatGPT App manifest validates
- [ ] Cost analysis confirms targets
- [ ] Demo video < 5 minutes

---

## Decision 8: Repository Structure

**Status:** ✅ DECIDED
```
course-companion-fte-hackathon-iv/
├── specs/                        # Source of Truth
│   ├── phase1/
│   │   ├── constitution/         # Immutable rules
│   │   ├── backend/             # API specs
│   │   ├── frontend/            # ChatGPT App specs
│   │   ├── skills/              # Agent Skills specs
│   │   └── content/             # Content structure specs
│   ├── phase2/                   # Hybrid intelligence specs
│   └── phase3/                   # Web frontend specs
├── src/                          # Generated Code
│   ├── backend/                 # FastAPI application
│   ├── chatgpt-app/             # OpenAI Apps manifest
│   └── web-frontend/            # Next.js application
└── docs/                         # Documentation
```

---

## Next Steps

1. ✅ Create Constitutional Rules
2. ⏳ Create Backend API Specs (6 endpoints)
3. ⏳ Create ChatGPT App Spec
4. ⏳ Create Agent Skills Specs (4 skills)
5. ⏳ Create Content Structure Spec
6. ⏳ Generate code via Claude Code

**Document Status:** Living Document  
**Last Updated:** January 15, 2026
