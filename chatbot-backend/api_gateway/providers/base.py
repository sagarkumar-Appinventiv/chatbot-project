# providers/base.py
#
# BaseProvider is a contract.
# Every provider MUST have:
#   - call() method
#   - classify_error() method
#
# Gateway only calls these two.
# It doesn't care if it's Groq or Gemini underneath.
# This is the power of abstraction.

from abc import ABC, abstractmethod


class BaseProvider(ABC):

    @abstractmethod
    async def call(
        self,
        messages: list,
        api_key: str,
        model_id: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        pass

    def classify_error(self, error: str) -> str:
        e = error.lower()

        if "429" in error:
            if any(w in e for w in ["daily", "quota", "exceeded"]):
                return "daily_limit"
            return "rate_limit"

        if "401" in error or "invalid_api_key" in e or "authentication" in e:
            return "invalid_key"

        if any(c in error for c in ["500", "502", "503"]):
            return "server_error"

        if "timeout" in e:
            return "timeout"

        if "expired" in e:
            return "daily_limit"

        if "empty" in e:
            return "empty"

        return "server_error"