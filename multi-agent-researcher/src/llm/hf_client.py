"""
HuggingFace Inference API client.

Uses HuggingFace's free tier inference API for cloud-based LLM inference.
Free tier includes access to models like Mistral-7B, Llama-3-8B, etc.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from src.config import LLMConfig
from src.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class HuggingFaceClient(BaseLLMClient):
    """LLM client for HuggingFace Inference API (free tier available)."""

    provider_name = "huggingface"
    API_URL = "https://api-inference.huggingface.co/models"

    def __init__(self, config: LLMConfig) -> None:
        self.token = config.hf_token
        self.default_model = config.hf_analyst_model

        if not self.token:
            raise ValueError(
                "HuggingFace token not set. Set HF_TOKEN in .env file. "
                "Get a free token at https://huggingface.co/settings/tokens"
            )

    def generate(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Generate text via HuggingFace Inference API.

        Args:
            prompt: Input prompt
            model_name: Model to use (defaults to configured model)

        Returns:
            Generated text response
        """
        model = model_name or self.default_model
        url = f"{self.API_URL}/{model}"

        # Format prompt for instruction-tuned models
        formatted_prompt = f"<s>[INST] {prompt} [/INST]"

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 2048,
                "temperature": 0.3,
                "return_full_text": False,
                "do_sample": True,
            },
        }

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Handle different response formats
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", "")
                elif isinstance(data, dict):
                    return data.get("generated_text", "")
                return str(data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                raise RuntimeError(
                    "Model is loading on HuggingFace. Try again in a moment. "
                    "For faster response, consider using Ollama or LM Studio."
                )
            logger.error(f"HuggingFace API error: {e.response.text}")
            raise

    def generate_stream(self, prompt: str, model_name: Optional[str] = None):
        """
        HuggingFace Inference API doesn't support streaming on free tier.
        Falls back to non-streaming generation.
        """
        result = self.generate(prompt, model_name)
        yield result

    def health_check(self) -> bool:
        """Check if HuggingFace API is accessible."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://huggingface.co/api/whoami",
                    headers={"Authorization": f"Bearer {self.token}"},
                )
                return response.status_code == 200
        except Exception:
            return False
