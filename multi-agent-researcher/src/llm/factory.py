"""
LLM client factory.

Creates the appropriate LLM client based on the configured provider.
"""

from __future__ import annotations

from src.config import LLMConfig


def create_llm_client(llm_config: LLMConfig):
    """
    Factory function to create the appropriate LLM client.

    Args:
        llm_config: The LLM configuration

    Returns:
        An instance of the appropriate LLM client
    """
    provider = llm_config.provider.lower()

    if provider == "ollama":
        from src.llm.ollama_client import OllamaClient
        return OllamaClient(llm_config)
    elif provider == "lmstudio":
        from src.llm.lmstudio_client import LMStudioClient
        return LMStudioClient(llm_config)
    elif provider == "huggingface":
        from src.llm.hf_client import HuggingFaceClient
        return HuggingFaceClient(llm_config)
    elif provider == "mock":
        from src.llm.mock_client import MockClient
        return MockClient(llm_config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Choose from: ollama, lmstudio, huggingface, mock")
