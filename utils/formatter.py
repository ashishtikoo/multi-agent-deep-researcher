"""
Formatting utilities for research outputs.
"""

from models import Finding, Insight, Contradiction, ResearchReport


def format_findings(findings: list[Finding]) -> str:
    """Format a list of findings into a readable string."""
    if not findings:
        return "No findings available."

    lines = []
    for i, f in enumerate(findings, 1):
        lines.append(f"Finding {i}: {f.claim}")
        lines.append(f"  Confidence: {f.confidence:.0%}")
        lines.append(f"  Sources: {', '.join(f.supporting_sources)}")
        if f.contradictions:
            lines.append(f"  Contradictions: {len(f.contradictions)} noted")
        lines.append("")
    return "\n".join(lines)


def format_report(report: ResearchReport) -> str:
    """Format a research report into markdown."""
    return report.to_markdown()
