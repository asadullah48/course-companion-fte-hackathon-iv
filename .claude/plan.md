# Phase 2 Implementation Plan: Hybrid Intelligence

## Overview

**Goal:** Transition from Zero-Backend-LLM (Phase 1) to Hybrid Intelligence architecture, adding selective LLM capabilities for adaptive learning and advanced assessment.

**Surface:** Project-level planning
**Success Criteria:** Complete spec documents for Phase 2 ready for implementation

---

## Current State Analysis

### Phase 1 Completed ✅
- **Backend API:** FastAPI with 6 API modules (content, navigation, quiz, progress, search, access)
- **Database Models:** User, Content, Quiz, Progress, Achievement
- **Authentication:** JWT-based with subscription tiers (Free, Premium, Pro, Team)
- **MCP Server:** Production-ready bridge for Claude Desktop/Code integration
- **Tests:** Unit and integration tests passing (bcrypt fix applied)

### Phase 2 Directory Status
- `/specs/phase2/` exists but is **empty** - ready for specification work

---

## Phase 2 Scope Definition

### In Scope
1. **Adaptive Learning Paths** - Claude Sonnet 4 API for personalized recommendations
2. **LLM-Based Assessment Grading** - Free-form answer evaluation with partial credit
3. **Cross-Chapter Synthesis** - AI-generated summaries connecting concepts
4. **Phase 2 Constitutional Rules** - New allowed capabilities document

### Out of Scope
- Web Frontend (Phase 3)
- Team management features
- Admin dashboard

### External Dependencies
- Anthropic Claude API (Sonnet 4)
- Existing Phase 1 backend infrastructure

---

## Implementation Tasks

### Task 1: Create Phase 2 Architecture Decisions Document
**File:** `specs/phase2/00-ARCHITECTURE-DECISIONS.md`
- Define Hybrid Intelligence rationale
- Document breaking changes from Phase 1 constitution
- Cost analysis for LLM API usage
- Technology stack additions (Claude API, potential vector DB)

### Task 2: Create Adaptive Learning API Spec
**File:** `specs/phase2/backend/07-adaptive-learning-api.md`
- Personalized learning path generation endpoints
- User learning profile analysis
- Knowledge gap detection algorithms
- Recommendation engine design

### Task 3: Create Assessment Grading API Spec
**File:** `specs/phase2/backend/08-assessment-grading-api.md`
- LLM-based free-form answer evaluation
- Partial credit scoring system
- Semantic similarity matching
- AI-generated feedback for incorrect answers

### Task 4: Create Synthesis API Spec
**File:** `specs/phase2/backend/09-synthesis-api.md`
- Cross-chapter summary generation
- Concept bridge creation
- Integration tutorial endpoints
- Real-world application examples

### Task 5: Create LLM Integration Spec
**File:** `specs/phase2/llm/01-claude-integration.md`
- Prompt templates for grading and synthesis
- Cost optimization strategies (caching, streaming)
- Rate limiting and error handling
- Token usage budgeting per tier

### Task 6: Create Phase 2 Constitutional Rules
**File:** `specs/phase2/constitution/02-PHASE2-RULES.md`
- New allowed capabilities (LLM calls, personalization)
- Cost compliance framework updates
- Audit requirements for AI features

### Task 7: Update Subscription Tier Features
**File:** `specs/phase2/access/01-tier-features-update.md`
- Pro tier: Adaptive learning, LLM grading
- Team tier: All Pro + analytics
- Cost per user estimates

---

## Recommended Approach

### Use spec-requirements Agent
For each spec document, use the `spec-requirements` subagent to:
1. Gather requirements
2. Define acceptance criteria
3. Specify API contracts

### Use spec-design Agent
After requirements are approved:
1. Create detailed technical design
2. Define data models
3. Document API endpoints

### Use spec-tasks Agent
After design approval:
1. Break down into testable tasks
2. Create implementation checklist
3. Define test cases

---

## Risk Analysis

1. **LLM Cost Overrun** - Mitigate with token budgets per tier and caching
2. **Latency Impact** - Mitigate with streaming responses and async processing
3. **Quality Variance** - Mitigate with prompt engineering and evaluation benchmarks

---

## Next Steps (After Plan Approval)

1. Start with `spec-requirements` agent for Task 1 (Architecture Decisions)
2. Iterate through requirements → design → tasks for each API spec
3. Use `spec-judge` agent to validate each spec before moving forward

---

## Directory Structure (Target)

```
specs/phase2/
├── 00-ARCHITECTURE-DECISIONS.md
├── backend/
│   ├── 07-adaptive-learning-api.md
│   ├── 08-assessment-grading-api.md
│   └── 09-synthesis-api.md
├── llm/
│   └── 01-claude-integration.md
├── constitution/
│   └── 02-PHASE2-RULES.md
└── access/
    └── 01-tier-features-update.md
```
