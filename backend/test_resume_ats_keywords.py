"""
Test Suite for Resume ATS Keyword Analysis & Perfect Skill Matching Engine
"""
import os
import sys
import unittest

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.routers.resume import _analyze_locally, _get_target_skills_for_role, _check_skill_in_text


class TestResumeATSKeywords(unittest.TestCase):
    def test_role_skill_lookup(self):
        skills, keywords = _get_target_skills_for_role("Full Stack Developer")
        self.assertIn("React", skills)
        self.assertIn("JavaScript", skills)

        ml_skills, ml_keywords = _get_target_skills_for_role("Machine Learning Engineer")
        self.assertIn("Python", ml_skills)
        self.assertIn("TensorFlow", ml_skills)

    def test_skill_alias_matching(self):
        text = "Experienced software engineer working with ts, react.js, psql, and k8s."
        self.assertTrue(_check_skill_in_text("TypeScript", text))
        self.assertTrue(_check_skill_in_text("React", text))
        self.assertTrue(_check_skill_in_text("PostgreSQL", text))
        self.assertTrue(_check_skill_in_text("Kubernetes", text))
        self.assertFalse(_check_skill_in_text("Flutter", text))

    def test_perfect_skill_match_detection(self):
        full_resume = """
        ALEX MORGAN
        SUMMARY: Senior Full Stack Developer
        SKILLS: React, TypeScript, Python, FastAPI, REST APIs, SQL, PostgreSQL, Git, Docker
        EXPERIENCE:
        Frontend Engineer | Developed cloud app scaling to 100k users with Docker and PostgreSQL.
        Reduced page latency by 35%.
        PROJECTS:
        Building AI Career Platform with React, TypeScript, and FastAPI.
        EDUCATION: B.S. Computer Science
        """

        result = _analyze_locally(full_resume, "Full-Stack Engineer")

        self.assertIn("skill_match_details", result)
        self.assertTrue(result["skill_match_details"]["is_perfect_match"])
        self.assertEqual(result["skill_match_details"]["match_percentage"], 100.0)
        self.assertEqual(len(result["missing_keywords"]), 0)
        self.assertTrue(result["structure_checks"]["summary"])
        self.assertTrue(result["structure_checks"]["skills"])
        self.assertTrue(result["structure_checks"]["experience"])
        self.assertTrue(result["structure_checks"]["education"])
        self.assertTrue(result["structure_checks"]["projects"])

    def test_partial_skill_match(self):
        partial_resume = """
        JANE DOE
        SKILLS: React, Python, Git
        EXPERIENCE: Developed REST API services.
        """

        result = _analyze_locally(partial_resume, "Full Stack Developer")

        self.assertFalse(result["skill_match_details"]["is_perfect_match"])
        self.assertLess(result["skill_match_details"]["match_percentage"], 100.0)
        self.assertGreater(len(result["missing_keywords"]), 0)
        self.assertIn("JavaScript", result["missing_keywords"])


    def test_gibberish_input_rejection(self):
        gibberish = "hibguvbkbmj k; hibguvbkbmj k; hibguvbkbmj k; hibguvbkbmj k;"
        result = _analyze_locally(gibberish, "Full-Stack Engineer")
        self.assertLessEqual(result["ats_score"], 15)
        self.assertFalse(result["skill_match_details"]["is_perfect_match"])
        self.assertEqual(len(result["matching_keywords"]), 0)


if __name__ == "__main__":
    unittest.main()
