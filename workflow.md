# CareerPilot AI — System Workflow & Architecture

## Stack Summary

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite + TypeScript |
| Styling | Vanilla CSS (design system in `index.css`) |
| State & Data | TanStack Query v5 |
| Auth (client) | Supabase JS (`@supabase/supabase-js`) |
| Auth (server) | Supabase JWT verified via `PyJWT` (`backend/app/core/supabase.py`) |
| Backend | FastAPI (Python 3.11+) |
| Database | Firebase Firestore (production) / MockFirestoreClient JSON file (dev) |
| ML Engine | Scikit-learn Random Forest + TF-IDF semantic scoring |

> **Note on "Firebase Auth":** The project name says "Firebase Authentication" but the auth stack is actually **Supabase**. Firebase Admin SDK is used only for Firestore data storage (not auth). In development (without a service account), the backend uses `MockFirestoreClient` which stores data in `backend/data/user_datastore.json`.

---

## User Authentication Flow

```
Browser                     FastAPI Backend          Supabase
  │                              │                      │
  │  signup(email, password)     │                      │
  │─────────────────────────────────────────────────►  │
  │                              │                 signUp()
  │                              │                      │
  │◄── session (JWT) ─────────────────────────────────  │
  │                              │                      │
  │  POST /api/auth/create-profile                       │
  │  (Bearer: Supabase JWT)      │                      │
  │─────────────────────────────►│                      │
  │                          verify JWT                  │
  │                         (supabase.py)                │
  │                              │                      │
  │                         create profiles/{uid}       │
  │                         create jobScores/{uid}      │
  │                         (both zero-initialized)     │
  │◄── { created: true } ───────│                      │
```

### Login Flow

```
Browser → supabase.auth.signInWithPassword() → Supabase returns JWT
AuthContext.onAuthStateChange fires → setUser() → localStorage cp_active_uid = uid
All subsequent API calls include Authorization: Bearer <JWT>
FastAPI verifies JWT → extracts uid → uses uid for ALL Firestore ops
```

### Logout Flow

```
AuthContext.logout():
  1. Reads cp_active_uid from localStorage
  2. Deletes cp_user_score_{uid}, cp_user_history_{uid}, cp_mock_profile_{uid}
  3. Calls supabase.auth.signOut()
  4. Clears user state → ProtectedRoute redirects to /login
```

---

## Firestore Data Schema

All documents are keyed by the authenticated UID. No anonymous or cross-user access is possible due to Firestore rules.

```
Firestore Root
│
├── profiles/{uid}                         # User profile document
│   ├── uid: string
│   ├── name, email, college, degree, department
│   ├── current_year: int, cgpa: float
│   ├── skills: [{name, level, verified, source}]
│   ├── projects: [{title, description, github_url, live_url, technologies}]
│   ├── internships: [{company, role, duration, start_date, end_date}]
│   ├── certifications: [{...}]
│   ├── github_url, linkedin_url, portfolio_url
│   ├── target_career: string
│   └── created_at, updated_at: ISO timestamps
│
├── jobScores/{uid}                        # Career Readiness Score (0–100)
│   ├── uid: string
│   ├── total_score: float (Max 100)
│   ├── skills_score: float (Max 25)
│   ├── projects_score: float (Max 20)
│   ├── interviews_score: float (Max 20)
│   ├── resume_score: float (Max 15)
│   ├── assessments_score: float (Max 10)
│   ├── certificates_score: float (Max 10)
│   ├── confidence_level: string
│   ├── prediction_method: string
│   ├── positive_drivers: string[]
│   ├── suggestions: string[]
│   ├── history: [{timestamp, total_score, delta, reason}]
│   └── updated_at: ISO timestamp
│
├── certificates/{certId}                  # Certificate metadata
│   └── uid: string  ← must match owner
│
├── assessments/{uid}/records/{recordId}   # Mock test attempts
│   ├── test_id, test_title, career_path
│   ├── score: float (percentage)
│   ├── correct_count, incorrect_count, total_questions
│   ├── time_taken: int (seconds)
│   ├── topic_breakdown: {topic: {correct, total}}
│   ├── difficulty_breakdown: {easy/medium/hard: {correct, total}}
│   └── timestamp: ISO string
│
├── interviews/{uid}/sessions/{sessionId}  # AI mock interview sessions
│
├── resumes/{uid}/versions/{versionId}     # ATS resume scans
│
└── users/{uid}/mockTests/{attemptId}      # (Legacy path — now uses assessments/)
```

---

## Career Readiness Score Calculation

Score is computed by `backend/app/services/scoring_service.py` (backend) and mirrored by `computeMockJobScore()` in `frontend/src/lib/api.ts` (offline fallback).

### Scoring Dimensions (Total: 100 pts)

| Dimension | Max | Source |
|-----------|-----|--------|
| Skills (TF-IDF weighted by proficiency) | 25 | `profile.skills[]` |
| Projects (quality rubric: desc length, GitHub, live URL) | 20 | `profile.projects[]` |
| AI Mock Interviews | 20 | `interviews/{uid}/sessions` |
| Resume ATS Score | 15 | `resumes/{uid}/versions` |
| Technical Assessments | 10 | `assessments/{uid}/records` |
| Industry Certifications | 10 | `certificates/{certId}` |

### Zero-State Rule

**New users always start at exactly 0.** This is enforced by:
1. `backend/app/routers/auth.py` — `POST /api/auth/create-profile` writes a zero-initialized `jobScores/{uid}` document on every new signup (idempotent: skips if doc already exists)
2. `frontend/src/lib/api.ts` — `getMockProfile(uid)` returns an empty profile for unknown UIDs; `computeMockJobScore` on an empty profile returns 0 for all dimensions

### Score Update Triggers

Score is recalculated by the backend when:
- Profile is updated (`PUT /api/profile`) — skills, projects, etc.
- Assessment is submitted (`POST /api/assessments/submit`)
- Interview session is saved (`POST /api/interview/save-session`)
- Resume ATS scan is completed (`POST /api/resume/analyze-ats`)

---

## Mock Test System (Phase 6)

### Flow

```
User opens MockTestsPage
→ GET /api/assessments/tests  (catalog, no questions in response)
→ User clicks "Start Assessment" for a career path
→ GET /api/assessments/tests/{test_id}  (requires auth; returns full questions)
→ 25-minute countdown timer starts
→ User answers questions (can flag, navigate freely)
→ Timer reaches 0 OR user clicks "Submit"
→ computeAndSubmit() calculates:
    - score (percentage of correct answers)
    - topic_breakdown, difficulty_breakdown
    - time_taken
→ POST /api/assessments/submit  → backend persists record + recalculates score
→ Result screen: score circle, difficulty bars, topic progress, full answer review
```

### Career Paths & Question Count

| Path | Questions | Time |
|------|-----------|------|
| Full-Stack Engineer | 22 | 25 min |
| AI/ML Engineer | 22 | 25 min |
| Backend Developer | 22 | 25 min |
| Frontend Developer | 22 | 25 min |
| Data Scientist | 22 | 25 min |
| Cloud Engineer | 22 | 25 min |

Each test has: ~30% easy, ~50% medium, ~20% hard questions.

---

## API Fallback Layer

When the FastAPI backend is unreachable, `frontend/src/lib/api.ts` intercepts failed requests and returns mock data. **Critical data isolation rules (post-fix):**

1. **Per-UID profile store**: Each user gets their own empty profile (in `mockProfileStore[uid]`). Alex Morgan's demo data is NOT returned for unknown users.
2. **Score isolation**: `computeMockJobScore()` only reads from the user's own profile's `certifications[]` array — never a shared cert store.
3. **Correct delta**: Assessment history deltas are computed as `newTotal - prevTotal`, not hardcoded 8.0.

---

## Security Data Isolation Guarantees

| Layer | Guarantee |
|-------|-----------|
| Firestore rules | Each `{uid}` path verified against `request.auth.uid` |
| Backend auth | Every route with `Depends(get_current_user)` extracts `uid` from Supabase JWT — no client-supplied uid is trusted |
| Frontend AuthContext | No fake/shared UIDs — auth failures throw visible errors |
| Logout | Per-user localStorage keys cleared on logout to prevent leftover data on shared devices |

---

## Known Fragile Points / Regression Risks

1. **MockFirestoreClient** (`backend/app/core/firebase.py`): In development, data is stored in `backend/data/user_datastore.json`. This file is shared across the dev session. If testing multi-user isolation locally, clear this file between user tests.

2. **Supabase unconfigured**: If `VITE_SUPABASE_URL` is not set in `.env`, `supabase.ts` uses placeholder values. Login and signup will fail with a Supabase error message (this is correct behavior — no fake sessions are created).

3. **Score fallback vs. live score**: If the backend is down, the frontend falls back to `computeMockJobScore()`. This score is an approximation and will differ from the backend's ML-computed score. It is saved to `localStorage` only — never to Firestore.

4. **Assessment correct-answer validation**: Currently, `correct_count` and `score` are computed client-side in `MockTestsPage.tsx` and submitted to the backend. The backend stores them without re-validation. For a production security model, answers should be submitted individually to the backend for server-side validation.

---

## Running the Project

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

**frontend/.env**
```
VITE_SUPABASE_URL=https://<your-project>.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
VITE_API_BASE_URL=http://localhost:8000
```

**backend/.env**
```
SUPABASE_URL=https://<your-project>.supabase.co
SUPABASE_SERVICE_KEY=<your-service-role-key>
FIREBASE_SERVICE_ACCOUNT_PATH=path/to/serviceAccount.json  # Optional; uses mock if absent
```
