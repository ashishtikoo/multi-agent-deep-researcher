"""
Base LLM client interface.

All LLM provider implementations (Ollama, LM Studio, HuggingFace, Mock)
inherit from this class, providing a unified generate() interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMClient(ABC):
    """Abstract base class for all LLM provider clients."""

    provider_name: str = "base"

    @abstractmethod
    def generate(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generate a text response from the LLM.

        Args:
            prompt: The input prompt text
            model_name: Optional override for the model to use

        Returns:
            The generated text response
        """
        ...

    @abstractmethod
    def generate_stream(self, prompt: str, model_name: Optional[str] = None):
        """
        Stream text tokens from the LLM.

        Yields:
            Individual text tokens as they are generated
        """
        ...

    def health_check(self) -> bool:
        """
        Check if the LLM provider is reachable and healthy.

        Returns:
            True if the provider is available, False otherwise
        """
        try:
            self.generate("Say 'ok' in one word.")
            return True
        except Exception:
            return False
