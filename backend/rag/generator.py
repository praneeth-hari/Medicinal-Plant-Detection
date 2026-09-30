"""
Response Generator
==================

Uses a local Ollama server to generate natural-language answers
grounded in the context retrieved by the ``DocumentRetriever``.

Default model: ``qwen2.5:3b``.
"""
from __future__ import annotations

import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """\
You are an expert medicinal plant assistant. Your role is to provide accurate, \
helpful information about medicinal plants, their properties, uses, preparation \
methods, and safety precautions.

Rules:
1. Answer the question using ONLY the facts directly stated in the provided context documents. Do NOT use external knowledge, speculate, or extrapolate.
2. If the context contains ANY relevant information, answer with what it states, even if only part of the question is covered, and say which part is not covered. Read the context carefully: a statement such as "must be avoided during pregnancy" directly answers a question about pregnancy safety.
3. Only when the context contains nothing relevant to the question (or the question is not about medicinal plants), state exactly: "Based on the available plant monographs, I cannot find sufficient information to answer your question." Do not answer from your own knowledge, and do not make up any facts.
4. For every claim you make, you MUST cite the source index at the end of the sentence or clause before the period, e.g. "Ashwagandha reduces cortisol levels [Source 3]." If multiple sources support a claim, list them together, e.g. "[Source 1, Source 2]".
5. Always explicitly state and highlight any relevant safety precautions, warnings, or contraindications listed for the plant being discussed.
6. Text under "Common Misconceptions" describes beliefs that are WRONG. Never present a misconception as a fact, benefit, or precaution.
7. Do not repeat yourself. Keep your response concise, professional, and well-structured. Do NOT put your internal thoughts, explanations, or reasoning in the output. Only provide the final answer."""


class ResponseGenerator:
    """Generate answers from a prompt + context using a local Ollama server.

    Args:
        model_name: Ollama model tag (e.g. ``qwen2.5:3b``).
        base_url: Ollama server URL.
        timeout: Seconds to wait for a completion (local CPU inference can be slow).
    """

    def __init__(
        self,
        model_name: str = "qwen2.5:3b",
        base_url: str = "http://localhost:11434",
        timeout: float = 180.0,
    ) -> None:
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

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
        temperature: Optional[float] = None,
        chat_history: Optional[list[dict[str, str]]] = None,
    ) -> str:
        messages = self.format_prompt(query, context, chat_history=chat_history)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": 0.3 if temperature is None else temperature,
                            "num_predict": max_tokens,
                        },
                    },
                )
                resp.raise_for_status()
            answer = (resp.json().get("message") or {}).get("content") or ""
            if not answer.strip():
                logger.warning("Ollama returned empty content")
                return "I was unable to generate a response. Please try again."
            logger.info("Generated response: model=%s", self.model_name)
            return answer.strip()

        except Exception as e:
            logger.exception("Error during Ollama generation: %s", e)
            return (
                "An error occurred while generating a response. Please ensure "
                f"Ollama is running and the model '{self.model_name}' is installed "
                f"(ollama pull {self.model_name})."
            )

    def is_available(self) -> bool:
        """Check whether the Ollama server is reachable."""
        try:
            return httpx.get(f"{self.base_url}/api/tags", timeout=2.0).status_code == 200
        except Exception:
            return False
