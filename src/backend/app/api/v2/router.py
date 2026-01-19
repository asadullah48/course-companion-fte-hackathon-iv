"""
API v2 Router - Adaptive Learning Features (Phase 2)
"""
from fastapi import APIRouter
from .learning import router as learning_router

router = APIRouter(prefix="/v2", tags=["v2-api"])

# Include adaptive learning routes
router.include_router(learning_router)