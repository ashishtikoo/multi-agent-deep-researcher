"""
Research Orchestrator – Coordinates all agents in a multi-agent pipeline.
"""

import time
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .retriever_agent import RetrieverAgent
from .analysis_agent import AnalysisAgent
from .insight_agent import InsightAgent
from .report_agent import ReportAgent
from models import Source, Finding, Insight, Contradiction, ResearchReport

console = Console()


class ResearchOrchestrator:
    """
    The central orchestrator that manages the multi-agent research pipeline.

    Pipeline:
    1. RetrieverAgent → gathers sources from multiple platforms
    2. AnalysisAgent → extracts findings and identifies contradictions
    3. InsightAgent → generates insights, hypotheses, and trends
    4. ReportAgent → compiles everything into a structured report
    """

    def __init__(
        self,
        llm_model: Optional[str] = None,
        verbose: bool = True,
    ):
        self.retriever = RetrieverAgent(llm_model)
        self.analyst = AnalysisAgent(llm_model)
        self.insights = InsightAgent(llm_model)
        self.reporter = ReportAgent(llm_model)
        self.verbose = verbose
        self.progress = None

    def _log(self, message: str, level: str = "info"):
        """Log a message if verbose mode is enabled."""
        if not self.verbose:
            return
        icons = {"info": "🔍", "success": "✅", "warning": "⚠️", "error": "❌", "agent": "🤖"}
        icon = icons.get(level, "•")
        console.print(f"[bold]{icon}[/bold] {message}")

    def _run_agent(self, agent_name: str, func, *args, **kwargs):
        """Run an agent with progress indication."""
        self._log(f"Starting {agent_name}...", "agent")
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        self._log(f"{agent_name} completed in {elapsed:.1f}s", "success")
        return result

    def research(self, query: str) -> ResearchReport:
        """
        Run the full multi-agent research pipeline.

        Args:
            query: The research question/topic to investigate.

        Returns:
            A complete ResearchReport with findings, insights, and recommendations.
        """
        self._log(f"Beginning deep research on: {query}", "info")
        self._log("=" * 60, "info")

        # Step 1: Retrieve sources
        self._log("Step 1/4: Gathering information from multiple sources...", "agent")
        sources: list[Source] = self._run_agent(
            "Contextual Retriever Agent",
            self.retriever.retrieve,
            query,
        )
        self._log(f"Retrieved {len(sources)} unique sources", "success")

        if not sources:
            raise RuntimeError(
                "No sources found. Check your API keys and internet connection."
            )

        # Step 2: Analyze findings
        self._log("Step 2/4: Analyzing findings and identifying contradictions...", "agent")
        analysis = self._run_agent(
            "Critical Analysis Agent",
            self.analyst.analyze,
            sources,
            query,
        )
        findings: list[Finding] = analysis.get("findings", [])
        contradictions: list[Contradiction] = analysis.get("contradictions", [])
        self._log(f"Extracted {len(findings)} findings, {len(contradictions)} contradictions", "success")

        # Step 3: Generate insights
        self._log("Step 3/4: Generating insights, hypotheses, and trends...", "agent")
        insight_data = self._run_agent(
            "Insight Generation Agent",
            self.insights.analyze,
            findings,
            contradictions,
            sources,
            query,
        )
        insights: list[Insight] = insight_data.get("insights", [])
        trends = insight_data.get("trends", [])
        hypotheses = insight_data.get("hypotheses", [])
        self._log(f"Generated {len(insights)} insights, {len(trends)} trends, {len(hypotheses)} hypotheses", "success")

        # Step 4: Build report
        self._log("Step 4/4: Compiling research report...", "agent")
        research_data = {
            "query": query,
            "sources": sources,
            "findings": findings,
            "insights": insights,
            "contradictions": contradictions,
            "trends": trends,
            "hypotheses": hypotheses,
        }
        report = self._run_agent(
            "Report Builder Agent",
            self.reporter.compile,
            research_data,
        )

        self._log("=" * 60, "info")
        self._log(f"Research complete! Report: '{report.title}'", "success")

        return report

    def research_stream(self, query: str) -> ResearchReport:
        """
        Run research with streaming progress updates via Rich.
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as progress:
            self.progress = progress

            task1 = progress.add_task("🔍 Gathering sources...", total=None)
            sources = self.retriever.retrieve(query)
            progress.update(task1, description=f"✅ Retrieved {len(sources)} sources")

            task2 = progress.add_task("🧠 Analyzing findings...", total=None)
            analysis = self.analyst.analyze(sources, query)
            findings = analysis["findings"]
            contradictions = analysis["contradictions"]
            progress.update(task2, description=f"✅ Found {len(findings)} findings, {len(contradictions)} contradictions")

            task3 = progress.add_task("💡 Generating insights...", total=None)
            insight_data = self.insights.analyze(findings, contradictions, sources, query)
            insights = insight_data["insights"]
            progress.update(task3, description=f"✅ Generated {len(insights)} insights")

            task4 = progress.add_task("📝 Building report...", total=None)
            research_data = {
                "query": query,
                "sources": sources,
                "findings": findings,
                "insights": insights,
                "contradictions": contradictions,
                "trends": insight_data.get("trends", []),
                "hypotheses": insight_data.get("hypotheses", []),
            }
            report = self.reporter.compile(research_data)
            progress.update(task4, description="✅ Report complete!")

        return report

    def print_report(self, report: ResearchReport):
        """Pretty-print the research report to the console."""
        console.print(Panel.fit(f"[bold blue]{report.title}[/bold blue]"))
        console.print()
        console.print(f"[bold]Research Query:[/bold] {report.query}")
        console.print(f"[bold]Sources:[/bold] {len(report.sources)}")
        console.print(f"[bold]Findings:[/bold] {len(report.findings)}")
        console.print(f"[bold]Insights:[/bold] {len(report.insights)}")
        console.print()

        console.print("[bold]Executive Summary[/bold]")
        console.print(report.executive_summary)
        console.print()

        if report.findings:
            console.print("[bold]Key Findings[/bold]")
            for i, finding in enumerate(report.findings, 1):
                console.print(f"  {i}. {finding.claim} [dim](confidence: {finding.confidence:.0%})[/dim]")
            console.print()

        if report.insights:
            console.print("[bold]Insights[/bold]")
            for i, ins in enumerate(report.insights, 1):
                console.print(f"  {i}. {ins.insight} [dim]({ins.category})[/dim]")
            console.print()

        if report.recommendations:
            console.print("[bold]Recommendations[/bold]")
            for i, rec in enumerate(report.recommendations, 1):
                console.print(f"  {i}. {rec}")
