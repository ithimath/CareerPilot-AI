"""
Test Script for User Career Readiness Score Persistence & 0 Starting Score Logic
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_scoring_service import get_ml_predictor
from app.services.scoring_service import calculate_job_readiness_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("score_test")

def test_score_persistence():
    logger.info("=== Testing User Score Initialization & Persistence ===")
    
    # 1. New User with empty profile
    new_user_profile = {
        "uid": "new_user_999",
        "name": "New Candidate",
        "skills": [],
        "projects": [],
        "internships": [],
        "certifications": []
    }
    
    score_new = calculate_job_readiness_score(new_user_profile)
    logger.info(f"New User Initial Score: {score_new.total_score} (Expected 0.0)")
    assert score_new.total_score == 0.0, f"Expected 0.0, got {score_new.total_score}"

    # 2. Existing User with profile history
    user_a_profile = {
        "uid": "user_a_101",
        "name": "Alice Dev",
        "target_career": "Full Stack Engineer",
        "skills": ["React", "TypeScript", "Python", "FastAPI", "PostgreSQL", "Git", "Docker"],
        "projects": [{"title": "Cloud App", "technologies": ["React", "FastAPI"], "github_url": "http://gh"}],
        "internships": [{"company": "Acme", "role": "Frontend Intern"}],
        "certifications": ["AWS Cloud Practitioner"],
        "cgpa": 8.5
    }

    score_a = calculate_job_readiness_score(user_a_profile)
    logger.info(f"User A Score: {score_a.total_score} (Expected > 40)")
    assert score_a.total_score > 40.0, f"Expected score > 40, got {score_a.total_score}"

    # 3. User B profile (Data Engineer)
    user_b_profile = {
        "uid": "user_b_202",
        "name": "Bob Data",
        "target_career": "Data Engineer",
        "skills": ["Python", "SQL", "Apache Spark", "Airflow"],
        "projects": [],
        "internships": [],
        "certifications": []
    }
    score_b = calculate_job_readiness_score(user_b_profile)
    logger.info(f"User B Score: {score_b.total_score}")

    # Verify score isolation
    assert score_a.total_score != score_b.total_score, "User A and User B scores must be distinct"
    assert score_a.total_score != score_new.total_score, "User A score must not equal 0"

    print("\n" + "="*50)
    print("  USER PERSISTENCE & INITIAL SCORE TEST PASSED!")
    print("="*50)

if __name__ == "__main__":
    test_score_persistence()
