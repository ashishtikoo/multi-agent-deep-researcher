"""
Mock LLM client.

Returns canned responses for testing and demo purposes.
Used when no real LLM is available.
"""

from __future__ import annotations

import logging
from typing import Optional

from src.config import LLMConfig
from src.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)

# Canned responses for different agent types
_CANNED_RESPONSES = {
    "analyst": """Source Summary:
This article discusses recent advances in AI research. Key points include:
1. Large language models continue to improve in reasoning capabilities
2. Multi-modal models are becoming more prevalent
3. Concerns about AI safety and alignment remain unresolved

Extracted Claims:
- Claim 1: LLM reasoning capabilities have improved significantly in 2024 (confidence: 0.9)
- Claim 2: Multi-modal AI models are now more common than text-only models (confidence: 0.7)
- Claim 3: AI safety research has received decreased funding compared to model development (confidence: 0.8)""",

    "critic": """Contradiction Analysis:

Contradiction #1:
- Source A claims: "Multi-modal AI models are now more common than text-only models"
- Source B claims: "Text-only models still dominate production deployments, accounting for 80% of use cases"
- Conflict: Prevalence of multi-modal vs text-only models
- Confidence: 0.85

Contradiction #2:
- Source A claims: "AI safety research has received decreased funding"
- Source C claims: "Government funding for AI safety increased by 40% in 2024"
- Conflict: Direction of AI safety funding trends
- Confidence: 0.72""",

    "report": """# Research Report

## Executive Summary
This report synthesizes findings from multiple sources on the research topic.

## Key Findings
1. **Finding 1**: [Detailed summary with citations]
2. **Finding 2**: [Detailed summary with citations]

## Contradictions Detected
| # | Claim A | Claim B | Confidence |
|---|---------|---------|------------|
| 1 | [Source A statement] | [Source B statement] | 0.85 |

## Sources
1. [Source 1](url)
2. [Source 2](url)

## Conclusion
[Summary of insights and recommendations]""",
}


class MockClient(BaseLLMClient):
    """Mock LLM client that returns canned responses."""

    provider_name = "mock"

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def generate(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Return a canned response based on the prompt content.

        Args:
            prompt: Input prompt (used to determine response type)
            model_name: Ignored in mock mode

        Returns:
            Canned response text
        """
        prompt_lower = prompt.lower()

        if "summarize" in prompt_lower or "claim" in prompt_lower or "extract" in prompt_lower:
            return _CANNED_RESPONSES["analyst"]
        elif "contradict" in prompt_lower or "conflict" in prompt_lower or "compare" in prompt_lower:
            return _CANNED_RESPONSES["critic"]
        elif "report" in prompt_lower or "compile" in prompt_lower:
            return _CANNED_RESPONSES["report"]

        # Default canned response
        return "This is a mock response. Configure a real LLM provider for actual results."

    def generate_stream(self, prompt: str, model_name: Optional[str] = None):
        """Stream a canned response token by token."""
        response = self.generate(prompt, model_name)
        for token in response.split():
            yield token + " "

    def health_check(self) -> bool:
        """Mock client is always healthy."""
        return True

    def list_models(self) -> list[str]:
        """List mock models."""
        return ["mock-model"]
