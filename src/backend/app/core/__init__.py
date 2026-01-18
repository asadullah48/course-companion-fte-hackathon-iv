"""
Core utilities module
Authentication, storage, and common dependencies
"""

from app.core.auth import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password,
    TokenPayload,
)
from app.core.r2 import R2Client, get_r2_client
from app.core.deps import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    get_db,
    require_subscription_tier,
    CurrentUser,
    ActiveUser,
    OptionalUser,
    DbSession,
)
from app.core.exceptions import (
    CourseCompanionException,
    ContentNotFoundError,
    ChapterNotFoundError,
    ModuleNotFoundError,
    QuizNotFoundError,
    AccessDeniedError,
    PrerequisitesNotMetError,
    AlreadyCompletedError,
    QuizAttemptError,
    MaxAttemptsExceededError,
    QuizNotStartedError,
    StorageError,
    ValidationError,
)

__all__ = [
    # Auth
    "create_access_token",
    "verify_token",
    "get_password_hash",
    "verify_password",
    "TokenPayload",
    # R2
    "R2Client",
    "get_r2_client",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "get_db",
    "require_subscription_tier",
    "CurrentUser",
    "ActiveUser",
    "OptionalUser",
    "DbSession",
    # Exceptions
    "CourseCompanionException",
    "ContentNotFoundError",
    "ChapterNotFoundError",
    "ModuleNotFoundError",
    "QuizNotFoundError",
    "AccessDeniedError",
    "PrerequisitesNotMetError",
    "AlreadyCompletedError",
    "QuizAttemptError",
    "MaxAttemptsExceededError",
    "QuizNotStartedError",
    "StorageError",
    "ValidationError",
]
