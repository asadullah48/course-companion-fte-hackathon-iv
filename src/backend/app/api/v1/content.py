"""
Content Delivery API
Serves course content verbatim from R2 storage

CONSTITUTIONAL COMPLIANCE:
- ✅ Content served byte-for-byte as stored
- ❌ NO LLM processing
- ❌ NO summarization
- ❌ NO content transformation
"""

from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core import (
    ActiveUser,
    DbSession,
    OptionalUser,
    ChapterNotFoundError,
    ModuleNotFoundError,
    AccessDeniedError,
    get_r2_client,
)
from app.models.content import Chapter, Module, MediaAsset
from app.models.progress import ChapterProgress, ProgressStatus
from app.schemas.content import (
    ChapterResponse,
    ChapterListItem,
    ChapterListResponse,
    ChapterMetadata,
    ModuleResponse,
    ModuleListResponse,
    ModuleChapterSummary,
    MediaAssetResponse,
    ChapterMediaResponse,
)

router = APIRouter()


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: str,
    format: Literal["markdown", "json", "html"] = Query(
        default="markdown", description="Response format"
    ),
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get chapter content verbatim from R2.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Content served byte-for-byte as stored
    - ❌ NO LLM processing
    - ❌ NO summarization
    - ❌ NO content transformation

    Args:
        chapter_id: Unique chapter identifier
        format: Response format (markdown, json, html)

    Returns:
        ChapterResponse with full content
    """
    # Get chapter metadata from database
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .where(Chapter.chapter_id == chapter_id)
    )
    chapter = result.scalar_one_or_none()

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "chapter_not_found",
                "message": f"Chapter '{chapter_id}' does not exist",
                "chapter_id": chapter_id,
            },
        )

    # Check access control
    if not chapter.is_accessible_by(user.tier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "access_denied",
                "message": "Premium subscription required for this chapter",
                "chapter_id": chapter_id,
                "required_tier": chapter.get_access_tier(),
                "upgrade_url": "/api/v1/pricing",
            },
        )

    # Fetch content from R2 (verbatim)
    r2_client = get_r2_client()
    content = await r2_client.get_object_text(chapter.r2_key)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "content_not_found",
                "message": f"Content for chapter '{chapter_id}' not found in storage",
                "chapter_id": chapter_id,
            },
        )

    # Calculate derived fields (deterministic only)
    word_count = len(content.split())
    estimated_read_time = max(1, word_count // 250)  # 250 words/min

    return ChapterResponse(
        chapter_id=chapter.chapter_id,
        title=chapter.title,
        content=content,  # ✅ Verbatim, no LLM processing
        content_type=format,
        word_count=word_count,
        estimated_read_time=estimated_read_time,
        metadata=ChapterMetadata(
            module=chapter.module.order if chapter.module else 0,
            order=chapter.order,
            tags=chapter.tags or [],
            difficulty=chapter.difficulty,
        ),
        created_at=chapter.created_at,
        updated_at=chapter.updated_at,
    )


@router.get("/chapters", response_model=ChapterListResponse)
async def list_chapters(
    module: Optional[int] = Query(default=None, description="Filter by module number"),
    include_locked: bool = Query(
        default=False, description="Include locked chapters"
    ),
    sort: Literal["order", "recent", "difficulty"] = Query(
        default="order", description="Sort order"
    ),
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    List all chapters with metadata (no content).

    Args:
        module: Filter by module number
        include_locked: Include chapters user can't access
        sort: Sort order

    Returns:
        ChapterListResponse with chapter metadata
    """
    # Build query
    query = select(Chapter).options(selectinload(Chapter.module))

    if module is not None:
        query = query.join(Module).where(Module.order == module)

    # Apply sorting
    if sort == "order":
        query = query.order_by(Chapter.order)
    elif sort == "recent":
        query = query.order_by(Chapter.updated_at.desc())
    elif sort == "difficulty":
        query = query.order_by(Chapter.difficulty)

    result = await db.execute(query)
    chapters = result.scalars().all()

    # Get user's progress
    user_progress = {}
    if user:
        progress_result = await db.execute(
            select(ChapterProgress).where(ChapterProgress.user_id == user.id)
        )
        for prog in progress_result.scalars():
            user_progress[str(prog.chapter_id)] = prog

    # Build response
    user_tier = user.tier if user else None
    chapter_list = []
    completed_count = 0
    locked_count = 0

    for chapter in chapters:
        is_locked = user_tier is None or not chapter.is_accessible_by(user_tier)

        if is_locked and not include_locked:
            continue

        if is_locked:
            locked_count += 1

        # Check completion status
        progress = user_progress.get(str(chapter.id))
        completed = progress and progress.status == ProgressStatus.COMPLETED
        if completed:
            completed_count += 1

        chapter_list.append(
            ChapterListItem(
                chapter_id=chapter.chapter_id,
                title=chapter.title,
                module=chapter.module.order if chapter.module else 0,
                order=chapter.order,
                difficulty=chapter.difficulty,
                word_count=chapter.word_count,
                estimated_read_time=chapter.estimated_read_time,
                is_locked=is_locked,
                required_tier=chapter.get_access_tier() if is_locked else None,
                completed=completed,
                completed_at=progress.completed_at if progress and completed else None,
            )
        )

    return ChapterListResponse(
        chapters=chapter_list,
        total_chapters=len(chapters),
        completed_count=completed_count,
        locked_count=locked_count,
    )


@router.get("/chapters/{chapter_id}/media", response_model=ChapterMediaResponse)
async def get_chapter_media(
    chapter_id: str,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get media assets for a chapter.

    Args:
        chapter_id: Chapter identifier

    Returns:
        List of media assets
    """
    # Get chapter
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.media_assets))
        .where(Chapter.chapter_id == chapter_id)
    )
    chapter = result.scalar_one_or_none()

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "chapter_not_found",
                "message": f"Chapter '{chapter_id}' does not exist",
                "chapter_id": chapter_id,
            },
        )

    # Check access
    if not chapter.is_accessible_by(user.tier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "access_denied",
                "message": "Premium subscription required",
                "required_tier": chapter.get_access_tier(),
            },
        )

    media_list = [
        MediaAssetResponse(
            asset_id=asset.asset_id,
            type=asset.type,
            url=asset.url,
            alt_text=asset.alt_text,
            caption=asset.caption,
            width=asset.width,
            height=asset.height,
            duration_seconds=asset.duration_seconds,
            size_bytes=asset.size_bytes,
            thumbnail=asset.thumbnail_url,
        )
        for asset in chapter.media_assets
    ]

    return ChapterMediaResponse(chapter_id=chapter_id, media=media_list)


@router.get("/modules/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: str,
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Get module details and chapter list.

    Args:
        module_id: Module identifier (e.g., "mod-1-foundations" or "1")

    Returns:
        ModuleResponse with module details
    """
    # Try to find by module_id string or by order number
    query = select(Module).options(selectinload(Module.chapters))

    if module_id.isdigit():
        query = query.where(Module.order == int(module_id))
    else:
        query = query.where(Module.module_id == module_id)

    result = await db.execute(query)
    module = result.scalar_one_or_none()

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "module_not_found",
                "message": f"Module '{module_id}' does not exist",
                "module_id": module_id,
            },
        )

    user_tier = user.tier if user else None
    is_locked = user_tier is None or not module.is_accessible_by(user_tier)

    chapters = [
        ModuleChapterSummary(
            chapter_id=ch.chapter_id,
            title=ch.title,
            order=ch.order,
        )
        for ch in sorted(module.chapters, key=lambda x: x.order)
    ]

    return ModuleResponse(
        module_id=module.module_id,
        title=module.title,
        description=module.description,
        order=module.order,
        chapters=chapters,
        total_chapters=len(chapters),
        estimated_duration_minutes=module.estimated_duration_minutes,
        difficulty=module.difficulty,
        prerequisites=module.prerequisites or [],
        learning_objectives=module.learning_objectives or [],
        is_locked=is_locked,
        required_tier=module.access_tier if is_locked else None,
    )


@router.get("/modules", response_model=ModuleListResponse)
async def list_modules(
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    List all modules.

    Returns:
        ModuleListResponse with all modules
    """
    result = await db.execute(
        select(Module).options(selectinload(Module.chapters)).order_by(Module.order)
    )
    modules = result.scalars().all()

    user_tier = user.tier if user else None

    module_list = []
    for module in modules:
        is_locked = user_tier is None or not module.is_accessible_by(user_tier)

        chapters = [
            ModuleChapterSummary(
                chapter_id=ch.chapter_id,
                title=ch.title,
                order=ch.order,
            )
            for ch in sorted(module.chapters, key=lambda x: x.order)
        ]

        module_list.append(
            ModuleResponse(
                module_id=module.module_id,
                title=module.title,
                description=module.description,
                order=module.order,
                chapters=chapters,
                total_chapters=len(chapters),
                estimated_duration_minutes=module.estimated_duration_minutes,
                difficulty=module.difficulty,
                prerequisites=module.prerequisites or [],
                learning_objectives=module.learning_objectives or [],
                is_locked=is_locked,
                required_tier=module.access_tier if is_locked else None,
            )
        )

    return ModuleListResponse(modules=module_list, total_modules=len(module_list))
