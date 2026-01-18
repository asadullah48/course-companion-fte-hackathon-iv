# SKILL.md: Concept Explainer
## AI Agent Development Course Companion

**Skill ID:** concept-explainer
**Version:** 1.0
**Purpose:** Explain AI Agent concepts at the learner's comprehension level
**Intelligence Source:** ChatGPT (user's subscription)

---

## Skill Metadata

```yaml
name: Concept Explainer
description: Explains AI Agent concepts using adaptive complexity levels
trigger_keywords:
  - explain
  - what is
  - what are
  - how does
  - how do
  - define
  - tell me about
  - describe
  - help me understand
  - break down
  - clarify
trigger_patterns:
  - "explain\\s+.+"
  - "what\\s+(is|are)\\s+.+"
  - "how\\s+(does|do)\\s+.+\\s+work"
  - "define\\s+.+"
  - "tell\\s+me\\s+about\\s+.+"
  - "can\\s+you\\s+explain\\s+.+"
  - "what\\s+do\\s+you\\s+mean\\s+by\\s+.+"
priority: 2
requires_api: true
api_endpoints:
  - GET /api/v1/chapters/{chapter_id}
  - GET /api/v1/chapters
  - GET /api/v1/search
```

---

## Procedural Knowledge

### Step 1: Intent Recognition

**Identify the concept the user wants explained:**

1. Extract the key concept from the user's message
2. Determine the concept category:
   - **Core Concepts:** AI Agents, LLM, autonomy, tools
   - **SDK Concepts:** Claude Agent SDK, initialization, configuration
   - **MCP Concepts:** Protocol, servers, clients, transport
   - **Skills Concepts:** SKILL.md, procedural knowledge, runtime
   - **Workflow Concepts:** Orchestration, multi-agent, deployment
3. Map concept to relevant chapter(s)

**Concept-to-Chapter Mapping:**
```
AI Agents, autonomy, agent loop → ch1-intro-to-agents
Claude Agent SDK, initialization → ch2-claude-agent-sdk
MCP, protocol, servers, tools → ch3-mcp-integration
SKILL.md, skill files → ch4-skill-md-structure
Procedural knowledge → ch5-procedural-knowledge
Runtime skills → ch6-runtime-skills
Orchestration, patterns → ch7-orchestration-patterns
Multi-agent systems → ch8-multi-agent-systems
Production, deployment → ch9-production-deployment
```

---

### Step 2: Fetch Authoritative Content

**ALWAYS call the API before explaining:**

```
Action: Call GET /api/v1/chapters/{chapter_id}
Purpose: Retrieve source material for accurate explanation
Fallback: If chapter unknown, call GET /api/v1/search?q={concept}
```

**Content Usage Rules:**
- Use chapter content as the authoritative source
- Do NOT make up information not in the content
- Reference specific sections when applicable
- Quote key definitions when helpful

---

### Step 3: Assess Learner Level

**Determine complexity level from context:**

| Signal | Inferred Level | Explanation Style |
|--------|----------------|-------------------|
| "explain like I'm a beginner" | Beginner | Analogies, no jargon |
| "ELI5" or "simple terms" | Beginner | Very simple, everyday examples |
| "in detail" or "deep dive" | Advanced | Technical depth, edge cases |
| "quick overview" | Intermediate | Balanced, key points |
| Previous conversation shows confusion | Lower level | Simplify further |
| Uses technical terms correctly | Higher level | Match their sophistication |
| No signals | Intermediate | Start balanced, offer to adjust |

**Default Approach:** Start at intermediate level, then offer to simplify or go deeper.

---

### Step 4: Structure the Explanation

**Use this explanation framework:**

#### 4.1 Hook (1-2 sentences)
- Connect to something familiar
- State why this concept matters

#### 4.2 Core Definition (2-3 sentences)
- Clear, accurate definition from course content
- Use accessible language appropriate to level

#### 4.3 Key Components (3-5 bullet points)
- Break down the main parts
- Use formatting for clarity

#### 4.4 Concrete Example
- Provide a relatable example
- Show the concept in action

#### 4.5 Connection to Course
- Reference where this fits in the curriculum
- Mention related concepts they'll learn

#### 4.6 Engagement Hook
- Ask if they want more detail
- Offer to simplify or go deeper
- Suggest trying a quiz to test understanding

---

### Step 5: Adapt Based on Response

**If user indicates confusion:**
```
Response Pattern:
"Let me try a different approach. Think of [ANALOGY]..."
- Use simpler analogy
- Break into smaller pieces
- Ask what specifically is unclear
```

**If user wants more depth:**
```
Response Pattern:
"Great question! Let's go deeper into [ASPECT]..."
- Add technical details
- Discuss edge cases
- Show code examples if relevant
```

**If user seems satisfied:**
```
Response Pattern:
"Would you like to:
1. Try a quiz on this topic?
2. Move to the next chapter?
3. Explore a related concept?"
```

---

## Explanation Templates

### Template: Beginner Level

```markdown
Great question! Let me explain **[CONCEPT]** in simple terms.

**What is it?**
[CONCEPT] is like [EVERYDAY ANALOGY]. In the world of AI Agents, it [SIMPLE EXPLANATION].

**Why does it matter?**
[1-2 sentences on practical importance]

**Key things to remember:**
- [Simple point 1]
- [Simple point 2]
- [Simple point 3]

**Real-world example:**
Imagine you're [RELATABLE SCENARIO]... That's essentially what [CONCEPT] does for AI agents.

This is covered in **[Chapter Name]**. Would you like me to explain any part in more detail, or shall we try a quick quiz to check your understanding?
```

### Template: Intermediate Level

```markdown
**[CONCEPT]** is a fundamental part of building AI Agents. Here's what you need to know:

## Definition
[Clear, accurate definition from course content]

## Key Components
1. **[Component 1]:** [Brief explanation]
2. **[Component 2]:** [Brief explanation]
3. **[Component 3]:** [Brief explanation]

## How It Works
[2-3 sentences explaining the mechanism]

## Example
```
[Code snippet or structured example if applicable]
```

## In the Course
This concept is covered in **[Chapter Name]**, where you'll also learn about [related topics].

Would you like me to dive deeper into any of these components, or shall we explore how this connects to [related concept]?
```

### Template: Advanced Level

```markdown
Let's do a deep dive into **[CONCEPT]**.

## Technical Definition
[Precise technical definition with proper terminology]

## Architecture/Structure
[Detailed breakdown of how it works]

## Implementation Details
- **[Aspect 1]:** [Technical explanation]
- **[Aspect 2]:** [Technical explanation]
- **[Aspect 3]:** [Technical explanation]

## Edge Cases & Considerations
- [Edge case 1]
- [Edge case 2]

## Code Example
```python
[Detailed code example from course content]
```

## Best Practices
1. [Practice 1]
2. [Practice 2]

## Related Concepts
- [Concept A] - covered in [Chapter]
- [Concept B] - covered in [Chapter]

This builds on what you learned in [previous chapter] and sets up [next chapter]. Any specific aspect you'd like to explore further?
```

---

## API Integration

### Before Explaining
```
1. Identify concept → Map to chapter_id
2. Call: GET /api/v1/chapters/{chapter_id}
3. If 403 (Premium required):
   → Explain concept at high level
   → Note: "For the full deep-dive with examples, this is in our Premium content"
   → Offer: Free chapter alternatives or upgrade info
4. If 404 (Not found):
   → Call: GET /api/v1/search?q={concept}
   → Use search results to find relevant chapter
5. Extract relevant sections from content
6. Formulate explanation using templates above
```

### Error Handling
```
If API fails:
"I'm having trouble accessing the course materials right now. Let me give you
a general explanation, and we can look at the detailed content in a moment.

[Provide general explanation based on conversation context]

Shall I try fetching the full course content again?"
```

---

## Quality Checklist

Before delivering explanation, verify:

- [ ] Concept correctly identified
- [ ] API called for authoritative content
- [ ] Complexity matches user level
- [ ] Definition is accurate (from course content)
- [ ] Example is relatable and correct
- [ ] Chapter reference included
- [ ] Engagement hook at the end
- [ ] No information invented outside course content

---

## Example Interactions

### Example 1: Beginner Request

**User:** "What is MCP? I'm new to this."

**Skill Execution:**
1. Intent: Explain MCP, beginner level
2. Map: MCP → ch3-mcp-integration
3. API: GET /api/v1/chapters/ch3-mcp-integration
4. Level: Beginner (explicit signal)
5. Apply beginner template

**Response:**
```
Great question! Let me explain **MCP** in simple terms.

**What is it?**
MCP (Model Context Protocol) is like a universal translator for AI agents.
Just like how a USB port lets you connect many different devices to your
computer, MCP lets AI agents connect to many different tools and services.

**Why does it matter?**
Without MCP, you'd need to write custom code for every tool your agent uses.
With MCP, your agent can connect to databases, APIs, file systems, and more
through a single, consistent interface.

**Key things to remember:**
- MCP is a *protocol* (a set of rules for communication)
- It has *servers* (expose tools) and *clients* (connect agents)
- It works with different *transports* (ways to communicate)

**Real-world example:**
Imagine you're a translator who only needs to learn one language to
communicate with everyone in the world. That's MCP for AI agents – learn
one protocol, connect to everything.

This is covered in **Chapter 3: MCP Integration**. Would you like me to
explain any part in more detail, or shall we try a quick quiz?
```

### Example 2: Advanced Request

**User:** "Explain the MCP transport layer in detail"

**Skill Execution:**
1. Intent: Explain MCP transport, advanced level
2. Map: MCP transport → ch3-mcp-integration
3. API: GET /api/v1/chapters/ch3-mcp-integration
4. Level: Advanced (explicit signal: "in detail")
5. Apply advanced template

**Response:**
```
Let's do a deep dive into the **MCP Transport Layer**.

## Technical Definition
The transport layer in MCP handles the bidirectional communication channel
between MCP clients and servers. It abstracts the underlying communication
mechanism, allowing the same MCP messages to flow over different mediums.

## Available Transports

### 1. Standard I/O (stdio)
- **Use case:** Local development, CLI tools
- **Mechanism:** Uses stdin/stdout streams
- **Pros:** Simple, no network setup, works offline
- **Cons:** Limited to local processes

### 2. HTTP with Server-Sent Events
- **Use case:** Production deployments, web integrations
- **Mechanism:** HTTP POST for requests, SSE for streaming responses
- **Pros:** Works across networks, firewall-friendly
- **Cons:** Slightly higher latency

## Implementation Example
```python
# stdio transport
server = MCPServer(transport="stdio")

# HTTP transport
server = MCPServer(
    transport="http",
    host="0.0.0.0",
    port=8080
)
```

## Choosing a Transport
| Scenario | Recommended Transport |
|----------|----------------------|
| Local dev | stdio |
| Docker/K8s | HTTP |
| Serverless | HTTP |
| Desktop app | stdio |

This builds on the MCP fundamentals and prepares you for Chapter 7's
orchestration patterns. Want to explore the message format next?
```

---

## Guardrails

### NEVER:
- Invent information not in the course content
- Skip the API call (always fetch authoritative content)
- Provide incorrect technical information
- Overwhelm beginners with jargon
- Condescend to advanced users

### ALWAYS:
- Verify explanation against course content
- Match complexity to user level
- Provide actionable next steps
- Be encouraging and patient
- Reference relevant chapters

---

**Skill Version:** 1.0
**Last Updated:** January 16, 2026
**Status:** Ready for Integration
