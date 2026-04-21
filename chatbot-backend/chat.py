from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv

from database import messages_collection, chats_collection
from models import ChatMessage, NewChat
from auth import get_current_user
from api_gateway.gateway import call

load_dotenv()

router = APIRouter()


# ── Helper: convert MongoDB doc to JSON friendly dict ──────
# MongoDB uses ObjectId for _id which is not JSON serializable
# This converts it to a string
def format_doc(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# ── 1. Create a new chat ───────────────────────────────────
@router.post("/new")
async def create_chat(
    data: NewChat,
    current_user: dict = Depends(get_current_user)
):
    username = current_user["username"]

    # Insert new chat into chats collection
    result = await chats_collection.insert_one({
        "username": username,
        "title": data.title,
        "created_at": datetime.utcnow()
    })

    # Return the new chat's ID — frontend needs this
    return {
        "chat_id": str(result.inserted_id),
        "title": data.title,
        "message": "Chat created"
    }


# ── 2. Get all chats of logged in user ─────────────────────
@router.get("/all")
async def get_all_chats(
    current_user: dict = Depends(get_current_user)
):
    username = current_user["username"]

    # Find all chats belonging to this user
    # Sort by newest first
    cursor = chats_collection.find(
        {"username": username}
    ).sort("created_at", -1)

    chats = await cursor.to_list(100)

    # Format each doc for JSON response
    return {"chats": [format_doc(chat) for chat in chats]}


# ── 3. Get messages of a specific chat ─────────────────────
@router.get("/{chat_id}/messages")
async def get_chat_messages(
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    username = current_user["username"]

    # First verify this chat belongs to this user
    # Security check — user should not see other's chats
    chat = await chats_collection.find_one({
        "_id": ObjectId(chat_id),
        "username": username
    })
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get all messages of this chat
    cursor = messages_collection.find(
        {"chat_id": chat_id}
    ).sort("timestamp", 1)

    messages = await cursor.to_list(500)

    return {"messages": [format_doc(msg) for msg in messages]}


# ── 4. Send message in a specific chat ─────────────────────
@router.post("/{chat_id}/send")
async def send_message(
    chat_id: str,
    data: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    username = current_user["username"]

    # Verify chat belongs to this user
    chat = await chats_collection.find_one({
        "_id": ObjectId(chat_id),
        "username": username
    })
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Get last 50 messages of THIS chat only
    past_cursor = messages_collection.find(
        {"chat_id": chat_id}        # ← filtered by chat_id now
    ).sort("timestamp", 1)
    past = await past_cursor.to_list(50)

    # Build messages in OpenAI-compatible format
    # Gateway handles provider-specific conversion (Groq, Gemini, etc.)
    messages = [
        {
            "role": "system",
            "content": "You are a helpful AI assistant. Answer clearly and concisely."
        }
    ]

    for msg in past:
        role = "assistant" if msg["role"] == "model" else "user"
        messages.append({
            "role": role,
            "content": msg["content"]
        })

    messages.append({
        "role": "user",
        "content": data.prompt
    })

    # Call AI through gateway (single source of truth)
    result = await call(
        messages=messages,
        task="general",
        max_tokens=1024,
        temperature=0.7
    )
    reply = result.reply

    # Save user message — now includes chat_id
    await messages_collection.insert_one({
        "chat_id": chat_id,            # ← new field
        "username": username,
        "role": "user",
        "content": data.prompt,
        "timestamp": datetime.utcnow()
    })

    # Save assistant reply
    await messages_collection.insert_one({
        "chat_id": chat_id,            # ← new field
        "username": username,
        "role": "model",
        "content": reply,
        "timestamp": datetime.utcnow()
    })

    # Update chat title automatically from first message
    # If title is still "New Chat", use first 30 chars of prompt
    if chat["title"] == "New Chat":
        auto_title = data.prompt[:30] + "..." if len(data.prompt) > 30 else data.prompt
        await chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"title": auto_title}}
        )

    return {"reply": reply}


# ── 5. Delete a chat and all its messages ──────────────────
@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: dict = Depends(get_current_user)
):
    username = current_user["username"]

    # Verify ownership
    chat = await chats_collection.find_one({
        "_id": ObjectId(chat_id),
        "username": username
    })
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Delete all messages of this chat
    await messages_collection.delete_many({"chat_id": chat_id})

    # Delete the chat itself
    await chats_collection.delete_one({"_id": ObjectId(chat_id)})

    return {"message": "Chat deleted"}