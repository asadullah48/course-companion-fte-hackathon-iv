"""
Progress Tracking API
User progress, streaks, and achievements

CONSTITUTIONAL COMPLIANCE:
- ✅ SQL-based progress calculations
- ✅ Rule-based achievement unlocking
- ✅ Arithmetic operations (percentage, streak count)
- ❌ NO LLM-based progress recommendations
- ❌ NO AI-generated motivational messages
"""

from datetime import datetime, date, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core import ActiveUser, DbSession
from app.models.content import Chapter, Module
from app.models.progress import (
    ChapterProgress,
    LearningSession,
    UserStreak,
    ProgressStatus,
    ActivityType,
)
from app.models.achievement import Achievement, UserAchievement, ACHIEVEMENT_RULES
from app.schemas.progress import (
    ProgressSummary,
    ModuleProgress,
    ChapterProgressDetail,
    ProgressResponse,
    ChapterCompletionRequest,
    ChapterCompletionResponse,
    AchievementUnlocked,
    StreakUpdate,
    StreakResponse,
    StreakHistoryItem,
    StreakMilestones,
    TimeLogRequest,
    TimeLogResponse,
)
from app.schemas.achievement import (
    AchievementResponse,
    AchievementProgress,
    AchievementsListResponse,
)

router = APIRouter()


async def calculate_user_stats(user_id: str, db) -> dict:
    """
    Calculate user statistics for achievement checking.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL aggregation queries
    - ✅ Pure arithmetic calculations
    - ❌ NO LLM analysis
    """
    # Get chapter completion stats
    chapter_stats = await db.execute(
        select(
            func.count(ChapterProgress.id).filter(
                ChapterProgress.status == ProgressStatus.COMPLETED
            ).label("completed"),
            func.count(ChapterProgress.id).label("total"),
        ).where(ChapterProgress.user_id == user_id)
    )
    row = chapter_stats.first()
    chapters_completed = row.completed if row else 0

    # Total chapters in course
    total_chapters_result = await db.execute(select(func.count(Chapter.id)))
    total_chapters = total_chapters_result.scalar() or 9

    # Get streak
    streak_result = await db.execute(
        select(UserStreak).where(UserStreak.user_id == user_id)
    )
    streak = streak_result.scalar_one_or_none()

    # Get best quiz score
    from app.models.quiz import QuizAttempt

    quiz_stats = await db.execute(
        select(func.max(QuizAttempt.score)).where(
            QuizAttempt.user_id == user_id,
            QuizAttempt.submitted_at.isnot(None),
        )
    )
    best_quiz_score = quiz_stats.scalar() or 0

    # Get total learning time
    time_stats = await db.execute(
        select(func.sum(LearningSession.duration_minutes)).where(
            LearningSession.user_id == user_id
        )
    )
    total_time = time_stats.scalar() or 0

    # Get completed modules
    modules_completed = {}
    modules_result = await db.execute(
        select(Module).options(selectinload(Module.chapters))
    )
    for module in modules_result.scalars():
        module_chapters = [ch.id for ch in module.chapters]
        completed_in_module = await db.execute(
            select(func.count(ChapterProgress.id)).where(
                ChapterProgress.user_id == user_id,
                ChapterProgress.chapter_id.in_(module_chapters),
                ChapterProgress.status == ProgressStatus.COMPLETED,
            )
        )
        completed_count = completed_in_module.scalar() or 0
        modules_completed[module.order] = completed_count == len(module_chapters)

    return {
        "chapters_completed": chapters_completed,
        "total_chapters": total_chapters,
        "completion_percentage": round(chapters_completed / total_chapters * 100)
        if total_chapters > 0
        else 0,
        "current_streak": streak.current_streak if streak else 0,
        "longest_streak": streak.longest_streak if streak else 0,
        "best_quiz_score": best_quiz_score,
        "total_time_minutes": total_time,
        "modules_completed": modules_completed,
    }


async def check_achievements(user_id: str, stats: dict, db) -> List[dict]:
    """
    Check and unlock new achievements (rule-based only).

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Deterministic lambda conditions
    - ❌ NO LLM involvement
    """
    new_achievements = []

    # Get existing achievements
    existing_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
    )
    existing_ids = {str(a) for a in existing_result.scalars()}

    for achievement_id, rule in ACHIEVEMENT_RULES.items():
        # Check if already earned
        achievement_result = await db.execute(
            select(Achievement).where(Achievement.achievement_id == achievement_id)
        )
        achievement = achievement_result.scalar_one_or_none()

        if achievement is None:
            continue

        if str(achievement.id) in existing_ids:
            continue

        # Check rule condition (deterministic lambda)
        if rule["condition"](stats):
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement.id,
                unlocked_at=datetime.utcnow(),
            )
            db.add(user_achievement)

            new_achievements.append({
                "achievement_id": achievement_id,
                "name": rule["name"],
                "description": rule["description"],
                "points": rule["points"],
                "unlocked_at": datetime.utcnow(),
            })

    if new_achievements:
        await db.commit()

    return new_achievements


@router.get("/progress/{user_id}", response_model=ProgressResponse)
async def get_progress(
    user_id: str,
    include_chapters: bool = Query(default=False),
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get user progress summary.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL aggregation queries
    - ✅ Arithmetic percentage calculations
    - ❌ NO LLM analysis
    - ❌ NO AI recommendations

    Args:
        user_id: User identifier
        include_chapters: Include chapter-level details

    Returns:
        ProgressResponse with overall and module progress
    """
    # Verify user can access this data
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied", "message": "Cannot access other user's progress"},
        )

    stats = await calculate_user_stats(user_id, db)

    # Get module-level progress
    modules_result = await db.execute(
        select(Module).options(selectinload(Module.chapters)).order_by(Module.order)
    )
    modules = list(modules_result.scalars())

    module_progress_list = []
    for module in modules:
        # Count completed chapters in this module
        chapter_ids = [ch.id for ch in module.chapters]
        completed_result = await db.execute(
            select(func.count(ChapterProgress.id)).where(
                ChapterProgress.user_id == user_id,
                ChapterProgress.chapter_id.in_(chapter_ids),
                ChapterProgress.status == ProgressStatus.COMPLETED,
            )
        )
        completed_count = completed_result.scalar() or 0

        time_result = await db.execute(
            select(func.sum(ChapterProgress.time_spent_minutes)).where(
                ChapterProgress.user_id == user_id,
                ChapterProgress.chapter_id.in_(chapter_ids),
            )
        )
        time_spent = time_result.scalar() or 0

        total_chapters = len(module.chapters)
        completion_pct = round(completed_count / total_chapters * 100) if total_chapters > 0 else 0

        if completed_count == total_chapters:
            status_str = "completed"
        elif completed_count > 0:
            status_str = "in_progress"
        else:
            status_str = "not_started"

        module_progress_list.append(
            ModuleProgress(
                module_id=module.order,
                title=module.title,
                total_chapters=total_chapters,
                completed_chapters=completed_count,
                completion_percentage=completion_pct,
                time_spent_minutes=time_spent,
                status=status_str,
            )
        )

    # Build response
    response = ProgressResponse(
        user_id=user_id,
        overall=ProgressSummary(
            total_chapters=stats["total_chapters"],
            completed_chapters=stats["chapters_completed"],
            completion_percentage=stats["completion_percentage"],
            total_time_minutes=stats["total_time_minutes"],
            current_module=None,
            current_chapter=None,
        ),
        modules=module_progress_list,
        chapters=None,
        last_activity=None,
        member_since=user.created_at,
    )

    if include_chapters:
        chapters_result = await db.execute(
            select(Chapter)
            .options(selectinload(Chapter.module))
            .order_by(Chapter.order)
        )
        chapters = list(chapters_result.scalars())

        progress_result = await db.execute(
            select(ChapterProgress).where(ChapterProgress.user_id == user_id)
        )
        user_progress = {str(p.chapter_id): p for p in progress_result.scalars()}

        chapter_details = []
        for ch in chapters:
            prog = user_progress.get(str(ch.id))
            chapter_details.append(
                ChapterProgressDetail(
                    chapter_id=ch.chapter_id,
                    title=ch.title,
                    module_id=ch.module.order if ch.module else 0,
                    status=prog.status.value if prog else "not_started",
                    started_at=prog.started_at if prog else None,
                    completed_at=prog.completed_at if prog else None,
                    time_spent_minutes=prog.time_spent_minutes if prog else 0,
                    quiz_score=prog.quiz_score if prog else None,
                )
            )

        response.chapters = chapter_details

    return response


@router.put("/progress/{user_id}/chapters/{chapter_id}", response_model=ChapterCompletionResponse)
async def mark_chapter_complete(
    user_id: str,
    chapter_id: str,
    completion: ChapterCompletionRequest,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Mark chapter as complete.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database update
    - ✅ Rule-based achievement checking
    - ❌ NO LLM validation

    Args:
        user_id: User identifier
        chapter_id: Chapter identifier
        completion: Completion details

    Returns:
        ChapterCompletionResponse with updated progress
    """
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied"},
        )

    # Get chapter
    chapter_result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .where(Chapter.chapter_id == chapter_id)
    )
    chapter = chapter_result.scalar_one_or_none()

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "chapter_not_found", "chapter_id": chapter_id},
        )

    # Check if already completed
    existing_result = await db.execute(
        select(ChapterProgress).where(
            ChapterProgress.user_id == user_id,
            ChapterProgress.chapter_id == chapter.id,
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing and existing.status == ProgressStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "already_completed",
                "message": "Chapter is already marked as complete",
                "completed_at": existing.completed_at.isoformat(),
            },
        )

    # Create or update progress
    now = datetime.utcnow()
    if existing:
        existing.status = ProgressStatus.COMPLETED
        existing.completed_at = now
        existing.time_spent_minutes += completion.time_spent_minutes
        if completion.quiz_attempt_id:
            existing.quiz_attempt_id = completion.quiz_attempt_id
    else:
        progress = ChapterProgress(
            user_id=user_id,
            chapter_id=chapter.id,
            status=ProgressStatus.COMPLETED,
            started_at=now,
            completed_at=now,
            time_spent_minutes=completion.time_spent_minutes,
            quiz_attempt_id=completion.quiz_attempt_id,
        )
        db.add(progress)

    # Log activity for streak
    session = LearningSession(
        user_id=user_id,
        chapter_id=chapter.id,
        activity_type=ActivityType.QUIZ if completion.completion_type == "quiz_passed" else ActivityType.READING,
        duration_minutes=completion.time_spent_minutes,
        logged_at=now,
    )
    db.add(session)

    # Update streak
    streak_result = await db.execute(
        select(UserStreak).where(UserStreak.user_id == user_id)
    )
    streak = streak_result.scalar_one_or_none()

    if streak is None:
        streak = UserStreak(user_id=user_id, current_streak=1, longest_streak=1, last_activity_date=date.today())
        db.add(streak)
        is_new_day = True
    else:
        is_new_day = streak.last_activity_date != date.today()
        streak.update_streak(date.today())

    await db.commit()

    # Check for new achievements
    stats = await calculate_user_stats(user_id, db)
    new_achievements = await check_achievements(user_id, stats, db)

    return ChapterCompletionResponse(
        user_id=user_id,
        chapter_id=chapter_id,
        status="completed",
        completed_at=now,
        time_spent_minutes=completion.time_spent_minutes,
        progress_update=ProgressSummary(
            total_chapters=stats["total_chapters"],
            completed_chapters=stats["chapters_completed"],
            completion_percentage=stats["completion_percentage"],
            total_time_minutes=stats["total_time_minutes"],
            current_module=None,
            current_chapter=None,
        ),
        achievements_unlocked=[
            AchievementUnlocked(**a) for a in new_achievements
        ],
        streak_update=StreakUpdate(
            current_streak=streak.current_streak,
            is_new_day=is_new_day,
        ),
    )


@router.get("/progress/{user_id}/streak", response_model=StreakResponse)
async def get_streak(
    user_id: str,
    history_days: int = Query(default=30, ge=1, le=365),
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get learning streak data.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL date calculations
    - ✅ Deterministic streak logic
    - ❌ NO LLM predictions

    Args:
        user_id: User identifier
        history_days: Days of history to include

    Returns:
        StreakResponse with current streak and history
    """
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied"},
        )

    # Get streak data
    streak_result = await db.execute(
        select(UserStreak).where(UserStreak.user_id == user_id)
    )
    streak = streak_result.scalar_one_or_none()

    if streak is None:
        streak = UserStreak(user_id=user_id, current_streak=0, longest_streak=0)

    # Build history
    today = date.today()
    history = []

    for i in range(history_days):
        check_date = today - timedelta(days=i)
        activity_result = await db.execute(
            select(func.sum(LearningSession.duration_minutes)).where(
                LearningSession.user_id == user_id,
                func.date(LearningSession.logged_at) == check_date,
            )
        )
        time_spent = activity_result.scalar() or 0

        history.append(
            StreakHistoryItem(
                date=check_date,
                active=time_spent > 0,
                time_spent_minutes=time_spent,
            )
        )

    # Calculate streak at risk
    today_activity = any(h.date == today and h.active for h in history)
    streak_at_risk = not today_activity and streak.current_streak > 0

    # Hours until streak loss
    if today_activity:
        tomorrow_end = datetime.combine(today + timedelta(days=1), datetime.max.time())
        hours_remaining = (tomorrow_end - datetime.now()).total_seconds() / 3600
    else:
        today_end = datetime.combine(today, datetime.max.time())
        hours_remaining = max(0, (today_end - datetime.now()).total_seconds() / 3600)

    # Milestones
    milestones = [3, 5, 7, 14, 30, 60, 90, 180, 365]
    current = streak.current_streak
    next_milestone = next((m for m in milestones if m > current), None)
    previous_milestones = [m for m in milestones if m <= current]

    # Get freeze info from subscription
    freezes_remaining = 0
    if user.subscription:
        freezes_remaining = user.subscription.streak_freezes_remaining

    return StreakResponse(
        user_id=user_id,
        current_streak=streak.current_streak,
        longest_streak=streak.longest_streak,
        streak_status="active" if today_activity else ("at_risk" if streak_at_risk else "broken"),
        today_activity=today_activity,
        streak_at_risk=streak_at_risk,
        hours_until_streak_loss=hours_remaining,
        history=history,
        milestones=StreakMilestones(
            next_milestone=next_milestone,
            days_to_next=next_milestone - current if next_milestone else None,
            previous_milestones=previous_milestones,
        ),
        freeze_available=freezes_remaining > 0,
        freezes_remaining=freezes_remaining,
    )


@router.get("/progress/{user_id}/achievements", response_model=AchievementsListResponse)
async def get_achievements(
    user_id: str,
    filter: str = Query(default="all", pattern="^(all|earned|locked)$"),
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get user achievements.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database query
    - ✅ Progress calculation (arithmetic)
    - ❌ NO LLM-generated achievement suggestions

    Args:
        user_id: User identifier
        filter: Filter achievements (all, earned, locked)

    Returns:
        AchievementsListResponse with achievements
    """
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied"},
        )

    # Get all achievements with user's unlock status
    achievements_result = await db.execute(select(Achievement).order_by(Achievement.sort_order))
    all_achievements = list(achievements_result.scalars())

    user_achievements_result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    )
    earned_ids = {str(ua.achievement_id): ua for ua in user_achievements_result.scalars()}

    # Get stats for progress calculation
    stats = await calculate_user_stats(user_id, db)

    achievement_list = []
    earned_count = 0
    points_earned = 0
    points_possible = 0

    for achievement in all_achievements:
        is_earned = str(achievement.id) in earned_ids
        user_achievement = earned_ids.get(str(achievement.id))

        if filter == "earned" and not is_earned:
            continue
        if filter == "locked" and is_earned:
            continue

        points_possible += achievement.points
        if is_earned:
            earned_count += 1
            points_earned += achievement.points

        # Calculate progress for locked achievements
        progress = None
        if not is_earned and achievement.requirement_value:
            current = 0
            if achievement.requirement_type == "chapters_completed":
                current = stats["chapters_completed"]
            elif achievement.requirement_type == "completion_percentage":
                current = stats["completion_percentage"]
            elif achievement.requirement_type == "streak_days":
                current = stats["current_streak"]
            elif achievement.requirement_type == "quiz_score":
                current = stats["best_quiz_score"]
            elif achievement.requirement_type == "total_time_minutes":
                current = stats["total_time_minutes"]

            progress = AchievementProgress(
                current=current,
                required=achievement.requirement_value,
                percentage=min(100, round(current / achievement.requirement_value * 100))
                if achievement.requirement_value > 0
                else 0,
            )

        achievement_list.append(
            AchievementResponse(
                achievement_id=achievement.achievement_id,
                name=achievement.name,
                description=achievement.description,
                icon=achievement.icon,
                points=achievement.points,
                category=achievement.category.value,
                status="earned" if is_earned else "locked",
                unlocked_at=user_achievement.unlocked_at if user_achievement else None,
                progress=progress,
            )
        )

    return AchievementsListResponse(
        user_id=user_id,
        total_achievements=len(all_achievements),
        earned_count=earned_count,
        points_earned=points_earned,
        points_possible=points_possible,
        achievements=achievement_list,
        recent_achievements=None,
    )


@router.post("/progress/{user_id}/time", response_model=TimeLogResponse)
async def log_time(
    user_id: str,
    time_log: TimeLogRequest,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Log learning time.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database insert
    - ✅ Streak update
    - ❌ NO LLM analysis

    Args:
        user_id: User identifier
        time_log: Time log details

    Returns:
        TimeLogResponse with logged session
    """
    if user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied"},
        )

    # Get chapter
    chapter_result = await db.execute(
        select(Chapter).where(Chapter.chapter_id == time_log.chapter_id)
    )
    chapter = chapter_result.scalar_one_or_none()

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "chapter_not_found", "chapter_id": time_log.chapter_id},
        )

    # Create session
    now = datetime.utcnow()
    session = LearningSession(
        user_id=user_id,
        chapter_id=chapter.id,
        activity_type=ActivityType(time_log.activity_type),
        duration_minutes=time_log.duration_minutes,
        logged_at=now,
    )
    db.add(session)

    # Update chapter progress time
    progress_result = await db.execute(
        select(ChapterProgress).where(
            ChapterProgress.user_id == user_id,
            ChapterProgress.chapter_id == chapter.id,
        )
    )
    progress = progress_result.scalar_one_or_none()

    if progress:
        progress.time_spent_minutes += time_log.duration_minutes
    else:
        progress = ChapterProgress(
            user_id=user_id,
            chapter_id=chapter.id,
            status=ProgressStatus.IN_PROGRESS,
            started_at=now,
            time_spent_minutes=time_log.duration_minutes,
        )
        db.add(progress)

    # Update streak
    streak_result = await db.execute(
        select(UserStreak).where(UserStreak.user_id == user_id)
    )
    streak = streak_result.scalar_one_or_none()

    if streak is None:
        streak = UserStreak(user_id=user_id, current_streak=1, longest_streak=1, last_activity_date=date.today())
        db.add(streak)
    else:
        streak.update_streak(date.today())

    await db.commit()
    await db.refresh(session)

    # Get today's total
    today_total_result = await db.execute(
        select(func.sum(LearningSession.duration_minutes)).where(
            LearningSession.user_id == user_id,
            func.date(LearningSession.logged_at) == date.today(),
        )
    )
    today_total = today_total_result.scalar() or 0

    return TimeLogResponse(
        logged=True,
        session_id=session.id,
        chapter_id=time_log.chapter_id,
        duration_minutes=time_log.duration_minutes,
        activity_type=time_log.activity_type,
        logged_at=now,
        today_total_minutes=today_total,
        streak_maintained=True,
    )
