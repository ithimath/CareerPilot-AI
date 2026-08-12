"""
Gemini AI service — skill extraction, career reasoning, chatbot
"""
import google.generativeai as genai
import json
import re
import logging
from typing import Optional
from app.core.config import settings
from app.schemas.models import ExtractedSkills

logger = logging.getLogger(__name__)

# Configure Gemini once on import
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    _model = genai.GenerativeModel("gemini-1.5-flash")
    _chat_model = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=(
            "You are CareerPilot AI Mentor — a professional career advisor for students. "
            "You provide actionable, concise, and encouraging guidance on careers, "
            "interview prep, technical skills, projects, and internships. "
            "When given student profile context, tailor your advice accordingly."
        ),
    )
else:
    _model = None
    _chat_model = None
    logger.warning("GEMINI_API_KEY not set — AI features will be disabled")


def _extract_json(text: str) -> dict:
    """Extract JSON from Gemini response text, even if wrapped in markdown."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try stripping markdown code fences
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    # Try finding first { ... } block
    match = re.search(r"\{[\s\S]+\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    raise ValueError("Could not extract valid JSON from Gemini response")


async def extract_skills_from_text(certificate_text: str) -> ExtractedSkills:
    """
    Send certificate text to Gemini and extract structured skills.
    Returns a validated ExtractedSkills object.
    """
    if not _model:
        raise RuntimeError("Gemini API key not configured")

    prompt = f"""You are an expert at analyzing certificates and extracting skills.

Analyze the following certificate text and extract all relevant information.

CERTIFICATE TEXT:
{certificate_text[:8000]}

Return ONLY a valid JSON object with this exact structure:
{{
  "certificate_title": "exact title of the certificate",
  "issuing_organization": "name of the organization that issued it",
  "skills": {{
    "programming_languages": ["list", "of", "languages"],
    "frameworks": ["list", "of", "frameworks"],
    "libraries": ["list", "of", "libraries"],
    "databases": ["list", "of", "databases"],
    "cloud_platforms": ["list", "of", "platforms"],
    "developer_tools": ["list", "of", "tools"],
    "soft_skills": ["list", "of", "soft", "skills"]
  }}
}}

Rules:
- Only include skills that are explicitly mentioned or strongly implied by the certificate
- Each skill should be a proper noun/name (e.g., "Python", not "python programming")
- If a category has no skills, use an empty array []
- Do not invent skills not evident from the text
- Return ONLY the JSON, no explanation"""

    try:
        response = _model.generate_content(prompt)
        raw = response.text
        data = _extract_json(raw)
        return ExtractedSkills(**data)
    except ValueError as e:
        logger.error(f"JSON extraction failed: {e}")
        return ExtractedSkills()
    except Exception as e:
        logger.error(f"Gemini skill extraction failed: {e}")
        raise


async def generate_career_reasoning(
    student_profile: dict, career_title: str, match_percentage: float
) -> str:
    """Generate a reasoning paragraph for why a career matches the student."""
    if not _model:
        return f"Based on your profile, {career_title} aligns well with your skills and interests."

    prompt = f"""Student profile: {json.dumps(student_profile, indent=2)}
Career: {career_title} (match score: {match_percentage:.0f}%)

Write a 2-3 sentence explanation of why this career is a good fit for this student.
Be specific, mention actual skills they have. Keep it professional and encouraging.
Return ONLY the explanation text, no JSON."""

    try:
        response = _model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Career reasoning failed: {e}")
        return f"{career_title} is a strong match based on your current skill set and interests."


def _get_intelligent_fallback_response(message: str, student_profile: Optional[dict] = None) -> str:
    """Intelligent fallback mentor response generator for quick prompts and general queries."""
    msg_lower = message.lower()
    name = student_profile.get('name', 'Candidate') if student_profile else 'Candidate'
    target = student_profile.get('target_career', 'Full-Stack Engineer') if student_profile else 'Full-Stack Engineer'
    skills = ", ".join(student_profile.get('skills', ['JavaScript', 'Python', 'React', 'SQL'])) if student_profile and student_profile.get('skills') else 'JavaScript, Python, React, SQL'

    # Prompt 1: Full-Stack technical skills
    if 'technical skills' in msg_lower or 'full-stack' in msg_lower or 'stack role' in msg_lower:
        return f"""### Technical Skill Roadmap for {target}

Hello {name}! Based on modern 2026 hiring standards, here is the prioritized technical stack you should master:

1. **Frontend Mastery**:
   - **Modern Frameworks**: React 18+ / Next.js with Server Components, TypeScript, TailwindCSS.
   - **State & Data Fetching**: TanStack Query (React Query) and Zustand for clean state architecture.
   - **Performance**: LCP/INP Core Web Vitals optimization and responsive UI patterns.

2. **Backend & Architecture**:
   - **API Frameworks**: FastAPI (Python) or Node.js (TypeScript/Express/NestJS) for async high-concurrency routes.
   - **Data Layer**: PostgreSQL for relational transactions, Redis for caching and rate-limiting.
   - **Authentication & Security**: OAuth2, JWT with refresh tokens, input validation with Pydantic/Zod.

3. **DevOps & Delivery**:
   - **Containerization**: Docker & Multi-stage builds.
   - **CI/CD & Cloud**: GitHub Actions workflows and deployment to AWS / Vercel.

**Recommended Action**: Verify your skills in your Career Profile to see your updated Market Skill Gap Diagnosis!"""

    # Prompt 2: Resume ATS alignment
    if 'resume' in msg_lower or 'ats' in msg_lower or 'parser' in msg_lower:
        return f"""### Resume ATS Diagnostic Audit

Hello {name}! Here is a strategic review to maximize your ATS (Applicant Tracking System) parser alignment:

1. **Formatting & Structure**:
   - Use a single-column layout without tables, text boxes, or embedded images in section titles.
   - Use standardized headers: `Technical Skills`, `Work Experience`, `Projects`, `Education`, `Certifications`.

2. **Keyword Optimization for {target}**:
   - Explicitly list tech keywords matching target job descriptions (e.g., `{skills}`).
   - Avoid generic terms; use exact names ("TypeScript", "PostgreSQL", "Docker", "REST API").

3. **Impact-Driven Experience Bullet Points (Google XYZ Method)**:
   - *Format*: "Accomplished [X], as measured by [Y], by doing [Z]".
   - *Example*: "Engineered a asynchronous queue processor handling 10k events/sec, reducing API response latency by 35%."

**Pro Tip**: Upload your resume to the **Resume & ATS Diagnostic Scanner** tab to get an immediate keyword density match percentage!"""

    # Prompt 3: System design interview prep
    if 'system design' in msg_lower or 'interview question' in msg_lower:
        return f"""### System Design Interview Preparation Guide

Hello {name}! System design interviews evaluate architectural reasoning and trade-off decisions. Use this 4-step framework:

#### 4-Step System Design Framework:
1. **Scope Requirements & Constraints (5 mins)**:
   - *Functional*: What features are in scope? (e.g., shorten URL, redirect link).
   - *Scale / Non-functional*: DAU, read/write ratio (e.g., 100:1 read heavy), latency targets (<50ms), availability (99.99%).

2. **High-Level Architecture (10 mins)**:
   - Draw client -> Load Balancer (Nginx) -> API Gateway -> App Server Cluster -> Cache (Redis) -> DB (PostgreSQL).

3. **Deep Dive Component Design (15 mins)**:
   - **Data Schema & Key Storage**: Unique base62 hashing algorithm.
   - **Caching Strategy**: Cache-Aside pattern for hot URLs with TTL expiration.
   - **Rate Limiting**: Token Bucket algorithm at gateway layer to block DDoS attacks.

4. **Bottlenecks & Fault Tolerance (10 mins)**:
   - Database read replicas, database sharding by user ID hash, CAP theorem trade-offs.

**Practice Exercise**: Try designing a real-time Notification System or Rate Limiter in the **AI Interview Simulator**!"""

    # Prompt 4: Open source projects for portfolio
    if 'open source' in msg_lower or 'portfolio' in msg_lower or 'projects' in msg_lower:
        return f"""### High-Impact Portfolio Project Ideas for {target}

Hello {name}! Recruiters value production-grade projects with live deployments and clean repository documentation:

1. **Project 1: Real-Time Collaborative Canvas / Editor**
   - *Tech*: React, TypeScript, WebSockets (Socket.io), Node.js, Redis Pub/Sub.
   - *Highlight*: Handles multi-user real-time state synchronization using CRDTs or Operational Transformation.

2. **Project 2: Distributed Job Queue & Task Worker Service**
   - *Tech*: Python (FastAPI), Redis, Docker, PostgreSQL.
   - *Highlight*: Implements retry mechanisms, dead-letter queues, and real-time WebSocket dashboard monitoring.

3. **Project 3: AI-Powered Knowledge Retrieval Engine (RAG)**
   - *Tech*: Next.js, Vector Database (Pinecone/Chroma), Gemini API / OpenAI API.
   - *Highlight*: Semantic search over PDF documents with strict context filtering and source citation.

**Portfolio Rule**: Every project MUST have a clean `README.md` with an architectural diagram, API documentation, and a working live demo link!"""

    # Prompt 5: Audit career readiness matrix
    if 'readiness' in msg_lower or 'matrix' in msg_lower or 'score' in msg_lower:
        return f"""### Comprehensive Career Readiness Matrix Audit

Hello {name}! Here is a breakdown of your dynamic Composite Readiness Index:

- **1. Technical Stack Alignment (30% weight)**: Measures verified skills mapped against current market job postings for {target}.
- **2. Practical Project Portfolio (25% weight)**: Evaluates repository links, commit activity, and deployment complexity.
- **3. Work Experience & Internships (20% weight)**: Assesses documented roles and professional team exposure.
- **4. ATS & Resume Compliance (15% weight)**: Audits keyword density against recruiter parsing standards.
- **5. Verified Credentials (10% weight)**: Validates accredited academic diplomas and industry certifications.

**Actionable Recommendation**: To boost your score tier:
1. Upload missing certificate documents in the **Certificates** tab for OCR extraction.
2. Complete targeted modules in your **Learning Roadmap**!"""

    # General / Custom query fallback
    return f"""### Career Strategy Insight

Hello {name}! Thank you for your question regarding **"{message}"**.

As your AI Career Strategist for **{target}**, here are key steps to guide you:

1. **Strategic Priority**: Align your current technical skills (`{skills}`) with industry demand trends.
2. **Execution Focus**: Build hands-on evidence through production code repositories and verified credentials.
3. **Next Recommended Action**: Explore your **Skill Gap Matrix** or run a practice session in the **AI Interview Simulator**!

Let me know if you would like me to unpack system architecture details, resume keyword optimization, or specific project ideas!"""


async def chat_with_mentor(
    message: str,
    history: list,
    student_profile: Optional[dict] = None,
) -> str:
    """
    Send a message to the AI career mentor with conversation history.
    Returns the mentor's response text with topic-specific intelligence.
    """
    profile_context = ""
    if student_profile:
        profile_context = f"""
Student Profile Context:
- Name: {student_profile.get('name', 'Student')}
- Degree: {student_profile.get('degree', '')} in {student_profile.get('department', '')}
- Current Year: {student_profile.get('current_year', '')}
- Skills: {', '.join(student_profile.get('skills', [])[:20])}
- Target Career: {student_profile.get('target_career', 'Not selected')}
- Interests: {', '.join(student_profile.get('interests', [])[:10])}
"""

    if _chat_model:
        # Build Gemini chat history format
        gemini_history = []
        for msg in history[-20:]:  # last 20 messages for context window
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        try:
            chat = _chat_model.start_chat(history=gemini_history)
            instruction = (
                "Provide a direct, detailed, highly specific, and distinct response tailored to the student's question. "
                "Use markdown formatting with headers, bullet points, and actionable advice. "
                "Do NOT return generic template text."
            )
            full_message = f"{profile_context}\n\n[Instruction: {instruction}]\n\nStudent question: {message}" if profile_context else f"[Instruction: {instruction}]\n\nStudent question: {message}"
            response = chat.send_message(full_message)
            if response and response.text and len(response.text.strip()) > 20:
                return response.text
        except Exception as e:
            logger.warning(f"Gemini chat fallback active due to API notice: {e}")

    # Return high-quality, topic-specific response
    return _get_intelligent_fallback_response(message, student_profile)

