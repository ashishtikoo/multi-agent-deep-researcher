"""
Configuration management for the Multi-Agent Deep Researcher.

Loads settings from .env file with sensible defaults.
Supports all free AI model providers (Ollama, LM Studio, HuggingFace).
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)


@dataclass
class LLMConfig:
    """Configuration for AI model providers."""
    provider: Literal["ollama", "lmstudio", "huggingface", "mock"] = "ollama"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    analyst_model: str = "mistral"
    critic_model: str = "mistral"
    report_model: str = "llama3.2"
    embedding_model: str = "nomic-embed-text"

    # LM Studio
    lmstudio_base_url: str = "http://localhost:1234/v1"
    lmstudio_analyst_model: str = "microsoft/Phi-3-mini-4k-instruct"
    lmstudio_critic_model: str = "microsoft/Phi-3-mini-4k-instruct"
    lmstudio_report_model: str = "microsoft/Phi-3-mini-4k-instruct"

    # HuggingFace
    hf_token: str = ""
    hf_analyst_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    hf_critic_model: str = "mistralai/Mistral-7B-Instruct-v0.3"
    hf_report_model: str = "meta-llama/Llama-3-8B-Instruct"

    @property
    def current_model(self) -> str:
        """Return the model name for the current provider."""
        if self.provider == "ollama":
            return self.analyst_model
        elif self.provider == "lmstudio":
            return self.lmstudio_analyst_model
        elif self.provider == "huggingface":
            return self.hf_analyst_model
        return "mock-model"


@dataclass
class RetrieverConfig:
    """Configuration for source retrieval."""
    provider: Literal["duckduckgo", "searxng"] = "duckduckgo"
    max_results: int = 5
    searxng_url: str = "http://localhost:8080"


@dataclass
class ResearchConfig:
    """Configuration for research parameters."""
    max_sources_per_query: int = 5
    max_claims_per_source: int = 10
    contradiction_confidence_threshold: float = 0.6
    research_timeout_seconds: int = 300


@dataclass
class APIConfig:
    """Configuration for API and UI."""
    host: str = "0.0.0.0"
    port: int = 8000
    streamlit_port: int = 8501


@dataclass
class AppConfig:
    """Top-level application configuration."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)
    api: APIConfig = field(default_factory=APIConfig)
    log_level: str = "INFO"


def load_config() -> AppConfig:
    """
    Load configuration from environment variables.

    Returns a fully populated AppConfig instance.
    """
    return AppConfig(
        llm=LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "ollama"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            analyst_model=os.getenv("OLLAMA_ANALYST_MODEL", "mistral"),
            critic_model=os.getenv("OLLAMA_CRITIC_MODEL", "mistral"),
            report_model=os.getenv("OLLAMA_REPORT_MODEL", "llama3.2"),
            embedding_model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
            lmstudio_base_url=os.getenv("LMSTUDIO_BASE_URL", "http://localhost:1234/v1"),
            lmstudio_analyst_model=os.getenv("LMSTUDIO_ANALYST_MODEL", "microsoft/Phi-3-mini-4k-instruct"),
            lmstudio_critic_model=os.getenv("LMSTUDIO_CRITIC_MODEL", "microsoft/Phi-3-mini-4k-instruct"),
            lmstudio_report_model=os.getenv("LMSTUDIO_REPORT_MODEL", "microsoft/Phi-3-mini-4k-instruct"),
            hf_token=os.getenv("HF_TOKEN", ""),
            hf_analyst_model=os.getenv("HF_ANALYST_MODEL", "mistralai/Mistral-7B-Instruct-v0.3"),
            hf_critic_model=os.getenv("HF_CRITIC_MODEL", "mistralai/Mistral-7B-Instruct-v0.3"),
            hf_report_model=os.getenv("HF_REPORT_MODEL", "meta-llama/Llama-3-8B-Instruct"),
        ),
        retriever=RetrieverConfig(
            provider=os.getenv("RETRIEVER_PROVIDER", "duckduckgo"),
            max_results=int(os.getenv("MAX_SOURCES_PER_QUERY", "5")),
            searxng_url=os.getenv("SEARXNG_URL", "http://localhost:8080"),
        ),
        research=ResearchConfig(
            max_sources_per_query=int(os.getenv("MAX_SOURCES_PER_QUERY", "5")),
            max_claims_per_source=int(os.getenv("MAX_CLAIMS_PER_SOURCE", "10")),
            contradiction_confidence_threshold=float(
                os.getenv("CONTRADICTION_CONFIDENCE_THRESHOLD", "0.6")
            ),
            research_timeout_seconds=int(os.getenv("RESEARCH_TIMEOUT_SECONDS", "300")),
        ),
        api=APIConfig(
            host=os.getenv("API_HOST", "0.0.0.0"),
            port=int(os.getenv("API_PORT", "8000")),
            streamlit_port=int(os.getenv("STREAMLIT_PORT", "8501")),
        ),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


# Global config singleton
config = load_config()


def get_config() -> AppConfig:
    """Get the global configuration singleton."""
    return config
