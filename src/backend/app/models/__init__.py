"""
Database Models
SQLAlchemy 2.0 models for Course Companion
"""

from app.models.user import User, Subscription, SubscriptionTier
from app.models.content import Module, Chapter, MediaAsset
from app.models.progress import (
    ChapterProgress,
    LearningSession,
    UserStreak,
    ProgressStatus,
    ActivityType,
)
from app.models.achievement import Achievement, UserAchievement, AchievementCategory
from app.models.quiz import Quiz, Question, QuizAttempt, QuestionType

__all__ = [
    # User models
    "User",
    "Subscription",
    "SubscriptionTier",
    # Content models
    "Module",
    "Chapter",
    "MediaAsset",
    # Progress models
    "ChapterProgress",
    "LearningSession",
    "UserStreak",
    "ProgressStatus",
    "ActivityType",
    # Achievement models
    "Achievement",
    "UserAchievement",
    "AchievementCategory",
    # Quiz models
    "Quiz",
    "Question",
    "QuizAttempt",
    "QuestionType",
]
