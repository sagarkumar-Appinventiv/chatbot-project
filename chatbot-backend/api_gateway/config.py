# config.py

import os
from dotenv import load_dotenv

load_dotenv()


# ── Model Registry ──────────────────────────────────────────
#
# Format: "provider/model_name"
# provider/model_name"
#
# Each model has:
#   provider          → which company (groq, gemini, openai)
#   model_id          → exact model name that API understands
#   max_input_tokens  → trim messages if longer than this
#   max_output_tokens → max reply length
#   standard_time_s   → mentor said "time should be less than
#                        standard time" — if slower, flag it
#   best_for          → what tasks this model is good at
#   keys              → list of API keys for this model
#                        mentor called this "n-keys"

MODELS = {

    "groq/llama3-8b-8192": {
        "provider":          "groq",
        "model_id":          "llama-3.1-8b-instant",
        "max_input_tokens":  7000,
        "max_output_tokens": 1024,
        "standard_time_s":   5,
        "best_for":          ["general", "chat", "quick"],
        "keys": [
            k for k in [
                os.getenv("GROQ_API_KEY"),  # Use existing env var
                os.getenv("GROQ_KEY_2"),
                os.getenv("GROQ_KEY_3"),
            ] if k
        ]
    },

    "groq/llama3-70b-8192": {
        "provider":          "groq",
        "model_id":          "llama-3.3-70b-versatile",
        "max_input_tokens":  7000,
        "max_output_tokens": 1024,
        "standard_time_s":   10,
        "best_for":          ["complex", "reasoning", "code"],
        "keys": [
            k for k in [
                os.getenv("GROQ_API_KEY"),  # Use existing env var
                os.getenv("GROQ_KEY_2"),
            ] if k
        ]
    },

    "gemini/gemini-1.5-flash": {
        "provider":          "gemini",
        "model_id":          "gemini-1.5-flash",
        "max_input_tokens":  30000,
        "max_output_tokens": 2048,
        "standard_time_s":   8,
        "best_for":          ["long", "content", "creative"],
        "keys": [
            k for k in [
                os.getenv("GEMINI_KEY_1"),
                os.getenv("GEMINI_KEY_2"),
            ] if k
        ]
    },

}


# ── Fallback Chain ──────────────────────────────────────────
#
# Gateway tries models in this exact order.
# If first fails → try second → try third.
# Put fastest and cheapest first.

FALLBACK_CHAIN = [
    "groq/llama3-8b-8192",
    "groq/llama3-70b-8192",
    "gemini/gemini-1.5-flash",
]


# ── Task to Model Mapping ───────────────────────────────────

# When caller says task="code" → we try groq/llama3-70b first
# When caller says task="general" → we use default chain

TASK_PREFERRED_MODEL = {
    "general":  "groq/llama3-8b-8192",
    "quick":    "groq/llama3-8b-8192",
    "code":     "groq/llama3-70b-8192",
    "reasoning":"groq/llama3-70b-8192",
    "long":     "gemini/gemini-1.5-flash",
    "creative": "gemini/gemini-1.5-flash",
}


# ── Cooldown Durations (in seconds) ────────────────────────
# 
# When a key fails, it gets this cooldown in Redis.
# Redis auto-deletes the record after TTL expires.
# That is how "auto-recovery" works — no manual cleanup.

COOLDOWNS = {
    "rate_limit":   120,        # 2 minutes
    "daily_limit":  86400,      # 24 hours
    "invalid_key":  31536000,   # 1 year = permanent skip
    "server_error": 300,        # 5 minutes
    "timeout":      60,         # 1 minute
    "empty":        30,         # 30 seconds
}


# ── Redis ───────────────────────────────────────────────────
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")


# ── MongoDB ─────────────────────────────────────────────────
MONGO_URL = os.getenv("MONGO_URL")