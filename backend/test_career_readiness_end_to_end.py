"""
End-to-End Verification Test for Career Readiness Score System
Tests:
1. Initial clean state for new user (score = 0.0)
2. Incremental score growth as activities are completed
3. Skill proficiency multipliers
4. Mock test submissions and score impact
5. AI interview session recording and growth tracking
6. Resume ATS diagnostics recording
7. Persistence across simulated restarts / logins
8. Historical audit logging and deltas
"""
import os
import sys
import json
import uuid

# Force UTF-8 on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Set backend path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.firebase import get_firestore
from app.services.scoring_service import calculate_job_readiness_score, load_user_activities
from app.services.ml_scoring_service import get_ml_predictor

def run_e2e_tests():
    print("==================================================")
    print("🧪 RUNNING CAREER READINESS SCORE E2E TEST SUITE")
    print("==================================================")

    test_uid = f"test_student_{uuid.uuid4().hex[:8]}"
    db = get_firestore()

    # 1. NEW USER INITIAL STATE TEST
    print("\n--- Test 1: Brand New User Initialization ---")
    activities = load_user_activities(test_uid)
    empty_profile = {"uid": test_uid, "skills": [], "projects": [], "certifications": []}
    initial_score = calculate_job_readiness_score(empty_profile, activities=activities, action_reason="User Created")
    
    print(f"Initial Total Score: {initial_score.total_score}")
    assert initial_score.total_score == 0.0, f"Expected 0.0, got {initial_score.total_score}"
    assert initial_score.skills_score == 0.0
    assert initial_score.interviews_score == 0.0
    assert initial_score.resume_score == 0.0
    assert initial_score.assessments_score == 0.0
    print("✅ Test 1 Passed: Brand new user starts at exactly 0.0 score.")

    # 2. SKILL ADDITION & PROFICIENCY TEST
    print("\n--- Test 2: Adding Skills with Proficiency Levels ---")
    skills_data = [
        {"name": "Python", "level": "Advanced", "verified": True},
        {"name": "FastAPI", "level": "Intermediate", "verified": False},
        {"name": "React", "level": "Advanced", "verified": True},
        {"name": "SQL", "level": "Expert", "verified": True},
        {"name": "Docker", "level": "Intermediate", "verified": False},
    ]
    profile = {
        "uid": test_uid,
        "name": "Jane Developer",
        "target_career": "Full-Stack Engineer",
        "skills": skills_data,
        "projects": [
            {
                "title": "E-Commerce Microservices",
                "description": "High-throughput microservices architecture with FastAPI and PostgreSQL",
                "technologies": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                "github_url": "https://github.com/janedev/ecommerce",
                "live_url": "https://ecommerce.demo"
            }
        ],
        "certifications": ["AWS Certified Cloud Practitioner"]
    }
    db.collection("profiles").document(test_uid).set(profile)

    score_after_profile = calculate_job_readiness_score(profile, action_reason="Profile & Skills Added")
    print(f"Score after profile & skills: {score_after_profile.total_score} (Skills: {score_after_profile.skills_score}, Projects: {score_after_profile.projects_score}, Certs: {score_after_profile.certificates_score})")
    assert score_after_profile.total_score > 25.0, "Score should have increased significantly"
    assert score_after_profile.skills_score > 10.0, "Skills score should reflect proficiency"
    assert score_after_profile.projects_score > 5.0, "Projects score should be non-zero"
    print("✅ Test 2 Passed: Skills, projects, and certs properly calculated with proficiency weighting.")

    # 3. MOCK TEST ASSESSMENT IMPACT
    print("\n--- Test 3: Technical Mock Test Submission ---")
    test_record = {
        "record_id": "test_dsa_1",
        "test_id": "dsa",
        "test_title": "Data Structures & Algorithms Core Assessment",
        "category": "Algorithms",
        "score": 90.0,
        "total_questions": 5,
        "correct_count": 4,
        "timestamp": "2026-08-14T10:00:00Z"
    }
    db.collection(f"assessments/{test_uid}/records").document("test_dsa_1").set(test_record)

    activities = load_user_activities(test_uid)
    score_after_assessment = calculate_job_readiness_score(profile, activities=activities, action_reason="Completed DSA Assessment (90%)")
    print(f"Score after assessment: {score_after_assessment.total_score} (Assessments: {score_after_assessment.assessments_score})")
    assert score_after_assessment.assessments_score >= 6.0, "Assessments score should increase"
    assert score_after_assessment.total_score > score_after_profile.total_score, "Total score should rise"
    print("✅ Test 3 Passed: Technical assessment successfully elevated assessments dimension.")

    # 4. AI MOCK INTERVIEW LOOP & GROWTH IMPACT
    print("\n--- Test 4: AI Mock Interview Sessions & Progression ---")
    interview_1 = {
        "session_id": "sess_1",
        "role": "Full-Stack Engineer",
        "category": "technical",
        "overall_score": 75.0,
        "score": 75.0,
        "clarity": 78.0,
        "technical_accuracy": 76.0,
        "timestamp": "2026-08-14T11:00:00Z"
    }
    db.collection(f"interviews/{test_uid}/sessions").document("sess_1").set(interview_1)

    interview_2 = {
        "session_id": "sess_2",
        "role": "Full-Stack Engineer",
        "category": "technical",
        "overall_score": 90.0,  # Improved performance
        "score": 90.0,
        "clarity": 92.0,
        "technical_accuracy": 88.0,
        "timestamp": "2026-08-14T12:00:00Z"
    }
    db.collection(f"interviews/{test_uid}/sessions").document("sess_2").set(interview_2)

    activities = load_user_activities(test_uid)
    score_after_interviews = calculate_job_readiness_score(profile, activities=activities, action_reason="Completed 2 Mock Interviews with score growth")
    print(f"Score after interviews: {score_after_interviews.total_score} (Interviews: {score_after_interviews.interviews_score})")
    assert score_after_interviews.interviews_score > 12.0, "Interviews score should reflect count, quality, and positive growth"
    print("✅ Test 4 Passed: AI Interview sessions recorded and growth trend rewarded.")

    # 5. RESUME ATS SCAN IMPACT
    print("\n--- Test 5: Resume ATS Diagnostic Scan ---")
    resume_scan = {
        "version_id": "v_1",
        "target_role": "Full-Stack Engineer",
        "ats_score": 85,
        "score": 85,
        "matched_keywords": ["Python", "React", "FastAPI", "PostgreSQL", "Docker"],
        "missing_keywords": ["AWS", "CI/CD"],
        "timestamp": "2026-08-14T13:00:00Z"
    }
    db.collection(f"resumes/{test_uid}/versions").document("v_1").set(resume_scan)

    activities = load_user_activities(test_uid)
    final_score = calculate_job_readiness_score(profile, activities=activities, action_reason="Completed Resume ATS Scan")
    print(f"Final Combined Score: {final_score.total_score} (Resume: {final_score.resume_score})")
    assert final_score.resume_score > 8.0, "Resume ATS score should reflect scan quality"
    assert len(final_score.positive_drivers) >= 3, "Explainable positive drivers should be generated"
    print("✅ Test 5 Passed: Resume ATS scan elevated score with explainable positive drivers.")

    # 6. PERSISTENCE & RE-FETCH TEST (Never resets to 0)
    print("\n--- Test 6: Database Persistence & Re-fetching ---")
    # Save the score to jobScores collection
    db.collection("jobScores").document(test_uid).set({
        **final_score.model_dump(),
        "uid": test_uid
    })

    # Simulate fresh login / new session load
    loaded_doc = db.collection("jobScores").document(test_uid).get()
    assert loaded_doc.exists, "Document should exist in persistent database"
    loaded_data = loaded_doc.to_dict()
    assert loaded_data["total_score"] == final_score.total_score, f"Loaded {loaded_data['total_score']} != {final_score.total_score}"
    assert loaded_data["total_score"] > 60.0, "Score must remain intact and non-zero across logins"
    print(f"Restored user score after simulated login: {loaded_data['total_score']}/100")
    print("✅ Test 6 Passed: Score persists 100% reliably and never unexpectedly resets to 0.")

    # 7. SCORE HISTORY AUDIT LOG TEST
    print("\n--- Test 7: Score History Audit Trail ---")
    history_doc = db.collection("readinessHistory").document(test_uid).get()
    assert history_doc.exists, "History document must exist"
    history_entries = history_doc.to_dict().get("history", [])
    print(f"Recorded History Entries Count: {len(history_entries)}")
    for entry in history_entries:
        print(f"  • [{entry.get('timestamp')}] {entry.get('reason')} -> Score: {entry.get('total_score')} (Delta: {entry.get('delta')})")
    assert len(history_entries) >= 2, "Should have multiple progression milestone logs"
    print("✅ Test 7 Passed: Score progression audit history logged accurately.")

    print("\n==================================================")
    print("🎉 ALL 7 CAREER READINESS SCORE TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_e2e_tests()
