# token_counter.py
#
# FLOW:
# 1. estimate_messages(messages) → count tokens before sending
# 2. trim(messages, limit)       → cut oldest if too long
#
# Rule: 1 token ≈ 4 characters + 10% safety buffer
# Not 100% accurate but close enough for our purpose.
# Real tokenizers (tiktoken) are complex — this is good enough.


def estimate(text: str) -> int:
    if not text:
        return 0
    return int(len(text) / 4 * 1.1)


def estimate_messages(messages: list) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        total += estimate(content)
        total += 4      # every message has role + formatting overhead
    return total


def trim(messages: list, max_tokens: int) -> list:
    """
    If messages are too long, remove oldest ones.

    Always keeps:
      system message   → instructions, never remove
      last 2 messages  → immediate context, always keep

    Example:
      messages = [system, msg1, msg2, msg3, msg4, msg5]
      max_tokens = 500
      msg1 makes it too long → remove msg1
      still too long → remove msg2
      fits now → return [system, msg3, msg4, msg5]
    """
    if estimate_messages(messages) <= max_tokens:
        return messages     # fits already, nothing to do

    system_msgs = [m for m in messages if m["role"] == "system"]
    convo_msgs  = [m for m in messages if m["role"] != "system"]

    removed = 0
    while (
        estimate_messages(system_msgs + convo_msgs) > max_tokens
        and len(convo_msgs) > 2
    ):
        convo_msgs.pop(0)
        removed += 1

    if removed:
        print(f"[TokenCounter] Removed {removed} old messages to fit limit")

    return system_msgs + convo_msgs