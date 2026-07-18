"""
Unit tests for the Multi-Agent Deep Researcher.
"""

import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from models import Source, SourceType, Finding, Insight, Contradiction, ResearchReport
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.insight_agent import InsightAgent
from agents.report_agent import ReportAgent


# ─── Model Tests ───────────────────────────────────────────────

class TestSource:
    def test_create_source(self):
        s = Source(
            title="Test Paper",
            url="https://example.com",
            source_type=SourceType.ACADEMIC,
            snippet="Test snippet",
        )
        assert s.title == "Test Paper"
        assert s.source_type == SourceType.ACADEMIC

    def test_source_str(self):
        s = Source(
            title="Test",
            url="https://example.com",
            source_type=SourceType.WEB,
            snippet="Test",
        )
        assert "[WEB]" in str(s)


class TestResearchReport:
    def test_create_report(self):
        report = ResearchReport(
            title="Test Report",
            query="Test query",
            executive_summary="Test summary",
        )
        assert report.title == "Test Report"
        assert len(report.findings) == 0

    def test_to_markdown(self):
        report = ResearchReport(
            title="Test Report",
            query="Test query",
            executive_summary="This is a summary.",
        )
        md = report.to_markdown()
        assert "# Test Report" in md
        assert "Test query" in md
        assert "This is a summary." in md

    def test_to_markdown_with_findings(self):
        report = ResearchReport(
            title="Report",
            query="Query",
            executive_summary="Summary",
            findings=[
                Finding(
                    claim="AI is advancing rapidly",
                    supporting_sources=["Source A"],
                    confidence=0.9,
                )
            ],
        )
        md = report.to_markdown()
        assert "AI is advancing rapidly" in md

    def test_to_markdown_with_insights(self):
        report = ResearchReport(
            title="Report",
            query="Query",
            executive_summary="Summary",
            insights=[
                Insight(
                    insight="Trend insight",
                    reasoning_chain=["Step 1", "Step 2"],
                    category="trend",
                    confidence=0.8,
                )
            ],
        )
        md = report.to_markdown()
        assert "Trend insight" in md
        assert "trend" in md


# ─── Agent Initialization Tests ────────────────────────────────

class TestAgentInitialization:
    def test_retriever_agent_exists(self):
        """Test that RetrieverAgent can be instantiated."""
        # May fail if no API keys, but class should be importable
        agent = RetrieverAgent()
        assert agent is not None

    def test_analysis_agent_exists(self):
        agent = AnalysisAgent()
        assert agent is not None

    def test_insight_agent_exists(self):
        agent = InsightAgent()
        assert agent is not None

    def test_report_agent_exists(self):
        agent = ReportAgent()
        assert agent is not None


# ─── Orchestrator Tests ────────────────────────────────────────

class TestOrchestrator:
    def test_orchestrator_import(self):
        """Test that the orchestrator can be imported."""
        from agents.orchestrator import ResearchOrchestrator
        assert ResearchOrchestrator is not None

    def test_orchestrator_create(self):
        from agents.orchestrator import ResearchOrchestrator
        orchestrator = ResearchOrchestrator(verbose=False)
        assert orchestrator is not None


# ─── Integration Test (requires API keys) ──────────────────────

@pytest.mark.integration
class TestIntegration:
    def test_full_pipeline(self):
        """Run a full research pipeline (requires API keys)."""
        from agents.orchestrator import ResearchOrchestrator

        orchestrator = ResearchOrchestrator(verbose=False)
        report = orchestrator.research("Test: renewable energy storage")

        assert report is not None
        assert report.title != ""
        assert len(report.sources) > 0
        assert report.executive_summary != ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
