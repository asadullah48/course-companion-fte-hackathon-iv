"""
Achievement Models
Definitions and user achievements
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class AchievementCategory(str, enum.Enum):
    """Achievement categories for grouping."""

    PROGRESS = "progress"
    MODULES = "modules"
    STREAKS = "streaks"
    QUIZZES = "quizzes"
    TIME = "time"


class Achievement(Base):
    """
    Achievement Definition model.

    Defines achievements that users can unlock.
    All unlock conditions are rule-based (deterministic lambdas).

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Rule-based achievement unlocking
    - ❌ NO LLM-based achievement suggestions
    """

    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    achievement_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )  # e.g., "first-chapter", "streak-7"

    # Display information
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="trophy")

    # Gamification
    points: Mapped[int] = mapped_column(Integer, default=50)
    category: Mapped[AchievementCategory] = mapped_column(
        Enum(AchievementCategory), nullable=False
    )

    # Ordering
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Rule metadata (for display purposes - actual logic in code)
    # Stores the requirement for progress display (e.g., "7" for streak-7)
    requirement_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requirement_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # e.g., "streak_days", "chapters_completed", "quiz_score"

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Achievement {self.achievement_id} points={self.points}>"


class UserAchievement(Base):
    """
    User Achievement model.

    Tracks which achievements a user has unlocked.
    """

    __tablename__ = "user_achievements"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # User and achievement relationship
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    achievement_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Unlock timestamp
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement")

    # Unique constraint: one unlock per user per achievement
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    def __repr__(self) -> str:
        return f"<UserAchievement user={self.user_id} achievement={self.achievement_id}>"


# Achievement rule definitions (deterministic only)
# These are used to check if a user has earned an achievement
ACHIEVEMENT_RULES = {
    # Progress Achievements
    "first-chapter": {
        "name": "First Steps",
        "description": "Complete your first chapter",
        "icon": "rocket",
        "points": 50,
        "category": AchievementCategory.PROGRESS,
        "requirement_type": "chapters_completed",
        "requirement_value": 1,
        "condition": lambda stats: stats.get("chapters_completed", 0) >= 1,
    },
    "halfway-there": {
        "name": "Halfway There",
        "description": "Complete 50% of the course",
        "icon": "flag",
        "points": 75,
        "category": AchievementCategory.PROGRESS,
        "requirement_type": "completion_percentage",
        "requirement_value": 50,
        "condition": lambda stats: stats.get("completion_percentage", 0) >= 50,
    },
    "course-complete": {
        "name": "Agent Expert",
        "description": "Complete the entire course",
        "icon": "medal",
        "points": 200,
        "category": AchievementCategory.PROGRESS,
        "requirement_type": "completion_percentage",
        "requirement_value": 100,
        "condition": lambda stats: stats.get("completion_percentage", 0) == 100,
    },
    # Module Achievements
    "module-1-complete": {
        "name": "Foundation Master",
        "description": "Complete all chapters in Module 1",
        "icon": "trophy",
        "points": 100,
        "category": AchievementCategory.MODULES,
        "requirement_type": "module_completed",
        "requirement_value": 1,
        "condition": lambda stats: stats.get("modules_completed", {}).get(1, False),
    },
    "module-2-complete": {
        "name": "Skill Builder",
        "description": "Complete all chapters in Module 2",
        "icon": "tools",
        "points": 100,
        "category": AchievementCategory.MODULES,
        "requirement_type": "module_completed",
        "requirement_value": 2,
        "condition": lambda stats: stats.get("modules_completed", {}).get(2, False),
    },
    "module-3-complete": {
        "name": "Workflow Wizard",
        "description": "Complete all chapters in Module 3",
        "icon": "magic",
        "points": 100,
        "category": AchievementCategory.MODULES,
        "requirement_type": "module_completed",
        "requirement_value": 3,
        "condition": lambda stats: stats.get("modules_completed", {}).get(3, False),
    },
    # Streak Achievements
    "streak-3": {
        "name": "Hat Trick",
        "description": "Maintain a 3-day learning streak",
        "icon": "fire",
        "points": 25,
        "category": AchievementCategory.STREAKS,
        "requirement_type": "streak_days",
        "requirement_value": 3,
        "condition": lambda stats: stats.get("current_streak", 0) >= 3,
    },
    "streak-5": {
        "name": "High Five",
        "description": "Maintain a 5-day learning streak",
        "icon": "fire",
        "points": 50,
        "category": AchievementCategory.STREAKS,
        "requirement_type": "streak_days",
        "requirement_value": 5,
        "condition": lambda stats: stats.get("current_streak", 0) >= 5,
    },
    "streak-7": {
        "name": "Week Warrior",
        "description": "Maintain a 7-day learning streak",
        "icon": "fire",
        "points": 75,
        "category": AchievementCategory.STREAKS,
        "requirement_type": "streak_days",
        "requirement_value": 7,
        "condition": lambda stats: stats.get("current_streak", 0) >= 7,
    },
    "streak-14": {
        "name": "Fortnight Focus",
        "description": "Maintain a 14-day learning streak",
        "icon": "fire",
        "points": 100,
        "category": AchievementCategory.STREAKS,
        "requirement_type": "streak_days",
        "requirement_value": 14,
        "condition": lambda stats: stats.get("current_streak", 0) >= 14,
    },
    "streak-30": {
        "name": "Monthly Master",
        "description": "Maintain a 30-day learning streak",
        "icon": "fire",
        "points": 150,
        "category": AchievementCategory.STREAKS,
        "requirement_type": "streak_days",
        "requirement_value": 30,
        "condition": lambda stats: stats.get("current_streak", 0) >= 30,
    },
    # Quiz Achievements
    "quiz-perfect": {
        "name": "Perfect Score",
        "description": "Score 100% on any quiz",
        "icon": "star",
        "points": 50,
        "category": AchievementCategory.QUIZZES,
        "requirement_type": "quiz_score",
        "requirement_value": 100,
        "condition": lambda stats: stats.get("best_quiz_score", 0) == 100,
    },
    "quiz-streak-3": {
        "name": "Quiz Champion",
        "description": "Pass 3 quizzes in a row",
        "icon": "crown",
        "points": 75,
        "category": AchievementCategory.QUIZZES,
        "requirement_type": "quiz_pass_streak",
        "requirement_value": 3,
        "condition": lambda stats: stats.get("quiz_pass_streak", 0) >= 3,
    },
    # Time Achievements
    "time-1-hour": {
        "name": "Dedicated Learner",
        "description": "Spend 1 hour learning",
        "icon": "clock",
        "points": 25,
        "category": AchievementCategory.TIME,
        "requirement_type": "total_time_minutes",
        "requirement_value": 60,
        "condition": lambda stats: stats.get("total_time_minutes", 0) >= 60,
    },
    "time-5-hours": {
        "name": "Committed Student",
        "description": "Spend 5 hours learning",
        "icon": "clock",
        "points": 75,
        "category": AchievementCategory.TIME,
        "requirement_type": "total_time_minutes",
        "requirement_value": 300,
        "condition": lambda stats: stats.get("total_time_minutes", 0) >= 300,
    },
    "time-10-hours": {
        "name": "Agent Scholar",
        "description": "Spend 10 hours learning",
        "icon": "clock",
        "points": 100,
        "category": AchievementCategory.TIME,
        "requirement_type": "total_time_minutes",
        "requirement_value": 600,
        "condition": lambda stats: stats.get("total_time_minutes", 0) >= 600,
    },
}
