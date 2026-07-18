"""
Critical Analysis Agent – Summarizes findings, highlights contradictions,
and validates sources.
"""

import json
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import create_llm
from config import settings
from models import Source, Finding, Contradiction


class AnalysisAgent:
    """
    The Critical Analysis Agent evaluates and synthesizes retrieved information.
    It identifies key findings, detects contradictions between sources,
    and assesses source credibility.
    """

    FINDINGS_SYSTEM_PROMPT = """You are a critical research analyst. Your job is to analyze
sources and extract structured findings from them.

For each finding, provide:
1. A clear, concise claim (the finding)
2. Which sources support it
3. A confidence score (0.0 to 1.0) based on source quality and agreement
4. Any contradictions with other sources

Analyze the following sources and extract the most important findings:

Sources:
{sources}

Research Query: {research_query}

Return a JSON object with this structure:
{{
    "findings": [
        {{
            "claim": "The finding/claim",
            "supporting_sources": ["source titles or URLs"],
            "confidence": 0.85,
            "contradictions": ["description of any contradictory claims"]
        }}
    ]
}}

Extract at least 3-5 key findings. Be thorough but concise.
"""

    CONTRADICTION_SYSTEM_PROMPT = """You are a critical analyst comparing conflicting information.
Identify and analyze contradictions between the following findings.

Findings:
{findings}

For each contradiction, provide:
- The conflicting claims
- Their respective sources
- A suggested resolution or explanation

Return as JSON:
{{
    "contradictions": [
        {{
            "claim_a": "First claim",
            "source_a": "Source of first claim",
            "claim_b": "Conflicting claim",
            "source_b": "Source of conflicting claim",
            "resolution": "Suggested resolution or explanation"
        }}
    ]
}}
"""

    VALIDATION_SYSTEM_PROMPT = """You are a source validation expert. Assess the credibility
of the following research sources.

Sources:
{sources}

For each source, rate:
- credibility: 0.0 to 1.0
- recency: 0.0 to 1.0
- relevance: 0.0 to 1.0

Return as JSON array with source index and scores.
"""

    def __init__(self, llm_model: Optional[str] = None):
        self.llm = create_llm(llm_model)

    def extract_findings(self, sources: list[Source], research_query: str) -> list[Finding]:
        """Extract structured findings from retrieved sources."""
        sources_text = "\n".join(
            f"[{i+1}] {s.title} ({s.source_type.value})\n"
            f"    URL: {s.url}\n"
            f"    Snippet: {s.snippet[:500]}\n"
            for i, s in enumerate(sources)
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.FINDINGS_SYSTEM_PROMPT),
            ("human", f"Sources:\n{sources_text}\n\nResearch Query: {research_query}"),
        ])
        chain = prompt | self.llm
        response = chain.invoke({
            "sources": sources_text,
            "research_query": research_query,
        })
        content = response.content.strip()

        # Parse JSON
        try:
            if "```" in content:
                content = content.split("```")[1].strip()
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            result = json.loads(content)
            findings_data = result.get("findings", [])
        except json.JSONDecodeError:
            # Fallback: create basic findings from sources
            findings_data = [
                {
                    "claim": s.snippet[:300],
                    "supporting_sources": [s.title],
                    "confidence": 0.5,
                    "contradictions": [],
                }
                for s in sources[:5]
            ]

        findings = []
        for fd in findings_data:
            findings.append(Finding(
                claim=fd.get("claim", ""),
                supporting_sources=fd.get("supporting_sources", []),
                confidence=fd.get("confidence", 0.5),
                contradictions=fd.get("contradictions", []),
            ))

        return findings

    def identify_contradictions(
        self,
        findings: list[Finding],
        sources: list[Source],
    ) -> list[Contradiction]:
        """Identify contradictions between findings."""
        findings_text = "\n".join(
            f"Finding {i+1}: {f.claim}\n"
            f"  Sources: {', '.join(f.supporting_sources)}\n"
            f"  Confidence: {f.confidence:.0%}\n"
            for i, f in enumerate(findings)
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.CONTRADICTION_SYSTEM_PROMPT),
            ("human", f"Findings:\n{findings_text}"),
        ])
        chain = prompt | self.llm
        response = chain.invoke({"findings": findings_text})
        content = response.content.strip()

        try:
            if "```" in content:
                content = content.split("```")[1].strip()
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            result = json.loads(content)
            contradiction_data = result.get("contradictions", [])
        except json.JSONDecodeError:
            contradiction_data = []

        contradictions = []
        for cd in contradiction_data:
            contradictions.append(Contradiction(
                claim_a=cd.get("claim_a", ""),
                source_a=cd.get("source_a", ""),
                claim_b=cd.get("claim_b", ""),
                source_b=cd.get("source_b", ""),
                resolution=cd.get("resolution"),
            ))

        return contradictions

    def validate_sources(self, sources: list[Source]) -> dict:
        """Validate and score source credibility."""
        sources_text = "\n".join(
            f"[{i+1}] {s.title} ({s.source_type.value})\n"
            f"    URL: {s.url}\n"
            f"    Snippet: {s.snippet[:300]}\n"
            for i, s in enumerate(sources)
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.VALIDATION_SYSTEM_PROMPT),
            ("human", f"Sources:\n{sources_text}"),
        ])
        chain = prompt | self.llm
        response = chain.invoke({"sources": sources_text})
        return json.loads(response.content) if response.content else {}

    def analyze(self, sources: list[Source], research_query: str) -> dict:
        """Full analysis pipeline: extract findings, identify contradictions."""
        findings = self.extract_findings(sources, research_query)
        contradictions = self.identify_contradictions(findings, sources)

        return {
            "query": research_query,
            "findings": findings,
            "contradictions": contradictions,
            "total_sources": len(sources),
        }
