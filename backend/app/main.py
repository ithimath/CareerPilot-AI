"""
CareerPilot AI — FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.core.config import settings
from app.core.supabase import init_supabase
from app.core.firebase import init_firebase
from app.routers import (
    auth, profile, certificates, ocr, skills,
    job_score, careers, skill_gap, learning, chat, health,
    resume, interview, company_prep, community, datasets, assessments
)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Rate limiter ───────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Secure rate limit exceeded response."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}. Please slow down your requests.",
            "type": "rate_limit_exceeded"
        },
        headers={"Retry-After": "60"}
    )


# ── Security Headers Middleware ────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Standard OWASP recommended security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        
        # HSTS only when running over HTTPS or configured
        if settings.ENABLE_HSTS and (request.url.scheme == "https" or settings.is_production):
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            
        return response


# ── App Initialization ─────────────────────────────────────────────────────────
is_docs_enabled = not settings.is_production or settings.ENABLE_DOCS_IN_PROD

app = FastAPI(
    title="CareerPilot AI API",
    description="AI-powered career readiness platform for students",
    version="1.0.0",
    docs_url="/docs" if is_docs_enabled else None,
    redoc_url="/redoc" if is_docs_enabled else None,
    openapi_url="/openapi.json" if is_docs_enabled else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# ── Security Middleware ────────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "Retry-After"],
    max_age=600,
)

# ── Supabase & Firebase init ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    init_supabase()
    init_firebase()
    logger.info(f"CareerPilot AI backend initialized (Environment: {settings.APP_ENV})")

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
app.include_router(assessments.router,  prefix="/api/assessments",  tags=["Assessments"])
app.include_router(community.router,    prefix="/api/community",    tags=["Community Board"])
app.include_router(datasets.router,     prefix="/api/datasets",     tags=["Dataset Manager"])

# ── Global error handler ───────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )

