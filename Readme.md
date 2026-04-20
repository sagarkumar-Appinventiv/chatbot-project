# AI Chatbot Project

A full-stack chatbot application with a production-grade LLM gateway for handling multiple AI providers.

---

## Project Structure

```
chatbot-project/
│
├── my-chatbot/              # Frontend (React)
│   ├── src/
│   │   ├── pages/           # Signup, Login, Chat pages
│   │   ├── services/        # API calls to backend
│   │   └── context/         # Auth state management
│   └── package.json
│
├── chatbot-backend/         # Backend (FastAPI)
│   ├── main.py              # FastAPI app entry point
│   ├── auth.py              # JWT authentication
│   ├── chat.py              # Chat endpoints
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Pydantic schemas
│   ├── llm_gateway/         # LLM Gateway (see below)
│   ├── .env                 # API keys and secrets
│   └── requirements.txt
│
└── README.md                # This file
```

---

## What Each Part Does

### Frontend (React + Vite)
The user interface where people chat with the AI.

**Features:**
- User signup and login
- Multiple chat conversations (like ChatGPT)
- Real-time messaging
- Clean, responsive UI

**Tech:** React, React Router, Axios, Context API

---

### Backend (FastAPI + Python)
The server that handles authentication, stores data, and talks to AI models.

**What it does:**
- Verifies users with JWT tokens
- Stores chat history in MongoDB
- Manages multiple conversations per user
- Routes AI requests through the LLM Gateway

**Tech:** FastAPI, MongoDB, Motor (async MongoDB driver), bcrypt

---

### LLM Gateway (Inside Backend)
The smart routing system that talks to multiple AI providers. This is the core innovation of the project.

**Location:** `chatbot-backend/llm_gateway/`

**What it solves:**
- One API key runs out → automatically switches to another
- One AI provider is down → falls back to a different provider
- Messages too long → trims them automatically
- Tracks which models are fast/slow, which keys are healthy

**How it works:**
```
User sends message
       ↓
Backend receives it
       ↓
LLM Gateway picks best available model
       ↓
Groq/Gemini/OpenAI responds
       ↓
User gets reply
```

---

## LLM Gateway — Detailed Breakdown

This is a **reusable library** that can be used in any Python project, not just this chatbot.

### Folder Structure

```
llm_gateway/
├── __init__.py              # Makes it importable
├── config.py                # All models and settings
├── gateway.py               # Main entry point
├── key_manager.py           # Tracks API key health in Redis
├── token_counter.py         # Estimates and trims tokens
├── request_logger.py        # Logs every AI call to MongoDB
├── exceptions.py            # Custom error types
└── providers/
    ├── __init__.py
    ├── base.py              # Blueprint all providers follow
    ├── groq_provider.py     # Groq implementation
    └── gemini_provider.py   # Gemini implementation
```

### Key Features

**1. Multiple API Keys (n-keys)**
Each AI model can have 3-5 API keys. If one hits rate limit, gateway automatically uses the next one.

**2. Smart Fallback Chain**
```
Try Groq Llama 3.1 8B (fast, free)
  → fails? Try Groq Llama 3.3 70B (smarter)
    → fails? Try Gemini Flash (different provider)
      → fails? Return clear error to user
```

**3. Key Health Tracking (Redis)**
When a key fails, it gets a "cooldown" period stored in Redis:
- Rate limit error → 2 min cooldown
- Daily quota hit → 24 hour cooldown
- Invalid key → permanent skip

After cooldown expires, the key is automatically retried. No manual intervention needed.

**4. Token Management**
Counts tokens before sending. If the conversation is too long, removes oldest messages automatically. Prevents token limit errors.

**5. Request Logging (MongoDB)**
Every AI call is logged with:
- Which model was used
- How many tokens (input + output)
- How long it took (latency)
- Success or error

You can query this later to see patterns, debug issues, optimize costs.

**6. Task-Based Routing**
Different tasks go to different models:
- Quick questions → Fast model (Llama 8B)
- Coding questions → Smart model (Llama 70B)
- Creative writing → Content model (Gemini)

**7. Built with LangChain**
LangChain provides a unified interface to talk to all AI providers. Adding a new provider (OpenAI, Anthropic, Azure) is just 20 lines of code.

---

## How to Use the LLM Gateway

### In your code:

```python
from llm_gateway import gateway

# Send a message
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain recursion."}
]

result = await gateway.call(messages, task="general")

print(result.reply)          # The AI's answer
print(result.model_used)     # Which model answered
print(result.total_tokens)   # How many tokens used
print(result.latency_ms)     # How long it took
```

That's it. The gateway handles everything else:
- Picking the right model
- Finding a healthy API key
- Trimming if too long
- Retrying if it fails
- Logging the request

---

## Tech Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React + Vite | User interface |
| Backend | FastAPI | API server |
| Database | MongoDB Atlas | User data, chat history, logs |
| Cache | Redis | Fast key health tracking |
| AI Gateway | LangChain + Custom | Smart AI provider management |
| AI Providers | Groq, Gemini | Actual AI models |
| Auth | JWT + bcrypt | Secure authentication |

---

## Why This Architecture?

**Problem:** Relying on one AI provider is risky. If your API key hits a rate limit or the provider goes down, your entire chatbot stops working.

**Solution:** Multiple providers + multiple keys + automatic failover. The LLM Gateway handles all the complexity. Your chatbot code stays simple — just one function call.

**Benefit:** The gateway is reusable. Any future project that needs AI can import this library and use it immediately. No rewriting. No copy-pasting.

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (free tier)
- Redis installed locally
- API keys from Groq and Gemini

### Backend Setup

```bash
cd chatbot-backend
pip install -r requirements.txt

# Create .env file with your keys
# Start Redis
sudo systemctl start redis

# Run server
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd my-chatbot
npm install
npm run dev
```

### LLM Gateway Setup

```bash
cd chatbot-backend/llm_gateway

# Add API keys to .env
# Test the gateway
python3 test_gateway.py
```

---

## Environment Variables

Create a `.env` file in `chatbot-backend/`:

```env
# MongoDB
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/chatbot

# JWT
SECRET_KEY=your-secret-key-here

# Groq (get from console.groq.com)
GROQ_KEY_1=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_KEY_2=gsk_yyyyyyyyyyyyyyyyyy
GROQ_KEY_3=gsk_zzzzzzzzzzzzzzzzzz

# Gemini (get from aistudio.google.com)
GEMINI_KEY_1=AIzaSyxxxxxxxxxxxxxxxxx
GEMINI_KEY_2=AIzaSyyyyyyyyyyyyyyyyy

# Redis
REDIS_URL=redis://localhost:6379
```

---

## Features Implemented

User authentication (signup/login with JWT)  
Multiple chat conversations per user  
Auto-generated chat titles from first message  
Real-time messaging  
Multi-provider AI with automatic failover  
Smart API key rotation  
Token counting and auto-trimming  
Request logging and performance tracking  
Redis-based key health monitoring  

---

## What Makes This Production-Ready

1. **Resilience** — Never fails due to one provider being down
2. **Observability** — Every request logged, easy to debug
3. **Performance** — Fast key health checks with Redis
4. **Scalability** — Add new models/providers without changing chatbot code
5. **Cost Control** — Tracks token usage, can set limits
6. **Maintainability** — Clean separation: frontend, backend, gateway

---

## Future Enhancements

- [ ] Add OpenAI and Anthropic, mistral, and other providers
- [ ] Admin dashboard to view key health and logs // in progress
- [ ] Rate limiting per user 

---

## Key learnings

- FastAPI async patterns
- JWT authentication
- React Context API
- MongoDB with Motor
- Redis for caching
- LangChain for AI providers
- Circuit breaker pattern
- Fallback chains
- Building reusable libraries

---

## Project is still in progress ...... 

