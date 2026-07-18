"""
LLM factory and utilities for the research agent system.
Supports OpenRouter (primary) and OpenAI/Anthropic (fallback).
"""

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from config import settings


def create_llm(
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int = 4096,
) -> ChatOpenAI | ChatAnthropic:
    """Create an LLM instance based on configuration.

    Priority:
    1. OpenRouter (if OPENROUTER_API_KEY is set)
    2. OpenAI (if OPENAI_API_KEY is set)
    3. Anthropic (if ANTHROPIC_API_KEY is set and model is Claude)
    """
    model = model or settings.default_llm_model
    temp = temperature if temperature is not None else settings.temperature

    # Check which API key is available
    api_key = None
    base_url = None

    if settings.openrouter_api_key and settings.openrouter_api_key != "sk-or-v1-your-key-here":
        # OpenRouter: uses OpenAI-compatible API
        api_key = settings.openrouter_api_key
        base_url = "https://openrouter.ai/api/v1"
    elif settings.openai_api_key and settings.openai_api_key != "sk-proj-your-openai-key-here":
        # Direct OpenAI
        api_key = settings.openai_api_key
    elif settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-key-here":
        # Anthropic
        return ChatAnthropic(
            model_name=model.replace("anthropic/", "").replace("claude-", "claude-"),
            temperature=temp,
            max_tokens=max_tokens,
            api_key=settings.anthropic_api_key,
        )
    else:
        raise ValueError(
            "No API key configured. Please set OPENROUTER_API_KEY or OPENAI_API_KEY in your .env file.\n"
            "Get an OpenRouter key: https://openrouter.ai/keys\n"
            "Or get an OpenAI key: https://platform.openai.com/api-keys"
        )

    return ChatOpenAI(
        model=model,
        temperature=temp,
        max_tokens=max_tokens,
        api_key=api_key,
        base_url=base_url,
        default_headers={
            "HTTP-Referer": "https://github.com/ashishtikoo/multi-agent-deep-researcher",
            "X-Title": "Multi-Agent Deep Researcher",
        },
    )


def get_llm(model: str | None = None) -> ChatOpenAI | ChatAnthropic:
    """Get the default LLM."""
    return create_llm(model)
