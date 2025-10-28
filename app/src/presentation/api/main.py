"""API router configuration."""

from fastapi import APIRouter

# Import controllers (will be created in subsequent tasks)
# from src.presentation.api.controllers.translation_controller import router as translation_router
# from src.presentation.api.controllers.feedback_controller import router as feedback_router
# from src.presentation.api.controllers.admin_controller import router as admin_router

api_router = APIRouter()

# Include routers (will be uncommented as controllers are implemented)
# api_router.include_router(translation_router, prefix="/translate", tags=["translation"])
# api_router.include_router(feedback_router, prefix="/feedback", tags=["feedback"])
# api_router.include_router(admin_router, prefix="/admin", tags=["admin"])


@api_router.get("/health")
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "message": "Shuar Chicham Translator API is running"}