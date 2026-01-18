"""
FastAPI Dependencies
Common dependencies for route handlers
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.core.auth import verify_token
from app.database import async_session_maker
from app.models.user import User, Subscription

settings = get_settings()

# Security scheme for JWT Bearer tokens
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncSession:
    """
    Dependency for getting database session.

    Yields:
        AsyncSession: Database session
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency for getting the current authenticated user.

    Args:
        credentials: JWT Bearer token from Authorization header
        db: Database session

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: If authentication fails
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    token_payload = verify_token(token)

    if token_payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database with subscription loaded
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(User.id == token_payload.sub)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency for getting the current active user.

    Args:
        current_user: The authenticated user

    Returns:
        User: The active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_optional_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[User]:
    """
    Dependency for getting the current user if authenticated, None otherwise.

    Useful for endpoints that work differently for authenticated vs anonymous users.

    Args:
        credentials: Optional JWT Bearer token
        db: Database session

    Returns:
        User if authenticated, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials
    token_payload = verify_token(token)

    if token_payload is None:
        return None

    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(User.id == token_payload.sub)
    )
    return result.scalar_one_or_none()


def require_subscription_tier(required_tier: str):
    """
    Dependency factory for requiring a minimum subscription tier.

    Args:
        required_tier: Minimum required tier ("free", "premium", "pro", "team")

    Returns:
        Dependency function
    """
    tier_order = {"free": 0, "premium": 1, "pro": 2, "team": 3}

    async def check_tier(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        user_tier = current_user.tier.value if current_user.tier else "free"
        user_tier_level = tier_order.get(user_tier, 0)
        required_tier_level = tier_order.get(required_tier, 0)

        if user_tier_level < required_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "subscription_required",
                    "message": f"This feature requires {required_tier} subscription",
                    "current_tier": user_tier,
                    "required_tier": required_tier,
                    "upgrade_url": "/api/v1/pricing",
                },
            )
        return current_user

    return check_tier


# Type aliases for common dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_current_active_user)]
OptionalUser = Annotated[Optional[User], Depends(get_optional_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
