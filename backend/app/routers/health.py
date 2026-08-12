"""Health check router"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("")
async def health_check():
    return {
        "status": "ok",
        "service": "CareerPilot AI API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }
