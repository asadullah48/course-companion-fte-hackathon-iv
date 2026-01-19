"""
API Router Module
All API endpoints for Course Companion
"""

from fastapi import APIRouter

from app.api.v1 import content, navigation, quiz, progress, search, access
from app.api.v2.router import router as v2_router

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(content.router, prefix="/v1", tags=["Content"])
api_router.include_router(navigation.router, prefix="/v1", tags=["Navigation"])
api_router.include_router(quiz.router, prefix="/v1", tags=["Quiz"])
api_router.include_router(progress.router, prefix="/v1", tags=["Progress"])
api_router.include_router(search.router, prefix="/v1", tags=["Search"])
api_router.include_router(access.router, prefix="/v1", tags=["Access Control"])

# Include v2 adaptive learning router
api_router.include_router(v2_router)
