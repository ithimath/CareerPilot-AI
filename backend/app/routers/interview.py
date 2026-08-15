"""
CareerPilot AI — AI Interview Simulator Router
Real-time evidence-based interview response evaluator.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.dependencies import get_current_user_optional
from app.services.gemini_service import call_gemini_json
import logging
import re

logger = logging.getLogger(__name__)
router = APIRouter()

QUESTION_KEYWORDS = {
    "rest": ["http", "endpoint", "json", "status", "middleware", "auth", "token", "jwt", "post", "get", "put", "delete", "rate limit", "swagger", "fastapi", "express", "router", "controller"],
    "memory": ["event loop", "closure", "async", "await", "promise", "memory", "heap", "garbage collection", "leak", "pointer", "thread", "process", "stack", "concurrency", "cpu", "profiler"],
    "database": ["index", "n+1", "join", "postgresql", "sql", "query", "table", "b-tree", "partition", "replica", "transaction", "orm", "sharding", "migration", "cache", "redis"],
    "debug": ["trace", "log", "stack trace", "reproduce", "profiler", "debugger", "test", "unit test", "regression", "root cause", "fix", "git", "issue", "reproduction"],
    "behavioral": ["situation", "task", "action", "result", "team", "conflict", "resolution", "deadline", "trade-off", "communicated", "collaborated", "delivered", "outcome", "feedback"],
    "system_design": ["scale", "load balancer", "cdn", "cache", "redis", "microservice", "queue", "kafka", "database", "partition", "sharding", "latency", "throughput", "failover", "redundancy", "websocket"]
}

def evaluate_realistically_fallback(question: str, answer: str, role: str) -> dict:
    clean_ans = answer.strip().toLowerCase() if hasattr(answer, "toLowerCase") else answer.strip().lower()
    
    # 1. Check for empty, gibberish or low effort input
    if len(clean_ans) < 15:
        return {
            "score": 10,
            "clarity": 15,
            "technical_accuracy": 5,
            "feedback": "Your response is too brief to evaluate candidate technical competency. Please provide a detailed response explaining your technical approach.",
            "sample_answer": f"For '{question}', a strong technical answer defines the core problem, states architectural choices (e.g. framework, caching, data model), and explains trade-offs."
        }

    # Check for character repetition or keyboard smashes
    letters_only = re.sub(r'[^a-z]', '', clean_ans)
    unique_chars = len(set(letters_only))
    words = clean_ans.split()
    max_word_len = max(len(w) for w in words) if words else 0

    is_low_effort = (
        unique_chars < 6 and len(letters_only) > 15 or
        max_word_len > 25 or
        clean_ans in ["idk", "i dont know", "i don't know", "no idea", "asdfghjkl", "qwertyuiop", "testing", "pass"]
    )

    if is_low_effort:
        return {
            "score": 12,
            "clarity": 10,
            "technical_accuracy": 5,
            "feedback": "Your input contains non-technical text or low-effort filler content. Candidate technical evaluation requires articulating relevant principles, algorithms, or architectural patterns.",
            "sample_answer": f"A comprehensive response for '{question}': Articulate the specific domain concepts, mention tools/frameworks, and highlight measurable outcomes."
        }

    # 2. Count technical keyword matches
    matched_keywords = []
    q_lower = question.lower()

    # Determine topic domain keywords
    relevant_domain = []
    if "api" in q_lower or "rest" in q_lower:
        relevant_domain.extend(QUESTION_KEYWORDS["rest"])
    if "memory" in q_lower or "async" in q_lower or "bug" in q_lower:
        relevant_domain.extend(QUESTION_KEYWORDS["memory"])
        relevant_domain.extend(QUESTION_KEYWORDS["debug"])
    if "database" in q_lower or "query" in q_lower or "sql" in q_lower or "n+1" in q_lower:
        relevant_domain.extend(QUESTION_KEYWORDS["database"])
    if "conflict" in q_lower or "team" in q_lower or "project" in q_lower or "behavioral" in q_lower:
        relevant_domain.extend(QUESTION_KEYWORDS["behavioral"])
    if "design" in q_lower or "scale" in q_lower or "architecture" in q_lower:
        relevant_domain.extend(QUESTION_KEYWORDS["system_design"])

    if not relevant_domain:
        # Default fallback list across common engineering terms
        relevant_domain = QUESTION_KEYWORDS["rest"] + QUESTION_KEYWORDS["database"] + QUESTION_KEYWORDS["system_design"]

    for kw in set(relevant_domain):
        if kw in clean_ans:
            matched_keywords.append(kw)

    match_count = len(matched_keywords)

    # 3. Dynamic Score Calculation
    if match_count == 0:
        score = min(38, max(20, 25 + len(words) // 5))
        clarity = min(45, max(30, 35 + len(words) // 4))
        tech_acc = 18
        feedback = f"Your response is well-formed grammatically, but lacks core technical keywords (such as {', '.join(relevant_domain[:3])}) expected for a {role} candidate."
    elif match_count <= 2:
        score = min(68, max(45, 50 + match_count * 8))
        clarity = min(75, 60 + match_count * 5)
        tech_acc = min(65, 45 + match_count * 10)
        feedback = f"Partial technical alignment. You correctly mentioned {', '.join(matched_keywords)}. To improve your grade, expand on implementation trade-offs and edge-case handling."
    elif match_count <= 4:
        score = min(85, 72 + match_count * 3)
        clarity = min(88, 75 + match_count * 3)
        tech_acc = min(84, 70 + match_count * 3)
        feedback = f"Strong technical response! You demonstrated solid understanding by referencing {', '.join(matched_keywords)}. Consider detailing performance metrics or unit test coverage for top score."
    else:
        score = min(96, 88 + (match_count - 4) * 2)
        clarity = min(95, 86 + match_count * 2)
        tech_acc = min(94, 85 + match_count * 2)
        feedback = f"Excellent, industry-ready answer! Outstanding coverage of key concepts ({', '.join(matched_keywords[:5])}) with clear structural articulation."

    return {
        "score": score,
        "clarity": clarity,
        "technical_accuracy": tech_acc,
        "feedback": feedback,
        "sample_answer": f"Benchmark response for '{question}': 1. State core system requirements. 2. Explain technical choices ({', '.join(relevant_domain[:3])}). 3. Highlight scalability and error handling."
    }

@router.post("/start")
async def start_interview(
    payload: dict = Body(...),
    user: dict = Depends(get_current_user_optional)
):
    role = payload.get("role", "Software Engineer")
    category = payload.get("category", "technical")
    
    questions = {
        "technical": [
            f"Explain how you would design a RESTful API for a high-traffic {role} application.",
            "How do you handle memory management and asynchronous operations in your primary programming language?",
            "Describe a complex technical bug you encountered recently and how you debugged and resolved it."
        ],
        "behavioral": [
            "Tell me about a time you had a conflict with a team member on a technical decision. How did you resolve it?",
            "Describe a project where requirements changed midway. How did you adapt?",
            "Give an example of a goal you set and how you achieved it under a tight deadline."
        ],
        "system_design": [
            "How would you design a scalable notification service like WhatsApp or Slack?",
            "Explain how caching (Redis/Memcached) fits into a modern web application architecture.",
            "How would you handle database partitioning and replication for millions of daily active users?"
        ]
    }
    
    selected_qs = questions.get(category, questions["technical"])
    return {
        "role": role,
        "category": category,
        "questions": selected_qs,
        "first_question": selected_qs[0]
    }

@router.post("/evaluate")
async def evaluate_answer(
    payload: dict = Body(...),
    user: dict = Depends(get_current_user_optional)
):
    question = payload.get("question", "")
    answer = payload.get("answer", "")
    role = payload.get("role", "Software Engineer")

    if not answer or len(answer.strip()) == 0:
        return {
            "score": 0,
            "clarity": 0,
            "technical_accuracy": 0,
            "feedback": "No response submitted. Candidate score is 0.",
            "sample_answer": "Provide a structured technical response demonstrating problem-solving logic and engineering principles."
        }

    prompt = f"""
    You are a Senior Technical Interviewer assessing a candidate for a {role} role.
    Question: "{question}"
    Candidate Answer: "{answer}"

    Analyze the candidate's answer for correctness, technical accuracy, conciseness, and depth.
    CRITICAL: If the answer is random gibberish, keyboard smashing (e.g. "asdfghjkl"), off-topic text, or extremely low effort, give a low score between 0 and 20.
    
    Return JSON with:
    - score (0-100)
    - clarity (0-100)
    - technical_accuracy (0-100)
    - feedback (detailed constructive breakdown highlighting specific strengths and missing concepts)
    - sample_answer (an ideal candidate response using STAR method or industry best practices)
    """

    eval_result = None
    try:
        res = await call_gemini_json(prompt)
        if isinstance(res, dict) and "score" in res:
            eval_result = res
        else:
            eval_result = evaluate_realistically_fallback(question, answer, role)
    except Exception as e:
        logger.warning(f"Gemini evaluation unavailable, using realistic fallback evaluator: {e}")
        eval_result = evaluate_realistically_fallback(question, answer, role)

    # Auto-record session if authenticated
    uid = user.get("uid") if user else None
    if uid and eval_result:
        try:
            import uuid
            from datetime import datetime
            from app.core.firebase import get_firestore
            from app.services.scoring_service import calculate_job_readiness_score

            db = get_firestore()
            session_id = payload.get("session_id") or f"sess_{int(datetime.utcnow().timestamp())}"
            rec = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "role": role,
                "category": payload.get("category", "technical"),
                "question": question,
                "score": eval_result.get("score", 0),
                "overall_score": eval_result.get("score", 0),
                "clarity": eval_result.get("clarity", 0),
                "technical_accuracy": eval_result.get("technical_accuracy", 0),
                "feedback": eval_result.get("feedback", ""),
                "timestamp": datetime.utcnow().isoformat(),
            }
            db.collection(f"interviews/{uid}/sessions").document(session_id).set(rec)

            # Update score in background
            profile_doc = db.collection("profiles").document(uid).get()
            profile = profile_doc.to_dict() if profile_doc.exists else {"uid": uid}
            profile["uid"] = uid
            score = calculate_job_readiness_score(profile, action_reason="Completed AI Mock Interview")
            db.collection("jobScores").document(uid).set({
                **score.model_dump(),
                "uid": uid,
                "updated_at": datetime.utcnow().isoformat(),
            })
            eval_result["readiness_score"] = score.total_score
        except Exception as e:
            logger.warning(f"Auto-saving interview session failed: {e}")

    return eval_result


@router.post("/save-session")
async def save_interview_session(
    payload: dict = Body(...),
    user: dict = Depends(get_current_user_optional)
):
    """Explicitly save a completed multi-question interview session."""
    uid = user.get("uid", "dev-user-id")
    try:
        import uuid
        from datetime import datetime
        from app.core.firebase import get_firestore
        from app.services.scoring_service import calculate_job_readiness_score

        db = get_firestore()
        session_id = payload.get("session_id") or f"sess_{int(datetime.utcnow().timestamp())}"
        score = float(payload.get("overall_score", payload.get("score", 75.0)))
        rec = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": payload.get("role", "Software Engineer"),
            "category": payload.get("category", "technical"),
            "overall_score": score,
            "score": score,
            "clarity": float(payload.get("clarity", 80.0)),
            "technical_accuracy": float(payload.get("technical_accuracy", 80.0)),
            "feedback": payload.get("feedback", "Session completed."),
            "questions_count": int(payload.get("questions_count", 3)),
            "timestamp": datetime.utcnow().isoformat(),
        }
        db.collection(f"interviews/{uid}/sessions").document(session_id).set(rec)

        profile_doc = db.collection("profiles").document(uid).get()
        profile = profile_doc.to_dict() if profile_doc.exists else {"uid": uid}
        profile["uid"] = uid
        readiness = calculate_job_readiness_score(profile, action_reason="Completed Mock Interview loop")
        db.collection("jobScores").document(uid).set({
            **readiness.model_dump(),
            "uid": uid,
            "updated_at": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "session_id": session_id,
            "readiness_score": readiness.total_score,
            "message": "Interview session saved and readiness score recalculated."
        }
    except Exception as e:
        logger.error(f"Failed to save interview session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_interview_history(user: dict = Depends(get_current_user_optional)):
    """Fetch completed interview history for user."""
    uid = user.get("uid", "dev-user-id")
    try:
        from app.core.firebase import get_firestore
        db = get_firestore()
        docs = db.collection(f"interviews/{uid}/sessions").stream()
        results = [d.to_dict() for d in docs if d.to_dict()]
        return {"uid": uid, "sessions": results}
    except Exception as e:
        logger.error(f"Failed to get interview history: {e}")
        return {"uid": uid, "sessions": []}

