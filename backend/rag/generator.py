"""
Response Generator
==================

Uses the Groq cloud API to generate natural-language answers
grounded in the context retrieved by the ``DocumentRetriever``.

Default model: ``llama-3.1-8b-instant``.
"""
from __future__ import annotations

import logging
from typing import Optional

from groq import AsyncGroq

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """\
You are an expert medicinal plant assistant. Your role is to provide accurate, \
helpful information about medicinal plants, their properties, uses, preparation \
methods, and safety precautions.

Rules:
1. Answer the question using ONLY the facts directly stated in the provided context documents. Do NOT use external knowledge, speculate, or extrapolate.
2. If the context does not contain the answer or is insufficient, state exactly: "Based on the available plant monographs, I cannot find sufficient information to answer your question." Do not make up any facts.
3. For every claim you make, you MUST cite the source index at the end of the sentence or clause before the period, e.g. "Ashwagandha reduces cortisol levels [Source 3]." If multiple sources support a claim, list them together, e.g. "[Source 1, Source 2]".
4. Always explicitly state and highlight any relevant safety precautions, warnings, or contraindications listed for the plant being discussed.
5. Keep your response concise, professional, and well-structured. Do NOT put your internal thoughts, explanations, or reasoning in the output. Only provide the final answer."""


class ResponseGenerator:
    """Generate answers from a prompt + context using the Groq cloud API.

    Args:
        model_name: Groq model identifier.
        api_key: Groq API key.
    """

    def __init__(
        self,
        model_name: str = "llama-3.1-8b-instant",
        api_key: str = "",
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key

    def format_prompt(
        self,
        query: str,
        context: str,
        *,
        system_message: Optional[str] = None,
        chat_history: Optional[list[dict[str, str]]] = None,
    ) -> list[dict[str, str]]:
        system = system_message or _SYSTEM_PROMPT
        messages: list[dict[str, str]] = [{"role": "system", "content": system}]

        context_msg = (
            "The following are relevant documents from the medicinal plant "
            "knowledge base. Use them to answer the user's question:\n\n"
            f"{context}"
        )
        messages.append({"role": "system", "content": context_msg})

        if chat_history:
            for turn in chat_history[-6:]:
                messages.append({
                    "role": turn.get("role", "user"),
                    "content": turn.get("content", ""),
                })

        messages.append({"role": "user", "content": query})
        return messages

    async def generate(
        self,
        query: str,
        context: str,
        *,
        max_tokens: int = 512,
        chat_history: Optional[list[dict[str, str]]] = None,
    ) -> str:
        messages = self.format_prompt(query, context, chat_history=chat_history)

        try:
            client = AsyncGroq(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            answer = response.choices[0].message.content or ""
            if not answer:
                logger.warning("Groq returned empty content")
                return "I was unable to generate a response. Please try again."
            logger.info("Generated response: model=%s", self.model_name)
            return answer.strip()

        except Exception as e:
            logger.exception("Error during Groq generation: %s", e)
            return (
                "An error occurred while generating a response. "
                "Please check your GROQ_API_KEY and try again."
            )

    def is_available(self) -> bool:
        """Check if the Groq API key is configured."""
        return bool(self.api_key)
