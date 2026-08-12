"""AI Career Mentor Chatbot router — Gemini-powered with Firestore history"""
from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_current_user
from app.core.firebase import get_firestore
from app.services.gemini_service import chat_with_mentor
from app.schemas.models import ChatRequest, ChatResponse
from datetime import datetime
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/send")
async def send_message(data: ChatRequest, user: dict = Depends(get_current_user)):
    """Send a message to the AI mentor and get a response."""
    try:
        db = get_firestore()
        uid = user["uid"]

        # Get or create conversation
        conv_id = data.conversation_id or str(uuid.uuid4())
        conv_ref = (
            db.collection("chatHistory")
            .document(uid)
            .collection("conversations")
            .document(conv_id)
        )

        # Load conversation history
        conv_doc = conv_ref.get()
        if conv_doc.exists:
            messages = conv_doc.to_dict().get("messages", [])
        else:
            messages = []
            conv_ref.set({
                "id": conv_id,
                "uid": uid,
                "title": data.message[:60] + ("..." if len(data.message) > 60 else ""),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "messages": [],
            })

        # Get student profile for context
        profile_doc = db.collection("profiles").document(uid).get()
        student_profile = profile_doc.to_dict() if profile_doc.exists else None

        # Get AI response
        history_for_gemini = [
            {"role": m["role"], "content": m["content"]}
            for m in messages[-20:]
        ]
        reply = await chat_with_mentor(
            message=data.message,
            history=history_for_gemini,
            student_profile=student_profile,
        )

        # Persist messages
        now = datetime.utcnow()
        user_msg = {"role": "user", "content": data.message, "timestamp": now.isoformat()}
        assistant_msg = {"role": "assistant", "content": reply, "timestamp": now.isoformat()}
        messages.extend([user_msg, assistant_msg])

        conv_ref.update({
            "messages": messages,
            "updated_at": now,
        })

        return ChatResponse(reply=reply, conversation_id=conv_id)

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations(user: dict = Depends(get_current_user)):
    """List all conversations for the user."""
    try:
        db = get_firestore()
        uid = user["uid"]
        convs = (
            db.collection("chatHistory")
            .document(uid)
            .collection("conversations")
            .order_by("updated_at", direction="DESCENDING")
            .limit(20)
            .stream()
        )
        result = []
        for doc in convs:
            data = doc.to_dict()
            data["id"] = doc.id
            # Don't send all messages in list view
            data.pop("messages", None)
            result.append(data)
        return {"conversations": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str, user: dict = Depends(get_current_user)):
    """Get a specific conversation with all messages."""
    try:
        db = get_firestore()
        uid = user["uid"]
        doc = (
            db.collection("chatHistory")
            .document(uid)
            .collection("conversations")
            .document(conv_id)
            .get()
        )
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Conversation not found")
        data = doc.to_dict()
        if data.get("uid") != uid:
            raise HTTPException(status_code=403, detail="Not authorized")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversations/{conv_id}")
async def delete_conversation(conv_id: str, user: dict = Depends(get_current_user)):
    """Delete a conversation."""
    try:
        db = get_firestore()
        uid = user["uid"]
        ref = (
            db.collection("chatHistory")
            .document(uid)
            .collection("conversations")
            .document(conv_id)
        )
        doc = ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Conversation not found")
        if doc.to_dict().get("uid") != uid:
            raise HTTPException(status_code=403, detail="Not authorized")
        ref.delete()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
