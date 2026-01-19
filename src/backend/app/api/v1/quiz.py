"""
Quiz Assessment API
Quiz management and grading endpoints

CONSTITUTIONAL COMPLIANCE:
- ✅ Exact match grading (deterministic)
- ✅ Score calculation is arithmetic
- ❌ NO LLM-based grading
- ❌ NO AI question generation
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core import ActiveUser, DbSession, get_r2_client
from app.models.quiz import Quiz, Question, QuizAttempt, QuestionType
from app.models.content import Module
from app.schemas.quiz import (
    QuizResponse,
    QuestionResponse,
    QuizStartResponse,
    QuizSubmitRequest,
    QuizResultResponse,
    QuestionResult,
    QuizAttemptResponse,
    QuizListItem,
    QuizListResponse,
)

router = APIRouter()


@router.get("/quizzes", response_model=QuizListResponse)
async def list_quizzes(
    module_id: Optional[str] = Query(None, description="Filter by module ID"),
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    List available quizzes.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Simple database query (deterministic)
    - ✅ Access control based on subscription tier
    - ❌ NO LLM filtering or recommendations

    Args:
        module_id: Optional filter by module

    Returns:
        QuizListResponse with list of quizzes
    """
    # Build query
    query = select(Quiz).options(selectinload(Quiz.module))

    # Apply filters
    if module_id:
        if module_id.isdigit():
            query = query.join(Module).where(Module.order == int(module_id))
        else:
            query = query.join(Module).where(Module.module_id == module_id)

    # Execute query
    result = await db.execute(query.order_by(Quiz.created_at))
    quizzes = result.scalars().all()

    # Build response with access info
    quiz_items = []
    for quiz in quizzes:
        # Check if user can access this quiz
        accessible = True
        if quiz.module:
            accessible = quiz.module.is_accessible_by(user.tier)

        # Determine quiz type from quiz_id pattern
        quiz_type = "module"  # Default for module quizzes
        if "chapter" in quiz.quiz_id.lower() or "ch" in quiz.quiz_id.lower():
            quiz_type = "chapter"
        elif "practice" in quiz.quiz_id.lower():
            quiz_type = "practice"

        quiz_items.append(
            QuizListItem(
                quiz_id=quiz.quiz_id,
                title=quiz.title,
                description=quiz.description,
                question_count=quiz.question_count,
                passing_score=quiz.passing_score,
                type=quiz_type,
                module_id=quiz.module.module_id if quiz.module else None,
                chapter_id=None,  # Not tracked in current model
                accessible=accessible,
            )
        )

    return QuizListResponse(
        quizzes=quiz_items,
        total_quizzes=len(quiz_items),
    )


@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get quiz metadata (without questions).

    Args:
        quiz_id: Quiz identifier

    Returns:
        QuizResponse with quiz metadata
    """
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.module))
        .where(Quiz.quiz_id == quiz_id)
    )
    quiz = result.scalar_one_or_none()

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "quiz_not_found",
                "message": f"Quiz '{quiz_id}' does not exist",
                "quiz_id": quiz_id,
            },
        )

    # Check module access
    if quiz.module and not quiz.module.is_accessible_by(user.tier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "access_denied",
                "message": "Premium subscription required for this quiz",
                "required_tier": quiz.module.access_tier,
            },
        )

    return QuizResponse(
        quiz_id=quiz.quiz_id,
        title=quiz.title,
        description=quiz.description,
        question_count=quiz.question_count,
        passing_score=quiz.passing_score,
        time_limit_minutes=quiz.time_limit_minutes,
        max_attempts=quiz.max_attempts,
    )


@router.post("/quizzes/{quiz_id}/start", response_model=QuizStartResponse)
async def start_quiz(
    quiz_id: str,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Start a new quiz attempt.

    Creates a new attempt and returns questions.

    Args:
        quiz_id: Quiz identifier

    Returns:
        QuizStartResponse with attempt ID and questions
    """
    # Get quiz with questions
    result = await db.execute(
        select(Quiz)
        .options(selectinload(Quiz.questions), selectinload(Quiz.module))
        .where(Quiz.quiz_id == quiz_id)
    )
    quiz = result.scalar_one_or_none()

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "quiz_not_found", "quiz_id": quiz_id},
        )

    # Check module access
    if quiz.module and not quiz.module.is_accessible_by(user.tier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied", "required_tier": quiz.module.access_tier},
        )

    # Check max attempts
    if quiz.max_attempts:
        attempt_count_result = await db.execute(
            select(func.count(QuizAttempt.id))
            .where(QuizAttempt.user_id == user.id)
            .where(QuizAttempt.quiz_id == quiz.id)
        )
        attempt_count = attempt_count_result.scalar()

        if attempt_count >= quiz.max_attempts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "max_attempts_exceeded",
                    "message": f"Maximum {quiz.max_attempts} attempts allowed",
                    "max_attempts": quiz.max_attempts,
                    "current_attempts": attempt_count,
                },
            )

    # Create new attempt
    attempt_number = (
        await db.execute(
            select(func.count(QuizAttempt.id))
            .where(QuizAttempt.user_id == user.id)
            .where(QuizAttempt.quiz_id == quiz.id)
        )
    ).scalar() + 1

    attempt = QuizAttempt(
        user_id=user.id,
        quiz_id=quiz.id,
        attempt_number=attempt_number,
        started_at=datetime.utcnow(),
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)

    # Build question list (without correct answers)
    questions = [
        QuestionResponse(
            question_id=q.question_id,
            type=q.type.value,
            question_text=q.question_text,
            options=q.options,
            points=q.points,
        )
        for q in sorted(quiz.questions, key=lambda x: x.order)
    ]

    # Calculate expiration if time-limited
    expires_at = None
    if quiz.time_limit_minutes:
        from datetime import timedelta

        expires_at = attempt.started_at + timedelta(minutes=quiz.time_limit_minutes)

    return QuizStartResponse(
        attempt_id=attempt.id,
        quiz_id=quiz.quiz_id,
        attempt_number=attempt.attempt_number,
        questions=questions,
        started_at=attempt.started_at,
        time_limit_minutes=quiz.time_limit_minutes,
        expires_at=expires_at,
    )


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizResultResponse)
async def submit_quiz(
    quiz_id: str,
    submission: QuizSubmitRequest,
    attempt_id: str = Query(..., description="Attempt ID from start"),
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Submit quiz answers and get results.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Grading is exact match (deterministic)
    - ✅ Score is arithmetic (correct/total * 100)
    - ❌ NO LLM involvement in grading

    Args:
        quiz_id: Quiz identifier
        submission: Quiz answers
        attempt_id: Attempt ID from start_quiz

    Returns:
        QuizResultResponse with score and results
    """
    # Get the attempt
    result = await db.execute(
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.quiz).selectinload(Quiz.questions))
        .where(QuizAttempt.id == attempt_id)
        .where(QuizAttempt.user_id == user.id)
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "attempt_not_found",
                "message": "Quiz attempt not found or doesn't belong to you",
            },
        )

    if attempt.submitted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "already_submitted",
                "message": "This attempt has already been submitted",
                "submitted_at": attempt.submitted_at.isoformat(),
            },
        )

    # Check time limit
    if attempt.quiz.time_limit_minutes:
        from datetime import timedelta

        expires_at = attempt.started_at + timedelta(
            minutes=attempt.quiz.time_limit_minutes
        )
        if datetime.utcnow() > expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "time_expired",
                    "message": "Time limit for this quiz has expired",
                },
            )

    # Grade the quiz using the model's submit method
    grading_result = attempt.submit(submission.answers)

    await db.commit()

    # Build detailed results
    results = {}
    for q_id, result_data in grading_result["results"].items():
        results[q_id] = QuestionResult(
            correct=result_data["correct"],
            user_answer=result_data["user_answer"],
            correct_answer=result_data["correct_answer"],
            explanation=result_data.get("explanation"),
            points=result_data["points"],
        )

    return QuizResultResponse(
        attempt_id=attempt.id,
        quiz_id=attempt.quiz.quiz_id,
        score=grading_result["score"],
        passed=grading_result["passed"],
        correct_count=grading_result["correct_count"],
        total_questions=grading_result["total_questions"],
        time_spent_seconds=attempt.time_spent_seconds or 0,
        results=results,
        submitted_at=attempt.submitted_at,
    )


@router.get("/quizzes/{quiz_id}/attempts", response_model=List[QuizAttemptResponse])
async def get_quiz_attempts(
    quiz_id: str,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get user's attempt history for a quiz.

    Args:
        quiz_id: Quiz identifier

    Returns:
        List of user's attempts
    """
    # Get quiz
    quiz_result = await db.execute(select(Quiz).where(Quiz.quiz_id == quiz_id))
    quiz = quiz_result.scalar_one_or_none()

    if quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "quiz_not_found", "quiz_id": quiz_id},
        )

    # Get attempts
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user.id)
        .where(QuizAttempt.quiz_id == quiz.id)
        .order_by(QuizAttempt.started_at.desc())
    )
    attempts = result.scalars().all()

    return [
        QuizAttemptResponse(
            attempt_id=a.id,
            quiz_id=quiz_id,
            attempt_number=a.attempt_number,
            score=a.score,
            passed=a.passed,
            started_at=a.started_at,
            submitted_at=a.submitted_at,
            time_spent_seconds=a.time_spent_seconds,
        )
        for a in attempts
    ]


@router.get("/quizzes/{quiz_id}/attempts/{attempt_id}", response_model=QuizResultResponse)
async def get_quiz_result(
    quiz_id: str,
    attempt_id: str,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get detailed results for a specific attempt.

    Args:
        quiz_id: Quiz identifier
        attempt_id: Attempt identifier

    Returns:
        Detailed quiz results
    """
    result = await db.execute(
        select(QuizAttempt)
        .options(selectinload(QuizAttempt.quiz).selectinload(Quiz.questions))
        .where(QuizAttempt.id == attempt_id)
        .where(QuizAttempt.user_id == user.id)
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "attempt_not_found"},
        )

    if attempt.submitted_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "not_submitted",
                "message": "This attempt has not been submitted yet",
            },
        )

    # Build results from stored data
    results = {}
    if attempt.results:
        for q_id, result_data in attempt.results.items():
            results[q_id] = QuestionResult(
                correct=result_data["correct"],
                user_answer=result_data["user_answer"],
                correct_answer=result_data["correct_answer"],
                explanation=result_data.get("explanation"),
                points=result_data.get("points", 0),
            )

    return QuizResultResponse(
        attempt_id=attempt.id,
        quiz_id=attempt.quiz.quiz_id,
        score=attempt.score or 0,
        passed=attempt.passed,
        correct_count=attempt.correct_count,
        total_questions=attempt.total_questions,
        time_spent_seconds=attempt.time_spent_seconds or 0,
        results=results,
        submitted_at=attempt.submitted_at,
    )


@router.get("/modules/{module_id}/quiz", response_model=QuizResponse)
async def get_module_quiz(
    module_id: str,
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get quiz for a specific module.

    Args:
        module_id: Module identifier

    Returns:
        Quiz metadata for the module
    """
    # Find module
    query = select(Module).options(selectinload(Module.quiz))

    if module_id.isdigit():
        query = query.where(Module.order == int(module_id))
    else:
        query = query.where(Module.module_id == module_id)

    result = await db.execute(query)
    module = result.scalar_one_or_none()

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "module_not_found", "module_id": module_id},
        )

    if module.quiz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "quiz_not_found",
                "message": f"No quiz found for module '{module_id}'",
            },
        )

    # Check access
    if not module.is_accessible_by(user.tier):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "access_denied", "required_tier": module.access_tier},
        )

    return QuizResponse(
        quiz_id=module.quiz.quiz_id,
        title=module.quiz.title,
        description=module.quiz.description,
        question_count=module.quiz.question_count,
        passing_score=module.quiz.passing_score,
        time_limit_minutes=module.quiz.time_limit_minutes,
        max_attempts=module.quiz.max_attempts,
    )
