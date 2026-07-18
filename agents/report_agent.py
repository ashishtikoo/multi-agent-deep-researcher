"""
Report Builder Agent – Compiles all insights into a structured report.
"""

import json
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from utils.llm import create_llm
from config import settings
from models import (
    Source,
    Finding,
    Insight,
    Contradiction,
    ResearchReport,
)


class ReportAgent:
    """
    The Report Builder Agent compiles all research findings, insights,
    and analysis into a comprehensive, well-structured research report.
    """

    REPORT_SYSTEM_PROMPT = """You are an expert research report writer.
Your task is to compile a comprehensive, well-structured research report
from the provided findings, insights, and analysis.

The report should include:
1. A compelling title
2. An executive summary (2-3 paragraphs)
3. Key findings organized by theme
4. Generated insights with reasoning
5. Identified contradictions and their analysis
6. Emerging trends
7. Testable hypotheses
8. Actionable recommendations
9. References

Make the report professional, clear, and actionable.
Use markdown formatting.

Research Query: {research_query}
"""

    SUMMARY_SYSTEM_PROMPT = """You are a research summarizer. Write a concise
executive summary (150-250 words) that captures the essence of the research.

Include:
- The research question
- Key findings
- Main insights
- Notable contradictions
- Overall conclusions

Research Query: {research_query}
Key Findings: {findings_summary}
Key Insights: {insights_summary}
"""

    RECOMMENDATIONS_SYSTEM_PROMPT = """You are a strategic advisor. Based on
the research findings and insights, provide actionable recommendations.

Research Query: {research_query}
Key Findings: {findings_summary}
Key Insights: {insights_summary}

Provide 5-8 specific, actionable recommendations.
Return as JSON array of strings.
"""

    def __init__(self, llm_model: Optional[str] = None):
        self.llm = create_llm(llm_model)

    def generate_title(self, research_query: str, findings: list[Finding]) -> str:
        """Generate a compelling report title."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a concise, professional report title for this research. Return only the title, nothing else."),
            ("human", "Research: {research_query}\nKey Finding: {key_finding}"),
        ])
        chain = prompt | self.llm
        response = chain.invoke({
            "research_query": research_query,
            "key_finding": findings[0].claim if findings else "N/A",
        })
        return response.content.strip().strip('"').strip("'")

    def generate_executive_summary(
        self,
        research_query: str,
        findings: list[Finding],
        insights: list[Insight],
    ) -> str:
        """Generate an executive summary."""
        findings_summary = "\n".join(f"- {f.claim}" for f in findings[:5])
        insights_summary = "\n".join(f"- {i.insight}" for i in insights[:5])

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.SUMMARY_SYSTEM_PROMPT),
            ("human",
             f"Research Query: {research_query}\n"
             f"Key Findings:\n{findings_summary}\n"
             f"Key Insights:\n{insights_summary}"),
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content.strip()

    def generate_recommendations(
        self,
        research_query: str,
        findings: list[Finding],
        insights: list[Insight],
    ) -> list[str]:
        """Generate actionable recommendations."""
        findings_summary = "\n".join(f"- {f.claim}" for f in findings[:5])
        insights_summary = "\n".join(f"- {i.insight}" for i in insights[:5])

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.RECOMMENDATIONS_SYSTEM_PROMPT),
            ("human",
             f"Research Query: {research_query}\n"
             f"Key Findings:\n{findings_summary}\n"
             f"Key Insights:\n{insights_summary}"),
        ])
        chain = prompt | self.llm
        response = chain.invoke({})

        try:
            content = response.content.strip()
            if "```" in content:
                content = content.split("```")[1].strip()
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            result = json.loads(content)
            if isinstance(result, list):
                return result
            return result.get("recommendations", [])
        except json.JSONDecodeError:
            return ["Review the full report for detailed recommendations."]

    def build_report(
        self,
        research_query: str,
        sources: list[Source],
        findings: list[Finding],
        insights: list[Insight],
        contradictions: list[Contradiction],
        trends: list[dict] | None = None,
        hypotheses: list[dict] | None = None,
    ) -> ResearchReport:
        """Build the complete research report."""
        title = self.generate_title(research_query, findings)
        summary = self.generate_executive_summary(
            research_query, findings, insights
        )
        recommendations = self.generate_recommendations(
            research_query, findings, insights
        )

        report = ResearchReport(
            title=title,
            query=research_query,
            executive_summary=summary,
            findings=findings,
            insights=insights,
            contradictions=contradictions,
            sources=sources,
            recommendations=recommendations,
        )

        return report

    def compile(self, research_data: dict) -> ResearchReport:
        """
        Compile a complete report from all research data.

        Args:
            research_data: Dictionary containing query, sources, findings,
                          insights, contradictions, trends, hypotheses
        """
        return self.build_report(
            research_query=research_data.get("query", "Research Topic"),
            sources=research_data.get("sources", []),
            findings=research_data.get("findings", []),
            insights=research_data.get("insights", []),
            contradictions=research_data.get("contradictions", []),
            trends=research_data.get("trends"),
            hypotheses=research_data.get("hypotheses"),
        )
