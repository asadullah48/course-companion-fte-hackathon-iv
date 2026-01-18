# Content Structure Specification
## AI Agent Development Course - Phase 1

**Version:** 1.0
**Purpose:** Define course organization, chapter structure, and content metadata
**Storage:** Cloudflare R2 (S3-compatible)

---

## Constitutional Compliance

This specification adheres to the Zero-Backend-LLM architecture:
- Content stored verbatim in R2
- No LLM processing at retrieval time
- All intelligence provided by ChatGPT (user's subscription)
- Backend serves content byte-for-byte

---

## Course Overview

| Attribute | Value |
|-----------|-------|
| **Course Title** | AI Agent Development: From Fundamentals to Production |
| **Total Modules** | 3 |
| **Total Chapters** | 9 |
| **Estimated Duration** | 6-8 hours |
| **Target Audience** | Developers familiar with Python/TypeScript |
| **Difficulty Range** | Beginner to Advanced |

---

## Module Structure

### Module 1: Foundations (Free Tier)

**Module ID:** `mod-1-foundations`
**Access Tier:** Free
**Estimated Duration:** 2 hours

| Chapter | ID | Title | Est. Time | Difficulty |
|---------|---|-------|-----------|------------|
| 1 | `ch1-intro-to-agents` | Introduction to AI Agents | 15 min | Beginner |
| 2 | `ch2-agent-factory-architecture` | Agent Factory Architecture | 25 min | Beginner |
| 3 | `ch3-mcp-fundamentals` | Model Context Protocol (MCP) Fundamentals | 30 min | Beginner |

**Learning Objectives:**
- Understand what AI agents are and why they matter
- Learn the 8-layer Agent Factory architecture
- Grasp MCP concepts: servers, tools, resources

**Module Quiz:** `quiz-mod-1-foundations` (15 questions)

---

### Module 2: Skills Development (Premium)

**Module ID:** `mod-2-skills`
**Access Tier:** Premium ($9.99/mo)
**Estimated Duration:** 2.5 hours
**Prerequisites:** Module 1 completion

| Chapter | ID | Title | Est. Time | Difficulty |
|---------|---|-------|-----------|------------|
| 4 | `ch4-claude-agent-sdk` | Claude Agent SDK Deep Dive | 30 min | Intermediate |
| 5 | `ch5-skill-md-structure` | SKILL.md Structure & Procedural Knowledge | 35 min | Intermediate |
| 6 | `ch6-tool-integration` | Tool Integration & External APIs | 25 min | Intermediate |

**Learning Objectives:**
- Master the Claude Agent SDK
- Create effective SKILL.md files
- Integrate tools and external services

**Module Quiz:** `quiz-mod-2-skills` (20 questions)

---

### Module 3: Agentic Workflows (Premium)

**Module ID:** `mod-3-workflows`
**Access Tier:** Premium ($9.99/mo)
**Estimated Duration:** 2 hours
**Prerequisites:** Module 2 completion

| Chapter | ID | Title | Est. Time | Difficulty |
|---------|---|-------|-----------|------------|
| 7 | `ch7-workflow-patterns` | Agentic Workflow Patterns | 30 min | Advanced |
| 8 | `ch8-multi-agent-systems` | Multi-Agent Orchestration | 35 min | Advanced |
| 9 | `ch9-production-deployment` | Production Deployment & Best Practices | 25 min | Advanced |

**Learning Objectives:**
- Design effective agentic workflows
- Build multi-agent systems
- Deploy agents to production

**Module Quiz:** `quiz-mod-3-workflows` (20 questions)

---

## Chapter Content Structure

### Standard Chapter Template

Each chapter follows this markdown structure:

```markdown
---
chapter_id: ch1-intro-to-agents
title: Introduction to AI Agents
module: 1
order: 1
difficulty: beginner
estimated_read_time: 15
word_count: ~1500
tags: ["fundamentals", "intro", "agents"]
prerequisites: []
learning_objectives:
  - "Define what an AI agent is"
  - "Explain the difference between agents and chatbots"
  - "Identify key components of an AI agent"
created_at: 2026-01-10T00:00:00Z
updated_at: 2026-01-15T12:00:00Z
---

# Introduction to AI Agents

## Overview
[Brief introduction paragraph]

## What You'll Learn
- Objective 1
- Objective 2
- Objective 3

## Concepts

### Concept 1: What is an AI Agent?
[Content with examples, code samples, diagrams]

### Concept 2: Agents vs Chatbots
[Comparison content]

### Concept 3: Key Components
[Component breakdown]

## Hands-On Example
```python
# Example code demonstrating the concept
```

## Key Takeaways
- Takeaway 1
- Takeaway 2
- Takeaway 3

## Check Your Understanding
[2-3 quick questions to test comprehension]

## Next Steps
[Preview of next chapter]
```

---

## Chapter Specifications

### Chapter 1: Introduction to AI Agents

**File:** `chapters/ch1-intro-to-agents.md`

**Content Sections:**
1. What is an AI Agent?
2. Evolution: From Chatbots to Agents
3. Autonomous Decision-Making
4. The Agent Loop: Observe → Think → Act
5. Real-World Applications
6. Why Learn Agent Development Now?

**Key Concepts:**
- Agent autonomy
- Tool use capability
- Goal-directed behavior
- Context awareness

**Code Examples:** Basic agent loop pseudocode

---

### Chapter 2: Agent Factory Architecture

**File:** `chapters/ch2-agent-factory-architecture.md`

**Content Sections:**
1. The 8-Layer Architecture Overview
2. Layer 1: Core Intelligence (Claude)
3. Layer 2: Skill System
4. Layer 3: Tool Integration
5. Layer 4: Memory & Context
6. Layer 5: Orchestration
7. Layer 6: Deployment
8. Layer 7: Monitoring
9. Layer 8: User Interface
10. How Layers Work Together

**Key Concepts:**
- Separation of concerns
- Skill-based architecture
- Memory persistence
- Orchestration patterns

**Diagrams:**
- `agent-factory-8-layers.png`
- `layer-interaction-flow.png`

---

### Chapter 3: MCP Fundamentals

**File:** `chapters/ch3-mcp-fundamentals.md`

**Content Sections:**
1. What is Model Context Protocol?
2. MCP Servers Explained
3. Tools: Extending Agent Capabilities
4. Resources: Read-Only Data Access
5. Prompts: Reusable Prompt Templates
6. MCP in Practice: A Complete Example
7. Setting Up Your First MCP Server

**Key Concepts:**
- Server-client architecture
- Tool definitions
- Resource schemas
- Prompt templates

**Code Examples:**
```python
# Example MCP server setup
from mcp import Server, Tool

server = Server("example-server")

@server.tool("get_weather")
async def get_weather(location: str) -> dict:
    """Get current weather for a location"""
    # Implementation
    pass
```

---

### Chapter 4: Claude Agent SDK Deep Dive

**File:** `chapters/ch4-claude-agent-sdk.md`

**Content Sections:**
1. SDK Overview & Installation
2. Creating Your First Agent
3. Tool Binding & Execution
4. Conversation Management
5. Error Handling Patterns
6. Streaming Responses
7. Token Management
8. Best Practices

**Key Concepts:**
- SDK initialization
- Agent configuration
- Tool binding
- Memory patterns

**Code Examples:** Full working agent implementation

---

### Chapter 5: SKILL.md Structure

**File:** `chapters/ch5-skill-md-structure.md`

**Content Sections:**
1. What is SKILL.md?
2. The Procedural Knowledge Approach
3. Skill Metadata & Triggers
4. Core Principles Section
5. Procedural Steps
6. Response Templates
7. Quality Checklists
8. Guardrails & Constraints
9. Writing Your First Skill

**Key Concepts:**
- Procedural vs declarative knowledge
- Trigger patterns
- Template-based responses
- Quality assurance

**Reference:** Link to actual skill examples in `/specs/phase1/skills/`

---

### Chapter 6: Tool Integration

**File:** `chapters/ch6-tool-integration.md`

**Content Sections:**
1. Why Tools Matter
2. Designing Tool Interfaces
3. Input Validation
4. Error Handling
5. Rate Limiting & Caching
6. Security Considerations
7. Testing Tools
8. Real-World Tool Examples

**Key Concepts:**
- Tool schemas
- Input/output contracts
- Error taxonomy
- Security best practices

**Code Examples:**
```python
# Tool with proper validation and error handling
from pydantic import BaseModel, Field

class WeatherInput(BaseModel):
    location: str = Field(..., min_length=2, max_length=100)
    units: str = Field(default="celsius", pattern="^(celsius|fahrenheit)$")

@tool("get_weather")
async def get_weather(input: WeatherInput) -> WeatherResult:
    try:
        # Implementation
        pass
    except ExternalAPIError as e:
        raise ToolError(f"Weather service unavailable: {e}")
```

---

### Chapter 7: Workflow Patterns

**File:** `chapters/ch7-workflow-patterns.md`

**Content Sections:**
1. Introduction to Agentic Workflows
2. Sequential Workflows
3. Parallel Workflows
4. Conditional Branching
5. Human-in-the-Loop Patterns
6. Error Recovery Strategies
7. Workflow Composition
8. Testing Workflows

**Key Concepts:**
- Workflow orchestration
- Parallel execution
- State management
- Checkpointing

**Diagrams:**
- `workflow-patterns-overview.png`
- `sequential-vs-parallel.png`

---

### Chapter 8: Multi-Agent Systems

**File:** `chapters/ch8-multi-agent-systems.md`

**Content Sections:**
1. Why Multiple Agents?
2. Agent Roles & Specialization
3. Communication Patterns
4. Coordinator Agent Pattern
5. Swarm Intelligence
6. Conflict Resolution
7. Scaling Considerations
8. Case Study: Research Team

**Key Concepts:**
- Agent specialization
- Message passing
- Coordination strategies
- Load balancing

**Diagrams:**
- `multi-agent-topology.png`
- `coordinator-pattern.png`

---

### Chapter 9: Production Deployment

**File:** `chapters/ch9-production-deployment.md`

**Content Sections:**
1. Deployment Readiness Checklist
2. Infrastructure Choices
3. Containerization with Docker
4. Kubernetes Deployment
5. Monitoring & Observability
6. Logging Best Practices
7. Error Tracking
8. Cost Optimization
9. Security Hardening
10. Continuous Deployment

**Key Concepts:**
- Container orchestration
- Observability stack
- Cost management
- Security patterns

**Code Examples:** Docker and K8s configurations

---

## Quiz Structure

### Quiz Format

Each module has a comprehensive quiz:

```json
{
  "quiz_id": "quiz-mod-1-foundations",
  "module_id": "mod-1-foundations",
  "title": "Foundations Quiz",
  "description": "Test your understanding of AI Agent fundamentals",
  "passing_score": 70,
  "time_limit_minutes": null,
  "questions": [
    {
      "question_id": "q1",
      "type": "multiple_choice",
      "question": "What is the primary difference between a chatbot and an AI agent?",
      "options": [
        "Agents can use tools",
        "Agents can browse the web",
        "Agents have better language models",
        "Agents are faster"
      ],
      "correct_answer": 0,
      "explanation": "AI agents are distinguished by their ability to use tools to take actions in the world, not just generate text responses.",
      "chapter_reference": "ch1-intro-to-agents"
    }
  ]
}
```

### Question Types

| Type | Description | Grading |
|------|-------------|---------|
| `multiple_choice` | 4 options, single answer | Exact match |
| `true_false` | Boolean answer | Exact match |
| `fill_blank` | Short text answer | Normalized match |
| `code_completion` | Complete code snippet | Exact match |

---

## Media Assets

### Directory Structure

```
r2://course-content/
├── chapters/
│   ├── ch1-intro-to-agents.md
│   ├── ch2-agent-factory-architecture.md
│   └── ... (9 chapters)
├── quizzes/
│   ├── quiz-mod-1-foundations.json
│   ├── quiz-mod-2-skills.json
│   └── quiz-mod-3-workflows.json
├── media/
│   ├── ch1/
│   │   └── agent-loop.png
│   ├── ch2/
│   │   ├── agent-factory-8-layers.png
│   │   └── layer-interaction-flow.png
│   ├── ch7/
│   │   ├── workflow-patterns-overview.png
│   │   └── sequential-vs-parallel.png
│   └── ch8/
│       ├── multi-agent-topology.png
│       └── coordinator-pattern.png
└── metadata/
    ├── chapters.json
    └── modules.json
```

### Image Specifications

| Type | Format | Max Size | Dimensions |
|------|--------|----------|------------|
| Diagram | PNG | 500KB | 1200x800 max |
| Screenshot | WebP | 300KB | 1920x1080 max |
| Icon | SVG | 50KB | 64x64 |
| Thumbnail | WebP | 50KB | 400x300 |

---

## Metadata Files

### chapters.json

```json
{
  "version": "1.0",
  "updated_at": "2026-01-15T12:00:00Z",
  "chapters": [
    {
      "chapter_id": "ch1-intro-to-agents",
      "title": "Introduction to AI Agents",
      "module_id": "mod-1-foundations",
      "order": 1,
      "difficulty": "beginner",
      "estimated_read_time": 15,
      "word_count": 1500,
      "tags": ["fundamentals", "intro", "agents"],
      "prerequisites": [],
      "access_tier": "free"
    },
    {
      "chapter_id": "ch2-agent-factory-architecture",
      "title": "Agent Factory Architecture",
      "module_id": "mod-1-foundations",
      "order": 2,
      "difficulty": "beginner",
      "estimated_read_time": 25,
      "word_count": 2500,
      "tags": ["architecture", "design", "layers"],
      "prerequisites": ["ch1-intro-to-agents"],
      "access_tier": "free"
    },
    {
      "chapter_id": "ch3-mcp-fundamentals",
      "title": "Model Context Protocol (MCP) Fundamentals",
      "module_id": "mod-1-foundations",
      "order": 3,
      "difficulty": "beginner",
      "estimated_read_time": 30,
      "word_count": 3000,
      "tags": ["mcp", "protocol", "tools"],
      "prerequisites": ["ch2-agent-factory-architecture"],
      "access_tier": "free"
    },
    {
      "chapter_id": "ch4-claude-agent-sdk",
      "title": "Claude Agent SDK Deep Dive",
      "module_id": "mod-2-skills",
      "order": 4,
      "difficulty": "intermediate",
      "estimated_read_time": 30,
      "word_count": 3500,
      "tags": ["sdk", "claude", "implementation"],
      "prerequisites": ["ch3-mcp-fundamentals"],
      "access_tier": "premium"
    },
    {
      "chapter_id": "ch5-skill-md-structure",
      "title": "SKILL.md Structure & Procedural Knowledge",
      "module_id": "mod-2-skills",
      "order": 5,
      "difficulty": "intermediate",
      "estimated_read_time": 35,
      "word_count": 4000,
      "tags": ["skills", "procedural", "templates"],
      "prerequisites": ["ch4-claude-agent-sdk"],
      "access_tier": "premium"
    },
    {
      "chapter_id": "ch6-tool-integration",
      "title": "Tool Integration & External APIs",
      "module_id": "mod-2-skills",
      "order": 6,
      "difficulty": "intermediate",
      "estimated_read_time": 25,
      "word_count": 2800,
      "tags": ["tools", "apis", "integration"],
      "prerequisites": ["ch5-skill-md-structure"],
      "access_tier": "premium"
    },
    {
      "chapter_id": "ch7-workflow-patterns",
      "title": "Agentic Workflow Patterns",
      "module_id": "mod-3-workflows",
      "order": 7,
      "difficulty": "advanced",
      "estimated_read_time": 30,
      "word_count": 3200,
      "tags": ["workflows", "patterns", "orchestration"],
      "prerequisites": ["ch6-tool-integration"],
      "access_tier": "premium"
    },
    {
      "chapter_id": "ch8-multi-agent-systems",
      "title": "Multi-Agent Orchestration",
      "module_id": "mod-3-workflows",
      "order": 8,
      "difficulty": "advanced",
      "estimated_read_time": 35,
      "word_count": 4000,
      "tags": ["multi-agent", "orchestration", "coordination"],
      "prerequisites": ["ch7-workflow-patterns"],
      "access_tier": "premium"
    },
    {
      "chapter_id": "ch9-production-deployment",
      "title": "Production Deployment & Best Practices",
      "module_id": "mod-3-workflows",
      "order": 9,
      "difficulty": "advanced",
      "estimated_read_time": 25,
      "word_count": 3000,
      "tags": ["deployment", "production", "devops"],
      "prerequisites": ["ch8-multi-agent-systems"],
      "access_tier": "premium"
    }
  ]
}
```

### modules.json

```json
{
  "version": "1.0",
  "updated_at": "2026-01-15T12:00:00Z",
  "modules": [
    {
      "module_id": "mod-1-foundations",
      "title": "Foundations of AI Agents",
      "description": "Learn the core concepts of AI Agents, the Agent Factory Architecture, and Model Context Protocol",
      "order": 1,
      "difficulty": "beginner",
      "estimated_duration_minutes": 70,
      "chapter_count": 3,
      "prerequisites": [],
      "access_tier": "free",
      "learning_objectives": [
        "Understand what AI agents are and their capabilities",
        "Learn the 8-layer Agent Factory architecture",
        "Master MCP fundamentals: servers, tools, resources"
      ],
      "quiz_id": "quiz-mod-1-foundations"
    },
    {
      "module_id": "mod-2-skills",
      "title": "Skills Development",
      "description": "Master the Claude Agent SDK, create effective SKILL.md files, and integrate external tools",
      "order": 2,
      "difficulty": "intermediate",
      "estimated_duration_minutes": 90,
      "chapter_count": 3,
      "prerequisites": ["mod-1-foundations"],
      "access_tier": "premium",
      "learning_objectives": [
        "Use the Claude Agent SDK effectively",
        "Create procedural knowledge with SKILL.md",
        "Integrate and test external tools"
      ],
      "quiz_id": "quiz-mod-2-skills"
    },
    {
      "module_id": "mod-3-workflows",
      "title": "Agentic Workflows",
      "description": "Design workflow patterns, build multi-agent systems, and deploy to production",
      "order": 3,
      "difficulty": "advanced",
      "estimated_duration_minutes": 90,
      "chapter_count": 3,
      "prerequisites": ["mod-2-skills"],
      "access_tier": "premium",
      "learning_objectives": [
        "Design effective agentic workflow patterns",
        "Build and orchestrate multi-agent systems",
        "Deploy agents to production with best practices"
      ],
      "quiz_id": "quiz-mod-3-workflows"
    }
  ]
}
```

---

## Access Control Matrix

| Content | Free | Premium | Pro | Team |
|---------|------|---------|-----|------|
| Module 1 (Ch 1-3) | ✅ | ✅ | ✅ | ✅ |
| Module 2 (Ch 4-6) | ❌ | ✅ | ✅ | ✅ |
| Module 3 (Ch 7-9) | ❌ | ✅ | ✅ | ✅ |
| Module Quizzes | ❌ | ✅ | ✅ | ✅ |
| Progress Tracking | Limited | ✅ | ✅ | ✅ |
| Streak Freezes | 0 | 2/mo | 5/mo | Unlimited |
| Certificate | ❌ | ✅ | ✅ | ✅ |

---

## Content Update Process

### Version Control

1. All content stored in Git
2. CI/CD syncs to R2 on merge to main
3. Metadata files regenerated automatically
4. Cache invalidation triggered on update

### Update Workflow

```
1. Edit chapter markdown in Git
2. Update metadata (word count, updated_at)
3. Create PR with content changes
4. Review and merge
5. CI/CD pipeline:
   - Validate markdown structure
   - Update chapters.json
   - Sync to R2
   - Invalidate CDN cache
```

---

## Success Criteria

- [ ] All 9 chapters written in markdown format
- [ ] All 3 module quizzes created with 15-20 questions each
- [ ] Metadata files (chapters.json, modules.json) complete
- [ ] Media assets uploaded to R2
- [ ] Content accessible via API endpoints
- [ ] Access control working per tier

---

**Spec Version:** 1.0
**Last Updated:** January 17, 2026
**Status:** Ready for Content Creation
