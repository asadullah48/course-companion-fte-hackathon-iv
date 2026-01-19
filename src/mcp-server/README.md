# Course Companion MCP Server

MCP (Model Context Protocol) server for Claude Desktop and Claude Code integration with the AI Agent Development course.

## Overview

This MCP server provides Claude with direct access to the Course Companion API, enabling:
- **Content Delivery**: Fetch chapters and modules
- **Quiz Management**: Start quizzes, submit answers, get results
- **Progress Tracking**: View progress, streaks, achievements
- **Search**: Find content by keyword
- **Navigation**: Course structure and chapter navigation

## Installation

```bash
cd src/mcp-server
pip install -r requirements.txt
```

## Configuration

Create a `.env` file:

```env
COURSE_COMPANION_API_URL=http://localhost:8000/api/v1
COURSE_COMPANION_API_TOKEN=your-jwt-token-here
```

## Usage with Claude Desktop

Add to your Claude Desktop configuration (`~/.config/claude/claude_desktop_config.json` on Linux or `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "course-companion": {
      "command": "python",
      "args": ["/path/to/src/mcp-server/server.py"],
      "env": {
        "COURSE_COMPANION_API_URL": "http://localhost:8000/api/v1",
        "COURSE_COMPANION_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

## Available Tools

### Content Delivery
| Tool | Description |
|------|-------------|
| `get_chapter` | Get chapter content for explaining concepts |
| `list_chapters` | List all chapters with metadata |
| `get_module` | Get module overview |
| `list_modules` | List all course modules |

### Quiz Management
| Tool | Description |
|------|-------------|
| `list_quizzes` | List available quizzes |
| `get_quiz` | Get quiz metadata |
| `start_quiz` | Start a quiz attempt (returns questions) |
| `submit_quiz` | Submit answers and get graded results |

### Progress Tracking
| Tool | Description |
|------|-------------|
| `get_progress` | Get overall user progress |
| `get_streak` | Get learning streak info |
| `get_achievements` | Get achievements (earned/locked) |
| `mark_chapter_complete` | Mark a chapter as completed |

### Search & Navigation
| Tool | Description |
|------|-------------|
| `search_content` | Search course content |
| `get_navigation_context` | Get prev/next chapters |
| `get_course_structure` | Get full course structure |

## Example Conversation

```
User: Explain what AI Agents are

Claude: [Uses get_chapter tool with chapter_id="ch1-intro-to-agents"]
        [Returns chapter content, then explains it naturally]

User: Quiz me on that

Claude: [Uses start_quiz tool]
        [Presents questions one at a time]
        [Uses submit_quiz when user answers]

User: How's my progress?

Claude: [Uses get_progress and get_streak tools]
        [Presents encouraging summary]
```

## Constitutional Compliance

This MCP server maintains Zero-Backend-LLM compliance:
- ✅ Server only proxies requests to deterministic backend
- ✅ All intelligence comes from Claude (client)
- ❌ NO LLM processing in this server
- ❌ NO content transformation

## Development

Run locally:
```bash
python server.py
```

Test with MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python server.py
```

## Architecture

```
┌─────────────────────────────────┐
│         Claude Desktop          │
│    (ALL INTELLIGENCE HERE)      │
└──────────────┬──────────────────┘
               │ MCP Protocol
               ▼
┌─────────────────────────────────┐
│     MCP Server (This file)      │
│   (Proxy - NO intelligence)     │
└──────────────┬──────────────────┘
               │ HTTP/REST
               ▼
┌─────────────────────────────────┐
│      Backend API (FastAPI)      │
│  (Deterministic - NO LLM)       │
└─────────────────────────────────┘
```
