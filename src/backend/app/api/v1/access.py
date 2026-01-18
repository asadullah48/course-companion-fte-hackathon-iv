"""
Access Control API
Subscription and access management

CONSTITUTIONAL COMPLIANCE:
- ✅ Rule-based access control
- ✅ Tier-based content gating
- ❌ NO LLM-based access decisions
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core import ActiveUser, DbSession, OptionalUser
from app.models.user import User, Subscription, SubscriptionTier
from app.models.content import Chapter, Module

router = APIRouter()


class TierBenefits(BaseModel):
    """Benefits for a subscription tier."""

    modules_accessible: List[str] = Field(..., description="Accessible module IDs")
    chapters_accessible: int = Field(..., description="Number of accessible chapters")
    streak_freezes_per_month: int = Field(..., description="Streak freezes per month")
    quiz_access: bool = Field(..., description="Access to quizzes")
    certificate: bool = Field(..., description="Certificate on completion")


class PricingTier(BaseModel):
    """Pricing tier information."""

    tier: str = Field(..., description="Tier name")
    display_name: str = Field(..., description="Display name")
    price_monthly: float = Field(..., description="Monthly price in USD")
    price_yearly: float = Field(..., description="Yearly price in USD")
    benefits: TierBenefits = Field(..., description="Tier benefits")
    is_current: bool = Field(default=False, description="Whether this is user's current tier")


class PricingResponse(BaseModel):
    """Pricing information response."""

    tiers: List[PricingTier] = Field(..., description="Available pricing tiers")
    current_tier: Optional[str] = Field(None, description="User's current tier")


class AccessCheckResponse(BaseModel):
    """Access check response."""

    allowed: bool = Field(..., description="Whether access is allowed")
    reason: Optional[str] = Field(None, description="Reason if denied")
    required_tier: Optional[str] = Field(None, description="Required tier if denied")
    upgrade_url: str = Field(default="/api/v1/pricing", description="Upgrade URL")


class UserSubscriptionResponse(BaseModel):
    """User subscription details."""

    user_id: str = Field(..., description="User identifier")
    tier: str = Field(..., description="Current tier")
    is_active: bool = Field(..., description="Subscription active status")
    current_period_start: Optional[datetime] = Field(None)
    current_period_end: Optional[datetime] = Field(None)
    streak_freezes_used: int = Field(default=0)
    streak_freezes_remaining: int = Field(default=0)


# Tier definitions
TIER_DEFINITIONS = {
    SubscriptionTier.FREE: {
        "display_name": "Free",
        "price_monthly": 0.0,
        "price_yearly": 0.0,
        "modules": ["mod-1-foundations"],
        "chapters": 3,
        "streak_freezes": 0,
        "quiz_access": False,
        "certificate": False,
    },
    SubscriptionTier.PREMIUM: {
        "display_name": "Premium",
        "price_monthly": 9.99,
        "price_yearly": 99.99,
        "modules": ["mod-1-foundations", "mod-2-skills", "mod-3-workflows"],
        "chapters": 9,
        "streak_freezes": 2,
        "quiz_access": True,
        "certificate": True,
    },
    SubscriptionTier.PRO: {
        "display_name": "Pro",
        "price_monthly": 19.99,
        "price_yearly": 199.99,
        "modules": ["mod-1-foundations", "mod-2-skills", "mod-3-workflows"],
        "chapters": 9,
        "streak_freezes": 5,
        "quiz_access": True,
        "certificate": True,
    },
    SubscriptionTier.TEAM: {
        "display_name": "Team",
        "price_monthly": 49.99,
        "price_yearly": 499.99,
        "modules": ["mod-1-foundations", "mod-2-skills", "mod-3-workflows"],
        "chapters": 9,
        "streak_freezes": 999,
        "quiz_access": True,
        "certificate": True,
    },
}


@router.get("/pricing", response_model=PricingResponse)
async def get_pricing(
    user: OptionalUser = None,
):
    """
    Get pricing tiers and benefits.

    Returns:
        PricingResponse with all tiers and current user's tier
    """
    current_tier = None
    if user:
        current_tier = user.tier.value if user.tier else "free"

    tiers = []
    for tier_enum, definition in TIER_DEFINITIONS.items():
        tiers.append(
            PricingTier(
                tier=tier_enum.value,
                display_name=definition["display_name"],
                price_monthly=definition["price_monthly"],
                price_yearly=definition["price_yearly"],
                benefits=TierBenefits(
                    modules_accessible=definition["modules"],
                    chapters_accessible=definition["chapters"],
                    streak_freezes_per_month=definition["streak_freezes"],
                    quiz_access=definition["quiz_access"],
                    certificate=definition["certificate"],
                ),
                is_current=tier_enum.value == current_tier,
            )
        )

    return PricingResponse(tiers=tiers, current_tier=current_tier)


@router.get("/access/check/chapter/{chapter_id}", response_model=AccessCheckResponse)
async def check_chapter_access(
    chapter_id: str,
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Check if user has access to a chapter.

    CONSTITUTIONAL COMPLIANCE:
    - ✅ Rule-based tier comparison
    - ❌ NO LLM involvement

    Args:
        chapter_id: Chapter to check

    Returns:
        AccessCheckResponse with access status
    """
    # Get chapter
    result = await db.execute(
        select(Chapter)
        .options(selectinload(Chapter.module))
        .where(Chapter.chapter_id == chapter_id)
    )
    chapter = result.scalar_one_or_none()

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "chapter_not_found", "chapter_id": chapter_id},
        )

    user_tier = user.tier if user else SubscriptionTier.FREE

    if chapter.is_accessible_by(user_tier):
        return AccessCheckResponse(
            allowed=True,
            reason=None,
            required_tier=None,
        )
    else:
        return AccessCheckResponse(
            allowed=False,
            reason="Premium subscription required for this chapter",
            required_tier=chapter.get_access_tier(),
        )


@router.get("/access/check/module/{module_id}", response_model=AccessCheckResponse)
async def check_module_access(
    module_id: str,
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Check if user has access to a module.

    Args:
        module_id: Module to check

    Returns:
        AccessCheckResponse with access status
    """
    # Find module
    query = select(Module)
    if module_id.isdigit():
        query = query.where(Module.order == int(module_id))
    else:
        query = query.where(Module.module_id == module_id)

    result = await db.execute(query)
    module = result.scalar_one_or_none()

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "module_not_found", "module_id": module_id},
        )

    user_tier = user.tier if user else SubscriptionTier.FREE

    if module.is_accessible_by(user_tier):
        return AccessCheckResponse(
            allowed=True,
            reason=None,
            required_tier=None,
        )
    else:
        return AccessCheckResponse(
            allowed=False,
            reason="Premium subscription required for this module",
            required_tier=module.access_tier,
        )


@router.get("/access/subscription", response_model=UserSubscriptionResponse)
async def get_subscription(
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Get current user's subscription details.

    Returns:
        UserSubscriptionResponse with subscription info
    """
    subscription = user.subscription

    if subscription is None:
        return UserSubscriptionResponse(
            user_id=user.id,
            tier="free",
            is_active=True,
            current_period_start=None,
            current_period_end=None,
            streak_freezes_used=0,
            streak_freezes_remaining=0,
        )

    return UserSubscriptionResponse(
        user_id=user.id,
        tier=subscription.tier.value,
        is_active=subscription.is_active,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        streak_freezes_used=subscription.streak_freezes_used,
        streak_freezes_remaining=subscription.streak_freezes_remaining,
    )


@router.get("/access/content-map")
async def get_content_access_map(
    user: OptionalUser = None,
    db: DbSession = None,
):
    """
    Get map of all content with access status.

    Returns:
        Map of all modules and chapters with access status
    """
    user_tier = user.tier if user else SubscriptionTier.FREE

    # Get all modules with chapters
    result = await db.execute(
        select(Module)
        .options(selectinload(Module.chapters))
        .order_by(Module.order)
    )
    modules = list(result.scalars())

    content_map = []
    for module in modules:
        module_accessible = module.is_accessible_by(user_tier)

        chapters = []
        for chapter in sorted(module.chapters, key=lambda x: x.order):
            chapter_accessible = chapter.is_accessible_by(user_tier)
            chapters.append({
                "chapter_id": chapter.chapter_id,
                "title": chapter.title,
                "order": chapter.order,
                "accessible": chapter_accessible,
                "required_tier": chapter.get_access_tier() if not chapter_accessible else None,
            })

        content_map.append({
            "module_id": module.module_id,
            "title": module.title,
            "order": module.order,
            "accessible": module_accessible,
            "required_tier": module.access_tier if not module_accessible else None,
            "chapters": chapters,
        })

    return {
        "user_tier": user_tier.value if user_tier else "free",
        "content_map": content_map,
    }


@router.post("/access/use-freeze")
async def use_streak_freeze(
    user: ActiveUser = None,
    db: DbSession = None,
):
    """
    Use a streak freeze to prevent streak loss.

    Returns:
        Updated freeze count
    """
    if user.subscription is None or user.subscription.streak_freezes_remaining <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "no_freezes_available",
                "message": "No streak freezes available",
                "upgrade_url": "/api/v1/pricing",
            },
        )

    user.subscription.streak_freezes_used += 1
    await db.commit()

    return {
        "success": True,
        "freezes_remaining": user.subscription.streak_freezes_remaining,
        "message": "Streak freeze applied successfully",
    }
