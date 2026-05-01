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

    "gemini/gemini-3-flash-preview": {
        "provider":          "gemini",
        "model_id":          "gemini-3-flash-preview",
        "max_input_tokens":  30000,
        "max_output_tokens": 2048,
        "standard_time_s":   6,
        "best_for":          ["long", "content", "general"],
        "keys": [
            k for k in [
                os.getenv("GEMINI_API_KEY"),
                os.getenv("GEMINI_KEY_1"),
            ] if k
        ]
    },

    "gemini/gemini-3.1-flash-lite-preview": {
        "provider":          "gemini",
        "model_id":          "gemini-3.1-flash-lite-preview",
        "max_input_tokens":  128000,
        "max_output_tokens": 4096,
        "standard_time_s":   4,
        "best_for":          ["quick", "general", "chat"],
        "keys": [
            k for k in [
                os.getenv("GEMINI_API_KEY"),
            ] if k
        ]
    },

    "gemini/gemini-3.1-pro-preview": {
        "provider":          "gemini",
        "model_id":          "gemini-3.1-pro-preview",
        "max_input_tokens":  128000,
        "max_output_tokens": 4096,
        "standard_time_s":   12,
        "best_for":          ["code", "reasoning", "complex"],
        "keys": [
            k for k in [
                os.getenv("GEMINI_API_KEY"),
            ] if k
        ]
    },

    "gemini/gemini-2.5-flash-lite": {
        "provider":          "gemini",
        "model_id":          "gemini-2.5-flash-lite",
        "max_input_tokens":  100000,
        "max_output_tokens": 4096,
        "standard_time_s":   5,
        "best_for":          ["quick", "general", "chat"],
        "keys": [
            k for k in [
                os.getenv("GEMINI_API_KEY"),
            ] if k
        ]
    },

    "mistral/mistral-small-2603": {
        "provider":          "mistral",
        "model_id":          "mistral-small-2603",
        "max_input_tokens":  32000,
        "max_output_tokens": 1024,
        "standard_time_s":   4,
        "best_for":          ["quick", "general", "chat"],
        "keys": [
            k for k in [
                os.getenv("MISTRAL_API_KEY"),
            ] if k
        ]
    },

    "mistral/ministral-8b-2512": {
        "provider":          "mistral",
        "model_id":          "ministral-8b-2512",
        "max_input_tokens":  32000,
        "max_output_tokens": 1024,
        "standard_time_s":   3,
        "best_for":          ["quick", "general", "chat"],
        "keys": [
            k for k in [
                os.getenv("MISTRAL_API_KEY"),
            ] if k
        ]
    },

    "mistral/ministral-14b-2512": {
        "provider":          "mistral",
        "model_id":          "ministral-14b-2512",
        "max_input_tokens":  32000,
        "max_output_tokens": 1024,
        "standard_time_s":   5,
        "best_for":          ["general", "code", "reasoning"],
        "keys": [
            k for k in [
                os.getenv("MISTRAL_API_KEY"),
            ] if k
        ]
    },

    "mistral/mistral-large-2512": {
        "provider":          "mistral",
        "model_id":          "mistral-large-2512",
        "max_input_tokens":  32000,
        "max_output_tokens": 2048,
        "standard_time_s":   10,
        "best_for":          ["complex", "code", "reasoning"],
        "keys": [
            k for k in [
                os.getenv("MISTRAL_API_KEY"),
            ] if k
        ]
    },

    "openrouter/ling-2.6-flash": {
        "provider":          "openrouter",
        "model_id":          "inclusionai/ling-2.6-flash:free",
        "max_input_tokens":  8000,
        "max_output_tokens": 512,
        "standard_time_s":   3,
        "best_for":          ["quick", "generation"],
        "keys": [
            k for k in [
                os.getenv("OPENROUTER_API_KEY"),
            ] if k
        ]
    },

    "openrouter/gpt-oss-120b": {
        "provider":          "openrouter",
        "model_id":          "openai/gpt-oss-120b:free",
        "max_input_tokens":  4096,
        "max_output_tokens": 1024,
        "standard_time_s":   12,
        "best_for":          ["reasoning", "complex"],
        "keys": [
            k for k in [
                os.getenv("OPENROUTER_API_KEY"),
            ] if k
        ]
    },

    "openrouter/nemotron-3-super-120b": {
        "provider":          "openrouter",
        "model_id":          "nvidia/nemotron-3-super-120b-a12b:free",
        "max_input_tokens":  4096,
        "max_output_tokens": 1024,
        "standard_time_s":   10,
        "best_for":          ["code", "reasoning"],
        "keys": [
            k for k in [
                os.getenv("OPENROUTER_API_KEY"),
            ] if k
        ]
    },

    "openrouter/trinity-large-preview": {
        "provider":          "openrouter",
        "model_id":          "arcee-ai/trinity-large-preview:free",
        "max_input_tokens":  8000,
        "max_output_tokens": 1024,
        "standard_time_s":   8,
        "best_for":          ["reasoning", "analysis"],
        "keys": [
            k for k in [
                os.getenv("OPENROUTER_API_KEY"),
            ] if k
        ]
    },

    "openrouter/glm-4.5-air": {
        "provider":          "openrouter",
        "model_id":          "z-ai/glm-4.5-air:free",
        "max_input_tokens":  8000,
        "max_output_tokens": 1024,
        "standard_time_s":   7,
        "best_for":          ["general", "chat"],
        "keys": [
            k for k in [
                os.getenv("OPENROUTER_API_KEY"),
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
    "mistral/ministral-8b-2512",
    "gemini/gemini-3.1-flash-lite-preview",
    "groq/llama3-70b-8192",
    "mistral/mistral-large-2512",
    "gemini/gemini-3.1-pro-preview",
    "openrouter/ling-2.6-flash",
]


# ── Task to Model Mapping ───────────────────────────────────

# When caller says task="code" → we try groq/llama3-70b first
# When caller says task="general" → we use default chain

TASK_PREFERRED_MODEL = {
    "general":   "groq/llama3-8b-8192",
    "quick":     "mistral/ministral-8b-2512",
    "code":      "groq/llama3-70b-8192",
    "reasoning": "mistral/mistral-large-2512",
    "long":      "gemini/gemini-3.1-pro-preview",
    "creative":  "gemini/gemini-3-flash-preview",
    "complex":   "mistral/mistral-large-2512",
    "analysis":  "openrouter/trinity-large-preview",
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