# gateway.py
#
# THIS IS THE ONLY FILE YOUR CHATBOT NEEDS TO IMPORT.
#
# Full flow on every call:
#
# 1. Estimate input tokens
# 2. Pick model based on task type
# 3. Build fallback chain
# 4. For each model in chain:
#    a. Trim messages if too long for this model
#    b. Get healthy key from Redis
#    c. Call model via LangChain with 30s timeout
#    d. If success → log → return response
#    e. If fail   → classify error → cooldown in Redis → try next
# 5. If all fail → raise AllModelsFailedError


import asyncio
import time
from .config import MODELS, FALLBACK_CHAIN, TASK_PREFERRED_MODEL
from .token_counter import estimate_messages, trim
from .key_manager import get_best_key, mark_healthy, mark_unhealthy, warmup
from .request_logger import log_request
from .providers import get_provider
from .exceptions import AllModelsFailedError, EmptyResponseError


class GatewayResponse:
    """
    What your chatbot gets back from gateway.call()

    result.reply          → the AI reply text
    result.model_used     → "groq/llama3-8b-8192"
    result.input_tokens   → tokens you sent
    result.output_tokens  → tokens in reply
    result.total_tokens   → input + output
    result.latency_ms     → how long it took
    result.slow           → True if slower than standard
    result.key_used       → "...KEY_3" (last 6 chars)
    """
    def __init__(
        self, reply, model_used, input_tokens,
        output_tokens, latency_ms, slow, key_used
    ):
        self.reply         = reply
        self.model_used    = model_used
        self.input_tokens  = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens  = input_tokens + output_tokens
        self.latency_ms    = latency_ms
        self.slow          = slow
        self.key_used      = key_used


async def call(
    messages:    list,
    task:        str  = "general",
    max_tokens:  int  = 1024,
    temperature: float = 0.7
) -> GatewayResponse:

    # Step 1 — count input tokens
    input_tokens = estimate_messages(messages)

    # Step 2 — build chain
    # task type decides which model goes first
    # Example: task="code" → llama3-70b first
    preferred = TASK_PREFERRED_MODEL.get(task, FALLBACK_CHAIN[0])

    chain = []
    if preferred in MODELS:
        chain.append(preferred)
    for model in FALLBACK_CHAIN:
        if model not in chain:
            chain.append(model)

    print(f"[Gateway] Task={task} | Chain={chain}")

    # Step 3 — try each model
    for model_path in chain:
        config   = MODELS[model_path]
        provider = get_provider(config["provider"])

        # Trim messages if too long for this model
        safe_messages = trim(messages, config["max_input_tokens"])

        # Get healthy key
        key = await get_best_key(model_path)
        if not key:
            print(f"[Gateway] No healthy keys for {model_path} → skip")
            continue

        print(f"[Gateway] Trying {model_path} with key ...{key[-6:]}")

        start = time.time()
        try:
            # 30 second hard timeout
            reply = await asyncio.wait_for(
                provider.call(
                    safe_messages,
                    key,
                    config["model_id"],
                    max_tokens,
                    temperature
                ),
                timeout=30.0
            )

            # Empty response check
            if not reply or not reply.strip():
                raise EmptyResponseError("Model returned empty response")

            # Calculate metrics
            latency_ms    = int((time.time() - start) * 1000)
            output_tokens = estimate_messages([{"content": reply}])
            slow          = latency_ms > (config["standard_time_s"] * 1000)

            if slow:
                print(f"[Gateway] SLOW: {model_path} took {latency_ms}ms "
                      f"(standard: {config['standard_time_s']}s)")

            # Mark key healthy
            await mark_healthy(model_path, key)

            # Log to MongoDB
            await log_request(
                model=model_path,
                key=key,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                slow=slow,
                status="success"
            )

            print(f"[Gateway] Success: {model_path} | "
                  f"{latency_ms}ms | {input_tokens+output_tokens} tokens")

            return GatewayResponse(
                reply=reply,
                model_used=model_path,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                slow=slow,
                key_used="..." + key[-6:]
            )

        except asyncio.TimeoutError:
            latency_ms = 30000
            print(f"[Gateway] Timeout: {model_path}")
            await mark_unhealthy(model_path, key, "timeout")
            await log_request(
                model=model_path, key=key,
                input_tokens=input_tokens, output_tokens=0,
                latency_ms=latency_ms, slow=True,
                status="timeout", error_msg="30s hard timeout"
            )
            continue

        except Exception as e:
            error_str  = str(e)
            error_type = provider.classify_error(error_str)
            latency_ms = int((time.time() - start) * 1000)
            print(f"[Gateway] Error: {model_path} | {error_type} | {error_str[:80]}")
            await mark_unhealthy(model_path, key, error_type)
            await log_request(
                model=model_path, key=key,
                input_tokens=input_tokens, output_tokens=0,
                latency_ms=latency_ms, slow=False,
                status=error_type, error_msg=error_str[:200]
            )
            continue

    # Everything failed
    raise AllModelsFailedError(
        "All models are currently unavailable. Please try again later."
    )