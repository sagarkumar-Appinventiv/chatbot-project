from typing import Optional

from pydantic import BaseModel

# Used for signup request body
class UserSignup(BaseModel):
    username: str
    password: str

# Used for login request body
class UserLogin(BaseModel):
    username: str
    password: str

# Used for chat request body
class ChatMessage(BaseModel):
    prompt: str

#new chat
class NewChat(BaseModel):
    title: Optional[str] = "New Chat"