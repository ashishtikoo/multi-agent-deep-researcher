"""
Demo data generator for the Multi-Agent Deep Researcher.
Provides realistic mock data when API keys are not available.
"""

from models import Source, SourceType, Finding, Insight, Contradiction, ResearchReport
from datetime import datetime


def get_demo_sources(query: str) -> list[Source]:
    """Generate realistic demo sources based on the query."""
    return [
        Source(
            title="Advances in Renewable Energy Storage: A 2024 Review",
            url="https://www.nature.com/articles/energy-storage-2024",
            source_type=SourceType.ACADEMIC,
            snippet="This comprehensive review examines the latest developments in battery storage technologies, including solid-state batteries, flow batteries, and emerging hydrogen storage solutions for renewable energy integration.",
            relevance_score=0.95,
            published_date="2024-03-15",
            author="Dr. Sarah Chen, MIT",
        ),
        Source(
            title="Global Energy Storage Market Reaches $45B in 2024",
            url="https://www.reuters.com/business/energy/storage-market-2024",
            source_type=SourceType.NEWS,
            snippet="The global energy storage market has experienced unprecedented growth, driven by falling lithium-ion battery costs and increasing renewable energy deployment worldwide.",
            relevance_score=0.90,
            published_date="2024-06-20",
            author="Reuters Energy Desk",
        ),
        Source(
            title="IEA World Energy Outlook 2024: Storage and Grid Integration",
            url="https://www.iea.org/reports/world-energy-outlook-2024",
            source_type=SourceType.REPORT,
            snippet="The International Energy Agency projects that energy storage capacity must triple by 2030 to meet net-zero emissions targets, with significant investment needed in grid-scale solutions.",
            relevance_score=0.88,
            published_date="2024-10-10",
            author="International Energy Agency",
        ),
        Source(
            title="Solid-State Batteries: The Next Frontier in Energy Storage",
            url="https://arxiv.org/abs/2403.12345",
            source_type=SourceType.ACADEMIC,
            snippet="Recent breakthroughs in solid-state battery technology demonstrate 2x energy density compared to conventional lithium-ion cells, with improved safety profiles and longer cycle life.",
            relevance_score=0.92,
            published_date="2024-03-22",
            author="Prof. Takashi Yamamoto, University of Tokyo",
        ),
        Source(
            title="Green Hydrogen Storage: Scaling for Industrial Applications",
            url="https://www.sciencedirect.com/science/hydrogen-storage",
            source_type=SourceType.ACADEMIC,
            snippet="Green hydrogen produced via electrolysis powered by renewable energy offers a promising long-duration storage solution, though current costs remain 2-3x higher than fossil fuel alternatives.",
            relevance_score=0.85,
            published_date="2024-05-18",
            author="Dr. Maria Rodriguez, ETH Zurich",
        ),
        Source(
            title="Tesla Megapack Deployments Surge 120% Year-over-Year",
            url="https://www.bloomberg.com/news/tesla-megapack-2024",
            source_type=SourceType.NEWS,
            snippet="Tesla's utility-scale battery deployments have surged, with the Megapack factory in Shanghai operating at full capacity to meet growing demand from grid operators worldwide.",
            relevance_score=0.80,
            published_date="2024-07-12",
            author="Bloomberg Green",
        ),
        Source(
            title="Thermal Energy Storage: The Overlooked Solution",
            url="https://www.sciencemag.org/news/thermal-storage",
            source_type=SourceType.ACADEMIC,
            snippet="Molten salt and phase-change thermal storage systems offer cost-effective long-duration storage at 1/10th the cost of lithium-ion batteries, making them ideal for industrial applications.",
            relevance_score=0.78,
            published_date="2024-04-30",
            author="Science Magazine",
        ),
        Source(
            title="BESS Market Forecast 2024-2030: Goldman Sachs Report",
            url="https://www.goldmansachs.com/insights/energy-storage",
            source_type=SourceType.REPORT,
            snippet="Goldman Sachs projects the Battery Energy Storage Systems market will grow at 25% CAGR through 2030, driven by policy support, falling costs, and increasing grid instability from renewable penetration.",
            relevance_score=0.87,
            published_date="2024-01-25",
            author="Goldman Sachs Research",
        ),
    ]


def get_demo_findings() -> list[Finding]:
    return [
        Finding(
            claim="Solid-state batteries represent the most significant near-term breakthrough in energy storage, offering 2x energy density over conventional lithium-ion technology.",
            supporting_sources=["Advances in Renewable Energy Storage: A 2024 Review", "Solid-State Batteries: The Next Frontier"],
            confidence=0.92,
        ),
        Finding(
            claim="The global energy storage market is experiencing exponential growth, reaching $45B in 2024 with projected 25% CAGR through 2030.",
            supporting_sources=["Global Energy Storage Market Reaches $45B", "BESS Market Forecast 2024-2030"],
            confidence=0.95,
        ),
        Finding(
            claim="Grid-scale storage capacity must triple by 2030 to meet international net-zero emissions targets, requiring unprecedented investment in infrastructure.",
            supporting_sources=["IEA World Energy Outlook 2024"],
            confidence=0.88,
        ),
        Finding(
            claim="Green hydrogen storage remains economically challenged, with costs 2-3x higher than fossil fuel alternatives, but offers unique long-duration storage capabilities.",
            supporting_sources=["Green Hydrogen Storage: Scaling for Industrial Applications"],
            confidence=0.80,
        ),
        Finding(
            claim="Thermal energy storage systems offer a cost-effective alternative at 1/10th the cost of lithium-ion, particularly for industrial and district heating applications.",
            supporting_sources=["Thermal Energy Storage: The Overlooked Solution"],
            confidence=0.78,
        ),
    ]


def get_demo_insights() -> list[Insight]:
    return [
        Insight(
            insight="The convergence of solid-state battery breakthroughs and massive market investment creates a window of opportunity for early adopters in the energy storage sector, with commercial-scale products expected by 2026-2027.",
            reasoning_chain=[
                "Solid-state batteries demonstrate 2x energy density in lab settings",
                "Major manufacturers are scaling production facilities",
                "Market investment is at record levels ($45B in 2024)",
                "Policy support is accelerating adoption",
                "Conclusion: Commercial viability within 2-3 years",
            ],
            supporting_findings=["Solid-state batteries breakthrough", "Market growth surge"],
            confidence=0.85,
            category="trend",
        ),
        Insight(
            insight="A bifurcated storage market is emerging: lithium-based solutions for short-duration (4-8h) applications and hydrogen/thermal for long-duration (24h+) storage, creating distinct investment and development pathways.",
            reasoning_chain=[
                "Lithium-ion dominates current installations but has duration limits",
                "Hydrogen and thermal offer superior long-duration capabilities",
                "Cost analysis shows thermal at 1/10th the cost of Li-ion",
                "Different applications require different storage durations",
                "Conclusion: Market segmentation by duration requirements",
            ],
            supporting_findings=["Market growth", "Green hydrogen", "Thermal storage"],
            confidence=0.82,
            category="pattern",
        ),
        Insight(
            insight="Grid instability from renewable penetration is the primary demand driver for energy storage, suggesting that storage adoption rates will correlate more strongly with renewable energy deployment than with policy incentives alone.",
            reasoning_chain=[
                "Renewable energy sources are intermittent by nature",
                "Grid operators face increasing stability challenges",
                "Storage is the most flexible grid stability solution",
                "Market growth correlates with renewable deployment rates",
                "Conclusion: Renewable growth drives storage demand",
            ],
            supporting_findings=["IEA outlook", "Market growth", "Tesla deployments"],
            confidence=0.80,
            category="implication",
        ),
    ]


def get_demo_contradictions() -> list[Contradiction]:
    return [
        Contradiction(
            claim_a="Solid-state batteries are 2-3 years from commercial viability",
            source_a="Solid-State Batteries: The Next Frontier (Academic)",
            claim_b="Solid-state battery commercialization faces 5+ years of additional development",
            source_b="Advances in Renewable Energy Storage: A 2024 Review (Academic)",
            resolution="The discrepancy likely reflects different definitions of 'commercial viability' — lab-scale vs. mass-manufactured at competitive pricing.",
        ),
        Contradiction(
            claim_a="Green hydrogen costs are 2-3x higher than fossil fuel alternatives",
            source_a="Green Hydrogen Storage: Scaling for Industrial Applications",
            claim_b="Green hydrogen is projected to reach cost parity with fossil fuels by 2028",
            source_b="IEA World Energy Outlook 2024",
            resolution="Both may be correct — current costs are indeed 2-3x higher, but IEA projects rapid cost reductions through scaling and policy support.",
        ),
    ]


def get_demo_report(query: str) -> ResearchReport:
    """Generate a complete demo report."""
    return ResearchReport(
        title=f"Comprehensive Analysis: {query}",
        query=query,
        executive_summary=(
            "This report presents findings from a multi-agent deep investigation into "
            f"{query}. Our team of specialized AI agents analyzed {len(get_demo_sources(query))} "
            "sources across academic papers, news articles, and industry reports. "
            "Key findings indicate rapid technological advancement in energy storage, "
            "significant market growth, and emerging opportunities in solid-state batteries "
            "and green hydrogen. The analysis also identified important contradictions "
            "between sources regarding timelines and cost projections, highlighting the "
            "dynamic nature of this rapidly evolving field."
        ),
        findings=get_demo_findings(),
        insights=get_demo_insights(),
        contradictions=get_demo_contradictions(),
        sources=get_demo_sources(query),
        recommendations=[
            "Invest in solid-state battery companies and supply chain companies ahead of the expected 2026-2027 commercialization wave.",
            "Develop a diversified storage strategy that combines short-duration lithium solutions with long-duration hydrogen or thermal storage.",
            "Monitor grid instability trends as a leading indicator for energy storage demand growth.",
            "Engage with policymakers to shape regulations that support storage integration with renewable energy systems.",
            "Consider pilot projects for thermal energy storage in industrial applications where cost sensitivity is high.",
        ],
    )
