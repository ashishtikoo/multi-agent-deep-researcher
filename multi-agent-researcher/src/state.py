"""
LangGraph State Schema for the Multi-Agent Deep Researcher.

Defines the shared state that flows between all agents:
Retriever → Analyst → Critic → Report Builder
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from langgraph.graph.message import add_messages
from typing_extensions import Annotated


# ---------------------------------------------------------------------------
# Data models for structured state
# ---------------------------------------------------------------------------

@dataclass
class Source:
    """A retrieved source (web article, paper, report, etc.)."""
    title: str
    url: str
    snippet: str
    content: str = ""
    retriever_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Claim:
    """A factual claim extracted from a source."""
    text: str
    source_url: str
    source_title: str
    confidence: float = 1.0
    claim_id: str = ""


@dataclass
class Contradiction:
    """A detected contradiction between two claims from different sources."""
    claim_a: Claim
    claim_b: Claim
    conflict_description: str
    confidence: float = 0.0  # 0-1 confidence that these genuinely conflict


@dataclass
class ReportSection:
    """A section within the final report."""
    title: str
    content: str
    citations: list[str] = field(default_factory=list)  # URLs or IDs


# ---------------------------------------------------------------------------
# Main research state
# ---------------------------------------------------------------------------

@dataclass
class ResearchState:
    """
    The central state object shared across all agents in the LangGraph workflow.

    This state flows through:
        Retriever → Analyst → Critic → Report Builder
    """
    # Input
    query: str = ""
    domain: str = ""

    # Agent outputs (populated as pipeline progresses)
    sources: list[Source] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    report_sections: list[ReportSection] = field(default_factory=list)

    # LLM messages for chain-of-thought / reasoning
    messages: Annotated[list, add_messages] = field(default_factory=list)

    # Pipeline metadata
    status: str = "pending"  # pending, retrieving, analyzing, critiquing, reporting, done
    current_agent: str = ""
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Output
    final_report: str = ""

    # Flags for conditional edges
    has_sources: bool = False
    has_claims: bool = False
    has_contradictions: bool = False

    def add_source(self, source: Source) -> None:
        """Add a source to the state."""
        self.sources.append(source)

    def add_claim(self, claim: Claim) -> None:
        """Add a claim to the state."""
        self.claims.append(claim)

    def add_contradiction(self, contradiction: Contradiction) -> None:
        """Add a contradiction to the state."""
        self.contradictions.append(contradiction)

    def add_error(self, error: str) -> None:
        """Record an error in the pipeline."""
        self.errors.append(error)

    def to_dict(self) -> dict[str, Any]:
        """Serialize state to dictionary (for API responses, logging)."""
        return {
            "query": self.query,
            "domain": self.domain,
            "status": self.status,
            "current_agent": self.current_agent,
            "sources_count": len(self.sources),
            "claims_count": len(self.claims),
            "contradictions_count": len(self.contradictions),
            "sources": [
                {"title": s.title, "url": s.url, "snippet": s.snippet}
                for s in self.sources
            ],
            "claims": [
                {
                    "text": c.text,
                    "source_url": c.source_url,
                    "confidence": c.confidence,
                }
                for c in self.claims
            ],
            "contradictions": [
                {
                    "claim_a": c.claim_a.text,
                    "claim_b": c.claim_b.text,
                    "conflict": c.conflict_description,
                    "confidence": c.confidence,
                }
                for c in self.contradictions
            ],
            "errors": self.errors,
            "final_report": self.final_report,
        }
