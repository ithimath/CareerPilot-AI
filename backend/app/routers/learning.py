"""Learning roadmap router"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.services.career_service import get_skill_gap_for_career
from app.services.data_service import get_courses_for_skill
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

STAGE_NAMES = {
    1: "Fundamentals",
    2: "Core Skills",
    3: "Advanced Skills",
    4: "Projects & Portfolio",
    5: "Interview Preparation",
}


def _build_roadmap(target_career: str, missing_skills: list) -> dict:
    """Build a 5-stage learning roadmap from missing skills."""
    # Partition skills by importance into stages
    stages = {str(i): [] for i in range(1, 6)}

    importance_to_stage = {
        "critical": "1",
        "high": "2",
        "medium": "3",
        "low": "4",
    }

    for item in missing_skills[:20]:  # Cap at 20 skills for roadmap
        stage_key = importance_to_stage.get(item.get("importance", "medium"), "3")
        skill = item["skill"]
        courses = get_courses_for_skill(skill)

        for i, course in enumerate(courses[:2]):  # max 2 courses per skill
            learning_item = {
                "id": str(uuid.uuid4()),
                "title": course.get("title", f"Learn {skill}"),
                "description": f"Master {skill} through this comprehensive course",
                "resource_url": course.get("url", ""),
                "skill": skill,
                "stage": int(stage_key),
                "stage_name": STAGE_NAMES[int(stage_key)],
                "status": "not_started",
                "difficulty": course.get("difficulty", "medium"),
                "platform": course.get("platform", ""),
            }
            stages[stage_key].append(learning_item)

    # Stage 5: Interview Prep (always included)
    stages["5"].append({
        "id": str(uuid.uuid4()),
        "title": f"Mock Interviews for {target_career}",
        "description": "Practice with LeetCode, system design, and behavioral questions",
        "resource_url": "https://leetcode.com",
        "skill": "Interview Skills",
        "stage": 5,
        "stage_name": "Interview Preparation",
        "status": "not_started",
        "difficulty": "hard",
        "platform": "LeetCode",
    })

    return stages


@router.get("")
async def get_learning_roadmap(user: dict = Depends(get_current_user)):
    """Get the learning roadmap for the user's target career."""
    try:
        db = get_firestore()
        uid = user["uid"]

        # Check if roadmap exists in Firestore
        roadmap_doc = db.collection("learningProgress").document(uid).get()

        profile_doc = db.collection("profiles").document(uid).get()
        if not profile_doc.exists:
            raise HTTPException(status_code=404, detail="Profile not found")

        profile = profile_doc.to_dict()
        target_career = profile.get("target_career", "")

        if not target_career:
            return {"message": "No target career selected", "roadmap": None}

        if roadmap_doc.exists:
            roadmap = roadmap_doc.to_dict()
            # Regenerate if target career changed
            if roadmap.get("target_career") == target_career:
                return roadmap

        # Generate fresh roadmap
        skills = profile.get("skills", [])
        gap = get_skill_gap_for_career(skills, target_career)
        missing_skills = gap.get("missing_skills", [])
        stages = _build_roadmap(target_career, missing_skills)

        total_items = sum(len(items) for items in stages.values())
        roadmap_data = {
            "uid": uid,
            "target_career": target_career,
            "stages": stages,
            "total_items": total_items,
            "completed_items": 0,
            "in_progress_items": 0,
            "progress_percentage": 0.0,
            "generated_at": datetime.utcnow(),
        }
        db.collection("learningProgress").document(uid).set(roadmap_data)
        return roadmap_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get roadmap failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/item/{item_id}/status")
async def update_item_status(
    item_id: str, data: dict, user: dict = Depends(get_current_user)
):
    """Update the status of a learning item (not_started|in_progress|completed)."""
    new_status = data.get("status", "not_started")
    if new_status not in ("not_started", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        db = get_firestore()
        uid = user["uid"]
        roadmap_ref = db.collection("learningProgress").document(uid)
        roadmap_doc = roadmap_ref.get()
        if not roadmap_doc.exists:
            raise HTTPException(status_code=404, detail="Roadmap not found")

        roadmap = roadmap_doc.to_dict()
        stages = roadmap.get("stages", {})
        found = False

        for stage_key, items in stages.items():
            for item in items:
                if item.get("id") == item_id:
                    item["status"] = new_status
                    found = True
                    break
            if found:
                break

        if not found:
            raise HTTPException(status_code=404, detail="Learning item not found")

        # Recalculate progress
        all_items = [item for items in stages.values() for item in items]
        completed = sum(1 for i in all_items if i.get("status") == "completed")
        in_progress = sum(1 for i in all_items if i.get("status") == "in_progress")
        total = len(all_items)
        progress_pct = round(completed / total * 100, 1) if total > 0 else 0.0

        roadmap_ref.update({
            "stages": stages,
            "completed_items": completed,
            "in_progress_items": in_progress,
            "progress_percentage": progress_pct,
            "updated_at": datetime.utcnow(),
        })

        return {
            "success": True,
            "progress_percentage": progress_pct,
            "completed_items": completed,
            "in_progress_items": in_progress,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
