"""
Pydantic schemas — shared data models across the application
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


# ── Enums ───────────────────────────────────────────────────────────────────────
class CertificateStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TEXT_EXTRACTED = "text_extracted"
    AI_ANALYZING = "ai_analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class LearningStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ── Skill with Proficiency ──────────────────────────────────────────────────
class SkillProficiency(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class SkillDetail(BaseModel):
    name: str
    level: str = "Intermediate"  # "Beginner" | "Intermediate" | "Advanced" | "Expert"
    verified: bool = False
    source: str = "manual"  # "manual" | "certificate" | "assessment"


# ── Profile ────────────────────────────────────────────────────────────────────
class ProjectItem(BaseModel):
    id: str = ""
    title: str
    description: str = ""
    technologies: List[str] = []
    github_url: str = ""
    live_url: str = ""


class InternshipItem(BaseModel):
    id: str = ""
    company: str
    role: str
    duration: str = ""
    description: str = ""
    start_date: str = ""
    end_date: str = ""


class StudentProfile(BaseModel):
    uid: str
    name: str = ""
    email: str = ""
    college: str = ""
    degree: str = ""
    department: str = ""
    current_year: int = 0
    cgpa: float = 0.0
    skills: List[Union[str, SkillDetail, Dict[str, Any]]] = []
    interests: List[str] = []
    projects: List[ProjectItem] = []
    internships: List[InternshipItem] = []
    certifications: List[Union[str, Dict[str, Any]]] = []
    github_url: str = ""
    linkedin_url: str = ""
    portfolio_url: str = ""
    profile_picture_url: str = ""
    target_career: str = ""
    created_at: Optional[Union[datetime, str]] = None
    updated_at: Optional[Union[datetime, str]] = None

    @field_validator("cgpa")
    @classmethod
    def validate_cgpa(cls, v):
        if v < 0 or v > 10:
            raise ValueError("CGPA must be between 0 and 10")
        return round(v, 2)


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    department: Optional[str] = None
    current_year: Optional[int] = None
    cgpa: Optional[float] = None
    skills: Optional[List[Union[str, Dict[str, Any]]]] = None
    interests: Optional[List[str]] = None
    projects: Optional[List[ProjectItem]] = None
    internships: Optional[List[InternshipItem]] = None
    certifications: Optional[List[Union[str, Dict[str, Any]]]] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    target_career: Optional[str] = None


# ── Activity Records ───────────────────────────────────────────────────────────
class InterviewSessionRecord(BaseModel):
    id: str = ""
    session_id: str = ""
    role: str = "Software Engineer"
    category: str = "technical"
    overall_score: float = 0.0
    clarity: float = 0.0
    technical_accuracy: float = 0.0
    feedback: str = ""
    questions_count: int = 1
    timestamp: str = ""


class AssessmentRecord(BaseModel):
    id: str = ""
    test_id: str = ""
    test_title: str = ""
    category: str = "Technical"
    score: float = 0.0
    total_questions: int = 0
    correct_count: int = 0
    timestamp: str = ""


class ResumeAuditRecord(BaseModel):
    id: str = ""
    target_role: str = "Software Engineer"
    ats_score: float = 0.0
    breakdown: Dict[str, Any] = {}
    matched_keywords: List[str] = []
    missing_keywords: List[str] = []
    strengths: List[str] = []
    improvements: List[str] = []
    version: int = 1
    timestamp: str = ""


# ── Certificate ────────────────────────────────────────────────────────────────
class CertificateMetadata(BaseModel):
    id: str
    uid: str
    file_name: str
    file_url: str
    storage_path: str
    upload_date: Union[datetime, str]
    status: CertificateStatus = CertificateStatus.UPLOADED
    extracted_text: str = ""
    extracted_skills: Dict[str, List[str]] = {}
    certificate_title: str = ""
    issuing_organization: str = ""
    processing_error: str = ""


class CertificateProcessRequest(BaseModel):
    certificate_id: str
    uid: str
    storage_path: str
    file_name: str


# ── Skills ─────────────────────────────────────────────────────────────────────
class ExtractedSkills(BaseModel):
    certificate_title: str = ""
    issuing_organization: str = ""
    skills: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "programming_languages": [],
            "frameworks": [],
            "libraries": [],
            "databases": [],
            "cloud_platforms": [],
            "developer_tools": [],
            "soft_skills": [],
        }
    )


# ── Job Score & Progression ────────────────────────────────────────────────────
class ScoreHistoryEntry(BaseModel):
    timestamp: str
    total_score: float
    delta: float = 0.0
    reason: str = "Score updated"
    category_breakdown: Dict[str, float] = {}


class FactorAnalysis(BaseModel):
    skills_factor: Dict[str, Any] = {}
    projects_factor: Dict[str, Any] = {}
    interviews_factor: Dict[str, Any] = {}
    resume_factor: Dict[str, Any] = {}
    assessments_factor: Dict[str, Any] = {}
    credentials_factor: Dict[str, Any] = {}


class ScoreBreakdown(BaseModel):
    uid: str = ""
    skills_score: float = 0.0        # Max 25
    projects_score: float = 0.0      # Max 20
    interviews_score: float = 0.0    # Max 20
    resume_score: float = 0.0        # Max 15
    assessments_score: float = 0.0   # Max 10
    certificates_score: float = 0.0  # Max 10
    profile_score: float = 0.0       # (Legacy compatibility mapping)
    internships_score: float = 0.0   # (Legacy compatibility mapping)
    total_score: float = 0.0         # Max 100
    confidence_level: str = "High"   # "High Data Precision" | "Moderate Data Grounding" | "Insufficient Data"
    data_quality_notice: str = ""
    max_scores: Dict[str, int] = {
        "skills": 25,
        "projects": 20,
        "interviews": 20,
        "resume": 15,
        "assessments": 10,
        "certificates": 10,
    }
    factors_breakdown: Optional[Dict[str, Any]] = None
    positive_drivers: List[str] = []
    suggestions: List[str] = []
    history: List[ScoreHistoryEntry] = []
    updated_at: Optional[str] = None


# ── Career ─────────────────────────────────────────────────────────────────────
class CareerRecommendation(BaseModel):
    title: str
    match_percentage: float
    description: str = ""
    required_skills: List[str] = []
    matching_skills: List[str] = []
    missing_skills: List[str] = []
    market_demand: str = ""
    salary_range: str = ""
    reason: str = ""
    category: str = ""


class CareerRecommendationResponse(BaseModel):
    uid: str
    recommendations: List[CareerRecommendation]
    generated_at: datetime


# ── Skill Gap ──────────────────────────────────────────────────────────────────
class SkillGapItem(BaseModel):
    skill: str
    importance: str = "medium"  # low | medium | high | critical
    difficulty: str = "medium"  # easy | medium | hard
    courses: List[Dict[str, str]] = []
    status: str = "missing"  # missing | partial | acquired


class SkillGapReport(BaseModel):
    uid: str
    target_career: str
    matching_skills: List[str] = []
    missing_skills: List[SkillGapItem] = []
    completion_percentage: float = 0.0
    generated_at: datetime


# ── Learning ───────────────────────────────────────────────────────────────────
class LearningItem(BaseModel):
    id: str
    title: str
    description: str = ""
    resource_url: str = ""
    skill: str = ""
    stage: int = 1
    stage_name: str = ""
    status: LearningStatus = LearningStatus.NOT_STARTED
    difficulty: str = "medium"


class LearningRoadmap(BaseModel):
    uid: str
    target_career: str
    stages: Dict[str, List[LearningItem]] = {}
    total_items: int = 0
    completed_items: int = 0
    in_progress_items: int = 0
    progress_percentage: float = 0.0


# ── Chat ───────────────────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    uid: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str


# ── Generic responses ──────────────────────────────────────────────────────────
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    detail: str
