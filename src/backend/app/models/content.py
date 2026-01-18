"""
Content Models for Course Structure
Modules, Chapters, and Media Assets
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.user import SubscriptionTier

if TYPE_CHECKING:
    from app.models.progress import ChapterProgress
    from app.models.quiz import Quiz


class Module(Base):
    """
    Course Module model.

    Represents a logical grouping of chapters (e.g., "Foundations", "Skills Development").
    Access is controlled by subscription tier.
    """

    __tablename__ = "modules"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    module_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )  # e.g., "mod-1-foundations"

    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Ordering and structure
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(
        String(20), default="beginner"
    )  # beginner, intermediate, advanced
    estimated_duration_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Access control
    access_tier: Mapped[str] = mapped_column(
        String(20), default="free"
    )  # free, premium, pro, team

    # Learning objectives stored as JSON array
    learning_objectives: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )

    # Prerequisites (list of module_ids)
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(100)), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    chapters: Mapped[List["Chapter"]] = relationship(
        "Chapter", back_populates="module", order_by="Chapter.order"
    )
    quiz: Mapped[Optional["Quiz"]] = relationship("Quiz", back_populates="module", uselist=False)

    @property
    def chapter_count(self) -> int:
        """Get number of chapters in this module."""
        return len(self.chapters) if self.chapters else 0

    def is_accessible_by(self, tier: SubscriptionTier) -> bool:
        """Check if module is accessible by given subscription tier."""
        tier_order = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PREMIUM: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.TEAM: 3,
        }
        access_order = {"free": 0, "premium": 1, "pro": 2, "team": 3}
        return tier_order.get(tier, 0) >= access_order.get(self.access_tier, 0)

    def __repr__(self) -> str:
        return f"<Module {self.module_id}>"


class Chapter(Base):
    """
    Course Chapter model.

    Represents a single learning unit within a module.
    Content is stored in R2 and served verbatim (Zero-Backend-LLM compliance).
    """

    __tablename__ = "chapters"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    chapter_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )  # e.g., "ch1-intro-to-agents"

    # Module relationship
    module_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Content metadata (actual content stored in R2)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Ordering and structure
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="beginner")
    estimated_read_time: Mapped[int] = mapped_column(Integer, default=15)  # minutes
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    # Content location in R2
    r2_key: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # e.g., "chapters/ch1-intro-to-agents.md"

    # Metadata
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(50)), nullable=True)
    learning_objectives: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)

    # Prerequisites (list of chapter_ids)
    prerequisites: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(100)), nullable=True)

    # Access control (inherited from module, but can be overridden)
    access_tier: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="chapters")
    media_assets: Mapped[List["MediaAsset"]] = relationship(
        "MediaAsset", back_populates="chapter"
    )
    progress: Mapped[List["ChapterProgress"]] = relationship(
        "ChapterProgress", back_populates="chapter"
    )

    def get_access_tier(self) -> str:
        """Get effective access tier (chapter override or module default)."""
        return self.access_tier or (self.module.access_tier if self.module else "free")

    def is_accessible_by(self, tier: SubscriptionTier) -> bool:
        """Check if chapter is accessible by given subscription tier."""
        tier_order = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PREMIUM: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.TEAM: 3,
        }
        access_order = {"free": 0, "premium": 1, "pro": 2, "team": 3}
        return tier_order.get(tier, 0) >= access_order.get(self.get_access_tier(), 0)

    def __repr__(self) -> str:
        return f"<Chapter {self.chapter_id}>"


class MediaAsset(Base):
    """
    Media Asset model.

    Represents images, diagrams, and videos associated with chapters.
    All assets stored in R2 and served verbatim.
    """

    __tablename__ = "media_assets"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    asset_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )  # e.g., "img-agent-architecture"

    # Chapter relationship
    chapter_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Asset metadata
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # image, video, diagram
    filename: Mapped[str] = mapped_column(String(255), nullable=False)

    # R2 storage
    r2_key: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)

    # Image/video specific metadata
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # for video
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)

    # Thumbnail for videos
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="media_assets")

    def __repr__(self) -> str:
        return f"<MediaAsset {self.asset_id} type={self.type}>"
