"""
Progress Tracking Schemas
Schemas for progress, streaks, and time tracking
"""

from datetime import datetime, date
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ProgressSummary(BaseModel):
    """Overall progress summary."""

    total_chapters: int = Field(..., description="Total chapters in course")
    completed_chapters: int = Field(..., description="Completed chapters")
    completion_percentage: int = Field(..., description="Completion percentage")
    total_time_minutes: int = Field(..., description="Total learning time")
    current_module: Optional[int] = Field(None, description="Current module number")
    current_chapter: Optional[str] = Field(None, description="Current chapter ID")


class ModuleProgress(BaseModel):
    """Module-level progress."""

    module_id: int = Field(..., description="Module number")
    title: str = Field(..., description="Module title")
    total_chapters: int = Field(..., description="Total chapters in module")
    completed_chapters: int = Field(..., description="Completed chapters")
    completion_percentage: int = Field(..., description="Completion percentage")
    time_spent_minutes: int = Field(..., description="Time spent on module")
    status: Literal["locked", "not_started", "in_progress", "completed"] = Field(
        ..., description="Module status"
    )


class ChapterProgressDetail(BaseModel):
    """Chapter-level progress detail."""

    chapter_id: str = Field(..., description="Chapter identifier")
    title: str = Field(..., description="Chapter title")
    module_id: int = Field(..., description="Module number")
    status: Literal["not_started", "in_progress", "completed"] = Field(
        ..., description="Chapter status"
    )
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    time_spent_minutes: int = Field(default=0, description="Time spent on chapter")
    quiz_score: Optional[int] = Field(None, description="Quiz score if completed")


class ProgressResponse(BaseModel):
    """Full progress response."""

    user_id: str = Field(..., description="User identifier")
    overall: ProgressSummary = Field(..., description="Overall progress summary")
    modules: List[ModuleProgress] = Field(..., description="Module progress list")
    chapters: Optional[List[ChapterProgressDetail]] = Field(
        None, description="Chapter progress list (if requested)"
    )
    last_activity: Optional[datetime] = Field(None, description="Last activity time")
    member_since: datetime = Field(..., description="Registration date")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "overall": {
                    "total_chapters": 9,
                    "completed_chapters": 4,
                    "completion_percentage": 44,
                    "total_time_minutes": 180,
                    "current_module": 2,
                    "current_chapter": "ch4-skill-md-structure",
                },
                "modules": [
                    {
                        "module_id": 1,
                        "title": "Foundations",
                        "total_chapters": 3,
                        "completed_chapters": 3,
                        "completion_percentage": 100,
                        "time_spent_minutes": 90,
                        "status": "completed",
                    }
                ],
                "last_activity": "2026-01-15T08:30:00Z",
                "member_since": "2026-01-10T00:00:00Z",
            }
        }


class ChapterCompletionRequest(BaseModel):
    """Request to mark chapter as complete."""

    completion_type: Literal["quiz_passed", "content_read"] = Field(
        ..., description="How chapter was completed"
    )
    quiz_attempt_id: Optional[str] = Field(
        None, description="Quiz attempt ID if quiz_passed"
    )
    time_spent_minutes: int = Field(..., ge=0, description="Time spent on chapter")


class AchievementUnlocked(BaseModel):
    """Achievement unlocked during completion."""

    achievement_id: str
    name: str
    description: str
    unlocked_at: datetime


class StreakUpdate(BaseModel):
    """Streak update info."""

    current_streak: int
    is_new_day: bool


class ChapterCompletionResponse(BaseModel):
    """Response after marking chapter complete."""

    user_id: str = Field(..., description="User identifier")
    chapter_id: str = Field(..., description="Chapter identifier")
    status: Literal["completed"] = Field(..., description="New status")
    completed_at: datetime = Field(..., description="Completion timestamp")
    time_spent_minutes: int = Field(..., description="Total time spent")
    progress_update: ProgressSummary = Field(..., description="Updated progress")
    achievements_unlocked: List[AchievementUnlocked] = Field(
        default_factory=list, description="New achievements"
    )
    streak_update: StreakUpdate = Field(..., description="Streak status")


class StreakHistoryItem(BaseModel):
    """Single day in streak history."""

    activity_date: date = Field(..., description="Date")
    active: bool = Field(..., description="Whether user was active")
    time_spent_minutes: int = Field(..., description="Time spent learning")


class StreakMilestones(BaseModel):
    """Streak milestone info."""

    next_milestone: Optional[int] = Field(None, description="Next streak milestone")
    days_to_next: Optional[int] = Field(None, description="Days until next milestone")
    previous_milestones: List[int] = Field(
        default_factory=list, description="Achieved milestones"
    )


class StreakResponse(BaseModel):
    """Learning streak response."""

    user_id: str = Field(..., description="User identifier")
    current_streak: int = Field(..., description="Current streak days")
    longest_streak: int = Field(..., description="Longest ever streak")
    streak_status: Literal["active", "at_risk", "broken"] = Field(
        ..., description="Current streak status"
    )
    today_activity: bool = Field(..., description="Whether active today")
    streak_at_risk: bool = Field(..., description="Whether streak is at risk")
    hours_until_streak_loss: float = Field(
        ..., description="Hours until streak is lost"
    )
    history: List[StreakHistoryItem] = Field(..., description="Recent history")
    milestones: StreakMilestones = Field(..., description="Milestone info")
    freeze_available: bool = Field(..., description="Whether freeze is available")
    freezes_remaining: int = Field(..., description="Remaining freezes")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "current_streak": 5,
                "longest_streak": 12,
                "streak_status": "active",
                "today_activity": True,
                "streak_at_risk": False,
                "hours_until_streak_loss": 18.5,
                "history": [
                    {"date": "2026-01-15", "active": True, "time_spent_minutes": 45}
                ],
                "milestones": {
                    "next_milestone": 7,
                    "days_to_next": 2,
                    "previous_milestones": [3, 5],
                },
                "freeze_available": True,
                "freezes_remaining": 2,
            }
        }


class TimeLogRequest(BaseModel):
    """Request to log learning time."""

    chapter_id: str = Field(..., description="Chapter being studied")
    duration_minutes: int = Field(..., ge=1, le=480, description="Duration in minutes")
    activity_type: Literal["reading", "quiz", "review", "practice"] = Field(
        ..., description="Type of activity"
    )


class TimeLogResponse(BaseModel):
    """Response after logging time."""

    logged: bool = Field(default=True, description="Whether time was logged")
    session_id: str = Field(..., description="Session identifier")
    chapter_id: str = Field(..., description="Chapter identifier")
    duration_minutes: int = Field(..., description="Duration logged")
    activity_type: str = Field(..., description="Activity type")
    logged_at: datetime = Field(..., description="Logging timestamp")
    today_total_minutes: int = Field(..., description="Total time today")
    streak_maintained: bool = Field(..., description="Whether streak is maintained")
