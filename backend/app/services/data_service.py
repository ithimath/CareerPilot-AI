"""
Data Service — loads career, skills, and course datasets from CSV/JSON files.
Designed to be dataset-agnostic: drop new files in backend/data/ and update loaders.
"""
import os
import json
import csv
import logging
from typing import List, Dict, Optional
from functools import lru_cache
from app.core.config import settings

logger = logging.getLogger(__name__)

DATA_DIR = settings.DATA_DIR


def _load_json(filename: str) -> list:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        logger.warning(f"Dataset file not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_csv(filename: str) -> list:
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        logger.warning(f"Dataset file not found: {path}")
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


@lru_cache(maxsize=1)
def get_careers() -> List[Dict]:
    """
    Load career definitions. Supports careers.json or careers.csv.
    Each career should have: title, description, required_skills, market_demand,
    salary_min, salary_max, category, keywords
    """
    # Try JSON first
    data = _load_json("careers.json")
    if data:
        return data
    # Try CSV
    rows = _load_csv("careers.csv")
    if rows:
        # Normalize: parse comma-separated skill strings into lists
        for row in rows:
            for field in ("required_skills", "keywords"):
                if isinstance(row.get(field), str):
                    row[field] = [s.strip() for s in row[field].split(",") if s.strip()]
        return rows

    logger.warning("No career dataset found — using built-in defaults")
    return _get_default_careers()


@lru_cache(maxsize=1)
def get_courses() -> List[Dict]:
    """
    Load course recommendations. Supports courses.json or courses.csv.
    Each course: title, url, platform, skill, difficulty, duration
    """
    data = _load_json("courses.json")
    if data:
        return data
    rows = _load_csv("courses.csv")
    if rows:
        return rows
    return _get_default_courses()


@lru_cache(maxsize=1)
def get_students_database() -> List[Dict]:
    """
    Load student dataset records. Supports students_database.json or students_database.csv.
    """
    data = _load_json("students_database.json")
    if data:
        return data
    rows = _load_csv("students_database.csv")
    if rows:
        return rows
    return []


def get_courses_for_skill(skill: str) -> List[Dict]:
    """Return courses relevant to a given skill (case-insensitive match)."""
    skill_lower = skill.lower()
    all_courses = get_courses()
    return [
        c for c in all_courses
        if skill_lower in c.get("skill", "").lower()
        or skill_lower in c.get("title", "").lower()
    ][:5]  # max 5 courses per skill


def get_career_by_title(title: str) -> Optional[Dict]:
    """Find a career by title (case-insensitive)."""
    title_lower = title.lower()
    for career in get_careers():
        if career.get("title", "").lower() == title_lower:
            return career
    return None


# ── Default datasets (used when no files are present) ─────────────────────────

def _get_default_careers() -> List[Dict]:
    return [
        {
            "title": "Machine Learning Engineer",
            "description": "Design and build ML models and pipelines that power AI applications.",
            "required_skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "NumPy", "Pandas",
                                 "SQL", "Docker", "Git", "Mathematics", "Statistics"],
            "market_demand": "Very High",
            "salary_min": 90000,
            "salary_max": 160000,
            "salary_range": "$90,000 – $160,000",
            "category": "AI/ML",
            "keywords": ["machine learning", "deep learning", "neural networks", "ai", "data science"],
        },
        {
            "title": "Data Scientist",
            "description": "Extract insights from large datasets using statistical analysis and ML.",
            "required_skills": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-learn",
                                 "Tableau", "Statistics", "Machine Learning", "Data Visualization"],
            "market_demand": "High",
            "salary_min": 80000,
            "salary_max": 140000,
            "salary_range": "$80,000 – $140,000",
            "category": "Data",
            "keywords": ["data science", "analytics", "statistics", "python", "machine learning"],
        },
        {
            "title": "Full Stack Developer",
            "description": "Build end-to-end web applications covering both frontend and backend.",
            "required_skills": ["JavaScript", "React", "Node.js", "HTML", "CSS", "SQL",
                                 "REST APIs", "Git", "Docker", "TypeScript"],
            "market_demand": "Very High",
            "salary_min": 75000,
            "salary_max": 140000,
            "salary_range": "$75,000 – $140,000",
            "category": "Web Development",
            "keywords": ["web development", "react", "nodejs", "javascript", "fullstack"],
        },
        {
            "title": "Backend Developer",
            "description": "Build scalable server-side applications, APIs, and databases.",
            "required_skills": ["Python", "Java", "Node.js", "SQL", "PostgreSQL", "Redis",
                                 "Docker", "REST APIs", "Git", "System Design"],
            "market_demand": "High",
            "salary_min": 70000,
            "salary_max": 130000,
            "salary_range": "$70,000 – $130,000",
            "category": "Web Development",
            "keywords": ["backend", "api", "server", "database", "python", "java"],
        },
        {
            "title": "Frontend Developer",
            "description": "Create interactive and responsive user interfaces for web applications.",
            "required_skills": ["JavaScript", "React", "HTML", "CSS", "TypeScript",
                                 "Tailwind CSS", "Git", "REST APIs", "UI/UX Design"],
            "market_demand": "High",
            "salary_min": 65000,
            "salary_max": 120000,
            "salary_range": "$65,000 – $120,000",
            "category": "Web Development",
            "keywords": ["frontend", "react", "javascript", "html", "css", "ui"],
        },
        {
            "title": "DevOps Engineer",
            "description": "Automate infrastructure, CI/CD pipelines, and manage cloud deployments.",
            "required_skills": ["Linux", "Docker", "Kubernetes", "AWS", "Terraform",
                                 "Python", "Git", "CI/CD", "Bash", "Monitoring"],
            "market_demand": "Very High",
            "salary_min": 85000,
            "salary_max": 150000,
            "salary_range": "$85,000 – $150,000",
            "category": "DevOps/Cloud",
            "keywords": ["devops", "cloud", "kubernetes", "docker", "automation"],
        },
        {
            "title": "Cloud Engineer",
            "description": "Design and manage cloud infrastructure on AWS, GCP, or Azure.",
            "required_skills": ["AWS", "GCP", "Azure", "Terraform", "Kubernetes",
                                 "Docker", "Python", "Networking", "Security", "Linux"],
            "market_demand": "Very High",
            "salary_min": 90000,
            "salary_max": 155000,
            "salary_range": "$90,000 – $155,000",
            "category": "DevOps/Cloud",
            "keywords": ["cloud", "aws", "gcp", "azure", "infrastructure"],
        },
        {
            "title": "Cybersecurity Analyst",
            "description": "Protect systems and networks from threats, vulnerabilities, and attacks.",
            "required_skills": ["Network Security", "SIEM", "Penetration Testing", "Python",
                                 "Firewalls", "Linux", "Cryptography", "Incident Response"],
            "market_demand": "Very High",
            "salary_min": 80000,
            "salary_max": 145000,
            "salary_range": "$80,000 – $145,000",
            "category": "Security",
            "keywords": ["security", "cybersecurity", "networking", "pentesting", "ethical hacking"],
        },
        {
            "title": "Data Analyst",
            "description": "Analyze data to generate business insights and support decision making.",
            "required_skills": ["SQL", "Excel", "Python", "Pandas", "Tableau", "Power BI",
                                 "Statistics", "Data Visualization"],
            "market_demand": "High",
            "salary_min": 55000,
            "salary_max": 100000,
            "salary_range": "$55,000 – $100,000",
            "category": "Data",
            "keywords": ["data analysis", "sql", "excel", "tableau", "reporting"],
        },
        {
            "title": "AI Engineer",
            "description": "Build and deploy AI systems including LLMs, vision models, and AI pipelines.",
            "required_skills": ["Python", "TensorFlow", "PyTorch", "LangChain", "OpenAI API",
                                 "Vector Databases", "Docker", "REST APIs", "Mathematics", "NLP"],
            "market_demand": "Extremely High",
            "salary_min": 100000,
            "salary_max": 200000,
            "salary_range": "$100,000 – $200,000",
            "category": "AI/ML",
            "keywords": ["ai", "llm", "generative ai", "nlp", "computer vision", "transformers"],
        },
        {
            "title": "Software Engineer",
            "description": "Design and implement software solutions across various domains and platforms.",
            "required_skills": ["Data Structures", "Algorithms", "Python", "Java", "C++",
                                 "System Design", "Git", "SQL", "OOP", "Testing"],
            "market_demand": "Very High",
            "salary_min": 75000,
            "salary_max": 160000,
            "salary_range": "$75,000 – $160,000",
            "category": "Software Engineering",
            "keywords": ["software", "programming", "algorithms", "system design", "sde"],
        },
        {
            "title": "Mobile App Developer",
            "description": "Build native or cross-platform mobile applications for iOS and Android.",
            "required_skills": ["Flutter", "React Native", "Dart", "Swift", "Kotlin",
                                 "REST APIs", "Firebase", "Git", "UI/UX Design"],
            "market_demand": "High",
            "salary_min": 70000,
            "salary_max": 130000,
            "salary_range": "$70,000 – $130,000",
            "category": "Mobile",
            "keywords": ["mobile", "android", "ios", "flutter", "react native"],
        },
    ]


def _get_default_courses() -> List[Dict]:
    return [
        # Python
        {"skill": "Python", "title": "Python for Everybody", "platform": "Coursera",
         "url": "https://www.coursera.org/specializations/python", "difficulty": "beginner", "duration": "8 weeks"},
        {"skill": "Python", "title": "100 Days of Code: Python", "platform": "Udemy",
         "url": "https://www.udemy.com/course/100-days-of-code/", "difficulty": "beginner", "duration": "15 weeks"},
        # Machine Learning
        {"skill": "Machine Learning", "title": "Machine Learning Specialization", "platform": "Coursera",
         "url": "https://www.coursera.org/specializations/machine-learning-introduction", "difficulty": "intermediate", "duration": "3 months"},
        {"skill": "TensorFlow", "title": "TensorFlow Developer Certificate", "platform": "Coursera",
         "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "difficulty": "intermediate", "duration": "4 months"},
        {"skill": "PyTorch", "title": "PyTorch for Deep Learning", "platform": "Udemy",
         "url": "https://www.udemy.com/course/pytorch-for-deep-learning/", "difficulty": "intermediate", "duration": "6 weeks"},
        # Web Development
        {"skill": "React", "title": "React - The Complete Guide", "platform": "Udemy",
         "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "difficulty": "intermediate", "duration": "10 weeks"},
        {"skill": "Node.js", "title": "Node.js, Express, MongoDB", "platform": "Udemy",
         "url": "https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/", "difficulty": "intermediate", "duration": "6 weeks"},
        {"skill": "JavaScript", "title": "The Complete JavaScript Course", "platform": "Udemy",
         "url": "https://www.udemy.com/course/the-complete-javascript-course/", "difficulty": "beginner", "duration": "10 weeks"},
        # Cloud
        {"skill": "AWS", "title": "AWS Certified Solutions Architect", "platform": "AWS",
         "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/", "difficulty": "intermediate", "duration": "3 months"},
        {"skill": "Docker", "title": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy",
         "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/", "difficulty": "intermediate", "duration": "4 weeks"},
        # Data
        {"skill": "SQL", "title": "The Complete SQL Bootcamp", "platform": "Udemy",
         "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "difficulty": "beginner", "duration": "4 weeks"},
        {"skill": "Data Science", "title": "IBM Data Science Professional Certificate", "platform": "Coursera",
         "url": "https://www.coursera.org/professional-certificates/ibm-data-science", "difficulty": "intermediate", "duration": "6 months"},
        # Security
        {"skill": "Cybersecurity", "title": "Google Cybersecurity Certificate", "platform": "Coursera",
         "url": "https://www.coursera.org/professional-certificates/google-cybersecurity", "difficulty": "beginner", "duration": "6 months"},
        # Git
        {"skill": "Git", "title": "Git & GitHub Crash Course", "platform": "YouTube",
         "url": "https://www.youtube.com/watch?v=RGOj5yH7evk", "difficulty": "beginner", "duration": "1 week"},
        # System Design
        {"skill": "System Design", "title": "Grokking System Design", "platform": "Educative",
         "url": "https://www.educative.io/courses/grokking-modern-system-design", "difficulty": "advanced", "duration": "6 weeks"},
    ]
