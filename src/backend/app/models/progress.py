"""
Progress Tracking Models
Chapter progress, learning sessions, and streaks
"""

import enum
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.content import Chapter
    from app.models.user import User


class ProgressStatus(str, enum.Enum):
    """Chapter progress status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ActivityType(str, enum.Enum):
    """Learning activity types."""

    READING = "reading"
    QUIZ = "quiz"
    REVIEW = "review"
    PRACTICE = "practice"


class ChapterProgress(Base):
    """
    Chapter Progress model.

    Tracks user's progress through each chapter.
    CONSTITUTIONAL COMPLIANCE: All calculations are SQL-based or arithmetic.
    """

    __tablename__ = "chapter_progress"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # User and chapter relationship
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chapter_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Progress status
    status: Mapped[ProgressStatus] = mapped_column(
        Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False
    )

    # Time tracking
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)

    # Quiz tracking
    quiz_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quiz_attempt_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False), nullable=True
    )

    # Timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chapter_progress")
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="progress")

    # Unique constraint: one progress record per user per chapter
    __table_args__ = (
        UniqueConstraint("user_id", "chapter_id", name="uq_chapter_progress_user_chapter"),
    )

    def mark_started(self) -> None:
        """Mark chapter as started."""
        if self.status == ProgressStatus.NOT_STARTED:
            self.status = ProgressStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()

    def mark_completed(self, quiz_score: Optional[int] = None) -> None:
        """Mark chapter as completed."""
        self.status = ProgressStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if quiz_score is not None:
            self.quiz_score = quiz_score

    def add_time(self, minutes: int) -> None:
        """Add learning time to chapter."""
        self.time_spent_minutes += minutes
        if self.status == ProgressStatus.NOT_STARTED:
            self.mark_started()

    def __repr__(self) -> str:
        return f"<ChapterProgress user={self.user_id} chapter={self.chapter_id} status={self.status.value}>"


class LearningSession(Base):
    """
    Learning Session model.

    Tracks individual learning sessions for time tracking and streak calculation.
    CONSTITUTIONAL COMPLIANCE: Used for SQL-based streak calculations.
    """

    __tablename__ = "learning_sessions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # User relationship
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Optional chapter reference
    chapter_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("chapters.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Activity tracking
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType), nullable=False
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Timestamp for streak calculation
    logged_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_sessions")

    def __repr__(self) -> str:
        return f"<LearningSession user={self.user_id} activity={self.activity_type.value} duration={self.duration_minutes}min>"


class UserStreak(Base):
    """
    User Streak model.

    Tracks user's learning streak (cached for performance).
    Streak calculation is deterministic and SQL-based.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL-based date calculations
    - ✅ Deterministic streak logic
    - ❌ NO LLM-based predictions
    """

    __tablename__ = "user_streaks"

    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Current streak
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)

    # Last activity date (for streak calculation)
    last_activity_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Streak freeze tracking
    freezes_used: Mapped[int] = mapped_column(Integer, default=0)
    freezes_reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamp
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="streak")

    def update_streak(self, activity_date: date) -> bool:
        """
        Update streak based on activity date.
        Returns True if streak was maintained/increased, False if broken.

        CONSTITUTIONAL COMPLIANCE:
        - Pure date arithmetic
        - No LLM involvement
        """
        from datetime import timedelta

        today = date.today()

        if self.last_activity_date is None:
            # First activity ever
            self.current_streak = 1
            self.last_activity_date = activity_date
            self._update_longest()
            return True

        days_since_last = (activity_date - self.last_activity_date).days

        if days_since_last == 0:
            # Same day - no change to streak count
            return True
        elif days_since_last == 1:
            # Consecutive day - increment streak
            self.current_streak += 1
            self.last_activity_date = activity_date
            self._update_longest()
            return True
        elif days_since_last > 1:
            # Streak broken - reset to 1
            self.current_streak = 1
            self.last_activity_date = activity_date
            return False

        return True

    def _update_longest(self) -> None:
        """Update longest streak if current exceeds it."""
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

    def use_freeze(self) -> bool:
        """
        Use a streak freeze to prevent streak break.
        Returns True if freeze was used successfully.
        """
        from datetime import timedelta

        # Check if freezes need reset (monthly)
        if self.freezes_reset_at:
            if datetime.utcnow() >= self.freezes_reset_at:
                self.freezes_used = 0
                self.freezes_reset_at = None

        # Attempt to use freeze (limit checked elsewhere based on tier)
        self.freezes_used += 1
        return True

    @property
    def streak_at_risk(self) -> bool:
        """Check if streak is at risk (no activity today)."""
        if self.last_activity_date is None:
            return False
        return self.last_activity_date < date.today()

    def __repr__(self) -> str:
        return f"<UserStreak user={self.user_id} current={self.current_streak} longest={self.longest_streak}>"
