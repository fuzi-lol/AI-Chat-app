from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth, chat, conversations, health
from app.services.ollama_service import ollama_service
from app.services.search_service import search_service
from app.database import create_tables
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="AI Chat App Backend with Ollama, Tavily Search, and Langfuse integration",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json"
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_v1_prefix)
app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(chat.router, prefix=settings.api_v1_prefix)
app.include_router(conversations.router, prefix=settings.api_v1_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Chat App Backend",
        "version": settings.version,
        "docs_url": "/docs",
        "health_check": f"{settings.api_v1_prefix}/health"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Starting AI Chat App Backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API prefix: {settings.api_v1_prefix}")
    
    # Create database tables if they don't exist
    try:
        create_tables()
        logger.info("Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down AI Chat App Backend...")
    
    # Close HTTP clients
    try:
        await ollama_service.close()
        logger.info("Ollama service client closed")
    except Exception as e:
        logger.error(f"Error closing Ollama service: {e}")
    
    try:
        await search_service.close()
        logger.info("Search service client closed")
    except Exception as e:
        logger.error(f"Error closing Search service: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
