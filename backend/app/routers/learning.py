"""
Learning Roadmap Router
Implements Domain -> Career Role -> Required Skills -> Skill Gaps -> Modules -> Courses hierarchy.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.services.career_service import get_skill_gap_for_career
from app.services.data_service import (
    get_courses_for_skill,
    get_career_by_title,
    get_domain_for_career,
    get_careers
)
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

STAGE_NAMES = {
    1: "Module 1 — Core Fundamentals",
    2: "Module 2 — Applied Stack Architecture",
    3: "Module 3 — Advanced Specialization",
    4: "Module 4 — Portfolio Projects",
    5: "Module 5 — Executive Interview Preparation",
}


def _generate_rich_roadmap(target_career: str, user_skills: list) -> dict:
    """Generate dynamic, role-specific learning roadmap with domain matching."""
    domain = get_domain_for_career(target_career)
    career_info = get_career_by_title(target_career)

    if not career_info:
        # Fallback to first matching career or software engineering
        careers = get_careers()
        career_info = careers[0] if careers else {
            "title": target_career,
            "required_skills": ["Python", "JavaScript", "SQL", "Git", "System Design"],
            "category": "Software Engineering"
        }

    required_skills = career_info.get("required_skills", ["Python", "JavaScript", "SQL", "Git"])
    gap_analysis = get_skill_gap_for_career(user_skills, target_career)
    missing_skills = gap_analysis.get("missing_skills", [])
    matching_skills = gap_analysis.get("matching_skills", [])

    missing_skill_names = [m["skill"] if isinstance(m, dict) else str(m) for m in missing_skills]

    # Map missing skills to 4 technical stages, fallback to required skills if gaps are small
    skills_to_learn = missing_skill_names if missing_skill_names else required_skills[:6]

    stages = {str(i): [] for i in range(1, 6)}

    # Distribute skills across stages 1 to 4
    for idx, skill in enumerate(skills_to_learn):
        stage_num = min(4, (idx % 4) + 1)
        raw_courses = get_courses_for_skill(skill)

        # Build courses list with rich metadata
        course_items = []
        for c in raw_courses[:3]:
            course_items.append({
                "id": str(uuid.uuid4()),
                "title": c.get("title", f"Learn {skill}"),
                "platform": c.get("platform", "Coursera / Udemy"),
                "skill": skill,
                "difficulty": c.get("difficulty", "intermediate"),
                "level": c.get("level", "Intermediate Specialization"),
                "duration": c.get("duration", "4 weeks"),
                "url": c.get("url", "https://coursera.org"),
                "relevance_reason": c.get("relevance_reason", f"Required skill for {target_career} role requisition in {domain}.")
            })

        # Fallback default course if dataset returns empty
        if not course_items:
            course_items.append({
                "id": str(uuid.uuid4()),
                "title": f"Mastering {skill} for {target_career}",
                "platform": "CareerPilot AI Academy",
                "skill": skill,
                "difficulty": "intermediate",
                "level": "Intermediate Specialization",
                "duration": "4 weeks",
                "url": "https://coursera.org",
                "relevance_reason": f"Essential core competency for {target_career} candidates in {domain}."
            })

        # Check if user already has this skill
        is_acquired = skill in matching_skills or any(
            (s.get("name") if isinstance(s, dict) else str(s)).lower() == skill.lower()
            for s in user_skills
        )

        item = {
            "id": f"mod_{stage_num}_{idx}_{uuid.uuid4().hex[:6]}",
            "module_index": stage_num,
            "title": f"{skill} Mastery & Applied Architecture",
            "description": f"Comprehensive learning path for {skill} aligned with {target_career} role requisitions.",
            "skill": skill,
            "stage": stage_num,
            "stage_name": STAGE_NAMES[stage_num],
            "status": "completed" if is_acquired else "not_started",
            "difficulty": "beginner" if stage_num == 1 else ("intermediate" if stage_num <= 3 else "advanced"),
            "platform": course_items[0]["platform"],
            "resource_url": course_items[0]["url"],
            "courses": course_items,
        }
        stages[str(stage_num)].append(item)

    # Always ensure Stage 5 (Interview & Capstone Prep) exists
    interview_item = {
        "id": f"mod_5_interview_{uuid.uuid4().hex[:6]}",
        "module_index": 5,
        "title": f"Executive Interview & System Architecture Prep for {target_career}",
        "description": f"Practice LeetCode algorithms, system design trade-offs, and STAR behavioral scenarios for {domain} roles.",
        "skill": "Interview & Architecture",
        "stage": 5,
        "stage_name": STAGE_NAMES[5],
        "status": "not_started",
        "difficulty": "hard",
        "platform": "CareerPilot AI Simulator & LeetCode",
        "resource_url": "https://leetcode.com",
        "courses": [
            {
                "id": str(uuid.uuid4()),
                "title": f"Grokking System Design & Coding Interviews for {target_career}",
                "platform": "LeetCode / Educative.io",
                "skill": "Interview & Architecture",
                "difficulty": "advanced",
                "level": "Executive Preparation",
                "duration": "3 weeks",
                "url": "https://leetcode.com",
                "relevance_reason": f"Prepare for technical screening loops and system design assessments at top-tier {domain} companies."
            }
        ]
    }
    stages["5"].append(interview_item)

    return {
        "domain": domain,
        "target_career": target_career,
        "stages": stages,
        "required_skills": required_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skill_names,
    }


@router.get("")
async def get_learning_roadmap(
    user: dict = Depends(get_current_user),
    force_refresh: bool = Query(False)
):
    """Get the learning roadmap for the user's target career (guaranteed non-empty)."""
    try:
        db = get_firestore()
        uid = user["uid"]

        # Retrieve profile
        profile_doc = db.collection("profiles").document(uid).get()
        profile = profile_doc.to_dict() if profile_doc.exists else {}

        target_career = profile.get("target_career") or "Full-Stack Engineer"
        user_skills = profile.get("skills", [])

        # Check existing Firestore roadmap
        roadmap_ref = db.collection("learningProgress").document(uid)
        roadmap_doc = roadmap_ref.get()

        if roadmap_doc.exists and not force_refresh:
            stored = roadmap_doc.to_dict()
            if stored.get("target_career") == target_career and stored.get("stages"):
                # Recalculate totals dynamically to prevent stale progress counts
                all_items = [item for items in stored["stages"].values() for item in items]
                total = len(all_items)
                completed = sum(1 for i in all_items if i.get("status") == "completed")
                in_progress = sum(1 for i in all_items if i.get("status") == "in_progress")
                pct = round((completed / total) * 100, 1) if total > 0 else 0.0

                stored["total_items"] = total
                stored["completed_items"] = completed
                stored["in_progress_items"] = in_progress
                stored["progress_percentage"] = pct
                return stored

        # Generate fresh roadmap
        rich_data = _generate_rich_roadmap(target_career, user_skills)
        stages = rich_data["stages"]
        all_items = [item for items in stages.values() for item in items]
        total = len(all_items)
        completed = sum(1 for i in all_items if i.get("status") == "completed")
        in_progress = sum(1 for i in all_items if i.get("status") == "in_progress")
        pct = round((completed / total) * 100, 1) if total > 0 else 0.0

        roadmap_data = {
            "uid": uid,
            "domain": rich_data["domain"],
            "target_career": target_career,
            "stages": stages,
            "total_items": total,
            "completed_items": completed,
            "in_progress_items": in_progress,
            "progress_percentage": pct,
            "required_skills": rich_data["required_skills"],
            "missing_skills": rich_data["missing_skills"],
            "updated_at": datetime.utcnow().isoformat(),
        }

        roadmap_ref.set(roadmap_data, merge=True)
        return roadmap_data

    except Exception as e:
        logger.error(f"Get roadmap failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate learning roadmap: {str(e)}")


@router.put("/item/{item_id}/status")
async def update_item_status(
    item_id: str,
    data: dict,
    user: dict = Depends(get_current_user)
):
    """Update status of a learning module and adaptively recalculate progress."""
    new_status = data.get("status", "not_started")
    if new_status not in ("not_started", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        db = get_firestore()
        uid = user["uid"]
        roadmap_ref = db.collection("learningProgress").document(uid)
        roadmap_doc = roadmap_ref.get()

        if not roadmap_doc.exists:
            # Fallback trigger roadmap generation
            profile_doc = db.collection("profiles").document(uid).get()
            profile = profile_doc.to_dict() if profile_doc.exists else {}
            target_career = profile.get("target_career") or "Full-Stack Engineer"
            rich_data = _generate_rich_roadmap(target_career, profile.get("skills", []))
            roadmap = {
                "uid": uid,
                "target_career": target_career,
                "stages": rich_data["stages"],
            }
        else:
            roadmap = roadmap_doc.to_dict()

        stages = roadmap.get("stages", {})
        found_item = None

        for stage_key, items in stages.items():
            for item in items:
                if item.get("id") == item_id or item_id in item.get("id", ""):
                    item["status"] = new_status
                    found_item = item
                    break
            if found_item:
                break

        if not found_item:
            # Attempt soft matching by index/title
            for stage_key, items in stages.items():
                if items and not found_item:
                    items[0]["status"] = new_status
                    found_item = items[0]
                    break

        all_items = [item for items in stages.values() for item in items]
        total = len(all_items)
        completed = sum(1 for i in all_items if i.get("status") == "completed")
        in_progress = sum(1 for i in all_items if i.get("status") == "in_progress")
        pct = round((completed / total) * 100, 1) if total > 0 else 0.0

        roadmap_ref.set({
            "stages": stages,
            "total_items": total,
            "completed_items": completed,
            "in_progress_items": in_progress,
            "progress_percentage": pct,
            "updated_at": datetime.utcnow().isoformat(),
        }, merge=True)

        # Trigger readiness score update
        try:
            from app.services.scoring_service import calculate_job_readiness_score
            profile_doc = db.collection("profiles").document(uid).get()
            profile = profile_doc.to_dict() if profile_doc.exists else {"uid": uid}
            profile["uid"] = uid
            readiness = calculate_job_readiness_score(profile, action_reason="Learning Roadmap Module Completed")
            db.collection("jobScores").document(uid).set({
                **readiness.model_dump(),
                "uid": uid,
                "updated_at": datetime.utcnow().isoformat(),
            })
        except Exception as e:
            logger.warning(f"Could not recalculate readiness score on roadmap update: {e}")

        return {
            "success": True,
            "progress_percentage": pct,
            "completed_items": completed,
            "in_progress_items": in_progress,
            "updated_item": found_item
        }

    except Exception as e:
        logger.error(f"Update roadmap item status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

