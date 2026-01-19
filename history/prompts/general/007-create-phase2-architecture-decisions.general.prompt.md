---
id: 007
title: Create Phase 2 Architecture Decisions Document
stage: spec
date: 2026-01-19
surface: agent
model: claude-opus-4-5-20251101
feature: phase2-hybrid-intelligence
branch: master
user: asadullahshafique
command: create
labels: ["architecture", "phase2", "llm-integration", "hybrid-intelligence", "adr"]
links:
  spec: specs/phase2/00-ARCHITECTURE-DECISIONS.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/phase2/00-ARCHITECTURE-DECISIONS.md (created)
tests: []
---

# Prompt

Create the Phase 2 Architecture Decisions document at specs/phase2/00-ARCHITECTURE-DECISIONS.md

Context:
- This is for a Course Companion app that teaches AI Agents
- Phase 1 uses "Zero-Backend-LLM" architecture (no LLM calls in backend)
- Phase 2 transitions to "Hybrid Intelligence" (selective LLM in backend)

Reference the existing Phase 1 architecture at specs/phase1/00-ARCHITECTURE-DECISIONS.md for format and style.

The Phase 2 document should include:

1. **Overview** - Hybrid Intelligence transition rationale
2. **Breaking Changes from Phase 1** - What constitutional rules are relaxed
3. **New Capabilities**:
   - Adaptive Learning Paths (Claude Sonnet 4 API)
   - LLM-Based Assessment Grading (free-form answers, partial credit)
   - Cross-Chapter Synthesis (AI-generated summaries)
4. **Technology Stack Additions**:
   - Claude Sonnet 4 API integration
   - Potential vector DB for semantic search (optional)
5. **Cost Analysis**:
   - Estimated LLM costs per user per tier
   - Pro tier: $0.05-0.10/user/month
   - Team tier: $0.15-0.30/user/month
   - Infrastructure increase projections
6. **Architecture Diagram** - Show the new LLM integration layer
7. **Risk Mitigation** - Token budgets, caching, rate limiting
8. **Directory Structure** - Phase 2 spec file organization

# Response

## Summary

Created a comprehensive Phase 2 Architecture Decisions document following the Phase 1 format. The document covers the transition from "Zero-Backend-LLM" to "Hybrid Intelligence" architecture.

### Document Structure

1. **Overview** - Explains the "Minimal LLM, Maximum Value" design philosophy
2. **Decision 1: Breaking Changes** - Details which Phase 1 rules are relaxed vs. preserved
3. **Decision 2: New Capabilities** - Three major features with full API contracts:
   - Adaptive Learning Paths
   - LLM-Based Assessment Grading
   - Cross-Chapter Synthesis
4. **Decision 3: Technology Stack Additions** - Claude Sonnet 4 integration, Redis caching, optional Qdrant
5. **Decision 4: Cost Analysis** - Detailed per-operation costs and monthly projections by tier
6. **Decision 5: Architecture Diagram** - ASCII diagram showing new LLM gateway layer
7. **Decision 6: Risk Mitigation** - Five risks with probability/impact and mitigations
8. **Decision 7: Directory Structure** - Phase 2 spec file organization with 6 feature subdirectories
9. **Decision 8: Success Criteria** - Launch checklist and metrics to track

### Key Decisions

- LLM calls only for Pro/Team tiers (Free/Premium remain $0 LLM cost)
- Aggressive 7-day caching for learning paths and syntheses
- Token budgets: Pro 50K/month, Team 150K/month
- Circuit breaker at 200% daily budget
- Deterministic fallbacks for all LLM features
- No PII sent to LLM (user_id only)

### Outcome

- Phase 2 architecture fully documented and ready for implementation planning
- Clear separation of Phase 1 (deterministic) and Phase 2 (selective LLM) responsibilities
- Cost projections aligned with original monetization model ($0.05-$0.30/user/month)
