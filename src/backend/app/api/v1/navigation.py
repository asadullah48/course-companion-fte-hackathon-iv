"""
Navigation API
Course navigation and structure endpoints
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core import ActiveUser, DbSession, OptionalUser
from app.models.content import Chapter, Module
from app.models.progress import ChapterProgress, ProgressStatus

router = APIRouter()


class NavigationContext(BaseModel):
    """Current navigation context."""

    current_chapter: Optional[str] = Field(None, description="Current chapter ID")
    current_module: Optional[str] = Field(None, description="Current module ID")
    previous_chapter: Optional[str] = Field(None, description="Previous chapter ID")
    next_chapter: Optional[str] = Field(None, description="Next chapter ID")
    previous_module: Optional[str] = Field(None, description="Previous module ID")
    next_module: Optional[str] = Field(None, description="Next module ID")
    is_first_chapter: bool = Field(default=False)
    is_last_chapter: bool = Field(default=False)
    is_first_in_module: bool = Field(default=False)
    is_last_in_module: bool = Field(default=False)
    progress_percentage: int = Field(default=0)


class BreadcrumbItem(BaseModel):
    """Breadcrumb navigation item."""

    id: str
    title: str
    type: str  # "course", "module", "chapter"
    url: str
    is_current: bool = False


class BreadcrumbResponse(BaseModel):
    """Breadcrumb navigation response."""

    items: list[BreadcrumbItem]


class CourseStructure(BaseModel):
    """Full course structure for navigation."""

    total_modules: int
    total_chapters: int
    modules: list["ModuleNavigation"]


class ModuleNavigation(BaseModel):
    """Module in navigation structure."""

    module_id: str
    title: str
    order: int
    is_locked: bool
    chapters: list["ChapterNavigation"]


class ChapterNavigation(BaseModel):
    """Chapter in navigation structure."""

    chapter_id: str
    title: str
    order: int
    is_locked: bool
    is_completed: bool


@router.get("/navigation/context/{chapter_id}", response_model=NavigationContext)
async def get_navigation_context(
    chapter_id: str,
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Get navigation context for a chapter.

    Provides previous/next chapter and module navigation.

    Args:
        chapter_id: Current chapter identifier

    Returns:
        NavigationContext with navigation links
    """
    # Get current chapter with module
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .where(Chapter.chapter_id == chapter_id)
    )
    current_chapter = result.scalar_one_or_none()

    if current_chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "chapter_not_found",
                "message": f"Chapter '{chapter_id}' does not exist",
            },
        )

    # Get all chapters ordered
    all_chapters_result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .order_by(Chapter.order)
    )
    all_chapters = list(all_chapters_result.scalars())

    # Find current position
    current_idx = None
    for i, ch in enumerate(all_chapters):
        if ch.chapter_id == chapter_id:
            current_idx = i
            break

    if current_idx is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "internal_error", "message": "Chapter index not found"},
        )

    # Determine previous/next
    prev_chapter = all_chapters[current_idx - 1] if current_idx > 0 else None
    next_chapter = (
        all_chapters[current_idx + 1] if current_idx < len(all_chapters) - 1 else None
    )

    # Check module boundaries
    current_module = current_chapter.module
    is_first_in_module = (
        prev_chapter is None or prev_chapter.module.id != current_module.id
    )
    is_last_in_module = (
        next_chapter is None or next_chapter.module.id != current_module.id
    )

    # Get modules for prev/next module navigation
    modules_result = await db.execute(select(Module).order_by(Module.order))
    all_modules = list(modules_result.scalars())

    current_module_idx = None
    for i, mod in enumerate(all_modules):
        if mod.id == current_module.id:
            current_module_idx = i
            break

    prev_module = all_modules[current_module_idx - 1] if current_module_idx > 0 else None
    next_module = (
        all_modules[current_module_idx + 1]
        if current_module_idx < len(all_modules) - 1
        else None
    )

    # Calculate progress
    completed_count = 0
    if user:
        progress_result = await db.execute(
            select(ChapterProgress)
            .where(ChapterProgress.user_id == user.id)
            .where(ChapterProgress.status == ProgressStatus.COMPLETED)
        )
        completed_count = len(list(progress_result.scalars()))

    progress_pct = (
        round(completed_count / len(all_chapters) * 100) if all_chapters else 0
    )

    return NavigationContext(
        current_chapter=current_chapter.chapter_id,
        current_module=current_module.module_id,
        previous_chapter=prev_chapter.chapter_id if prev_chapter else None,
        next_chapter=next_chapter.chapter_id if next_chapter else None,
        previous_module=prev_module.module_id if prev_module else None,
        next_module=next_module.module_id if next_module else None,
        is_first_chapter=current_idx == 0,
        is_last_chapter=current_idx == len(all_chapters) - 1,
        is_first_in_module=is_first_in_module,
        is_last_in_module=is_last_in_module,
        progress_percentage=progress_pct,
    )


@router.get("/navigation/breadcrumb/{chapter_id}", response_model=BreadcrumbResponse)
async def get_breadcrumb(
    chapter_id: str,
    db: DbSession = None,
):
    """
    Get breadcrumb navigation for a chapter.

    Args:
        chapter_id: Chapter identifier

    Returns:
        Breadcrumb items from course -> module -> chapter
    """
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .where(Chapter.chapter_id == chapter_id)
    )
    chapter = result.scalar_one_or_none()

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "chapter_not_found"},
        )

    items = [
        BreadcrumbItem(
            id="course",
            title="AI Agent Development",
            type="course",
            url="/api/v1/modules",
            is_current=False,
        ),
        BreadcrumbItem(
            id=chapter.module.module_id,
            title=chapter.module.title,
            type="module",
            url=f"/api/v1/modules/{chapter.module.module_id}",
            is_current=False,
        ),
        BreadcrumbItem(
            id=chapter.chapter_id,
            title=chapter.title,
            type="chapter",
            url=f"/api/v1/chapters/{chapter.chapter_id}",
            is_current=True,
        ),
    ]

    return BreadcrumbResponse(items=items)


@router.get("/navigation/structure", response_model=CourseStructure)
async def get_course_structure(
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Get full course structure for navigation sidebar.

    Returns:
        Complete course structure with modules and chapters
    """
    # Get all modules with chapters
    result = await db.execute(
        select(Module)
        .options(selectinload(Module.chapters))
        .order_by(Module.order)
    )
    modules = list(result.scalars())

    # Get user's progress
    user_progress = {}
    if user:
        progress_result = await db.execute(
            select(ChapterProgress).where(ChapterProgress.user_id == user.id)
        )
        for prog in progress_result.scalars():
            user_progress[str(prog.chapter_id)] = prog

    user_tier = user.tier if user else None

    module_list = []
    total_chapters = 0

    for module in modules:
        is_module_locked = user_tier is None or not module.is_accessible_by(user_tier)

        chapter_list = []
        for chapter in sorted(module.chapters, key=lambda x: x.order):
            is_chapter_locked = user_tier is None or not chapter.is_accessible_by(
                user_tier
            )
            progress = user_progress.get(str(chapter.id))
            is_completed = progress and progress.status == ProgressStatus.COMPLETED

            chapter_list.append(
                ChapterNavigation(
                    chapter_id=chapter.chapter_id,
                    title=chapter.title,
                    order=chapter.order,
                    is_locked=is_chapter_locked,
                    is_completed=is_completed,
                )
            )
            total_chapters += 1

        module_list.append(
            ModuleNavigation(
                module_id=module.module_id,
                title=module.title,
                order=module.order,
                is_locked=is_module_locked,
                chapters=chapter_list,
            )
        )

    return CourseStructure(
        total_modules=len(module_list),
        total_chapters=total_chapters,
        modules=module_list,
    )


@router.get("/navigation/resume")
async def get_resume_point(
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get the chapter where user should resume.

    Returns the first incomplete chapter or the last completed chapter.

    Returns:
        Resume point with chapter ID and context
    """
    # Get all chapters ordered
    chapters_result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .order_by(Chapter.order)
    )
    all_chapters = list(chapters_result.scalars())

    if not all_chapters:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "no_content", "message": "No chapters available"},
        )

    # Get user's progress
    progress_result = await db.execute(
        select(ChapterProgress).where(ChapterProgress.user_id == user.id)
    )
    user_progress = {str(p.chapter_id): p for p in progress_result.scalars()}

    # Find first incomplete chapter that user can access
    resume_chapter = None
    last_completed = None

    for chapter in all_chapters:
        if not chapter.is_accessible_by(user.tier):
            continue

        progress = user_progress.get(str(chapter.id))

        if progress and progress.status == ProgressStatus.COMPLETED:
            last_completed = chapter
        elif resume_chapter is None:
            # First incomplete chapter
            resume_chapter = chapter
            break

    # If no incomplete chapter found, resume at last completed or first chapter
    if resume_chapter is None:
        resume_chapter = last_completed or all_chapters[0]

    return {
        "resume_chapter_id": resume_chapter.chapter_id,
        "resume_chapter_title": resume_chapter.title,
        "resume_module_id": resume_chapter.module.module_id,
        "resume_module_title": resume_chapter.module.title,
        "is_continuation": last_completed is not None,
        "completed_chapters": len(
            [p for p in user_progress.values() if p.status == ProgressStatus.COMPLETED]
        ),
        "total_chapters": len(all_chapters),
    }
