"""
CareerPilot AI — Community & Peer Network Router
"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user_optional, get_current_user
from app.schemas.models import CommunityPostCreateRequest, CommunityCommentCreateRequest
from datetime import datetime
import html
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

MOCK_POSTS = [
    {
        "id": "post-1",
        "author": "Alex Chen",
        "avatar": "AC",
        "role": "Aspiring AI Engineer",
        "title": "Looking for study partners for System Design & LeetCode Hard!",
        "content": "Hi everyone! I'm preparing for AI/ML engineering interviews and want to form a 3-4 person study group meeting twice a week. Let me know if you'd like to join!",
        "tags": ["Study Group", "System Design", "Interview Prep"],
        "upvotes": 14,
        "comments_count": 2,
        "created_at": "2 hours ago"
    },
    {
        "id": "post-2",
        "author": "Priya Sharma",
        "avatar": "PS",
        "role": "Frontend Developer",
        "title": "Building an open source React + FastAPI project — looking for contributors",
        "content": "We are building an open-source student productivity tracker. Need 1 backend developer proficient in Python/FastAPI. Great for portfolio projects!",
        "tags": ["Collaboration", "Open Source", "FastAPI", "React"],
        "upvotes": 29,
        "comments_count": 1,
        "created_at": "5 hours ago"
    },
    {
        "id": "post-3",
        "author": "Marcus Vance",
        "avatar": "MV",
        "role": "Data Scientist",
        "title": "How I boosted my Job Readiness score from 45 to 88 in 30 days",
        "content": "Focus on high-value projects and getting key cloud certifications. Added Docker and AWS credentials which made a massive difference during resume screening.",
        "tags": ["Career Advice", "Job Readiness", "Certifications"],
        "upvotes": 52,
        "comments_count": 1,
        "created_at": "1 day ago"
    }
]

MOCK_COMMENTS: dict = {
    "post-1": [
        {
            "id": "comment-101",
            "author": "Rohan Mehta",
            "avatar": "RM",
            "role": "Backend Intern",
            "content": "Count me in! I'm focusing on distributed caching and database indexing.",
            "created_at": "1 hour ago"
        },
        {
            "id": "comment-102",
            "author": "Sarah Jenkins",
            "avatar": "SJ",
            "role": "Full Stack Dev",
            "content": "Interested as well! Are you hosting the sessions on Discord or Zoom?",
            "created_at": "30 mins ago"
        }
    ],
    "post-2": [
        {
            "id": "comment-201",
            "author": "Vikram Patel",
            "avatar": "VP",
            "role": "Python Enthusiast",
            "content": "I can help with the FastAPI endpoints and Pydantic schemas! Sent you a message.",
            "created_at": "3 hours ago"
        }
    ],
    "post-3": [
        {
            "id": "comment-301",
            "author": "Emily Zhang",
            "avatar": "EZ",
            "role": "Student SDE",
            "content": "Solid advice! Getting AWS Cloud Practitioner really boosted my profile visibility.",
            "created_at": "18 hours ago"
        }
    ]
}

@router.get("/posts")
async def get_community_posts(user: dict = Depends(get_current_user_optional)):
    return {"posts": MOCK_POSTS}

@router.post("/posts")
async def create_community_post(
    payload: CommunityPostCreateRequest,
    user: dict = Depends(get_current_user_optional)
):
    # Sanitize inputs against stored XSS
    title = html.escape(payload.title.strip())
    content = html.escape(payload.content.strip())
    tags = [html.escape(t.strip()[:30]) for t in payload.tags[:5] if t.strip()] or ["General"]
    
    author_name = user.get("name", "Student User") if user else "Student User"
    author_name = html.escape(author_name[:50])
    avatar = (author_name or "U")[0].upper()
    role = user.get("target_career", "Active Member") if user else "Active Member"
    role = html.escape(role[:50])

    new_post = {
        "id": f"post-{len(MOCK_POSTS) + 1}_{int(datetime.utcnow().timestamp())}",
        "author": author_name,
        "avatar": avatar,
        "role": role,
        "title": title,
        "content": content,
        "tags": tags,
        "upvotes": 1,
        "comments_count": 0,
        "created_at": "Just now"
    }
    MOCK_POSTS.insert(0, new_post)
    return new_post

@router.post("/posts/{post_id}/upvote")
@router.post("/posts/{post_id}/like")
async def upvote_post(
    post_id: str,
    user: dict = Depends(get_current_user_optional)
):
    for post in MOCK_POSTS:
        if post["id"] == post_id:
            post["upvotes"] = post.get("upvotes", 0) + 1
            return {"message": "Upvoted post successfully", "upvotes": post["upvotes"]}
    raise HTTPException(status_code=404, detail="Post not found")

@router.get("/posts/{post_id}/comments")
async def get_post_comments(
    post_id: str,
    user: dict = Depends(get_current_user_optional)
):
    comments = MOCK_COMMENTS.get(post_id, [])
    return {"comments": comments}

@router.post("/posts/{post_id}/comments")
async def add_post_comment(
    post_id: str,
    payload: CommunityCommentCreateRequest,
    user: dict = Depends(get_current_user_optional)
):
    content = html.escape(payload.content.strip())
    if not content:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")

    author = user.get("name", "Candidate Peer") if user else "Candidate Peer"
    author = html.escape(author[:50])
    avatar = author[0].upper()
    role = user.get("target_career", "Student Developer") if user else "Student Developer"
    role = html.escape(role[:50])

    new_comment = {
        "id": f"comment-{post_id}-{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:4]}",
        "author": author,
        "avatar": avatar,
        "role": role,
        "content": content,
        "created_at": "Just now"
    }

    if post_id not in MOCK_COMMENTS:
        MOCK_COMMENTS[post_id] = []
    MOCK_COMMENTS[post_id].append(new_comment)

    # Update comments_count on post
    for post in MOCK_POSTS:
        if post["id"] == post_id:
            post["comments_count"] = len(MOCK_COMMENTS[post_id])
            break

    return {"message": "Comment added", "comment": new_comment}

