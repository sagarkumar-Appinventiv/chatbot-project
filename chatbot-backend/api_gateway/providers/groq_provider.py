# providers/groq_provider.py
#
# Uses LangChain's ChatGroq.
# LangChain handles all Groq SDK details.
# We just call .ainvoke(messages)

from langchain_groq import ChatGroq
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


class GroqProvider(BaseProvider):

    async def call(
        self,
        messages: list,
        api_key: str,
        model_id: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        # LangChain creates Groq client internally
        llm = ChatGroq(
            api_key=api_key,
            model=model_id,
            max_tokens=max_tokens,
            temperature=temperature
        )

        lc_messages = _convert(messages)

        # ainvoke = async call
        # LangChain handles the Groq SDK call internally
        response = await llm.ainvoke(lc_messages)

        # response.content = the reply text
        return response.content