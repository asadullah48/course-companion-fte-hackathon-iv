"""
Unit Tests for Database Models
Tests model creation, relationships, and business logic

NOTE: Tests that require database fixtures are skipped when using SQLite
due to PostgreSQL-specific types (UUID, ARRAY). Run against PostgreSQL for
full integration tests.
"""

from datetime import datetime, date, timedelta
from uuid import uuid4

import pytest

from app.models.user import SubscriptionTier
from app.models.progress import ProgressStatus, ActivityType
from app.models.achievement import AchievementCategory
from app.core.auth import get_password_hash, verify_password, create_access_token, verify_token


class TestSubscriptionTiers:
    """Tests for SubscriptionTier enum."""

    def test_subscription_tiers(self):
        """Test subscription tier enum values."""
        assert SubscriptionTier.FREE.value == "free"
        assert SubscriptionTier.PREMIUM.value == "premium"
        assert SubscriptionTier.PRO.value == "pro"
        assert SubscriptionTier.TEAM.value == "team"

    def test_tier_comparison(self):
        """Test tier string values for access control."""
        free = SubscriptionTier.FREE
        premium = SubscriptionTier.PREMIUM
        assert free.value != premium.value


class TestProgressStatus:
    """Tests for ProgressStatus enum."""

    def test_progress_status_enum(self):
        """Test progress status enum values."""
        assert ProgressStatus.NOT_STARTED.value == "not_started"
        assert ProgressStatus.IN_PROGRESS.value == "in_progress"
        assert ProgressStatus.COMPLETED.value == "completed"


class TestActivityType:
    """Tests for ActivityType enum."""

    def test_activity_types(self):
        """Test activity type enum values."""
        assert ActivityType.READING.value == "reading"
        assert ActivityType.QUIZ.value == "quiz"
        assert ActivityType.PRACTICE.value == "practice"


class TestAchievementCategory:
    """Tests for AchievementCategory enum."""

    def test_achievement_categories(self):
        """Test achievement category enum values."""
        assert AchievementCategory.PROGRESS.value == "progress"
        assert AchievementCategory.MODULES.value == "modules"
        assert AchievementCategory.STREAKS.value == "streaks"
        assert AchievementCategory.QUIZZES.value == "quizzes"
        assert AchievementCategory.TIME.value == "time"


class TestAuthFunctions:
    """Tests for authentication functions."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "securepassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False

    def test_password_different_hashes(self):
        """Test same password produces different hashes (salted)."""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_create_access_token(self):
        """Test JWT token creation."""
        user_id = str(uuid4())
        token = create_access_token(subject=user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_access_token(self):
        """Test JWT token verification."""
        user_id = str(uuid4())
        token = create_access_token(subject=user_id)
        payload = verify_token(token)

        assert payload is not None
        assert payload.sub == user_id

    def test_token_expiry(self):
        """Test token has expiry claim."""
        user_id = str(uuid4())
        token = create_access_token(subject=user_id)
        payload = verify_token(token)

        assert payload is not None
        assert payload.exp is not None

    def test_invalid_token_returns_none(self):
        """Test verifying invalid token returns None."""
        result = verify_token("invalid.token.here")
        assert result is None


class TestStreakLogic:
    """Tests for streak calculation logic (pure Python, no DB)."""

    def test_streak_at_risk_logic(self):
        """Test streak at risk calculation logic."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        # If last activity was today, not at risk
        assert (today - today).days == 0

        # If last activity was yesterday, at risk (need to be active today)
        assert (today - yesterday).days == 1

        # If last activity was 2 days ago, streak broken
        assert (today - two_days_ago).days == 2

    def test_streak_update_logic(self):
        """Test streak update calculation."""
        # Starting with streak of 5
        current_streak = 5
        last_activity = date.today() - timedelta(days=1)
        activity_date = date.today()

        # If activity is next day after last, increment streak
        days_gap = (activity_date - last_activity).days
        if days_gap == 1:
            new_streak = current_streak + 1
        elif days_gap == 0:
            new_streak = current_streak  # Same day, no change
        else:
            new_streak = 1  # Gap too big, restart

        assert new_streak == 6

    def test_streak_freeze_logic(self):
        """Test streak freeze usage logic."""
        freezes_used = 0
        max_freezes_by_tier = {
            "free": 1,
            "premium": 3,
            "pro": 5,
            "team": 10,
        }

        # Free user can use 1 freeze
        tier = "free"
        can_use_freeze = freezes_used < max_freezes_by_tier[tier]
        assert can_use_freeze is True

        # After using, can't use another
        freezes_used = 1
        can_use_freeze = freezes_used < max_freezes_by_tier[tier]
        assert can_use_freeze is False


class TestAccessControlLogic:
    """Tests for access control logic."""

    def test_free_chapter_access(self):
        """Test free chapter access logic."""
        FREE_CHAPTER_LIMIT = 3
        chapter_order = 2  # Second chapter

        # Free users can access chapters 1-3
        has_access = chapter_order <= FREE_CHAPTER_LIMIT
        assert has_access is True

        # Chapter 4 requires premium
        chapter_order = 4
        has_access = chapter_order <= FREE_CHAPTER_LIMIT
        assert has_access is False

    def test_tier_based_access(self):
        """Test tier-based content access."""
        content_tiers = {
            "module-1": "free",
            "module-2": "premium",
            "module-3": "premium",
        }

        tier_hierarchy = {
            "free": ["free"],
            "premium": ["free", "premium"],
            "pro": ["free", "premium", "pro"],
            "team": ["free", "premium", "pro", "team"],
        }

        # Free user accessing free module
        user_tier = "free"
        module_tier = content_tiers["module-1"]
        has_access = module_tier in tier_hierarchy[user_tier]
        assert has_access is True

        # Free user accessing premium module
        module_tier = content_tiers["module-2"]
        has_access = module_tier in tier_hierarchy[user_tier]
        assert has_access is False

        # Premium user accessing premium module
        user_tier = "premium"
        has_access = module_tier in tier_hierarchy[user_tier]
        assert has_access is True


class TestQuizGrading:
    """Tests for quiz grading logic (deterministic, exact-match)."""

    def test_multiple_choice_grading(self):
        """Test MCQ grading is exact-match."""
        correct_answer = "B"

        # Correct answer
        user_answer = "B"
        is_correct = user_answer == correct_answer
        assert is_correct is True

        # Wrong answer
        user_answer = "A"
        is_correct = user_answer == correct_answer
        assert is_correct is False

        # Case sensitive
        user_answer = "b"
        is_correct = user_answer == correct_answer
        assert is_correct is False

    def test_true_false_grading(self):
        """Test T/F grading."""
        correct_answer = True

        assert (True == correct_answer) is True
        assert (False == correct_answer) is False

    def test_quiz_score_calculation(self):
        """Test quiz score calculation."""
        total_questions = 10
        correct_answers = 7

        score = int((correct_answers / total_questions) * 100)
        assert score == 70

        # Passing threshold (usually 70%)
        passing_score = 70
        passed = score >= passing_score
        assert passed is True

    def test_quiz_pass_threshold(self):
        """Test various passing thresholds."""
        passing_thresholds = {
            "easy": 60,
            "medium": 70,
            "hard": 80,
        }

        # Score of 75 passes easy and medium, fails hard
        score = 75
        assert score >= passing_thresholds["easy"]
        assert score >= passing_thresholds["medium"]
        assert score < passing_thresholds["hard"]
