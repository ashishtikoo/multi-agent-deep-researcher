"""
Insight Generation Agent – Suggests hypotheses or trends using reasoning chains.
"""

import json
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import create_llm
from config import settings
from models import Finding, Insight, Contradiction, Source


class InsightAgent:
    """
    The Insight Generation Agent analyzes findings and contradictions
    to generate novel insights, hypotheses, and trend analyses
    using structured reasoning chains.
    """

    INSIGHT_SYSTEM_PROMPT = """You are an expert research analyst and strategic thinker.
Your job is to generate deep, actionable insights from research findings.

Given the research findings, contradictions, and sources, generate insights by:
1. Identifying patterns and trends across findings
2. Drawing connections between seemingly unrelated findings
3. Proposing testable hypotheses
4. Identifying emerging themes or shifts
5. Suggesting implications and future directions

Each insight must include a clear reasoning chain showing how you arrived at it.

Return your response as a JSON object with the following structure:
{
    "insights": [
        {
            "insight": "The insight statement",
            "reasoning_chain": ["Step 1", "Step 2", "Step 3", "Conclusion"],
            "supporting_findings": ["finding descriptions"],
            "confidence": 0.8,
            "category": "trend|hypothesis|implication|pattern|emerging_theme"
        }
    ]
}

Generate 3-5 high-quality insights. Prioritize depth over quantity.
"""

    HYPOTHESIS_SYSTEM_PROMPT = """You are a hypothesis generation expert.
Based on the research findings, propose testable hypotheses that explain
the observed patterns or contradictions.

For each hypothesis, provide:
- A clear hypothesis statement
- The evidence supporting it
- Suggested tests or experiments to validate it
- Confidence level

Return your response as a JSON object:
{
    "hypotheses": [
        {
            "hypothesis": "Statement",
            "evidence": ["Evidence point 1", "Evidence point 2"],
            "tests": ["Test 1", "Test 2"],
            "confidence": 0.7
        }
    ]
}
"""

    TREND_SYSTEM_PROMPT = """You are a trend analyst. Identify emerging trends
and shifts based on the research findings.

Return your response as a JSON object:
{
    "trends": [
        {
            "trend": "Trend description",
            "evidence": ["Supporting evidence"],
            "direction": "increasing|decreasing|emerging|declining",
            "confidence": 0.8
        }
    ]
}
"""

    def __init__(self, llm_model: Optional[str] = None):
        self.llm = create_llm(llm_model)

    def generate_insights(
        self,
        findings: list[Finding],
        contradictions: list[Contradiction],
        sources: list[Source],
        research_query: str,
    ) -> list[Insight]:
        """Generate insights from findings and contradictions."""
        findings_text = "\n".join(
            f"Finding {i+1}: {finding.claim}\n"
            f"  Confidence: {finding.confidence:.0%}\n"
            f"  Sources: {', '.join(finding.supporting_sources)}\n"
            for i, finding in enumerate(findings)
        )

        contradictions_text = "\n".join(
            f"Conflict {i+1}: {contradiction.claim_a} vs {contradiction.claim_b}\n"
            f"  Sources: {contradiction.source_a} vs {contradiction.source_b}\n"
            for i, contradiction in enumerate(contradictions)
        )

        sources_text = "\n".join(
            f"- {s.title} ({s.source_type.value})" for s in sources[:10]
        )

        user_message = (
            f"Research Query: {research_query}\n\n"
            f"Findings:\n{findings_text}\n\n"
            f"Contradictions:\n{contradictions_text}\n\n"
            f"Sources:\n{sources_text}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.INSIGHT_SYSTEM_PROMPT),
            ("human", user_message),
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        content = response.content.strip()

        try:
            if "```" in content:
                content = content.split("```")[1].strip()
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            result = json.loads(content)
            insights_data = result.get("insights", [])
        except json.JSONDecodeError:
            insights_data = []

        insights = []
        for ind in insights_data:
            insights.append(Insight(
                insight=ind.get("insight", ""),
                reasoning_chain=ind.get("reasoning_chain", []),
                supporting_findings=ind.get("supporting_findings", []),
                confidence=ind.get("confidence", 0.5),
                category=ind.get("category", "general"),
            ))

        return insights

    def generate_hypotheses(
        self,
        findings: list[Finding],
        contradictions: list[Contradiction],
    ) -> list[dict]:
        """Generate testable hypotheses from findings."""
        findings_text = "\n".join(f"- {finding.claim}" for finding in findings)
        contradictions_text = "\n".join(
            f"- {contradiction.claim_a} vs {contradiction.claim_b}" for contradiction in contradictions
        )

        user_message = f"Findings:\n{findings_text}\n\nContradictions:\n{contradictions_text}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.HYPOTHESIS_SYSTEM_PROMPT),
            ("human", user_message),
        ])
        chain = prompt | self.llm
        response = chain.invoke({})

        try:
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].strip()
            return json.loads(content).get("hypotheses", [])
        except json.JSONDecodeError:
            return []

    def identify_trends(
        self,
        findings: list[Finding],
        sources: list[Source],
    ) -> list[dict]:
        """Identify emerging trends from findings."""
        findings_text = "\n".join(f"- {finding.claim}" for finding in findings)
        sources_text = "\n".join(f"- {s.title} ({s.source_type.value})" for s in sources)

        user_message = f"Findings:\n{findings_text}\n\nSources:\n{sources_text}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.TREND_SYSTEM_PROMPT),
            ("human", user_message),
        ])
        chain = prompt | self.llm
        response = chain.invoke({})

        try:
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].strip()
            return json.loads(content).get("trends", [])
        except json.JSONDecodeError:
            return []

    def analyze(
        self,
        findings: list[Finding],
        contradictions: list[Contradiction],
        sources: list[Source],
        research_query: str,
    ) -> dict:
        """Full insight analysis pipeline."""
        insights = self.generate_insights(findings, contradictions, sources, research_query)
        hypotheses = self.generate_hypotheses(findings, contradictions)
        trends = self.identify_trends(findings, sources)

        return {
            "query": research_query,
            "insights": insights,
            "hypotheses": hypotheses,
            "trends": trends,
        }
