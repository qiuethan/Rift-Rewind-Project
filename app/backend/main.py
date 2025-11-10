"""
Rift Rewind API - Main application entry point
FastAPI backend for League of Legends player analytics and champion recommendations
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config.settings import settings
from routes import (
    auth_router,
    players_router,
    matches_router,
    champions_router,
    analytics_router,
    health_router,
    champion_progress_router,
    llm_router,
    tracked_champions_router
)
from middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from utils.logger import logger


# ============================================================================
# APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered League of Legends analytics and champion recommendation system",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# ============================================================================
# ROUTES
# ============================================================================

# Include all routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(players_router)
app.include_router(matches_router)
app.include_router(champions_router)
app.include_router(analytics_router)
app.include_router(champion_progress_router)
app.include_router(llm_router)
app.include_router(tracked_champions_router)


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down application")


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
