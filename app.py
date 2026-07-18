"""
Multi-Agent AI Deep Researcher – Streamlit Web Application
"""

import streamlit as st
import os
import sys
import hashlib
from datetime import datetime
import base64

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.orchestrator import ResearchOrchestrator
from models import ResearchReport


# ─── Load Background Image ─────────────────────────────────────
def get_background_image():
    """Load and encode the background image."""
    bg_path = os.path.join(os.path.dirname(__file__), "assets", "background.jpeg")
    if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None


bg_image = get_background_image()

# ─── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent AI Deep Researcher",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Styles ─────────────────────────────────────────────
if bg_image:
    bg_css = f"""
[data-testid="stAppViewContainer"] {{
    background-image: url("data:image/jpeg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
"""
else:
    bg_css = """
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0f1e 0%, #1a2a4a 50%, #0a0f1e 100%);
}
"""

st.markdown("""
<style>
/* ─── Background Image ─── */
""" + bg_css + """
[data-testid="stAppViewContainer"] > .main {
    background: rgba(240, 248, 220, 0.95);
}

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: rgba(240, 248, 220, 0.95) !important;
    border-right: 1px solid rgba(100, 180, 80, 0.3) !important;
}

[data-testid="stSidebar"] .stMarkdown {
    color: #2d3a1a !important;
}

[data-testid="stSidebar"] .stMarkdown h1,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #1a2a0a !important;
}

[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown strong,
[data-testid="stSidebar"] .stMarkdown li,
[data-testid="stSidebar"] .stMarkdown span,
[data-testid="stSidebar"] .stMarkdown div,
[data-testid="stSidebar"] .stMarkdown a {
    color: #3d4a2a !important;
}

[data-testid="stSidebar"] .stMarkdown hr {
    border-color: rgba(100, 200, 255, 0.3) !important;
}

/* ─── Sidebar Title Fix ─── */
[data-testid="stSidebar"] .stMarkdown h1 {
    color: #1a2a0a !important;
    font-size: 1.5rem !important;
}

[data-testid="stSidebar"] .stMarkdown h1 > span {
    color: #1a2a0a !important;
}

[data-testid="stSidebar"] .stMarkdown h1 > img,
[data-testid="stSidebar"] .stMarkdown h1 > svg {
    filter: brightness(0) invert(1);
}

/* ─── Sidebar Title (st.title) ─── */
[data-testid="stSidebar"] .stTitle {
    color: #1a2a0a !important;
}

[data-testid="stSidebar"] .stTitle > span {
    color: #1a2a0a !important;
}

/* ─── Sidebar Title - Override All ─── */
[data-testid="stSidebar"] .stTitle h1,
[data-testid="stSidebar"] .stTitle h2,
[data-testid="stSidebar"] .stTitle h3 {
    color: #1a2a0a !important;
}

[data-testid="stSidebar"] .stTitle strong,
[data-testid="stSidebar"] .stTitle span,
[data-testid="stSidebar"] .stTitle p {
    color: #1a2a0a !important;
}

/* ─── Sidebar All Text ─── */
[data-testid="stSidebar"] * {
    color: #2d3a1a !important;
}

[data-testid="stSidebar"] .stMarkdown * {
    color: #2d3a1a !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div > div,
[data-testid="stSidebar"] .stSelectbox > div > div > div > div,
[data-testid="stSidebar"] .stSelectbox > div > div > div > div > div {
    color: #2d3a1a !important;
}

[data-testid="stSidebar"] .stCheckbox > label > div > div {
    color: #ffffff !important;
}

/* ─── Main Content ─── */
.main {
    color: #ffffff !important;
}

/* ─── Main Content - Override All Text ─── */
.main * {
    color: #ffffff !important;
}

.main .stMarkdown h1,
.main .stMarkdown h2,
.main .stMarkdown h3,
.main .stMarkdown h4,
.main .stMarkdown h5,
.main .stMarkdown h6 {
    color: #ffffff !important;
    text-shadow: 0 2px 10px rgba(0, 150, 255, 0.5);
}

.main .stMarkdown p,
.main .stMarkdown li,
.main .stMarkdown span,
.main .stMarkdown div,
.main .stMarkdown strong,
.main .stMarkdown em,
.main .stMarkdown a {
    color: #e0e8f0 !important;
}

/* ─── Main Page Title ─── */
.main > div > div:nth-child(1) > div:nth-child(1) > h1 {
    color: #ffffff !important;
}

.main > div > div:nth-child(1) > div:nth-child(1) > h1 > span {
    color: #ffffff !important;
}

/* ─── Main Page Paragraph ─── */
.main > div > div:nth-child(1) > div:nth-child(1) > p {
    color: #e0e8f0 !important;
}

/* ─── Main Page Section Headers ─── */
.main > div > div:nth-child(1) > div:nth-child(1) > h2 {
    color: #ffffff !important;
}

/* ─── Fix for st.text_area label ─── */
.stTextInput > label > div > div {
    color: #ffffff !important;
}

/* ─── Fix for all headings ─── */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

/* ─── Fix for all paragraphs ─── */
p {
    color: #e0e8f0 !important;
}

.main .stMarkdown a {
    color: #64c8ff !important;
}

/* ─── Fix for Streamlit's internal components ─── */
.main > div > div:nth-child(2) > div > div > div > div > div > div,
.main > div > div:nth-child(2) > div > div > div > div > div > div > div {
    color: #ffffff !important;
}

/* ─── Fix for selectbox dropdown ─── */
.stSelectbox > div > div > div > div > div {
    color: #ffffff !important;
}

/* ─── Fix for text area ─── */
.stTextArea > div > div > textarea {
    color: #ffffff !important;
}

/* ─── Fix for chat history ─── */
[data-testid="stContainer"] p,
[data-testid="stContainer"] span,
[data-testid="stContainer"] div {
    color: #ffffff !important;
}

/* ─── Buttons ─── */
.stButton > button {
    background: linear-gradient(135deg, #0066cc, #0099ff) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
    transition: all 0.3s;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #0088ff, #00bbff) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 150, 255, 0.4);
}

/* ─── Text Input ─── */
.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    color: #000000 !important;
    font-weight: 500 !important;
}

.stTextInput > div > div > input::placeholder {
    color: rgba(0, 0, 0, 0.4) !important;
}

/* ─── Text Area ─── */
.stTextArea > div > div > textarea {
    background: #ffffff !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    color: #000000 !important;
    font-weight: 500 !important;
}

/* ─── Selectbox ─── */
.stSelectbox > div > div {
    background: #ffffff !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    color: #000000 !important;
}

.stSelectbox > div > div > div {
    color: #000000 !important;
}

.stSelectbox > div > div > div > div {
    color: #000000 !important;
}

/* ─── Selectbox Help Icon ─── */
.stSelectbox > div > div > span {
    color: #000000 !important;
}

.stSelectbox > div > div > span > div {
    color: #000000 !important;
}

/* ─── Selectbox Tooltip ─── */
.stSelectbox > div > div > span > span {
    color: #000000 !important;
}

/* ─── Selectbox Tooltip Icon (?) ─── */
.stSelectbox > div > div > span > span > span,
.stSelectbox > div > div > span > span > span > span {
    color: #000000 !important;
}

/* ─── Selectbox Help Tooltip ─── */
[data-testid="stTooltipHoverText"] {
    color: #000000 !important;
}

/* ─── Selectbox Help Icon Circle ─── */
.stSelectbox > div > div > span > span > span > span > span {
    color: #000000 !important;
}

/* ─── Selectbox Help Icon - Aggressive Fix ─── */
.stSelectbox > div > div > span > span > span > span > span > span,
.stSelectbox > div > div > span > span > span > span > span > span > span,
.stSelectbox > div > div > span > span > span > span > span > span > span > span {
    color: #000000 !important;
}

/* ─── Selectbox All Children ─── */
.stSelectbox > div > div > span * {
    color: #000000 !important;
}

/* ─── Selectbox Label ─── */
.stSelectbox > label > div > div {
    color: #000000 !important;
}

/* ─── Tabs ─── */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    border-radius: 8px 8px 0 0 !important;
    color: #ffffff !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: rgba(0, 150, 255, 0.3) !important;
    border-bottom-color: rgba(0, 150, 255, 0.3) !important;
    color: #ffffff !important;
}

/* ─── Expander ─── */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(100, 200, 255, 0.2) !important;
    color: #ffffff !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(255, 255, 255, 0.15) !important;
}

.streamlit-expanderHeader > button {
    color: #ffffff !important;
}

/* ─── Progress Bar ─── */
.stProgress > div > div {
    background: rgba(255, 255, 255, 0.2) !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #0066cc, #00ccff) !important;
}

/* ─── Spinner ─── */
.stSpinner > div {
    border-top-color: #0099ff !important;
    border-right-color: #0099ff !important;
}

/* ─── Info/Success/Warning/Error Boxes ─── */
.stAlert {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    color: #ffffff !important;
}

/* ─── Download Buttons ─── */
.stDownloadButton > button {
    background: rgba(255, 255, 255, 0.1) !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    color: #ffffff !important;
}

.stDownloadButton > button:hover {
    background: rgba(0, 150, 255, 0.3) !important;
    border-color: rgba(0, 150, 255, 0.5) !important;
}

/* ─── Chat History ─── */
[data-testid="stContainer"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(100, 200, 255, 0.2) !important;
    border-radius: 8px !important;
    padding: 12px !important;
    margin-bottom: 8px !important;
    color: #ffffff !important;
}

/* ─── Example Research Topics ─── */
.stHorizontalBlock > div {
    background: rgba(255, 255, 255, 0.08) !important;
    border: 1px solid rgba(100, 200, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    font-size: 12px !important;
    padding: 8px 12px !important;
}

.stHorizontalBlock > div:hover {
    background: rgba(0, 150, 255, 0.2) !important;
    border-color: rgba(0, 150, 255, 0.4) !important;
}

/* ─── Scrollbar ─── */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
    background: rgba(0, 150, 255, 0.3);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 150, 255, 0.5);
}

/* ─── Developer Menu ─── */
.dev-menu-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.dev-menu-btn {
    background: rgba(0, 150, 255, 0.2) !important;
    border: 1px solid rgba(100, 200, 255, 0.4) !important;
    color: #ffffff !important;
    backdrop-filter: blur(10px);
}

.dev-menu-btn:hover {
    background: rgba(0, 150, 255, 0.4) !important;
    box-shadow: 0 0 20px rgba(0, 150, 255, 0.3);
}

.dev-dropdown {
    background: rgba(15, 20, 40, 0.95) !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    backdrop-filter: blur(10px);
    color: #ffffff !important;
}

.dev-menu-item {
    color: #ffffff !important;
}

.dev-menu-item:hover {
    background: rgba(0, 150, 255, 0.2) !important;
}

.dev-menu-divider {
    background: rgba(100, 200, 255, 0.2) !important;
}

.toggle-switch {
    background: rgba(255, 255, 255, 0.2) !important;
}

.toggle-switch.active {
    background: #00cc66 !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("🔬 Deep Researcher")
    st.markdown("---")

    st.markdown("### Configuration")

    llm_model = st.selectbox(
        "LLM Model",
        ["openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3.1-sonnet", "google/gemini-2.0-flash"],
        index=0,
        help="Models available via OpenRouter (cheaper than direct API access)",
    )

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

# ─── Handle Developer Options Actions ──────────────────────────
import os

def handle_dev_actions():
    """Handle developer actions from query parameters."""
    query_params = st.query_params
    
    # Handle Run on Save toggle
    if "dev_run_on_save" in query_params:
        enabled = query_params["dev_run_on_save"] == "true"
        config_dir = os.path.join(os.path.dirname(__file__), ".streamlit")
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, "config.toml")
        
        if enabled:
            with open(config_path, "w") as f:
                f.write("[server]\nrunOnSave = true\n")
        else:
            if os.path.exists(config_path):
                os.remove(config_path)
        
        # Clear the query param to avoid infinite loop
        st.query_params.clear()
        st.rerun()
    
    # Handle Clear Cache
    if "dev_clear_cache" in query_params:
        st.cache_data.clear()
        st.cache_resource.clear()
        st.session_state["chat_history"] = []
        st.session_state["current_report"] = None
        st.session_state["research_done"] = False
        st.query_params.clear()
        st.rerun()

handle_dev_actions()

# ─── Top-Right Menu (Developer Options) ────────────────────────
import streamlit.components.v1 as components

components.html("""
<style>
/* Top-right menu container */
.dev-menu-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Menu button */
.dev-menu-btn {
    background: rgba(0, 150, 255, 0.2) !important;
    border: 1px solid rgba(100, 200, 255, 0.4) !important;
    color: #ffffff !important;
    backdrop-filter: blur(10px);
    width: 40px;
    height: 40px;
    font-size: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all 0.2s;
}

.dev-menu-btn:hover {
    background: rgba(0, 150, 255, 0.4) !important;
    box-shadow: 0 0 20px rgba(0, 150, 255, 0.3);
    transform: scale(1.05);
}

/* Dropdown menu */
.dev-dropdown {
    display: none;
    position: absolute;
    top: 50px;
    right: 0;
    background: rgba(15, 20, 40, 0.95) !important;
    border: 1px solid rgba(100, 200, 255, 0.3) !important;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 150, 255, 0.2);
    min-width: 240px;
    padding: 8px 0;
    animation: fadeIn 0.2s;
    backdrop-filter: blur(10px);
}

.dev-dropdown.show {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Menu items */
.dev-menu-item {
    padding: 12px 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: background 0.15s;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    font-size: 14px;
    color: #ffffff !important;
}

.dev-menu-item:hover {
    background: rgba(0, 150, 255, 0.2) !important;
}

.dev-menu-item .icon {
    font-size: 16px;
    width: 20px;
    text-align: center;
}

.dev-menu-item .label {
    flex: 1;
}

.dev-menu-item .sublabel {
    font-size: 11px;
    color: #888 !important;
    margin-top: 2px;
}

.dev-menu-divider {
    height: 1px;
    background: rgba(100, 200, 255, 0.2) !important;
    margin: 8px 0;
}

/* Toggle switch */
.toggle-switch {
    position: relative;
    width: 40px;
    height: 22px;
    background: rgba(255, 255, 255, 0.2) !important;
    border-radius: 11px;
    cursor: pointer;
    transition: background 0.3s;
}

.toggle-switch.active {
    background: #00cc66 !important;
}

.toggle-switch::after {
    content: '';
    position: absolute;
    top: 2px;
    left: 2px;
    width: 18px;
    height: 18px;
    background: white;
    border-radius: 50%;
    transition: transform 0.3s;
}

.toggle-switch.active::after {
    transform: translateX(18px);
}
</style>

<div class="dev-menu-container">
    <button class="dev-menu-btn" onclick="toggleDevMenu()">⋯</button>
    <div class="dev-dropdown" id="devDropdown">
        <div style="padding: 12px 16px 8px; font-size: 12px; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Developer Options</div>
        
        <button class="dev-menu-item" onclick="toggleRunOnSave()">
            <span class="icon">🔄</span>
            <div>
                <div class="label">Run on Save</div>
                <div class="sublabel">Auto-restart when files change</div>
            </div>
            <div class="toggle-switch" id="runOnSaveToggle"></div>
        </button>
        
        <div class="dev-menu-divider"></div>
        
        <button class="dev-menu-item" onclick="clearCache()">
            <span class="icon">🗑️</span>
            <div class="label">Clear Cache & Reset</div>
        </button>
        
        <div class="dev-menu-divider"></div>
        
        <div style="padding: 8px 16px; font-size: 11px; color: #aaa; text-align: center;">v1.0.0</div>
    </div>
</div>

<script>
function toggleDevMenu() {
    const dropdown = document.getElementById('devDropdown');
    dropdown.classList.toggle('show');
}

// Close menu when clicking outside
document.addEventListener('click', function(e) {
    const container = document.querySelector('.dev-menu-container');
    const dropdown = document.getElementById('devDropdown');
    if (!container.contains(e.target)) {
        dropdown.classList.remove('show');
    }
});

function toggleRunOnSave() {
    const toggle = document.getElementById('runOnSaveToggle');
    const isActive = toggle.classList.contains('active');
    
    if (isActive) {
        toggle.classList.remove('active');
        // Disable runOnSave via query param
        window.location.href = window.location.pathname + '?dev_run_on_save=false';
    } else {
        toggle.classList.add('active');
        // Enable runOnSave via query param
        window.location.href = window.location.pathname + '?dev_run_on_save=true';
    }
}

function clearCache() {
    if (confirm('Clear cache and reset the app? This will restart the application.')) {
        window.location.href = window.location.pathname + '?dev_clear_cache=true';
    }
}

// Initialize toggle state from query params
window.addEventListener('load', function() {
    const params = new URLSearchParams(window.location.search);
    if (params.get('dev_run_on_save') === 'true') {
        document.getElementById('runOnSaveToggle').classList.add('active');
    }
});
</script>
""", height=0)

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
