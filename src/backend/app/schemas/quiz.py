"""
Quiz Schemas
Schemas for quizzes and assessments
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class QuestionResponse(BaseModel):
    """Quiz question (without correct answer)."""

    question_id: str = Field(..., description="Question identifier")
    type: Literal["multiple_choice", "true_false", "fill_blank", "code_completion"] = (
        Field(..., description="Question type")
    )
    question_text: str = Field(..., description="Question text")
    options: Optional[List[str]] = Field(
        None, description="Options for multiple choice"
    )
    points: int = Field(default=1, description="Points for this question")

    class Config:
        json_schema_extra = {
            "example": {
                "question_id": "q1",
                "type": "multiple_choice",
                "question_text": "What is the primary difference between a chatbot and an AI agent?",
                "options": [
                    "Agents can use tools",
                    "Agents can browse the web",
                    "Agents have better language models",
                    "Agents are faster",
                ],
                "points": 1,
            }
        }


class QuizResponse(BaseModel):
    """Quiz details for starting."""

    quiz_id: str = Field(..., description="Quiz identifier")
    title: str = Field(..., description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")
    question_count: int = Field(..., description="Number of questions")
    passing_score: int = Field(..., description="Passing score percentage")
    time_limit_minutes: Optional[int] = Field(None, description="Time limit if any")
    max_attempts: Optional[int] = Field(None, description="Max attempts if limited")

    class Config:
        json_schema_extra = {
            "example": {
                "quiz_id": "quiz-mod-1-foundations",
                "title": "Foundations Quiz",
                "description": "Test your understanding of AI Agent fundamentals",
                "question_count": 15,
                "passing_score": 70,
                "time_limit_minutes": None,
                "max_attempts": None,
            }
        }


class QuizStartResponse(BaseModel):
    """Response when starting a quiz attempt."""

    attempt_id: str = Field(..., description="Attempt identifier")
    quiz_id: str = Field(..., description="Quiz identifier")
    attempt_number: int = Field(..., description="Which attempt this is")
    questions: List[QuestionResponse] = Field(..., description="Quiz questions")
    started_at: datetime = Field(..., description="Start timestamp")
    time_limit_minutes: Optional[int] = Field(None, description="Time limit")
    expires_at: Optional[datetime] = Field(
        None, description="Expiration time if time-limited"
    )


class QuizSubmitRequest(BaseModel):
    """Request to submit quiz answers."""

    answers: Dict[str, str] = Field(
        ...,
        description="Question answers mapping (question_id -> answer)",
        json_schema_extra={
            "example": {
                "q1": "0",
                "q2": "true",
                "q3": "async/await",
            }
        },
    )


class QuestionResult(BaseModel):
    """Result for a single question."""

    correct: bool = Field(..., description="Whether answer was correct")
    user_answer: str = Field(..., description="User's answer")
    correct_answer: str = Field(..., description="Correct answer")
    explanation: Optional[str] = Field(None, description="Explanation")
    points: int = Field(..., description="Points earned")


class QuizResultResponse(BaseModel):
    """
    Quiz submission result.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Score is arithmetic (correct/total * 100)
    - ✅ Grading is exact match (deterministic)
    - ❌ NO LLM involvement
    """

    attempt_id: str = Field(..., description="Attempt identifier")
    quiz_id: str = Field(..., description="Quiz identifier")
    score: int = Field(..., description="Score percentage")
    passed: bool = Field(..., description="Whether quiz was passed")
    correct_count: int = Field(..., description="Number correct")
    total_questions: int = Field(..., description="Total questions")
    time_spent_seconds: int = Field(..., description="Time spent")
    results: Dict[str, QuestionResult] = Field(
        ..., description="Per-question results"
    )
    submitted_at: datetime = Field(..., description="Submission timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "attempt-uuid-12345",
                "quiz_id": "quiz-mod-1-foundations",
                "score": 85,
                "passed": True,
                "correct_count": 13,
                "total_questions": 15,
                "time_spent_seconds": 720,
                "results": {
                    "q1": {
                        "correct": True,
                        "user_answer": "0",
                        "correct_answer": "0",
                        "explanation": "AI agents are distinguished by their ability to use tools.",
                        "points": 1,
                    }
                },
                "submitted_at": "2026-01-15T14:30:00Z",
            }
        }


class QuizAttemptResponse(BaseModel):
    """Quiz attempt summary (for history)."""

    attempt_id: str = Field(..., description="Attempt identifier")
    quiz_id: str = Field(..., description="Quiz identifier")
    attempt_number: int = Field(..., description="Attempt number")
    score: Optional[int] = Field(None, description="Score if submitted")
    passed: Optional[bool] = Field(None, description="Pass status if submitted")
    started_at: datetime = Field(..., description="Start timestamp")
    submitted_at: Optional[datetime] = Field(None, description="Submission timestamp")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent")


class QuizListItem(BaseModel):
    """Quiz summary for listing."""

    quiz_id: str = Field(..., description="Quiz identifier")
    title: str = Field(..., description="Quiz title")
    description: Optional[str] = Field(None, description="Quiz description")
    question_count: int = Field(..., description="Number of questions")
    passing_score: int = Field(..., description="Passing score percentage")
    type: Literal["chapter", "module", "practice"] = Field(
        "chapter", description="Quiz type"
    )
    module_id: Optional[str] = Field(None, description="Associated module ID")
    chapter_id: Optional[str] = Field(None, description="Associated chapter ID")
    accessible: bool = Field(True, description="Whether user can access this quiz")


class QuizListResponse(BaseModel):
    """Response for quiz listing."""

    quizzes: List[QuizListItem] = Field(..., description="List of quizzes")
    total_quizzes: int = Field(..., description="Total quiz count")
