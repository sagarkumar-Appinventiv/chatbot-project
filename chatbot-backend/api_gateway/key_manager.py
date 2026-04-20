# key_manager.py
#
# FLOW:
# 1. get_best_key(model_path)
#    → loops through all keys of that model
#    → checks Redis: is this key in cooldown?
#    → returns first healthy key
#    → returns None if all unhealthy
#
# 2. mark_unhealthy(model, key, error_type)
#    → stores error in Redis with TTL
#    → TTL comes from COOLDOWNS in config
#    → Redis auto-deletes after TTL → key auto-recovers
#
# 3. mark_healthy(model, key)
#    → deletes Redis record
#    → key is clean again
#
# WHY REDIS and not MongoDB?
#    MongoDB query = 5-20ms (network round trip)
#    Redis query   = 0.1-0.5ms (in-memory)
#    We check keys on EVERY request → must be fast


import redis.asyncio as aioredis
from .config import MODELS, COOLDOWNS, REDIS_URL

_redis_client = None


async def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            REDIS_URL,
            decode_responses=True
        )
    return _redis_client


def _redis_key(model_path: str, api_key: str) -> str:
    # Format: "gw:health:groq/llama3-8b:...KEY_3"
    # Only last 8 chars of API key stored — security
    return f"gw:health:{model_path}:{api_key[-8:]}"


async def is_key_healthy(model_path: str, api_key: str) -> bool:
    try:
        r = await get_redis()
        # If record exists → in cooldown → unhealthy
        # If no record → never failed OR cooldown expired → healthy
        record = await r.get(_redis_key(model_path, api_key))
        return record is None
    except Exception as e:
        # If Redis fails, assume key is healthy
        print(f"[Gateway] Redis unavailable, assuming key healthy: {e}")
        return True


async def mark_unhealthy(model_path: str, api_key: str, error_type: str):
    try:
        r = await get_redis()
        ttl  = COOLDOWNS.get(error_type, 300)
        name = _redis_key(model_path, api_key)
        # setex = set with expiry (TTL in seconds)
        # After TTL → Redis deletes it → key auto-recovers
        await r.setex(name, ttl, error_type)
        print(f"[KeyManager] {model_path} ...{api_key[-6:]} → {error_type} ({ttl}s)")
    except Exception as e:
        print(f"[KeyManager] Redis unavailable, skipping mark_unhealthy: {e}")


async def mark_healthy(model_path: str, api_key: str):
    try:
        r = await get_redis()
        await r.delete(_redis_key(model_path, api_key))
    except Exception as e:
        print(f"[KeyManager] Redis unavailable, skipping mark_healthy: {e}")


async def get_best_key(model_path: str):
    config = MODELS.get(model_path)
    if not config:
        return None

    for key in config["keys"]:
        if await is_key_healthy(model_path, key):
            return key

    return None     # all keys in cooldown


async def warmup():
    """
    Check all keys on startup before any user hits the server.
    """
    print("\n[Gateway] Warming up...")
    r = await get_redis()

    for model_path, config in MODELS.items():
        if not config["keys"]:
            print(f"  {model_path} → NO KEYS CONFIGURED")
            continue
        for key in config["keys"]:
            record = await r.get(_redis_key(model_path, key))
            if record:
                print(f"  {model_path} ...{key[-6:]} → unhealthy ({record})")
            else:
                print(f"  {model_path} ...{key[-6:]} → healthy")

    print("[Gateway] Warmup done\n")

    