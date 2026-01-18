"""
Content Schemas
Schemas for chapters, modules, and media assets
"""

from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class ChapterMetadata(BaseModel):
    """Chapter metadata schema."""

    module: int = Field(..., description="Module number")
    order: int = Field(..., description="Chapter order within module")
    tags: List[str] = Field(default_factory=list, description="Chapter tags")
    difficulty: str = Field(..., description="Difficulty level")


class ChapterResponse(BaseModel):
    """
    Full chapter content response.

    CONSTITUTIONAL COMPLIANCE:
    - Content is served verbatim from R2
    - No LLM processing or transformation
    """

    chapter_id: str = Field(..., description="Unique chapter identifier")
    title: str = Field(..., description="Chapter title")
    content: str = Field(..., description="Chapter content (markdown)")
    content_type: Literal["markdown", "json", "html"] = Field(
        default="markdown", description="Content format"
    )
    word_count: int = Field(..., description="Word count")
    estimated_read_time: int = Field(..., description="Estimated read time in minutes")
    metadata: ChapterMetadata = Field(..., description="Chapter metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "ch1-intro-to-agents",
                "title": "Introduction to AI Agents",
                "content": "# Introduction to AI Agents\n\nAI Agents are...",
                "content_type": "markdown",
                "word_count": 1250,
                "estimated_read_time": 5,
                "metadata": {
                    "module": 1,
                    "order": 1,
                    "tags": ["fundamentals", "intro"],
                    "difficulty": "beginner",
                },
                "created_at": "2026-01-10T00:00:00Z",
                "updated_at": "2026-01-12T15:30:00Z",
            }
        }


class ChapterListItem(BaseModel):
    """Chapter list item (without full content)."""

    chapter_id: str = Field(..., description="Unique chapter identifier")
    title: str = Field(..., description="Chapter title")
    module: int = Field(..., description="Module number")
    order: int = Field(..., description="Chapter order")
    difficulty: str = Field(..., description="Difficulty level")
    word_count: int = Field(..., description="Word count")
    estimated_read_time: int = Field(..., description="Estimated read time in minutes")
    is_locked: bool = Field(..., description="Whether chapter is locked for user")
    required_tier: Optional[str] = Field(
        default=None, description="Required subscription tier if locked"
    )
    completed: bool = Field(default=False, description="Whether user completed chapter")
    completed_at: Optional[datetime] = Field(
        default=None, description="Completion timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "ch1-intro-to-agents",
                "title": "Introduction to AI Agents",
                "module": 1,
                "order": 1,
                "difficulty": "beginner",
                "word_count": 1250,
                "estimated_read_time": 5,
                "is_locked": False,
                "required_tier": None,
                "completed": True,
                "completed_at": "2026-01-14T10:30:00Z",
            }
        }


class ChapterListResponse(BaseModel):
    """List of chapters response."""

    chapters: List[ChapterListItem] = Field(..., description="List of chapters")
    total_chapters: int = Field(..., description="Total number of chapters")
    completed_count: int = Field(..., description="Number of completed chapters")
    locked_count: int = Field(..., description="Number of locked chapters")

    class Config:
        json_schema_extra = {
            "example": {
                "chapters": [],
                "total_chapters": 9,
                "completed_count": 3,
                "locked_count": 3,
            }
        }


class ModuleChapterSummary(BaseModel):
    """Brief chapter info for module response."""

    chapter_id: str
    title: str
    order: int


class ModuleResponse(BaseModel):
    """Module details response."""

    module_id: str = Field(..., description="Unique module identifier")
    title: str = Field(..., description="Module title")
    description: Optional[str] = Field(None, description="Module description")
    order: int = Field(..., description="Module order")
    chapters: List[ModuleChapterSummary] = Field(..., description="Chapters in module")
    total_chapters: int = Field(..., description="Total chapters in module")
    estimated_duration_minutes: int = Field(
        ..., description="Estimated duration in minutes"
    )
    difficulty: str = Field(..., description="Difficulty level")
    prerequisites: List[str] = Field(
        default_factory=list, description="Required module IDs"
    )
    learning_objectives: List[str] = Field(
        default_factory=list, description="Learning objectives"
    )
    is_locked: bool = Field(default=False, description="Whether module is locked")
    required_tier: Optional[str] = Field(
        default=None, description="Required tier if locked"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "module_id": "mod-1-foundations",
                "title": "Foundations of AI Agents",
                "description": "Learn the core concepts of AI Agents",
                "order": 1,
                "chapters": [
                    {
                        "chapter_id": "ch1-intro-to-agents",
                        "title": "Introduction to AI Agents",
                        "order": 1,
                    }
                ],
                "total_chapters": 3,
                "estimated_duration_minutes": 70,
                "difficulty": "beginner",
                "prerequisites": [],
                "learning_objectives": [
                    "Understand what AI agents are",
                    "Learn the 8-layer architecture",
                ],
                "is_locked": False,
                "required_tier": None,
            }
        }


class ModuleListResponse(BaseModel):
    """List of modules response."""

    modules: List[ModuleResponse] = Field(..., description="List of modules")
    total_modules: int = Field(..., description="Total number of modules")


class MediaAssetResponse(BaseModel):
    """Media asset details."""

    asset_id: str = Field(..., description="Unique asset identifier")
    type: str = Field(..., description="Asset type (image, video, diagram)")
    url: str = Field(..., description="Asset URL")
    alt_text: Optional[str] = Field(None, description="Alt text for accessibility")
    caption: Optional[str] = Field(None, description="Asset caption")
    width: Optional[int] = Field(None, description="Width in pixels")
    height: Optional[int] = Field(None, description="Height in pixels")
    duration_seconds: Optional[int] = Field(None, description="Duration for video")
    size_bytes: int = Field(..., description="File size in bytes")
    thumbnail: Optional[str] = Field(None, description="Thumbnail URL for video")

    class Config:
        json_schema_extra = {
            "example": {
                "asset_id": "img-agent-architecture",
                "type": "image",
                "url": "https://r2.example.com/media/ch1/agent-architecture.png",
                "alt_text": "Agent Factory Architecture Diagram",
                "caption": "The 8-layer Agent Factory architecture",
                "width": 1200,
                "height": 800,
                "size_bytes": 125840,
            }
        }


class ChapterMediaResponse(BaseModel):
    """Chapter media assets response."""

    chapter_id: str = Field(..., description="Chapter identifier")
    media: List[MediaAssetResponse] = Field(..., description="List of media assets")
