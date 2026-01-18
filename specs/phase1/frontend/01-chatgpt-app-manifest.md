# ChatGPT App Specification: AI Agent Development Course Companion
## Phase 1 - Zero-Backend-LLM Architecture

**App Version:** 1.0
**Platform:** OpenAI ChatGPT Custom GPT with Actions
**Intelligence Source:** ChatGPT (user's existing subscription)
**Backend Intelligence:** ZERO (All LLM capabilities in ChatGPT only)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ChatGPT Plus/Team                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Custom GPT: Course Companion             │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              System Instructions                │  │  │
│  │  │  - Educational Persona                          │  │  │
│  │  │  - 4 Agent Skills                               │  │  │
│  │  │  - Course Context                               │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Actions (API Integration)          │  │  │
│  │  │  - Content Delivery API                         │  │  │
│  │  │  - Navigation API                               │  │  │
│  │  │  - Quiz API                                     │  │  │
│  │  │  - Progress API                                 │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API Calls
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (Zero-LLM)                     │
│  - Serves content verbatim                                  │
│  - Grades quizzes deterministically                         │
│  - Tracks progress with SQL                                 │
│  - NO LLM processing                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Constitutional Compliance

✅ **ALL INTELLIGENCE:** Resides in ChatGPT (user's subscription)
✅ **BACKEND ROLE:** Dumb data server only
❌ **FORBIDDEN:** Backend LLM calls for content generation
❌ **FORBIDDEN:** Backend LLM calls for personalization

**Reference:** `specs/phase1/constitution/01-IMMUTABLE-RULES.md`

---

## GPT Configuration

### Basic Information

```yaml
Name: AI Agent Development Tutor
Description: >
  Your personal tutor for mastering AI Agent development.
  Learn to build autonomous agents using Claude Agent SDK,
  MCP integration, and production deployment patterns.

Instructions: See "System Instructions" section below

Conversation Starters:
  - "What will I learn in this course?"
  - "Explain AI Agents to me like I'm a beginner"
  - "Quiz me on Claude Agent SDK"
  - "How's my progress looking?"

Capabilities:
  Web Browsing: OFF
  DALL·E Image Generation: OFF
  Code Interpreter: OFF

Actions: See "OpenAPI Schema" section below

Authentication: OAuth 2.0 (See "Authentication" section)
```

---

## System Instructions

```markdown
# AI Agent Development Course Companion

You are an expert tutor for the AI Agent Development course. Your role is to help students master building AI agents using Claude Agent SDK, MCP integration, and production deployment patterns.

## Your Personality
- Patient, encouraging, and knowledgeable
- Adapt explanations to student's level
- Celebrate progress and achievements
- Provide clear, structured responses

## Course Structure
The course has 3 modules with 9 chapters total:

**Module 1: Foundations (Free)**
1. Introduction to AI Agents
2. Claude Agent SDK Fundamentals
3. MCP Integration

**Module 2: Skills Development (Premium)**
4. SKILL.md Structure
5. Procedural Knowledge
6. Runtime Skills

**Module 3: Agentic Workflows (Premium)**
7. Orchestration Patterns
8. Multi-Agent Systems
9. Production Deployment

## Your 4 Skills

### Skill 1: Concept Explainer
**Trigger:** User asks "explain", "what is", "how does", "define"
**Behavior:**
1. Identify the concept they're asking about
2. Call the Content Delivery API to get relevant chapter content
3. Use the content to craft an explanation at their level
4. Offer to simplify or go deeper based on their response

### Skill 2: Quiz Master
**Trigger:** User says "quiz", "test me", "practice", "assess my knowledge"
**Behavior:**
1. Ask which chapter/topic they want to be quizzed on
2. Call the Quiz API to get questions
3. Present questions ONE AT A TIME
4. After each answer, submit to Quiz API for grading
5. Provide feedback with the pre-stored explanation
6. After all questions, summarize their performance

### Skill 3: Socratic Tutor
**Trigger:** User says "help me think", "guide me", "I'm stuck", "don't give me the answer"
**Behavior:**
1. NEVER give direct answers immediately
2. Ask probing questions to guide their thinking
3. Build understanding incrementally
4. Use the Socratic questioning hierarchy:
   - Clarifying: "What do you already know about X?"
   - Probing: "Why do you think that is?"
   - Connecting: "How does this relate to Y?"
   - Synthesis: "What would happen if...?"
5. Only reveal answers after genuine effort

### Skill 4: Progress Motivator
**Trigger:** User asks "my progress", "how am I doing", "streak", "achievements"
**Behavior:**
1. Call the Progress API to get their current stats
2. Present progress in an encouraging way
3. Celebrate streaks and achievements
4. Suggest next steps based on their progress
5. If streak at risk, gently remind them

## Response Guidelines

### Always:
- Be concise but thorough
- Use markdown formatting for clarity
- Include relevant chapter references
- Encourage continued learning

### Never:
- Make up course content (always fetch from API)
- Provide incorrect information about AI agents
- Skip straight to answers in Socratic mode
- Discourage or criticize the student

## API Usage Rules

1. **Content Requests:** Always call the Content API before explaining concepts
2. **Quiz Sessions:** Submit each answer individually for immediate feedback
3. **Progress Checks:** Fetch fresh progress data, don't assume from memory
4. **Error Handling:** If API fails, apologize and suggest trying again

## Example Interactions

**Concept Explanation:**
User: "What is MCP?"
You: [Call GET /chapters/ch3-mcp-integration]
Response: "MCP (Model Context Protocol) is a standardized way for AI agents to connect to external tools and services. Think of it as a universal adapter that lets your agent talk to databases, APIs, file systems, and more..."

**Quiz Session:**
User: "Quiz me on Chapter 1"
You: [Call GET /quizzes?chapter_id=ch1-intro-to-agents]
Response: "Great! Let's test your knowledge of AI Agents. Here's question 1 of 5:

**What is the primary purpose of an AI Agent?**
A) To replace human workers
B) To autonomously complete tasks using tools
C) To generate random text
D) To store data in databases

Take your time!"

**Progress Check:**
User: "How's my streak?"
You: [Call GET /progress/{user_id}/streak]
Response: "🔥 You're on a 5-day streak! You've been consistently learning for almost a week. Just 2 more days to hit the Week Warrior achievement. Keep it up!"
```

---

## OpenAPI Schema (Actions)

```yaml
openapi: 3.1.0
info:
  title: Course Companion API
  description: API for AI Agent Development course content, quizzes, and progress tracking
  version: 1.0.0
servers:
  - url: https://api.coursecompanion.dev/api/v1
    description: Production server

paths:
  # ===================
  # CONTENT DELIVERY
  # ===================
  /chapters/{chapter_id}:
    get:
      operationId: getChapterContent
      summary: Get chapter content verbatim
      description: Retrieves the full content of a specific chapter for explanation purposes
      parameters:
        - name: chapter_id
          in: path
          required: true
          description: Unique chapter identifier (e.g., ch1-intro-to-agents)
          schema:
            type: string
        - name: format
          in: query
          required: false
          description: Response format
          schema:
            type: string
            enum: [markdown, json]
            default: markdown
      responses:
        '200':
          description: Chapter content retrieved successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChapterContent'
        '404':
          description: Chapter not found
        '403':
          description: Access denied (premium content)

  /chapters:
    get:
      operationId: listChapters
      summary: List all chapters
      description: Get list of all chapters with metadata and completion status
      parameters:
        - name: module
          in: query
          required: false
          description: Filter by module number
          schema:
            type: integer
        - name: include_locked
          in: query
          required: false
          description: Include locked premium chapters
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Chapter list retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChapterList'

  /modules/{module_id}:
    get:
      operationId: getModuleOverview
      summary: Get module overview
      description: Retrieves module metadata and chapter list
      parameters:
        - name: module_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Module retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ModuleOverview'

  # ===================
  # NAVIGATION
  # ===================
  /chapters/{chapter_id}/next:
    get:
      operationId: getNextChapter
      summary: Get next chapter
      description: Returns the next chapter in sequence based on completion status
      parameters:
        - name: chapter_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Next chapter information
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NavigationResult'

  /navigation/sequence:
    get:
      operationId: getFullSequence
      summary: Get full chapter sequence
      description: Returns the complete ordered list of chapters with progress
      responses:
        '200':
          description: Full sequence retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ChapterSequence'

  /navigation/recommend:
    get:
      operationId: getRecommendedAction
      summary: Get recommended next action
      description: Suggests what the user should do next based on progress
      responses:
        '200':
          description: Recommendation retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Recommendation'

  # ===================
  # QUIZZES
  # ===================
  /quizzes:
    get:
      operationId: listQuizzes
      summary: List available quizzes
      description: Get list of quizzes filtered by chapter or module
      parameters:
        - name: chapter_id
          in: query
          required: false
          schema:
            type: string
        - name: module_id
          in: query
          required: false
          schema:
            type: integer
        - name: type
          in: query
          required: false
          schema:
            type: string
            enum: [chapter, module, practice]
      responses:
        '200':
          description: Quiz list retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QuizList'

  /quizzes/{quiz_id}:
    get:
      operationId: getQuizQuestions
      summary: Get quiz questions
      description: Retrieves quiz questions WITHOUT correct answers
      parameters:
        - name: quiz_id
          in: path
          required: true
          schema:
            type: string
        - name: shuffle
          in: query
          required: false
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Quiz retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Quiz'
        '429':
          description: Attempt limit reached

  /quizzes/{quiz_id}/submit:
    post:
      operationId: submitQuizAnswers
      summary: Submit quiz answers
      description: Submit answers for grading and receive score
      parameters:
        - name: quiz_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QuizSubmission'
      responses:
        '200':
          description: Quiz graded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QuizResult'

  /quizzes/{quiz_id}/results/{attempt_id}:
    get:
      operationId: getQuizResults
      summary: Get quiz results
      description: Retrieve detailed results for a specific quiz attempt
      parameters:
        - name: quiz_id
          in: path
          required: true
          schema:
            type: string
        - name: attempt_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Results retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QuizResultDetail'

  # ===================
  # PROGRESS
  # ===================
  /progress/{user_id}:
    get:
      operationId: getUserProgress
      summary: Get user progress
      description: Retrieve overall progress across all modules and chapters
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
        - name: include_chapters
          in: query
          required: false
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Progress retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserProgress'

  /progress/{user_id}/chapters/{chapter_id}:
    put:
      operationId: markChapterComplete
      summary: Mark chapter complete
      description: Mark a chapter as completed after quiz passed or content consumed
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
        - name: chapter_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ChapterCompletion'
      responses:
        '200':
          description: Chapter marked complete
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CompletionResult'

  /progress/{user_id}/streak:
    get:
      operationId: getUserStreak
      summary: Get learning streak
      description: Get current streak and streak history
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
        - name: history_days
          in: query
          required: false
          schema:
            type: integer
            default: 30
      responses:
        '200':
          description: Streak data retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/StreakData'

  /progress/{user_id}/achievements:
    get:
      operationId: getUserAchievements
      summary: Get achievements
      description: List all achievements (earned and locked)
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
        - name: filter
          in: query
          required: false
          schema:
            type: string
            enum: [all, earned, locked]
            default: all
      responses:
        '200':
          description: Achievements retrieved
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AchievementList'

  /progress/{user_id}/time:
    post:
      operationId: logLearningTime
      summary: Log learning time
      description: Log time spent learning for streak and analytics
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TimeLog'
      responses:
        '200':
          description: Time logged
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TimeLogResult'

components:
  schemas:
    ChapterContent:
      type: object
      properties:
        chapter_id:
          type: string
        title:
          type: string
        content:
          type: string
        content_type:
          type: string
        word_count:
          type: integer
        estimated_read_time:
          type: integer
        metadata:
          type: object

    ChapterList:
      type: object
      properties:
        chapters:
          type: array
          items:
            type: object
        total_chapters:
          type: integer
        completed_count:
          type: integer

    ModuleOverview:
      type: object
      properties:
        module_id:
          type: integer
        title:
          type: string
        description:
          type: string
        chapters:
          type: array
          items:
            type: object

    NavigationResult:
      type: object
      properties:
        next:
          type: string
          nullable: true
        reason:
          type: string

    ChapterSequence:
      type: object
      properties:
        sequence:
          type: array
          items:
            type: object
        current_position:
          type: integer

    Recommendation:
      type: object
      properties:
        action:
          type: string
        chapter_id:
          type: string
        reason:
          type: string

    QuizList:
      type: object
      properties:
        quizzes:
          type: array
          items:
            type: object
        total_quizzes:
          type: integer

    Quiz:
      type: object
      properties:
        quiz_id:
          type: string
        title:
          type: string
        questions:
          type: array
          items:
            type: object
        attempt_id:
          type: string
        expires_at:
          type: string

    QuizSubmission:
      type: object
      required:
        - attempt_id
        - answers
      properties:
        attempt_id:
          type: string
        answers:
          type: array
          items:
            type: object
            properties:
              question_id:
                type: string
              answer:
                type: string

    QuizResult:
      type: object
      properties:
        quiz_id:
          type: string
        score:
          type: integer
        total_points:
          type: integer
        passed:
          type: boolean
        results:
          type: array
          items:
            type: object

    QuizResultDetail:
      type: object
      properties:
        quiz_id:
          type: string
        attempt_id:
          type: string
        score:
          type: integer
        results:
          type: array
          items:
            type: object

    UserProgress:
      type: object
      properties:
        user_id:
          type: string
        overall:
          type: object
        modules:
          type: array
          items:
            type: object
        chapters:
          type: array
          items:
            type: object

    ChapterCompletion:
      type: object
      required:
        - completion_type
        - time_spent_minutes
      properties:
        completion_type:
          type: string
        quiz_attempt_id:
          type: string
        time_spent_minutes:
          type: integer

    CompletionResult:
      type: object
      properties:
        chapter_id:
          type: string
        status:
          type: string
        achievements_unlocked:
          type: array
          items:
            type: object

    StreakData:
      type: object
      properties:
        current_streak:
          type: integer
        longest_streak:
          type: integer
        streak_at_risk:
          type: boolean
        history:
          type: array
          items:
            type: object

    AchievementList:
      type: object
      properties:
        achievements:
          type: array
          items:
            type: object
        earned_count:
          type: integer
        points_earned:
          type: integer

    TimeLog:
      type: object
      required:
        - chapter_id
        - duration_minutes
        - activity_type
      properties:
        chapter_id:
          type: string
        duration_minutes:
          type: integer
        activity_type:
          type: string

    TimeLogResult:
      type: object
      properties:
        logged:
          type: boolean
        today_total_minutes:
          type: integer
        streak_maintained:
          type: boolean

  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://api.coursecompanion.dev/oauth/authorize
          tokenUrl: https://api.coursecompanion.dev/oauth/token
          scopes:
            read:content: Read course content
            read:progress: Read user progress
            write:progress: Update user progress

security:
  - oauth2: [read:content, read:progress, write:progress]
```

---

## Authentication Configuration

### OAuth 2.0 Flow

```yaml
Authentication Type: OAuth 2.0

OAuth Configuration:
  Client ID: (generated during app registration)
  Client Secret: (stored securely in GPT settings)
  Authorization URL: https://api.coursecompanion.dev/oauth/authorize
  Token URL: https://api.coursecompanion.dev/oauth/token
  Scope: read:content read:progress write:progress

Token Behavior:
  - Access token expires: 1 hour
  - Refresh token: Automatic
  - User consent: Required on first use

User Identification:
  - user_id derived from OAuth token
  - Backend extracts user from JWT claims
  - No manual user ID input needed
```

### Alternative: API Key (Simplified)

```yaml
Authentication Type: API Key

Configuration:
  Header Name: X-API-Key
  Key Source: User provides during setup

Usage:
  - Each user generates API key in web portal
  - Key entered in GPT settings
  - Simpler but less secure than OAuth
```

---

## Skill Routing Logic

### Intent Detection Rules

```python
# Skill routing based on user input patterns
# Used by ChatGPT to determine which skill to activate

SKILL_TRIGGERS = {
    "concept_explainer": {
        "keywords": ["explain", "what is", "what are", "how does", "how do", "define", "tell me about", "describe"],
        "patterns": [
            r"explain\s+.+",
            r"what\s+(is|are)\s+.+",
            r"how\s+(does|do)\s+.+\s+work",
            r"define\s+.+",
            r"tell\s+me\s+about\s+.+",
            r"can\s+you\s+explain\s+.+"
        ],
        "priority": 2
    },
    "quiz_master": {
        "keywords": ["quiz", "test", "assess", "practice", "questions", "exam"],
        "patterns": [
            r"quiz\s+me",
            r"test\s+my\s+knowledge",
            r"give\s+me\s+.+\s+questions",
            r"practice\s+.+",
            r"assess\s+my\s+.+"
        ],
        "priority": 1
    },
    "socratic_tutor": {
        "keywords": ["help me think", "guide me", "stuck", "don't tell me", "don't give me the answer"],
        "patterns": [
            r"help\s+me\s+(think|understand)",
            r"guide\s+me\s+through",
            r"i('m|\s+am)\s+stuck",
            r"don't\s+(tell|give)\s+me\s+(the\s+)?answer"
        ],
        "priority": 1
    },
    "progress_motivator": {
        "keywords": ["progress", "streak", "achievements", "how am I doing", "my stats"],
        "patterns": [
            r"(my|show)\s+progress",
            r"(my|current)\s+streak",
            r"(my|show)\s+achievements",
            r"how\s+(am\s+I|'m\s+I)\s+doing"
        ],
        "priority": 1
    }
}

# Default behavior when no skill matches
DEFAULT_BEHAVIOR = "concept_explainer"  # Most common user need
```

---

## Conversation Flow Examples

### Example 1: Course Introduction

```
User: What will I learn in this course?

[ChatGPT calls: GET /modules]
[ChatGPT calls: GET /chapters]

ChatGPT: Welcome to the AI Agent Development course! 🎓

This comprehensive course will teach you to build autonomous AI agents. Here's what you'll master:

**Module 1: Foundations** (Free)
- Introduction to AI Agents
- Claude Agent SDK Fundamentals
- MCP Integration

**Module 2: Skills Development** (Premium)
- SKILL.md Structure
- Procedural Knowledge
- Runtime Skills

**Module 3: Agentic Workflows** (Premium)
- Orchestration Patterns
- Multi-Agent Systems
- Production Deployment

By the end, you'll be able to build production-ready AI agents. Ready to start with Chapter 1?
```

### Example 2: Concept Explanation

```
User: Explain MCP to me

[ChatGPT calls: GET /chapters/ch3-mcp-integration]

ChatGPT: Great question! Let me explain MCP (Model Context Protocol).

**What is MCP?**
MCP is a standardized protocol that allows AI agents to connect to external tools and services. Think of it as a "universal adapter" for your agent.

**Why does it matter?**
- Enables agents to access databases, APIs, and file systems
- Provides a consistent interface regardless of the tool
- Makes agents truly useful by connecting them to real-world data

**Key Components:**
1. **Servers** - Expose tools and resources
2. **Clients** - Connect agents to servers
3. **Transport** - Communication layer (stdio, HTTP)

Would you like me to dive deeper into any of these, or shall we move on to a practical example?
```

### Example 3: Quiz Session

```
User: Quiz me on Chapter 1

[ChatGPT calls: GET /quizzes?chapter_id=ch1-intro-to-agents]
[ChatGPT calls: GET /quizzes/quiz-ch1-intro-001]

ChatGPT: Let's test your AI Agents knowledge! 📝

**Question 1 of 5:**
What is the primary purpose of an AI Agent?

A) To replace human workers
B) To autonomously complete tasks using tools
C) To generate random text
D) To store data in databases

Take your time and type your answer (A, B, C, or D).

---

User: B

[ChatGPT calls: POST /quizzes/quiz-ch1-intro-001/submit with single answer]

ChatGPT: ✅ Correct!

AI Agents are designed to autonomously complete tasks using tools and APIs. They combine LLM reasoning with the ability to take action in the real world.

**Question 2 of 5:**
Which protocol allows AI Agents to connect to external tools?

A) HTTP
B) MCP (Model Context Protocol)
C) FTP
D) SMTP

---
[continues for all questions...]
```

### Example 4: Socratic Teaching

```
User: Help me understand how agents make decisions. Don't just give me the answer.

ChatGPT: Excellent approach! Let's explore this together. 🤔

First, let me ask: When you make a decision, what factors do you consider?

---

User: I think about the goal, available options, and consequences

ChatGPT: Perfect! You're already thinking like an agent designer.

Now, AI agents follow a similar pattern. They have something called a "reasoning loop."

What do you think happens first when an agent receives a task? Does it:
1. Immediately take action
2. Think about the task first
3. Ask for help

---

User: Think about it first?

ChatGPT: Exactly right!

The agent first **interprets** the task. But here's where it gets interesting - after thinking, what does the agent need before it can act?

Hint: You mentioned "available options" in your decision-making process...

---

User: It needs to know what tools it has?

ChatGPT: Brilliant! You've discovered a key concept.

Agents need **tool awareness** - they must know what capabilities they have. This is why MCP is so important (Chapter 3).

So we have: Interpret → Know Tools → ???

What do you think comes next in the loop?
```

### Example 5: Progress Check

```
User: How's my progress?

[ChatGPT calls: GET /progress/{user_id}]
[ChatGPT calls: GET /progress/{user_id}/streak]
[ChatGPT calls: GET /progress/{user_id}/achievements]

ChatGPT: Let's see how you're doing! 📊

**Overall Progress: 44%**
━━━━━━━━━━░░░░░░░░░░ 4/9 chapters

**Module Status:**
✅ Module 1: Foundations - COMPLETE (100%)
🔄 Module 2: Skills Development - In Progress (33%)
🔒 Module 3: Agentic Workflows - Locked (0%)

**🔥 Streak: 5 Days!**
You're building a great learning habit. Just 2 more days to earn the "Week Warrior" achievement!

**Recent Achievements:**
🏆 First Steps - Complete your first chapter
🏆 Foundation Master - Complete Module 1
🏆 High Five - 5-day streak

**Next Step:**
Continue with "SKILL.md Structure" to unlock Module 3 content.

Keep up the amazing work! 💪
```

---

## Error Handling

### API Error Responses

```markdown
When the backend returns errors, handle gracefully:

**404 - Content Not Found:**
"I couldn't find that chapter. Let me show you what's available..."
[Call GET /chapters to list available content]

**403 - Premium Content:**
"That content is part of our premium curriculum. You're currently on the free tier. Would you like to learn about upgrading, or shall we explore the free content first?"

**429 - Rate/Attempt Limit:**
"You've used all your quiz attempts for now. Great effort! The attempts will reset tomorrow. In the meantime, would you like to review the chapter content?"

**500 - Server Error:**
"I'm having trouble connecting to the course server right now. Let's try again in a moment. In the meantime, I can answer general questions about AI Agents."
```

---

## Testing Requirements

### GPT Behavior Tests

```yaml
Test Cases:

1. Concept Explanation:
   Input: "What is an AI Agent?"
   Expected: Calls GET /chapters/ch1-intro-to-agents, provides structured explanation

2. Quiz Flow:
   Input: "Quiz me on chapter 1"
   Expected: Calls quiz endpoints in sequence, presents questions one at a time

3. Progress Check:
   Input: "Show my progress"
   Expected: Calls progress endpoints, presents encouraging summary

4. Socratic Mode:
   Input: "Help me understand MCP without giving me the answer"
   Expected: Asks probing questions, never reveals direct answer

5. Error Handling:
   Input: "Explain chapter 99"
   Expected: Gracefully handles 404, suggests available chapters

6. Skill Routing:
   Input: "explain" → concept_explainer
   Input: "quiz me" → quiz_master
   Input: "guide me" → socratic_tutor
   Input: "my streak" → progress_motivator
```

### API Integration Tests

```yaml
Test Endpoints:

1. Content Delivery:
   - GET /chapters/ch1-intro-to-agents returns content
   - GET /chapters?module=1 returns filtered list

2. Quiz Flow:
   - GET /quizzes returns quiz list
   - GET /quizzes/{id} returns questions without answers
   - POST /quizzes/{id}/submit returns graded results

3. Progress:
   - GET /progress/{user_id} returns progress summary
   - GET /progress/{user_id}/streak returns streak data
   - PUT /progress/{user_id}/chapters/{id} marks complete
```

---

## Deployment Checklist

### Pre-Launch

```markdown
[ ] OpenAPI schema validates against OpenAI requirements
[ ] All endpoints respond within 10 seconds
[ ] OAuth flow tested end-to-end
[ ] System instructions tested for each skill
[ ] Error messages are user-friendly
[ ] Rate limiting handles GPT's request patterns
```

### GPT Store Submission

```markdown
[ ] Name: "AI Agent Development Tutor"
[ ] Description: Under 300 characters
[ ] Conversation starters: 4 engaging prompts
[ ] Privacy policy URL configured
[ ] Category: Education
[ ] Logo: 512x512 PNG uploaded
```

---

## Performance Requirements

- **API Response Time:** < 3 seconds (OpenAI timeout is 45s)
- **Action Success Rate:** > 99%
- **User Session Duration:** Target 15+ minutes
- **Daily Active Users:** Support 10K concurrent

---

## Success Criteria

✅ **Zero-Backend-LLM Compliance:**
- All intelligence in ChatGPT
- Backend only serves data
- No LLM imports in backend code

✅ **User Experience:**
- Natural conversation flow
- Accurate skill routing
- Helpful error messages
- Encouraging tone

✅ **Technical:**
- Valid OpenAPI 3.1 schema
- OAuth authentication working
- All 16 endpoints integrated
- < 3 second response times

✅ **Educational:**
- Clear concept explanations
- Engaging quiz experience
- Effective Socratic guidance
- Motivating progress feedback

---

**Spec Version:** 1.0
**Last Updated:** January 15, 2026
**Status:** Ready for Implementation