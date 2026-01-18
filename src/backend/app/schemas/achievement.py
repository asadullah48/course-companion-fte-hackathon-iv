"""
Achievement Schemas
Schemas for achievements and gamification
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AchievementProgress(BaseModel):
    """Progress toward locked achievement."""

    current: int = Field(..., description="Current progress value")
    required: int = Field(..., description="Required value to unlock")
    percentage: int = Field(..., description="Progress percentage")


class AchievementResponse(BaseModel):
    """Single achievement details."""

    achievement_id: str = Field(..., description="Unique achievement identifier")
    name: str = Field(..., description="Achievement name")
    description: str = Field(..., description="Achievement description")
    icon: str = Field(..., description="Icon identifier")
    points: int = Field(..., description="Points awarded")
    category: Literal["progress", "modules", "streaks", "quizzes", "time"] = Field(
        ..., description="Achievement category"
    )
    status: Literal["earned", "locked"] = Field(..., description="Unlock status")
    unlocked_at: Optional[datetime] = Field(None, description="When unlocked")
    progress: Optional[AchievementProgress] = Field(
        None, description="Progress if locked"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "achievement_id": "streak-7",
                "name": "Week Warrior",
                "description": "Maintain a 7-day learning streak",
                "icon": "fire",
                "points": 75,
                "category": "streaks",
                "status": "locked",
                "unlocked_at": None,
                "progress": {"current": 5, "required": 7, "percentage": 71},
            }
        }


class AchievementsListResponse(BaseModel):
    """List of achievements response."""

    user_id: str = Field(..., description="User identifier")
    total_achievements: int = Field(..., description="Total achievements available")
    earned_count: int = Field(..., description="Number of earned achievements")
    points_earned: int = Field(..., description="Total points earned")
    points_possible: int = Field(..., description="Total possible points")
    achievements: List[AchievementResponse] = Field(
        ..., description="List of achievements"
    )
    recent_achievements: Optional[List[AchievementResponse]] = Field(
        None, description="Recently earned achievements"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "total_achievements": 15,
                "earned_count": 6,
                "points_earned": 350,
                "points_possible": 1000,
                "achievements": [],
                "recent_achievements": [],
            }
        }
