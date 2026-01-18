# Backend API Specification: Access Control & Freemium
## Phase 1 - Zero-Backend-LLM Architecture

**API Version:** 1.0
**Responsibility:** Manage user subscriptions, access tiers, and content gating
**Intelligence Level:** ZERO (Rule-Based Access Control Only)

---

## Constitutional Compliance

✅ **ALLOWED:** Rule-based tier checking (if/else logic)
✅ **ALLOWED:** Database lookups for subscription status
✅ **ALLOWED:** Deterministic access decisions
❌ **FORBIDDEN:** LLM-based access recommendations
❌ **FORBIDDEN:** AI-driven pricing optimization
❌ **FORBIDDEN:** Dynamic tier assignment via ML

**Reference:** `specs/phase1/constitution/01-IMMUTABLE-RULES.md`

---

## Subscription Tiers

### Tier Structure

| Tier | Price | Content Access | Features |
|------|-------|----------------|----------|
| **Free** | $0 | Chapters 1-3 (Module 1) | Basic quizzes, progress tracking |
| **Premium** | $9.99/mo | All 9 chapters | Full quizzes, achievements, streaks |
| **Pro** | $19.99/mo | All + Adaptive Paths* | Phase 2: LLM-graded assessments |
| **Team** | $49.99/mo | All + Analytics* | Phase 2: Team management |

*Phase 2 features - not implemented in Phase 1

### Access Rules (Hardcoded)

```python
# Immutable access rules for Phase 1
ACCESS_RULES = {
    "free": {
        "chapters": ["ch1-intro-to-agents", "ch2-claude-agent-sdk", "ch3-mcp-integration"],
        "modules": [1],
        "quiz_attempts_per_quiz": 3,
        "quiz_types": ["chapter", "practice"],
        "features": ["progress_tracking", "basic_achievements"]
    },
    "premium": {
        "chapters": "all",  # All 9 chapters
        "modules": [1, 2, 3],
        "quiz_attempts_per_quiz": "unlimited",
        "quiz_types": ["chapter", "module", "practice"],
        "features": ["progress_tracking", "all_achievements", "streaks", "certificates"]
    },
    "pro": {
        "chapters": "all",
        "modules": [1, 2, 3],
        "quiz_attempts_per_quiz": "unlimited",
        "quiz_types": ["chapter", "module", "practice", "adaptive"],
        "features": ["progress_tracking", "all_achievements", "streaks", "certificates", "adaptive_learning"]
    },
    "team": {
        "chapters": "all",
        "modules": [1, 2, 3],
        "quiz_attempts_per_quiz": "unlimited",
        "quiz_types": ["chapter", "module", "practice", "adaptive"],
        "features": ["progress_tracking", "all_achievements", "streaks", "certificates", "adaptive_learning", "team_analytics", "admin_dashboard"]
    }
}
```

---

## API Endpoints

### 1. Check Content Access

**Endpoint:** `GET /api/v1/access/check`

**Purpose:** Verify if user can access specific content

**Query Parameters:**
- `content_type` (string, required): Type of content
  - `chapter`, `quiz`, `module`, `feature`
- `content_id` (string, required): Identifier of the content
- `user_id` (string, optional): User to check (defaults to authenticated user)

**Request Example:**
```http
GET /api/v1/access/check?content_type=chapter&content_id=ch4-skill-md-structure
Authorization: Bearer <user_token>
```

**Response 200 (Access Granted):**
```json
{
  "access": true,
  "content_type": "chapter",
  "content_id": "ch4-skill-md-structure",
  "user_tier": "premium",
  "reason": "subscription_active"
}
```

**Response 200 (Access Denied):**
```json
{
  "access": false,
  "content_type": "chapter",
  "content_id": "ch4-skill-md-structure",
  "user_tier": "free",
  "reason": "premium_required",
  "required_tier": "premium",
  "upgrade_options": {
    "premium": {
      "price": "$9.99/month",
      "url": "/api/v1/pricing/premium"
    },
    "pro": {
      "price": "$19.99/month",
      "url": "/api/v1/pricing/pro"
    }
  },
  "message": "Upgrade to Premium to access Module 2 content"
}
```

---

### 2. Get User Subscription

**Endpoint:** `GET /api/v1/subscriptions/{user_id}`

**Purpose:** Get current subscription details for a user

**Path Parameters:**
- `user_id` (string, required): User identifier

**Request Example:**
```http
GET /api/v1/subscriptions/user-123
Authorization: Bearer <user_token>
```

**Response 200 (Active Subscription):**
```json
{
  "user_id": "user-123",
  "subscription": {
    "tier": "premium",
    "status": "active",
    "started_at": "2026-01-01T00:00:00Z",
    "current_period_start": "2026-01-01T00:00:00Z",
    "current_period_end": "2026-02-01T00:00:00Z",
    "cancel_at_period_end": false,
    "payment_method": "card_ending_4242"
  },
  "access": {
    "chapters": ["ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "ch7", "ch8", "ch9"],
    "modules": [1, 2, 3],
    "features": ["progress_tracking", "all_achievements", "streaks", "certificates"]
  },
  "usage": {
    "chapters_accessed": 4,
    "quizzes_completed": 3,
    "total_time_minutes": 180
  }
}
```

**Response 200 (Free Tier):**
```json
{
  "user_id": "user-456",
  "subscription": {
    "tier": "free",
    "status": "active",
    "started_at": "2026-01-10T00:00:00Z"
  },
  "access": {
    "chapters": ["ch1-intro-to-agents", "ch2-claude-agent-sdk", "ch3-mcp-integration"],
    "modules": [1],
    "features": ["progress_tracking", "basic_achievements"]
  },
  "upgrade_prompt": {
    "message": "Upgrade to Premium to unlock all 9 chapters",
    "savings": "Complete Module 1 to get 20% off Premium",
    "url": "/api/v1/pricing"
  }
}
```

---

### 3. Create/Update Subscription

**Endpoint:** `POST /api/v1/subscriptions`

**Purpose:** Create or upgrade a subscription (webhook from payment provider)

**Request Body:**
```json
{
  "user_id": "user-123",
  "tier": "premium",
  "payment_id": "pay_abc123",
  "payment_provider": "stripe",
  "period_months": 1
}
```

**Request Example:**
```http
POST /api/v1/subscriptions
Authorization: Bearer <webhook_secret>
Content-Type: application/json

{
  "user_id": "user-123",
  "tier": "premium",
  "payment_id": "pay_abc123",
  "payment_provider": "stripe",
  "period_months": 1
}
```

**Response 201 (Created):**
```json
{
  "subscription_id": "sub_xyz789",
  "user_id": "user-123",
  "tier": "premium",
  "status": "active",
  "started_at": "2026-01-15T10:30:00Z",
  "current_period_end": "2026-02-15T10:30:00Z",
  "access_granted": {
    "new_chapters": ["ch4", "ch5", "ch6", "ch7", "ch8", "ch9"],
    "new_features": ["all_achievements", "streaks", "certificates"]
  }
}
```

**Response 200 (Upgraded):**
```json
{
  "subscription_id": "sub_xyz789",
  "user_id": "user-123",
  "previous_tier": "premium",
  "new_tier": "pro",
  "status": "active",
  "upgraded_at": "2026-01-15T10:30:00Z",
  "prorated_amount": "$5.00",
  "access_granted": {
    "new_features": ["adaptive_learning"]
  }
}
```

---

### 4. Cancel Subscription

**Endpoint:** `DELETE /api/v1/subscriptions/{subscription_id}`

**Purpose:** Cancel a subscription (takes effect at period end)

**Path Parameters:**
- `subscription_id` (string, required): Subscription to cancel

**Query Parameters:**
- `immediate` (boolean, optional): Cancel immediately (default: false)
- `reason` (string, optional): Cancellation reason

**Request Example:**
```http
DELETE /api/v1/subscriptions/sub_xyz789?reason=too_expensive
Authorization: Bearer <user_token>
```

**Response 200 (Scheduled Cancellation):**
```json
{
  "subscription_id": "sub_xyz789",
  "status": "active",
  "cancel_at_period_end": true,
  "access_until": "2026-02-15T10:30:00Z",
  "message": "Your subscription will remain active until February 15, 2026",
  "reactivate_url": "/api/v1/subscriptions/sub_xyz789/reactivate"
}
```

**Response 200 (Immediate Cancellation):**
```json
{
  "subscription_id": "sub_xyz789",
  "status": "cancelled",
  "cancelled_at": "2026-01-15T10:30:00Z",
  "tier_downgraded_to": "free",
  "refund_amount": "$5.00",
  "message": "Your subscription has been cancelled. You've been downgraded to the free tier."
}
```

---

### 5. Get Pricing Plans

**Endpoint:** `GET /api/v1/pricing`

**Purpose:** Get available pricing plans with features comparison

**Query Parameters:**
- `promo_code` (string, optional): Apply promotional discount

**Request Example:**
```http
GET /api/v1/pricing?promo_code=LAUNCH20
Authorization: Bearer <user_token>
```

**Response 200:**
```json
{
  "plans": [
    {
      "tier": "free",
      "name": "Free",
      "price": {
        "amount": 0,
        "currency": "USD",
        "interval": null
      },
      "features": {
        "chapters": "3 chapters (Module 1)",
        "quizzes": "Basic quizzes (3 attempts each)",
        "progress": "Basic progress tracking",
        "achievements": "5 basic achievements",
        "support": "Community support"
      },
      "limitations": {
        "no_certificates": true,
        "no_streaks": true,
        "no_advanced_quizzes": true
      }
    },
    {
      "tier": "premium",
      "name": "Premium",
      "price": {
        "amount": 9.99,
        "currency": "USD",
        "interval": "month",
        "original_amount": 9.99,
        "discount_percent": 20,
        "discounted_amount": 7.99,
        "promo_code": "LAUNCH20"
      },
      "features": {
        "chapters": "All 9 chapters (3 modules)",
        "quizzes": "All quizzes (unlimited attempts)",
        "progress": "Full progress tracking",
        "achievements": "All 15 achievements",
        "streaks": "Learning streaks with freeze",
        "certificates": "Completion certificate",
        "support": "Email support"
      },
      "popular": true,
      "cta": "Start Learning"
    },
    {
      "tier": "pro",
      "name": "Pro",
      "price": {
        "amount": 19.99,
        "currency": "USD",
        "interval": "month"
      },
      "features": {
        "everything_in_premium": true,
        "adaptive_learning": "AI-powered learning paths (Phase 2)",
        "advanced_assessments": "LLM-graded free-text answers (Phase 2)",
        "priority_support": "Priority email support"
      },
      "badge": "Coming Soon"
    },
    {
      "tier": "team",
      "name": "Team",
      "price": {
        "amount": 49.99,
        "currency": "USD",
        "interval": "month",
        "per_seat": true,
        "minimum_seats": 5
      },
      "features": {
        "everything_in_pro": true,
        "team_management": "Add/remove team members",
        "analytics_dashboard": "Team learning analytics",
        "bulk_enrollment": "Bulk course enrollment",
        "dedicated_support": "Dedicated account manager"
      },
      "badge": "Coming Soon"
    }
  ],
  "promo_applied": {
    "code": "LAUNCH20",
    "discount_percent": 20,
    "valid_until": "2026-02-01T00:00:00Z",
    "applicable_tiers": ["premium"]
  },
  "currency": "USD",
  "tax_info": "Prices exclude applicable taxes"
}
```

---

### 6. Apply Promo Code

**Endpoint:** `POST /api/v1/pricing/promo`

**Purpose:** Validate and apply a promotional code

**Request Body:**
```json
{
  "promo_code": "LAUNCH20",
  "tier": "premium"
}
```

**Response 200 (Valid):**
```json
{
  "valid": true,
  "promo_code": "LAUNCH20",
  "discount_type": "percentage",
  "discount_value": 20,
  "applicable_tiers": ["premium"],
  "valid_until": "2026-02-01T00:00:00Z",
  "original_price": 9.99,
  "discounted_price": 7.99,
  "savings": 2.00
}
```

**Response 200 (Invalid):**
```json
{
  "valid": false,
  "promo_code": "EXPIRED123",
  "reason": "promo_expired",
  "message": "This promotional code has expired"
}
```

---

### 7. Get Access Summary

**Endpoint:** `GET /api/v1/access/summary`

**Purpose:** Get comprehensive access summary for current user

**Request Example:**
```http
GET /api/v1/access/summary
Authorization: Bearer <user_token>
```

**Response 200:**
```json
{
  "user_id": "user-123",
  "tier": "free",
  "access_summary": {
    "chapters": {
      "accessible": 3,
      "locked": 6,
      "total": 9,
      "list": [
        {"id": "ch1-intro-to-agents", "accessible": true},
        {"id": "ch2-claude-agent-sdk", "accessible": true},
        {"id": "ch3-mcp-integration", "accessible": true},
        {"id": "ch4-skill-md-structure", "accessible": false, "required_tier": "premium"},
        {"id": "ch5-procedural-knowledge", "accessible": false, "required_tier": "premium"},
        {"id": "ch6-runtime-skills", "accessible": false, "required_tier": "premium"},
        {"id": "ch7-orchestration-patterns", "accessible": false, "required_tier": "premium"},
        {"id": "ch8-multi-agent-systems", "accessible": false, "required_tier": "premium"},
        {"id": "ch9-production-deployment", "accessible": false, "required_tier": "premium"}
      ]
    },
    "modules": {
      "accessible": 1,
      "locked": 2,
      "total": 3
    },
    "quizzes": {
      "accessible_types": ["chapter", "practice"],
      "locked_types": ["module", "adaptive"],
      "attempts_per_quiz": 3
    },
    "features": {
      "enabled": ["progress_tracking", "basic_achievements"],
      "locked": ["all_achievements", "streaks", "certificates", "adaptive_learning"]
    }
  },
  "upgrade_benefits": {
    "premium": {
      "price": "$9.99/month",
      "unlocks": [
        "6 additional chapters",
        "2 additional modules",
        "Unlimited quiz attempts",
        "10 more achievements",
        "Learning streaks",
        "Completion certificate"
      ]
    }
  },
  "special_offers": [
    {
      "type": "module_completion",
      "message": "Complete Module 1 to unlock 20% off Premium!",
      "progress": 67,
      "promo_code_on_completion": "MODULE1COMPLETE"
    }
  ]
}
```

---

## Database Schema

```sql
-- User subscriptions
CREATE TABLE user_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL UNIQUE,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('free', 'premium', 'pro', 'team')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'cancelled', 'past_due', 'trialing')),

    -- Billing info
    payment_provider VARCHAR(50),  -- 'stripe', 'paypal', etc.
    payment_id VARCHAR(100),
    payment_method VARCHAR(50),

    -- Period tracking
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    current_period_start TIMESTAMP NOT NULL DEFAULT NOW(),
    current_period_end TIMESTAMP,
    trial_end TIMESTAMP,

    -- Cancellation
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Subscription history for audit
CREATE TABLE subscription_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id UUID REFERENCES user_subscriptions(subscription_id),
    user_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,  -- 'created', 'upgraded', 'downgraded', 'cancelled', 'reactivated'
    previous_tier VARCHAR(20),
    new_tier VARCHAR(20),
    event_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Promotional codes
CREATE TABLE promo_codes (
    code VARCHAR(50) PRIMARY KEY,
    discount_type VARCHAR(20) NOT NULL CHECK (discount_type IN ('percentage', 'fixed')),
    discount_value DECIMAL(10, 2) NOT NULL,
    applicable_tiers VARCHAR(20)[] NOT NULL,
    max_uses INTEGER,
    current_uses INTEGER DEFAULT 0,
    valid_from TIMESTAMP DEFAULT NOW(),
    valid_until TIMESTAMP,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Promo code usage tracking
CREATE TABLE promo_code_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    promo_code VARCHAR(50) REFERENCES promo_codes(code),
    user_id VARCHAR(100) NOT NULL,
    subscription_id UUID REFERENCES user_subscriptions(subscription_id),
    discount_amount DECIMAL(10, 2),
    used_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(promo_code, user_id)  -- Each user can use a code once
);

-- Content access cache (for fast lookups)
CREATE TABLE user_content_access (
    user_id VARCHAR(100) NOT NULL,
    content_type VARCHAR(20) NOT NULL,  -- 'chapter', 'module', 'feature'
    content_id VARCHAR(100) NOT NULL,
    has_access BOOLEAN NOT NULL,
    reason VARCHAR(50),
    cached_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_id, content_type, content_id)
);

-- Indexes
CREATE INDEX idx_subscriptions_user ON user_subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON user_subscriptions(status);
CREATE INDEX idx_subscription_history_user ON subscription_history(user_id, created_at);
CREATE INDEX idx_promo_codes_valid ON promo_codes(valid_until) WHERE valid_until IS NOT NULL;
CREATE INDEX idx_content_access_user ON user_content_access(user_id);
```

---

## Implementation Requirements

### FastAPI Implementation Pattern

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, Literal, List
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter(prefix="/api/v1")

class SubscriptionTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PRO = "pro"
    TEAM = "team"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


# Hardcoded access rules (Constitutional Compliance)
ACCESS_RULES = {
    "free": {
        "chapters": ["ch1-intro-to-agents", "ch2-claude-agent-sdk", "ch3-mcp-integration"],
        "modules": [1],
        "quiz_attempts": 3,
        "features": ["progress_tracking", "basic_achievements"]
    },
    "premium": {
        "chapters": "all",
        "modules": [1, 2, 3],
        "quiz_attempts": None,  # Unlimited
        "features": ["progress_tracking", "all_achievements", "streaks", "certificates"]
    },
    "pro": {
        "chapters": "all",
        "modules": [1, 2, 3],
        "quiz_attempts": None,
        "features": ["progress_tracking", "all_achievements", "streaks", "certificates", "adaptive_learning"]
    },
    "team": {
        "chapters": "all",
        "modules": [1, 2, 3],
        "quiz_attempts": None,
        "features": ["progress_tracking", "all_achievements", "streaks", "certificates", "adaptive_learning", "team_analytics"]
    }
}

ALL_CHAPTERS = [
    "ch1-intro-to-agents", "ch2-claude-agent-sdk", "ch3-mcp-integration",
    "ch4-skill-md-structure", "ch5-procedural-knowledge", "ch6-runtime-skills",
    "ch7-orchestration-patterns", "ch8-multi-agent-systems", "ch9-production-deployment"
]


def get_tier_chapters(tier: str) -> List[str]:
    """Get accessible chapters for a tier."""
    rules = ACCESS_RULES.get(tier, ACCESS_RULES["free"])
    if rules["chapters"] == "all":
        return ALL_CHAPTERS
    return rules["chapters"]


def get_tier_features(tier: str) -> List[str]:
    """Get accessible features for a tier."""
    return ACCESS_RULES.get(tier, ACCESS_RULES["free"])["features"]


@router.get("/access/check")
async def check_access(
    content_type: Literal["chapter", "quiz", "module", "feature"],
    content_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Check if user can access specific content.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Rule-based access check (if/else)
    - ✅ Database tier lookup
    - ❌ NO LLM-based access decisions
    - ❌ NO AI personalization
    """
    # Get user subscription
    subscription = await db.fetchrow(
        "SELECT tier, status FROM user_subscriptions WHERE user_id = $1",
        user["id"]
    )

    tier = subscription["tier"] if subscription else "free"
    status = subscription["status"] if subscription else "active"

    # Check if subscription is active
    if status not in ("active", "trialing"):
        tier = "free"  # Downgrade to free if not active

    # Determine access based on content type
    has_access = False
    reason = "unknown"
    required_tier = None

    if content_type == "chapter":
        accessible_chapters = get_tier_chapters(tier)
        has_access = content_id in accessible_chapters

        if not has_access:
            reason = "premium_required"
            required_tier = "premium"

    elif content_type == "module":
        accessible_modules = ACCESS_RULES[tier]["modules"]
        module_id = int(content_id)
        has_access = module_id in accessible_modules

        if not has_access:
            reason = "premium_required"
            required_tier = "premium"

    elif content_type == "feature":
        accessible_features = get_tier_features(tier)
        has_access = content_id in accessible_features

        if not has_access:
            # Determine minimum tier for feature
            for check_tier in ["premium", "pro", "team"]:
                if content_id in ACCESS_RULES[check_tier]["features"]:
                    required_tier = check_tier
                    break
            reason = f"{required_tier}_required" if required_tier else "not_available"

    elif content_type == "quiz":
        # Quizzes are tied to chapters
        quiz = await db.fetchrow(
            "SELECT chapter_id FROM quizzes WHERE quiz_id = $1",
            content_id
        )
        if quiz:
            accessible_chapters = get_tier_chapters(tier)
            has_access = quiz["chapter_id"] in accessible_chapters

    if has_access:
        reason = "subscription_active" if tier != "free" else "free_tier"

    response = {
        "access": has_access,
        "content_type": content_type,
        "content_id": content_id,
        "user_tier": tier,
        "reason": reason
    }

    if not has_access and required_tier:
        response["required_tier"] = required_tier
        response["upgrade_options"] = {
            "premium": {"price": "$9.99/month", "url": "/api/v1/pricing/premium"},
            "pro": {"price": "$19.99/month", "url": "/api/v1/pricing/pro"}
        }
        response["message"] = f"Upgrade to {required_tier.capitalize()} to access this content"

    return response


@router.get("/subscriptions/{user_id}")
async def get_subscription(
    user_id: str,
    user: dict = Depends(get_current_user)
):
    """
    Get user's subscription details.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database lookup
    - ✅ Rule-based access calculation
    - ❌ NO LLM involvement
    """
    # Verify user can access this data
    if user["id"] != user_id and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    subscription = await db.fetchrow(
        """
        SELECT * FROM user_subscriptions WHERE user_id = $1
        """,
        user_id
    )

    tier = subscription["tier"] if subscription else "free"

    # Get usage stats
    usage = await db.fetchrow(
        """
        SELECT
            COUNT(DISTINCT chapter_id) as chapters_accessed,
            COUNT(DISTINCT qa.quiz_id) as quizzes_completed,
            COALESCE(SUM(ls.duration_minutes), 0) as total_time_minutes
        FROM chapter_progress cp
        LEFT JOIN quiz_attempts qa ON qa.user_id = cp.user_id AND qa.submitted_at IS NOT NULL
        LEFT JOIN learning_sessions ls ON ls.user_id = cp.user_id
        WHERE cp.user_id = $1
        """,
        user_id
    )

    response = {
        "user_id": user_id,
        "subscription": {
            "tier": tier,
            "status": subscription["status"] if subscription else "active",
            "started_at": subscription["started_at"].isoformat() if subscription else None,
            "current_period_start": subscription["current_period_start"].isoformat() if subscription and subscription["current_period_start"] else None,
            "current_period_end": subscription["current_period_end"].isoformat() if subscription and subscription["current_period_end"] else None,
            "cancel_at_period_end": subscription["cancel_at_period_end"] if subscription else False
        } if subscription else {"tier": "free", "status": "active"},
        "access": {
            "chapters": get_tier_chapters(tier),
            "modules": ACCESS_RULES[tier]["modules"],
            "features": get_tier_features(tier)
        },
        "usage": {
            "chapters_accessed": usage["chapters_accessed"] or 0,
            "quizzes_completed": usage["quizzes_completed"] or 0,
            "total_time_minutes": usage["total_time_minutes"] or 0
        }
    }

    # Add upgrade prompt for free users
    if tier == "free":
        response["upgrade_prompt"] = {
            "message": "Upgrade to Premium to unlock all 9 chapters",
            "url": "/api/v1/pricing"
        }

    return response


@router.post("/subscriptions")
async def create_subscription(
    subscription: dict,
    webhook_auth: dict = Depends(verify_webhook_signature)
):
    """
    Create or update subscription (webhook from payment provider).

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database operations only
    - ✅ Deterministic tier assignment
    - ❌ NO LLM processing
    """
    user_id = subscription["user_id"]
    tier = subscription["tier"]
    payment_id = subscription.get("payment_id")
    period_months = subscription.get("period_months", 1)

    # Check for existing subscription
    existing = await db.fetchrow(
        "SELECT subscription_id, tier FROM user_subscriptions WHERE user_id = $1",
        user_id
    )

    period_end = datetime.utcnow() + timedelta(days=30 * period_months)

    if existing:
        # Upgrade/downgrade existing subscription
        previous_tier = existing["tier"]

        await db.execute(
            """
            UPDATE user_subscriptions
            SET tier = $1, status = 'active', payment_id = $2,
                current_period_start = NOW(), current_period_end = $3,
                cancel_at_period_end = FALSE, updated_at = NOW()
            WHERE user_id = $4
            """,
            tier, payment_id, period_end, user_id
        )

        # Log history
        await db.execute(
            """
            INSERT INTO subscription_history
            (subscription_id, user_id, event_type, previous_tier, new_tier)
            VALUES ($1, $2, 'upgraded', $3, $4)
            """,
            existing["subscription_id"], user_id, previous_tier, tier
        )

        return {
            "subscription_id": str(existing["subscription_id"]),
            "user_id": user_id,
            "previous_tier": previous_tier,
            "new_tier": tier,
            "status": "active",
            "upgraded_at": datetime.utcnow().isoformat()
        }

    else:
        # Create new subscription
        subscription_id = await db.fetchval(
            """
            INSERT INTO user_subscriptions
            (user_id, tier, status, payment_provider, payment_id, current_period_end)
            VALUES ($1, $2, 'active', $3, $4, $5)
            RETURNING subscription_id
            """,
            user_id, tier, subscription.get("payment_provider", "stripe"),
            payment_id, period_end
        )

        # Log history
        await db.execute(
            """
            INSERT INTO subscription_history
            (subscription_id, user_id, event_type, new_tier)
            VALUES ($1, $2, 'created', $3)
            """,
            subscription_id, user_id, tier
        )

        # Calculate newly unlocked content
        new_chapters = [ch for ch in ALL_CHAPTERS if ch not in ACCESS_RULES["free"]["chapters"]]

        return {
            "subscription_id": str(subscription_id),
            "user_id": user_id,
            "tier": tier,
            "status": "active",
            "started_at": datetime.utcnow().isoformat(),
            "current_period_end": period_end.isoformat(),
            "access_granted": {
                "new_chapters": new_chapters if tier != "free" else [],
                "new_features": [f for f in get_tier_features(tier) if f not in get_tier_features("free")]
            }
        }


@router.delete("/subscriptions/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    immediate: bool = False,
    reason: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """
    Cancel a subscription.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database operations
    - ✅ Deterministic status change
    - ❌ NO LLM retention offers
    """
    subscription = await db.fetchrow(
        "SELECT * FROM user_subscriptions WHERE subscription_id = $1",
        subscription_id
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    if subscription["user_id"] != user["id"] and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")

    if immediate:
        # Immediate cancellation
        await db.execute(
            """
            UPDATE user_subscriptions
            SET status = 'cancelled', cancelled_at = NOW(),
                cancellation_reason = $1, tier = 'free', updated_at = NOW()
            WHERE subscription_id = $2
            """,
            reason, subscription_id
        )

        # Log history
        await db.execute(
            """
            INSERT INTO subscription_history
            (subscription_id, user_id, event_type, previous_tier, new_tier, event_data)
            VALUES ($1, $2, 'cancelled', $3, 'free', $4)
            """,
            subscription_id, subscription["user_id"], subscription["tier"],
            {"reason": reason, "immediate": True}
        )

        return {
            "subscription_id": subscription_id,
            "status": "cancelled",
            "cancelled_at": datetime.utcnow().isoformat(),
            "tier_downgraded_to": "free",
            "message": "Your subscription has been cancelled. You've been downgraded to the free tier."
        }

    else:
        # Cancel at period end
        await db.execute(
            """
            UPDATE user_subscriptions
            SET cancel_at_period_end = TRUE, cancellation_reason = $1, updated_at = NOW()
            WHERE subscription_id = $2
            """,
            reason, subscription_id
        )

        return {
            "subscription_id": subscription_id,
            "status": "active",
            "cancel_at_period_end": True,
            "access_until": subscription["current_period_end"].isoformat(),
            "message": f"Your subscription will remain active until {subscription['current_period_end'].strftime('%B %d, %Y')}",
            "reactivate_url": f"/api/v1/subscriptions/{subscription_id}/reactivate"
        }


@router.get("/pricing")
async def get_pricing(
    promo_code: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """
    Get available pricing plans.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Hardcoded pricing data
    - ✅ Database promo lookup
    - ❌ NO dynamic AI pricing
    """
    plans = [
        {
            "tier": "free",
            "name": "Free",
            "price": {"amount": 0, "currency": "USD", "interval": None},
            "features": {
                "chapters": "3 chapters (Module 1)",
                "quizzes": "Basic quizzes (3 attempts each)",
                "progress": "Basic progress tracking",
                "achievements": "5 basic achievements",
                "support": "Community support"
            },
            "limitations": {
                "no_certificates": True,
                "no_streaks": True,
                "no_advanced_quizzes": True
            }
        },
        {
            "tier": "premium",
            "name": "Premium",
            "price": {"amount": 9.99, "currency": "USD", "interval": "month"},
            "features": {
                "chapters": "All 9 chapters (3 modules)",
                "quizzes": "All quizzes (unlimited attempts)",
                "progress": "Full progress tracking",
                "achievements": "All 15 achievements",
                "streaks": "Learning streaks with freeze",
                "certificates": "Completion certificate",
                "support": "Email support"
            },
            "popular": True,
            "cta": "Start Learning"
        },
        {
            "tier": "pro",
            "name": "Pro",
            "price": {"amount": 19.99, "currency": "USD", "interval": "month"},
            "features": {
                "everything_in_premium": True,
                "adaptive_learning": "AI-powered learning paths (Phase 2)",
                "advanced_assessments": "LLM-graded free-text answers (Phase 2)",
                "priority_support": "Priority email support"
            },
            "badge": "Coming Soon"
        },
        {
            "tier": "team",
            "name": "Team",
            "price": {
                "amount": 49.99,
                "currency": "USD",
                "interval": "month",
                "per_seat": True,
                "minimum_seats": 5
            },
            "features": {
                "everything_in_pro": True,
                "team_management": "Add/remove team members",
                "analytics_dashboard": "Team learning analytics",
                "bulk_enrollment": "Bulk course enrollment",
                "dedicated_support": "Dedicated account manager"
            },
            "badge": "Coming Soon"
        }
    ]

    promo_applied = None

    # Apply promo code if provided
    if promo_code:
        promo = await db.fetchrow(
            """
            SELECT * FROM promo_codes
            WHERE code = $1
            AND (valid_until IS NULL OR valid_until > NOW())
            AND (max_uses IS NULL OR current_uses < max_uses)
            """,
            promo_code.upper()
        )

        if promo:
            promo_applied = {
                "code": promo["code"],
                "discount_percent": promo["discount_value"] if promo["discount_type"] == "percentage" else None,
                "discount_amount": promo["discount_value"] if promo["discount_type"] == "fixed" else None,
                "valid_until": promo["valid_until"].isoformat() if promo["valid_until"] else None,
                "applicable_tiers": promo["applicable_tiers"]
            }

            # Apply discount to applicable plans
            for plan in plans:
                if plan["tier"] in promo["applicable_tiers"]:
                    original = plan["price"]["amount"]
                    if promo["discount_type"] == "percentage":
                        discounted = original * (1 - promo["discount_value"] / 100)
                    else:
                        discounted = max(0, original - promo["discount_value"])

                    plan["price"]["original_amount"] = original
                    plan["price"]["discount_percent"] = promo["discount_value"] if promo["discount_type"] == "percentage" else None
                    plan["price"]["discounted_amount"] = round(discounted, 2)
                    plan["price"]["promo_code"] = promo["code"]

    return {
        "plans": plans,
        "promo_applied": promo_applied,
        "currency": "USD",
        "tax_info": "Prices exclude applicable taxes"
    }


@router.post("/pricing/promo")
async def validate_promo_code(
    request: dict,
    user: dict = Depends(get_current_user)
):
    """
    Validate a promotional code.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Database lookup
    - ✅ Rule-based validation
    - ❌ NO AI promo generation
    """
    promo_code = request.get("promo_code", "").upper()
    tier = request.get("tier", "premium")

    promo = await db.fetchrow(
        """
        SELECT * FROM promo_codes
        WHERE code = $1
        """,
        promo_code
    )

    if not promo:
        return {
            "valid": False,
            "promo_code": promo_code,
            "reason": "invalid_code",
            "message": "This promotional code is not valid"
        }

    # Check expiration
    if promo["valid_until"] and promo["valid_until"] < datetime.utcnow():
        return {
            "valid": False,
            "promo_code": promo_code,
            "reason": "promo_expired",
            "message": "This promotional code has expired"
        }

    # Check usage limits
    if promo["max_uses"] and promo["current_uses"] >= promo["max_uses"]:
        return {
            "valid": False,
            "promo_code": promo_code,
            "reason": "usage_limit_reached",
            "message": "This promotional code has reached its usage limit"
        }

    # Check if applicable to tier
    if tier not in promo["applicable_tiers"]:
        return {
            "valid": False,
            "promo_code": promo_code,
            "reason": "tier_not_applicable",
            "message": f"This code is not valid for the {tier} plan",
            "applicable_tiers": promo["applicable_tiers"]
        }

    # Check if user already used this code
    already_used = await db.fetchrow(
        "SELECT * FROM promo_code_usage WHERE promo_code = $1 AND user_id = $2",
        promo_code, user["id"]
    )

    if already_used:
        return {
            "valid": False,
            "promo_code": promo_code,
            "reason": "already_used",
            "message": "You have already used this promotional code"
        }

    # Calculate discount
    tier_prices = {"free": 0, "premium": 9.99, "pro": 19.99, "team": 49.99}
    original_price = tier_prices.get(tier, 9.99)

    if promo["discount_type"] == "percentage":
        discounted_price = original_price * (1 - promo["discount_value"] / 100)
    else:
        discounted_price = max(0, original_price - promo["discount_value"])

    return {
        "valid": True,
        "promo_code": promo_code,
        "discount_type": promo["discount_type"],
        "discount_value": promo["discount_value"],
        "applicable_tiers": promo["applicable_tiers"],
        "valid_until": promo["valid_until"].isoformat() if promo["valid_until"] else None,
        "original_price": original_price,
        "discounted_price": round(discounted_price, 2),
        "savings": round(original_price - discounted_price, 2)
    }


@router.get("/access/summary")
async def get_access_summary(user: dict = Depends(get_current_user)):
    """
    Get comprehensive access summary for current user.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Rule-based access calculation
    - ✅ Database lookups
    - ❌ NO LLM recommendations
    """
    subscription = await db.fetchrow(
        "SELECT tier, status FROM user_subscriptions WHERE user_id = $1",
        user["id"]
    )

    tier = subscription["tier"] if subscription and subscription["status"] == "active" else "free"
    accessible_chapters = get_tier_chapters(tier)
    accessible_features = get_tier_features(tier)

    # Build chapter access list
    chapter_list = []
    for ch in ALL_CHAPTERS:
        chapter_list.append({
            "id": ch,
            "accessible": ch in accessible_chapters,
            "required_tier": None if ch in accessible_chapters else "premium"
        })

    # Calculate progress toward promo unlock
    progress = await db.fetchrow(
        """
        SELECT COUNT(*) as completed
        FROM chapter_progress
        WHERE user_id = $1 AND status = 'completed'
        AND chapter_id IN ('ch1-intro-to-agents', 'ch2-claude-agent-sdk', 'ch3-mcp-integration')
        """,
        user["id"]
    )

    module1_progress = (progress["completed"] / 3) * 100 if progress else 0

    return {
        "user_id": user["id"],
        "tier": tier,
        "access_summary": {
            "chapters": {
                "accessible": len(accessible_chapters),
                "locked": 9 - len(accessible_chapters),
                "total": 9,
                "list": chapter_list
            },
            "modules": {
                "accessible": len(ACCESS_RULES[tier]["modules"]),
                "locked": 3 - len(ACCESS_RULES[tier]["modules"]),
                "total": 3
            },
            "quizzes": {
                "accessible_types": ["chapter", "practice"],
                "locked_types": ["module", "adaptive"] if tier == "free" else ["adaptive"] if tier == "premium" else [],
                "attempts_per_quiz": ACCESS_RULES[tier]["quiz_attempts"]
            },
            "features": {
                "enabled": accessible_features,
                "locked": [f for f in ACCESS_RULES["team"]["features"] if f not in accessible_features]
            }
        },
        "upgrade_benefits": {
            "premium": {
                "price": "$9.99/month",
                "unlocks": [
                    "6 additional chapters",
                    "2 additional modules",
                    "Unlimited quiz attempts",
                    "10 more achievements",
                    "Learning streaks",
                    "Completion certificate"
                ]
            }
        } if tier == "free" else None,
        "special_offers": [
            {
                "type": "module_completion",
                "message": "Complete Module 1 to unlock 20% off Premium!",
                "progress": int(module1_progress),
                "promo_code_on_completion": "MODULE1COMPLETE"
            }
        ] if tier == "free" and module1_progress < 100 else []
    }
```

---

## Performance Requirements

- **Response Time:** < 50ms (p95) for access checks
- **Response Time:** < 100ms (p95) for subscription operations
- **Throughput:** 1000 access checks/second
- **Cache:** Access decisions cached for 5 minutes

---

## Security Requirements

1. **Authentication:** JWT Bearer tokens required for all endpoints
2. **Authorization:**
   - Users can only access their own subscription data
   - Webhook endpoints require signature verification
3. **Rate Limiting:**
   - 60 access checks/minute per user
   - 10 subscription operations/minute per user
4. **Payment Security:**
   - Never store full credit card numbers
   - Webhook signatures must be verified
   - Use idempotency keys for payment operations

---

## Testing Requirements

### Unit Tests

```python
def test_access_check_free_user():
    """Test free user can access Module 1"""
    response = client.get(
        "/api/v1/access/check?content_type=chapter&content_id=ch1-intro-to-agents",
        headers={"Authorization": f"Bearer {free_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["access"] == True

def test_access_check_free_user_premium_content():
    """Test free user denied Premium content"""
    response = client.get(
        "/api/v1/access/check?content_type=chapter&content_id=ch4-skill-md-structure",
        headers={"Authorization": f"Bearer {free_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["access"] == False
    assert response.json()["required_tier"] == "premium"

def test_access_check_premium_user():
    """Test premium user can access all content"""
    response = client.get(
        "/api/v1/access/check?content_type=chapter&content_id=ch9-production-deployment",
        headers={"Authorization": f"Bearer {premium_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["access"] == True

def test_subscription_create():
    """Test subscription creation"""
    response = client.post(
        "/api/v1/subscriptions",
        json={
            "user_id": "test-user",
            "tier": "premium",
            "payment_id": "pay_test123"
        },
        headers={"Authorization": f"Bearer {webhook_token}"}
    )
    assert response.status_code == 201
    assert response.json()["tier"] == "premium"

def test_subscription_cancel():
    """Test subscription cancellation"""
    response = client.delete(
        f"/api/v1/subscriptions/{subscription_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["cancel_at_period_end"] == True

def test_promo_code_valid():
    """Test valid promo code"""
    response = client.post(
        "/api/v1/pricing/promo",
        json={"promo_code": "LAUNCH20", "tier": "premium"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["valid"] == True
    assert response.json()["discounted_price"] == 7.99

def test_promo_code_expired():
    """Test expired promo code"""
    response = client.post(
        "/api/v1/pricing/promo",
        json={"promo_code": "EXPIRED", "tier": "premium"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["valid"] == False
    assert response.json()["reason"] == "promo_expired"

def test_access_summary():
    """Test access summary endpoint"""
    response = client.get(
        "/api/v1/access/summary",
        headers={"Authorization": f"Bearer {free_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["access_summary"]["chapters"]["accessible"] == 3
    assert response.json()["access_summary"]["chapters"]["locked"] == 6
```

### Integration Tests

- Stripe webhook signature verification
- Subscription lifecycle (create → upgrade → cancel → reactivate)
- Promo code usage tracking and limits
- Access cache invalidation on subscription change

---

## Monitoring & Observability

### Metrics to Track
- Conversion rate (free → paid)
- Churn rate
- Promo code usage and effectiveness
- Access denial rate by content
- Subscription status distribution

### Logging
```python
logger.info(
    "access_checked",
    user_id=user_id,
    content_type=content_type,
    content_id=content_id,
    access_granted=has_access,
    user_tier=tier,
    reason=reason
)

logger.info(
    "subscription_changed",
    user_id=user_id,
    event_type=event_type,
    previous_tier=previous_tier,
    new_tier=new_tier
)
```

---

## Cost Analysis

### Per Request Cost
```
Access Check:
- Single database query: ~0.1ms
- Cache hit: 0ms
- Total: Negligible

Subscription Operations:
- 2-3 database queries: ~0.5ms
- Webhook processing: ~5ms
- Total: Negligible

No LLM costs - all operations are database and rule-based.
```

---

## Success Criteria

✅ **Zero-Backend-LLM Compliance:**
- All access decisions are rule-based (if/else)
- No AI-powered pricing or recommendations
- Pure database operations

✅ **Performance:**
- P95 access check < 50ms
- Support 1000 checks/second

✅ **Functionality:**
- All 7 endpoints implemented
- Tier-based access working
- Promo codes functional
- Subscription lifecycle complete

✅ **Security:**
- Webhook signature verification
- User data isolation
- Rate limiting in place

---

**Spec Version:** 1.0
**Last Updated:** January 16, 2026
**Status:** Ready for Implementation
