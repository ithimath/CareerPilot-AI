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


def get_domain_for_career(title: str) -> str:
    """Resolve domain hierarchy for a given career title."""
    t = title.lower()
    if "ai" in t or "machine learning" in t or "ml" in t or "data scientist" in t or "data engineer" in t or "nlp" in t:
        return "AI & Machine Learning"
    elif "data analyst" in t or "analytics" in t:
        return "Data Analytics & Intelligence"
    elif "devops" in t or "cloud" in t or "infrastructure" in t or "sysadmin" in t:
        return "DevOps & Cloud Infrastructure"
    elif "security" in t or "cyber" in t or "pentest" in t:
        return "Cybersecurity & Systems Protection"
    elif "mobile" in t or "ios" in t or "android" in t or "flutter" in t:
        return "Mobile Application Development"
    elif "full" in t or "web" in t or "front" in t or "back" in t or "react" in t or "node" in t:
        return "Full Stack & Web Engineering"
    else:
        return "Software Systems & Architecture"


def _get_default_courses() -> List[Dict]:
    return [
        # Python
        {
            "skill": "Python",
            "title": "Python for Everybody Specialization",
            "platform": "Coursera (Univ. of Michigan)",
            "url": "https://www.coursera.org/specializations/python",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "8 weeks (4 hrs/wk)",
            "relevance_reason": "Core programming foundation required for backend services and AI workflows."
        },
        {
            "skill": "Python",
            "title": "Complete Python Developer in 2026",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/complete-python-developer/",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "12 weeks",
            "relevance_reason": "Hands-on mastery of object-oriented Python, decorators, and memory management."
        },
        # Machine Learning & AI
        {
            "skill": "Machine Learning",
            "title": "Machine Learning Specialization by Andrew Ng",
            "platform": "DeepLearning.AI / Coursera",
            "url": "https://www.coursera.org/specializations/machine-learning-introduction",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "3 months (6 hrs/wk)",
            "relevance_reason": "Industry standard foundation for supervised learning, neural networks, and model evaluation."
        },
        {
            "skill": "TensorFlow",
            "title": "TensorFlow Developer Professional Certificate",
            "platform": "DeepLearning.AI / Coursera",
            "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "4 months",
            "relevance_reason": "Essential for building and training production computer vision and NLP models."
        },
        {
            "skill": "PyTorch",
            "title": "Deep Learning with PyTorch for Beginners",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/pytorch-for-deep-learning/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "6 weeks",
            "relevance_reason": "Dynamic neural graph framework preferred for research and production AI architectures."
        },
        {
            "skill": "NLP",
            "title": "Natural Language Processing Specialization",
            "platform": "DeepLearning.AI",
            "url": "https://www.coursera.org/specializations/natural-language-processing",
            "difficulty": "advanced",
            "level": "Advanced Architecture",
            "duration": "4 months",
            "relevance_reason": "Master transformers, attention mechanisms, sentiment analysis, and LLM fine-tuning."
        },
        {
            "skill": "LangChain",
            "title": "LangChain for LLM Application Development",
            "platform": "DeepLearning.AI",
            "url": "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "2 weeks",
            "relevance_reason": "Build autonomous agents, prompt chaining, and context-aware RAG pipelines."
        },
        {
            "skill": "Vector Databases",
            "title": "Vector Databases for AI Search & RAG",
            "platform": "DeepLearning.AI",
            "url": "https://www.deeplearning.ai/short-courses/vector-databases-embeddings-applications/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "2 weeks",
            "relevance_reason": "Required for indexing semantic embeddings with Pinecone, Chroma, and Qdrant."
        },
        {
            "skill": "Scikit-learn",
            "title": "Machine Learning with Python & Scikit-Learn",
            "platform": "edX / MIT",
            "url": "https://www.edx.org/course/machine-learning-with-python-from-linear-models-to-deep-learning",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "6 weeks",
            "relevance_reason": "Implement classic algorithms, feature engineering, and cross-validation pipelines."
        },
        # Web Development & Frontend
        {
            "skill": "React",
            "title": "React 19 & Next.js - The Complete Guide",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "10 weeks",
            "relevance_reason": "Industry standard library for component architecture, state hooks, and SSR."
        },
        {
            "skill": "TypeScript",
            "title": "Understanding TypeScript - 2026 Edition",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/understanding-typescript/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "5 weeks",
            "relevance_reason": "Ensures type safety, prevents runtime errors, and scales enterprise web applications."
        },
        {
            "skill": "JavaScript",
            "title": "The Complete JavaScript Course: From Zero to Expert!",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/the-complete-javascript-course/",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "10 weeks",
            "relevance_reason": "Core web language for asynchronous event loops, DOM manipulation, and modern ES6+."
        },
        {
            "skill": "FastAPI",
            "title": "FastAPI - Modern Python Web Framework",
            "platform": "TestDriven.io",
            "url": "https://testdriven.io/courses/fastapi-crud/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "4 weeks",
            "relevance_reason": "High-performance microservices, async routing, and auto-generated OpenAPI schemas."
        },
        {
            "skill": "Node.js",
            "title": "Node.js, Express, & MongoDB Bootcamp",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/nodejs-express-mongodb-bootcamp/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "6 weeks",
            "relevance_reason": "Server-side JavaScript runtime for asynchronous non-blocking event-driven backends."
        },
        # Cloud & DevOps
        {
            "skill": "AWS",
            "title": "AWS Certified Solutions Architect Associate",
            "platform": "AWS Skill Builder",
            "url": "https://aws.amazon.com/certification/certified-solutions-architect-associate/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "3 months",
            "relevance_reason": "Master resilient cloud architecture, VPC networking, IAM, and EC2/S3 infrastructure."
        },
        {
            "skill": "Docker",
            "title": "Docker & Kubernetes: The Complete Practical Guide",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "4 weeks",
            "relevance_reason": "Essential for containerizing microservices and ensuring environment parity."
        },
        {
            "skill": "Kubernetes",
            "title": "Certified Kubernetes Administrator (CKA)",
            "platform": "Linux Foundation / Udemy",
            "url": "https://www.udemy.com/course/certified-kubernetes-administrator-with-pracrice-tests/",
            "difficulty": "advanced",
            "level": "Advanced Architecture",
            "duration": "6 weeks",
            "relevance_reason": "Orchestrate multi-node clusters, ingress controllers, and auto-scaling pods."
        },
        {
            "skill": "Terraform",
            "title": "HashiCorp Certified: Terraform Associate",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/terraform-hands-on-labs/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "4 weeks",
            "relevance_reason": "Declarative Infrastructure-as-Code for multi-cloud deployment automation."
        },
        {
            "skill": "Linux",
            "title": "Linux Command Line & Shell Scripting",
            "platform": "Coursera",
            "url": "https://www.coursera.org/learn/hands-on-introduction-to-linux-commands-and-shell-scripting",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "3 weeks",
            "relevance_reason": "Foundational operating system command line skills for cloud servers and DevOps."
        },
        # Data & Databases
        {
            "skill": "SQL",
            "title": "The Complete SQL Bootcamp for Data & Engineering",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "4 weeks",
            "relevance_reason": "Query optimization, complex JOINs, aggregate functions, and window operations."
        },
        {
            "skill": "Pandas",
            "title": "Data Analysis with Python & Pandas",
            "platform": "Coursera",
            "url": "https://www.coursera.org/learn/data-analysis-with-python",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "4 weeks",
            "relevance_reason": "Manipulate structured DataFrames, handle missing values, and transform datasets."
        },
        {
            "skill": "Tableau",
            "title": "Tableau 2026 A-Z: Hands-On Data Visualization",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/tableau10/",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "4 weeks",
            "relevance_reason": "Build executive dashboards and communicate business analytics effectively."
        },
        # Security
        {
            "skill": "Network Security",
            "title": "Google Cybersecurity Professional Certificate",
            "platform": "Coursera",
            "url": "https://www.coursera.org/professional-certificates/google-cybersecurity",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "5 months",
            "relevance_reason": "Comprehensive training in threat analysis, firewalls, and incident mitigation."
        },
        {
            "skill": "Penetration Testing",
            "title": "Practical Ethical Hacking & Pentesting",
            "platform": "TCM Security",
            "url": "https://academy.tcm-sec.com/p/practical-ethical-hacking-the-complete-course",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "8 weeks",
            "relevance_reason": "Identify security vulnerabilities, exploit mechanisms, and harden system defenses."
        },
        # Mobile
        {
            "skill": "Flutter",
            "title": "Flutter & Dart - The Complete Guide",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/flutter-dart-the-complete-guide/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "8 weeks",
            "relevance_reason": "Build high-performance cross-platform mobile apps for iOS and Android from a single codebase."
        },
        {
            "skill": "React Native",
            "title": "React Native - The Practical Guide",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/react-native-the-practical-guide/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "6 weeks",
            "relevance_reason": "Leverage React skills to build native mobile UI applications."
        },
        # General Software Engineering & System Design
        {
            "skill": "System Design",
            "title": "Grokking Modern System Design for Engineers",
            "platform": "Educative.io",
            "url": "https://www.educative.io/courses/grokking-modern-system-design",
            "difficulty": "advanced",
            "level": "Advanced Architecture",
            "duration": "6 weeks",
            "relevance_reason": "Architect distributed load balancers, message queues, caching layers, and database sharding."
        },
        {
            "skill": "Data Structures",
            "title": "Data Structures & Algorithms Masterclass",
            "platform": "Udemy",
            "url": "https://www.udemy.com/course/data-structures-and-algorithms-deep-dive-using-java/",
            "difficulty": "intermediate",
            "level": "Intermediate Specialization",
            "duration": "8 weeks",
            "relevance_reason": "Master trees, graphs, dynamic programming, and space/time complexity optimization."
        },
        {
            "skill": "Git",
            "title": "Git & GitHub Complete Masterclass",
            "platform": "YouTube / freeCodeCamp",
            "url": "https://www.youtube.com/watch?v=RGOj5yH7evk",
            "difficulty": "beginner",
            "level": "Beginner Track",
            "duration": "1 week",
            "relevance_reason": "Distributed version control, branching models, and pull request code reviews."
        },
    ]

