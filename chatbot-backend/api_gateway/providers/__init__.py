# providers/__init__.py
#
# Registry of all providers.
# To add OpenAI later:
#   from .openai_provider import OpenAIProvider
#   "openai": OpenAIProvider()

from .groq_provider import GroqProvider
from .gemini_provider import GeminiProvider

_REGISTRY = {
    "groq":   GroqProvider(),
    "gemini": GeminiProvider(),
}


def get_provider(name: str):
    provider = _REGISTRY.get(name)
    if not provider:
        raise Exception(
            f"Provider '{name}' not found. "
            f"Available: {list(_REGISTRY.keys())}"
        )
    return provider