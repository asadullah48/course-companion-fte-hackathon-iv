"""
Search API
Content search endpoints

CONSTITUTIONAL COMPLIANCE:
- ✅ SQL full-text search
- ✅ Pattern matching
- ❌ NO LLM-based semantic search
- ❌ NO embedding-based similarity
"""

from typing import List, Literal, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.core import OptionalUser, DbSession
from app.models.content import Chapter, Module

router = APIRouter()


class SearchResult(BaseModel):
    """Individual search result."""

    id: str = Field(..., description="Content ID")
    type: Literal["chapter", "module"] = Field(..., description="Content type")
    title: str = Field(..., description="Content title")
    excerpt: Optional[str] = Field(None, description="Matching excerpt")
    module_id: Optional[str] = Field(None, description="Parent module ID")
    chapter_id: Optional[str] = Field(None, description="Chapter ID if applicable")
    relevance_score: float = Field(..., description="Search relevance score")
    is_locked: bool = Field(default=False, description="Whether content is locked")


class SearchResponse(BaseModel):
    """Search results response."""

    query: str = Field(..., description="Search query")
    total_results: int = Field(..., description="Total matching results")
    results: List[SearchResult] = Field(..., description="Search results")
    suggestions: List[str] = Field(default_factory=list, description="Search suggestions")


class TagSearchResponse(BaseModel):
    """Tag search response."""

    tag: str = Field(..., description="Searched tag")
    chapters: List[dict] = Field(..., description="Chapters with this tag")


@router.get("/search", response_model=SearchResponse)
async def search_content(
    q: str = Query(..., min_length=2, max_length=100, description="Search query"),
    type: Optional[Literal["all", "chapter", "module"]] = Query(
        default="all", description="Filter by content type"
    ),
    module: Optional[int] = Query(default=None, description="Filter by module number"),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum results"),
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Search course content.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL LIKE/ILIKE pattern matching
    - ✅ PostgreSQL full-text search
    - ❌ NO LLM semantic understanding
    - ❌ NO embedding similarity

    Args:
        q: Search query
        type: Filter by content type
        module: Filter by module number
        limit: Maximum results

    Returns:
        SearchResponse with matching content
    """
    results = []
    search_pattern = f"%{q.lower()}%"

    user_tier = user.tier if user else None

    # Search chapters
    if type in ("all", "chapter"):
        query = (
            select(Chapter)
            .options(selectinload(Chapter.module))
        )

        # Apply filters
        query = query.where(
            or_(
                func.lower(Chapter.title).like(search_pattern),
                func.lower(Chapter.chapter_id).like(search_pattern),
            )
        )

        if module is not None:
            query = query.join(Module).where(Module.order == module)

        query = query.limit(limit)

        result = await db.execute(query)
        chapters = result.scalars().all()

        for chapter in chapters:
            is_locked = user_tier is None or not chapter.is_accessible_by(user_tier)

            # Calculate simple relevance (title match higher than ID match)
            title_lower = chapter.title.lower()
            query_lower = q.lower()
            if query_lower in title_lower:
                relevance = 1.0 - (title_lower.index(query_lower) / len(title_lower))
            else:
                relevance = 0.5

            results.append(
                SearchResult(
                    id=chapter.chapter_id,
                    type="chapter",
                    title=chapter.title,
                    excerpt=None,
                    module_id=chapter.module.module_id if chapter.module else None,
                    chapter_id=chapter.chapter_id,
                    relevance_score=relevance,
                    is_locked=is_locked,
                )
            )

    # Search modules
    if type in ("all", "module"):
        query = select(Module).where(
            or_(
                func.lower(Module.title).like(search_pattern),
                func.lower(Module.module_id).like(search_pattern),
                func.lower(Module.description).like(search_pattern),
            )
        ).limit(limit)

        result = await db.execute(query)
        modules = result.scalars().all()

        for mod in modules:
            is_locked = user_tier is None or not mod.is_accessible_by(user_tier)

            title_lower = mod.title.lower()
            query_lower = q.lower()
            if query_lower in title_lower:
                relevance = 1.0 - (title_lower.index(query_lower) / len(title_lower))
            else:
                relevance = 0.5

            results.append(
                SearchResult(
                    id=mod.module_id,
                    type="module",
                    title=mod.title,
                    excerpt=mod.description[:200] if mod.description else None,
                    module_id=mod.module_id,
                    chapter_id=None,
                    relevance_score=relevance,
                    is_locked=is_locked,
                )
            )

    # Sort by relevance
    results.sort(key=lambda x: x.relevance_score, reverse=True)

    # Limit results
    results = results[:limit]

    # Generate suggestions (simple autocomplete)
    suggestions = []
    if len(results) == 0:
        # Suggest similar terms
        all_chapters = await db.execute(select(Chapter.title).limit(100))
        all_titles = [t[0] for t in all_chapters]
        for title in all_titles:
            if any(word.lower().startswith(q.lower()[:3]) for word in title.split()):
                suggestions.append(title)
                if len(suggestions) >= 5:
                    break

    return SearchResponse(
        query=q,
        total_results=len(results),
        results=results,
        suggestions=suggestions,
    )


@router.get("/search/tags/{tag}", response_model=TagSearchResponse)
async def search_by_tag(
    tag: str,
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Search chapters by tag.

    Args:
        tag: Tag to search for

    Returns:
        Chapters with matching tag
    """
    # PostgreSQL array contains
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .where(Chapter.tags.contains([tag]))
    )
    chapters = result.scalars().all()

    user_tier = user.tier if user else None

    chapter_list = [
        {
            "chapter_id": ch.chapter_id,
            "title": ch.title,
            "module_id": ch.module.module_id if ch.module else None,
            "difficulty": ch.difficulty,
            "is_locked": user_tier is None or not ch.is_accessible_by(user_tier),
        }
        for ch in chapters
    ]

    return TagSearchResponse(tag=tag, chapters=chapter_list)


@router.get("/search/tags")
async def list_all_tags(db: DbSession = None):
    """
    List all unique tags in the course.

    Returns:
        List of all tags with counts
    """
    result = await db.execute(
        select(Chapter.tags).where(Chapter.tags.isnot(None))
    )

    # Flatten and count tags
    tag_counts = {}
    for row in result:
        if row.tags:
            for tag in row.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Sort by count
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "tags": [{"tag": tag, "count": count} for tag, count in sorted_tags],
        "total_tags": len(tag_counts),
    }


@router.get("/search/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, max_length=50),
    limit: int = Query(default=10, ge=1, le=20),
    db: DbSession = None,
):
    """
    Get autocomplete suggestions for search.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL prefix matching
    - ❌ NO LLM completion

    Args:
        q: Partial search query
        limit: Maximum suggestions

    Returns:
        List of search suggestions
    """
    pattern = f"{q.lower()}%"

    # Get matching chapter titles
    result = await db.execute(
        select(Chapter.title)
        .where(func.lower(Chapter.title).like(pattern))
        .limit(limit)
    )
    titles = [r[0] for r in result]

    # Get matching module titles
    result = await db.execute(
        select(Module.title)
        .where(func.lower(Module.title).like(pattern))
        .limit(limit)
    )
    titles.extend([r[0] for r in result])

    # Deduplicate and limit
    unique_titles = list(dict.fromkeys(titles))[:limit]

    return {"suggestions": unique_titles, "query": q}
