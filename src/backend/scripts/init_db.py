#!/usr/bin/env python3
"""
Database Initialization Script
Creates tables and seeds initial data for Course Companion

Run with: python -m scripts.init_db
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import Base, engine
from app.models.user import User, Subscription
from app.models.content import Module, Chapter, MediaAsset
from app.models.progress import ChapterProgress, LearningSession, UserStreak
from app.models.quiz import Question, QuizAttempt, Quiz
from app.models.achievement import Achievement, UserAchievement


async def init_db():
    """Initialize database tables."""
    print("Initializing database...")

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created successfully!")
    print("\nTables created:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


async def main():
    """Main entry point."""
    try:
        await init_db()
        print("\nDatabase initialization complete!")
    except Exception as e:
        print(f"\nError initializing database: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
