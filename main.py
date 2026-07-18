"""
CLI entry point for the Multi-Agent AI Deep Researcher.

Usage:
    python main.py "What are the latest advances in AI?"
    python main.py --model gpt-4o-mini "Your research question"
    python main.py --output report.md "Your research question"
"""

import typer
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown

from agents.orchestrator import ResearchOrchestrator

console = Console()

app = typer.Typer(
    name="deep-researcher",
    help="Multi-Agent AI Deep Researcher",
    add_completion=False,
)


@app.command()
def research(
    query: str = typer.Argument(..., help="The research question or topic"),
    model: Optional[str] = typer.Option(
        "gpt-4o", "--model", "-m", help="LLM model to use"
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Save report to file"
    ),
    no_verbose: bool = typer.Option(
        False, "--quiet", "-q", help="Suppress verbose output"
    ),
):
    """Run a deep multi-agent research investigation."""
    console.print()
    console.print("[bold blue]🔬 Multi-Agent AI Deep Researcher[/bold blue]")
    console.print(f"Query: [italic]{query}[/italic]")
    console.print(f"Model: {model}")
    console.print()

    orchestrator = ResearchOrchestrator(llm_model=model, verbose=not no_verbose)
    report = orchestrator.research(query)

    # Display report
    console.print()
    orchestrator.print_report(report)

    # Save to file if requested
    if output:
        markdown = report.to_markdown()
        with open(output, "w", encoding="utf-8") as f:
            f.write(markdown)
        console.print(f"\n[green]✅ Report saved to {output}[/green]")


@app.command()
def demo():
    """Run a demo research query."""
    console.print()
    console.print("[bold blue]🔬 Multi-Agent AI Deep Researcher - Demo Mode[/bold blue]")
    console.print()

    demo_query = "What are the latest developments in renewable energy storage technologies and their market potential?"

    orchestrator = ResearchOrchestrator(llm_model="gpt-4o", verbose=True)
    report = orchestrator.research(demo_query)

    console.print()
    orchestrator.print_report(report)


if __name__ == "__main__":
    app()
