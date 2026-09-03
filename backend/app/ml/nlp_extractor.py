"""
NLP Skill Extraction & Normalization Pipeline
Post-processes Gemini-extracted skills into canonical normalized forms.
Uses an extended alias/synonym dictionary for consistent skill representation.
No external NLP library dependency — pure Python dictionary-based approach.
"""
import logging
import re
from typing import List, Dict, Optional, Tuple, Set

logger = logging.getLogger(__name__)

# ── Master Skill Normalization Map ─────────────────────────────────────────────
# Maps variant forms → canonical name used in CareerPilot AI skill system.
# Extended from SKILL_ALIASES in ml_scoring_service.py
NORMALIZATION_MAP: Dict[str, str] = {
    # Python
    "python3":                  "Python",
    "python 3":                 "Python",
    "py":                       "Python",
    "cpython":                  "Python",

    # JavaScript
    "js":                       "JavaScript",
    "javascript es6":           "JavaScript",
    "ecmascript":               "JavaScript",
    "es6":                      "JavaScript",
    "es2015":                   "JavaScript",
    "vanilla js":               "JavaScript",

    # TypeScript
    "ts":                       "TypeScript",

    # React
    "react.js":                 "React",
    "reactjs":                  "React",
    "react js":                 "React",

    # Next.js
    "next.js":                  "Next.js",
    "nextjs":                   "Next.js",
    "next js":                  "Next.js",

    # Vue
    "vue.js":                   "Vue",
    "vuejs":                    "Vue",
    "vue js":                   "Vue",
    "vue 3":                    "Vue",

    # Angular
    "angular.js":               "Angular",
    "angularjs":                "Angular",

    # Node.js
    "node":                     "Node.js",
    "nodejs":                   "Node.js",
    "node js":                  "Node.js",

    # Svelte
    "svelte.js":                "Svelte",
    "sveltekit":                "SvelteKit",

    # Django / Flask / FastAPI
    "django rest framework":    "Django",
    "drf":                      "Django",
    "flask api":                "Flask",

    # SQL variants
    "structured query language": "SQL",
    "mysql":                    "SQL",
    "sqlite":                   "SQL",
    "sqlite3":                  "SQL",
    "t-sql":                    "SQL",
    "pl/sql":                   "SQL",

    # PostgreSQL
    "postgres":                 "PostgreSQL",
    "psql":                     "PostgreSQL",

    # MongoDB
    "mongo":                    "MongoDB",
    "nosql":                    "MongoDB",

    # Machine Learning
    "ml":                       "Machine Learning",
    "maching learning":         "Machine Learning",  # common typo
    "supervised learning":      "Machine Learning",
    "unsupervised learning":    "Machine Learning",

    # Deep Learning
    "dl":                       "Deep Learning",
    "neural networks":          "Deep Learning",
    "neural network":           "Deep Learning",
    "ann":                      "Deep Learning",
    "cnn":                      "Deep Learning",
    "rnn":                      "Deep Learning",
    "lstm":                     "Deep Learning",

    # NLP
    "natural language processing": "NLP",
    "text analysis":            "NLP",
    "text mining":              "NLP",
    "sentiment analysis":       "NLP",

    # Computer Vision
    "cv":                       "Computer Vision",
    "image processing":         "Computer Vision",
    "object detection":         "Computer Vision",

    # LLM
    "large language model":     "LLM",
    "large language models":    "LLM",
    "generative ai":            "LLM",
    "gen ai":                   "LLM",
    "gpt":                      "LLM",
    "chatgpt":                  "LLM",

    # Scikit-learn
    "scikit learn":             "Scikit-Learn",
    "sklearn":                  "Scikit-Learn",
    "sci-kit learn":            "Scikit-Learn",
    "scikit-learn":             "Scikit-Learn",

    # TensorFlow
    "tensorflow 2":             "TensorFlow",
    "tf":                       "TensorFlow",
    "tensorflow2":              "TensorFlow",

    # PyTorch
    "torch":                    "PyTorch",

    # Cloud
    "amazon web services":      "AWS",
    "aws cloud":                "AWS",
    "google cloud":             "GCP",
    "google cloud platform":    "GCP",
    "microsoft azure":          "Azure",
    "azure cloud":              "Azure",
    "oracle cloud":             "Oracle Cloud",

    # DevOps
    "kubernetes":               "Kubernetes",
    "k8s":                      "Kubernetes",
    "ci/cd":                    "CI/CD",
    "cicd":                     "CI/CD",
    "continuous integration":   "CI/CD",
    "continuous deployment":    "CI/CD",
    "continuous delivery":      "CI/CD",
    "github actions":           "CI/CD",
    "jenkins":                  "CI/CD",
    "gitlab ci":                "CI/CD",

    # Docker
    "containerization":         "Docker",
    "container":                "Docker",
    "dockerfile":               "Docker",
    "docker compose":           "Docker",

    # Linux
    "bash":                     "Linux",
    "shell scripting":          "Linux",
    "unix":                     "Linux",
    "shell":                    "Linux",

    # Git
    "github":                   "Git",
    "gitlab":                   "Git",
    "bitbucket":                "Git",
    "version control":          "Git",

    # REST APIs
    "rest":                     "REST APIs",
    "rest api":                 "REST APIs",
    "restful":                  "REST APIs",
    "restful api":              "REST APIs",
    "restful apis":             "REST APIs",
    "api development":          "REST APIs",
    "web api":                  "REST APIs",

    # Data Analysis
    "data analytics":           "Data Analysis",
    "exploratory data analysis": "Data Analysis",
    "eda":                      "Data Analysis",

    # Statistics
    "statistical analysis":     "Statistics",
    "probability":              "Statistics",
    "inferential statistics":   "Statistics",

    # OOP
    "oop":                      "Object-Oriented Programming",
    "oops":                     "Object-Oriented Programming",
    "object oriented":          "Object-Oriented Programming",
    "object-oriented":          "Object-Oriented Programming",

    # Data Structures
    "dsa":                      "Data Structures & Algorithms",
    "data structures and algorithms": "Data Structures & Algorithms",
    "algorithms":               "Data Structures & Algorithms",
    "ds & algo":                "Data Structures & Algorithms",
    "data structure":           "Data Structures & Algorithms",

    # Agile
    "scrum":                    "Agile",
    "kanban":                   "Agile",
    "agile methodology":        "Agile",
    "agile/scrum":              "Agile",

    # Tailwind
    "tailwind":                 "Tailwind CSS",
    "tailwindcss":              "Tailwind CSS",

    # Microservices
    "microservice architecture": "Microservices",
    "micro-services":           "Microservices",

    # Big Data
    "hadoop":                   "Big Data",
    "apache hadoop":            "Big Data",
    "hdfs":                     "Big Data",

    # Spark
    "apache spark":             "Apache Spark",
    "pyspark":                  "Apache Spark",

    # Security
    "pen testing":              "Penetration Testing",
    "pentesting":               "Penetration Testing",
    "ethical hacking":          "Ethical Hacking",
    "kali linux":               "Ethical Hacking",
    "nmap":                     "Network Security",
    "wireshark":                "Network Security",
    "siem":                     "SIEM Tools",
    "network monitoring":       "Network Security",

    # Mobile
    "android development":      "Android / Kotlin",
    "android":                  "Android / Kotlin",
    "kotlin":                   "Android / Kotlin",
    "ios development":          "iOS / Swift",
    "ios":                      "iOS / Swift",
    "swift":                    "iOS / Swift",
    "react native":             "React Native",

    # Communication / Soft
    "communication skills":     "Communication",
    "verbal communication":     "Communication",
    "written communication":    "Communication",
    "public speaking":          "Communication",
    "problem solving":          "Problem-Solving",
    "critical thinking":        "Problem-Solving",
    "analytical thinking":      "Problem-Solving",
    "leadership skills":        "Leadership",
    "team leadership":          "Leadership",
    "teamwork":                 "Teamwork",
    "collaboration":            "Teamwork",
    "time management":          "Time Management",
    "adaptability":             "Adaptability",

    # Data Visualization
    "matplotlib":               "Data Visualization",
    "seaborn":                  "Data Visualization",
    "plotly":                   "Data Visualization",
    "bokeh":                    "Data Visualization",
    "tableau":                  "Tableau",
    "power bi":                 "Power BI",
    "powerbi":                  "Power BI",
    "d3.js":                    "D3.js",

    # Excel / Spreadsheets
    "microsoft excel":          "Excel",
    "ms excel":                 "Excel",
    "google sheets":            "Excel",
    "spreadsheets":             "Excel",

    # Databases general
    "database management":      "SQL",
    "dbms":                     "SQL",
    "rdbms":                    "SQL",

    # Redis
    "redis cache":              "Redis",
    "caching":                  "Redis",

    # GraphQL
    "graph ql":                 "GraphQL",

    # Testing
    "unit testing":             "Testing",
    "integration testing":      "Testing",
    "test driven development":  "Testing",
    "tdd":                      "Testing",
    "pytest":                   "Testing",
    "jest":                     "Testing",
    "selenium":                 "Testing",

    # Design patterns
    "design patterns":          "Software Design Patterns",
    "mvc":                      "Software Design Patterns",
    "mvvm":                     "Software Design Patterns",

    # Langchain
    "lang chain":               "LangChain",
    "langchain framework":      "LangChain",

    # Vector DBs
    "pinecone":                 "Vector Databases",
    "weaviate":                 "Vector Databases",
    "chroma":                   "Vector Databases",
    "qdrant":                   "Vector Databases",
    "faiss":                    "Vector Databases",
    "vector database":          "Vector Databases",
}


def normalize_skill(raw_skill: str) -> Tuple[str, float]:
    """
    Normalize a skill name to its canonical form.
    Returns (canonical_name, confidence) where confidence ∈ [0.0, 1.0].
    - 1.0 = exact match in normalization map
    - 0.9 = lowercase exact match
    - 0.75 = partial/fuzzy match
    - 0.5 = title-cased raw (no match found)
    """
    if not raw_skill or not raw_skill.strip():
        return "", 0.0

    stripped = raw_skill.strip()
    lower = stripped.lower()

    # 1. Exact lowercase match in normalization map
    if lower in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[lower], 1.0

    # 2. Remove version numbers (e.g. "Python 3.10" → "Python")
    no_version = re.sub(r'\s*\d+(\.\d+)*\s*$', '', stripped).strip()
    if no_version.lower() in NORMALIZATION_MAP:
        return NORMALIZATION_MAP[no_version.lower()], 0.9

    # 3. Partial match — check if a map key is a substring or vice versa
    for key, canonical in NORMALIZATION_MAP.items():
        if len(key) > 3 and (key in lower or lower in key):
            return canonical, 0.75

    # 4. Return title-cased raw as fallback
    return stripped.title(), 0.5


def normalize_skills_list(skills: List[str]) -> List[Dict]:
    """
    Normalize a list of skill strings.
    Returns list of {original, canonical, confidence} dicts.
    Deduplicates by canonical name (keeps highest confidence).
    """
    seen_canonical: Dict[str, float] = {}  # canonical → confidence
    results = []

    for skill in skills:
        if not skill or not isinstance(skill, str):
            continue
        canonical, confidence = normalize_skill(skill)
        if not canonical:
            continue

        if canonical not in seen_canonical or confidence > seen_canonical[canonical]:
            seen_canonical[canonical] = confidence
            results.append({
                "original": skill.strip(),
                "canonical": canonical,
                "confidence": round(confidence, 2),
            })

    # Deduplicate (keep highest-confidence entry per canonical name)
    deduped: Dict[str, dict] = {}
    for item in results:
        c = item["canonical"]
        if c not in deduped or item["confidence"] > deduped[c]["confidence"]:
            deduped[c] = item

    return sorted(deduped.values(), key=lambda x: x["confidence"], reverse=True)


def normalize_extracted_skills(
    extracted_skills: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    Post-process Gemini's extracted skills dict (by category) through normalization.
    Input:  {"programming_languages": ["Python", "py", "JS"], "frameworks": [...], ...}
    Output: Same structure but with canonical skill names, deduped across categories.
    """
    global_seen: Set[str] = set()
    normalized_output: Dict[str, List[str]] = {}

    # Process categories in order of semantic importance
    category_order = [
        "programming_languages", "frameworks", "libraries",
        "databases", "cloud_platforms", "developer_tools", "soft_skills",
    ]
    all_categories = category_order + [k for k in extracted_skills if k not in category_order]

    for category in all_categories:
        raw_list = extracted_skills.get(category) or []
        if not isinstance(raw_list, list):
            continue

        category_skills = []
        for skill in raw_list:
            if not isinstance(skill, str) or not skill.strip():
                continue
            canonical, confidence = normalize_skill(skill)
            if not canonical or confidence < 0.4:
                continue
            if canonical.lower() not in global_seen:
                global_seen.add(canonical.lower())
                category_skills.append(canonical)

        if category_skills:
            normalized_output[category] = category_skills

    return normalized_output


def extract_skills_from_raw_text(text: str) -> List[str]:
    """
    Lightweight keyword-based skill extraction from raw certificate text.
    Supplements Gemini extraction as a sanity-check pass.
    Returns list of canonical skill names found in the text.
    """
    if not text:
        return []

    text_lower = text.lower()
    found: Dict[str, float] = {}

    # Check all normalization map keys against the text
    for key, canonical in NORMALIZATION_MAP.items():
        if len(key) < 3:
            continue
        # Word-boundary match
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, text_lower):
            if canonical not in found or 1.0 > found[canonical]:
                found[canonical] = 1.0

    # Also check canonical names directly
    for canonical in set(NORMALIZATION_MAP.values()):
        key = canonical.lower()
        if len(key) < 3:
            continue
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, text_lower) and canonical not in found:
            found[canonical] = 0.9

    return sorted(found.keys())
