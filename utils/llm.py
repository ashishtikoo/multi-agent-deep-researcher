"""
LLM factory and utilities for the research agent system.
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from config import settings


def create_llm(
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int = 4096,
) -> ChatOpenAI | ChatAnthropic:
    """Create an LLM instance based on configuration."""
    model = model or settings.default_llm_model
    temp = temperature if temperature is not None else settings.temperature

    if model.startswith("claude"):
        return ChatAnthropic(
            model_name=model,
            temperature=temp,
            max_tokens=max_tokens,
            api_key=settings.anthropic_api_key,
        )
    return ChatOpenAI(
        model=model,
        temperature=temp,
        max_tokens=max_tokens,
        api_key=settings.openai_api_key,
    )


def get_llm(model: str | None = None) -> ChatOpenAI | ChatAnthropic:
    """Get the default LLM."""
    return create_llm(model)
