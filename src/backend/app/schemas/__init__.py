"""
Pydantic Schemas for API request/response models
"""

from app.schemas.content import (
    ChapterResponse,
    ChapterListItem,
    ChapterListResponse,
    ModuleResponse,
    ModuleListResponse,
    MediaAssetResponse,
)
from app.schemas.progress import (
    ProgressSummary,
    ModuleProgress,
    ChapterProgressDetail,
    ProgressResponse,
    ChapterCompletionRequest,
    ChapterCompletionResponse,
    StreakResponse,
    StreakHistoryItem,
    TimeLogRequest,
    TimeLogResponse,
)
from app.schemas.achievement import (
    AchievementResponse,
    AchievementProgress,
    AchievementsListResponse,
)
from app.schemas.quiz import (
    QuizResponse,
    QuestionResponse,
    QuizStartResponse,
    QuizSubmitRequest,
    QuizResultResponse,
    QuizAttemptResponse,
)
from app.schemas.common import (
    ErrorResponse,
    SuccessResponse,
    PaginatedResponse,
)

__all__ = [
    # Content
    "ChapterResponse",
    "ChapterListItem",
    "ChapterListResponse",
    "ModuleResponse",
    "ModuleListResponse",
    "MediaAssetResponse",
    # Progress
    "ProgressSummary",
    "ModuleProgress",
    "ChapterProgressDetail",
    "ProgressResponse",
    "ChapterCompletionRequest",
    "ChapterCompletionResponse",
    "StreakResponse",
    "StreakHistoryItem",
    "TimeLogRequest",
    "TimeLogResponse",
    # Achievement
    "AchievementResponse",
    "AchievementProgress",
    "AchievementsListResponse",
    # Quiz
    "QuizResponse",
    "QuestionResponse",
    "QuizStartResponse",
    "QuizSubmitRequest",
    "QuizResultResponse",
    "QuizAttemptResponse",
    # Common
    "ErrorResponse",
    "SuccessResponse",
    "PaginatedResponse",
]
