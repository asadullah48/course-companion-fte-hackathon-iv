"""
Pytest Configuration and Fixtures
Course Companion Backend Tests

NOTE: These tests use SQLite for simplicity. The actual app uses PostgreSQL
with UUID types. For SQLite compatibility, we register a UUID type compiler.
"""

import asyncio
from datetime import datetime, date, timedelta
from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.dialects import sqlite

from app.config import get_settings
from app.database import Base, get_db
from app.main import app
from app.models.user import User, Subscription, SubscriptionTier
from app.models.content import Module, Chapter
from app.models.progress import ChapterProgress, UserStreak, ProgressStatus
from app.models.achievement import Achievement, AchievementCategory
from app.core.auth import create_access_token, get_password_hash


# Register UUID type for SQLite (converts to VARCHAR)
def visit_uuid(self, type_, **kw):
    return "VARCHAR(36)"

sqlite.base.SQLiteTypeCompiler.visit_UUID = visit_uuid


# Use SQLite for testing (in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for session scope."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create fresh database for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with overridden database."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        display_name="Test User",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user_token(test_user: User) -> str:
    """Create access token for test user."""
    return create_access_token(data={"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def premium_user(db_session: AsyncSession) -> User:
    """Create a premium subscription user."""
    user = User(
        id=uuid4(),
        email="premium@example.com",
        hashed_password=get_password_hash("premiumpass123"),
        display_name="Premium User",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.flush()

    subscription = Subscription(
        id=uuid4(),
        user_id=user.id,
        tier=SubscriptionTier.PREMIUM,
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30),
        created_at=datetime.utcnow(),
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_module(db_session: AsyncSession) -> Module:
    """Create a test module."""
    module = Module(
        id=uuid4(),
        module_id="module-1",
        title="Test Module 1",
        description="Test module description",
        order=1,
        difficulty="beginner",
        estimated_duration_minutes=60,
        access_tier="free",
        learning_objectives=["Learn basics", "Understand concepts"],
        prerequisites=[],
        created_at=datetime.utcnow(),
    )
    db_session.add(module)
    await db_session.commit()
    await db_session.refresh(module)
    return module


@pytest_asyncio.fixture
async def test_chapters(db_session: AsyncSession, test_module: Module) -> list[Chapter]:
    """Create test chapters."""
    chapters = []
    for i in range(1, 4):
        chapter = Chapter(
            id=uuid4(),
            chapter_id=f"ch{i}-test-chapter",
            slug=f"test-chapter-{i}",
            title=f"Test Chapter {i}",
            module_id=test_module.id,
            order=i,
            difficulty="beginner",
            estimated_read_time=15,
            word_count=1500,
            r2_key=f"chapters/ch{i}-test-chapter.md",
            tags=["test", "chapter"],
            learning_objectives=["Learn something"],
            prerequisites=[],
            created_at=datetime.utcnow(),
        )
        chapters.append(chapter)
        db_session.add(chapter)

    await db_session.commit()
    for chapter in chapters:
        await db_session.refresh(chapter)
    return chapters


@pytest_asyncio.fixture
async def user_streak(db_session: AsyncSession, test_user: User) -> UserStreak:
    """Create user streak record."""
    streak = UserStreak(
        id=uuid4(),
        user_id=test_user.id,
        current_streak=5,
        longest_streak=10,
        last_activity_date=date.today(),
        freezes_used=0,
        created_at=datetime.utcnow(),
    )
    db_session.add(streak)
    await db_session.commit()
    await db_session.refresh(streak)
    return streak


@pytest_asyncio.fixture
async def chapter_progress(
    db_session: AsyncSession,
    test_user: User,
    test_chapters: list[Chapter]
) -> list[ChapterProgress]:
    """Create chapter progress records."""
    progress_list = []
    for i, chapter in enumerate(test_chapters):
        status = ProgressStatus.COMPLETED if i == 0 else ProgressStatus.NOT_STARTED
        progress = ChapterProgress(
            id=uuid4(),
            user_id=test_user.id,
            chapter_id=chapter.id,
            status=status,
            time_spent_minutes=30 if i == 0 else 0,
            started_at=datetime.utcnow() if i == 0 else None,
            completed_at=datetime.utcnow() if i == 0 else None,
            created_at=datetime.utcnow(),
        )
        progress_list.append(progress)
        db_session.add(progress)

    await db_session.commit()
    for progress in progress_list:
        await db_session.refresh(progress)
    return progress_list
