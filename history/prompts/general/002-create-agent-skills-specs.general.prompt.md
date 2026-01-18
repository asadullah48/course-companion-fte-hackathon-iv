---
id: 002
title: Create Agent Skills Specs (4 Educational Skills)
stage: spec
date: 2026-01-17
surface: agent
model: claude-opus-4-5
feature: phase1-skills
branch: master
user: asadullahshafique
command: resume plan mode
labels: ["skills", "agent", "spec", "chatgpt-app", "education", "tutor"]
links:
  spec: null
  ticket: null
  adr: specs/phase1/00-ARCHITECTURE-DECISIONS.md
  pr: null
files:
  - specs/phase1/skills/01-concept-explainer.skill.md
  - specs/phase1/skills/02-quiz-master.skill.md
  - specs/phase1/skills/03-socratic-tutor.skill.md
  - specs/phase1/skills/04-progress-motivator.skill.md
  - specs/phase1/frontend/01-chatgpt-app-manifest.md
tests: []
---

## Prompt

User requested to continue the planning session to create the 4 required Agent Skills specs as defined in ADR Decision 5 (Agent Skills Strategy). Additionally, the ChatGPT App Manifest spec was created to define the frontend integration.

## Response

Created 5 comprehensive specifications:

### 1. Concept Explainer (`01-concept-explainer.skill.md`)
- **Purpose:** Multi-level explanations adapted to learner's comprehension level
- **Trigger Keywords:** "explain", "what is", "how does", "define", "tell me about"
- **Features:**
  - 5 explanation levels (ELI5 to Expert)
  - Analogies and real-world examples
  - Visual diagrams and code samples
  - Prerequisite concept linking

### 2. Quiz Master (`02-quiz-master.skill.md`)
- **Purpose:** Guided quiz sessions with immediate feedback
- **Trigger Keywords:** "quiz", "test me", "practice", "check my knowledge"
- **Features:**
  - Multiple question types (MCQ, true/false, code completion)
  - Immediate feedback with explanations
  - Adaptive difficulty based on performance
  - Progress tracking integration

### 3. Socratic Tutor (`03-socratic-tutor.skill.md`)
- **Purpose:** Question-based learning through guided discovery
- **Trigger Keywords:** "help me think", "I'm stuck", "walk me through"
- **Features:**
  - Never gives direct answers
  - Leads through clarifying questions
  - Celebrates discoveries
  - Scaffolded problem-solving

### 4. Progress Motivator (`04-progress-motivator.skill.md`)
- **Purpose:** Achievement celebration and motivation
- **Trigger Keywords:** "my progress", "streak", "achievements", "how am I doing"
- **Features:**
  - Visual progress displays
  - Streak tracking and alerts
  - Achievement celebrations
  - Personalized motivation strategies

### 5. ChatGPT App Manifest (`01-chatgpt-app-manifest.md`)
- **Purpose:** OpenAI Apps SDK integration specification
- **Features:**
  - API action definitions for all 6 backend endpoints
  - Skill routing logic
  - Conversation flow management
  - Freemium tier handling

All skills follow the SKILL.md format with:
- Procedural knowledge (not code)
- Response templates
- Quality checklists
- API integration patterns
- Constitutional compliance (ChatGPT handles ALL intelligence)

## Outcome

Successfully completed all required Phase 1 specifications:
1. ✅ Constitutional Rules
2. ✅ Backend API Specs (6 endpoints)
3. ✅ ChatGPT App Manifest
4. ✅ Agent Skills (4 skills)
5. ⏳ Content Structure Spec (remaining)

## Next Steps

1. Create Content Structure Spec
2. Begin code generation from specs
