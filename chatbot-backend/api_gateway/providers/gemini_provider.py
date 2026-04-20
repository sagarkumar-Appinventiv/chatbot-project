# providers/gemini_provider.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .base import BaseProvider
import os

def _convert(messages: list):
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


class GeminiProvider(BaseProvider):

    async def call(
        self,
        messages: list,
        api_key: str,
        model_id: str,
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> str:
        # Set env var — langchain-google-genai reads from here
        os.environ["GOOGLE_API_KEY"] = api_key

        llm = ChatGoogleGenerativeAI(
            model=model_id,                   # no google_api_key param
            max_output_tokens=max_tokens,
            temperature=temperature
        )

        lc_messages = _convert(messages)
        response    = await llm.ainvoke(lc_messages)
        return response.content