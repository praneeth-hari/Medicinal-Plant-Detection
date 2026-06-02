"""
Response Generator
==================

Uses a language model (local or API-based) to generate natural-language
answers grounded in the context retrieved by the ``DocumentRetriever``.
"""

from __future__ import annotations

from typing import Any, Optional


class ResponseGenerator:
    """Generate answers from a prompt + context using an LLM.

    Args:
        model_name: Identifier or path for the language model.
    """

    def __init__(self, model_name: str = "default") -> None:
        """Initialise the generator.

        Args:
            model_name: Model identifier.  Could be a HuggingFace model
                        name, an OpenAI model slug, or a local path.
        """
        self.model_name = model_name
        # TODO: Load or connect to the LLM here.

    def generate(
        self,
        query: str,
        context: str,
        *,
        max_tokens: int = 512,
    ) -> str:
        """Generate an answer to a query using retrieved context.

        Args:
            query: The user's original question.
            context: Formatted context string from the retriever.
            max_tokens: Maximum number of tokens in the generated response.

        Returns:
            The generated answer string.
        """
        raise NotImplementedError("Not yet implemented")

    def format_prompt(
        self,
        query: str,
        context: str,
        *,
        system_message: Optional[str] = None,
    ) -> str:
        """Construct the full prompt to send to the language model.

        Args:
            query: User question.
            context: Retrieved context.
            system_message: Optional system-level instruction.

        Returns:
            Formatted prompt string.
        """
        raise NotImplementedError("Not yet implemented")
