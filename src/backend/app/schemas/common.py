"""
Common Schemas
Shared response models for API
"""

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict[str, Any]] = Field(
        default=None, description="Additional error details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "chapter_not_found",
                "message": "Chapter 'ch99-invalid' does not exist",
                "details": {"chapter_id": "ch99-invalid"},
            }
        }


class SuccessResponse(BaseModel):
    """Standard success response schema."""

    success: bool = Field(default=True, description="Operation success flag")
    message: Optional[str] = Field(default=None, description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Operation completed successfully",
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "page_size": 10,
                "pages": 10,
                "has_next": True,
                "has_prev": False,
            }
        }
