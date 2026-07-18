"""
Multi-Agent AI Deep Researcher – Streamlit Web Application
"""

import streamlit as st
import os
import sys
import hashlib
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.orchestrator import ResearchOrchestrator
from models import ResearchReport


# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent AI Deep Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("🔬 Deep Researcher")
    st.markdown("---")

    st.markdown("### Configuration")

    llm_model = st.selectbox(
        "LLM Model",
        ["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet", "google/gemini-2.0-flash"],
        index=0,
        help="Models available via OpenRouter (cheaper than direct API access)",
    )

    st.markdown("---")
    st.markdown("### Developer Options")

    run_on_save = st.checkbox(
        "Run on Save",
        value=False,
        help="Automatically restart the app when files are saved (useful during development)",
    )

    if run_on_save:
        # Create .streamlit/config.toml to enable runOnSave
        import os
        config_dir = os.path.join(os.path.dirname(__file__), ".streamlit")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config.toml")
        with open(config_path, "w") as f:
            f.write("[server]\nrunOnSave = true\n")
        st.info("✅ Run on Save enabled — app will restart on file saves.")
    else:
        # Remove the config file if it exists
        config_path = os.path.join(os.path.dirname(__file__), ".streamlit", "config.toml")
        if os.path.exists(config_path):
            os.remove(config_path)

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Multi-Agent AI Deep Researcher**

    An AI-powered research assistant that spins up specialized agents to:
    - 🔍 **Retrieve** data from multiple sources
    - 🧠 **Analyze** findings and contradictions
    - 💡 **Generate** insights and hypotheses
    - 📝 **Compile** structured reports

    Built with LangChain & Streamlit
    """)


# ─── Main Content ──────────────────────────────────────────────
st.title("🔬 Multi-Agent AI Deep Researcher")
st.markdown(
    "Enter a research topic or question, and our team of AI agents will conduct "
    "a deep, multi-source investigation and compile a comprehensive report."
)

# Initialize session state
if "query" not in st.session_state:
    st.session_state["query"] = ""
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "current_report" not in st.session_state:
    st.session_state["current_report"] = None
if "research_done" not in st.session_state:
    st.session_state["research_done"] = False

# ─── Input Section ─────────────────────────────────────────────
query = st.text_area(
    "📋 Research Question / Topic",
    value=st.session_state["query"],
    placeholder="e.g., 'What are the latest advances in quantum computing and their implications for cryptography?'",
    height=100,
)

# Update session state when user types
st.session_state["query"] = query

col1, col2 = st.columns([1, 5])
with col1:
    run_button = st.button("🚀 Start Research", type="primary", use_container_width=True)


# ─── Helper: Display Report ────────────────────────────────────
def display_report(report: ResearchReport):
    """Display a research report in the Streamlit UI."""
    st.success("✅ Research Complete!")
    st.markdown("---")

    st.markdown(f"## {report.title}")
    st.caption(f"Research Query: {report.query} | Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M')}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Summary",
        "🔍 Findings",
        "💡 Insights",
        "⚠️ Contradictions",
        "📚 References",
    ])

    with tab1:
        st.markdown("### Executive Summary")
        st.markdown(report.executive_summary)

        if report.recommendations:
            st.markdown("### Recommendations")
            for i, rec in enumerate(report.recommendations, 1):
                st.markdown(f"{i}. {rec}")

    with tab2:
        st.markdown("### Key Findings")
        for i, finding in enumerate(report.findings, 1):
            with st.expander(f"Finding {i}: {finding.claim[:150]}...", expanded=False):
                st.markdown(f"**Confidence:** {finding.confidence:.0%}")
                st.markdown(f"**Supporting Sources:** {', '.join(finding.supporting_sources)}")
                if finding.contradictions:
                    st.warning(f"**Contradictions:** {len(finding.contradictions)} noted")

    with tab3:
        st.markdown("### Generated Insights")
        for i, ins in enumerate(report.insights, 1):
            with st.expander(f"Insight {i}", expanded=False):
                st.markdown(f"**{ins.insight}**")
                st.markdown(f"**Reasoning:** {' → '.join(ins.reasoning_chain)}")
                st.markdown(f"**Confidence:** {ins.confidence:.0%}")
                st.markdown(f"**Category:** {ins.category}")

    with tab4:
        st.markdown("### Contradictions & Conflicts")
        if report.contradictions:
            for i, c in enumerate(report.contradictions, 1):
                st.warning(f"**Conflict {i}**")
                st.markdown(f"- **Claim A:** {c.claim_a}")
                st.markdown(f"- **Claim B:** {c.claim_b}")
                if c.resolution:
                    st.markdown(f"- **Resolution:** {c.resolution}")
        else:
            st.info("No significant contradictions found.")

    with tab5:
        st.markdown("### References")
        for i, s in enumerate(report.sources, 1):
            st.markdown(f"{i}. **{s.title}** — [{s.source_type.value}]({s.url})")

    # Download buttons
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        markdown_content = report.to_markdown()
        st.download_button(
            label="📥 Download Markdown Report",
            data=markdown_content,
            file_name=f"research_{report.query[:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )
    with col_b:
        json_content = report.model_dump_json(indent=2)
        st.download_button(
            label="📥 Download JSON Report",
            data=json_content,
            file_name=f"research_{report.query[:30].replace(' ', '_')}.json",
            mime="application/json",
        )


# ─── Helper: Chat Follow-up ────────────────────────────────────
def handle_follow_up(question: str, report: ResearchReport):
    """Handle a follow-up question using the existing research context."""
    from agents.report_agent import ReportAgent
    from utils.llm import create_llm

    llm = create_llm()

    # Build context from the report
    context = f"""
RESEARCH CONTEXT:
- Query: {report.query}
- Title: {report.title}
- Executive Summary: {report.executive_summary}

KEY FINDINGS:
"""
    for i, finding in enumerate(report.findings, 1):
        context += f"{i}. {finding.claim} (Confidence: {finding.confidence:.0%})\n"

    if report.insights:
        context += "\nKEY INSIGHTS:\n"
        for i, insight in enumerate(report.insights, 1):
            context += f"{i}. {insight.insight} (Category: {insight.category})\n"

    if report.recommendations:
        context += "\nRECOMMENDATIONS:\n"
        for i, rec in enumerate(report.recommendations, 1):
            context += f"{i}. {rec}\n"

    # Generate follow-up response
    prompt = f"""You are a research assistant that has just completed a deep investigation.

{context}

The user is asking a follow-up question based on this research.

Follow-up Question: {question}

Please provide a thoughtful, concise answer that:
1. References specific findings from the research above
2. Provides additional context or analysis
3. Is honest about limitations or gaps in the research
4. Suggests next steps if applicable

Keep the response under 300 words. Be direct and helpful."""

    response = llm.invoke(prompt)
    return response.content


# ─── Research Execution ────────────────────────────────────────
if run_button and query.strip():
    with st.spinner("Initializing research agents..."):
        try:
            orchestrator = ResearchOrchestrator(llm_model=llm_model, verbose=False)

            # ── Step 1: Retrieval ──────────────────────────────
            progress_bar = st.progress(0, text="🔍 Step 1/4: Gathering information from multiple sources...")
            sources_container = st.container()

            with sources_container:
                st.markdown("#### 🔍 Step 1: Retrieving Sources")
                sources = orchestrator.retriever.retrieve(query)
                st.markdown(f"**✅ Found {len(sources)} unique sources**")
                for i, s in enumerate(sources[:8], 1):
                    st.markdown(f"{i}. **{s.title}**")
                    st.caption(f"   Type: {s.source_type.value} | URL: {s.url[:80]}...")
                if len(sources) > 8:
                    st.caption(f"... and {len(sources) - 8} more sources")

            # ── Step 2: Analysis ───────────────────────────────
            progress_bar.progress(35, text="🧠 Step 2/4: Analyzing findings...")
            analysis_container = st.container()

            with analysis_container:
                st.markdown("#### 🧠 Step 2: Analyzing Findings")
                analysis = orchestrator.analyst.analyze(sources, query)
                findings = analysis["findings"]
                contradictions = analysis["contradictions"]
                st.markdown(f"**✅ Extracted {len(findings)} findings**")
                for i, finding in enumerate(findings[:5], 1):
                    st.markdown(f"{i}. {finding.claim[:200]}...")
                    st.caption(f"   Confidence: {finding.confidence:.0%} | Sources: {', '.join(finding.supporting_sources[:2])}")
                if contradictions:
                    st.warning(f"**⚠️ {len(contradictions)} contradictions detected**")
                    for c in contradictions[:3]:
                        st.markdown(f"- {c.claim_a[:150]}")
                        st.caption(f"  vs {c.claim_b[:150]}")
                else:
                    st.success("✅ No contradictions detected")

            # ── Step 3: Insights ───────────────────────────────
            progress_bar.progress(65, text="💡 Step 3/4: Generating insights...")
            insights_container = st.container()

            with insights_container:
                st.markdown("#### 💡 Step 3: Generating Insights")
                insight_data = orchestrator.insights.analyze(
                    findings, contradictions, sources, query
                )
                insights = insight_data["insights"]
                trends = insight_data.get("trends", [])
                hypotheses = insight_data.get("hypotheses", [])
                st.markdown(f"**✅ Generated {len(insights)} insights**")
                for i, ins in enumerate(insights[:5], 1):
                    st.markdown(f"{i}. {ins.insight[:200]}...")
                    st.caption(f"   Category: {ins.category} | Confidence: {ins.confidence:.0%}")
                if trends:
                    st.info(f"📈 **{len(trends)} trends identified**")
                if hypotheses:
                    st.info(f"🧪 **{len(hypotheses)} hypotheses generated**")

            # ── Step 4: Report ─────────────────────────────────
            progress_bar.progress(90, text="📝 Step 4/4: Compiling research report...")
            report_container = st.container()

            with report_container:
                st.markdown("#### 📝 Step 4: Compiling Report")

            research_data = {
                "query": query,
                "sources": sources,
                "findings": findings,
                "insights": insights,
                "contradictions": contradictions,
                "trends": trends,
                "hypotheses": hypotheses,
            }
            report = orchestrator.reporter.compile(research_data)
            progress_bar.progress(100, text="✅ Research complete!")

            # ── Display Report ─────────────────────────────────
            display_report(report)

            # ── Store for follow-ups ───────────────────────────
            st.session_state["current_report"] = report
            st.session_state["research_done"] = True

            # ── Chat Follow-up Section ─────────────────────────
            st.markdown("---")
            st.subheader("💬 Follow-up Questions")
            st.caption("Ask anything about this research — the AI will answer based on the findings above.")

            # Show chat history
            if st.session_state["chat_history"]:
                for i, chat in enumerate(st.session_state["chat_history"]):
                    with st.container():
                        col_q, col_a = st.columns([1, 4])
                        with col_q:
                            st.markdown("**👤 You:**")
                        with col_a:
                            st.markdown(chat["question"])

                        with col_q:
                            st.markdown("**🤖 AI:**")
                        with col_a:
                            st.markdown(chat["answer"])
                        st.markdown("---")

            # Chat input
            chat_col1, chat_col2 = st.columns([4, 1])
            with chat_col1:
                follow_up = st.text_input(
                    "Ask a follow-up question...",
                    placeholder="e.g., 'What are the main risks mentioned?' or 'How does this compare to 2023?'",
                    key="follow_up_input",
                )
            with chat_col2:
                send_button = st.button("➡️", type="primary")

            if send_button and follow_up.strip():
                with st.spinner("🤖 Analyzing your question..."):
                    try:
                        report = st.session_state["current_report"]
                        answer = handle_follow_up(follow_up, report)

                        # Store in chat history
                        st.session_state["chat_history"].append({
                            "question": follow_up,
                            "answer": answer,
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            if not follow_up.strip() and send_button:
                st.warning("Please type a follow-up question.")

        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Research failed: {error_msg}")

            if "api_key" in error_msg.lower() or "invalid_api_key" in error_msg.lower():
                st.error(
                    "🔑 **API Key Issue**\n\n"
                    "1. Make sure your `.env` file exists (run: `cp .env.example .env`)\n"
                    "2. Add your **OpenRouter** API key to `.env`:\n\n"
                    "```env\n"
                    "OPENROUTER_API_KEY=sk-or-v1-your-key-here\n"
                    "```\n\n"
                    "3. Restart the Streamlit app"
                )
            elif "tavily" in error_msg.lower() or "tavily" in error_msg.lower():
                st.warning(
                    "⚠️ **Tavily API Key Not Set**\n\n"
                    "Web search results may be limited. The agents will still work "
                    "using academic sources. To enable full web search, add your "
                    "Tavily API key to `.env` (free tier at tavily.com)."
                )
            else:
                st.error("Check the terminal for detailed error logs.")

elif run_button and not query.strip():
    st.warning("Please enter a research question or topic.")

# ─── Demo Examples ─────────────────────────────────────────────
st.markdown("---")
st.markdown("### 💡 Example Research Topics")

# Rotate examples based on current minute (no API calls needed)
all_examples = [
    "What are the latest advances in quantum computing and their implications for cryptography?",
    "How effective are carbon capture technologies in mitigating climate change?",
    "What is the impact of remote work on urban real estate markets post-pandemic?",
    "What are the ethical implications of AI-generated deepfakes in democratic processes?",
    "How is CRISPR technology advancing the treatment of genetic diseases?",
    "What role does blockchain play in supply chain transparency?",
    "How are autonomous vehicles changing urban transportation?",
    "What are the environmental impacts of data centers?",
    "How is AI transforming drug discovery and development?",
    "What are the security challenges of IoT devices?",
]

# Use current minute to rotate examples
minute_hash = int(hashlib.md5(str(datetime.now().minute).encode()).hexdigest(), 16)
start_idx = minute_hash % len(all_examples)
rotated_examples = all_examples[start_idx:] + all_examples[:start_idx]

# Show 5 rotating examples
for example in rotated_examples[:5]:
    if st.button(example, key=example[:30], use_container_width=True):
        st.session_state["query"] = example
        st.rerun()
