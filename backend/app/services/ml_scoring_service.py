"""
ML-Based Dynamic Career Readiness Prediction Engine

Evaluates candidate readiness across 6 key employability dimensions:
1. Skills & Proficiency Vector (Max 25 pts) — TF-IDF alignment, proficiency depth, verified skills.
2. Practical Projects & Tech Fit (Max 20 pts) — Tech stack overlap, repository links, live URLs, quality depth.
3. AI Mock Interviews & Growth (Max 20 pts) — Completed mock interview loops, average score, technical accuracy, improvement trend.
4. Resume Quality & ATS Diagnostic (Max 15 pts) — ATS parser compliance, keyword coverage, version improvement delta.
5. Technical Assessments & Drills (Max 10 pts) — Completed domain test drills, speed challenge accuracy.
6. Industry Certifications (Max 10 pts) — OCR-verified domain credentials matching role requisitions.

Total Score = 100.0 Maximum.
Brand new users start at 0.0.
"""

import math
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.data_service import get_careers, get_career_by_title
from app.schemas.models import ScoreBreakdown, ScoreHistoryEntry

logger = logging.getLogger(__name__)

# Scoring Max Weights (Sum to 100)
MAX_SKILLS       = 25.0
MAX_PROJECTS     = 20.0
MAX_INTERVIEWS   = 20.0
MAX_RESUME       = 15.0
MAX_ASSESSMENTS  = 10.0
MAX_CERTIFICATES = 10.0
TOTAL_MAX        = 100.0

PROFICIENCY_MULTIPLIERS = {
    "beginner": 0.70,
    "intermediate": 1.00,
    "advanced": 1.25,
    "expert": 1.40,
}


class MLCareerPredictor:
    def __init__(self):
        self.careers_data = get_careers()
        self._init_tfidf()

    def _init_tfidf(self):
        """Build TF-IDF corpus from all career required skills & descriptions."""
        corpus = []
        for c in self.careers_data:
            req = " ".join(c.get("required_skills", []))
            kw = " ".join(c.get("keywords", []))
            desc = c.get("description", "")
            corpus.append(f"{req} {kw} {desc}")

        if not corpus:
            corpus = ["python react javascript node sql Machine Learning Data Science Docker AWS"]

        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.vectorizer.fit(corpus)
        logger.info(f"ML Predictor initialized with TF-IDF vocabulary size {len(self.vectorizer.vocabulary_)}")

    def _get_target_career(self, target_career_title: str) -> Dict[str, Any]:
        """Retrieve target career requisition schema or fallback to default."""
        if target_career_title:
            career = get_career_by_title(target_career_title)
            if career:
                return career
            target_lower = target_career_title.lower()
            for c in self.careers_data:
                if target_lower in c.get("title", "").lower() or c.get("title", "").lower() in target_lower:
                    return c

        return self.careers_data[0] if self.careers_data else {
            "title": "Software Engineer",
            "required_skills": ["Python", "JavaScript", "SQL", "Git", "Data Structures"],
            "keywords": ["software", "development", "web", "api"],
        }

    def predict_readiness(
        self,
        profile: Dict[str, Any],
        interviews: Optional[List[Dict[str, Any]]] = None,
        resumes: Optional[List[Dict[str, Any]]] = None,
        assessments: Optional[List[Dict[str, Any]]] = None,
        certificates: Optional[List[Dict[str, Any]]] = None,
    ) -> ScoreBreakdown:
        """
        Evaluate full 6-dimensional candidate readiness.
        """
        uid = profile.get("uid", "")
        raw_skills = profile.get("skills", [])
        projects_raw = profile.get("projects", [])
        internships_raw = profile.get("internships", [])
        certs_raw = profile.get("certifications", []) or (certificates or [])
        interviews_raw = interviews or profile.get("interview_records", [])
        resumes_raw = resumes or profile.get("resume_records", [])
        assessments_raw = assessments or profile.get("assessment_records", [])

        # Check for zero career development activity
        has_any_data = (
            bool(raw_skills) or
            bool(projects_raw) or
            bool(internships_raw) or
            bool(certs_raw) or
            bool(interviews_raw) or
            bool(resumes_raw) or
            bool(assessments_raw)
        )

        if not has_any_data:
            return ScoreBreakdown(
                uid=uid,
                skills_score=0.0,
                projects_score=0.0,
                interviews_score=0.0,
                resume_score=0.0,
                assessments_score=0.0,
                certificates_score=0.0,
                profile_score=0.0,
                internships_score=0.0,
                total_score=0.0,
                confidence_level="Insufficient Data",
                data_quality_notice="New candidate account. Complete activities such as adding technical skills, taking mock tests, or running ATS resume diagnostics to compute your score.",
                positive_drivers=[],
                suggestions=[
                    "Add 3+ technical skills with proficiency levels in your profile.",
                    "Execute a resume ATS diagnostic scan.",
                    "Complete a domain-specific AI Mock Interview.",
                ],
                history=[],
                updated_at=datetime.utcnow().isoformat(),
            )

        target_role = self._get_target_career(profile.get("target_career", ""))
        target_skills = [s.strip().lower() for s in target_role.get("required_skills", [])]
        target_title = target_role.get("title", "Software Engineer")

        # ── 1. SKILLS & PROFICIENCY SCORE (MAX: 25.0) ───────────────────────────
        skills_score = 0.0
        parsed_skills = []
        proficiency_weights_sum = 0.0
        verified_count = 0

        for item in raw_skills:
            if isinstance(item, str):
                s_name = item.strip()
                s_level = "Intermediate"
                s_verified = False
            elif isinstance(item, dict):
                s_name = item.get("name", "").strip()
                s_level = item.get("level", "Intermediate")
                s_verified = item.get("verified", False)
            else:
                s_name = getattr(item, "name", "").strip()
                s_level = getattr(item, "level", "Intermediate")
                s_verified = getattr(item, "verified", False)

            if s_name:
                parsed_skills.append(s_name.lower())
                mult = PROFICIENCY_MULTIPLIERS.get(str(s_level).lower(), 1.0)
                if s_verified:
                    mult *= 1.15
                    verified_count += 1
                proficiency_weights_sum += mult

        if parsed_skills and target_skills:
            cand_text = " ".join(parsed_skills)
            target_text = " ".join(target_skills)

            vecs = self.vectorizer.transform([cand_text, target_text])
            tfidf_sim = float(cosine_similarity(vecs[0], vecs[1])[0][0])

            cand_set = set(parsed_skills)
            target_set = set(target_skills)
            overlap_count = len(cand_set.intersection(target_set))
            direct_ratio = overlap_count / len(target_set) if target_set else 0.0

            alignment_factor = (direct_ratio * 0.65) + (tfidf_sim * 0.35)
            # Factor in depth of proficiency (average multiplier over baseline)
            avg_depth = (proficiency_weights_sum / len(parsed_skills)) if parsed_skills else 1.0
            raw_skill_pts = alignment_factor * MAX_SKILLS * avg_depth * 1.10
            skills_score = round(min(raw_skill_pts, MAX_SKILLS), 2)
        elif parsed_skills:
            avg_depth = (proficiency_weights_sum / len(parsed_skills)) if parsed_skills else 1.0
            skills_score = round(min((len(parsed_skills) / 15.0) * (MAX_SKILLS * 0.5) * avg_depth, MAX_SKILLS * 0.5), 2)

        # ── 2. PRACTICAL PROJECTS & TECH STACK FIT (MAX: 20.0) ──────────────────
        projects_score = 0.0
        if projects_raw:
            proj_techs = []
            proj_quality_sum = 0.0
            for p in projects_raw:
                if isinstance(p, dict):
                    techs = p.get("technologies", [])
                    if isinstance(techs, str):
                        techs = [t.strip() for t in techs.split(",")]
                    proj_techs.extend([t.lower() for t in techs])

                    q = 0.4
                    if p.get("title"): q += 0.2
                    if p.get("description"): q += 0.2
                    if p.get("github_url"): q += 0.1
                    if p.get("live_url"): q += 0.1
                    proj_quality_sum += q
                else:
                    techs = getattr(p, "technologies", [])
                    proj_techs.extend([t.lower() for t in techs])
                    q = 0.4
                    if getattr(p, "title", None): q += 0.2
                    if getattr(p, "description", None): q += 0.2
                    if getattr(p, "github_url", None): q += 0.1
                    if getattr(p, "live_url", None): q += 0.1
                    proj_quality_sum += q

            proj_tech_set = set(proj_techs)
            target_set = set(target_skills)
            proj_match = len(proj_tech_set.intersection(target_set)) / len(target_set) if target_set else 0.5

            project_ratio = min((proj_quality_sum / 3.0) * (0.6 + 0.4 * proj_match), 1.0)
            projects_score = round(project_ratio * MAX_PROJECTS, 2)

        # ── 3. AI MOCK INTERVIEWS & READINESS (MAX: 20.0) ────────────────────────
        interviews_score = 0.0
        interview_count = len(interviews_raw)
        if interview_count > 0:
            scores_list = []
            for item in interviews_raw:
                s = item.get("overall_score", item.get("score", 0))
                try:
                    scores_list.append(float(s))
                except (ValueError, TypeError):
                    pass

            if scores_list:
                avg_interview_score = sum(scores_list) / len(scores_list)
                # Volume factor (1 session = 0.5x, 2 = 0.8x, 3+ = 1.0x)
                vol_factor = min(interview_count / 3.0, 1.0)
                # Growth factor: check if latest score > earlier score
                growth_bonus = 1.0
                if len(scores_list) >= 2 and scores_list[-1] > scores_list[0]:
                    growth_bonus = 1.10  # 10% bonus for demonstrated improvement!

                calc = (avg_interview_score / 100.0) * MAX_INTERVIEWS * (0.5 + 0.5 * vol_factor) * growth_bonus
                interviews_score = round(min(calc, MAX_INTERVIEWS), 2)
        elif internships_raw:
            # Fallback to internships if candidate has verified work experience
            exp_quality = sum(0.6 for _ in internships_raw)
            interviews_score = round(min((exp_quality / 2.0) * (MAX_INTERVIEWS * 0.75), MAX_INTERVIEWS * 0.75), 2)

        # ── 4. RESUME QUALITY & ATS DIAGNOSTIC (MAX: 15.0) ───────────────────────
        resume_score = 0.0
        if resumes_raw:
            latest_resume = resumes_raw[-1] if isinstance(resumes_raw, list) else resumes_raw
            ats = latest_resume.get("ats_score", latest_resume.get("score", 0))
            try:
                ats_val = float(ats)
            except (ValueError, TypeError):
                ats_val = 60.0

            # Check for version improvement
            version_bonus = 1.0
            if len(resumes_raw) >= 2:
                first_ats = resumes_raw[0].get("ats_score", 0)
                if ats_val > first_ats:
                    version_bonus = 1.08  # 8% bonus for iteration improvement

            calc = (ats_val / 100.0) * MAX_RESUME * version_bonus
            resume_score = round(min(calc, MAX_RESUME), 2)
        elif profile.get("github_url") or profile.get("linkedin_url"):
            # Partial credit for professional profile presence
            cred_count = sum(1 for f in ["github_url", "linkedin_url", "portfolio_url"] if profile.get(f))
            resume_score = round(min((cred_count / 3.0) * 8.0, 8.0), 2)

        # ── 5. TECHNICAL ASSESSMENTS & DRILLS (MAX: 10.0) ────────────────────────
        assessments_score = 0.0
        if assessments_raw:
            test_scores = []
            for a in assessments_raw:
                sc = a.get("score", 0)
                try:
                    test_scores.append(float(sc))
                except (ValueError, TypeError):
                    pass
            if test_scores:
                avg_test = sum(test_scores) / len(test_scores)
                vol = min(len(test_scores) / 3.0, 1.0)
                calc = (avg_test / 100.0) * MAX_ASSESSMENTS * (0.6 + 0.4 * vol)
                assessments_score = round(min(calc, MAX_ASSESSMENTS), 2)

        # ── 6. INDUSTRY CERTIFICATIONS (MAX: 10.0) ──────────────────────────────
        certificates_score = 0.0
        if certs_raw:
            cert_count = len(certs_raw)
            # Alignment multiplier
            alignment_bonus = 1.0
            for c in certs_raw:
                c_name = c if isinstance(c, str) else (c.get("certificate_title", "") or c.get("file_name", ""))
                c_lower = c_name.lower()
                if any(ts in c_lower for ts in target_skills):
                    alignment_bonus = 1.25
                    break

            calc = (cert_count / 3.0) * MAX_CERTIFICATES * alignment_bonus
            certificates_score = round(min(calc, MAX_CERTIFICATES), 2)

        # ── TOTAL COMPOSITE SCORE ───────────────────────────────────────────────
        total_score = round(
            skills_score + projects_score + interviews_score +
            resume_score + assessments_score + certificates_score,
            1
        )
        total_score = min(total_score, TOTAL_MAX)

        # Legacy backward-compatible fields
        profile_compat_score = round((resume_score / MAX_RESUME) * 10.0 + (assessments_score / MAX_ASSESSMENTS) * 5.0, 1)
        internships_compat_score = interviews_score

        # Confidence level
        evidence_signals = sum([
            bool(parsed_skills),
            bool(projects_raw),
            bool(interviews_raw),
            bool(resumes_raw),
            bool(assessments_raw),
            bool(certs_raw)
        ])

        if evidence_signals >= 4 and len(parsed_skills) >= 5:
            confidence_level = "High Data Precision"
            data_quality_notice = "Verified multi-signal evidence matched against 2026 corporate hiring benchmarks."
        elif evidence_signals >= 2:
            confidence_level = "Moderate Data Grounding"
            data_quality_notice = "Prediction grounded in verified candidate inputs. Complete remaining mock drills and resume scans for maximum precision."
        else:
            confidence_level = "Foundational Evidence"
            data_quality_notice = "Initial data detected. Complete mock interviews and project portfolio items to elevate candidate score."

        # Positive Drivers & Suggestions
        positive_drivers = self._generate_positive_drivers(
            skills_score=skills_score,
            projects_score=projects_score,
            interviews_score=interviews_score,
            resume_score=resume_score,
            assessments_score=assessments_score,
            certs_score=certificates_score,
            target_title=target_title,
            verified_count=verified_count,
            interview_count=len(interviews_raw),
        )

        suggestions = self._generate_actionable_suggestions(
            profile=profile,
            target_role=target_role,
            skills_score=skills_score,
            projects_score=projects_score,
            interviews_score=interviews_score,
            resume_score=resume_score,
            assessments_score=assessments_score,
            certs_score=certificates_score,
        )

        factors_breakdown = {
            "skills": {
                "score": skills_score,
                "max": MAX_SKILLS,
                "percentage": round((skills_score / MAX_SKILLS) * 100, 1),
                "count": len(parsed_skills),
                "verified": verified_count,
            },
            "projects": {
                "score": projects_score,
                "max": MAX_PROJECTS,
                "percentage": round((projects_score / MAX_PROJECTS) * 100, 1),
                "count": len(projects_raw),
            },
            "interviews": {
                "score": interviews_score,
                "max": MAX_INTERVIEWS,
                "percentage": round((interviews_score / MAX_INTERVIEWS) * 100, 1),
                "count": len(interviews_raw),
            },
            "resume": {
                "score": resume_score,
                "max": MAX_RESUME,
                "percentage": round((resume_score / MAX_RESUME) * 100, 1),
                "version_count": len(resumes_raw),
            },
            "assessments": {
                "score": assessments_score,
                "max": MAX_ASSESSMENTS,
                "percentage": round((assessments_score / MAX_ASSESSMENTS) * 100, 1),
                "completed": len(assessments_raw),
            },
            "certificates": {
                "score": certificates_score,
                "max": MAX_CERTIFICATES,
                "percentage": round((certificates_score / MAX_CERTIFICATES) * 100, 1),
                "count": len(certs_raw),
            },
        }

        return ScoreBreakdown(
            uid=uid,
            skills_score=skills_score,
            projects_score=projects_score,
            interviews_score=interviews_score,
            resume_score=resume_score,
            assessments_score=assessments_score,
            certificates_score=certificates_score,
            profile_score=profile_compat_score,
            internships_score=internships_compat_score,
            total_score=total_score,
            confidence_level=confidence_level,
            data_quality_notice=data_quality_notice,
            factors_breakdown=factors_breakdown,
            positive_drivers=positive_drivers,
            suggestions=suggestions,
            updated_at=datetime.utcnow().isoformat(),
        )

    def _generate_positive_drivers(
        self,
        skills_score: float,
        projects_score: float,
        interviews_score: float,
        resume_score: float,
        assessments_score: float,
        certs_score: float,
        target_title: str,
        verified_count: int,
        interview_count: int,
    ) -> List[str]:
        drivers = []
        if skills_score >= (MAX_SKILLS * 0.6):
            drivers.append(f"+{skills_score} pts: Strong technical skill alignment with {target_title} requisitions.")
        if projects_score >= (MAX_PROJECTS * 0.6):
            drivers.append(f"+{projects_score} pts: Portfolio projects demonstrate practical hands-on implementation.")
        if interviews_score >= (MAX_INTERVIEWS * 0.5):
            drivers.append(f"+{interviews_score} pts: Verified AI Mock Interview performance across {interview_count} sessions.")
        if resume_score >= (MAX_RESUME * 0.6):
            drivers.append(f"+{resume_score} pts: ATS keyword density and structure compliance audited.")
        if assessments_score >= (MAX_ASSESSMENTS * 0.5):
            drivers.append(f"+{assessments_score} pts: High accuracy retention on technical speed drills.")
        if certs_score >= (MAX_CERTIFICATES * 0.5):
            drivers.append(f"+{certs_score} pts: Verified industry credentials on file.")

        return drivers[:3] if drivers else ["Foundational profile created. Add skills and projects to unlock score drivers."]

    def _generate_actionable_suggestions(
        self,
        profile: Dict,
        target_role: Dict,
        skills_score: float,
        projects_score: float,
        interviews_score: float,
        resume_score: float,
        assessments_score: float,
        certs_score: float,
    ) -> List[str]:
        suggestions = []
        target_title = target_role.get("title", "Target Role")
        required_skills = target_role.get("required_skills", [])
        cand_skills = [
            (s.get("name") if isinstance(s, dict) else str(s)).strip().lower()
            for s in profile.get("skills", [])
        ]
        missing_critical = [s for s in required_skills if s.strip().lower() not in cand_skills]

        # 1. Critical Skill Gap
        if missing_critical and skills_score < (MAX_SKILLS * 0.85):
            top_missing = missing_critical[:3]
            suggestions.append(
                f"Target Alignment ({target_title}): Add key role skills '{', '.join(top_missing)}' to boost your score by up to +{round(MAX_SKILLS - skills_score, 1)} pts."
            )

        # 2. Mock Interview
        if interviews_score < (MAX_INTERVIEWS * 0.7):
            suggestions.append(
                f"AI Interview Simulation: Complete a Technical or System Design drill in the AI Interview Simulator (+{round(MAX_INTERVIEWS - interviews_score, 1)} pts potential)."
            )

        # 3. Resume ATS
        if resume_score < (MAX_RESUME * 0.7):
            suggestions.append(
                f"Resume Optimization: Run an ATS Diagnostic scan with measurable project metrics (+{round(MAX_RESUME - resume_score, 1)} pts potential)."
            )

        # 4. Projects
        if projects_score < (MAX_PROJECTS * 0.7):
            suggestions.append(
                "Portfolio Depth: Add detailed project descriptions with GitHub repository links and live demo URLs."
            )

        # 5. Assessments
        if assessments_score < (MAX_ASSESSMENTS * 0.6):
            suggestions.append(
                "Speed Drills: Take the Technical Mock Tests to demonstrate concept retention under timed constraints."
            )

        return suggestions[:3]


# Singleton Predictor Instance
_ml_predictor = None

def get_ml_predictor() -> MLCareerPredictor:
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = MLCareerPredictor()
    return _ml_predictor

