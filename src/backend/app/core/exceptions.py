"""
Custom Exceptions
Application-specific exceptions for better error handling
"""

from typing import Any, Optional


class CourseCompanionException(Exception):
    """Base exception for Course Companion application."""

    def __init__(
        self,
        message: str,
        error_code: str = "error",
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)


class ContentNotFoundError(CourseCompanionException):
    """Raised when content is not found in storage."""

    def __init__(self, content_type: str, content_id: str):
        super().__init__(
            message=f"{content_type.capitalize()} '{content_id}' not found",
            error_code=f"{content_type}_not_found",
            details={"content_type": content_type, "content_id": content_id},
        )


class ChapterNotFoundError(ContentNotFoundError):
    """Raised when a chapter is not found."""

    def __init__(self, chapter_id: str):
        super().__init__("chapter", chapter_id)


class ModuleNotFoundError(ContentNotFoundError):
    """Raised when a module is not found."""

    def __init__(self, module_id: str):
        super().__init__("module", module_id)


class QuizNotFoundError(ContentNotFoundError):
    """Raised when a quiz is not found."""

    def __init__(self, quiz_id: str):
        super().__init__("quiz", quiz_id)


class AccessDeniedError(CourseCompanionException):
    """Raised when user doesn't have access to content."""

    def __init__(
        self,
        content_type: str,
        content_id: str,
        required_tier: str,
        current_tier: str,
    ):
        super().__init__(
            message=f"Access denied to {content_type} '{content_id}'. Required tier: {required_tier}",
            error_code="access_denied",
            details={
                "content_type": content_type,
                "content_id": content_id,
                "required_tier": required_tier,
                "current_tier": current_tier,
                "upgrade_url": "/api/v1/pricing",
            },
        )


class PrerequisitesNotMetError(CourseCompanionException):
    """Raised when prerequisites are not completed."""

    def __init__(self, content_id: str, required_ids: list[str]):
        super().__init__(
            message=f"Prerequisites not met for '{content_id}'",
            error_code="prerequisites_not_met",
            details={
                "content_id": content_id,
                "required_prerequisites": required_ids,
            },
        )


class AlreadyCompletedError(CourseCompanionException):
    """Raised when trying to complete something already completed."""

    def __init__(self, content_type: str, content_id: str, completed_at: str):
        super().__init__(
            message=f"{content_type.capitalize()} '{content_id}' is already completed",
            error_code="already_completed",
            details={
                "content_type": content_type,
                "content_id": content_id,
                "completed_at": completed_at,
            },
        )


class QuizAttemptError(CourseCompanionException):
    """Raised for quiz attempt related errors."""

    pass


class MaxAttemptsExceededError(QuizAttemptError):
    """Raised when maximum quiz attempts are exceeded."""

    def __init__(self, quiz_id: str, max_attempts: int, current_attempts: int):
        super().__init__(
            message=f"Maximum attempts ({max_attempts}) exceeded for quiz '{quiz_id}'",
            error_code="max_attempts_exceeded",
            details={
                "quiz_id": quiz_id,
                "max_attempts": max_attempts,
                "current_attempts": current_attempts,
            },
        )


class QuizNotStartedError(QuizAttemptError):
    """Raised when trying to submit a quiz that wasn't started."""

    def __init__(self, quiz_id: str):
        super().__init__(
            message=f"No active attempt for quiz '{quiz_id}'",
            error_code="quiz_not_started",
            details={"quiz_id": quiz_id},
        )


class StorageError(CourseCompanionException):
    """Raised for storage (R2) related errors."""

    def __init__(self, operation: str, key: str, message: str):
        super().__init__(
            message=f"Storage error during {operation}: {message}",
            error_code="storage_error",
            details={"operation": operation, "key": key},
        )


class ValidationError(CourseCompanionException):
    """Raised for validation errors."""

    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation error on '{field}': {message}",
            error_code="validation_error",
            details={"field": field},
        )
