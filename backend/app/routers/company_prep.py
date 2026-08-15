"""
CareerPilot AI — Company Prep & Insights Router
"""
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_current_user_optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

COMPANIES_DATA = [
    {
        "id": "google",
        "name": "Google",
        "domain": "google.com",
        "roles": ["Software Engineer", "AI/ML Engineer", "Product Manager"],
        "culture": "Emphasis on data structures, algorithms, system design, and Googleyness.",
        "difficulty": "Hard",
        "rounds": ["Recruiter Screen", "Phone Technical (1)", "Onsite Coding (3-4)", "System Design (1)", "Behavioral/Leadership"],
        "top_topics": ["Graphs & Trees", "Dynamic Programming", "System Architecture", "Concurrency"],
        "sample_questions": [
            "Implement a LRU Cache in O(1) time.",
            "Design a distributed rate limiter.",
            "Tell me about a time you took a calculated risk and failed."
        ]
    },
    {
        "id": "microsoft",
        "name": "Microsoft",
        "domain": "microsoft.com",
        "roles": ["Software Engineer", "Cloud Solutions Architect", "Data Scientist"],
        "culture": "Growth mindset, customer obsession, collaboration, and deep fundamentals.",
        "difficulty": "Medium-Hard",
        "rounds": ["Online Assessment", "Technical Phone Screen", "Final Round (4 interviews)"],
        "top_topics": ["Arrays & Strings", "Linked Lists", "Object Oriented Design", "Cloud Infrastructure"],
        "sample_questions": [
            "Reverse words in a given string.",
            "Design an online collaborative document editor (like Word Online).",
            "How do you prioritize competing requests from multiple teams?"
        ]
    },
    {
        "id": "amazon",
        "name": "Amazon",
        "domain": "amazon.com",
        "roles": ["Software Development Engineer (SDE)", "DevOps Engineer", "Solutions Architect"],
        "culture": "Heavy focus on 16 Leadership Principles (Customer Obsession, Ownership, Dive Deep).",
        "difficulty": "Hard",
        "rounds": ["Online Assessment (OA)", "Technical Screen", "Loop Interview (4-5 interviews with Bar Raiser)"],
        "top_topics": ["Trees & Graphs", "Dynamic Programming", "Low Level Design", "Leadership Principles (STAR method)"],
        "sample_questions": [
            "Serialize and Deserialize a Binary Tree.",
            "Design Amazon Shopping Cart & Checkout Service.",
            "Describe a situation where you had to make a decision without complete data."
        ]
    },
    {
        "id": "meta",
        "name": "Meta",
        "domain": "meta.com",
        "roles": ["Frontend Engineer", "Full Stack Engineer", "Production Engineer"],
        "culture": "Fast execution, impact-driven, rapid coding accuracy under pressure.",
        "difficulty": "Hard",
        "rounds": ["Initial Screen", "Coding Interview (2 coding questions in 45 min)", "System Design / Product Architecture", "Behavioral"],
        "top_topics": ["Binary Search", "Hash Tables", "BFS/DFS", "System Design"],
        "sample_questions": [
            "Find the lowest common ancestor of a binary tree.",
            "Design Instagram Newsfeed Architecture.",
            "How do you push code safely to millions of active users?"
        ]
    },
    {
        "id": "apple",
        "name": "Apple",
        "domain": "apple.com",
        "roles": ["iOS Engineer", "Systems Engineer", "Hardware Software Integration"],
        "culture": "Extreme attention to detail, privacy-first engineering, and functional excellence.",
        "difficulty": "Hard",
        "rounds": ["Recruiter Call", "Technical Phone Screen", "Onsite Loop (5-6 interviews)"],
        "top_topics": ["Memory Management", "Concurrency", "Algorithms", "OS Fundamentals"],
        "sample_questions": [
            "Explain memory retain cycles in Swift/Objective-C.",
            "Design a key-value store with transaction support.",
            "Tell me about a time you resolved a complex cross-team technical bug."
        ]
    },
    {
        "id": "netflix",
        "name": "Netflix",
        "domain": "netflix.com",
        "roles": ["Senior Software Engineer", "Platform Engineer", "Data Engineer"],
        "culture": "Freedom and Responsibility, high talent density, context over control.",
        "difficulty": "Hard",
        "rounds": ["Recruiter Screening", "Technical Screen (2 rounds)", "Onsite Panel (Deep Architecture + Culture Fit)"],
        "top_topics": ["Distributed Systems", "Microservices", "Resilience & Chaos Engineering", "API Design"],
        "sample_questions": [
            "Design a video streaming CDN delivery architecture.",
            "How do you ensure service availability under sudden global traffic spikes?",
            "Describe how you handle constructive disagreement with senior leadership."
        ]
    },
    {
        "id": "tesla",
        "name": "Tesla",
        "domain": "tesla.com",
        "roles": ["Autopilot Engineer", "Embedded Software Engineer", "Full Stack Web"],
        "culture": "High urgency, hands-on engineering, fast prototyping, zero bureaucracy.",
        "difficulty": "Hard",
        "rounds": ["Recruiter Screening", "Technical Deep Dive", "Presentation / Coding Loop"],
        "top_topics": ["C++ / Python", "Real-Time Systems", "Control Loops & State Machines", "Computer Vision"],
        "sample_questions": [
            "Write a thread-safe circular buffer for sensor data streaming.",
            "Design real-time telemetry processing pipeline for fleet telemetry.",
            "How do you perform under tight deadline constraints with ambiguous specs?"
        ]
    },
    {
        "id": "uber",
        "name": "Uber",
        "domain": "uber.com",
        "roles": ["Backend Engineer", "Infrastructure Engineer", "Mobile Engineer"],
        "culture": "Geospatial routing at scale, real-time matching, microservice resilience.",
        "difficulty": "Hard",
        "rounds": ["OA / Phone Screen", "System Architecture", "Coding Loop", "ManagerialSTAR"],
        "top_topics": ["Geospatial Indexing (H3/Quadtree)", "High Concurrency", "Distributed Databases", "System Architecture"],
        "sample_questions": [
            "Design a ride-matching system for drivers and riders in real time.",
            "Implement a thread-safe Rate Limiter token bucket.",
            "How do you debug high tail latency in distributed microservices?"
        ]
    }
]

@router.get("/companies")
async def get_companies(
    search: str = Query(None),
    query: str = Query(None),
    user: dict = Depends(get_current_user_optional)
):
    search_term = search or query
    if not search_term or not search_term.strip():
        return {"companies": COMPANIES_DATA}
    
    term_lower = search_term.lower().strip()
    filtered = [
        c for c in COMPANIES_DATA
        if term_lower in c["name"].lower() or any(term_lower in r.lower() for r in c.get("roles", []))
    ]
    return {"companies": filtered}

@router.get("/companies/{company_id}")
async def get_company_detail(
    company_id: str,
    user: dict = Depends(get_current_user_optional)
):
    company = next((c for c in COMPANIES_DATA if c["id"] == company_id.lower()), None)
    if not company:
        return COMPANIES_DATA[0]
    return company
