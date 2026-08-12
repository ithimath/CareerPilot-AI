"""
Comprehensive ML Accuracy, Edge Case & High-Impact Verification Script

Validates:
1. Empty Account (0 skills, 0 projects) -> Score 0.0, Insufficient Data status
2. Relevant High-Match Candidate -> Factual TF-IDF score, High Data Precision
3. Mismatched Role Target Candidate -> Low score, Factual Gap Explanation
4. Intermediate Candidate -> Moderate score, Factual Gap Explanation
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_scoring_service import get_ml_predictor
from app.services.career_service import generate_career_recommendations, get_skill_gap_for_career

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml_accuracy")

def run_accuracy_edgecase_tests():
    predictor = get_ml_predictor()
    print("\n" + "="*70)
    print("      HIGH-IMPACT ML ACCURACY & EDGE CASE VALIDATION SUITE")
    print("="*70)

    # ── CASE 1: Brand New Empty Profile ────────────────────────────────────────
    p1_empty = {"uid": "p1", "skills": [], "projects": [], "internships": [], "certifications": []}
    res1 = predictor.predict_readiness(p1_empty)
    print(f"\n[Case 1] Empty Profile:")
    print(f"  - Score: {res1.total_score}/100")
    print(f"  - Confidence Level: {res1.confidence_level}")
    print(f"  - Notice: {res1.data_quality_notice}")
    assert res1.total_score == 0.0, "Empty profile score must be 0.0"
    assert res1.confidence_level == "Insufficient Data"

    # ── CASE 2: High Match Full Stack Engineer ─────────────────────────────────
    p2_high = {
        "uid": "p2",
        "name": "David Dev",
        "target_career": "Full Stack Engineer",
        "skills": ["React", "TypeScript", "Python", "FastAPI", "REST APIs", "SQL", "PostgreSQL", "Git", "Docker"],
        "projects": [
            {
                "title": "Cloud Commerce",
                "description": "Microservices platform with React & FastAPI",
                "technologies": ["React", "FastAPI", "PostgreSQL", "Docker"],
                "github_url": "https://github.com/david/shop"
            }
        ],
        "internships": [{"company": "Tech Corp", "role": "Full Stack Intern", "duration": "4 months"}],
        "certifications": ["AWS Developer Certified", "Meta Frontend Developer"],
        "cgpa": 9.1
    }
    res2 = predictor.predict_readiness(p2_high)
    print(f"\n[Case 2] High-Match Candidate (Full Stack):")
    print(f"  - Score: {res2.total_score}/100 (Skills: {res2.skills_score}, Projects: {res2.projects_score})")
    print(f"  - Confidence Level: {res2.confidence_level}")
    print(f"  - Insights: {res2.suggestions}")
    assert res2.total_score >= 55.0, f"High-match profile score should be >= 55.0, got {res2.total_score}"
    assert res2.confidence_level == "High Data Precision"

    # ── CASE 3: Mismatched Target Role ──────────────────────────────────────────
    p3_mismatch = {
        "uid": "p3",
        "name": "Sam Admin",
        "target_career": "AI / Machine Learning Engineer",
        "skills": ["Microsoft Word", "Excel", "Data Entry", "Customer Service"],
        "projects": [],
        "internships": [],
        "certifications": [],
        "cgpa": 6.8
    }
    res3 = predictor.predict_readiness(p3_mismatch)
    print(f"\n[Case 3] Mismatched Target Role Candidate (Office Skills -> AI Role):")
    print(f"  - Score: {res3.total_score}/100 (Skills Score: {res3.skills_score})")
    print(f"  - Confidence Level: {res3.confidence_level}")
    print(f"  - Insights: {res3.suggestions}")
    assert res3.skills_score == 0.0, "Irrelevant skills must score 0.0 for target role"
    assert res3.total_score < 15.0, f"Mismatched role should score < 15.0, got {res3.total_score}"

    # ── CASE 4: Intermediate Developer ──────────────────────────────────────────
    p4_mid = {
        "uid": "p4",
        "name": "Maya Lin",
        "target_career": "Frontend Developer",
        "skills": ["HTML5", "CSS3", "JavaScript", "React"],
        "projects": [{"title": "Portfolio Website", "technologies": ["HTML5", "CSS3", "JavaScript"]}],
        "internships": [],
        "certifications": [],
        "cgpa": 7.8
    }
    res4 = predictor.predict_readiness(p4_mid)
    print(f"\n[Case 4] Intermediate Candidate (Frontend Dev):")
    print(f"  - Score: {res4.total_score}/100 (Skills: {res4.skills_score}, Projects: {res4.projects_score})")
    print(f"  - Confidence Level: {res4.confidence_level}")
    print(f"  - Insights: {res4.suggestions}")
    assert 20.0 <= res4.total_score <= 65.0, f"Intermediate score should be between 20 and 65, got {res4.total_score}"

    print("\n" + "="*70)
    print("      ALL ML ACCURACY & EDGE CASE TESTS PASSED PERFECTLY!")
    print("="*70)

if __name__ == "__main__":
    run_accuracy_edgecase_tests()
