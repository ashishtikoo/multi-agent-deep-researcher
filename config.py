"""
Project configuration for Multi-Agent AI Deep Researcher.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM Configuration — OpenRouter (primary) or OpenAI (fallback)
    openrouter_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    default_llm_model: str = "openai/gpt-4o"
    fast_llm_model: str = "openai/gpt-4o-mini"

    # Web Search
    tavily_api_key: str = ""

    # Agent Configuration
    max_hops: int = 5
    max_sources_per_query: int = 10
    max_insights_per_topic: int = 5
    temperature: float = 0.3

    # Report
    report_max_pages: int = 20
    report_format: str = "markdown"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
