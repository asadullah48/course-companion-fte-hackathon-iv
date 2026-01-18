# Backend API Specification: Quiz & Assessment
## Phase 1 - Zero-Backend-LLM Architecture

**API Version:** 1.0
**Responsibility:** Serve quizzes and grade answers using deterministic matching
**Intelligence Level:** ZERO (Answer Key Matching Only)

---

## Constitutional Compliance

✅ **ALLOWED:** Serve quiz questions from storage
✅ **ALLOWED:** Grade answers by exact match against answer key
✅ **ALLOWED:** Calculate scores using arithmetic operations
❌ **FORBIDDEN:** ANY LLM-based answer evaluation
❌ **FORBIDDEN:** Free-text response grading
❌ **FORBIDDEN:** AI-generated feedback or explanations

**Reference:** `specs/phase1/constitution/01-IMMUTABLE-RULES.md`

---

## API Endpoints

### 1. List Available Quizzes

**Endpoint:** `GET /api/v1/quizzes`

**Purpose:** Get list of quizzes filtered by chapter or module

**Query Parameters:**
- `chapter_id` (string, optional): Filter quizzes for specific chapter
- `module_id` (integer, optional): Filter quizzes for specific module
- `type` (string, optional): Quiz type filter
  - `chapter` (default): End-of-chapter quizzes
  - `module`: Module comprehensive quizzes
  - `practice`: Practice quizzes
- `difficulty` (string, optional): Filter by difficulty
  - `beginner`, `intermediate`, `advanced`

**Request Example:**
```http
GET /api/v1/quizzes?chapter_id=ch1-intro-to-agents&type=chapter
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "quizzes": [
    {
      "quiz_id": "quiz-ch1-intro-001",
      "title": "Introduction to AI Agents Quiz",
      "chapter_id": "ch1-intro-to-agents",
      "module_id": 1,
      "type": "chapter",
      "question_count": 5,
      "difficulty": "beginner",
      "time_limit_minutes": 10,
      "passing_score": 80,
      "attempts_allowed": 3,
      "user_attempts": 1,
      "best_score": 80,
      "is_locked": false
    },
    {
      "quiz_id": "quiz-ch1-intro-practice",
      "title": "AI Agents Practice Questions",
      "chapter_id": "ch1-intro-to-agents",
      "module_id": 1,
      "type": "practice",
      "question_count": 10,
      "difficulty": "beginner",
      "time_limit_minutes": null,
      "passing_score": null,
      "attempts_allowed": null,
      "user_attempts": 3,
      "best_score": 90,
      "is_locked": false
    }
  ],
  "total_quizzes": 2,
  "completed_count": 1
}
```

---

### 2. Get Quiz Questions

**Endpoint:** `GET /api/v1/quizzes/{quiz_id}`

**Purpose:** Retrieve quiz questions WITHOUT correct answers

**Path Parameters:**
- `quiz_id` (string, required): Unique quiz identifier

**Query Parameters:**
- `shuffle` (boolean, optional): Randomize question order (default: `false`)

**Request Example:**
```http
GET /api/v1/quizzes/quiz-ch1-intro-001?shuffle=true
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "quiz_id": "quiz-ch1-intro-001",
  "title": "Introduction to AI Agents Quiz",
  "chapter_id": "ch1-intro-to-agents",
  "instructions": "Answer all questions. You have 10 minutes.",
  "time_limit_minutes": 10,
  "passing_score": 80,
  "questions": [
    {
      "question_id": "q1",
      "order": 1,
      "type": "multiple_choice",
      "text": "What is the primary purpose of an AI Agent?",
      "options": [
        {"id": "a", "text": "To replace human workers"},
        {"id": "b", "text": "To autonomously complete tasks using tools"},
        {"id": "c", "text": "To generate random text"},
        {"id": "d", "text": "To store data in databases"}
      ],
      "points": 20
    },
    {
      "question_id": "q2",
      "order": 2,
      "type": "multiple_choice",
      "text": "Which protocol allows AI Agents to connect to external tools?",
      "options": [
        {"id": "a", "text": "HTTP"},
        {"id": "b", "text": "MCP (Model Context Protocol)"},
        {"id": "c", "text": "FTP"},
        {"id": "d", "text": "SMTP"}
      ],
      "points": 20
    },
    {
      "question_id": "q3",
      "order": 3,
      "type": "true_false",
      "text": "AI Agents can operate autonomously without any human intervention.",
      "options": [
        {"id": "true", "text": "True"},
        {"id": "false", "text": "False"}
      ],
      "points": 20
    },
    {
      "question_id": "q4",
      "order": 4,
      "type": "multiple_choice",
      "text": "What is Claude Agent SDK used for?",
      "options": [
        {"id": "a", "text": "Building web applications"},
        {"id": "b", "text": "Creating AI-powered agents"},
        {"id": "c", "text": "Database management"},
        {"id": "d", "text": "Image processing"}
      ],
      "points": 20
    },
    {
      "question_id": "q5",
      "order": 5,
      "type": "fill_blank",
      "text": "The 8-layer architecture for building agents is called the _____ Architecture.",
      "hint": "Starts with 'Agent'",
      "points": 20
    }
  ],
  "total_points": 100,
  "attempt_id": "attempt-uuid-12345",
  "started_at": "2026-01-15T14:30:00Z",
  "expires_at": "2026-01-15T14:40:00Z"
}
```

**Response 403 (Access Denied):**
```json
{
  "error": "access_denied",
  "message": "Premium subscription required for this quiz",
  "quiz_id": "quiz-ch1-intro-001",
  "required_tier": "premium"
}
```

**Response 429 (Attempts Exhausted):**
```json
{
  "error": "attempts_exhausted",
  "message": "Maximum attempts reached for this quiz",
  "quiz_id": "quiz-ch1-intro-001",
  "max_attempts": 3,
  "user_attempts": 3,
  "retry_after": "2026-01-16T00:00:00Z"
}
```

---

### 3. Submit Quiz Answers

**Endpoint:** `POST /api/v1/quizzes/{quiz_id}/submit`

**Purpose:** Submit answers and receive score (deterministic grading)

**Path Parameters:**
- `quiz_id` (string, required): Unique quiz identifier

**Request Body:**
```json
{
  "attempt_id": "attempt-uuid-12345",
  "answers": [
    {"question_id": "q1", "answer": "b"},
    {"question_id": "q2", "answer": "b"},
    {"question_id": "q3", "answer": "false"},
    {"question_id": "q4", "answer": "b"},
    {"question_id": "q5", "answer": "Agent Factory"}
  ]
}
```

**Request Example:**
```http
POST /api/v1/quizzes/quiz-ch1-intro-001/submit
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "attempt_id": "attempt-uuid-12345",
  "answers": [...]
}
```

**Response 200 (Success):**
```json
{
  "quiz_id": "quiz-ch1-intro-001",
  "attempt_id": "attempt-uuid-12345",
  "score": 80,
  "total_points": 100,
  "passing_score": 80,
  "passed": true,
  "time_taken_seconds": 420,
  "results": [
    {
      "question_id": "q1",
      "user_answer": "b",
      "correct_answer": "b",
      "is_correct": true,
      "points_earned": 20,
      "points_possible": 20,
      "explanation": "AI Agents are designed to autonomously complete tasks using tools and APIs."
    },
    {
      "question_id": "q2",
      "user_answer": "b",
      "correct_answer": "b",
      "is_correct": true,
      "points_earned": 20,
      "points_possible": 20,
      "explanation": "MCP (Model Context Protocol) enables AI Agents to connect to external tools."
    },
    {
      "question_id": "q3",
      "user_answer": "false",
      "correct_answer": "false",
      "is_correct": true,
      "points_earned": 20,
      "points_possible": 20,
      "explanation": "While agents can operate autonomously, they typically have human oversight."
    },
    {
      "question_id": "q4",
      "user_answer": "b",
      "correct_answer": "b",
      "is_correct": true,
      "points_earned": 20,
      "points_possible": 20,
      "explanation": "Claude Agent SDK provides tools for building AI-powered agents."
    },
    {
      "question_id": "q5",
      "user_answer": "Agent Factory",
      "correct_answer": "Agent Factory",
      "is_correct": true,
      "points_earned": 20,
      "points_possible": 20,
      "explanation": "The Agent Factory Architecture consists of 8 layers for building agents."
    }
  ],
  "summary": {
    "correct_count": 5,
    "incorrect_count": 0,
    "skipped_count": 0,
    "percentage": 100
  },
  "submitted_at": "2026-01-15T14:37:00Z"
}
```

**Response 400 (Invalid Submission):**
```json
{
  "error": "invalid_submission",
  "message": "Attempt has already been submitted",
  "attempt_id": "attempt-uuid-12345"
}
```

**Response 408 (Time Expired):**
```json
{
  "error": "time_expired",
  "message": "Quiz time limit exceeded",
  "quiz_id": "quiz-ch1-intro-001",
  "attempt_id": "attempt-uuid-12345",
  "time_limit_minutes": 10,
  "actual_time_minutes": 15
}
```

---

### 4. Get Quiz Results History

**Endpoint:** `GET /api/v1/quizzes/{quiz_id}/results/{attempt_id}`

**Purpose:** Retrieve detailed results for a specific attempt

**Path Parameters:**
- `quiz_id` (string, required): Unique quiz identifier
- `attempt_id` (string, required): Unique attempt identifier

**Request Example:**
```http
GET /api/v1/quizzes/quiz-ch1-intro-001/results/attempt-uuid-12345
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "quiz_id": "quiz-ch1-intro-001",
  "attempt_id": "attempt-uuid-12345",
  "user_id": "user-123",
  "score": 80,
  "total_points": 100,
  "passed": true,
  "attempt_number": 1,
  "started_at": "2026-01-15T14:30:00Z",
  "submitted_at": "2026-01-15T14:37:00Z",
  "time_taken_seconds": 420,
  "results": [
    {
      "question_id": "q1",
      "question_text": "What is the primary purpose of an AI Agent?",
      "user_answer": "b",
      "user_answer_text": "To autonomously complete tasks using tools",
      "correct_answer": "b",
      "correct_answer_text": "To autonomously complete tasks using tools",
      "is_correct": true,
      "points_earned": 20,
      "explanation": "AI Agents are designed to autonomously complete tasks using tools and APIs."
    }
  ],
  "comparison": {
    "best_score": 80,
    "average_score": 80,
    "total_attempts": 1
  }
}
```

**Response 404 (Not Found):**
```json
{
  "error": "result_not_found",
  "message": "Quiz attempt not found",
  "quiz_id": "quiz-ch1-intro-001",
  "attempt_id": "attempt-uuid-12345"
}
```

---

## Question Types & Grading Logic

### 1. Multiple Choice (Exact Match)

```python
# ✅ ALLOWED: Exact string comparison
def grade_multiple_choice(user_answer: str, correct_answer: str) -> bool:
    """Grade by exact option ID match"""
    return user_answer.strip().lower() == correct_answer.strip().lower()

# Example
grade_multiple_choice("b", "b")  # True
grade_multiple_choice("B", "b")  # True (case insensitive)
grade_multiple_choice("a", "b")  # False
```

### 2. True/False (Boolean Match)

```python
# ✅ ALLOWED: Boolean string comparison
def grade_true_false(user_answer: str, correct_answer: str) -> bool:
    """Grade by boolean value match"""
    user_bool = user_answer.strip().lower() in ("true", "t", "yes", "1")
    correct_bool = correct_answer.strip().lower() in ("true", "t", "yes", "1")
    return user_bool == correct_bool

# Example
grade_true_false("true", "true")  # True
grade_true_false("True", "true")  # True
grade_true_false("false", "true") # False
```

### 3. Fill-in-Blank (Normalized String Match)

```python
# ✅ ALLOWED: Normalized string comparison
import re

def grade_fill_blank(user_answer: str, correct_answer: str, aliases: list = None) -> bool:
    """
    Grade by normalized string match.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ String normalization (lowercase, trim)
    - ✅ Pre-defined alias matching
    - ❌ NO LLM semantic similarity
    - ❌ NO fuzzy matching without explicit rules
    """
    def normalize(text: str) -> str:
        # Lowercase, remove extra spaces, remove punctuation
        text = text.strip().lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text

    user_normalized = normalize(user_answer)
    correct_normalized = normalize(correct_answer)

    # Check exact match
    if user_normalized == correct_normalized:
        return True

    # Check pre-defined aliases (NOT AI-generated)
    if aliases:
        for alias in aliases:
            if user_normalized == normalize(alias):
                return True

    return False

# Example
grade_fill_blank("Agent Factory", "Agent Factory")  # True
grade_fill_blank("agent factory", "Agent Factory")  # True
grade_fill_blank("AgentFactory", "Agent Factory", aliases=["AgentFactory", "agent-factory"])  # True
grade_fill_blank("Factory Agent", "Agent Factory")  # False (no LLM to detect similarity)
```

---

## Answer Key Storage Schema

### Database Schema (PostgreSQL)

```sql
-- Quiz definitions
CREATE TABLE quizzes (
    quiz_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    chapter_id VARCHAR(100) REFERENCES chapters(chapter_id),
    module_id INTEGER REFERENCES modules(module_id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('chapter', 'module', 'practice')),
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
    time_limit_minutes INTEGER,
    passing_score INTEGER DEFAULT 80,
    attempts_allowed INTEGER DEFAULT 3,
    instructions TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Quiz questions with pre-stored correct answers
CREATE TABLE quiz_questions (
    question_id VARCHAR(100) PRIMARY KEY,
    quiz_id VARCHAR(100) REFERENCES quizzes(quiz_id),
    order_num INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('multiple_choice', 'true_false', 'fill_blank')),
    text TEXT NOT NULL,
    hint TEXT,
    options JSONB,  -- Array of {id, text} for MC/TF questions
    correct_answer VARCHAR(255) NOT NULL,  -- Pre-stored correct answer
    aliases JSONB DEFAULT '[]',  -- Pre-defined acceptable answers for fill_blank
    explanation TEXT NOT NULL,  -- Pre-written explanation (NOT LLM-generated)
    points INTEGER DEFAULT 20,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User quiz attempts
CREATE TABLE quiz_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id VARCHAR(100) REFERENCES quizzes(quiz_id),
    user_id VARCHAR(100) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMP,
    expired_at TIMESTAMP,
    score INTEGER,
    passed BOOLEAN,
    answers JSONB,  -- User's submitted answers
    results JSONB,  -- Graded results per question
    time_taken_seconds INTEGER
);

-- Indexes for performance
CREATE INDEX idx_quiz_attempts_user ON quiz_attempts(user_id, quiz_id);
CREATE INDEX idx_quiz_questions_quiz ON quiz_questions(quiz_id);
CREATE INDEX idx_quizzes_chapter ON quizzes(chapter_id);
```

---

## Implementation Requirements

### FastAPI Implementation Pattern

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/v1")

class Answer(BaseModel):
    question_id: str
    answer: str

class QuizSubmission(BaseModel):
    attempt_id: str
    answers: List[Answer]

@router.get("/quizzes")
async def list_quizzes(
    chapter_id: Optional[str] = None,
    module_id: Optional[int] = None,
    type: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """
    List available quizzes with user's attempt history.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database query (deterministic)
    - ✅ User progress lookup
    - ❌ NO LLM recommendations
    """
    query = "SELECT * FROM quizzes WHERE 1=1"
    params = []

    if chapter_id:
        query += " AND chapter_id = $1"
        params.append(chapter_id)
    if module_id:
        query += " AND module_id = $2"
        params.append(module_id)
    if type:
        query += " AND type = $3"
        params.append(type)

    quizzes = await db.fetch(query, *params)

    # Add user attempt data
    for quiz in quizzes:
        attempts = await db.fetch(
            "SELECT * FROM quiz_attempts WHERE quiz_id = $1 AND user_id = $2",
            quiz["quiz_id"], user["id"]
        )
        quiz["user_attempts"] = len(attempts)
        quiz["best_score"] = max([a["score"] for a in attempts], default=None)

    return {"quizzes": quizzes, "total_quizzes": len(quizzes)}


@router.get("/quizzes/{quiz_id}")
async def get_quiz(
    quiz_id: str,
    shuffle: bool = False,
    user: dict = Depends(get_current_user)
):
    """
    Get quiz questions (without correct answers).

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Serve questions from database
    - ✅ Shuffle order (deterministic random)
    - ❌ NO correct answers exposed
    - ❌ NO LLM-generated questions
    """

    # Check attempt limits
    attempts = await db.fetch(
        "SELECT COUNT(*) FROM quiz_attempts WHERE quiz_id = $1 AND user_id = $2",
        quiz_id, user["id"]
    )
    quiz = await db.fetchrow("SELECT * FROM quizzes WHERE quiz_id = $1", quiz_id)

    if quiz["attempts_allowed"] and attempts >= quiz["attempts_allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "attempts_exhausted",
                "message": "Maximum attempts reached",
                "max_attempts": quiz["attempts_allowed"]
            }
        )

    # Get questions WITHOUT correct_answer field
    questions = await db.fetch(
        """
        SELECT question_id, order_num as order, type, text, hint, options, points
        FROM quiz_questions
        WHERE quiz_id = $1
        ORDER BY order_num
        """,
        quiz_id
    )

    if shuffle:
        import random
        random.shuffle(questions)

    # Create attempt record
    attempt_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=quiz["time_limit_minutes"]) if quiz["time_limit_minutes"] else None

    await db.execute(
        """
        INSERT INTO quiz_attempts (attempt_id, quiz_id, user_id, expired_at)
        VALUES ($1, $2, $3, $4)
        """,
        attempt_id, quiz_id, user["id"], expires_at
    )

    return {
        "quiz_id": quiz_id,
        "title": quiz["title"],
        "instructions": quiz["instructions"],
        "time_limit_minutes": quiz["time_limit_minutes"],
        "passing_score": quiz["passing_score"],
        "questions": questions,
        "total_points": sum(q["points"] for q in questions),
        "attempt_id": attempt_id,
        "started_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None
    }


@router.post("/quizzes/{quiz_id}/submit")
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    user: dict = Depends(get_current_user)
):
    """
    Submit quiz answers and receive score.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Exact answer key matching
    - ✅ Pre-stored explanations (NOT LLM-generated)
    - ✅ Arithmetic score calculation
    - ❌ NO LLM grading
    - ❌ NO AI-generated feedback
    """

    # Verify attempt exists and not already submitted
    attempt = await db.fetchrow(
        "SELECT * FROM quiz_attempts WHERE attempt_id = $1 AND user_id = $2",
        submission.attempt_id, user["id"]
    )

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    if attempt["submitted_at"]:
        raise HTTPException(status_code=400, detail="Already submitted")

    # Check time limit
    if attempt["expired_at"] and datetime.utcnow() > attempt["expired_at"]:
        raise HTTPException(status_code=408, detail="Time expired")

    # Get questions with correct answers
    questions = await db.fetch(
        "SELECT * FROM quiz_questions WHERE quiz_id = $1",
        quiz_id
    )
    questions_map = {q["question_id"]: q for q in questions}

    # Grade each answer (DETERMINISTIC ONLY)
    results = []
    total_score = 0

    for answer in submission.answers:
        question = questions_map.get(answer.question_id)
        if not question:
            continue

        # Deterministic grading based on question type
        if question["type"] == "multiple_choice":
            is_correct = grade_multiple_choice(answer.answer, question["correct_answer"])
        elif question["type"] == "true_false":
            is_correct = grade_true_false(answer.answer, question["correct_answer"])
        elif question["type"] == "fill_blank":
            is_correct = grade_fill_blank(
                answer.answer,
                question["correct_answer"],
                question.get("aliases", [])
            )
        else:
            is_correct = False

        points_earned = question["points"] if is_correct else 0
        total_score += points_earned

        results.append({
            "question_id": answer.question_id,
            "user_answer": answer.answer,
            "correct_answer": question["correct_answer"],
            "is_correct": is_correct,
            "points_earned": points_earned,
            "points_possible": question["points"],
            "explanation": question["explanation"]  # Pre-stored, NOT generated
        })

    # Calculate final score
    quiz = await db.fetchrow("SELECT * FROM quizzes WHERE quiz_id = $1", quiz_id)
    total_points = sum(q["points"] for q in questions)
    passed = total_score >= (quiz["passing_score"] * total_points / 100)

    # Save results
    time_taken = int((datetime.utcnow() - attempt["started_at"]).total_seconds())

    await db.execute(
        """
        UPDATE quiz_attempts
        SET submitted_at = NOW(), score = $1, passed = $2, answers = $3,
            results = $4, time_taken_seconds = $5
        WHERE attempt_id = $6
        """,
        total_score, passed, submission.answers, results, time_taken, submission.attempt_id
    )

    return {
        "quiz_id": quiz_id,
        "attempt_id": submission.attempt_id,
        "score": total_score,
        "total_points": total_points,
        "passing_score": quiz["passing_score"],
        "passed": passed,
        "time_taken_seconds": time_taken,
        "results": results,
        "summary": {
            "correct_count": sum(1 for r in results if r["is_correct"]),
            "incorrect_count": sum(1 for r in results if not r["is_correct"]),
            "skipped_count": len(questions) - len(results),
            "percentage": round(total_score / total_points * 100) if total_points > 0 else 0
        },
        "submitted_at": datetime.utcnow().isoformat()
    }


@router.get("/quizzes/{quiz_id}/results/{attempt_id}")
async def get_quiz_results(
    quiz_id: str,
    attempt_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get detailed results for a specific attempt.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database retrieval
    - ✅ Pre-stored data only
    - ❌ NO LLM analysis
    """
    attempt = await db.fetchrow(
        """
        SELECT * FROM quiz_attempts
        WHERE attempt_id = $1 AND quiz_id = $2 AND user_id = $3
        """,
        attempt_id, quiz_id, user["id"]
    )

    if not attempt:
        raise HTTPException(status_code=404, detail="Result not found")

    # Get comparison stats
    all_attempts = await db.fetch(
        "SELECT score FROM quiz_attempts WHERE quiz_id = $1 AND user_id = $2 AND submitted_at IS NOT NULL",
        quiz_id, user["id"]
    )

    return {
        "quiz_id": quiz_id,
        "attempt_id": attempt_id,
        "user_id": user["id"],
        "score": attempt["score"],
        "total_points": sum(r["points_possible"] for r in attempt["results"]),
        "passed": attempt["passed"],
        "attempt_number": len(all_attempts),
        "started_at": attempt["started_at"].isoformat(),
        "submitted_at": attempt["submitted_at"].isoformat(),
        "time_taken_seconds": attempt["time_taken_seconds"],
        "results": attempt["results"],
        "comparison": {
            "best_score": max(a["score"] for a in all_attempts),
            "average_score": sum(a["score"] for a in all_attempts) / len(all_attempts),
            "total_attempts": len(all_attempts)
        }
    }
```

---

## Performance Requirements

- **Response Time:** < 100ms (p95) for all endpoints
- **Throughput:** 500 quiz submissions/minute
- **Availability:** 99.9% uptime
- **Database Query Time:** < 50ms for grading

---

## Security Requirements

1. **Authentication:** JWT Bearer tokens required for all endpoints
2. **Authorization:**
   - Users can only access their own attempts
   - Premium quizzes require subscription check
3. **Rate Limiting:** 10 quiz submissions/minute per user
4. **Attempt Validation:**
   - Verify attempt belongs to user
   - Check time limits before accepting submission
   - Prevent duplicate submissions

---

## Testing Requirements

### Unit Tests

```python
def test_list_quizzes():
    """Test quiz listing with filters"""
    response = client.get("/api/v1/quizzes?chapter_id=ch1-intro-to-agents")
    assert response.status_code == 200
    assert "quizzes" in response.json()

def test_get_quiz_no_answers():
    """Verify correct answers are not exposed"""
    response = client.get("/api/v1/quizzes/quiz-ch1-intro-001")
    assert response.status_code == 200
    for question in response.json()["questions"]:
        assert "correct_answer" not in question

def test_submit_quiz_correct():
    """Test correct answer grading"""
    # Setup: Get quiz first
    quiz = client.get("/api/v1/quizzes/quiz-ch1-intro-001").json()

    response = client.post(
        "/api/v1/quizzes/quiz-ch1-intro-001/submit",
        json={
            "attempt_id": quiz["attempt_id"],
            "answers": [
                {"question_id": "q1", "answer": "b"},
                {"question_id": "q2", "answer": "b"}
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["passed"] == True

def test_submit_quiz_incorrect():
    """Test incorrect answer grading"""
    response = client.post(
        "/api/v1/quizzes/quiz-ch1-intro-001/submit",
        json={
            "attempt_id": "test-attempt",
            "answers": [
                {"question_id": "q1", "answer": "a"}  # Wrong answer
            ]
        }
    )
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["is_correct"] == False
    assert result["points_earned"] == 0

def test_fill_blank_case_insensitive():
    """Test fill-in-blank accepts case variations"""
    assert grade_fill_blank("Agent Factory", "agent factory") == True
    assert grade_fill_blank("AGENT FACTORY", "agent factory") == True

def test_fill_blank_aliases():
    """Test fill-in-blank accepts pre-defined aliases"""
    assert grade_fill_blank("AgentFactory", "Agent Factory", ["AgentFactory"]) == True

def test_attempt_limit_enforcement():
    """Test that attempt limits are enforced"""
    # Exhaust attempts
    for _ in range(3):
        quiz = client.get("/api/v1/quizzes/quiz-ch1-intro-001").json()
        client.post(f"/api/v1/quizzes/quiz-ch1-intro-001/submit", json={
            "attempt_id": quiz["attempt_id"],
            "answers": []
        })

    # Next attempt should fail
    response = client.get("/api/v1/quizzes/quiz-ch1-intro-001")
    assert response.status_code == 429

def test_time_limit_enforcement():
    """Test that time limits are enforced"""
    # Submit after time expires
    response = client.post(
        "/api/v1/quizzes/quiz-ch1-intro-001/submit",
        json={"attempt_id": "expired-attempt", "answers": []}
    )
    assert response.status_code == 408
```

### Integration Tests

- Database connection verification
- Foreign key constraint validation
- Concurrent submission handling
- Time zone handling for expiry

---

## Monitoring & Observability

### Metrics to Track
- Quiz completion rate
- Average score by chapter
- Time taken distribution
- Attempt exhaustion rate
- Failed submission reasons

### Logging
```python
logger.info(
    "quiz_submitted",
    quiz_id=quiz_id,
    user_id=user_id,
    score=score,
    passed=passed,
    time_taken=time_taken,
    attempt_number=attempt_number
)
```

---

## Cost Analysis

### Per Request Cost (10K users, 20 quizzes/user/month)
```
Database Operations:
- Read queries: 200K reads/month
- Write operations: 200K writes/month
- Neon free tier: 3B reads included

Compute:
- Grading: Pure Python (no LLM)
- No external API calls
- CPU only, no GPU required

Total: ~$0.00 additional cost (within free tier)
```

---

## Success Criteria

✅ **Zero-Backend-LLM Compliance:**
- No LLM imports in module
- No LLM-based answer evaluation
- All grading is deterministic (exact match)
- All explanations are pre-stored

✅ **Performance:**
- P95 latency < 100ms
- Grading < 50ms per quiz

✅ **Functionality:**
- All 4 endpoints implemented
- 3 question types supported (MC, TF, Fill-blank)
- Attempt limits enforced
- Time limits enforced

✅ **Security:**
- User can only access own attempts
- Correct answers never exposed before submission
- Rate limiting in place

---

**Spec Version:** 1.0
**Last Updated:** January 15, 2026
**Status:** Ready for Implementation
