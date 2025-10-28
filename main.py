"""Main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.shared.config import settings
from app.core.shared.container import container
from app.core.utils.logger import configure_logging, get_logger

# Import routers
from app.features.translation.presentation.controllers.translation_controller import router as translation_router
from app.features.feedback.presentation.controllers.feedback_controller import router as feedback_router
from app.features.admin.presentation.controllers.admin_controller import router as admin_router

# Configure logging
configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        description="Interactive translator for Shuar Chicham language preservation"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(translation_router, prefix="/api/translate", tags=["translation"])
    app.include_router(feedback_router, prefix="/api/feedback", tags=["feedback"])
    app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
    
    # Configure dependency injection
    container.wire(modules=[
        "app.features.translation.presentation.controllers.translation_controller",
        "app.features.feedback.presentation.controllers.feedback_controller",
        "app.features.admin.presentation.controllers.admin_controller",
    ])
    
    logger.info("FastAPI application created", app_name=settings.app_name, version=settings.app_version)
    return app


# Create the application instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "healthy",
        "description": "Interactive translator for Shuar Chicham language preservation"
    }


@app.get("/api/health")
async def health_check():
    """API health check endpoint."""
    try:
        # Test database connection
        supabase_client = container.supabase_client()
        db_status = await supabase_client.health_check()
        
        return {
            "status": "healthy", 
            "message": "Shuar Chicham Translator API is running",
            "version": settings.app_version,
            "database": db_status,
            "features": {
                "translation": "available",
                "feedback": "available", 
                "admin": "available"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "degraded",
            "message": "Some services may be unavailable",
            "version": settings.app_version,
            "error": str(e)
        }


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting Shuar Chicham Translator API")
    
    # Test database connection
    try:
        supabase_client = container.supabase_client()
        connection_ok = await supabase_client.test_connection()
        if connection_ok:
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection failed")
    except Exception as e:
        logger.error("Database connection error", error=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Shuar Chicham Translator API")
    
    # Close database connections
    try:
        supabase_client = container.supabase_client()
        supabase_client.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Error closing database connections", error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )