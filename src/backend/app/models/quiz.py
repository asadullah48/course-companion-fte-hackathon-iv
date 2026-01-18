"""
Quiz and Assessment Models
Quizzes, questions, and user attempts
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.content import Module
    from app.models.user import User


class QuestionType(str, enum.Enum):
    """Quiz question types."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    CODE_COMPLETION = "code_completion"


class Quiz(Base):
    """
    Quiz Definition model.

    Represents a quiz for a module.
    Questions are stored as JSON for flexibility.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Exact match grading (deterministic)
    - ❌ NO LLM-based question generation
    - ❌ NO AI grading for open-ended answers
    """

    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    quiz_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )  # e.g., "quiz-mod-1-foundations"

    # Module relationship
    module_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Quiz metadata
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Quiz settings
    passing_score: Mapped[int] = mapped_column(Integer, default=70)  # percentage
    time_limit_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # null = no limit
    max_attempts: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )  # null = unlimited

    # Question count (derived but cached for performance)
    question_count: Mapped[int] = mapped_column(Integer, default=0)

    # R2 storage for quiz JSON (questions stored in R2)
    r2_key: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # e.g., "quizzes/quiz-mod-1-foundations.json"

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    module: Mapped[Optional["Module"]] = relationship("Module", back_populates="quiz")
    questions: Mapped[List["Question"]] = relationship(
        "Question", back_populates="quiz", order_by="Question.order"
    )
    attempts: Mapped[List["QuizAttempt"]] = relationship(
        "QuizAttempt", back_populates="quiz"
    )

    def __repr__(self) -> str:
        return f"<Quiz {self.quiz_id} questions={self.question_count}>"


class Question(Base):
    """
    Quiz Question model.

    Individual questions for quizzes.
    All grading is exact match (deterministic).

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Exact match grading
    - ✅ Normalized string comparison for fill_blank
    - ❌ NO LLM-based grading
    """

    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    question_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # e.g., "q1", "q2"

    # Quiz relationship
    quiz_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Question content
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Options (for multiple_choice - stored as JSON array)
    options: Mapped[Optional[List[str]]] = mapped_column(ARRAY(Text), nullable=True)

    # Answer (stored as index for MC, string for fill_blank, bool for T/F)
    correct_answer: Mapped[str] = mapped_column(
        String(500), nullable=False
    )  # "0" for MC index, "true"/"false" for T/F, text for fill_blank

    # Explanation shown after answering
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Reference to chapter for learning context
    chapter_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Ordering
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Points for this question
    points: Mapped[int] = mapped_column(Integer, default=1)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Relationships
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")

    def check_answer(self, user_answer: str) -> bool:
        """
        Check if user's answer is correct.

        CONSTITUTIONAL COMPLIANCE:
        - ✅ Exact match for MC (index comparison)
        - ✅ Case-insensitive normalized match for fill_blank
        - ✅ Boolean comparison for T/F
        - ❌ NO LLM involvement
        """
        user_answer = str(user_answer).strip()

        if self.type == QuestionType.MULTIPLE_CHOICE:
            # Compare index (e.g., "0", "1", "2", "3")
            return user_answer == self.correct_answer

        elif self.type == QuestionType.TRUE_FALSE:
            # Normalize boolean strings
            user_bool = user_answer.lower() in ("true", "yes", "1", "t")
            correct_bool = self.correct_answer.lower() in ("true", "yes", "1", "t")
            return user_bool == correct_bool

        elif self.type == QuestionType.FILL_BLANK:
            # Case-insensitive, whitespace-normalized comparison
            return self._normalize_text(user_answer) == self._normalize_text(
                self.correct_answer
            )

        elif self.type == QuestionType.CODE_COMPLETION:
            # Exact match for code (whitespace-normalized)
            return self._normalize_code(user_answer) == self._normalize_code(
                self.correct_answer
            )

        return False

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text for comparison."""
        return " ".join(text.lower().split())

    @staticmethod
    def _normalize_code(code: str) -> str:
        """Normalize code for comparison (remove extra whitespace)."""
        lines = [line.strip() for line in code.strip().split("\n") if line.strip()]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"<Question {self.question_id} type={self.type.value}>"


class QuizAttempt(Base):
    """
    Quiz Attempt model.

    Tracks user's attempts at quizzes.
    Stores answers and calculates score deterministically.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Score calculation is arithmetic (correct/total * 100)
    - ❌ NO LLM involvement in grading
    """

    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # User and quiz relationship
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quiz_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Attempt tracking
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)

    # Answers stored as JSON: {"q1": "0", "q2": "true", "q3": "async/await"}
    answers: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Grading results (populated on submission)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # percentage
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Detailed results: {"q1": {"correct": true, "user_answer": "0"}, ...}
    results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    time_spent_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")

    def submit(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Submit answers and calculate score.

        CONSTITUTIONAL COMPLIANCE:
        - ✅ Arithmetic score calculation
        - ✅ Exact match grading per question
        - ❌ NO LLM involvement
        """
        self.answers = answers
        self.submitted_at = datetime.utcnow()
        self.time_spent_seconds = int(
            (self.submitted_at - self.started_at).total_seconds()
        )

        # Grade each question
        results = {}
        correct_count = 0
        total_points = 0
        earned_points = 0

        for question in self.quiz.questions:
            q_id = question.question_id
            user_answer = answers.get(q_id, "")
            is_correct = question.check_answer(user_answer)

            results[q_id] = {
                "correct": is_correct,
                "user_answer": user_answer,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "points": question.points if is_correct else 0,
            }

            total_points += question.points
            if is_correct:
                correct_count += 1
                earned_points += question.points

        self.results = results
        self.correct_count = correct_count
        self.total_questions = len(self.quiz.questions)

        # Calculate score as percentage (deterministic arithmetic)
        if total_points > 0:
            self.score = round((earned_points / total_points) * 100)
        else:
            self.score = 0

        # Check if passed
        self.passed = self.score >= self.quiz.passing_score

        return {
            "score": self.score,
            "passed": self.passed,
            "correct_count": self.correct_count,
            "total_questions": self.total_questions,
            "results": self.results,
        }

    def __repr__(self) -> str:
        return f"<QuizAttempt user={self.user_id} quiz={self.quiz_id} score={self.score}>"
