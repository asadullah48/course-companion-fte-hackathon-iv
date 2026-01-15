# CONSTITUTIONAL RULES - PHASE 1
## Zero-Backend-LLM Architecture Enforcement

**Status:** 🔒 IMMUTABLE - Cannot be overridden by any subsequent spec  
**Purpose:** Prevent disqualification by enforcing architectural boundaries  
**Enforcement:** Automated audit + code review before submission

---

## ⚠️ CRITICAL: Disqualification Triggers

**Teams are IMMEDIATELY DISQUALIFIED if backend contains:**
```python
# ❌ FORBIDDEN PATTERNS - Instant Disqualification
import openai
import anthropic
from langchain import *
from llama_index import *

# ❌ FORBIDDEN FUNCTION CALLS
openai.ChatCompletion.create()
anthropic.Anthropic().messages.create()
any_llm_api.generate()
any_llm_api.complete()

# ❌ FORBIDDEN OPERATIONS
summarize_with_llm()
generate_with_rag()
prompt_orchestration()
agent_loop()
```

**Detection Method:**
```bash
# Audit script that MUST pass
grep -rn "import openai\|import anthropic\|from langchain\|from llama" src/backend/
# Exit code MUST be 1 (no matches)

grep -rn "\.create(.*model=\|\.generate(\|\.complete(" src/backend/
# Exit code MUST be 1 (no matches)
```

---

## ✅ ALLOWED: Backend Capabilities

### 1. Content Delivery (Verbatim Only)
```python
# ✅ ALLOWED: Serve content exactly as stored
@app.get("/chapters/{chapter_id}")
async def get_chapter(chapter_id: str):
    """Serve chapter content verbatim from R2/database"""
    content = await r2_client.get_object(f"chapters/{chapter_id}.md")
    return {"content": content}  # No LLM processing
```

**Rules:**
- Content MUST be served byte-for-byte as stored
- No summarization, no paraphrasing, no LLM enhancement
- Markdown/JSON/text returned without modification

---

### 2. Navigation (Rule-Based Only)
```python
# ✅ ALLOWED: Deterministic navigation logic
@app.get("/chapters/{chapter_id}/next")
async def get_next_chapter(chapter_id: str, user_id: str):
    """Return next chapter based on completion status"""
    current_index = CHAPTER_ORDER.index(chapter_id)
    
    # Check if user completed current chapter
    completed = await db.check_completion(user_id, chapter_id)
    
    if not completed:
        return {"next": None, "reason": "complete_current_first"}
    
    next_index = current_index + 1
    if next_index < len(CHAPTER_ORDER):
        return {"next": CHAPTER_ORDER[next_index]}
    
    return {"next": None, "reason": "course_complete"}
```

**Rules:**
- Navigation based on hardcoded sequences or database state
- No LLM-based "personalized path recommendation"
- Conditional logic only (if/else, not AI reasoning)

---

### 3. Quiz Grading (Answer Key Matching Only)
```python
# ✅ ALLOWED: Exact answer matching
@app.post("/quizzes/{quiz_id}/submit")
async def grade_quiz(quiz_id: str, answers: dict):
    """Grade quiz using stored answer key"""
    answer_key = await db.get_answer_key(quiz_id)
    
    results = {}
    for question_id, user_answer in answers.items():
        correct_answer = answer_key[question_id]
        
        # Exact match or normalized comparison
        is_correct = normalize(user_answer) == normalize(correct_answer)
        results[question_id] = {
            "correct": is_correct,
            "correct_answer": correct_answer if not is_correct else None
        }
    
    score = sum(1 for r in results.values() if r["correct"])
    return {"score": score, "total": len(answers), "results": results}

def normalize(answer: str) -> str:
    """Deterministic normalization only"""
    return answer.strip().lower().replace(" ", "")
```

**Rules:**
- Multiple choice: exact option matching
- True/False: boolean comparison
- Fill-in-blank: normalized string comparison (case-insensitive, whitespace-trimmed)
- ❌ NO free-form answer evaluation via LLM
- ❌ NO "partial credit" based on LLM judgment

---

### 4. Progress Tracking (Database Operations Only)
```python
# ✅ ALLOWED: Track completion state
@app.put("/progress/{user_id}")
async def update_progress(user_id: str, progress: ProgressUpdate):
    """Update user progress in database"""
    await db.execute("""
        INSERT INTO user_progress (user_id, chapter_id, completed_at)
        VALUES ($1, $2, NOW())
        ON CONFLICT (user_id, chapter_id) DO UPDATE
        SET completed_at = NOW()
    """, user_id, progress.chapter_id)
    
    # Calculate streak
    streak = await calculate_streak(user_id)
    
    return {"success": True, "streak": streak}

async def calculate_streak(user_id: str) -> int:
    """Deterministic streak calculation"""
    recent_days = await db.fetch("""
        SELECT DISTINCT DATE(completed_at) as day
        FROM user_progress
        WHERE user_id = $1
        ORDER BY day DESC
        LIMIT 365
    """, user_id)
    
    # Count consecutive days
    streak = 0
    expected_date = date.today()
    for row in recent_days:
        if row['day'] == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        else:
            break
    
    return streak
```

**Rules:**
- SQL queries for state management
- Deterministic calculations (streaks, completion %, time spent)
- No LLM-based "learning analytics" or "recommendations"

---

### 5. Search (Pre-Computed Embeddings Only)
```python
# ✅ ALLOWED: Keyword search
@app.get("/search")
async def search_content(query: str):
    """Search using pre-computed embeddings or keywords"""
    # Option A: Simple keyword search
    results = await db.fetch("""
        SELECT chapter_id, title, snippet
        FROM chapters
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $1)
        ORDER BY ts_rank(to_tsvector('english', content), plainto_tsquery('english', $1)) DESC
        LIMIT 10
    """, query)
    
    # Option B: Pre-computed embedding search (if embeddings exist)
    query_embedding = PRECOMPUTED_EMBEDDINGS.get(query.lower())
    if query_embedding:
        results = await vector_db.search(query_embedding, limit=10)
    
    return {"results": results}
```

**Rules:**
- Keyword search via PostgreSQL full-text search ✅
- Pre-computed embeddings (generated offline) ✅
- ❌ NO real-time embedding generation via OpenAI API
- ❌ NO LLM-based semantic search with on-the-fly inference

---

### 6. Freemium Gate (Access Control Rules)
```python
# ✅ ALLOWED: Rule-based access control
@app.get("/access/check")
async def check_access(user_id: str, chapter_id: str):
    """Check if user has access to content"""
    user = await db.get_user(user_id)
    chapter_index = CHAPTER_ORDER.index(chapter_id)
    
    # Free tier: First 3 chapters
    if chapter_index < 3:
        return {"access": True, "reason": "free_tier"}
    
    # Premium required
    if user.subscription_tier in ["premium", "pro", "team"]:
        return {"access": True, "reason": user.subscription_tier}
    
    return {
        "access": False,
        "reason": "premium_required",
        "upgrade_url": "/pricing"
    }
```

**Rules:**
- Access based on subscription tier + chapter index
- No LLM involvement in access decisions
- Deterministic rule evaluation

---

## 🛡️ Enforcement Mechanisms

### Pre-Commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "🔍 Running Zero-Backend-LLM audit..."

# Check for forbidden imports
if grep -rn "import openai\|import anthropic\|from langchain\|from llama_index" src/backend/ ; then
    echo "❌ FORBIDDEN: LLM imports detected in backend"
    exit 1
fi

# Check for forbidden API calls
if grep -rn "\.create(.*model=\|\.generate(\|\.complete(\|ChatCompletion\|messages\.create" src/backend/ ; then
    echo "❌ FORBIDDEN: LLM API calls detected in backend"
    exit 1
fi

# Check for forbidden packages in requirements.txt
if grep -i "openai\|anthropic\|langchain\|llama-index" src/backend/requirements.txt ; then
    echo "❌ FORBIDDEN: LLM packages in requirements.txt"
    exit 1
fi

echo "✅ Zero-Backend-LLM audit passed"
exit 0
```

### CI/CD Pipeline Check
```yaml
# .github/workflows/architecture-audit.yml
name: Architecture Audit
on: [push, pull_request]

jobs:
  zero-backend-llm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Audit for LLM imports
        run: |
          if grep -rn "import openai\|import anthropic\|from langchain" src/backend/ ; then
            echo "❌ DISQUALIFICATION RISK: LLM imports found"
            exit 1
          fi
      
      - name: Audit for LLM API calls
        run: |
          if grep -rn "\.create(.*model=\|\.generate(\|\.complete(" src/backend/ ; then
            echo "❌ DISQUALIFICATION RISK: LLM API calls found"
            exit 1
          fi
      
      - name: Success
        run: echo "✅ Zero-Backend-LLM architecture verified"
```

---

## 📊 Cost Compliance Rules

### Backend Cost MUST Stay Under:
- **$0.004 per user per month** (10K users = $40/month max)
- **Zero LLM inference costs** in Phase 1

### Allowed Costs:
```
✅ Cloudflare R2: ~$5/month (storage + reads)
✅ PostgreSQL: $0-25/month (Neon/Supabase free tier)
✅ Compute: $5-20/month (Fly.io/Railway)
✅ Domain: ~$1/month
---
Total: $16-41/month for 10K users
```

### Forbidden Costs:
```
❌ OpenAI API calls
❌ Anthropic API calls
❌ Google AI API calls
❌ Embedding generation APIs
❌ Any LLM inference service
```

---

## 🎯 Phase 1 Feature Boundaries

### What Backend CAN Do:
1. ✅ Serve content verbatim
2. ✅ Track progress/streaks
3. ✅ Grade quizzes (answer key)
4. ✅ Navigate (rule-based)
5. ✅ Search (keyword/precomputed)
6. ✅ Enforce access control

### What Backend CANNOT Do:
1. ❌ Explain concepts (ChatGPT does this)
2. ❌ Answer questions (ChatGPT does this)
3. ❌ Summarize content (ChatGPT does this)
4. ❌ Generate examples (ChatGPT does this)
5. ❌ Personalized recommendations (Phase 2 only)
6. ❌ Free-form assessment (Phase 2 only)

---

## 🔐 Constitutional Guarantee

**This specification is IMMUTABLE for Phase 1.**

Any developer, AI agent (including Claude Code), or team member who attempts to:
- Add LLM imports to backend
- Add LLM API calls to backend
- Justify "just a small LLM call" in backend
- Claim "it's necessary for user experience"

**Is violating the Constitution and risking team disqualification.**

---

## 📜 Sign-Off Required

**By proceeding with implementation, the team acknowledges:**

- [ ] I understand Zero-Backend-LLM architecture
- [ ] I will NOT add LLM calls to backend under any circumstances
- [ ] I will run audit scripts before every commit
- [ ] I understand this prevents disqualification
- [ ] ChatGPT handles ALL intelligence in Phase 1

**Team Lead Signature:** Asadullah (@asadullah48)  
**Date:** January 15, 2026  
**Status:** 🔒 IMMUTABLE - CONSTITUTIONAL RULES IN EFFECT

---

**Enforcement Level:** CRITICAL  
**Violation Consequence:** IMMEDIATE DISQUALIFICATION  
**Review Frequency:** Every commit, every PR, before submission
