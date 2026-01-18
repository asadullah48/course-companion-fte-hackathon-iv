"""
User and Subscription Models
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.achievement import UserAchievement
    from app.models.progress import ChapterProgress, LearningSession, UserStreak
    from app.models.quiz import QuizAttempt


class SubscriptionTier(str, enum.Enum):
    """Subscription tier levels."""

    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"
    TEAM = "team"


class User(Base):
    """
    User model for authentication and profile.

    Stores user credentials and basic profile information.
    Access control is determined by the user's subscription tier.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Profile
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # OAuth providers
    google_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    github_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    subscription: Mapped[Optional["Subscription"]] = relationship(
        "Subscription", back_populates="user", uselist=False
    )
    chapter_progress: Mapped[List["ChapterProgress"]] = relationship(
        "ChapterProgress", back_populates="user"
    )
    learning_sessions: Mapped[List["LearningSession"]] = relationship(
        "LearningSession", back_populates="user"
    )
    streak: Mapped[Optional["UserStreak"]] = relationship(
        "UserStreak", back_populates="user", uselist=False
    )
    achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user"
    )
    quiz_attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="user"
    )

    @property
    def tier(self) -> SubscriptionTier:
        """Get user's subscription tier."""
        if self.subscription and self.subscription.is_active:
            return self.subscription.tier
        return SubscriptionTier.FREE

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class Subscription(Base):
    """
    Subscription model for access control.

    Tracks user's subscription tier and billing status.
    Access control is enforced based on tier:
    - FREE: Module 1 only (Chapters 1-3)
    - PREMIUM: All modules, 2 streak freezes/month
    - PRO: All modules, 5 streak freezes/month
    - TEAM: All modules, unlimited streak freezes
    """

    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Subscription details
    tier: Mapped[SubscriptionTier] = mapped_column(
        Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Billing
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Period
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Streak freezes (resets monthly based on tier)
    streak_freezes_used: Mapped[int] = mapped_column(Integer, default=0)
    streak_freezes_reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="subscription")

    @property
    def streak_freezes_remaining(self) -> int:
        """Calculate remaining streak freezes based on tier."""
        limits = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PREMIUM: 2,
            SubscriptionTier.PRO: 5,
            SubscriptionTier.TEAM: 999,  # Effectively unlimited
        }
        return max(0, limits.get(self.tier, 0) - self.streak_freezes_used)

    def __repr__(self) -> str:
        return f"<Subscription {self.user_id} tier={self.tier.value}>"
