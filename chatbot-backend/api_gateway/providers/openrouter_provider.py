# providers/openrouter_provider.py
#
# Uses LangChain's ChatOpenAI with OpenRouter base URL.
# OpenRouter is a gateway to multiple models (OpenAI, Anthropic, etc).

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .base import BaseProvider


def _convert(messages: list):
    """
    Convert our dict messages to LangChain message objects.

    Our format:   {"role": "user", "content": "hello"}
    LangChain:    HumanMessage(content="hello")
    """
    converted = []
    for msg in messages:
        role    = msg["role"]
        content = msg["content"]
        if role == "system":
            converted.append(SystemMessage(content=content))
        elif role == "user":
            converted.append(HumanMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))
    return converted


class OpenRouterProvider(BaseProvider):

    async def call(
        self,
        messages: list,
        api_key: str,
        model_id: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        # OpenRouter uses OpenAI compatible API
        # Point to OpenRouter's endpoint with the model ID
        llm = ChatOpenAI(
            api_key=api_key,
            model=model_id,
            base_url="https://openrouter.io/api/v1",
            max_tokens=max_tokens,
            temperature=temperature
        )

        lc_messages = _convert(messages)

        # ainvoke = async call
        # LangChain handles the OpenRouter call internally
        response = await llm.ainvoke(lc_messages)

        # response.content = the reply text
        return response.content
