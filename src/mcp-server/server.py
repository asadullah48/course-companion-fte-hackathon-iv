#!/usr/bin/env python3
"""
Course Companion MCP Server
Provides Claude Desktop/Code integration for the AI Agent Development course.

CONSTITUTIONAL COMPLIANCE:
- ✅ All intelligence in Claude (client)
- ✅ Server only proxies to deterministic backend
- ❌ NO LLM processing in this server
"""

import os
import asyncio
from typing import Any, Optional

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("COURSE_COMPANION_API_URL", "http://localhost:8000/api/v1")
API_TOKEN = os.getenv("COURSE_COMPANION_API_TOKEN", "")

# Create MCP server
server = Server("course-companion")

# HTTP client for backend API
http_client: Optional[httpx.AsyncClient] = None


async def get_client() -> httpx.AsyncClient:
    """Get or create HTTP client."""
    global http_client
    if http_client is None:
        headers = {}
        if API_TOKEN:
            headers["Authorization"] = f"Bearer {API_TOKEN}"
        http_client = httpx.AsyncClient(
            base_url=API_BASE_URL,
            headers=headers,
            timeout=30.0,
        )
    return http_client


async def api_request(method: str, path: str, **kwargs) -> dict[str, Any]:
    """Make API request to backend."""
    client = await get_client()
    response = await client.request(method, path, **kwargs)
    if response.status_code >= 400:
        return {
            "error": True,
            "status_code": response.status_code,
            "detail": response.json() if response.content else {"message": "Request failed"},
        }
    return response.json()


# ============================================
# TOOL DEFINITIONS
# ============================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        # Content Delivery Tools
        Tool(
            name="get_chapter",
            description="Get chapter content for explaining concepts. Returns the full chapter markdown content verbatim.",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "string",
                        "description": "Chapter identifier (e.g., 'ch1-intro-to-agents', 'ch2-agent-factory')",
                    },
                },
                "required": ["chapter_id"],
            },
        ),
        Tool(
            name="list_chapters",
            description="List all available chapters with their metadata and completion status.",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_id": {
                        "type": "string",
                        "description": "Optional: Filter by module ID (e.g., 'mod-1-foundations')",
                    },
                },
            },
        ),
        Tool(
            name="get_module",
            description="Get module overview with its chapters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_id": {
                        "type": "string",
                        "description": "Module identifier (e.g., 'mod-1-foundations', or just '1')",
                    },
                },
                "required": ["module_id"],
            },
        ),
        Tool(
            name="list_modules",
            description="List all course modules.",
            inputSchema={"type": "object", "properties": {}},
        ),

        # Quiz Tools
        Tool(
            name="list_quizzes",
            description="List all available quizzes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "module_id": {
                        "type": "string",
                        "description": "Optional: Filter by module ID",
                    },
                },
            },
        ),
        Tool(
            name="get_quiz",
            description="Get quiz metadata (without starting an attempt).",
            inputSchema={
                "type": "object",
                "properties": {
                    "quiz_id": {
                        "type": "string",
                        "description": "Quiz identifier (e.g., 'quiz-mod-1-foundations')",
                    },
                },
                "required": ["quiz_id"],
            },
        ),
        Tool(
            name="start_quiz",
            description="Start a new quiz attempt. Returns questions (without correct answers).",
            inputSchema={
                "type": "object",
                "properties": {
                    "quiz_id": {
                        "type": "string",
                        "description": "Quiz identifier",
                    },
                },
                "required": ["quiz_id"],
            },
        ),
        Tool(
            name="submit_quiz",
            description="Submit quiz answers and get graded results.",
            inputSchema={
                "type": "object",
                "properties": {
                    "quiz_id": {
                        "type": "string",
                        "description": "Quiz identifier",
                    },
                    "attempt_id": {
                        "type": "string",
                        "description": "Attempt ID from start_quiz",
                    },
                    "answers": {
                        "type": "object",
                        "description": "Answers as {question_id: answer} mapping",
                        "additionalProperties": {"type": "string"},
                    },
                },
                "required": ["quiz_id", "attempt_id", "answers"],
            },
        ),

        # Progress Tools
        Tool(
            name="get_progress",
            description="Get user's overall progress across all modules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier",
                    },
                },
                "required": ["user_id"],
            },
        ),
        Tool(
            name="get_streak",
            description="Get user's learning streak information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier",
                    },
                },
                "required": ["user_id"],
            },
        ),
        Tool(
            name="get_achievements",
            description="Get user's achievements (earned and locked).",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier",
                    },
                    "filter": {
                        "type": "string",
                        "enum": ["all", "earned", "locked"],
                        "description": "Filter achievements by status",
                    },
                },
                "required": ["user_id"],
            },
        ),
        Tool(
            name="mark_chapter_complete",
            description="Mark a chapter as completed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier",
                    },
                    "chapter_id": {
                        "type": "string",
                        "description": "Chapter identifier",
                    },
                    "completion_type": {
                        "type": "string",
                        "enum": ["quiz_passed", "content_read"],
                        "description": "How the chapter was completed",
                    },
                    "time_spent_minutes": {
                        "type": "integer",
                        "description": "Time spent on the chapter",
                    },
                },
                "required": ["user_id", "chapter_id", "completion_type", "time_spent_minutes"],
            },
        ),

        # Search Tools
        Tool(
            name="search_content",
            description="Search course content by keyword.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                    },
                },
                "required": ["query"],
            },
        ),

        # Navigation Tools
        Tool(
            name="get_navigation_context",
            description="Get navigation context for a chapter (previous/next chapters).",
            inputSchema={
                "type": "object",
                "properties": {
                    "chapter_id": {
                        "type": "string",
                        "description": "Current chapter identifier",
                    },
                },
                "required": ["chapter_id"],
            },
        ),
        Tool(
            name="get_course_structure",
            description="Get the full course structure (all modules and chapters).",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


# ============================================
# TOOL IMPLEMENTATIONS
# ============================================

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Handle tool calls."""
    try:
        result = await _execute_tool(name, arguments)
        return CallToolResult(
            content=[TextContent(type="text", text=str(result))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )


async def _execute_tool(name: str, args: dict[str, Any]) -> Any:
    """Execute a tool and return the result."""

    # Content Delivery
    if name == "get_chapter":
        return await api_request("GET", f"/chapters/{args['chapter_id']}")

    elif name == "list_chapters":
        params = {}
        if args.get("module_id"):
            params["module_id"] = args["module_id"]
        return await api_request("GET", "/chapters", params=params)

    elif name == "get_module":
        return await api_request("GET", f"/modules/{args['module_id']}")

    elif name == "list_modules":
        return await api_request("GET", "/modules")

    # Quiz
    elif name == "list_quizzes":
        params = {}
        if args.get("module_id"):
            params["module_id"] = args["module_id"]
        return await api_request("GET", "/quizzes", params=params)

    elif name == "get_quiz":
        return await api_request("GET", f"/quizzes/{args['quiz_id']}")

    elif name == "start_quiz":
        return await api_request("POST", f"/quizzes/{args['quiz_id']}/start")

    elif name == "submit_quiz":
        return await api_request(
            "POST",
            f"/quizzes/{args['quiz_id']}/submit",
            params={"attempt_id": args["attempt_id"]},
            json={"answers": args["answers"]},
        )

    # Progress
    elif name == "get_progress":
        return await api_request("GET", f"/progress/{args['user_id']}")

    elif name == "get_streak":
        return await api_request("GET", f"/progress/{args['user_id']}/streak")

    elif name == "get_achievements":
        params = {}
        if args.get("filter"):
            params["filter"] = args["filter"]
        return await api_request("GET", f"/progress/{args['user_id']}/achievements", params=params)

    elif name == "mark_chapter_complete":
        return await api_request(
            "PUT",
            f"/progress/{args['user_id']}/chapters/{args['chapter_id']}",
            json={
                "completion_type": args["completion_type"],
                "time_spent_minutes": args["time_spent_minutes"],
            },
        )

    # Search
    elif name == "search_content":
        params = {"q": args["query"]}
        if args.get("limit"):
            params["limit"] = args["limit"]
        return await api_request("GET", "/search", params=params)

    # Navigation
    elif name == "get_navigation_context":
        return await api_request("GET", f"/navigation/context/{args['chapter_id']}")

    elif name == "get_course_structure":
        return await api_request("GET", "/navigation/structure")

    else:
        return {"error": f"Unknown tool: {name}"}


# ============================================
# SERVER LIFECYCLE
# ============================================

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
