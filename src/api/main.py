"""
FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import tasks_router, sources_router
from .models import HealthResponse, ErrorResponse
from ..core.config import get_settings
from ..core.task_manager import get_task_manager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting SmartNews Learn API...")
    settings = get_settings()
    settings.ensure_directories()

    # Initialize task manager
    get_task_manager()

    logger.info(f"API running on {settings.api_host}:{settings.api_port}")
    yield

    # Shutdown
    logger.info("Shutting down SmartNews Learn API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="SmartNews Learn API",
        description="""
        AI-Powered News Video Platform for Language Learning.

        ## Features
        - 📺 Multi-source news videos (CNN10, BBC Learning English, VOA, etc.)
        - 🤖 AI-powered subtitle generation with Whisper
        - 🎓 Smart learning modes (repeat, slow-motion, with subtitles)
        - 📊 Task queue management for video processing
        - 🔌 RESTful API for WordPress and third-party integrations

        ## Authentication
        Pass user ID in `X-User-Id` header for user-specific operations.
        """,
        version=settings.app_version,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for your WordPress domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(tasks_router, prefix="/api/v1")
    app.include_router(sources_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check():
        """Check API health status."""
        manager = get_task_manager()
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            pending_tasks=manager.get_pending_tasks_count(),
        )

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """API root - returns basic info."""
        return {
            "name": "CNN Video Timer API",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)},
        )

    return app


# Create app instance
app = create_app()
