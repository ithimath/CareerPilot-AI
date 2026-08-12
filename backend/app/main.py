"""
CareerPilot AI — FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from app.core.config import settings
from app.core.supabase import init_supabase
from app.routers import (
    auth, profile, certificates, ocr, skills,
    job_score, careers, skill_gap, learning, chat, health,
    resume, interview, company_prep, community, datasets
)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rate limiter ───────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="CareerPilot AI API",
    description="AI-powered career readiness platform for students",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Supabase init ──────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    init_supabase()
    logger.info("Supabase backend initialized successfully")

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(health.router,       prefix="/api/health",       tags=["Health"])
app.include_router(auth.router,         prefix="/api/auth",         tags=["Auth"])
app.include_router(profile.router,      prefix="/api/profile",      tags=["Profile"])
app.include_router(certificates.router, prefix="/api/certificates", tags=["Certificates"])
app.include_router(ocr.router,          prefix="/api/ocr",          tags=["OCR"])
app.include_router(skills.router,       prefix="/api/skills",       tags=["Skills"])
app.include_router(job_score.router,    prefix="/api/job-score",    tags=["Job Score"])
app.include_router(careers.router,      prefix="/api/careers",      tags=["Careers"])
app.include_router(skill_gap.router,    prefix="/api/skill-gap",    tags=["Skill Gap"])
app.include_router(learning.router,     prefix="/api/learning",     tags=["Learning"])
app.include_router(chat.router,         prefix="/api/chat",         tags=["Chat"])
app.include_router(resume.router,       prefix="/api/resume",       tags=["Resume ATS"])
app.include_router(interview.router,    prefix="/api/interview",    tags=["AI Interview"])
app.include_router(company_prep.router, prefix="/api/company-prep", tags=["Company Prep"])
app.include_router(community.router,    prefix="/api/community",    tags=["Community Board"])
app.include_router(datasets.router,     prefix="/api/datasets",     tags=["Dataset Manager"])

# ── Global error handler ───────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )
