"""
Database Seed Script
Populates database with initial course content, quizzes, and achievements

Run with: python -m app.scripts.seed_data
"""

import asyncio
from datetime import datetime
from uuid import uuid4

from app.database import async_session_maker, init_db
from app.models.content import Module, Chapter
from app.models.quiz import Quiz, Question, QuestionType
from app.models.achievement import Achievement, AchievementCategory


# Module data
MODULES = [
    {
        "module_id": "mod-1-foundations",
        "title": "Foundations of AI Agents",
        "description": "Learn the core concepts of AI Agents, the Agent Factory Architecture, and Model Context Protocol",
        "order": 1,
        "difficulty": "beginner",
        "estimated_duration_minutes": 70,
        "access_tier": "free",
        "learning_objectives": [
            "Understand what AI agents are and their capabilities",
            "Learn the 8-layer Agent Factory architecture",
            "Master MCP fundamentals: servers, tools, resources",
        ],
        "prerequisites": [],
    },
    {
        "module_id": "mod-2-skills",
        "title": "Skills Development",
        "description": "Master the Claude Agent SDK, create effective SKILL.md files, and integrate external tools",
        "order": 2,
        "difficulty": "intermediate",
        "estimated_duration_minutes": 90,
        "access_tier": "premium",
        "learning_objectives": [
            "Use the Claude Agent SDK effectively",
            "Create procedural knowledge with SKILL.md",
            "Integrate and test external tools",
        ],
        "prerequisites": ["mod-1-foundations"],
    },
    {
        "module_id": "mod-3-workflows",
        "title": "Agentic Workflows",
        "description": "Design workflow patterns, build multi-agent systems, and deploy to production",
        "order": 3,
        "difficulty": "advanced",
        "estimated_duration_minutes": 90,
        "access_tier": "premium",
        "learning_objectives": [
            "Design effective agentic workflow patterns",
            "Build and orchestrate multi-agent systems",
            "Deploy agents to production with best practices",
        ],
        "prerequisites": ["mod-2-skills"],
    },
]

# Chapter data (references module by order)
CHAPTERS = [
    # Module 1: Foundations
    {
        "chapter_id": "ch1-intro-to-agents",
        "title": "Introduction to AI Agents",
        "slug": "intro-to-agents",
        "module_order": 1,
        "order": 1,
        "difficulty": "beginner",
        "estimated_read_time": 15,
        "word_count": 1500,
        "r2_key": "chapters/ch1-intro-to-agents.md",
        "tags": ["fundamentals", "intro", "agents"],
        "learning_objectives": [
            "Define what an AI agent is",
            "Explain the difference between agents and chatbots",
            "Identify key components of an AI agent",
        ],
        "prerequisites": [],
        "access_tier": "free",
    },
    {
        "chapter_id": "ch2-agent-factory-architecture",
        "title": "Agent Factory Architecture",
        "slug": "agent-factory-architecture",
        "module_order": 1,
        "order": 2,
        "difficulty": "beginner",
        "estimated_read_time": 25,
        "word_count": 2500,
        "r2_key": "chapters/ch2-agent-factory-architecture.md",
        "tags": ["architecture", "design", "layers"],
        "learning_objectives": [
            "Understand the 8-layer architecture",
            "Identify the purpose of each layer",
            "Design agents using separation of concerns",
        ],
        "prerequisites": ["ch1-intro-to-agents"],
        "access_tier": "free",
    },
    {
        "chapter_id": "ch3-mcp-fundamentals",
        "title": "Model Context Protocol (MCP) Fundamentals",
        "slug": "mcp-fundamentals",
        "module_order": 1,
        "order": 3,
        "difficulty": "beginner",
        "estimated_read_time": 30,
        "word_count": 3000,
        "r2_key": "chapters/ch3-mcp-fundamentals.md",
        "tags": ["mcp", "protocol", "tools"],
        "learning_objectives": [
            "Explain what MCP is and why it matters",
            "Set up an MCP server",
            "Connect agents to MCP tools",
        ],
        "prerequisites": ["ch2-agent-factory-architecture"],
        "access_tier": "free",
    },
    # Module 2: Skills Development
    {
        "chapter_id": "ch4-claude-agent-sdk",
        "title": "Claude Agent SDK Deep Dive",
        "slug": "claude-agent-sdk",
        "module_order": 2,
        "order": 4,
        "difficulty": "intermediate",
        "estimated_read_time": 30,
        "word_count": 3500,
        "r2_key": "chapters/ch4-claude-agent-sdk.md",
        "tags": ["sdk", "claude", "implementation"],
        "learning_objectives": [
            "Install and configure Claude Agent SDK",
            "Create your first agent",
            "Handle tool calls and responses",
        ],
        "prerequisites": ["ch3-mcp-fundamentals"],
        "access_tier": "premium",
    },
    {
        "chapter_id": "ch5-skill-md-structure",
        "title": "SKILL.md Structure & Procedural Knowledge",
        "slug": "skill-md-structure",
        "module_order": 2,
        "order": 5,
        "difficulty": "intermediate",
        "estimated_read_time": 35,
        "word_count": 4000,
        "r2_key": "chapters/ch5-skill-md-structure.md",
        "tags": ["skills", "procedural", "templates"],
        "learning_objectives": [
            "Create effective SKILL.md files",
            "Structure procedural knowledge",
            "Design skill triggers and responses",
        ],
        "prerequisites": ["ch4-claude-agent-sdk"],
        "access_tier": "premium",
    },
    {
        "chapter_id": "ch6-tool-integration",
        "title": "Tool Integration & External APIs",
        "slug": "tool-integration",
        "module_order": 2,
        "order": 6,
        "difficulty": "intermediate",
        "estimated_read_time": 25,
        "word_count": 2800,
        "r2_key": "chapters/ch6-tool-integration.md",
        "tags": ["tools", "apis", "integration"],
        "learning_objectives": [
            "Design effective tool interfaces",
            "Handle errors gracefully",
            "Test tool integrations",
        ],
        "prerequisites": ["ch5-skill-md-structure"],
        "access_tier": "premium",
    },
    # Module 3: Agentic Workflows
    {
        "chapter_id": "ch7-workflow-patterns",
        "title": "Agentic Workflow Patterns",
        "slug": "workflow-patterns",
        "module_order": 3,
        "order": 7,
        "difficulty": "advanced",
        "estimated_read_time": 30,
        "word_count": 3200,
        "r2_key": "chapters/ch7-workflow-patterns.md",
        "tags": ["workflows", "patterns", "orchestration"],
        "learning_objectives": [
            "Design sequential and parallel workflows",
            "Handle conditional branching",
            "Implement error recovery",
        ],
        "prerequisites": ["ch6-tool-integration"],
        "access_tier": "premium",
    },
    {
        "chapter_id": "ch8-multi-agent-systems",
        "title": "Multi-Agent Orchestration",
        "slug": "multi-agent-systems",
        "module_order": 3,
        "order": 8,
        "difficulty": "advanced",
        "estimated_read_time": 35,
        "word_count": 4000,
        "r2_key": "chapters/ch8-multi-agent-systems.md",
        "tags": ["multi-agent", "orchestration", "coordination"],
        "learning_objectives": [
            "Design multi-agent systems",
            "Coordinate agent communication",
            "Handle conflicts and priorities",
        ],
        "prerequisites": ["ch7-workflow-patterns"],
        "access_tier": "premium",
    },
    {
        "chapter_id": "ch9-production-deployment",
        "title": "Production Deployment & Best Practices",
        "slug": "production-deployment",
        "module_order": 3,
        "order": 9,
        "difficulty": "advanced",
        "estimated_read_time": 25,
        "word_count": 3000,
        "r2_key": "chapters/ch9-production-deployment.md",
        "tags": ["deployment", "production", "devops"],
        "learning_objectives": [
            "Deploy agents to production",
            "Monitor and observe agents",
            "Scale agent systems",
        ],
        "prerequisites": ["ch8-multi-agent-systems"],
        "access_tier": "premium",
    },
]

# Quiz data
QUIZZES = [
    {
        "quiz_id": "quiz-mod-1-foundations",
        "module_order": 1,
        "title": "Foundations Quiz",
        "description": "Test your understanding of AI Agent fundamentals",
        "passing_score": 70,
        "time_limit_minutes": None,
        "max_attempts": None,
        "questions": [
            {
                "question_id": "q1",
                "type": QuestionType.MULTIPLE_CHOICE,
                "question_text": "What is the primary difference between a chatbot and an AI agent?",
                "options": [
                    "Agents can use tools",
                    "Agents can browse the web",
                    "Agents have better language models",
                    "Agents are faster",
                ],
                "correct_answer": "0",
                "explanation": "AI agents are distinguished by their ability to use tools to take actions in the world, not just generate text responses.",
                "chapter_reference": "ch1-intro-to-agents",
                "order": 1,
                "points": 1,
            },
            {
                "question_id": "q2",
                "type": QuestionType.MULTIPLE_CHOICE,
                "question_text": "How many layers are in the Agent Factory architecture?",
                "options": ["4", "6", "8", "10"],
                "correct_answer": "2",
                "explanation": "The Agent Factory architecture has 8 layers: Core Intelligence, Skill System, Tool Integration, Memory & Context, Orchestration, Deployment, Monitoring, and User Interface.",
                "chapter_reference": "ch2-agent-factory-architecture",
                "order": 2,
                "points": 1,
            },
            {
                "question_id": "q3",
                "type": QuestionType.TRUE_FALSE,
                "question_text": "MCP (Model Context Protocol) allows agents to connect to external tools and services.",
                "options": None,
                "correct_answer": "true",
                "explanation": "MCP is a standardized protocol that enables AI agents to connect to databases, APIs, file systems, and other external services.",
                "chapter_reference": "ch3-mcp-fundamentals",
                "order": 3,
                "points": 1,
            },
            {
                "question_id": "q4",
                "type": QuestionType.MULTIPLE_CHOICE,
                "question_text": "Which layer of the Agent Factory is responsible for persistent data storage?",
                "options": [
                    "Core Intelligence",
                    "Memory & Context",
                    "Deployment",
                    "Monitoring",
                ],
                "correct_answer": "1",
                "explanation": "The Memory & Context layer (Layer 4) handles persistent data storage, conversation history, and context management.",
                "chapter_reference": "ch2-agent-factory-architecture",
                "order": 4,
                "points": 1,
            },
            {
                "question_id": "q5",
                "type": QuestionType.FILL_BLANK,
                "question_text": "An MCP server exposes tools and _____.",
                "options": None,
                "correct_answer": "resources",
                "explanation": "MCP servers expose tools (for actions) and resources (for read-only data access).",
                "chapter_reference": "ch3-mcp-fundamentals",
                "order": 5,
                "points": 1,
            },
        ],
    },
]

# Achievement data
ACHIEVEMENTS = [
    {
        "achievement_id": "first-chapter",
        "name": "First Steps",
        "description": "Complete your first chapter",
        "icon": "rocket",
        "points": 50,
        "category": AchievementCategory.PROGRESS,
        "sort_order": 1,
        "requirement_value": 1,
        "requirement_type": "chapters_completed",
    },
    {
        "achievement_id": "halfway-there",
        "name": "Halfway There",
        "description": "Complete 50% of the course",
        "icon": "flag",
        "points": 75,
        "category": AchievementCategory.PROGRESS,
        "sort_order": 2,
        "requirement_value": 50,
        "requirement_type": "completion_percentage",
    },
    {
        "achievement_id": "course-complete",
        "name": "Agent Expert",
        "description": "Complete the entire course",
        "icon": "medal",
        "points": 200,
        "category": AchievementCategory.PROGRESS,
        "sort_order": 3,
        "requirement_value": 100,
        "requirement_type": "completion_percentage",
    },
    {
        "achievement_id": "module-1-complete",
        "name": "Foundation Master",
        "description": "Complete all chapters in Module 1",
        "icon": "trophy",
        "points": 100,
        "category": AchievementCategory.MODULES,
        "sort_order": 10,
        "requirement_value": 1,
        "requirement_type": "module_completed",
    },
    {
        "achievement_id": "module-2-complete",
        "name": "Skill Builder",
        "description": "Complete all chapters in Module 2",
        "icon": "tools",
        "points": 100,
        "category": AchievementCategory.MODULES,
        "sort_order": 11,
        "requirement_value": 2,
        "requirement_type": "module_completed",
    },
    {
        "achievement_id": "module-3-complete",
        "name": "Workflow Wizard",
        "description": "Complete all chapters in Module 3",
        "icon": "magic",
        "points": 100,
        "category": AchievementCategory.MODULES,
        "sort_order": 12,
        "requirement_value": 3,
        "requirement_type": "module_completed",
    },
    {
        "achievement_id": "streak-3",
        "name": "Hat Trick",
        "description": "Maintain a 3-day learning streak",
        "icon": "fire",
        "points": 25,
        "category": AchievementCategory.STREAKS,
        "sort_order": 20,
        "requirement_value": 3,
        "requirement_type": "streak_days",
    },
    {
        "achievement_id": "streak-5",
        "name": "High Five",
        "description": "Maintain a 5-day learning streak",
        "icon": "fire",
        "points": 50,
        "category": AchievementCategory.STREAKS,
        "sort_order": 21,
        "requirement_value": 5,
        "requirement_type": "streak_days",
    },
    {
        "achievement_id": "streak-7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day learning streak",
        "icon": "fire",
        "points": 75,
        "category": AchievementCategory.STREAKS,
        "sort_order": 22,
        "requirement_value": 7,
        "requirement_type": "streak_days",
    },
    {
        "achievement_id": "streak-30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day learning streak",
        "icon": "fire",
        "points": 150,
        "category": AchievementCategory.STREAKS,
        "sort_order": 23,
        "requirement_value": 30,
        "requirement_type": "streak_days",
    },
    {
        "achievement_id": "quiz-perfect",
        "name": "Perfect Score",
        "description": "Score 100% on any quiz",
        "icon": "star",
        "points": 50,
        "category": AchievementCategory.QUIZZES,
        "sort_order": 30,
        "requirement_value": 100,
        "requirement_type": "quiz_score",
    },
    {
        "achievement_id": "time-1-hour",
        "name": "Dedicated Learner",
        "description": "Spend 1 hour learning",
        "icon": "clock",
        "points": 25,
        "category": AchievementCategory.TIME,
        "sort_order": 40,
        "requirement_value": 60,
        "requirement_type": "total_time_minutes",
    },
    {
        "achievement_id": "time-5-hours",
        "name": "Committed Student",
        "description": "Spend 5 hours learning",
        "icon": "clock",
        "points": 75,
        "category": AchievementCategory.TIME,
        "sort_order": 41,
        "requirement_value": 300,
        "requirement_type": "total_time_minutes",
    },
    {
        "achievement_id": "time-10-hours",
        "name": "Agent Scholar",
        "description": "Spend 10 hours learning",
        "icon": "clock",
        "points": 100,
        "category": AchievementCategory.TIME,
        "sort_order": 42,
        "requirement_value": 600,
        "requirement_type": "total_time_minutes",
    },
]


async def seed_database():
    """Seed database with initial data."""
    print("Initializing database...")
    await init_db()

    async with async_session_maker() as db:
        # Check if data already exists
        from sqlalchemy import select

        existing = await db.execute(select(Module).limit(1))
        if existing.scalar_one_or_none():
            print("Database already seeded. Skipping...")
            return

        print("Seeding modules...")
        module_map = {}
        for module_data in MODULES:
            module = Module(
                id=str(uuid4()),
                module_id=module_data["module_id"],
                title=module_data["title"],
                description=module_data["description"],
                order=module_data["order"],
                difficulty=module_data["difficulty"],
                estimated_duration_minutes=module_data["estimated_duration_minutes"],
                access_tier=module_data["access_tier"],
                learning_objectives=module_data["learning_objectives"],
                prerequisites=module_data["prerequisites"],
            )
            db.add(module)
            module_map[module_data["order"]] = module

        await db.flush()

        print("Seeding chapters...")
        for chapter_data in CHAPTERS:
            module = module_map[chapter_data["module_order"]]
            chapter = Chapter(
                id=str(uuid4()),
                chapter_id=chapter_data["chapter_id"],
                module_id=module.id,
                title=chapter_data["title"],
                slug=chapter_data["slug"],
                order=chapter_data["order"],
                difficulty=chapter_data["difficulty"],
                estimated_read_time=chapter_data["estimated_read_time"],
                word_count=chapter_data["word_count"],
                r2_key=chapter_data["r2_key"],
                tags=chapter_data["tags"],
                learning_objectives=chapter_data["learning_objectives"],
                prerequisites=chapter_data["prerequisites"],
                access_tier=chapter_data.get("access_tier"),
            )
            db.add(chapter)

        await db.flush()

        print("Seeding quizzes...")
        for quiz_data in QUIZZES:
            module = module_map[quiz_data["module_order"]]
            quiz = Quiz(
                id=str(uuid4()),
                quiz_id=quiz_data["quiz_id"],
                module_id=module.id,
                title=quiz_data["title"],
                description=quiz_data["description"],
                passing_score=quiz_data["passing_score"],
                time_limit_minutes=quiz_data["time_limit_minutes"],
                max_attempts=quiz_data["max_attempts"],
                question_count=len(quiz_data["questions"]),
            )
            db.add(quiz)
            await db.flush()

            for q_data in quiz_data["questions"]:
                question = Question(
                    id=str(uuid4()),
                    question_id=q_data["question_id"],
                    quiz_id=quiz.id,
                    type=q_data["type"],
                    question_text=q_data["question_text"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                    chapter_reference=q_data["chapter_reference"],
                    order=q_data["order"],
                    points=q_data["points"],
                )
                db.add(question)

        print("Seeding achievements...")
        for achievement_data in ACHIEVEMENTS:
            achievement = Achievement(
                id=str(uuid4()),
                achievement_id=achievement_data["achievement_id"],
                name=achievement_data["name"],
                description=achievement_data["description"],
                icon=achievement_data["icon"],
                points=achievement_data["points"],
                category=achievement_data["category"],
                sort_order=achievement_data["sort_order"],
                requirement_value=achievement_data.get("requirement_value"),
                requirement_type=achievement_data.get("requirement_type"),
            )
            db.add(achievement)

        await db.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
