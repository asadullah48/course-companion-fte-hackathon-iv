# Backend API Specification: Search
## Phase 1 - Zero-Backend-LLM Architecture

**API Version:** 1.0
**Responsibility:** Content search using keyword matching and pre-computed embeddings
**Intelligence Level:** ZERO (No Real-Time LLM Inference)

---

## Constitutional Compliance

✅ **ALLOWED:** PostgreSQL full-text search (tsvector/tsquery)
✅ **ALLOWED:** Pre-computed embeddings stored in database (generated offline)
✅ **ALLOWED:** Keyword matching and ranking algorithms
❌ **FORBIDDEN:** Real-time embedding generation via OpenAI/Anthropic API
❌ **FORBIDDEN:** LLM-based semantic search with on-the-fly inference
❌ **FORBIDDEN:** AI-powered query expansion or understanding

**Reference:** `specs/phase1/constitution/01-IMMUTABLE-RULES.md`

---

## Search Strategy

### Phase 1: Keyword Search (Primary)
PostgreSQL full-text search provides robust keyword matching without any LLM costs.

### Phase 1: Pre-Computed Embeddings (Optional Enhancement)
- Embeddings generated **offline** during content authoring
- Stored in PostgreSQL with pgvector extension
- No real-time API calls during search

```
Search Query Flow:
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ User Query  │────▶│ PostgreSQL FTS   │────▶│ Ranked Results  │
└─────────────┘     │ (tsvector match) │     └─────────────────┘
                    └──────────────────┘
                           OR
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ User Query  │────▶│ Pre-computed     │────▶│ Similar Content │
│ (normalized)│     │ Embedding Match  │     │ (cosine dist)   │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

---

## API Endpoints

### 1. Search Content

**Endpoint:** `GET /api/v1/search`

**Purpose:** Search across all course content using keyword matching

**Query Parameters:**
- `q` (string, required): Search query (min 2 characters)
- `type` (string, optional): Content type filter
  - `all` (default): Search everything
  - `chapters`: Chapter content only
  - `quizzes`: Quiz questions only
  - `glossary`: Glossary terms only
- `module` (integer, optional): Filter by module number
- `limit` (integer, optional): Max results to return (default: 10, max: 50)
- `offset` (integer, optional): Pagination offset (default: 0)

**Request Example:**
```http
GET /api/v1/search?q=MCP+protocol&type=chapters&limit=5
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "query": "MCP protocol",
  "results": [
    {
      "id": "ch3-mcp-integration",
      "type": "chapter",
      "title": "MCP Integration",
      "snippet": "...The **MCP** (Model Context **Protocol**) enables AI agents to connect to external tools...",
      "module": 1,
      "relevance_score": 0.95,
      "highlights": ["MCP", "Protocol"],
      "url": "/api/v1/chapters/ch3-mcp-integration",
      "is_locked": false
    },
    {
      "id": "ch7-orchestration-patterns",
      "type": "chapter",
      "title": "Orchestration Patterns",
      "snippet": "...using **MCP** servers to orchestrate multiple tools through a unified **protocol**...",
      "module": 3,
      "relevance_score": 0.72,
      "highlights": ["MCP", "protocol"],
      "url": "/api/v1/chapters/ch7-orchestration-patterns",
      "is_locked": true,
      "required_tier": "premium"
    }
  ],
  "total_results": 2,
  "limit": 5,
  "offset": 0,
  "search_time_ms": 12
}
```

**Response 200 (No Results):**
```json
{
  "query": "quantum computing",
  "results": [],
  "total_results": 0,
  "limit": 10,
  "offset": 0,
  "search_time_ms": 8,
  "suggestions": [
    "Try broader terms like 'computing' or 'architecture'",
    "Check spelling of your search terms"
  ]
}
```

**Response 400 (Invalid Query):**
```json
{
  "error": "invalid_query",
  "message": "Search query must be at least 2 characters",
  "query": "M"
}
```

---

### 2. Search Suggestions (Autocomplete)

**Endpoint:** `GET /api/v1/search/suggest`

**Purpose:** Provide autocomplete suggestions as user types

**Query Parameters:**
- `q` (string, required): Partial search query (min 2 characters)
- `limit` (integer, optional): Max suggestions (default: 5, max: 10)

**Request Example:**
```http
GET /api/v1/search/suggest?q=agen&limit=5
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "query": "agen",
  "suggestions": [
    {
      "term": "AI Agents",
      "type": "topic",
      "result_count": 12
    },
    {
      "term": "Agent Factory",
      "type": "concept",
      "result_count": 8
    },
    {
      "term": "Agent SDK",
      "type": "topic",
      "result_count": 6
    },
    {
      "term": "agentic workflows",
      "type": "chapter",
      "result_count": 4
    },
    {
      "term": "agent skills",
      "type": "topic",
      "result_count": 5
    }
  ]
}
```

---

### 3. Search Within Chapter

**Endpoint:** `GET /api/v1/chapters/{chapter_id}/search`

**Purpose:** Search within a specific chapter's content

**Path Parameters:**
- `chapter_id` (string, required): Chapter to search within

**Query Parameters:**
- `q` (string, required): Search query
- `context_lines` (integer, optional): Lines of context around match (default: 2)

**Request Example:**
```http
GET /api/v1/chapters/ch3-mcp-integration/search?q=transport&context_lines=3
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "chapter_id": "ch3-mcp-integration",
  "query": "transport",
  "matches": [
    {
      "section": "Transport Layer",
      "line_number": 145,
      "match": "The **transport** layer handles communication between client and server.",
      "context_before": [
        "## Communication Architecture",
        "",
        "MCP uses a layered approach to communication."
      ],
      "context_after": [
        "Common transport options include:",
        "- Standard I/O (stdio)",
        "- HTTP with Server-Sent Events"
      ]
    },
    {
      "section": "Transport Options",
      "line_number": 162,
      "match": "Choosing the right **transport** depends on your deployment environment.",
      "context_before": [
        "### Selecting a Transport",
        ""
      ],
      "context_after": [
        "For local development, stdio is recommended.",
        "For production, consider HTTP transport."
      ]
    }
  ],
  "total_matches": 2
}
```

---

### 4. Get Popular Searches

**Endpoint:** `GET /api/v1/search/popular`

**Purpose:** Return trending/popular search terms (for discovery)

**Query Parameters:**
- `period` (string, optional): Time period
  - `day` (default): Last 24 hours
  - `week`: Last 7 days
  - `all`: All time
- `limit` (integer, optional): Max results (default: 10)

**Request Example:**
```http
GET /api/v1/search/popular?period=week&limit=5
Authorization: Bearer <user_token>
```

**Response 200 (Success):**
```json
{
  "period": "week",
  "popular_searches": [
    {
      "term": "MCP",
      "search_count": 342,
      "trend": "up",
      "related_chapter": "ch3-mcp-integration"
    },
    {
      "term": "Claude Agent SDK",
      "search_count": 287,
      "trend": "stable",
      "related_chapter": "ch2-claude-agent-sdk"
    },
    {
      "term": "SKILL.md",
      "search_count": 198,
      "trend": "up",
      "related_chapter": "ch4-skill-md-structure"
    },
    {
      "term": "orchestration",
      "search_count": 156,
      "trend": "down",
      "related_chapter": "ch7-orchestration-patterns"
    },
    {
      "term": "multi-agent",
      "search_count": 134,
      "trend": "up",
      "related_chapter": "ch8-multi-agent-systems"
    }
  ]
}
```

---

## Database Schema

### PostgreSQL Full-Text Search Setup

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy matching
CREATE EXTENSION IF NOT EXISTS unaccent; -- For accent-insensitive search

-- Search index on chapters
CREATE TABLE chapter_search_index (
    chapter_id VARCHAR(100) PRIMARY KEY REFERENCES chapters(chapter_id),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    module_id INTEGER NOT NULL,

    -- Full-text search vector (auto-updated)
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(content, '')), 'B')
    ) STORED,

    -- Metadata for filtering
    tags TEXT[],
    difficulty VARCHAR(20),
    word_count INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- GIN index for fast full-text search
CREATE INDEX idx_chapter_search_vector ON chapter_search_index USING GIN(search_vector);

-- Trigram index for fuzzy/partial matching
CREATE INDEX idx_chapter_title_trgm ON chapter_search_index USING GIN(title gin_trgm_ops);

-- Search suggestions table (pre-computed)
CREATE TABLE search_suggestions (
    term VARCHAR(100) PRIMARY KEY,
    type VARCHAR(20) CHECK (type IN ('topic', 'concept', 'chapter', 'glossary')),
    result_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Popular searches tracking
CREATE TABLE search_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query VARCHAR(255) NOT NULL,
    normalized_query VARCHAR(255) NOT NULL,
    user_id VARCHAR(100),
    results_count INTEGER,
    clicked_result VARCHAR(100),
    searched_at TIMESTAMP DEFAULT NOW()
);

-- Index for popular searches aggregation
CREATE INDEX idx_search_logs_normalized ON search_logs(normalized_query, searched_at);

-- Quiz questions search index
CREATE TABLE quiz_search_index (
    question_id VARCHAR(100) PRIMARY KEY,
    quiz_id VARCHAR(100) NOT NULL,
    chapter_id VARCHAR(100),
    question_text TEXT NOT NULL,
    search_vector TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(question_text, ''))
    ) STORED
);

CREATE INDEX idx_quiz_search_vector ON quiz_search_index USING GIN(search_vector);

-- Glossary terms for search
CREATE TABLE glossary (
    term_id VARCHAR(100) PRIMARY KEY,
    term VARCHAR(100) NOT NULL,
    definition TEXT NOT NULL,
    related_chapters VARCHAR(100)[],
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(term, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(definition, '')), 'B')
    ) STORED
);

CREATE INDEX idx_glossary_search ON glossary USING GIN(search_vector);
```

### Pre-Computed Embeddings (Optional)

```sql
-- Only if using pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Store pre-computed embeddings (generated offline)
CREATE TABLE content_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id VARCHAR(100) NOT NULL,  -- chapter_id, question_id, etc.
    content_type VARCHAR(20) NOT NULL, -- 'chapter', 'quiz', 'glossary'
    chunk_index INTEGER DEFAULT 0,      -- For long content split into chunks
    chunk_text TEXT NOT NULL,           -- The text this embedding represents
    embedding VECTOR(1536),             -- OpenAI ada-002 dimension
    created_at TIMESTAMP DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX idx_content_embeddings ON content_embeddings
USING hnsw (embedding vector_cosine_ops);

-- Pre-computed query embeddings for common searches
CREATE TABLE query_embeddings (
    query_normalized VARCHAR(255) PRIMARY KEY,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Implementation Requirements

### FastAPI Implementation Pattern

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Literal
from pydantic import BaseModel
import re

router = APIRouter(prefix="/api/v1")

class SearchResult(BaseModel):
    id: str
    type: str
    title: str
    snippet: str
    module: int
    relevance_score: float
    highlights: List[str]
    url: str
    is_locked: bool
    required_tier: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    limit: int
    offset: int
    search_time_ms: int
    suggestions: Optional[List[str]] = None


def normalize_query(query: str) -> str:
    """
    Normalize search query for consistent matching.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ String manipulation only
    - ❌ NO LLM-based query understanding
    """
    # Lowercase
    query = query.lower().strip()
    # Remove special characters except spaces
    query = re.sub(r'[^\w\s]', '', query)
    # Collapse multiple spaces
    query = re.sub(r'\s+', ' ', query)
    return query


def highlight_matches(text: str, query_terms: List[str], max_length: int = 200) -> str:
    """
    Create snippet with highlighted matches.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ String manipulation
    - ❌ NO LLM summarization
    """
    text_lower = text.lower()

    # Find first match position
    first_match = len(text)
    for term in query_terms:
        pos = text_lower.find(term.lower())
        if pos != -1 and pos < first_match:
            first_match = pos

    # Extract snippet around first match
    start = max(0, first_match - 50)
    end = min(len(text), start + max_length)
    snippet = text[start:end]

    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."

    # Highlight matches with markdown bold
    for term in query_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        snippet = pattern.sub(f"**{term}**", snippet)

    return snippet


@router.get("/search")
async def search_content(
    q: str = Query(..., min_length=2, max_length=100, description="Search query"),
    type: Literal["all", "chapters", "quizzes", "glossary"] = "all",
    module: Optional[int] = None,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    user: dict = Depends(get_current_user)
) -> SearchResponse:
    """
    Search course content using PostgreSQL full-text search.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ PostgreSQL tsvector/tsquery (no LLM)
    - ✅ Deterministic ranking (ts_rank)
    - ❌ NO real-time embedding generation
    - ❌ NO LLM-based query expansion
    """
    import time
    start_time = time.time()

    # Normalize and prepare query
    normalized = normalize_query(q)
    query_terms = normalized.split()

    # Convert to tsquery format
    tsquery = " & ".join(query_terms)  # AND search

    # Build search query based on type
    results = []

    if type in ("all", "chapters"):
        chapter_results = await db.fetch(
            """
            SELECT
                c.chapter_id as id,
                'chapter' as type,
                c.title,
                c.content,
                c.module_id as module,
                ts_rank(csi.search_vector, plainto_tsquery('english', $1)) as relevance_score,
                CASE WHEN c.module_id > 1 THEN true ELSE false END as is_locked
            FROM chapter_search_index csi
            JOIN chapters c ON c.chapter_id = csi.chapter_id
            WHERE csi.search_vector @@ plainto_tsquery('english', $1)
            AND ($2::int IS NULL OR c.module_id = $2)
            ORDER BY relevance_score DESC
            LIMIT $3 OFFSET $4
            """,
            normalized, module, limit, offset
        )

        for row in chapter_results:
            results.append(SearchResult(
                id=row["id"],
                type=row["type"],
                title=row["title"],
                snippet=highlight_matches(row["content"], query_terms),
                module=row["module"],
                relevance_score=round(row["relevance_score"], 2),
                highlights=query_terms,
                url=f"/api/v1/chapters/{row['id']}",
                is_locked=row["is_locked"],
                required_tier="premium" if row["is_locked"] else None
            ))

    if type in ("all", "quizzes"):
        quiz_results = await db.fetch(
            """
            SELECT
                qsi.question_id as id,
                'quiz' as type,
                q.title,
                qsi.question_text as content,
                c.module_id as module,
                ts_rank(qsi.search_vector, plainto_tsquery('english', $1)) as relevance_score
            FROM quiz_search_index qsi
            JOIN quizzes q ON q.quiz_id = qsi.quiz_id
            JOIN chapters c ON c.chapter_id = q.chapter_id
            WHERE qsi.search_vector @@ plainto_tsquery('english', $1)
            ORDER BY relevance_score DESC
            LIMIT $2
            """,
            normalized, limit
        )

        for row in quiz_results:
            results.append(SearchResult(
                id=row["id"],
                type="quiz",
                title=row["title"],
                snippet=highlight_matches(row["content"], query_terms),
                module=row["module"],
                relevance_score=round(row["relevance_score"], 2),
                highlights=query_terms,
                url=f"/api/v1/quizzes/{row['id'].split('-')[0]}",
                is_locked=row["module"] > 1
            ))

    if type in ("all", "glossary"):
        glossary_results = await db.fetch(
            """
            SELECT
                g.term_id as id,
                'glossary' as type,
                g.term as title,
                g.definition as content,
                ts_rank(g.search_vector, plainto_tsquery('english', $1)) as relevance_score
            FROM glossary g
            WHERE g.search_vector @@ plainto_tsquery('english', $1)
            ORDER BY relevance_score DESC
            LIMIT $2
            """,
            normalized, limit
        )

        for row in glossary_results:
            results.append(SearchResult(
                id=row["id"],
                type="glossary",
                title=row["title"],
                snippet=highlight_matches(row["content"], query_terms),
                module=0,
                relevance_score=round(row["relevance_score"], 2),
                highlights=query_terms,
                url=f"/api/v1/glossary/{row['id']}",
                is_locked=False
            ))

    # Sort all results by relevance
    results.sort(key=lambda x: x.relevance_score, reverse=True)
    results = results[:limit]

    # Log search for analytics
    await db.execute(
        """
        INSERT INTO search_logs (query, normalized_query, user_id, results_count)
        VALUES ($1, $2, $3, $4)
        """,
        q, normalized, user["id"], len(results)
    )

    search_time_ms = int((time.time() - start_time) * 1000)

    # Add suggestions if no results
    suggestions = None
    if len(results) == 0:
        suggestions = [
            "Try broader terms like 'agents' or 'SDK'",
            "Check spelling of your search terms",
            "Use fewer keywords"
        ]

    return SearchResponse(
        query=q,
        results=results,
        total_results=len(results),
        limit=limit,
        offset=offset,
        search_time_ms=search_time_ms,
        suggestions=suggestions
    )


@router.get("/search/suggest")
async def search_suggestions(
    q: str = Query(..., min_length=2, max_length=50),
    limit: int = Query(5, ge=1, le=10)
):
    """
    Provide autocomplete suggestions.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database lookup (pre-computed suggestions)
    - ✅ Trigram similarity matching
    - ❌ NO LLM-based suggestions
    """
    normalized = normalize_query(q)

    # Use trigram similarity for fuzzy matching
    suggestions = await db.fetch(
        """
        SELECT term, type, result_count,
               similarity(term, $1) as sim
        FROM search_suggestions
        WHERE term % $1  -- Trigram similarity operator
        ORDER BY sim DESC, result_count DESC
        LIMIT $2
        """,
        normalized, limit
    )

    return {
        "query": q,
        "suggestions": [
            {
                "term": s["term"],
                "type": s["type"],
                "result_count": s["result_count"]
            }
            for s in suggestions
        ]
    }


@router.get("/chapters/{chapter_id}/search")
async def search_within_chapter(
    chapter_id: str,
    q: str = Query(..., min_length=2),
    context_lines: int = Query(2, ge=0, le=5),
    user: dict = Depends(get_current_user)
):
    """
    Search within a specific chapter.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Line-by-line text search
    - ✅ Context extraction
    - ❌ NO LLM processing
    """
    # Check access
    access = await check_chapter_access(user["id"], chapter_id)
    if not access["allowed"]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get chapter content
    chapter = await db.fetchrow(
        "SELECT content FROM chapters WHERE chapter_id = $1",
        chapter_id
    )

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    lines = chapter["content"].split("\n")
    normalized_query = normalize_query(q)
    query_terms = normalized_query.split()

    matches = []
    current_section = "Introduction"

    for i, line in enumerate(lines):
        # Track section headers
        if line.startswith("## "):
            current_section = line[3:].strip()

        # Check for match
        line_lower = line.lower()
        if any(term in line_lower for term in query_terms):
            # Highlight match
            highlighted_line = line
            for term in query_terms:
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted_line = pattern.sub(f"**{term}**", highlighted_line)

            # Get context
            context_before = lines[max(0, i - context_lines):i]
            context_after = lines[i + 1:min(len(lines), i + 1 + context_lines)]

            matches.append({
                "section": current_section,
                "line_number": i + 1,
                "match": highlighted_line,
                "context_before": context_before,
                "context_after": context_after
            })

    return {
        "chapter_id": chapter_id,
        "query": q,
        "matches": matches,
        "total_matches": len(matches)
    }


@router.get("/search/popular")
async def get_popular_searches(
    period: Literal["day", "week", "all"] = "day",
    limit: int = Query(10, ge=1, le=20)
):
    """
    Get popular search terms.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ SQL aggregation
    - ✅ COUNT operations
    - ❌ NO LLM trend analysis
    """
    # Determine time filter
    time_filters = {
        "day": "NOW() - INTERVAL '1 day'",
        "week": "NOW() - INTERVAL '7 days'",
        "all": "'1970-01-01'"
    }

    popular = await db.fetch(
        f"""
        SELECT
            normalized_query as term,
            COUNT(*) as search_count,
            MODE() WITHIN GROUP (ORDER BY clicked_result) as related_chapter
        FROM search_logs
        WHERE searched_at > {time_filters[period]}
        GROUP BY normalized_query
        ORDER BY search_count DESC
        LIMIT $1
        """,
        limit
    )

    # Calculate trend (compare to previous period)
    results = []
    for item in popular:
        # Simple trend calculation: compare current vs previous period count
        prev_count = await db.fetchval(
            f"""
            SELECT COUNT(*) FROM search_logs
            WHERE normalized_query = $1
            AND searched_at BETWEEN {time_filters[period]} - INTERVAL '7 days' AND {time_filters[period]}
            """,
            item["term"]
        )

        current = item["search_count"]
        if prev_count == 0:
            trend = "new"
        elif current > prev_count * 1.1:
            trend = "up"
        elif current < prev_count * 0.9:
            trend = "down"
        else:
            trend = "stable"

        results.append({
            "term": item["term"],
            "search_count": item["search_count"],
            "trend": trend,
            "related_chapter": item["related_chapter"]
        })

    return {
        "period": period,
        "popular_searches": results
    }
```

---

## Pre-Computed Embedding Generation (Offline Script)

```python
"""
OFFLINE SCRIPT - Run during content authoring, NOT at runtime.
This is the ONLY place where LLM APIs are used.
"""
import openai
import asyncio

async def generate_embeddings_offline():
    """
    Generate embeddings for all content ONCE during setup.
    Store in database for fast retrieval.

    This script runs OFFLINE, not during user requests.
    """
    client = openai.OpenAI()

    # Get all chapters
    chapters = await db.fetch("SELECT chapter_id, content FROM chapters")

    for chapter in chapters:
        # Split content into chunks (max 8000 tokens)
        chunks = split_into_chunks(chapter["content"], max_tokens=8000)

        for i, chunk in enumerate(chunks):
            # Generate embedding (OFFLINE ONLY)
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=chunk
            )

            embedding = response.data[0].embedding

            # Store pre-computed embedding
            await db.execute(
                """
                INSERT INTO content_embeddings
                (content_id, content_type, chunk_index, chunk_text, embedding)
                VALUES ($1, 'chapter', $2, $3, $4)
                """,
                chapter["chapter_id"], i, chunk, embedding
            )

    print("Embeddings generated and stored successfully")


def split_into_chunks(text: str, max_tokens: int = 8000) -> list:
    """Split text into chunks for embedding."""
    # Approximate: 1 token ≈ 4 characters
    max_chars = max_tokens * 4

    chunks = []
    current_chunk = ""

    paragraphs = text.split("\n\n")

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# Run this script ONCE during setup
if __name__ == "__main__":
    asyncio.run(generate_embeddings_offline())
```

---

## Performance Requirements

- **Response Time:** < 100ms (p95) for keyword search
- **Response Time:** < 200ms (p95) for embedding search (if enabled)
- **Throughput:** 500 searches/minute
- **Index Update:** < 1 second per chapter reindex

---

## Security Requirements

1. **Authentication:** JWT Bearer tokens required
2. **Rate Limiting:** 30 searches/minute per user
3. **Input Validation:**
   - Query length limits (2-100 characters)
   - No SQL injection via parameterized queries
4. **Access Control:**
   - Premium content snippets visible but flagged as locked
   - Full content requires access check

---

## Testing Requirements

### Unit Tests

```python
def test_search_basic():
    """Test basic keyword search"""
    response = client.get("/api/v1/search?q=MCP")
    assert response.status_code == 200
    assert len(response.json()["results"]) > 0

def test_search_no_results():
    """Test search with no matches"""
    response = client.get("/api/v1/search?q=xyznonexistent")
    assert response.status_code == 200
    assert response.json()["total_results"] == 0
    assert "suggestions" in response.json()

def test_search_min_length():
    """Test minimum query length"""
    response = client.get("/api/v1/search?q=a")
    assert response.status_code == 400

def test_search_type_filter():
    """Test filtering by content type"""
    response = client.get("/api/v1/search?q=agent&type=chapters")
    assert response.status_code == 200
    assert all(r["type"] == "chapter" for r in response.json()["results"])

def test_search_highlights():
    """Test that matches are highlighted"""
    response = client.get("/api/v1/search?q=MCP")
    result = response.json()["results"][0]
    assert "**MCP**" in result["snippet"] or "**mcp**" in result["snippet"].lower()

def test_suggestions_autocomplete():
    """Test autocomplete suggestions"""
    response = client.get("/api/v1/search/suggest?q=agen")
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]
    assert any("agent" in s["term"].lower() for s in suggestions)

def test_search_within_chapter():
    """Test chapter-specific search"""
    response = client.get("/api/v1/chapters/ch3-mcp-integration/search?q=transport")
    assert response.status_code == 200
    assert len(response.json()["matches"]) > 0

def test_popular_searches():
    """Test popular searches endpoint"""
    response = client.get("/api/v1/search/popular?period=week")
    assert response.status_code == 200
    assert "popular_searches" in response.json()
```

### Integration Tests

- PostgreSQL full-text search index verification
- Trigram index performance check
- Search log aggregation accuracy
- Embedding similarity search (if enabled)

---

## Monitoring & Observability

### Metrics to Track
- Search query latency (p50, p95, p99)
- Zero-result search rate
- Popular search terms
- Search-to-click conversion rate
- Index freshness

### Logging
```python
logger.info(
    "search_executed",
    query=q,
    normalized_query=normalized,
    results_count=len(results),
    search_time_ms=search_time_ms,
    user_id=user["id"],
    type_filter=type
)
```

---

## Cost Analysis

### Per Request Cost
```
PostgreSQL Full-Text Search:
- CPU: Minimal (indexed search)
- Memory: ~50MB for index
- I/O: Single index scan

Pre-Computed Embeddings (optional):
- Storage: ~6KB per chapter (1536 floats × 4 bytes)
- One-time generation cost: ~$0.0001 per chapter
- Runtime: Zero LLM API costs

Total Search Cost: ~$0.00 per search (database only)
```

---

## Success Criteria

✅ **Zero-Backend-LLM Compliance:**
- No real-time LLM API calls during search
- All embeddings pre-computed offline
- Pure PostgreSQL full-text search

✅ **Performance:**
- P95 latency < 100ms
- Support 500 searches/minute

✅ **Functionality:**
- All 4 endpoints implemented
- Relevance ranking working
- Autocomplete functional
- Popular searches tracked

✅ **Security:**
- Input sanitization complete
- Rate limiting in place
- Access control enforced

---

**Spec Version:** 1.0
**Last Updated:** January 16, 2026
**Status:** Ready for Implementation
