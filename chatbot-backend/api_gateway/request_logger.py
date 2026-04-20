# request_logger.py
#
# Logs every LLM call to MongoDB permanently.
# You can query this later:
#   - Which model is slowest?
#   - Which key fails most?
#   - How many tokens per day?
#   - How many slow requests today?

from datetime import datetime
from pymongo import MongoClient
from .config import MONGO_URL
import os

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        client = MongoClient(MONGO_URL)
        db = client["llm_gateway"]
        _collection = db["request_logs"]
    return _collection


async def log_request(
    model:         str,
    key:           str,
    input_tokens:  int,
    output_tokens: int,
    latency_ms:    int,
    slow:          bool,
    status:        str,
    error_msg:     str = None
):
    try:
        col = get_collection()
        col.insert_one({
            "model":         model,
            "key":           "..." + key[-6:],
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "total_tokens":  input_tokens + output_tokens,
            "latency_ms":    latency_ms,
            "slow":          slow,
            "status":        status,
            "error_msg":     error_msg,
            "timestamp":     datetime.utcnow()
        })
    except Exception as e:
        # Never let logging crash the main request
        print(f"[Logger] Failed to log: {e}")