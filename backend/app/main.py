"""Main FastAPI application."""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.database import async_engine
from app.models import Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan."""
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize rate limiter
    try:
        redis_instance = redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        await FastAPILimiter.init(redis_instance)
        logging.info("Rate limiter initialized successfully")
    except Exception as e:
        logging.warning(f"Failed to initialize rate limiter: {e}. Running without rate limits.")

    yield

    # Cleanup
    await async_engine.dispose()


app = FastAPI(
    title="Domain Expert RAG Assistant API",
    description="Enterprise-grade RAG system for domain-specific document Q&A",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Welcome to Domain Expert RAG Assistant API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )