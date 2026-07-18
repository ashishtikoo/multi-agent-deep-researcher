"""
Formatting utilities for research outputs.
"""

from models import Finding, Insight, Contradiction, ResearchReport


def format_findings(findings: list[Finding]) -> str:
    """Format a list of findings into a readable string."""
    if not findings:
        return "No findings available."

    lines = []
    for i, finding in enumerate(findings, 1):
        lines.append(f"Finding {i}: {finding.claim}")
        lines.append(f"  Confidence: {finding.confidence:.0%}")
        lines.append(f"  Sources: {', '.join(finding.supporting_sources)}")
        if finding.contradictions:
            lines.append(f"  Contradictions: {len(finding.contradictions)} noted")
        lines.append("")
    return "\n".join(lines)


def format_report(report: ResearchReport) -> str:
    """Format a research report into markdown."""
    return report.to_markdown()
