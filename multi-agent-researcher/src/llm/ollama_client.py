"""
Ollama LLM client.

Connects to a local Ollama instance for free, local LLM inference.
Supports all Ollama models (Mistral, Llama, Phi, etc.).
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from src.config import LLMConfig
from src.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class OllamaClient(BaseLLMClient):
    """LLM client for Ollama (local, free inference)."""

    provider_name = "ollama"

    def __init__(self, config: LLMConfig) -> None:
        self.base_url = config.ollama_base_url.rstrip("/")
        self.default_model = config.analyst_model

    def generate(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generate text via Ollama API.

        Args:
            prompt: Input prompt
            model_name: Model to use (defaults to configured analyst model)

        Returns:
            Generated text response
        """
        model = model_name or self.default_model
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 2048,
            },
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: `ollama serve`"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.text}")
            raise

    def generate_stream(self, prompt: str, model_name: Optional[str] = None):
        """
        Stream text tokens from Ollama.

        Yields:
            Text tokens as they are generated
        """
        model = model_name or self.default_model
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.3,
                "num_predict": 2048,
            },
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: `ollama serve`"
            )

    def health_check(self) -> bool:
        """Check if Ollama is running."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                return True
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """List available Ollama models."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []
