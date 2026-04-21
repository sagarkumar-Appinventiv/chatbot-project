# test_gateway.py
# Run this to verify everything works before connecting to chatbot

import asyncio
import sys
sys.path.insert(0, '/home/appinventiv/ChatBot_practice/chatbot-backend')

from api_gateway import call, warmup


async def main():

    # ── Test 0: Warmup ─────────────────────────────────────
    print("=" * 50)
    print("TEST 0: Warmup")
    print("=" * 50)
    await warmup()


    # ── Test 1: Basic call ─────────────────────────────────
    print("=" * 50)
    print("TEST 1: Basic call")
    print("=" * 50)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "What is 2 + 2? One word answer."}
    ]
    result = await call(messages, task="general")
    print(f"Reply:        {result.reply}")
    print(f"Model used:   {result.model_used}")
    print(f"Input tokens: {result.input_tokens}")
    print(f"Output tokens:{result.output_tokens}")
    print(f"Latency:      {result.latency_ms}ms")
    print(f"Slow:         {result.slow}")


    # ── Test 2: Memory test ────────────────────────────────
    print("\n" + "=" * 50)
    print("TEST 2: Memory — does it remember context?")
    print("=" * 50)
    messages2 = [
        {"role": "system",    "content": "You are a helpful assistant."},
        {"role": "user",      "content": "My name is Ravi."},
        {"role": "assistant", "content": "Hello Ravi! Nice to meet you."},
        {"role": "user",      "content": "What is my name?"}
    ]
    result2 = await call(messages2, task="general")
    print(f"Reply: {result2.reply}")
    print(f"Model: {result2.model_used}")


    # ── Test 3: Task routing ───────────────────────────────
    print("\n" + "=" * 50)
    print("TEST 3: Task routing — code task goes to stronger model")
    print("=" * 50)
    messages3 = [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user",   "content": "Write a Python function to reverse a string."}
    ]
    result3 = await call(messages3, task="code")
    print(f"Reply:  {result3.reply[:100]}...")
    print(f"Model:  {result3.model_used}")
    # Should use groq/llama3-70b because task="code"


    # ── Test 4: Long content task ──────────────────────────
    print("\n" + "=" * 50)
    print("TEST 4: Long task goes to Gemini")
    print("=" * 50)
    messages4 = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "Write a short poem about coding."}
    ]
    result4 = await call(messages4, task="creative")
    print(f"Reply:  {result4.reply[:100]}...")
    print(f"Model:  {result4.model_used}")
    # Should prefer gemini because task="creative"

    print("\n All tests done.")


asyncio.run(main())