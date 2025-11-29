from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.services.ollama_service import ollama_service
from app.services.search_service import search_service
from app.services.langfuse_service import langfuse_service
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Chat App Backend",
        "version": "1.0.0"
    }


@router.get("/database")
def check_database_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check database connectivity."""
    try:
        # Simple query to test database connection
        result = db.execute(text("SELECT 1"))
        result.fetchone()
        
        return {
            "status": "healthy",
            "service": "PostgreSQL Database",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "PostgreSQL Database",
                "error": str(e)
            }
        )


@router.get("/ollama")
async def check_ollama_health() -> Dict[str, Any]:
    """Check Ollama service connectivity."""
    try:
        is_healthy = await ollama_service.health_check()
        
        if is_healthy:
            # Get available models
            models = await ollama_service.list_models()
            return {
                "status": "healthy",
                "service": "Ollama LLM Service",
                "message": "Ollama connection successful",
                "available_models": len(models),
                "default_model": ollama_service.default_model
            }
        else:
            raise Exception("Ollama health check failed")
                
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "Ollama LLM Service",
                "error": str(e)
            }
        )


@router.get("/search")
async def check_search_health() -> Dict[str, Any]:
    """Check Tavily search service connectivity."""
    try:
        is_healthy = await search_service.health_check()
        
        if is_healthy:
            return {
                "status": "healthy",
                "service": "Tavily Search API",
                "message": "Search service connection successful"
            }
        else:
            raise Exception("Search service health check failed")
                
    except Exception as e:
        logger.error(f"Search service health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "Tavily Search API",
                "error": str(e)
            }
        )


@router.get("/langfuse")
async def check_langfuse_health() -> Dict[str, Any]:
    """Check Langfuse service connectivity."""
    try:
        if not langfuse_service.is_enabled():
            return {
                "status": "disabled",
                "service": "Langfuse Tracing",
                "message": "Langfuse is not configured"
            }
        
        is_healthy = await langfuse_service.health_check()
        
        if is_healthy:
            return {
                "status": "healthy",
                "service": "Langfuse Tracing",
                "message": "Langfuse connection successful"
            }
        else:
            raise Exception("Langfuse health check failed")
            
    except Exception as e:
        logger.error(f"Langfuse health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "Langfuse Tracing",
                "error": str(e)
            }
        )


@router.get("/all")
async def check_all_services_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Check health of all services."""
    services = {}
    overall_status = "healthy"
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        services["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        services["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check Ollama
    try:
        is_healthy = await ollama_service.health_check()
        if is_healthy:
            models = await ollama_service.list_models()
            services["ollama"] = {
                "status": "healthy",
                "message": "Ollama connection successful",
                "available_models": len(models)
            }
        else:
            raise Exception("Health check failed")
    except Exception as e:
        services["ollama"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check Search Service
    try:
        is_healthy = await search_service.health_check()
        if is_healthy:
            services["search"] = {
                "status": "healthy",
                "message": "Search service connection successful"
            }
        else:
            raise Exception("Health check failed")
    except Exception as e:
        services["search"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        # Search is optional, don't mark as degraded
    
    # Check Langfuse
    try:
        if langfuse_service.is_enabled():
            is_healthy = await langfuse_service.health_check()
            if is_healthy:
                services["langfuse"] = {
                    "status": "healthy",
                    "message": "Langfuse connection successful"
                }
            else:
                raise Exception("Health check failed")
        else:
            services["langfuse"] = {
                "status": "disabled",
                "message": "Langfuse is not configured"
            }
    except Exception as e:
        services["langfuse"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        # Langfuse is optional, don't mark as degraded
    
    return {
        "status": overall_status,
        "services": services,
        "timestamp": "2025-11-25T22:00:00Z"  # You might want to use actual timestamp
    }
