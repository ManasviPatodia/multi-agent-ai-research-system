import streamlit as st
import time

# Attempt to import your backend agents. 
try:
    from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain
    HAS_BACKEND = True
except ImportError:
    HAS_BACKEND = False
    st.warning("Backend agents not found. Running UI in simulation mode for demonstration.")

# ── 1. Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="SwarmScholar",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── 2. Refined CSS Styling (Colors, Logo, Centering) ───────────────────────────
st.markdown("""
<style>
/* Import specialized fonts */
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

/* Base Theme overrides */
.stApp {
    background-color: #09090b; /* Very dark/almost black background */
    color: #a1a1aa;
    font-family: 'DM Sans', sans-serif;
}
.block-container { padding-top: 3rem; max-width: 1300px; }
header { visibility: hidden; }

/* ── Centered Header Styling (Logo & Subtitle) ── */
.rm-header-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 100%;
    margin-bottom: 3rem;
}

.rm-logo-container {
    /* Giving the scaled logo room to breathe so it doesn't overlap */
    padding: 10px 40px; 
    margin-bottom: 25px;
}

.rm-logo {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    
    /* Reduced the size here: (Minimum size, Preferred size, Maximum size) */
    font-size: clamp(2.5rem, 2.5vw, 4rem) !important; 
    
    color: #ffffff !important; 
    background: none !important;
    -webkit-text-fill-color: #ffffff !important; 
    letter-spacing: -1px !important;
    line-height: 1 !important;
    margin: 0 !important;
    transform: scaleX(1.5) !important; 
    display: inline-block !important;
}

.rm-subtitle {
    font-size: 1.05rem;
    color: #ffffff;
    max-width: 650px;
    line-height: 1.6;
    margin: 0 auto;
    font-weight: 400;
}

/* ── Custom Divider ── */
.custom-divider {
    height: 1px;
    background-color: #27272a;
    margin: 2rem 0 3rem 0;
    width: 100%;
}

/* ── Left Column: Inputs & Buttons ── */
.input-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #ff6b1a;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    font-weight: 500;
}
.stTextInput > div > div > input {
    background-color: #18181b !important;
    border: 1px solid #3f3f46 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    padding: 1rem 1.2rem !important;
    font-size: 1.05rem !important;
    transition: all 0.2s ease;
}
.stTextInput > div > div > input:focus {
    border-color: #ff6b1a !important;
    box-shadow: 0 0 0 1px #ff6b1a !important;
}

/* Primary Run Button */
.stButton > button {
    background: linear-gradient(90deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.8rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    width: 100%;
    margin-top: 1rem;
    box-shadow: 0 4px 15px rgba(255, 90, 26, 0.25) !important;
    transition: transform 0.1s ease;
}
.stButton > button:active { transform: scale(0.98) !important; }
.stButton > button p { margin: 0; }

/* TRY Pills */
.try-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #52525b;
    margin-top: 2rem;
    margin-bottom: 0.8rem;
    letter-spacing: 1px;
}
.pill-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.pill-button {
    background-color: #121214;
    border: 1px solid #27272a;
    border-radius: 6px;
    color: #a1a1aa;
    padding: 0.4rem 0.9rem;
    font-size: 0.8rem;
    cursor: default;
}

/* Empty Top Box placeholder */
.top-placeholder-box {
    background-color: #121214;
    border: 1px solid #27272a;
    border-radius: 12px;
    height: 70px;
    margin-bottom: 2rem;
}

/* ── Right Column: Pipeline Cards ── */
.pipeline-header {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    color: #ffffff;
    font-weight: 700;
    margin-bottom: 1.5rem;
}

/* Card Base */
.p-card {
    background-color: #121214;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
/* Card States */
.p-card.running {
    border-color: rgba(255, 107, 26, 0.6);
    background-color: #1a1412;
}
.p-card.done {
    border-color: rgba(80, 200, 120, 0.3);
}

.p-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}
.p-card-left { display: flex; align-items: center; gap: 14px; }

.p-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #ff6b1a;
    font-weight: 600;
}
.p-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
}

/* Status text formatting */
.p-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 1.5px;
}
.status-waiting { color: #52525b; }
.status-running { color: #ff6b1a; animation: pulse 1.5s infinite; }
.status-done { color: #50c878; }

.p-desc {
    font-size: 0.85rem;
    color: #71717a;
    margin-left: 32px; /* Aligns with text, past the number */
}

@keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }

/* Output Panels */
.output-panel {
    background-color: #121214;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 2.5rem;
    margin-top: 1.5rem;
    color: #d4d4d8;
    line-height: 1.7;
}
.output-panel h1, .output-panel h2, .output-panel h3 {
    color: #ffffff;
    font-family: 'Syne', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ── 3. Helper: Dynamic HTML Generator for Right Column ─────────────────────────
def generate_pipeline_html(current_step: int):
    """Generates the HTML for the 4 stacked cards based on the current step."""
    steps_config = [
        {"num": "01", "title": "Search Agent", "desc": "Gathers recent web information"},
        {"num": "02", "title": "Reader Agent", "desc": "Scrapes & extracts deep content"},
        {"num": "03", "title": "Writer Chain", "desc": "Drafts the full research report"},
        {"num": "04", "title": "Critic Chain", "desc": "Reviews & scores the report"}
    ]
    
    html = ""
    for i, config in enumerate(steps_config):
        step_number = i + 1
        
        # Determine state
        if current_step < step_number:
            card_class = "waiting"
            status_class = "status-waiting"
            status_text = "WAITING"
        elif current_step == step_number:
            card_class = "running"
            status_class = "status-running"
            status_text = "● RUNNING"
        else:
            card_class = "done"
            status_class = "status-done"
            status_text = "✓ DONE"
            
        html += f"""
        <div class="p-card {card_class}">
            <div class="p-card-top">
                <div class="p-card-left">
                    <span class="p-num">{config['num']}</span>
                    <span class="p-title">{config['title']}</span>
                </div>
                <span class="p-status {status_class}">{status_text}</span>
            </div>
            <div class="p-desc">{config['desc']}</div>
        </div>
        """
    return html

# ── 4. Session State Init ──────────────────────────────────────────────────────
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'pipeline_step' not in st.session_state:
    st.session_state.pipeline_step = 0
if 'results' not in st.session_state:
    st.session_state.results = {}

# ── 5. Main Layout Rendering ───────────────────────────────────────────────────
# Perfectly Centered Header
st.markdown("""
<div class="rm-header-wrapper">
    <div class="rm-logo-container">
        <h1 class="rm-logo">SwarmScholar</h1>
    </div>
    <p class="rm-subtitle">Four specialized AI agents collaborate — searching, scraping, writing, and critiquing — to deliver a polished research report on any topic.</p>
</div>
<div class="custom-divider"></div>
""", unsafe_allow_html=True)

# Columns definition
col_left, col_gap, col_right = st.columns([4.2, 0.6, 5.2])

# -- Left Column (Input)
with col_left:
    st.markdown('<div class="top-placeholder-box"></div>', unsafe_allow_html=True)
    st.markdown('<div class="input-label">RESEARCH TOPIC</div>', unsafe_allow_html=True)
    
    topic = st.text_input(
        "hidden_label", 
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        label_visibility="collapsed"
    )
    
    run_clicked = st.button("⚡ Run Research Pipeline")
    
    st.markdown("""
    <div class="try-label">TRY &rarr;</div>
    <div class="pill-container">
        <div class="pill-button">LLM agents 2025</div>
        <div class="pill-button">CRISPR gene editing</div>
        <div class="pill-button">Fusion energy progress</div>
    </div>
    """, unsafe_allow_html=True)

# -- Right Column (Pipeline UI Placeholder)
with col_right:
    st.markdown('<div class="pipeline-header">Pipeline</div>', unsafe_allow_html=True)
    pipeline_container = st.empty()
    pipeline_container.markdown(generate_pipeline_html(st.session_state.pipeline_step), unsafe_allow_html=True)

# ── 6. Execution & Animation Logic ─────────────────────────────────────────────
if run_clicked and topic.strip():
    st.session_state.is_running = True
    st.session_state.pipeline_step = 1
    st.session_state.results = {}
    st.rerun()

if st.session_state.is_running:
    try:
        # Step 1: SEARCH
        pipeline_container.markdown(generate_pipeline_html(1), unsafe_allow_html=True)
        if HAS_BACKEND:
            search_agent = build_search_agent()
            sr = search_agent.invoke({"messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]})
            st.session_state.results["search"] = sr['messages'][-1].content
        else:
            time.sleep(2)
            st.session_state.results["search"] = "Simulated search data..."
            
        # Step 2: READ
        st.session_state.pipeline_step = 2
        pipeline_container.markdown(generate_pipeline_html(2), unsafe_allow_html=True)
        if HAS_BACKEND:
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({"messages": [("user", f"Based on the following search results about '{topic}', pick the most relevant URL and scrape it.\n{st.session_state.results['search'][:800]}")]})
            st.session_state.results["reader"] = rr['messages'][-1].content
        else:
            time.sleep(2)
            st.session_state.results["reader"] = "Simulated scraped data..."
            
        # Step 3: WRITE
        st.session_state.pipeline_step = 3
        pipeline_container.markdown(generate_pipeline_html(3), unsafe_allow_html=True)
        if HAS_BACKEND:
            res_combined = f"SEARCH RESULTS : \n {st.session_state.results['search']} \n\n DETAILED SCRAPED CONTENT : \n {st.session_state.results['reader']}"
            st.session_state.results["writer"] = writer_chain.invoke({"topic" : topic, "research" : res_combined})
        else:
            time.sleep(3)
            st.session_state.results["writer"] = "# Generated Report\nThis is a placeholder report generated in simulation mode."
            
        # Step 4: CRITIQUE
        st.session_state.pipeline_step = 4
        pipeline_container.markdown(generate_pipeline_html(4), unsafe_allow_html=True)
        if HAS_BACKEND:
            st.session_state.results["critic"] = critic_chain.invoke({"report": st.session_state.results['writer']})
        else:
            time.sleep(2)
            st.session_state.results["critic"] = "Simulated critic review notes: The report looks solid."
        
        # Done
        st.session_state.pipeline_step = 5
        pipeline_container.markdown(generate_pipeline_html(5), unsafe_allow_html=True)
        st.session_state.is_running = False
        st.rerun()

    except Exception as e:
        st.error(f"Pipeline Error: {str(e)}")
        st.session_state.is_running = False

# ── 7. Display Results ─────────────────────────────────────────────────────────
if not st.session_state.is_running and st.session_state.pipeline_step == 5:
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("## Final Analysis")
    
    r = st.session_state.results
    
    tab1, tab2 = st.tabs(["Final Report", "Critic Chain Feedback"])
    
    with tab1:
        st.markdown(f'<div class="output-panel">{r.get("writer", "")}</div>', unsafe_allow_html=True)
        
        st.download_button(
            label="Download Markdown",
            data=r.get("writer", "No data"),
            file_name=f"report_{int(time.time())}.md"
        )
        
    with tab2:
        st.markdown(f'<div class="output-panel" style="border-color: rgba(255, 107, 26, 0.4);">{r.get("critic", "")}</div>', unsafe_allow_html=True)