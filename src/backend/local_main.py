"""
Course Companion Backend - Local Content Mode
Lightweight FastAPI app that serves content from local markdown files.
No database, no R2, no external dependencies required.

CONSTITUTIONAL COMPLIANCE:
- Content served verbatim from local markdown files
- Deterministic calculations only
- NO LLM processing
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# --- Configuration ---

CONTENT_DIR = os.environ.get(
    "CONTENT_DIR",
    str(Path(__file__).parent / "sample-content"),
)
CHAPTERS_DIR = os.path.join(CONTENT_DIR, "chapters")
APP_ENV = os.environ.get("APP_ENV", "production")
CORS_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,https://chat.openai.com",
).split(",")


# --- Schemas ---

class ChapterMetadata(BaseModel):
    module: int
    order: int
    tags: list[str] = []
    difficulty: str = "beginner"


class ChapterResponse(BaseModel):
    chapter_id: str
    title: str
    content: str
    content_type: str = "markdown"
    word_count: int
    estimated_read_time: int
    metadata: ChapterMetadata
    created_at: str
    updated_at: str


class ChapterListItem(BaseModel):
    chapter_id: str
    title: str
    module: int
    order: int
    difficulty: str
    word_count: int
    estimated_read_time: int
    is_locked: bool = False
    required_tier: Optional[str] = None
    completed: bool = False
    completed_at: Optional[str] = None


class ChapterListResponse(BaseModel):
    chapters: list[ChapterListItem]
    total_chapters: int
    completed_count: int = 0
    locked_count: int = 0


class ModuleChapterSummary(BaseModel):
    chapter_id: str
    title: str
    order: int


class ModuleResponse(BaseModel):
    module_id: str
    title: str
    description: Optional[str] = None
    order: int
    chapters: list[ModuleChapterSummary]
    total_chapters: int
    estimated_duration_minutes: int = 60
    difficulty: str = "beginner"
    prerequisites: list[str] = []
    learning_objectives: list[str] = []
    is_locked: bool = False
    required_tier: Optional[str] = None


class ModuleListResponse(BaseModel):
    modules: list[ModuleResponse]
    total_modules: int


class SearchResult(BaseModel):
    chapter_id: str
    title: str
    snippet: str
    relevance: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total_results: int


class NavigationContext(BaseModel):
    current: ChapterListItem
    previous: Optional[ChapterListItem] = None
    next: Optional[ChapterListItem] = None
    module_title: str
    progress_in_module: str


# --- Content Loader ---

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        meta = {}
    body = parts[2].strip()
    return meta, body


def load_chapters() -> dict[str, dict]:
    """Load all chapters from local markdown files."""
    chapters = {}
    chapters_path = Path(CHAPTERS_DIR)
    if not chapters_path.exists():
        return chapters

    for md_file in sorted(chapters_path.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        chapter_id = meta.get("chapter_id", md_file.stem)
        word_count = len(body.split())
        chapters[chapter_id] = {
            "chapter_id": chapter_id,
            "title": meta.get("title", chapter_id),
            "module": meta.get("module", 1),
            "order": meta.get("order", 0),
            "difficulty": meta.get("difficulty", "beginner"),
            "tags": meta.get("tags", []),
            "prerequisites": meta.get("prerequisites", []),
            "learning_objectives": meta.get("learning_objectives", []),
            "word_count": word_count,
            "estimated_read_time": max(1, word_count // 250),
            "content": body,
            "raw": raw,
            "created_at": str(meta.get("created_at", "2026-01-10T00:00:00Z")),
            "updated_at": str(meta.get("updated_at", "2026-01-15T12:00:00Z")),
        }
    return chapters


# Module definitions
MODULE_DEFINITIONS = [
    {
        "module_id": "mod-1-foundations",
        "title": "Foundations of AI Agents",
        "description": "Learn the core concepts of AI Agents, the Agent Factory Architecture, and Model Context Protocol.",
        "order": 1,
        "difficulty": "beginner",
        "estimated_duration_minutes": 120,
        "learning_objectives": [
            "Define what an AI agent is",
            "Understand the 8-layer Agent Factory Architecture",
            "Learn MCP fundamentals",
        ],
        "prerequisites": [],
    },
    {
        "module_id": "mod-2-skills",
        "title": "Skills Development",
        "description": "Master building AI skills including Concept Explainer, Quiz Master, Socratic Tutor, and Progress Motivator.",
        "order": 2,
        "difficulty": "intermediate",
        "estimated_duration_minutes": 150,
        "learning_objectives": [
            "Build a Concept Explainer skill",
            "Create a Quiz Master skill",
            "Implement Socratic Tutor patterns",
            "Design progress motivation systems",
        ],
        "prerequisites": ["mod-1-foundations"],
    },
    {
        "module_id": "mod-3-production",
        "title": "Agentic Workflows & Production",
        "description": "Design workflow patterns, build multi-agent systems, and deploy to production.",
        "order": 3,
        "difficulty": "advanced",
        "estimated_duration_minutes": 120,
        "learning_objectives": [
            "Design agentic workflow patterns",
            "Deploy agents to production",
            "Monitor and scale AI systems",
        ],
        "prerequisites": ["mod-1-foundations", "mod-2-skills"],
    },
]

# Global chapter cache
_chapters_cache: dict[str, dict] | None = None


def get_chapters() -> dict[str, dict]:
    """Get chapters with caching."""
    global _chapters_cache
    if _chapters_cache is None:
        _chapters_cache = load_chapters()
    return _chapters_cache


def reload_chapters():
    """Force reload chapters from disk."""
    global _chapters_cache
    _chapters_cache = None


# --- FastAPI App ---

app = FastAPI(
    title="Course Companion API",
    description="AI Agent Development Course - Local Content Mode",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Endpoints ---

@app.get("/health")
async def health_check():
    chapters = get_chapters()
    return {
        "status": "healthy",
        "app": "course-companion",
        "version": "1.0.0",
        "environment": APP_ENV,
        "content_mode": "local",
        "chapters_loaded": len(chapters),
    }


@app.get("/")
async def root():
    return {
        "name": "Course Companion API",
        "version": "1.0.0",
        "description": "AI Agent Development Course - Local Content Mode",
        "docs_url": "/docs",
        "chapters_available": len(get_chapters()),
    }


@app.get("/api/v1/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(chapter_id: str):
    chapters = get_chapters()
    ch = chapters.get(chapter_id)
    if not ch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "chapter_not_found", "message": f"Chapter '{chapter_id}' not found"},
        )
    return ChapterResponse(
        chapter_id=ch["chapter_id"],
        title=ch["title"],
        content=ch["content"],
        content_type="markdown",
        word_count=ch["word_count"],
        estimated_read_time=ch["estimated_read_time"],
        metadata=ChapterMetadata(
            module=ch["module"],
            order=ch["order"],
            tags=ch["tags"],
            difficulty=ch["difficulty"],
        ),
        created_at=ch["created_at"],
        updated_at=ch["updated_at"],
    )


@app.get("/api/v1/chapters", response_model=ChapterListResponse)
async def list_chapters(
    module: Optional[int] = Query(default=None, description="Filter by module number"),
):
    chapters = get_chapters()
    items = []
    for ch in sorted(chapters.values(), key=lambda x: x["order"]):
        if module is not None and ch["module"] != module:
            continue
        items.append(
            ChapterListItem(
                chapter_id=ch["chapter_id"],
                title=ch["title"],
                module=ch["module"],
                order=ch["order"],
                difficulty=ch["difficulty"],
                word_count=ch["word_count"],
                estimated_read_time=ch["estimated_read_time"],
                is_locked=False,
            )
        )
    return ChapterListResponse(
        chapters=items,
        total_chapters=len(items),
    )


@app.get("/api/v1/modules/{module_id}", response_model=ModuleResponse)
async def get_module(module_id: str):
    chapters = get_chapters()

    # Find module by ID or order number
    mod_def = None
    for m in MODULE_DEFINITIONS:
        if m["module_id"] == module_id or str(m["order"]) == module_id:
            mod_def = m
            break

    if not mod_def:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "module_not_found", "message": f"Module '{module_id}' not found"},
        )

    mod_chapters = [
        ModuleChapterSummary(
            chapter_id=ch["chapter_id"],
            title=ch["title"],
            order=ch["order"],
        )
        for ch in sorted(chapters.values(), key=lambda x: x["order"])
        if ch["module"] == mod_def["order"]
    ]

    return ModuleResponse(
        module_id=mod_def["module_id"],
        title=mod_def["title"],
        description=mod_def["description"],
        order=mod_def["order"],
        chapters=mod_chapters,
        total_chapters=len(mod_chapters),
        estimated_duration_minutes=mod_def["estimated_duration_minutes"],
        difficulty=mod_def["difficulty"],
        prerequisites=mod_def["prerequisites"],
        learning_objectives=mod_def["learning_objectives"],
    )


@app.get("/api/v1/modules", response_model=ModuleListResponse)
async def list_modules():
    chapters = get_chapters()
    modules = []
    for mod_def in MODULE_DEFINITIONS:
        mod_chapters = [
            ModuleChapterSummary(
                chapter_id=ch["chapter_id"],
                title=ch["title"],
                order=ch["order"],
            )
            for ch in sorted(chapters.values(), key=lambda x: x["order"])
            if ch["module"] == mod_def["order"]
        ]
        modules.append(
            ModuleResponse(
                module_id=mod_def["module_id"],
                title=mod_def["title"],
                description=mod_def["description"],
                order=mod_def["order"],
                chapters=mod_chapters,
                total_chapters=len(mod_chapters),
                estimated_duration_minutes=mod_def["estimated_duration_minutes"],
                difficulty=mod_def["difficulty"],
                prerequisites=mod_def["prerequisites"],
                learning_objectives=mod_def["learning_objectives"],
            )
        )
    return ModuleListResponse(modules=modules, total_modules=len(modules))


@app.get("/api/v1/search", response_model=SearchResponse)
async def search_content(
    q: str = Query(..., description="Search query"),
    limit: int = Query(default=10, description="Max results"),
):
    chapters = get_chapters()
    results = []
    query_lower = q.lower()

    for ch in chapters.values():
        content_lower = ch["content"].lower()
        title_lower = ch["title"].lower()

        # Simple relevance scoring
        relevance = 0.0
        if query_lower in title_lower:
            relevance += 2.0
        occurrences = content_lower.count(query_lower)
        if occurrences > 0:
            relevance += min(1.0, occurrences * 0.2)

        if relevance > 0:
            # Extract snippet around first match
            idx = content_lower.find(query_lower)
            start = max(0, idx - 80)
            end = min(len(ch["content"]), idx + len(q) + 80)
            snippet = ch["content"][start:end].replace("\n", " ").strip()
            if start > 0:
                snippet = "..." + snippet
            if end < len(ch["content"]):
                snippet = snippet + "..."

            results.append(
                SearchResult(
                    chapter_id=ch["chapter_id"],
                    title=ch["title"],
                    snippet=snippet,
                    relevance=relevance,
                )
            )

    results.sort(key=lambda r: r.relevance, reverse=True)
    return SearchResponse(
        query=q,
        results=results[:limit],
        total_results=len(results),
    )


@app.get("/api/v1/navigation/context/{chapter_id}", response_model=NavigationContext)
async def get_navigation_context(chapter_id: str):
    chapters = get_chapters()
    ch = chapters.get(chapter_id)
    if not ch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "chapter_not_found", "message": f"Chapter '{chapter_id}' not found"},
        )

    sorted_chapters = sorted(chapters.values(), key=lambda x: x["order"])
    current_idx = next(
        (i for i, c in enumerate(sorted_chapters) if c["chapter_id"] == chapter_id),
        0,
    )

    def to_list_item(c):
        return ChapterListItem(
            chapter_id=c["chapter_id"],
            title=c["title"],
            module=c["module"],
            order=c["order"],
            difficulty=c["difficulty"],
            word_count=c["word_count"],
            estimated_read_time=c["estimated_read_time"],
            is_locked=False,
        )

    prev_ch = sorted_chapters[current_idx - 1] if current_idx > 0 else None
    next_ch = sorted_chapters[current_idx + 1] if current_idx < len(sorted_chapters) - 1 else None

    # Find module title
    mod_title = "Unknown Module"
    for m in MODULE_DEFINITIONS:
        if m["order"] == ch["module"]:
            mod_title = m["title"]
            break

    # Progress in module
    module_chapters = [c for c in sorted_chapters if c["module"] == ch["module"]]
    ch_idx = next((i for i, c in enumerate(module_chapters) if c["chapter_id"] == chapter_id), 0)

    return NavigationContext(
        current=to_list_item(ch),
        previous=to_list_item(prev_ch) if prev_ch else None,
        next=to_list_item(next_ch) if next_ch else None,
        module_title=mod_title,
        progress_in_module=f"{ch_idx + 1}/{len(module_chapters)}",
    )


@app.get("/api/v1/navigation/structure")
async def get_course_structure():
    chapters = get_chapters()
    structure = []
    for mod_def in MODULE_DEFINITIONS:
        mod_chapters = [
            {
                "chapter_id": ch["chapter_id"],
                "title": ch["title"],
                "order": ch["order"],
                "difficulty": ch["difficulty"],
            }
            for ch in sorted(chapters.values(), key=lambda x: x["order"])
            if ch["module"] == mod_def["order"]
        ]
        structure.append({
            "module_id": mod_def["module_id"],
            "title": mod_def["title"],
            "order": mod_def["order"],
            "chapters": mod_chapters,
        })
    return {"modules": structure, "total_chapters": len(chapters)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("local_main:app", host="0.0.0.0", port=8000, reload=True)
