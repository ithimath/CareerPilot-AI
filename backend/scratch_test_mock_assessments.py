import asyncio
import httpx
import json
import jwt
from app.core.config import settings

BASE_URL = "http://127.0.0.1:8000"

async def run_tests():
    token = jwt.encode(
        {"sub": "test_user_alex_123", "email": "alex@example.com", "aud": "authenticated"},
        settings.SUPABASE_JWT_SECRET or "test_secret",
        algorithm="HS256"
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        print("=== 1. Test GET /api/assessments/tests ===")
        r = await client.get("/api/assessments/tests")
        assert r.status_code == 200, f"Failed: {r.text}"
        data = r.json()
        tests = data.get("tests", [])
        assert len(tests) == 6, f"Expected 6 tests, got {len(tests)}"
        for t in tests:
            assert t["time_limit_seconds"] == 600, f"Expected 600s time limit, got {t['time_limit_seconds']}"
            assert t.get("open_ended_count") == 3, f"Expected 3 open-ended questions, got {t.get('open_ended_count')}"
            print(f"  [OK] Test '{t['id']}': {t['title']} | Time: {t['time_limit_seconds']}s | MCQs: {t['questions_count']} | Open-Ended: {t['open_ended_count']}")

        print("\n=== 2. Test GET /api/assessments/tests/full-stack ===")
        r = await client.get("/api/assessments/tests/full-stack", headers=headers)
        assert r.status_code == 200, f"Failed: {r.text}"
        fs_test = r.json()
        assert "questions" in fs_test
        assert "open_ended_questions" in fs_test
        assert len(fs_test["open_ended_questions"]) == 3
        print(f"  [OK] Full-Stack Test fetched: {len(fs_test['questions'])} MCQs, {len(fs_test['open_ended_questions'])} open-ended scenarios.")
        for oq in fs_test["open_ended_questions"]:
            print(f"       - Q{oq['id']}: {oq['title']} (Rubrics: {', '.join(oq['rubric_focus'])})")

        print("\n=== 3. Test POST /api/assessments/start-session ===")
        r = await client.post("/api/assessments/start-session", json={"test_id": "full-stack"}, headers=headers)
        assert r.status_code == 200, f"Failed: {r.text}"
        sess_data = r.json()
        assert "session_id" in sess_data
        assert sess_data["time_limit_seconds"] == 600
        session_id = sess_data["session_id"]
        print(f"  [OK] Started session: {session_id}, expires at: {sess_data['expires_at']}")

        print("\n=== 4. Test POST /api/assessments/submit with MCQs & Open-Ended Answers ===")
        # Prepare submission: 3 correct MCQs, 3 open-ended detailed answers
        mcq_answers = {"0": 1, "1": 2, "2": 1} # IDs/indices
        open_ended_answers = [
            {
                "question_id": 101,
                "question": "Real-Time Collaborative Document Sync",
                "answer": (
                    "We choose Conflict-free Replicated Data Types (CRDTs), specifically Yjs with state vectors, "
                    "because CRDTs support peer-to-peer and client-server synchronization without requiring a single "
                    "centralized serialization bottleneck like Operational Transformation (OT). For the WebSocket "
                    "protocol, we send differential updates (binary encoded Yjs updates) and maintain client-side "
                    "optimistic updates. To handle offline reconnections, clients buffer mutations in IndexedDB and "
                    "upon reconnect exchange state vectors to merge only missing deltas. Edge cases like packet drops "
                    "are naturally resolved by CRDT commutativity and idempotency, while document snapshots are "
                    "periodically flushed to PostgreSQL."
                )
            },
            {
                "question_id": 102,
                "question": "React Performance Optimization",
                "answer": (
                    "First, we profile using Chrome DevTools Performance panel to record Interaction to Next Paint (INP) "
                    "and identify long tasks (>50ms). We isolate live WebSocket ticker updates by decoupling state using "
                    "external stores with useSyncExternalStore or Zustand, preventing root re-renders. High-frequency chart "
                    "data points are offloaded to Web Workers for data crunching. We introduce windowing/virtualization "
                    "(TanStack Virtual) so only visible widgets are rendered, and wrap user search inputs in React 18 "
                    "useTransition/useDeferredValue so high-priority typing is never blocked by chart recalculations."
                )
            },
            {
                "question_id": 103,
                "question": "Resilient Microservices Payment Gateway",
                "answer": (
                    "To prevent double charges, every checkout request generates a UUID v4 idempotency key passed in the "
                    "Idempotency-Key header, stored atomically in Redis with a 24-hour TTL and verified in PostgreSQL. "
                    "When the payment gateway times out (HTTP 504), we apply exponential backoff with full jitter up to 3 "
                    "retries, governed by a circuit breaker (e.g. Resilience4j or PyBreaker) to avoid cascading gateway failure. "
                    "If a timeout occurs after card charge, our system does not immediately refund or retry blindly; instead, "
                    "it enqueues the transaction to a reconciliation Dead Letter Queue (DLQ) and polls the gateway's status "
                    "API or relies on verified webhook callbacks to reconcile before marking the order status."
                )
            }
        ]

        submit_payload = {
            "test_id": "full-stack",
            "test_title": "Full-Stack Engineer Assessment",
            "career_path": "Full-Stack Engineer",
            "category": "Full-Stack",
            "score": 0.0,
            "total_questions": len(fs_test["questions"]),
            "correct_count": 0,
            "incorrect_count": 0,
            "time_taken": 240,
            "session_id": session_id,
            "mcq_answers": mcq_answers,
            "open_ended_answers": open_ended_answers,
        }

        r = await client.post("/api/assessments/submit", json=submit_payload, headers=headers)
        assert r.status_code == 200, f"Submit failed: {r.text}"
        res = r.json()
        assert res["success"] is True
        assert "mcq_score" in res
        assert "open_ended_score" in res
        assert "score" in res
        assert "open_ended_evaluations" in res
        assert len(res["open_ended_evaluations"]) == 3

        print(f"  [OK] Assessment submitted successfully!")
        print(f"       - MCQ Score: {res['mcq_score']}% ({res['correct_count']} correct)")
        print(f"       - Open-Ended Score: {res['open_ended_score']}%")
        print(f"       - Composite Overall Score: {res['score']}%")
        print(f"       - Readiness Score updated to: {res['readiness_score']}")

        for ev in res["open_ended_evaluations"]:
            print(f"\n       Scenario Review [{ev['question_title']}]:")
            print(f"         Correctness: {ev['correctness']}/20 | Reasoning: {ev['reasoning']}/20 | Depth: {ev['technical_understanding']}/20")
            print(f"         Relevance: {ev['relevance']}/20 | Completeness: {ev['completeness']}/20 | Total: {ev['score']}/100")
            print(f"         Feedback: {ev['feedback']}")

        print("\n=== 5. Test Duplicate Submission Rejection ===")
        dup_r = await client.post("/api/assessments/submit", json=submit_payload, headers=headers)
        assert dup_r.status_code == 409, f"Expected 409 for duplicate session, got {dup_r.status_code}"
        print(f"  [OK] Duplicate submission correctly rejected with HTTP 409: {dup_r.json().get('detail')}")

if __name__ == "__main__":
    asyncio.run(run_tests())
