"""
AutoStream AI Agent – FastAPI Application Entry Point

Run locally:
    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent.graph import AutoStreamAgent
from .api.chat import router as chat_router

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Application lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise heavy resources once at startup."""
    logger.info("Starting AutoStream Agent API …")
    app.state.agent = AutoStreamAgent()
    logger.info("Agent ready ✓")
    yield
    logger.info("Shutting down …")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AutoStream AI Agent API",
    description=(
        "Conversational AI sales agent for AutoStream SaaS. "
        "Combines RAG over a local knowledge base with a LangGraph "
        "state machine for intent classification and lead capture."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────────────────
allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)


# ---------------------------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------------------------

@app.get("/", tags=["root"])
async def root():
    return {
        "service": "AutoStream AI Agent",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
