# Backend API Specification: Progress Tracking
## Phase 1 - Zero-Backend-LLM Architecture

**API Version:** 1.0
**Responsibility:** Track user progress, streaks, and achievements using SQL operations
**Intelligence Level:** ZERO (Database Operations Only)

---

## Constitutional Compliance

✅ **ALLOWED:** SQL-based progress calculations
✅ **ALLOWED:** Rule-based achievement unlocking
✅ **ALLOWED:** Arithmetic operations (percentage, streak count)
❌ **FORBIDDEN:** LLM-based progress recommendations
❌ **FORBIDDEN:** AI-generated motivational messages
❌ **FORBIDDEN:** Personalized learning path suggestions via AI

**Reference:** `specs/phase1/constitution/01-IMMUTABLE-RULES.md`

---

## API Endpoints

### 1. Get User Progress Summary

**Endpoint:** `GET /api/v1/progress/{user_id}`

**Purpose:** Retrieve overall progress across all modules and chapters

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `include_chapters` (boolean, optional): Include chapter-level details (default: `false`)

**Request Example:**
```http
GET /api/v1/progress/user-123?include_chapters=true
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "user_id": "user-123",
  "overall": {
    "total_chapters": 9,
    "completed_chapters": 4,
    "completion_percentage": 44,
    "total_time_minutes": 180,
    "current_module": 2,
    "current_chapter": "ch4-skill-md-structure"
  },
  "modules": [
    {
      "module_id": 1,
      "title": "Foundations",
      "total_chapters": 3,
      "completed_chapters": 3,
      "completion_percentage": 100,
      "time_spent_minutes": 90,
      "status": "completed"
    },
    {
      "module_id": 2,
      "title": "Skills Development",
      "total_chapters": 3,
      "completed_chapters": 1,
      "completion_percentage": 33,
      "time_spent_minutes": 60,
      "status": "in_progress"
    },
    {
      "module_id": 3,
      "title": "Agentic Workflows",
      "total_chapters": 3,
      "completed_chapters": 0,
      "completion_percentage": 0,
      "time_spent_minutes": 0,
      "status": "locked"
    }
  ],
  "chapters": [
    {
      "chapter_id": "ch1-intro-to-agents",
      "title": "Introduction to AI Agents",
      "module_id": 1,
      "status": "completed",
      "completed_at": "2026-01-10T10:30:00Z",
      "time_spent_minutes": 25,
      "quiz_score": 90
    },
    {
      "chapter_id": "ch2-claude-agent-sdk",
      "title": "Claude Agent SDK Fundamentals",
      "module_id": 1,
      "status": "completed",
      "completed_at": "2026-01-11T14:15:00Z",
      "time_spent_minutes": 35,
      "quiz_score": 85
    },
    {
      "chapter_id": "ch3-mcp-integration",
      "title": "MCP Integration",
      "module_id": 1,
      "status": "completed",
      "completed_at": "2026-01-12T09:00:00Z",
      "time_spent_minutes": 30,
      "quiz_score": 80
    },
    {
      "chapter_id": "ch4-skill-md-structure",
      "title": "SKILL.md Structure",
      "module_id": 2,
      "status": "in_progress",
      "started_at": "2026-01-13T11:00:00Z",
      "time_spent_minutes": 15,
      "quiz_score": null
    }
  ],
  "last_activity": "2026-01-15T08:30:00Z",
  "member_since": "2026-01-10T00:00:00Z"
}
```

---

### 2. Mark Chapter Complete

**Endpoint:** `PUT /api/v1/progress/{user_id}/chapters/{chapter_id}`

**Purpose:** Mark a chapter as complete (after quiz passed or content consumed)

**Path Parameters:**
- `user_id` (string, required): User identifier
- `chapter_id` (string, required): Chapter to mark complete

**Request Body:**
```json
{
  "completion_type": "quiz_passed",
  "quiz_attempt_id": "attempt-uuid-12345",
  "time_spent_minutes": 25
}
```

**Request Example:**
```http
PUT /api/v1/progress/user-123/chapters/ch1-intro-to-agents
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "completion_type": "quiz_passed",
  "quiz_attempt_id": "attempt-uuid-12345",
  "time_spent_minutes": 25
}
```

**Response 200 (Success):**
```json
{
  "user_id": "user-123",
  "chapter_id": "ch1-intro-to-agents",
  "status": "completed",
  "completed_at": "2026-01-15T14:30:00Z",
  "time_spent_minutes": 25,
  "progress_update": {
    "chapters_completed": 5,
    "total_chapters": 9,
    "completion_percentage": 56
  },
  "achievements_unlocked": [
    {
      "achievement_id": "first-chapter",
      "name": "First Steps",
      "description": "Complete your first chapter",
      "unlocked_at": "2026-01-15T14:30:00Z"
    }
  ],
  "streak_update": {
    "current_streak": 5,
    "is_new_day": true
  }
}
```

**Response 400 (Already Completed):**
```json
{
  "error": "already_completed",
  "message": "Chapter is already marked as complete",
  "chapter_id": "ch1-intro-to-agents",
  "completed_at": "2026-01-10T10:30:00Z"
}
```

**Response 403 (Prerequisites Not Met):**
```json
{
  "error": "prerequisites_not_met",
  "message": "Previous chapter must be completed first",
  "chapter_id": "ch5-procedural-knowledge",
  "required_chapters": ["ch4-skill-md-structure"]
}
```

---

### 3. Get Learning Streak

**Endpoint:** `GET /api/v1/progress/{user_id}/streak`

**Purpose:** Get current streak and streak history

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `history_days` (integer, optional): Number of days to include in history (default: 30)

**Request Example:**
```http
GET /api/v1/progress/user-123/streak?history_days=7
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "user_id": "user-123",
  "current_streak": 5,
  "longest_streak": 12,
  "streak_status": "active",
  "today_activity": true,
  "streak_at_risk": false,
  "hours_until_streak_loss": 18,
  "history": [
    {"date": "2026-01-15", "active": true, "time_spent_minutes": 45},
    {"date": "2026-01-14", "active": true, "time_spent_minutes": 30},
    {"date": "2026-01-13", "active": true, "time_spent_minutes": 60},
    {"date": "2026-01-12", "active": true, "time_spent_minutes": 25},
    {"date": "2026-01-11", "active": true, "time_spent_minutes": 40},
    {"date": "2026-01-10", "active": false, "time_spent_minutes": 0},
    {"date": "2026-01-09", "active": false, "time_spent_minutes": 0}
  ],
  "milestones": {
    "next_milestone": 7,
    "days_to_next": 2,
    "previous_milestones": [3, 5]
  },
  "freeze_available": true,
  "freezes_remaining": 2
}
```

---

### 4. Get Achievements

**Endpoint:** `GET /api/v1/progress/{user_id}/achievements`

**Purpose:** List all achievements (earned and locked)

**Path Parameters:**
- `user_id` (string, required): User identifier

**Query Parameters:**
- `filter` (string, optional): Filter achievements
  - `all` (default): All achievements
  - `earned`: Only earned achievements
  - `locked`: Only locked achievements

**Request Example:**
```http
GET /api/v1/progress/user-123/achievements?filter=all
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "user_id": "user-123",
  "total_achievements": 15,
  "earned_count": 6,
  "points_earned": 350,
  "points_possible": 1000,
  "achievements": [
    {
      "achievement_id": "first-chapter",
      "name": "First Steps",
      "description": "Complete your first chapter",
      "icon": "rocket",
      "points": 50,
      "category": "progress",
      "status": "earned",
      "unlocked_at": "2026-01-10T10:30:00Z",
      "progress": null
    },
    {
      "achievement_id": "module-1-complete",
      "name": "Foundation Master",
      "description": "Complete all chapters in Module 1",
      "icon": "trophy",
      "points": 100,
      "category": "modules",
      "status": "earned",
      "unlocked_at": "2026-01-12T09:00:00Z",
      "progress": null
    },
    {
      "achievement_id": "streak-7",
      "name": "Week Warrior",
      "description": "Maintain a 7-day learning streak",
      "icon": "fire",
      "points": 75,
      "category": "streaks",
      "status": "locked",
      "unlocked_at": null,
      "progress": {
        "current": 5,
        "required": 7,
        "percentage": 71
      }
    },
    {
      "achievement_id": "quiz-perfect",
      "name": "Perfect Score",
      "description": "Score 100% on any quiz",
      "icon": "star",
      "points": 50,
      "category": "quizzes",
      "status": "locked",
      "unlocked_at": null,
      "progress": {
        "best_score": 90,
        "required": 100,
        "percentage": 90
      }
    },
    {
      "achievement_id": "course-complete",
      "name": "Agent Expert",
      "description": "Complete the entire course",
      "icon": "medal",
      "points": 200,
      "category": "progress",
      "status": "locked",
      "unlocked_at": null,
      "progress": {
        "current": 4,
        "required": 9,
        "percentage": 44
      }
    }
  ],
  "recent_achievements": [
    {
      "achievement_id": "streak-5",
      "name": "High Five",
      "unlocked_at": "2026-01-15T08:30:00Z"
    }
  ]
}
```

---

### 5. Log Learning Time

**Endpoint:** `POST /api/v1/progress/{user_id}/time`

**Purpose:** Log time spent learning (for streak and analytics)

**Path Parameters:**
- `user_id` (string, required): User identifier

**Request Body:**
```json
{
  "chapter_id": "ch4-skill-md-structure",
  "duration_minutes": 15,
  "activity_type": "reading"
}
```

**Request Example:**
```http
POST /api/v1/progress/user-123/time
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "chapter_id": "ch4-skill-md-structure",
  "duration_minutes": 15,
  "activity_type": "reading"
}
```

**Response 200 (Success):**
```json
{
  "logged": true,
  "session_id": "session-uuid-12345",
  "chapter_id": "ch4-skill-md-structure",
  "duration_minutes": 15,
  "activity_type": "reading",
  "logged_at": "2026-01-15T14:45:00Z",
  "today_total_minutes": 45,
  "streak_maintained": true
}
```

---

## Achievement System

### Achievement Rules (Deterministic Only)

```python
# ✅ ALLOWED: Rule-based achievement checks
# ❌ FORBIDDEN: LLM-based achievement suggestions

ACHIEVEMENT_RULES = {
    # Progress Achievements
    "first-chapter": {
        "name": "First Steps",
        "description": "Complete your first chapter",
        "points": 50,
        "condition": lambda stats: stats["chapters_completed"] >= 1
    },
    "halfway-there": {
        "name": "Halfway There",
        "description": "Complete 50% of the course",
        "points": 75,
        "condition": lambda stats: stats["completion_percentage"] >= 50
    },
    "course-complete": {
        "name": "Agent Expert",
        "description": "Complete the entire course",
        "points": 200,
        "condition": lambda stats: stats["completion_percentage"] == 100
    },

    # Module Achievements
    "module-1-complete": {
        "name": "Foundation Master",
        "description": "Complete all chapters in Module 1",
        "points": 100,
        "condition": lambda stats: stats["modules_completed"].get(1, False)
    },
    "module-2-complete": {
        "name": "Skill Builder",
        "description": "Complete all chapters in Module 2",
        "points": 100,
        "condition": lambda stats: stats["modules_completed"].get(2, False)
    },
    "module-3-complete": {
        "name": "Workflow Wizard",
        "description": "Complete all chapters in Module 3",
        "points": 100,
        "condition": lambda stats: stats["modules_completed"].get(3, False)
    },

    # Streak Achievements
    "streak-3": {
        "name": "Hat Trick",
        "description": "Maintain a 3-day learning streak",
        "points": 25,
        "condition": lambda stats: stats["current_streak"] >= 3
    },
    "streak-5": {
        "name": "High Five",
        "description": "Maintain a 5-day learning streak",
        "points": 50,
        "condition": lambda stats: stats["current_streak"] >= 5
    },
    "streak-7": {
        "name": "Week Warrior",
        "description": "Maintain a 7-day learning streak",
        "points": 75,
        "condition": lambda stats: stats["current_streak"] >= 7
    },
    "streak-30": {
        "name": "Monthly Master",
        "description": "Maintain a 30-day learning streak",
        "points": 150,
        "condition": lambda stats: stats["current_streak"] >= 30
    },

    # Quiz Achievements
    "quiz-perfect": {
        "name": "Perfect Score",
        "description": "Score 100% on any quiz",
        "points": 50,
        "condition": lambda stats: stats["best_quiz_score"] == 100
    },
    "quiz-streak-3": {
        "name": "Quiz Champion",
        "description": "Pass 3 quizzes in a row",
        "points": 75,
        "condition": lambda stats: stats["quiz_pass_streak"] >= 3
    },

    # Time Achievements
    "time-1-hour": {
        "name": "Dedicated Learner",
        "description": "Spend 1 hour learning",
        "points": 25,
        "condition": lambda stats: stats["total_time_minutes"] >= 60
    },
    "time-5-hours": {
        "name": "Committed Student",
        "description": "Spend 5 hours learning",
        "points": 75,
        "condition": lambda stats: stats["total_time_minutes"] >= 300
    },
    "time-10-hours": {
        "name": "Agent Scholar",
        "description": "Spend 10 hours learning",
        "points": 100,
        "condition": lambda stats: stats["total_time_minutes"] >= 600
    }
}
```

---

## Streak Calculation Logic

### Core Streak Rules (Deterministic)

```python
from datetime import datetime, timedelta, timezone

def calculate_streak(user_id: str, user_timezone: str = "UTC") -> dict:
    """
    Calculate user's current learning streak.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL-based date calculations
    - ✅ Timezone-aware date handling
    - ❌ NO LLM-based predictions
    - ❌ NO AI-generated streak recommendations
    """

    # Get user's local date
    tz = timezone.utc  # Use pytz for production
    today = datetime.now(tz).date()

    # Get all activity dates
    activities = db.fetch(
        """
        SELECT DISTINCT DATE(logged_at AT TIME ZONE $2) as activity_date
        FROM learning_sessions
        WHERE user_id = $1
        ORDER BY activity_date DESC
        """,
        user_id, user_timezone
    )

    activity_dates = {row["activity_date"] for row in activities}

    # Calculate current streak
    current_streak = 0
    check_date = today

    # Check if today has activity (streak continues)
    today_activity = today in activity_dates

    # If no activity today, start from yesterday
    if not today_activity:
        check_date = today - timedelta(days=1)

    # Count consecutive days
    while check_date in activity_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Calculate hours until streak loss
    if today_activity:
        # Streak safe until end of tomorrow
        tomorrow_end = datetime.combine(today + timedelta(days=1), datetime.max.time())
        hours_remaining = (tomorrow_end - datetime.now(tz)).total_seconds() / 3600
    else:
        # Streak at risk - must act today
        today_end = datetime.combine(today, datetime.max.time())
        hours_remaining = (today_end - datetime.now(tz)).total_seconds() / 3600

    return {
        "current_streak": current_streak,
        "today_activity": today_activity,
        "streak_at_risk": not today_activity and current_streak > 0,
        "hours_until_streak_loss": max(0, hours_remaining)
    }
```

---

## Database Schema

```sql
-- Chapter completion tracking
CREATE TABLE chapter_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    chapter_id VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'not_started' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    time_spent_minutes INTEGER DEFAULT 0,
    quiz_score INTEGER,
    quiz_attempt_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, chapter_id)
);

-- Learning sessions for time tracking
CREATE TABLE learning_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    chapter_id VARCHAR(100),
    activity_type VARCHAR(20) CHECK (activity_type IN ('reading', 'quiz', 'review', 'practice')),
    duration_minutes INTEGER NOT NULL,
    logged_at TIMESTAMP DEFAULT NOW()
);

-- User achievements
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    achievement_id VARCHAR(100) NOT NULL,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);

-- Achievement definitions
CREATE TABLE achievements (
    achievement_id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(50),
    points INTEGER DEFAULT 0,
    category VARCHAR(50) CHECK (category IN ('progress', 'modules', 'streaks', 'quizzes', 'time')),
    sort_order INTEGER
);

-- User streak data (cached for performance)
CREATE TABLE user_streaks (
    user_id VARCHAR(100) PRIMARY KEY,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    freezes_remaining INTEGER DEFAULT 2,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_chapter_progress_user ON chapter_progress(user_id);
CREATE INDEX idx_learning_sessions_user_date ON learning_sessions(user_id, logged_at);
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
```

---

## Implementation Requirements

### FastAPI Implementation Pattern

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta

router = APIRouter(prefix="/api/v1")

class ChapterCompletion(BaseModel):
    completion_type: str  # "quiz_passed" | "content_read"
    quiz_attempt_id: Optional[str] = None
    time_spent_minutes: int

class TimeLog(BaseModel):
    chapter_id: str
    duration_minutes: int
    activity_type: str  # "reading" | "quiz" | "review" | "practice"

@router.get("/progress/{user_id}")
async def get_progress(
    user_id: str,
    include_chapters: bool = False,
    user: dict = Depends(get_current_user)
):
    """
    Get user progress summary.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL aggregation queries
    - ✅ Arithmetic percentage calculations
    - ❌ NO LLM analysis
    - ❌ NO AI recommendations
    """

    # Verify user can access this data
    if user["id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    # Get overall progress (SQL aggregation)
    overall = await db.fetchrow(
        """
        SELECT
            COUNT(*) FILTER (WHERE status = 'completed') as completed_chapters,
            COUNT(*) as total_chapters,
            SUM(time_spent_minutes) as total_time_minutes
        FROM chapter_progress cp
        JOIN chapters c ON cp.chapter_id = c.chapter_id
        WHERE cp.user_id = $1
        """,
        user_id
    )

    # Get module-level progress
    modules = await db.fetch(
        """
        SELECT
            m.module_id,
            m.title,
            COUNT(c.chapter_id) as total_chapters,
            COUNT(cp.chapter_id) FILTER (WHERE cp.status = 'completed') as completed_chapters,
            SUM(COALESCE(cp.time_spent_minutes, 0)) as time_spent_minutes
        FROM modules m
        JOIN chapters c ON c.module_id = m.module_id
        LEFT JOIN chapter_progress cp ON cp.chapter_id = c.chapter_id AND cp.user_id = $1
        GROUP BY m.module_id, m.title
        ORDER BY m.module_id
        """,
        user_id
    )

    # Calculate percentages (deterministic math)
    total = overall["total_chapters"] or 9  # Default course size
    completed = overall["completed_chapters"] or 0
    completion_percentage = round(completed / total * 100) if total > 0 else 0

    response = {
        "user_id": user_id,
        "overall": {
            "total_chapters": total,
            "completed_chapters": completed,
            "completion_percentage": completion_percentage,
            "total_time_minutes": overall["total_time_minutes"] or 0
        },
        "modules": [
            {
                "module_id": m["module_id"],
                "title": m["title"],
                "total_chapters": m["total_chapters"],
                "completed_chapters": m["completed_chapters"],
                "completion_percentage": round(m["completed_chapters"] / m["total_chapters"] * 100) if m["total_chapters"] > 0 else 0,
                "time_spent_minutes": m["time_spent_minutes"],
                "status": "completed" if m["completed_chapters"] == m["total_chapters"] else ("in_progress" if m["completed_chapters"] > 0 else "locked")
            }
            for m in modules
        ]
    }

    if include_chapters:
        chapters = await db.fetch(
            """
            SELECT
                c.chapter_id, c.title, c.module_id,
                COALESCE(cp.status, 'not_started') as status,
                cp.completed_at, cp.started_at, cp.time_spent_minutes, cp.quiz_score
            FROM chapters c
            LEFT JOIN chapter_progress cp ON cp.chapter_id = c.chapter_id AND cp.user_id = $1
            ORDER BY c.module_id, c.order_num
            """,
            user_id
        )
        response["chapters"] = chapters

    return response


@router.put("/progress/{user_id}/chapters/{chapter_id}")
async def mark_chapter_complete(
    user_id: str,
    chapter_id: str,
    completion: ChapterCompletion,
    user: dict = Depends(get_current_user)
):
    """
    Mark chapter as complete.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database update
    - ✅ Rule-based achievement checking
    - ❌ NO LLM validation
    """

    # Check if already completed
    existing = await db.fetchrow(
        "SELECT * FROM chapter_progress WHERE user_id = $1 AND chapter_id = $2",
        user_id, chapter_id
    )

    if existing and existing["status"] == "completed":
        raise HTTPException(status_code=400, detail="Already completed")

    # Check prerequisites (deterministic rule)
    chapter = await db.fetchrow(
        "SELECT * FROM chapters WHERE chapter_id = $1",
        chapter_id
    )

    if chapter["order_num"] > 1:
        prev_chapter = await db.fetchrow(
            """
            SELECT cp.status FROM chapters c
            JOIN chapter_progress cp ON cp.chapter_id = c.chapter_id
            WHERE c.module_id = $1 AND c.order_num = $2 AND cp.user_id = $3
            """,
            chapter["module_id"], chapter["order_num"] - 1, user_id
        )

        if not prev_chapter or prev_chapter["status"] != "completed":
            raise HTTPException(status_code=403, detail="Prerequisites not met")

    # Mark complete
    await db.execute(
        """
        INSERT INTO chapter_progress (user_id, chapter_id, status, completed_at, time_spent_minutes, quiz_score, quiz_attempt_id)
        VALUES ($1, $2, 'completed', NOW(), $3, $4, $5)
        ON CONFLICT (user_id, chapter_id)
        DO UPDATE SET status = 'completed', completed_at = NOW(),
            time_spent_minutes = chapter_progress.time_spent_minutes + $3
        """,
        user_id, chapter_id, completion.time_spent_minutes,
        None, completion.quiz_attempt_id
    )

    # Log activity for streak
    await db.execute(
        "INSERT INTO learning_sessions (user_id, chapter_id, activity_type, duration_minutes) VALUES ($1, $2, 'quiz', $3)",
        user_id, chapter_id, completion.time_spent_minutes
    )

    # Check for new achievements (rule-based)
    stats = await calculate_user_stats(user_id)
    new_achievements = await check_achievements(user_id, stats)

    # Update streak
    streak = await update_streak(user_id)

    return {
        "user_id": user_id,
        "chapter_id": chapter_id,
        "status": "completed",
        "completed_at": datetime.utcnow().isoformat(),
        "achievements_unlocked": new_achievements,
        "streak_update": streak
    }


@router.get("/progress/{user_id}/streak")
async def get_streak(
    user_id: str,
    history_days: int = 30,
    user: dict = Depends(get_current_user)
):
    """
    Get learning streak data.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL date calculations
    - ✅ Deterministic streak logic
    - ❌ NO LLM predictions
    """

    streak_data = await calculate_streak(user_id)

    # Get history
    today = date.today()
    history = []

    for i in range(history_days):
        check_date = today - timedelta(days=i)
        activity = await db.fetchrow(
            """
            SELECT SUM(duration_minutes) as time_spent
            FROM learning_sessions
            WHERE user_id = $1 AND DATE(logged_at) = $2
            """,
            user_id, check_date
        )

        history.append({
            "date": check_date.isoformat(),
            "active": activity["time_spent"] is not None and activity["time_spent"] > 0,
            "time_spent_minutes": activity["time_spent"] or 0
        })

    # Get longest streak
    longest = await db.fetchrow(
        "SELECT longest_streak FROM user_streaks WHERE user_id = $1",
        user_id
    )

    # Calculate next milestone
    current = streak_data["current_streak"]
    milestones = [3, 5, 7, 14, 30, 60, 90, 180, 365]
    next_milestone = next((m for m in milestones if m > current), None)

    return {
        "user_id": user_id,
        "current_streak": current,
        "longest_streak": longest["longest_streak"] if longest else current,
        "streak_status": "active" if streak_data["today_activity"] else "at_risk",
        "today_activity": streak_data["today_activity"],
        "streak_at_risk": streak_data["streak_at_risk"],
        "hours_until_streak_loss": streak_data["hours_until_streak_loss"],
        "history": history,
        "milestones": {
            "next_milestone": next_milestone,
            "days_to_next": next_milestone - current if next_milestone else None,
            "previous_milestones": [m for m in milestones if m <= current]
        }
    }


@router.get("/progress/{user_id}/achievements")
async def get_achievements(
    user_id: str,
    filter: str = "all",
    user: dict = Depends(get_current_user)
):
    """
    Get user achievements.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database query
    - ✅ Progress calculation (arithmetic)
    - ❌ NO LLM-generated achievement suggestions
    """

    # Get all achievements with user's unlock status
    achievements = await db.fetch(
        """
        SELECT
            a.*,
            ua.unlocked_at,
            CASE WHEN ua.achievement_id IS NOT NULL THEN 'earned' ELSE 'locked' END as status
        FROM achievements a
        LEFT JOIN user_achievements ua ON ua.achievement_id = a.achievement_id AND ua.user_id = $1
        ORDER BY a.sort_order
        """,
        user_id
    )

    # Apply filter
    if filter == "earned":
        achievements = [a for a in achievements if a["status"] == "earned"]
    elif filter == "locked":
        achievements = [a for a in achievements if a["status"] == "locked"]

    # Calculate progress for locked achievements
    stats = await calculate_user_stats(user_id)

    for achievement in achievements:
        if achievement["status"] == "locked":
            achievement["progress"] = calculate_achievement_progress(
                achievement["achievement_id"], stats
            )

    earned_count = sum(1 for a in achievements if a["status"] == "earned")
    points_earned = sum(a["points"] for a in achievements if a["status"] == "earned")
    points_possible = sum(a["points"] for a in achievements)

    return {
        "user_id": user_id,
        "total_achievements": len(achievements),
        "earned_count": earned_count,
        "points_earned": points_earned,
        "points_possible": points_possible,
        "achievements": achievements
    }


@router.post("/progress/{user_id}/time")
async def log_time(
    user_id: str,
    time_log: TimeLog,
    user: dict = Depends(get_current_user)
):
    """
    Log learning time.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database insert
    - ✅ Streak update
    - ❌ NO LLM analysis
    """

    session_id = await db.fetchval(
        """
        INSERT INTO learning_sessions (user_id, chapter_id, activity_type, duration_minutes)
        VALUES ($1, $2, $3, $4)
        RETURNING session_id
        """,
        user_id, time_log.chapter_id, time_log.activity_type, time_log.duration_minutes
    )

    # Update chapter progress time
    await db.execute(
        """
        UPDATE chapter_progress
        SET time_spent_minutes = time_spent_minutes + $1, updated_at = NOW()
        WHERE user_id = $2 AND chapter_id = $3
        """,
        time_log.duration_minutes, user_id, time_log.chapter_id
    )

    # Get today's total
    today_total = await db.fetchval(
        """
        SELECT SUM(duration_minutes)
        FROM learning_sessions
        WHERE user_id = $1 AND DATE(logged_at) = CURRENT_DATE
        """,
        user_id
    )

    # Check streak
    await update_streak(user_id)

    return {
        "logged": True,
        "session_id": str(session_id),
        "chapter_id": time_log.chapter_id,
        "duration_minutes": time_log.duration_minutes,
        "activity_type": time_log.activity_type,
        "logged_at": datetime.utcnow().isoformat(),
        "today_total_minutes": today_total,
        "streak_maintained": True
    }


# Helper functions

async def calculate_user_stats(user_id: str) -> dict:
    """Calculate user statistics for achievement checking."""
    stats = await db.fetchrow(
        """
        SELECT
            COUNT(*) FILTER (WHERE status = 'completed') as chapters_completed,
            COUNT(*) as total_chapters
        FROM chapter_progress
        WHERE user_id = $1
        """,
        user_id
    )

    streak = await db.fetchrow(
        "SELECT current_streak, longest_streak FROM user_streaks WHERE user_id = $1",
        user_id
    )

    quiz_stats = await db.fetchrow(
        """
        SELECT MAX(score) as best_quiz_score
        FROM quiz_attempts
        WHERE user_id = $1 AND submitted_at IS NOT NULL
        """,
        user_id
    )

    time_stats = await db.fetchrow(
        "SELECT SUM(duration_minutes) as total_time_minutes FROM learning_sessions WHERE user_id = $1",
        user_id
    )

    return {
        "chapters_completed": stats["chapters_completed"] or 0,
        "total_chapters": stats["total_chapters"] or 9,
        "completion_percentage": round((stats["chapters_completed"] or 0) / 9 * 100),
        "current_streak": streak["current_streak"] if streak else 0,
        "longest_streak": streak["longest_streak"] if streak else 0,
        "best_quiz_score": quiz_stats["best_quiz_score"] if quiz_stats else 0,
        "total_time_minutes": time_stats["total_time_minutes"] or 0,
        "modules_completed": {}  # Calculate per module
    }


async def check_achievements(user_id: str, stats: dict) -> list:
    """Check and unlock new achievements (rule-based only)."""
    new_achievements = []

    for achievement_id, rule in ACHIEVEMENT_RULES.items():
        # Check if already earned
        existing = await db.fetchrow(
            "SELECT * FROM user_achievements WHERE user_id = $1 AND achievement_id = $2",
            user_id, achievement_id
        )

        if existing:
            continue

        # Check rule condition (deterministic lambda)
        if rule["condition"](stats):
            await db.execute(
                "INSERT INTO user_achievements (user_id, achievement_id) VALUES ($1, $2)",
                user_id, achievement_id
            )

            new_achievements.append({
                "achievement_id": achievement_id,
                "name": rule["name"],
                "description": rule["description"],
                "points": rule["points"],
                "unlocked_at": datetime.utcnow().isoformat()
            })

    return new_achievements


def calculate_achievement_progress(achievement_id: str, stats: dict) -> dict:
    """Calculate progress toward locked achievement."""
    progress_rules = {
        "first-chapter": {"current": stats["chapters_completed"], "required": 1},
        "halfway-there": {"current": stats["completion_percentage"], "required": 50},
        "course-complete": {"current": stats["chapters_completed"], "required": 9},
        "streak-3": {"current": stats["current_streak"], "required": 3},
        "streak-5": {"current": stats["current_streak"], "required": 5},
        "streak-7": {"current": stats["current_streak"], "required": 7},
        "streak-30": {"current": stats["current_streak"], "required": 30},
        "quiz-perfect": {"current": stats["best_quiz_score"], "required": 100},
        "time-1-hour": {"current": stats["total_time_minutes"], "required": 60},
        "time-5-hours": {"current": stats["total_time_minutes"], "required": 300},
        "time-10-hours": {"current": stats["total_time_minutes"], "required": 600}
    }

    rule = progress_rules.get(achievement_id)
    if not rule:
        return None

    return {
        "current": rule["current"],
        "required": rule["required"],
        "percentage": min(100, round(rule["current"] / rule["required"] * 100))
    }
```

---

## Performance Requirements

- **Response Time:** < 100ms (p95) for all endpoints
- **Throughput:** 1000 progress checks/minute
- **Availability:** 99.9% uptime
- **Database Query Time:** < 50ms for aggregations

---

## Security Requirements

1. **Authentication:** JWT Bearer tokens required
2. **Authorization:** Users can only access their own progress
3. **Rate Limiting:** 100 requests/minute per user
4. **Data Integrity:** Prevent duplicate completions

---

## Testing Requirements

### Unit Tests

```python
def test_get_progress():
    """Test progress retrieval"""
    response = client.get("/api/v1/progress/user-123")
    assert response.status_code == 200
    assert "overall" in response.json()
    assert "completion_percentage" in response.json()["overall"]

def test_mark_chapter_complete():
    """Test chapter completion"""
    response = client.put(
        "/api/v1/progress/user-123/chapters/ch1-intro",
        json={"completion_type": "quiz_passed", "time_spent_minutes": 25}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_streak_calculation():
    """Test streak is calculated correctly"""
    # Log activity for 3 consecutive days
    for i in range(3):
        client.post("/api/v1/progress/user-123/time", json={
            "chapter_id": "ch1",
            "duration_minutes": 10,
            "activity_type": "reading"
        })

    response = client.get("/api/v1/progress/user-123/streak")
    assert response.json()["current_streak"] >= 1

def test_achievement_unlock():
    """Test achievement unlocks on condition met"""
    # Complete first chapter
    client.put(
        "/api/v1/progress/user-123/chapters/ch1",
        json={"completion_type": "quiz_passed", "time_spent_minutes": 25}
    )

    # Check achievements
    response = client.get("/api/v1/progress/user-123/achievements")
    earned = [a for a in response.json()["achievements"] if a["status"] == "earned"]
    assert any(a["achievement_id"] == "first-chapter" for a in earned)

def test_progress_percentage_calculation():
    """Test percentage is calculated correctly"""
    # Complete 3 of 9 chapters
    for i in range(1, 4):
        client.put(
            f"/api/v1/progress/user-123/chapters/ch{i}",
            json={"completion_type": "quiz_passed", "time_spent_minutes": 20}
        )

    response = client.get("/api/v1/progress/user-123")
    assert response.json()["overall"]["completion_percentage"] == 33  # 3/9 = 33%

def test_cannot_access_other_user_progress():
    """Test authorization check"""
    response = client.get(
        "/api/v1/progress/other-user",
        headers={"Authorization": f"Bearer {user_123_token}"}
    )
    assert response.status_code == 403
```

### Integration Tests

- Database connection verification
- Streak calculation across time zones
- Achievement unlock atomicity
- Concurrent progress updates

---

## Monitoring & Observability

### Metrics to Track
- Daily active users (streak activity)
- Completion rate by chapter
- Average time to complete course
- Achievement unlock distribution
- Streak length distribution

### Logging
```python
logger.info(
    "chapter_completed",
    user_id=user_id,
    chapter_id=chapter_id,
    time_spent=time_spent,
    achievements_unlocked=len(new_achievements),
    new_completion_percentage=percentage
)
```

---

## Cost Analysis

### Per Request Cost (10K users)
```
Database Operations:
- Progress queries: ~500K/month
- Completion updates: ~50K/month
- Streak checks: ~300K/month

All within Neon/Supabase free tier (3B reads)

Compute:
- No LLM calls
- Pure SQL and Python arithmetic
- No external API dependencies

Total: ~$0.00 additional cost
```

---

## Success Criteria

✅ **Zero-Backend-LLM Compliance:**
- No LLM imports
- All calculations are SQL or arithmetic
- Achievement rules are deterministic lambdas
- Streak logic uses date comparisons only

✅ **Performance:**
- P95 latency < 100ms
- Aggregation queries < 50ms

✅ **Functionality:**
- All 5 endpoints implemented
- Streak calculation accurate
- Achievement system working
- Time tracking functional

✅ **Security:**
- User data isolation enforced
- Rate limiting in place

---

**Spec Version:** 1.0
**Last Updated:** January 15, 2026
**Status:** Ready for Implementation
