"""
Test Suite for Candidate Profile Dossier Router & Completeness Calculator
"""
import os
import sys
import unittest
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.core.firebase import get_firestore
from app.services.scoring_service import calculate_profile_completion, calculate_job_readiness_score


class TestProfileDossier(unittest.TestCase):
    def setUp(self):
        self.test_uid = f"dossier_test_{uuid.uuid4().hex[:8]}"

    def test_profile_completion_calculator(self):
        partial_profile = {
            "name": "Jane Candidate",
            "college": "Tech University",
            "degree": "B.Tech",
            "department": "Computer Science",
            "current_year": 4,
            "cgpa": 8.8,
            "skills": [{"name": "React"}, {"name": "Python"}, {"name": "SQL"}],
            "interests": ["Full-Stack", "AI"],
            "projects": [],
            "internships": [],
            "certifications": []
        }

        result = calculate_profile_completion(partial_profile)
        self.assertIn("percentage", result)
        self.assertIn("missing_fields", result)
        self.assertFalse(result["is_complete"])
        self.assertGreater(len(result["missing_fields"]), 0)

        # Complete profile
        complete_profile = {
            **partial_profile,
            "github_url": "https://github.com/janedev",
            "linkedin_url": "https://linkedin.com/in/janedev",
            "portfolio_url": "https://janedev.io",
            "projects": [{"title": "AI Platform", "technologies": ["React", "FastAPI"]}],
            "internships": [{"company": "Tech Corp", "role": "Frontend Intern"}],
            "certifications": ["AWS Certified Cloud Practitioner"]
        }

        complete_result = calculate_profile_completion(complete_profile)
        self.assertEqual(complete_result["percentage"], 100.0)
        self.assertTrue(complete_result["is_complete"])
        self.assertEqual(len(complete_result["missing_fields"]), 0)

    def test_job_readiness_score_incorporates_dossier_projects_and_experience(self):
        full_dossier = {
            "uid": self.test_uid,
            "name": "Alex Candidate",
            "target_career": "Full-Stack Engineer",
            "skills": [
                {"name": "React", "level": "Advanced", "verified": True},
                {"name": "TypeScript", "level": "Advanced", "verified": True},
                {"name": "Python", "level": "Intermediate", "verified": False},
            ],
            "projects": [
                {
                    "title": "E-Commerce Microservices",
                    "description": "High-throughput microservices architecture with FastAPI and PostgreSQL",
                    "technologies": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                    "github_url": "https://github.com/alex/ecommerce",
                    "live_url": "https://ecommerce.demo"
                }
            ],
            "internships": [
                {
                    "company": "Cloud Tech Inc",
                    "role": "Frontend Engineering Intern",
                    "duration": "Summer 2025",
                    "description": "Built React components and RESTful API integrations."
                }
            ],
            "certifications": ["AWS Certified Solutions Architect"]
        }

        score = calculate_job_readiness_score(full_dossier)
        self.assertGreater(score.total_score, 25.0)
        self.assertGreater(score.skills_score, 10.0)
        self.assertGreater(score.projects_score, 5.0)


if __name__ == "__main__":
    unittest.main()
