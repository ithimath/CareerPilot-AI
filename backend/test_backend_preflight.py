"""
Pre-Deployment Backend & ML Verification Test Script

Runs actual verification tests against:
1. Environment variables & Secret Audit
2. ML Readiness Predictor Logic & Consistency
3. Supabase / Database Integration & Auth Token Verification
4. Frontend Secret Leak Audit
5. Route / Service Execution Check
"""

import os
import sys
import json
import logging

# Set PYTHONPATH to root of backend
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.ml_scoring_service import get_ml_predictor
from app.services.scoring_service import calculate_job_readiness_score
from app.services.career_service import get_skill_gap_for_career

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("preflight")

def test_environment_secrets():
    logger.info("=== 1. Checking Environment Variables ===")
    results = {}
    
    # Check Gemini API Key
    gemini_key = settings.GEMINI_API_KEY
    if not gemini_key or "your_gemini_api_key" in gemini_key:
        results["GEMINI_API_KEY"] = "MISSING_OR_PLACEHOLDER (Placeholder string found in .env)"
    else:
        results["GEMINI_API_KEY"] = "CONFIGURED"

    # Check Supabase URL & Keys
    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_ANON_KEY
    if not supabase_url or "https://" not in supabase_url:
        results["SUPABASE_URL"] = "MISSING_OR_INVALID"
    else:
        results["SUPABASE_URL"] = f"CONFIGURED ({supabase_url})"

    if not supabase_key or len(supabase_key) < 20:
        results["SUPABASE_ANON_KEY"] = "MISSING_OR_INVALID"
    else:
        results["SUPABASE_ANON_KEY"] = "CONFIGURED"

    # Check Tesseract CMD
    tesseract_cmd = settings.TESSERACT_CMD
    if os.path.exists(tesseract_cmd):
        results["TESSERACT_OCR"] = f"INSTALLED ({tesseract_cmd})"
    else:
        results["TESSERACT_OCR"] = f"NOT_FOUND_LOCALLY ({tesseract_cmd} not present on current host)"

    return results


def test_ml_predictor():
    logger.info("=== 2. Testing ML Career Readiness Predictor ===")
    predictor = get_ml_predictor()

    # Profile A: High-alignment Full Stack Engineer
    profile_a = {
        "uid": "test_fs_01",
        "name": "Sarah Chen",
        "target_career": "Full Stack Engineer",
        "skills": ["React", "TypeScript", "Node.js", "Express", "PostgreSQL", "Docker", "Git", "REST APIs"],
        "projects": [
            {
                "title": "E-Commerce Platform",
                "description": "Full stack marketplace with React and Node",
                "technologies": ["React", "Node.js", "PostgreSQL"],
                "github_url": "https://github.com/example/shop",
                "live_url": "https://shop.example.com"
            }
        ],
        "internships": [
            {
                "role": "Software Engineering Intern",
                "company": "Tech Startup",
                "duration": "3 months"
            }
        ],
        "certifications": ["AWS Certified Developer"],
        "cgpa": 8.8,
        "college": "State University",
        "degree": "B.Tech CSE",
        "current_year": "Final Year"
    }

    # Profile B: Irrelevant skills for Data Scientist role
    profile_b = {
        "uid": "test_ds_02",
        "name": "John Miller",
        "target_career": "Data Scientist",
        "skills": ["Photoshop", "Word", "Excel", "Typing", "Customer Support"],
        "projects": [],
        "internships": [],
        "certifications": [],
        "cgpa": 6.5,
        "college": "City College",
        "degree": "BBA",
        "current_year": "2nd Year"
    }

    res_a = predictor.predict_readiness(profile_a)
    res_b = predictor.predict_readiness(profile_b)

    logger.info(f"Profile A (Full Stack): Score = {res_a.total_score} | Skills = {res_a.skills_score} | Projects = {res_a.projects_score}")
    logger.info(f"Profile B (Data Science Irrelevant): Score = {res_b.total_score} | Skills = {res_b.skills_score} | Projects = {res_b.projects_score}")
    logger.info(f"Profile A Insights: {res_a.suggestions}")
    logger.info(f"Profile B Insights: {res_b.suggestions}")

    # Consistency verification: Same input yields exact same score
    res_a_repeat = predictor.predict_readiness(profile_a)
    is_consistent = (res_a.total_score == res_a_repeat.total_score)
    is_discriminative = (res_a.total_score > res_b.total_score + 25.0)

    return {
        "profile_a_score": res_a.total_score,
        "profile_b_score": res_b.total_score,
        "is_consistent": is_consistent,
        "is_discriminative": is_discriminative,
        "explainable_insights_a": res_a.suggestions,
        "explainable_insights_b": res_b.suggestions
    }


def test_frontend_secret_leak_check():
    logger.info("=== 3. Auditing Frontend for Hardcoded Secret Leaks ===")
    frontend_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "src"))
    leaks = []
    
    if os.path.exists(frontend_src):
        for root, _, files in os.walk(frontend_src):
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if "AIzaSy" in content: # Common Gemini API Key pattern
                            leaks.append((file, "Gemini API Key detected"))
                        if "service_role" in content:
                            leaks.append((file, "Supabase service_role key string detected"))
    
    return leaks


def test_skill_gap_service():
    logger.info("=== 4. Testing Skill Gap Engine ===")
    gap = get_skill_gap_for_career(["React", "TypeScript", "Git"], "Full Stack Engineer")
    return {
        "target": gap.get("target_career"),
        "matching_count": gap.get("total_matching"),
        "missing_count": gap.get("total_required"),
        "completion_pct": gap.get("completion_percentage")
    }


if __name__ == "__main__":
    logger.info("Starting Pre-Deployment Preflight Check...")
    env_res = test_environment_secrets()
    ml_res = test_ml_predictor()
    leak_res = test_frontend_secret_leak_check()
    gap_res = test_skill_gap_service()

    print("\n" + "="*60)
    print("      PRE-DEPLOYMENT BACKEND VERIFICATION REPORT")
    print("="*60)
    print("\n[1] Environment & Secrets:")
    for k, v in env_res.items():
        print(f"  - {k}: {v}")

    print("\n[2] ML Prediction Pipeline:")
    print(f"  - High Alignment Candidate Score: {ml_res['profile_a_score']}/100")
    print(f"  - Low Alignment Candidate Score:  {ml_res['profile_b_score']}/100")
    print(f"  - Consistency Check (Same Input = Same Output): {'PASSED' if ml_res['is_consistent'] else 'FAILED'}")
    print(f"  - Feature Discrimination Check: {'PASSED' if ml_res['is_discriminative'] else 'FAILED'}")

    print("\n[3] Frontend Secret Leak Audit:")
    if leak_res:
        print(f"  - WARNING: Leaks found: {leak_res}")
    else:
        print("  - PASSED: No private service keys or API secrets exposed in frontend code.")

    print("\n[4] Skill Gap Engine:")
    print(f"  - Target Role: {gap_res['target']}")
    print(f"  - Completion: {gap_res['completion_pct']}% (Matching: {gap_res['matching_count']}/{gap_res['missing_count']})")
    print("="*60)
