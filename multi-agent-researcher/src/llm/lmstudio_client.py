"""
LM Studio LLM client.

Connects to LM Studio's local OpenAI-compatible API server.
LM Studio provides a free local LLM server with OpenAI API compatibility.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from src.config import LLMConfig
from src.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class LMStudioClient(BaseLLMClient):
    """LLM client for LM Studio (local, free inference via OpenAI-compatible API)."""

    provider_name = "lmstudio"

    def __init__(self, config: LLMConfig) -> None:
        self.base_url = config.lmstudio_base_url.rstrip("/")
        self.default_model = config.lmstudio_analyst_model

    def generate(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generate text via LM Studio's OpenAI-compatible API.

        Args:
            prompt: Input prompt
            model_name: Model to use (defaults to configured model)

        Returns:
            Generated text response
        """
        model = model_name or self.default_model
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
            "stream": False,
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to LM Studio at {self.base_url}. "
                "Make sure LM Studio is running with a loaded model."
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"LM Studio API error: {e.response.text}")
            raise

    def generate_stream(self, prompt: str, model_name: Optional[str] = None):
        """
        Stream text tokens from LM Studio.

        Yields:
            Text tokens as they are generated
        """
        model = model_name or self.default_model
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
            "stream": True,
        }

        try:
            import json as _json
            with httpx.Client(timeout=120.0) as client:
                with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if line and line.startswith(b"data: "):
                            data_str = line[6:].decode()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = _json.loads(data_str)
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                            except Exception:
                                continue
        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to LM Studio at {self.base_url}. "
                "Make sure LM Studio is running with a loaded model."
            )

    def health_check(self) -> bool:
        """Check if LM Studio server is running."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/models")
                response.raise_for_status()
                return True
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """List available models in LM Studio."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/models")
                response.raise_for_status()
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            return []
