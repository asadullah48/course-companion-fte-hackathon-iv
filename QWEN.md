# Course Companion FTE - Hackathon IV

## Project Overview

The Course Companion is an AI-powered educational platform designed to teach AI Agent Development using a "Zero-Backend-LLM" architecture. The project follows a three-phase development approach:

1. **Phase 1**: Zero-Backend-LLM Architecture (deterministic backend + intelligent frontend)
2. **Phase 2**: Hybrid Intelligence (some LLM features added)
3. **Phase 3**: Full Web Application

The core concept is to leverage ChatGPT's intelligence for explaining concepts, answering questions, and providing personalized learning experiences while keeping the backend completely deterministic (no LLM calls in the backend).

## Architecture

### Zero-Backend-LLM Architecture

The system follows a strict architectural pattern:

```
User → ChatGPT App (OpenAI Apps SDK) → FastAPI Backend → Cloudflare R2
                    ↓                          ↓
              (ALL Intelligence)      (ZERO Intelligence)
                                              ↓
                                       PostgreSQL (Progress)
```

**Backend Responsibilities (Deterministic ONLY):**
- Serve course content verbatim from R2 storage
- Track user progress, streaks, and completion
- Grade quizzes using exact answer-key matching
- Keyword/semantic search (using pre-computed embeddings)
- Enforce freemium access gates
- Return navigation paths (next/previous chapter)

**Forbidden in Backend:**
- ANY LLM API calls (OpenAI, Anthropic, Google)
- RAG summarization or content generation
- Prompt orchestration or agent loops
- Dynamic content transformation via LLM
- Evaluation beyond exact-match comparison

### Components

#### Backend (src/backend/)
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (with asyncpg)
- **Storage**: Cloudflare R2 (S3-compatible)
- **Authentication**: JWT tokens with bcrypt
- **Caching**: Redis

#### MCP Server (src/mcp-server/)
- **Purpose**: Model Context Protocol server for Claude Desktop/Code integration
- **Function**: Acts as a proxy between Claude and the backend API
- **Dependencies**: mcp, httpx, python-dotenv

#### ChatGPT App (src/chatgpt-app/)
- **Framework**: OpenAI Apps SDK
- **Responsibilities**: All intelligent processing (explanations, Q&A, motivation)

#### Web Frontend (src/web-frontend/)
- Planned for Phase 3 (Next.js 14, Tailwind CSS, shadcn/ui)

## Technology Stack

### Phase 1 Stack
| Layer | Technology | Justification |
|-------|------------|---------------|
| **Frontend** | OpenAI Apps SDK | 800M+ user reach, conversational UI |
| **Backend** | FastAPI (Python) | High performance, type safety, async support |
| **Database** | PostgreSQL (Neon/Supabase) | Free tier, reliable, SQL for progress tracking |
| **Storage** | Cloudflare R2 | S3-compatible, $0.015/GB, zero egress fees |
| **Compute** | Fly.io / Railway | Low-cost, auto-scaling, global edge |
| **Search** | Pre-computed embeddings | Avoid real-time LLM inference |

## Building and Running

### Backend Setup
```bash
cd src/backend
pip install -r requirements.txt
# Set up environment variables
cp .env.example .env
# Configure your .env file with database, R2, and JWT settings
```

### MCP Server Setup
```bash
cd src/mcp-server
pip install -r requirements.txt
# Configure .env file with COURSE_COMPANION_API_URL and COURSE_COMPANION_API_TOKEN
```

### Running the Backend
```bash
cd src/backend
uvicorn app.main:app --reload --port 8000
```

### Running the MCP Server
```bash
cd src/mcp-server
python server.py
```

### Claude Desktop Integration
Add the MCP server to Claude Desktop configuration:
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

## Available Tools (MCP Server)

The MCP server provides Claude with access to various tools:

### Content Delivery
- `get_chapter`: Get chapter content for explaining concepts
- `list_chapters`: List all chapters with metadata
- `get_module`: Get module overview
- `list_modules`: List all course modules

### Quiz Management
- `list_quizzes`: List available quizzes
- `get_quiz`: Get quiz metadata
- `start_quiz`: Start a quiz attempt
- `submit_quiz`: Submit answers and get graded results

### Progress Tracking
- `get_progress`: Get overall user progress
- `get_streak`: Get learning streak info
- `get_achievements`: Get achievements (earned/locked)
- `mark_chapter_complete`: Mark a chapter as completed

### Search & Navigation
- `search_content`: Search course content
- `get_navigation_context`: Get prev/next chapters
- `get_course_structure`: Get full course structure

## Development Conventions

### Constitutional Rules
- **Zero-Backend-LLM**: No LLM calls in the backend (disqualification risk)
- **Content Verbatim**: Serve content exactly as stored, no transformations
- **Deterministic Operations**: All backend operations must be predictable and repeatable

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints throughout
- Write comprehensive tests
- Use async/await for I/O operations

### Testing
- Unit tests using pytest
- Async tests with pytest-asyncio
- Integration tests for API endpoints

### Cost Optimization
- Target $0.002-$0.004 per user per month in Phase 1
- Zero LLM costs in backend
- Use pre-computed embeddings instead of real-time generation

## Project Structure

```
course-companion-fte-hackathon-iv/
├── specs/                        # Source of Truth
│   ├── phase1/
│   │   ├── constitution/         # Immutable rules
│   │   ├── backend/             # API specs
│   │   ├── frontend/            # ChatGPT App specs
│   │   ├── skills/              # Agent Skills specs
│   │   └── content/             # Content structure specs
│   ├── phase2/                   # Hybrid intelligence specs
│   └── phase3/                   # Web frontend specs
├── src/                          # Generated Code
│   ├── backend/                 # FastAPI application
│   ├── chatgpt-app/             # OpenAI Apps manifest
│   ├── mcp-server/              # MCP server for Claude integration
│   └── web-frontend/            # Next.js application
├── docs/                         # Documentation
│   ├── architecture/
│   ├── cost-analysis/
│   └── demo/
└── history/                      # Prompt history
```

## Phase-Specific Features

### Phase 1: Zero-Backend-LLM
- Deterministic backend with no LLM calls
- ChatGPT handles all intelligence
- Content delivery and progress tracking
- Quiz management with exact-answer grading

### Phase 2: Hybrid Intelligence
- Claude Sonnet 4 API for adaptive learning paths
- LLM-based assessment grading
- Cross-chapter synthesis

### Phase 3: Full Web Application
- Next.js 14 with App Router
- Advanced UI with Tailwind CSS and shadcn/ui
- Recharts for progress visualization

## Cost Targets

### Phase 1 Cost Targets
- **Infrastructure**: $16-$41/month (10K users)
- **Per User**: $0.002-$0.004/month
- **Zero LLM costs** in backend

### Monetization Model
| Tier | Price | Features | LLM Cost |
|------|-------|----------|----------|
| Free | $0 | 3 chapters, basic quizzes | $0 |
| Premium | $9.99/mo | All content, progress tracking | $0 |
| Pro | $19.99/mo | + Adaptive paths, LLM grading | $0.05-0.10/user |
| Team | $49.99/mo | + Analytics, multi-seat | $0.15-0.30/user |