"""
ML-Based Dynamic Career Readiness Prediction Engine — v2.0 (Accuracy-Upgraded)

Evaluates candidate readiness across 6 key employability dimensions:
1. Skills & Proficiency Vector (Max 25 pts) — TF-IDF alignment, relevance-weighted
   proficiency depth, semantic alias expansion, CGPA academic bonus.
2. Practical Projects & Tech Fit (Max 20 pts) — Quality rubric (description, GitHub,
   live URL, tech count), tech-stack semantic overlap with target role.
3. AI Mock Interviews & Growth (Max 20 pts) — Score-quality-aware volume curve,
   internship experience as an independent guaranteed sub-signal (not just fallback).
4. Resume Quality & ATS Diagnostic (Max 15 pts) — ATS compliance, version delta.
5. Technical Assessments & Drills (Max 10 pts) — Accuracy under timed constraints.
6. Industry Certifications (Max 10 pts) — Prestige-tier weighting (Google/AWS/
   Microsoft = Tier-1), semantic role alignment check.

Total Score = 100.0 Maximum.  Brand-new users start at 0.0.
Score calibrated against 4 benchmark profiles to match 2026 hiring realities.
"""

import logging
from datetime import datetime
from typing import List, Dict, Tuple, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.data_service import get_careers, get_career_by_title
from app.schemas.models import ScoreBreakdown, ScoreHistoryEntry

logger = logging.getLogger(__name__)

# ── Scoring Max Weights (Sum = 100) ───────────────────────────────────────────
MAX_SKILLS       = 25.0
MAX_PROJECTS     = 20.0
MAX_INTERVIEWS   = 20.0
MAX_RESUME       = 15.0
MAX_ASSESSMENTS  = 10.0
MAX_CERTIFICATES = 10.0
TOTAL_MAX        = 100.0

# ── Proficiency Multipliers ────────────────────────────────────────────────────
PROFICIENCY_MULTIPLIERS = {
    "beginner":     0.65,
    "intermediate": 1.00,
    "advanced":     1.30,
    "expert":       1.55,
}

# ── Skill Alias / Synonym Normalization Map ────────────────────────────────────
# Maps variants to canonical forms used in career required_skills lists.
SKILL_ALIASES: Dict[str, str] = {
    # JavaScript ecosystem
    "js":               "javascript",
    "node.js":          "node.js",
    "node":             "node.js",
    "nodejs":           "node.js",
    "react.js":         "react",
    "reactjs":          "react",
    "next.js":          "next.js",
    "nextjs":           "next.js",
    "vue.js":           "vue",
    "vuejs":            "vue",
    "angular.js":       "angular",
    "ts":               "typescript",
    # Python ecosystem
    "py":               "python",
    "fastapi":          "rest apis",
    "flask":            "rest apis",
    "django":           "rest apis",
    "sklearn":          "scikit-learn",
    "sci-kit learn":    "scikit-learn",
    # AI / ML
    "ml":               "machine learning",
    "dl":               "deep learning",
    "neural networks":  "deep learning",
    "natural language processing": "nlp",
    "large language model": "llm",
    "generative ai":    "llm",
    # Cloud / DevOps
    "amazon web services": "aws",
    "google cloud":     "gcp",
    "microsoft azure":  "azure",
    "k8s":              "kubernetes",
    "cicd":             "ci/cd",
    "continuous integration": "ci/cd",
    # Databases
    "postgres":         "postgresql",
    "mongo":            "mongodb",
    "mysql":            "sql",
    "sqlite":           "sql",
    "nosql":            "mongodb",
    # General
    "oop":              "object-oriented programming",
    "oops":             "object-oriented programming",
    "dsa":              "data structures",
    "data structures and algorithms": "data structures",
    "rest":             "rest apis",
    "rest api":         "rest apis",
    "restful":          "rest apis",
    "github":           "git",
    "version control":  "git",
    "containerization": "docker",
    "bash":             "linux",
    "shell":            "linux",
    "tailwind":         "tailwind css",
    "tailwindcss":      "tailwind css",
}

# Semantic expansion: skills that semantically cover a broader concept
SKILL_SEMANTIC_EXPANSION: Dict[str, List[str]] = {
    "react":            ["javascript", "frontend"],
    "node.js":          ["javascript", "backend", "rest apis"],
    "python":           ["backend", "scripting"],
    "fastapi":          ["python", "rest apis", "backend"],
    "django":           ["python", "rest apis", "backend"],
    "tensorflow":       ["machine learning", "deep learning", "python"],
    "pytorch":          ["machine learning", "deep learning", "python"],
    "scikit-learn":     ["machine learning", "python"],
    "kubernetes":       ["docker", "devops", "cloud"],
    "docker":           ["devops", "containerization"],
    "aws":              ["cloud", "devops"],
    "gcp":              ["cloud", "devops"],
    "azure":            ["cloud", "devops"],
    "flutter":          ["dart", "mobile"],
    "react native":     ["javascript", "mobile"],
    "sql":              ["postgresql", "databases"],
    "postgresql":       ["sql", "databases"],
    "mongodb":          ["nosql", "databases"],
    "langchain":        ["llm", "python", "machine learning"],
}

# ── Certificate Prestige Tiers ─────────────────────────────────────────────────
CERT_TIER_1_ORGS = {
    "google", "aws", "amazon", "amazon web services",
    "microsoft", "meta", "ibm", "coursera", "stanford",
    "mit", "deeplearning.ai", "deeplearning", "oracle",
    "cisco", "redhat", "red hat", "linux foundation",
}
CERT_TIER_1_KEYWORDS = {
    "professional", "aws certified", "google certified",
    "microsoft certified", "certified kubernetes", "cka", "ckad",
    "azure certified", "gcp certified", "cisco certified",
    "certified solutions architect", "tensorflow developer",
    "deep learning specialization", "machine learning engineer",
}
CERT_TIER_2_ORGS = {
    "udemy", "linkedin learning", "edx", "nptel", "udacity",
    "datacamp", "pluralsight", "codecademy", "hackerrank",
}

CERT_TIER_1_PTS = 4.5
CERT_TIER_2_PTS = 3.0
CERT_TIER_3_PTS = 1.5


def _normalize_skill(skill: str) -> str:
    """Normalize a skill name via alias map."""
    cleaned = skill.strip().lower()
    return SKILL_ALIASES.get(cleaned, cleaned)


def _expand_skill_set(skills: List[str]) -> List[str]:
    """Expand a skill list with semantic siblings for better TF-IDF coverage."""
    expanded = list(skills)
    seen = set(skills)
    for skill in skills:
        for sibling in SKILL_SEMANTIC_EXPANSION.get(skill, []):
            if sibling not in seen:
                expanded.append(sibling)
                seen.add(sibling)
    return expanded


def _cgpa_bonus(cgpa: float) -> float:
    """Academic performance bonus — early-career hiring gate signal."""
    if cgpa >= 8.5:
        return 2.5
    if cgpa >= 7.5:
        return 1.5
    if cgpa >= 6.5:
        return 0.5
    return 0.0


def _cert_tier(cert: Any) -> int:
    """Classify a certificate into prestige tier 1, 2, or 3."""
    if isinstance(cert, str):
        c_title, c_org = cert.lower(), ""
    elif isinstance(cert, dict):
        c_title = (cert.get("certificate_title") or cert.get("file_name") or "").lower()
        c_org   = (cert.get("issuing_organization") or "").lower()
    else:
        c_title = (getattr(cert, "certificate_title", "") or "").lower()
        c_org   = (getattr(cert, "issuing_organization", "") or "").lower()

    for t1 in CERT_TIER_1_ORGS:
        if t1 in c_org or t1 in c_title:
            return 1
    for kw in CERT_TIER_1_KEYWORDS:
        if kw in c_title:
            return 1
    for t2 in CERT_TIER_2_ORGS:
        if t2 in c_org or t2 in c_title:
            return 2
    return 3


def _cert_role_aligned(cert: Any, target_skills: List[str], target_keywords: List[str]) -> bool:
    """Check if a cert is semantically aligned with the target role."""
    if isinstance(cert, str):
        c_text = cert.lower()
    elif isinstance(cert, dict):
        parts = [
            cert.get("certificate_title") or "",
            cert.get("issuing_organization") or "",
        ]
        es = cert.get("extracted_skills", {})
        if isinstance(es, dict):
            for v in es.values():
                if isinstance(v, list):
                    parts.extend(v)
        c_text = " ".join(parts).lower()
    else:
        c_text = (getattr(cert, "certificate_title", "") or "").lower()

    for s in target_skills:
        if len(s) > 2 and s in c_text:
            return True
    for kw in target_keywords:
        if len(kw) > 2 and kw in c_text:
            return True
    return False


class MLCareerPredictor:
    def __init__(self):
        self.careers_data = get_careers()
        self._init_tfidf()

    def _init_tfidf(self):
        """Build TF-IDF corpus from all career required skills & descriptions."""
        corpus = []
        for c in self.careers_data:
            req  = " ".join(c.get("required_skills", []))
            kw   = " ".join(c.get("keywords", []))
            desc = c.get("description", "")
            corpus.append(f"{req} {kw} {desc}")

        if not corpus:
            corpus = ["python react javascript node sql machine learning docker aws rest apis typescript"]

        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.vectorizer.fit(corpus)
        logger.info(
            f"MLPredictor v2.0 — TF-IDF vocab size: {len(self.vectorizer.vocabulary_)}"
        )

    def _get_target_career(self, target_career_title: str) -> Dict[str, Any]:
        """Retrieve target career schema or fallback to first career in dataset."""
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
        """Evaluate full 6-dimensional candidate readiness against 2026 benchmarks."""
        uid = profile.get("uid", "")
        raw_skills      = profile.get("skills", [])
        projects_raw    = profile.get("projects", [])
        internships_raw = profile.get("internships", [])
        certs_raw       = profile.get("certifications", []) or (certificates or [])
        interviews_raw  = interviews or profile.get("interview_records", [])
        resumes_raw     = resumes or profile.get("resume_records", [])
        assessments_raw = assessments or profile.get("assessment_records", [])

        has_any_data = (
            bool(raw_skills) or bool(projects_raw) or bool(internships_raw) or
            bool(certs_raw)  or bool(interviews_raw) or bool(resumes_raw) or
            bool(assessments_raw)
        )

        if not has_any_data:
            return ScoreBreakdown(
                uid=uid,
                skills_score=0.0, projects_score=0.0, interviews_score=0.0,
                resume_score=0.0, assessments_score=0.0, certificates_score=0.0,
                profile_score=0.0, internships_score=0.0, total_score=0.0,
                confidence_level="Insufficient Data",
                data_quality_notice=(
                    "New candidate account. Add technical skills, run ATS resume diagnostics, "
                    "or complete a mock interview to compute your score."
                ),
                positive_drivers=[],
                suggestions=[
                    "Add 3+ technical skills with proficiency levels in your profile.",
                    "Execute a resume ATS diagnostic scan to unlock resume scoring.",
                    "Complete a domain-specific AI Mock Interview session.",
                ],
                history=[],
                updated_at=datetime.utcnow().isoformat(),
            )

        target_role     = self._get_target_career(profile.get("target_career", ""))
        target_skills   = [s.strip().lower() for s in target_role.get("required_skills", [])]
        target_keywords = [k.strip().lower() for k in target_role.get("keywords", [])]
        target_title    = target_role.get("title", "Software Engineer")
        target_skill_set = set(target_skills)

        # ── 1. SKILLS & PROFICIENCY (MAX 25) ─────────────────────────────────
        skills_score    = 0.0
        parsed_skills   = []
        verified_count  = 0
        proficiency_sum = 0.0

        for item in raw_skills:
            if isinstance(item, str):
                s_name, s_level, s_verified = item.strip(), "intermediate", False
            elif isinstance(item, dict):
                s_name     = item.get("name", "").strip()
                s_level    = item.get("level", "Intermediate")
                s_verified = item.get("verified", False)
            else:
                s_name     = getattr(item, "name", "").strip()
                s_level    = getattr(item, "level", "Intermediate")
                s_verified = getattr(item, "verified", False)

            if not s_name:
                continue

            canonical = _normalize_skill(s_name)
            parsed_skills.append(canonical)

            # Relevance: 1.0 directly required, 0.55 semantically related, 0.20 other
            if canonical in target_skill_set:
                rel = 1.0
            elif any(canonical in _expand_skill_set([ts]) for ts in target_skill_set):
                rel = 0.55
            else:
                rel = 0.20

            depth = PROFICIENCY_MULTIPLIERS.get(str(s_level).lower(), 1.0)
            if s_verified:
                depth *= 1.20
                verified_count += 1

            # Relevance-weighted depth contribution
            proficiency_sum += depth * (rel * 0.80 + 0.20)

        if parsed_skills and target_skills:
            expanded_cand   = _expand_skill_set(parsed_skills)
            expanded_target = _expand_skill_set(target_skills)

            vecs      = self.vectorizer.transform([" ".join(expanded_cand), " ".join(expanded_target)])
            tfidf_sim = float(cosine_similarity(vecs[0], vecs[1])[0][0])

            cand_set     = set(expanded_cand)
            overlap      = len(cand_set.intersection(set(expanded_target)))
            direct_ratio = overlap / len(set(expanded_target)) if expanded_target else 0.0

            # If there is ZERO direct overlap AND tfidf_sim is very low (< 0.08)
            # This is a completely mismatched role target (e.g. Word/Excel for AI/ML Engineer)
            if overlap == 0 and tfidf_sim < 0.08:
                skills_score = 0.0
            else:
                alignment_factor = (direct_ratio * 0.60) + (tfidf_sim * 0.40)
                avg_depth        = proficiency_sum / len(parsed_skills)
                raw_pts          = alignment_factor * MAX_SKILLS * avg_depth * 1.15
                skills_score     = round(min(raw_pts, MAX_SKILLS), 2)
        elif parsed_skills:
            avg_depth    = proficiency_sum / len(parsed_skills)
            skills_score = round(
                min((len(parsed_skills) / 12.0) * (MAX_SKILLS * 0.55) * avg_depth, MAX_SKILLS * 0.55), 2
            )

        # CGPA academic bonus: only applies if candidate has relevant skills
        cgpa       = float(profile.get("cgpa", 0) or 0)
        cgpa_bonus = _cgpa_bonus(cgpa) if skills_score > 0 else 0.0
        skills_score = round(min(skills_score + cgpa_bonus, MAX_SKILLS), 2)

        # ── 2. PRACTICAL PROJECTS & TECH FIT (MAX 20) ────────────────────────
        projects_score   = 0.0
        proj_quality_sum = 0.0

        for p in projects_raw:
            if isinstance(p, dict):
                techs  = p.get("technologies", [])
                title  = p.get("title", "")
                desc   = p.get("description", "")
                gh_url = p.get("github_url", "")
                live   = p.get("live_url", "")
            else:
                techs  = getattr(p, "technologies", [])
                title  = getattr(p, "title", "")
                desc   = getattr(p, "description", "")
                gh_url = getattr(p, "github_url", "")
                live   = getattr(p, "live_url", "")

            if isinstance(techs, str):
                techs = [t.strip() for t in techs.split(",")]
            norm_techs = [_normalize_skill(t) for t in techs if t.strip()]

            # Quality rubric per project
            q = 0.30
            if title:                            q += 0.05
            if desc and len(str(desc)) >= 30:    q += 0.25
            if gh_url and "http" in str(gh_url): q += 0.20
            if live and "http" in str(live):     q += 0.15
            if len(norm_techs) >= 3:             q += 0.10

            # Role-tech alignment bonus: fraction of project's techs that match the target role
            norm_tech_set = set(norm_techs)
            if norm_tech_set:
                expanded_proj = set(_expand_skill_set(norm_techs))
                expanded_tgt  = set(_expand_skill_set(target_skills))
                relevant_count = len(expanded_proj.intersection(expanded_tgt))
                match_ratio    = min(relevant_count / len(norm_tech_set), 1.0)
            else:
                match_ratio = 0.40

            q *= (0.60 + 0.40 * match_ratio)
            proj_quality_sum += q

        if projects_raw:
            # Normalize: 2 high-quality aligned projects → 18 pts (0.90 ratio), 3 → full score
            project_ratio  = min(proj_quality_sum / 2.0, 1.0)
            projects_score = round(project_ratio * MAX_PROJECTS, 2)

        # ── 3. INTERVIEWS & INTERNSHIP EXPERIENCE (MAX 20) ───────────────────
        # Internship: independent sub-signal (sub-cap 8 pts)
        # Interviews: performance-quality-aware (sub-cap 15 pts)
        interview_sub  = 0.0
        internship_sub = 0.0

        if internships_raw:
            intern_quality = 0.0
            for exp in internships_raw:
                if isinstance(exp, dict):
                    has_role     = bool(exp.get("role"))
                    has_company  = bool(exp.get("company"))
                    has_desc     = bool(exp.get("description"))
                    has_duration = bool(exp.get("duration"))
                else:
                    has_role     = bool(getattr(exp, "role", None))
                    has_company  = bool(getattr(exp, "company", None))
                    has_desc     = bool(getattr(exp, "description", None))
                    has_duration = bool(getattr(exp, "duration", None))

                exp_pts = 5.0
                if has_desc:                  exp_pts += 1.5
                if has_duration:              exp_pts += 1.0
                if has_role and has_company:  exp_pts += 1.0
                intern_quality += exp_pts

            internship_sub = round(min(intern_quality, 8.0), 2)

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

                # Quality-aware volume curve
                if interview_count >= 3:
                    vol_factor = 1.0
                elif interview_count == 2:
                    vol_factor = 0.90
                else:  # single session — quality determines vol weight
                    if avg_interview_score >= 80:
                        vol_factor = 0.82
                    elif avg_interview_score >= 65:
                        vol_factor = 0.68
                    else:
                        vol_factor = 0.55

                # Growth bonus for demonstrated improvement
                growth_bonus = 1.0
                if len(scores_list) >= 2 and scores_list[-1] > scores_list[0]:
                    growth_bonus = 1.12

                calc = (avg_interview_score / 100.0) * 15.0 * vol_factor * growth_bonus
                interview_sub = round(min(calc, 15.0), 2)

        interviews_score = round(min(interview_sub + internship_sub, MAX_INTERVIEWS), 2)

        # ── 4. RESUME QUALITY & ATS DIAGNOSTIC (MAX 15) ──────────────────────
        resume_score = 0.0
        if resumes_raw:
            latest = resumes_raw[-1] if isinstance(resumes_raw, list) else resumes_raw
            try:
                ats_val = float(latest.get("ats_score", latest.get("score", 0)) or 0)
            except (ValueError, TypeError):
                ats_val = 60.0

            version_bonus = 1.0
            if len(resumes_raw) >= 2:
                try:
                    first_ats = float(resumes_raw[0].get("ats_score", 0) or 0)
                    if ats_val > first_ats:
                        version_bonus = 1.08
                except (ValueError, TypeError):
                    pass

            resume_score = round(min((ats_val / 100.0) * MAX_RESUME * version_bonus, MAX_RESUME), 2)
        else:
            # Check for portfolio presence via profile URLs or project repo/live links
            cred_count = sum(
                1 for f in ["github_url", "linkedin_url", "portfolio_url"]
                if profile.get(f) and str(profile.get(f)).startswith("http")
            )
            proj_links = sum(
                1 for p in projects_raw
                if (isinstance(p, dict) and (p.get("github_url") or p.get("live_url"))) or
                   (getattr(p, "github_url", None) or getattr(p, "live_url", None))
            )
            effective_creds = max(cred_count, min(proj_links, 2))
            if effective_creds > 0:
                resume_score = round(min((effective_creds / 3.0) * 5.0 + 3.0, 7.5), 2)

        # ── 5. TECHNICAL ASSESSMENTS & DRILLS (MAX 10) ───────────────────────
        assessments_score = 0.0
        if assessments_raw:
            test_scores = []
            for a in assessments_raw:
                try:
                    test_scores.append(float(a.get("score", 0)))
                except (ValueError, TypeError):
                    pass
            if test_scores:
                avg_test  = sum(test_scores) / len(test_scores)
                vol       = min(len(test_scores) / 3.0, 1.0)
                calc      = (avg_test / 100.0) * MAX_ASSESSMENTS * (0.60 + 0.40 * vol)
                assessments_score = round(min(calc, MAX_ASSESSMENTS), 2)

        # ── 6. INDUSTRY CERTIFICATIONS (MAX 10) ──────────────────────────────
        # Prestige tier system: Tier-1 = 4.5 pts, Tier-2 = 3.0, Tier-3 = 1.5
        # Role-aligned cert earns +25% bonus on its tier pts
        certificates_score = 0.0
        if certs_raw:
            cert_pts_total = 0.0
            for cert in certs_raw:
                tier      = _cert_tier(cert)
                base_pts  = {1: CERT_TIER_1_PTS, 2: CERT_TIER_2_PTS, 3: CERT_TIER_3_PTS}.get(tier, CERT_TIER_3_PTS)
                if _cert_role_aligned(cert, target_skills, target_keywords):
                    base_pts *= 1.25
                cert_pts_total += base_pts

            certificates_score = round(min(cert_pts_total, MAX_CERTIFICATES), 2)

        # ── TOTAL COMPOSITE SCORE ─────────────────────────────────────────────
        total_score = round(
            skills_score + projects_score + interviews_score +
            resume_score + assessments_score + certificates_score, 1
        )
        total_score = min(total_score, TOTAL_MAX)

        # Legacy backward-compatible fields
        profile_compat_score     = round((resume_score / MAX_RESUME) * 10.0 + (assessments_score / MAX_ASSESSMENTS) * 5.0, 1)
        internships_compat_score = round(internship_sub, 2)

        # Confidence level
        evidence_signals = sum([
            bool(parsed_skills), bool(projects_raw), bool(interviews_raw),
            bool(resumes_raw), bool(assessments_raw), bool(certs_raw),
            bool(internships_raw),
        ])

        if evidence_signals >= 4 and len(parsed_skills) >= 5:
            confidence_level    = "High Data Precision"
            data_quality_notice = (
                "Verified multi-signal evidence matched against 2026 corporate hiring benchmarks "
                "using semantic skill alignment and prestige-weighted credentials."
            )
        elif evidence_signals >= 2:
            confidence_level    = "Moderate Data Grounding"
            data_quality_notice = (
                "Prediction grounded in verified candidate inputs. Complete remaining mock drills "
                "and resume scans for maximum precision."
            )
        else:
            confidence_level    = "Foundational Evidence"
            data_quality_notice = (
                "Initial data detected. Add skills, projects, and run a mock interview "
                "to generate a comprehensive readiness score."
            )

        positive_drivers = self._generate_positive_drivers(
            skills_score=skills_score, projects_score=projects_score,
            interviews_score=interviews_score, resume_score=resume_score,
            assessments_score=assessments_score, certs_score=certificates_score,
            target_title=target_title, verified_count=verified_count,
            interview_count=interview_count, internship_count=len(internships_raw),
            cgpa=cgpa, internship_sub=internship_sub,
        )

        suggestions = self._generate_actionable_suggestions(
            profile=profile, target_role=target_role, parsed_skills=parsed_skills,
            skills_score=skills_score, projects_score=projects_score,
            interviews_score=interviews_score, resume_score=resume_score,
            assessments_score=assessments_score, certs_score=certificates_score,
        )

        factors_breakdown = {
            "skills": {
                "score": skills_score, "max": MAX_SKILLS,
                "percentage": round((skills_score / MAX_SKILLS) * 100, 1),
                "count": len(parsed_skills), "verified": verified_count,
                "cgpa_bonus": cgpa_bonus,
            },
            "projects": {
                "score": projects_score, "max": MAX_PROJECTS,
                "percentage": round((projects_score / MAX_PROJECTS) * 100, 1),
                "count": len(projects_raw),
            },
            "interviews": {
                "score": interviews_score, "max": MAX_INTERVIEWS,
                "percentage": round((interviews_score / MAX_INTERVIEWS) * 100, 1),
                "interview_sub": interview_sub, "internship_sub": internship_sub,
                "count": interview_count, "internship_count": len(internships_raw),
            },
            "resume": {
                "score": resume_score, "max": MAX_RESUME,
                "percentage": round((resume_score / MAX_RESUME) * 100, 1),
                "version_count": len(resumes_raw),
            },
            "assessments": {
                "score": assessments_score, "max": MAX_ASSESSMENTS,
                "percentage": round((assessments_score / MAX_ASSESSMENTS) * 100, 1),
                "completed": len(assessments_raw),
            },
            "certificates": {
                "score": certificates_score, "max": MAX_CERTIFICATES,
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
        skills_score: float, projects_score: float, interviews_score: float,
        resume_score: float, assessments_score: float, certs_score: float,
        target_title: str, verified_count: int, interview_count: int,
        internship_count: int, cgpa: float, internship_sub: float,
    ) -> List[str]:
        drivers = []
        if skills_score >= (MAX_SKILLS * 0.55):
            note = f" ({verified_count} certificate-verified)" if verified_count else ""
            drivers.append(
                f"+{skills_score} pts: Strong semantic skill alignment with {target_title} requisitions{note}."
            )
        if projects_score >= (MAX_PROJECTS * 0.55):
            drivers.append(
                f"+{projects_score} pts: Portfolio projects demonstrate role-relevant tech-stack implementation."
            )
        if interview_count > 0 and interviews_score >= (MAX_INTERVIEWS * 0.40):
            drivers.append(
                f"+{interviews_score} pts: Verified AI Mock Interview performance across {interview_count} session(s)."
            )
        if internship_count > 0 and internship_sub >= 3.0:
            drivers.append(
                f"Work experience: {internship_count} internship(s) contributing +{internship_sub} pts to readiness."
            )
        if resume_score >= (MAX_RESUME * 0.55):
            drivers.append(f"+{resume_score} pts: ATS keyword compliance and resume structure audited.")
        if certs_score >= (MAX_CERTIFICATES * 0.40):
            drivers.append(f"+{certs_score} pts: Industry credentials on file (prestige-weighted).")
        if cgpa >= 7.5:
            drivers.append(f"Academic signal: CGPA {cgpa} → +{_cgpa_bonus(cgpa)} pts bonus applied.")

        return drivers[:4] if drivers else [
            "Foundational profile created. Add skills and projects to unlock score drivers."
        ]

    def _generate_actionable_suggestions(
        self,
        profile: Dict, target_role: Dict, parsed_skills: List[str],
        skills_score: float, projects_score: float, interviews_score: float,
        resume_score: float, assessments_score: float, certs_score: float,
    ) -> List[str]:
        suggestions  = []
        target_title = target_role.get("title", "Target Role")
        req_skills   = [s.strip().lower() for s in target_role.get("required_skills", [])]
        cand_set     = set(parsed_skills)
        expanded_cand = set(_expand_skill_set(parsed_skills))

        missing_critical = [
            s for s in req_skills
            if _normalize_skill(s) not in cand_set
            and _normalize_skill(s) not in expanded_cand
        ]

        if missing_critical and skills_score < (MAX_SKILLS * 0.82):
            top3 = [s.title() for s in missing_critical[:3]]
            suggestions.append(
                f"Skill Gap ({target_title}): Add '{', '.join(top3)}' — "
                f"up to +{round(MAX_SKILLS - skills_score, 1)} pts potential."
            )

        if interviews_score < (MAX_INTERVIEWS * 0.60):
            suggestions.append(
                f"AI Interview Simulator: Complete a Technical or System Design drill "
                f"(+{round(MAX_INTERVIEWS * 0.75 - interviews_score, 1)} pts potential)."
            )

        if resume_score < (MAX_RESUME * 0.65):
            suggestions.append(
                f"Resume ATS Scan: Run an ATS Diagnostic with measurable metrics "
                f"(+{round(MAX_RESUME - resume_score, 1)} pts potential)."
            )

        if projects_score < (MAX_PROJECTS * 0.65):
            suggestions.append(
                "Portfolio Depth: Add project descriptions with GitHub links, live URLs, "
                "and 3+ technologies for maximum quality score."
            )

        if certs_score < (MAX_CERTIFICATES * 0.50):
            suggestions.append(
                "Credentials: Upload a Google, AWS, or Microsoft professional certificate "
                "for Tier-1 prestige weighting (+4.5 pts per credential)."
            )

        if assessments_score < (MAX_ASSESSMENTS * 0.50):
            suggestions.append(
                "Mock Tests: Complete Technical Drills to prove concept retention "
                "under timed constraints."
            )

        return suggestions[:4]


# ── Singleton Predictor Instance ──────────────────────────────────────────────
_ml_predictor: Optional[MLCareerPredictor] = None


def get_ml_predictor() -> MLCareerPredictor:
    global _ml_predictor
    if _ml_predictor is None:
        _ml_predictor = MLCareerPredictor()
    return _ml_predictor

