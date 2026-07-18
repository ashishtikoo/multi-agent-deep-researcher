"""
Base agent class for the Multi-Agent Deep Researcher.

All specialized agents (Retriever, Analyst, Critic, Report Builder)
inherit from this class, providing:
- Standardized interface for execution
- LLM integration via pluggable providers
- Progress tracking and status reporting
- Error handling
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from src.config import get_config
from src.state import ResearchState

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all research agents.

    Each agent implements:
    - `name`: Unique identifier for the agent
    - `execute()`: Core logic for what this agent does
    - `prompt()`: LLM prompt template for this agent's task
    """

    name: str = "base"

    def __init__(self, config=None) -> None:
        self.config = config or get_config()
        self._execution_time: float = 0.0
        self._status: str = "idle"
        self._progress: float = 0.0

    @property
    def status(self) -> str:
        """Current agent status (idle, running, done, error)."""
        return self._status

    @property
    def progress(self) -> float:
        """Progress indicator 0.0 - 1.0."""
        return self._progress

    @property
    def execution_time(self) -> float:
        """Total execution time in seconds."""
        return self._execution_time

    def set_status(self, status: str, progress: float = 0.0) -> None:
        """Update agent status and progress."""
        self._status = status
        self._progress = progress
        logger.debug(f"[{self.name}] status={status}, progress={progress:.2f}")

    @abstractmethod
    async def execute(self, state: ResearchState) -> ResearchState:
        """
        Execute the agent's core logic on the given research state.

        Args:
            state: The current research state to process

        Returns:
            The updated research state with agent outputs
        """
        ...

    def get_prompt(self, **kwargs) -> str:
        """
        Generate the LLM prompt for this agent.

        Subclasses override this to provide agent-specific prompts.
        """
        return ""

    def _call_llm(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Call the configured LLM provider with a prompt.

        This is a placeholder — actual implementation goes in src/llm/.
        For Phase 1 (mock mode), returns canned responses.
        """
        start = time.time()
        try:
            from src.llm import create_llm_client
            client = create_llm_client(self.config.llm)
            result = client.generate(prompt, model_name=model_name)
            self._execution_time = time.time() - start
            return result
        except Exception as e:
            logger.error(f"[{self.name}] LLM call failed: {e}")
            self._execution_time = time.time() - start
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}' status='{self._status}'>"
