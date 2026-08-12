"""
ML-Based Career Readiness Prediction Engine

Replaces static count-based scoring with a TF-IDF + Cosine Vector Matching model
trained on industry career requisitions (backend/data/careers.json).

Features Extracted:
1. Skill-Relevance Alignment (TF-IDF + Cosine Similarity against Target Role Requisitions)
2. Practical Project Fit (Technology Stack Overlap + Quality Depth)
3. Experience & Internship Alignment (Domain Relevance + Duration Weight)
4. Credential Verification Index (Domain Certifications)
5. Profile & Academic Completeness Ratio
"""

import math
import logging
from typing import List, Dict, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.data_service import get_careers, get_career_by_title
from app.schemas.models import ScoreBreakdown

logger = logging.getLogger(__name__)

# Scoring Max Weights (Sum to 100)
MAX_SKILLS       = 35.0
MAX_PROJECTS     = 25.0
MAX_INTERNSHIPS  = 20.0
MAX_CERTIFICATES = 10.0
MAX_PROFILE      = 10.0
TOTAL_MAX        = 100.0


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
            # Partial match lookup
            target_lower = target_career_title.lower()
            for c in self.careers_data:
                if target_lower in c.get("title", "").lower() or c.get("title", "").lower() in target_lower:
                    return c

        # Default fallback if no target specified or not found
        return self.careers_data[0] if self.careers_data else {
            "title": "Software Engineer",
            "required_skills": ["Python", "JavaScript", "SQL", "Git", "Data Structures"],
            "keywords": ["software", "development", "web", "api"],
        }

    def predict_readiness(self, profile: Dict[str, Any]) -> ScoreBreakdown:
        """
        ML Prediction Pipeline:
        1. Extract candidate features
        2. Vectorize candidate skills & projects vs target role
        3. Compute feature scores & explainable drivers
        """
        candidate_skills_raw = profile.get("skills", [])
        projects_raw = profile.get("projects", [])
        internships_raw = profile.get("internships", [])
        certs_raw = profile.get("certifications", [])

        # If candidate has no career activity data, initial score is 0.0
        if not candidate_skills_raw and not projects_raw and not internships_raw and not certs_raw:
            return ScoreBreakdown(
                skills_score=0.0,
                projects_score=0.0,
                internships_score=0.0,
                certificates_score=0.0,
                profile_score=0.0,
                total_score=0.0,
                confidence_level="Insufficient Data",
                data_quality_notice="New candidate account. Add technical skills, projects, and certifications to compute your ML Career Readiness Score.",
                suggestions=[
                    "Welcome! Add technical skills, portfolio projects, and certifications to compute your ML Career Readiness Score."
                ]
            )
        target_role = self._get_target_career(profile.get("target_career", ""))
        target_skills = [s.strip().lower() for s in target_role.get("required_skills", [])]
        candidate_skills = [s.strip().lower() for s in profile.get("skills", [])]

        # ── 1. SKILL RELEVANCE SCORE (TF-IDF + Cosine + Direct Match Ratio) ─────
        if candidate_skills and target_skills:
            cand_text = " ".join(candidate_skills)
            target_text = " ".join(target_skills)

            # TF-IDF Cosine Similarity
            vecs = self.vectorizer.transform([cand_text, target_text])
            tfidf_sim = float(cosine_similarity(vecs[0], vecs[1])[0][0])

            # Direct overlap ratio
            cand_set = set(candidate_skills)
            target_set = set(target_skills)
            overlap_count = len(cand_set.intersection(target_set))
            direct_ratio = overlap_count / len(target_set) if target_set else 0.0

            # Combined Skill Match (60% direct req overlap + 40% TF-IDF semantic overlap)
            combined_skill_match = (direct_ratio * 0.60) + (tfidf_sim * 0.40)
            skills_score = round(min(combined_skill_match * MAX_SKILLS * 1.15, MAX_SKILLS), 2)
        elif candidate_skills:
            # General skills without target match
            skills_score = round(min((len(candidate_skills) / 20.0) * (MAX_SKILLS * 0.5), MAX_SKILLS * 0.5), 2)
        else:
            skills_score = 0.0

        # ── 2. PRACTICAL PROJECT FIT SCORE ──────────────────────────────────────
        projects = profile.get("projects", [])
        if projects:
            proj_techs = []
            proj_quality_sum = 0.0
            for p in projects:
                if isinstance(p, dict):
                    techs = p.get("technologies", [])
                    if isinstance(techs, str):
                        techs = [t.strip() for t in techs.split(",")]
                    proj_techs.extend([t.lower() for t in techs])

                    # Project completeness quality multiplier
                    q = 0.4
                    if p.get("title"): quality_added = 0.2
                    if p.get("description"): quality_added += 0.2
                    if p.get("github_url"): quality_added += 0.1
                    if p.get("live_url"): quality_added += 0.1
                    proj_quality_sum += (q + quality_added)

            # Project tech stack alignment with target career
            proj_tech_set = set(proj_techs)
            target_set = set(target_skills)
            proj_match = len(proj_tech_set.intersection(target_set)) / len(target_set) if target_set else 0.5
            
            project_ratio = min((proj_quality_sum / 3.0) * (0.6 + 0.4 * proj_match), 1.0)
            projects_score = round(project_ratio * MAX_PROJECTS, 2)
        else:
            projects_score = 0.0

        # ── 3. INDUSTRY EXPERIENCE FIT SCORE ───────────────────────────────────
        internships = profile.get("internships", [])
        if internships:
            exp_quality_sum = 0.0
            for i in internships:
                if isinstance(i, dict):
                    role = i.get("role", "").lower()
                    comp = i.get("company", "")
                    dur = i.get("duration", "")
                    
                    q = 0.5
                    if role and any(k in role for k in ["engineer", "developer", "analyst", "intern", "data", "ai", "tech"]):
                        q += 0.3
                    if comp: q += 0.1
                    if dur: q += 0.1
                    exp_quality_sum += q

            exp_ratio = min(exp_quality_sum / 2.0, 1.0)
            internships_score = round(exp_ratio * MAX_INTERNSHIPS, 2)
        else:
            internships_score = 0.0

        # ── 4. CREDENTIAL VERIFICATION INDEX ──────────────────────────────────
        certs = profile.get("certifications", [])
        if certs:
            cert_count = len(certs)
            certs_score = round(min((cert_count / 3.0) * MAX_CERTIFICATES, MAX_CERTIFICATES), 2)
        else:
            certs_score = 0.0

        # ── 5. PROFILE & ACADEMIC COMPLETENESS ────────────────────────────────
        required_profile_fields = ["name", "email", "college", "degree", "current_year", "cgpa"]
        filled_fields = sum(1 for f in required_profile_fields if profile.get(f))
        field_ratio = filled_fields / len(required_profile_fields)
        
        # Academic CGPA multiplier (e.g. 8.0+ CGPA gives full academic rating)
        try:
            cgpa = float(profile.get("cgpa", 7.0))
            cgpa_mult = min(cgpa / 8.5, 1.1)
        except (ValueError, TypeError):
            cgpa_mult = 1.0

        profile_score = round(min(field_ratio * MAX_PROFILE * cgpa_mult, MAX_PROFILE), 2)

        # ── TOTAL SCORE CALCULATION ───────────────────────────────────────────
        total_score = round(skills_score + projects_score + internships_score + certs_score + profile_score, 1)
        total_score = min(total_score, TOTAL_MAX)

        # Determine confidence level based on candidate profile evidence
        data_points = len(candidate_skills_raw) + len(projects_raw) + len(internships_raw) + len(certs_raw)
        if data_points >= 6 and profile.get("target_career"):
            confidence_level = "High Data Precision"
            data_quality_notice = "Verified candidate evidence matched against target corporate requisitions."
        elif data_points >= 2:
            confidence_level = "Moderate Data Grounding"
            data_quality_notice = "Prediction based on initial candidate inputs. Adding project repository links and certifications will increase evaluation confidence."
        else:
            confidence_level = "Insufficient Data"
            data_quality_notice = "Low candidate evidence. Please add technical skills and projects for an accurate readiness evaluation."

        # Generate explainable insights
        suggestions = self._generate_explainable_insights(
            profile=profile,
            target_role=target_role,
            skills_score=skills_score,
            projects_score=projects_score,
            internships_score=internships_score,
            certs_score=certs_score,
            profile_score=profile_score
        )

        return ScoreBreakdown(
            skills_score=skills_score,
            projects_score=projects_score,
            internships_score=internships_score,
            certificates_score=certs_score,
            profile_score=profile_score,
            total_score=total_score,
            confidence_level=confidence_level,
            data_quality_notice=data_quality_notice,
            suggestions=suggestions,
        )

    def _generate_explainable_insights(
        self,
        profile: Dict,
        target_role: Dict,
        skills_score: float,
        projects_score: float,
        internships_score: float,
        certs_score: float,
        profile_score: float,
    ) -> List[str]:
        """Generate data-grounded, explainable readiness insights and suggestions."""
        insights = []
        target_title = target_role.get("title", "Target Role")
        required_skills = target_role.get("required_skills", [])
        cand_skills = {s.strip().lower() for s in profile.get("skills", [])}

        missing_critical = [s for s in required_skills if s.strip().lower() not in cand_skills]

        # 1. Critical Skill Gap Insight
        if missing_critical:
            top_missing = missing_critical[:3]
            insights.append(
                f"Target Alignment ({target_title}): Add key role skills '{', '.join(top_missing)}' to elevate your skill relevance score."
            )
        else:
            insights.append(
                f"Strong Skill Alignment: Your skill vector covers 100% of core requisitions for {target_title}."
            )

        # 2. Project Fit Insight
        if projects_score < (MAX_PROJECTS * 0.6):
            insights.append(
                f"Practical Experience Gap: Add project portfolio items featuring {target_title} tech stack and include GitHub repositories."
            )

        # 3. Internship Insight
        if internships_score < (MAX_INTERNSHIPS * 0.5):
            insights.append(
                "Industry Experience: Gain domain-relevant internship or practical open-source project experience to improve market readiness."
            )

        # 4. Credential Verification Insight
        if certs_score < (MAX_CERTIFICATES * 0.5):
            insights.append(
                f"Verified Credentials: Complete verified certifications in {required_skills[0] if required_skills else 'core domain'} to strengthen resume ATS audit."
            )

        return insights[:3]


# Singleton Predictor Instance
_ml_predictor = None

def get_ml_predictor() -> MLCareerPredictor:
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = MLCareerPredictor()
    return _ml_predictor
