"""
CareerPilot AI — Technical Assessments & Mock Drills Router
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.dependencies import get_current_user
from app.schemas.models import AssessmentSubmitRequest
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


MOCK_TESTS_CATALOG = [
    {
        "id": "dsa",
        "title": "Data Structures & Algorithms Core Assessment",
        "category": "Algorithms",
        "questions_count": 5,
        "time_limit": "20 mins",
        "difficulty": "Hard",
        "questions": [
            {
                "id": 1,
                "q": "Which data structure offers average O(1) time complexity for lookup, insert, and delete operations?",
                "options": ["Binary Search Tree", "Hash Table / Map", "Linked List", "Max Heap"],
                "correct": 1,
                "explanation": "Hash tables leverage a hash function to map keys to bucket indices, yielding O(1) average time complexity."
            },
            {
                "id": 2,
                "q": "What is the time complexity of Breadth-First Search (BFS) on a graph with V vertices and E edges?",
                "options": ["O(V * E)", "O(V + E)", "O(V^2)", "O(log V)"],
                "correct": 1,
                "explanation": "BFS visits every vertex once and explores every edge once, taking O(V + E) time."
            },
            {
                "id": 3,
                "q": "What is the primary advantage of a Red-Black Tree over a standard Binary Search Tree?",
                "options": ["O(1) search time", "Guaranteed O(log N) height balancing", "Requires 50% less memory", "Faster array allocation"],
                "correct": 1,
                "explanation": "Red-Black Trees automatically rebalance during insertions/deletions, preventing worst-case O(N) degradation."
            }
        ]
    },
    {
        "id": "react-arch",
        "title": "React.js & Architecture Benchmark",
        "category": "Frontend",
        "questions_count": 4,
        "time_limit": "15 mins",
        "difficulty": "Medium",
        "questions": [
            {
                "id": 1,
                "q": "What triggers a re-render in a React functional component?",
                "options": ["Changes in state, props, or parent context", "Calling a helper utility function", "Mutating a regular let variable", "Inspecting DOM nodes"],
                "correct": 0,
                "explanation": "React components re-render whenever state updates (useState), prop values change, or parent context values mutate."
            },
            {
                "id": 2,
                "q": "What is the primary purpose of the useMemo hook?",
                "options": ["To create side effects on mount", "To memoize expensive calculations between renders", "To replace Redux store", "To lazy load components"],
                "correct": 1,
                "explanation": "useMemo caches the result of a calculation between renders unless dependencies change."
            }
        ]
    },
    {
        "id": "sql-db",
        "title": "SQL Performance & Database Design Drill",
        "category": "Database",
        "questions_count": 4,
        "time_limit": "15 mins",
        "difficulty": "Medium",
        "questions": [
            {
                "id": 1,
                "q": "Which SQL clause is used to filter aggregate query results (e.g. after GROUP BY)?",
                "options": ["WHERE", "HAVING", "ORDER BY", "FILTER BY"],
                "correct": 1,
                "explanation": "WHERE filters rows before aggregation, while HAVING filters aggregated groups after GROUP BY execution."
            }
        ]
    }
]


@router.get("/tests")
async def get_tests():
    """Retrieve available technical assessment drills."""
    return {"tests": MOCK_TESTS_CATALOG}


@router.post("/submit")
async def submit_assessment(
    payload: AssessmentSubmitRequest,
    user: dict = Depends(get_current_user)
):
    """
    Record completed assessment results and recalculate candidate Career Readiness Score.
    """
    uid = user["uid"]
    test_id = payload.test_id
    test_title = payload.test_title
    score = payload.score
    category = payload.category
    total_q = payload.total_questions
    correct = payload.correct_count

    try:
        from app.core.firebase import get_firestore
        from app.services.scoring_service import calculate_job_readiness_score

        db = get_firestore()
        record_id = f"test_{int(datetime.utcnow().timestamp())}"
        test_record = {
            "id": str(uuid.uuid4()),
            "record_id": record_id,
            "test_id": test_id,
            "test_title": test_title,
            "category": category,
            "score": score,
            "total_questions": total_q,
            "correct_count": correct,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store test record under assessments/{uid}/records
        db.collection(f"assessments/{uid}/records").document(record_id).set(test_record)

        # Recalculate Career Readiness Score
        profile_doc = db.collection("profiles").document(uid).get()
        profile = profile_doc.to_dict() if profile_doc.exists else {"uid": uid}
        profile["uid"] = uid
        readiness = calculate_job_readiness_score(profile, action_reason=f"Completed {test_title} ({int(score)}%)")
        db.collection("jobScores").document(uid).set({
            **readiness.model_dump(),
            "uid": uid,
            "updated_at": datetime.utcnow().isoformat(),
        })

        return {
            "success": True,
            "test_id": test_id,
            "score": score,
            "readiness_score": readiness.total_score,
            "message": "Assessment score recorded and Career Readiness Score recalculated."
        }
    except Exception as e:
        logger.error(f"Failed to record assessment for uid={uid}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to record assessment.")


@router.get("/history")
async def get_assessment_history(user: dict = Depends(get_current_user)):
    """Fetch completed assessment history strictly for authenticated user."""
    uid = user["uid"]
    try:
        from app.core.firebase import get_firestore
        db = get_firestore()
        docs = db.collection(f"assessments/{uid}/records").stream()
        results = [d.to_dict() for d in docs if d.to_dict()]
        return {"uid": uid, "assessments": results}
    except Exception as e:
        logger.error(f"Failed to fetch assessments history for uid={uid}: {e}")
        return {"uid": uid, "assessments": []}

