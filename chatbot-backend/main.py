from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth
import chat

app = FastAPI(title="Chatbot API")

# CORS — allows React on port 5173 to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
async def root():
    return {"message": "Chatbot backend is running ✓"}