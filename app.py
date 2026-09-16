import streamlit as st
import time
import re
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Research Desk",
    page_icon="🖋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #FFFFFF;
}

.stApp {
    background:
        radial-gradient(ellipse 65% 40% at 50% 5%, rgba(255,255,255,0.12) 0%, transparent 60%),
        linear-gradient(135deg, #7A5AAE 0%, #4D63AC 55%, #3A5AA6 100%);
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 3rem 2rem 4rem; max-width: 760px; margin: 0 auto; }

/* ── Header ── */
.desk-header {
    text-align: center;
    padding-bottom: 2rem;
    margin-bottom: 2rem;
}
.desk-header h1 {
    font-family: 'Poppins', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0 0 0.7rem;
    letter-spacing: -0.01em;
}
.desk-header p {
    font-size: 1.05rem;
    font-weight: 400;
    color: rgba(255,255,255,0.78);
    max-width: 480px;
    line-height: 1.6;
    margin: 0 auto;
}

/* ── Input ── */
.stTextInput > label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    color: rgba(255,255,255,0.8) !important;
    font-weight: 500 !important;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.10) !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 12px !important;
    color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.8rem 1rem !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(255,255,255,0.5) !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2EC4B6 !important;
    box-shadow: 0 0 0 3px rgba(46,196,182,0.25) !important;
}

.stButton > button {
    background: #2EC4B6 !important;
    color: #FFFFFF !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.8rem !important;
    margin-top: 0.6rem;
    box-shadow: 0 8px 24px rgba(46,196,182,0.35) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 28px rgba(46,196,182,0.45) !important;
}

/* ── Secondary (suggestion) buttons — ghost style like Carrd's "Log In" ── */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #FFFFFF !important;
    border: 1.5px solid rgba(255,255,255,0.4) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.55rem 1rem !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #FFFFFF !important;
    background: rgba(255,255,255,0.08) !important;
    transform: none !important;
    box-shadow: none !important;
}

.stCaptionContainer, [data-testid="stCaptionContainer"] {
    color: rgba(255,255,255,0.6) !important;
}

/* ── Pipeline log ── */
.log-heading {
    font-family: 'Poppins', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 1rem;
}
.log-row {
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
    padding: 0.9rem 1.1rem;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    border-radius: 12px;
    margin-bottom: 0.6rem;
}

.log-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-top: 0.35rem;
    flex-shrink: 0;
    border: 1.5px solid rgba(255,255,255,0.35);
    background: transparent;
}
.log-dot.step-search.running  { background: #2EC4B6; border-color: #2EC4B6; box-shadow: 0 0 0 5px rgba(46,196,182,0.22); }
.log-dot.step-search.done     { background: #2EC4B6; border-color: #2EC4B6; }
.log-dot.step-reader.running  { background: #6FB1E8; border-color: #6FB1E8; box-shadow: 0 0 0 5px rgba(111,177,232,0.22); }
.log-dot.step-reader.done     { background: #6FB1E8; border-color: #6FB1E8; }
.log-dot.step-writer.running  { background: #F2C14E; border-color: #F2C14E; box-shadow: 0 0 0 5px rgba(242,193,78,0.22); }
.log-dot.step-writer.done     { background: #F2C14E; border-color: #F2C14E; }
.log-dot.step-critic.running  { background: #F2785C; border-color: #F2785C; box-shadow: 0 0 0 5px rgba(242,120,92,0.22); }
.log-dot.step-critic.done     { background: #F2785C; border-color: #F2785C; }

.log-mark.step-search  { color: #2EC4B6; }
.log-mark.step-reader  { color: #6FB1E8; }
.log-mark.step-writer  { color: #F2C14E; }
.log-mark.step-critic  { color: #F2785C; }

.log-body { flex: 1; }
.log-title {
    font-family: 'Poppins', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #FFFFFF;
}
.log-title.waiting { color: rgba(255,255,255,0.45); }
.log-desc {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.6);
    margin-top: 0.15rem;
}
.log-mark {
    font-size: 0.78rem;
    font-weight: 600;
    margin-left: auto;
    white-space: nowrap;
}

/* ── Field notes (raw agent output) ── */
details summary {
    font-size: 0.85rem !important;
    color: rgba(255,255,255,0.75) !important;
    cursor: pointer;
    padding: 0.4rem 0;
}
.field-note {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.14);
    border-left: 3px solid rgba(255,255,255,0.3);
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-top: 0.6rem;
    font-size: 0.88rem;
    line-height: 1.75;
    color: rgba(255,255,255,0.85);
    white-space: pre-wrap;
}
.field-note.step-search { border-left-color: #2EC4B6; }
.field-note.step-reader { border-left-color: #6FB1E8; }

/* ── The report, as a paper page floating on the gradient ── */
.dossier {
    background: #FBF9F3;
    border-radius: 14px;
    border-top: 5px solid #F2C14E;
    padding: 2.6rem 2.8rem;
    margin-top: 2.5rem;
    box-shadow: 0 20px 50px rgba(0,0,0,0.3);
    color: #22201B;
    position: relative;
}
.dossier-label {
    font-family: 'Poppins', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: #A8791F;
    margin-bottom: 1.2rem;
    padding-bottom: 0.9rem;
    border-bottom: 1px solid #E5DFC9;
}
.dossier h1, .dossier h2, .dossier h3 { font-family: 'Poppins', sans-serif; color: #22201B; }
.dossier p, .dossier li { color: #3A3628; line-height: 1.75; }

.dossier-wrap [data-testid="stMarkdownContainer"] {
    color: #3A3628;
}
.dossier-wrap [data-testid="stMarkdownContainer"] h1,
.dossier-wrap [data-testid="stMarkdownContainer"] h2,
.dossier-wrap [data-testid="stMarkdownContainer"] h3 {
    font-family: 'Poppins', sans-serif;
    color: #22201B;
}

/* ── Critic stamp ── */
.stamp-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: -1rem;
    margin-bottom: 1rem;
}
.stamp {
    border: 3px solid #F2785C;
    color: #F2785C;
    background: rgba(255,255,255,0.9);
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 1.3rem;
    padding: 0.5rem 1.1rem;
    border-radius: 10px;
    transform: rotate(-4deg);
}

.verdict-panel {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-top: 4px solid #F2785C;
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    margin-top: 1rem;
}
.verdict-panel [data-testid="stMarkdownContainer"] {
    color: rgba(255,255,255,0.88);
}

.desk-footer {
    text-align: center;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.5);
    margin-top: 4rem;
}

.stDownloadButton > button {
    background: transparent !important;
    color: #22201B !important;
    border: 1.5px solid #A8791F !important;
    border-radius: 10px !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    box-shadow: none !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background-color: #2EC4B6 !important;
}
.stProgress > div > div {
    background-color: rgba(255,255,255,0.15) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 1.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.18);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: rgba(255,255,255,0.55);
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    font-size: 0.9rem;
    padding: 0 0 0.7rem 0;
}
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 3px solid #2EC4B6 !important;
}

/* ── Report meta line ── */
.report-meta {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.65);
    margin: -1.5rem 0 1.2rem;
}

/* ── Sources ── */
.source-row {
    display: flex;
    gap: 0.6rem;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.14);
    font-size: 0.88rem;
    color: rgba(255,255,255,0.85);
}
.source-row:last-child { border-bottom: none; }
.source-row a { color: #6FB1E8; text-decoration: none; }
.source-row a:hover { text-decoration: underline; }
.source-title { color: rgba(255,255,255,0.9); }
</style>
""", unsafe_allow_html=True)



# ── Session state init ────────────────────────────────────────────────────────
for key, default in (("results", {}), ("running", False), ("done", False), ("current_topic", "")):
    if key not in st.session_state:
        st.session_state[key] = default

STEPS = [
    ("search", "Search agent", "Gathering recent sources from the open web"),
    ("reader", "Reader agent", "Scraping the most relevant page for depth"),
    ("writer", "Writer", "Drafting the report from what was gathered"),
    ("critic", "Critic", "Reviewing the draft and scoring it"),
]


def set_topic(value: str):
    st.session_state.topic_input = value


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="desk-header">
    <h1>The Research Desk</h1>
    <p>Give it a topic. A search agent, a reader, a writer, and a critic
    work it in sequence and hand back a finished report.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("How this works"):
    st.markdown(
        "- **Search agent** looks up recent, reliable sources on the web for your topic.\n"
        "- **Reader agent** picks the most relevant result and scrapes it for deeper detail.\n"
        "- **Writer** combines both into a structured report — introduction, key findings, "
        "conclusion, and sources.\n"
        "- **Critic** reads that report back and scores it, pointing out gaps or weak spots.\n\n"
        "Each step feeds the next, and you can watch the log below update live as it runs."
    )

topic = st.text_input(
    "Topic",
    placeholder="e.g. Fusion energy progress",
    key="topic_input",
)
run_btn = st.button("Begin research")

st.caption("Or try one of these")
sug_cols = st.columns(3)
for col, example in zip(sug_cols, ["LLM agents in 2026", "CRISPR gene editing", "Fusion energy progress"]):
    with col:
        st.button(example, key=f"sugg_{example}", on_click=set_topic, args=(example,),
                   use_container_width=True, type="secondary")


# ── Run pipeline, one step per rerun so the log visibly advances ──────────────
if run_btn:
    if not topic.strip():
        st.warning("Enter a topic before starting.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.session_state.current_topic = topic.strip()
        st.rerun()

r = st.session_state.results

# Figure out which step (if any) is still pending, before running it,
# so the log below can be rendered showing that step as "running".
pending_key = None
if st.session_state.running and not st.session_state.done:
    for key, _, _ in STEPS:
        if key not in r:
            pending_key = key
            break

# ── Pipeline log ──────────────────────────────────────────────────────────────
if r or st.session_state.running:
    st.markdown('<div class="log-heading">Pipeline</div>', unsafe_allow_html=True)
    rows = ""
    for key, title, desc in STEPS:
        if key in r:
            state = "done"
        elif key == pending_key:
            state = "running"
        else:
            state = "waiting"
        mark_text = {"done": "done", "running": "running", "waiting": ""}[state]
        rows += f"""
        <div class="log-row">
            <div class="log-dot step-{key} {state}"></div>
            <div class="log-body">
                <div class="log-title {state}">{title}</div>
                <div class="log-desc">{desc}</div>
            </div>
            <div class="log-mark step-{key}">{mark_text}</div>
        </div>
        """
    st.markdown(rows, unsafe_allow_html=True)
    if st.session_state.running:
        st.progress(len(r) / len(STEPS))

# ── Execute the pending step, then rerun so the log above reflects it ────────
if pending_key:
    topic_val = st.session_state.current_topic

    if pending_key == "search":
        with st.spinner("Search agent is working…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            r["search"] = sr["messages"][-1].content

    elif pending_key == "reader":
        with st.spinner("Reader agent is scraping the top source…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{r['search'][:800]}"
                )]
            })
            r["reader"] = rr["messages"][-1].content

    elif pending_key == "writer":
        with st.spinner("Writer is drafting the report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{r['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{r['reader']}"
            )
            r["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })

    elif pending_key == "critic":
        with st.spinner("Critic is reviewing the report…"):
            r["critic"] = critic_chain.invoke({"report": r["writer"]})

    st.session_state.results = dict(r)
    if len(st.session_state.results) >= len(STEPS):
        st.session_state.running = False
        st.session_state.done = True
    st.rerun()


# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_sources(search_text: str):
    """Pull Title/URL pairs out of the search agent's raw output."""
    entries = []
    blocks = search_text.split("----")
    for block in blocks:
        title_match = re.search(r"Title:\s*(.+)", block)
        url_match = re.search(r"URL:\s*(\S+)", block)
        if url_match:
            title = title_match.group(1).strip() if title_match else url_match.group(1)
            entries.append((title, url_match.group(1).strip()))
    return entries


def collapse_blank_lines(text: str) -> str:
    """Raw agent output sometimes has many blank lines in its table
    formatting; the field-note panel uses pre-wrap, so collapse runs
    of 2+ blank lines down to a single one before displaying."""
    return re.sub(r"\n\s*\n+", "\n\n", text.strip())


# ── Results ────────────────────────────────────────────────────────────────────
if r:
    tab_labels = ["Report"]
    if "critic" in r:
        tab_labels.append("Critic feedback")
    if "search" in r:
        tab_labels.append("Sources")
    if "search" in r or "reader" in r:
        tab_labels.append("Raw notes")

    tabs = st.tabs(tab_labels)
    tab_map = dict(zip(tab_labels, tabs))

    with tab_map["Report"]:
        if "writer" in r:
            word_count = len(r["writer"].split())
            read_time = max(1, round(word_count / 200))
            st.markdown(
                f'<div class="report-meta">{word_count} words · about {read_time} min read</div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="dossier-wrap">', unsafe_allow_html=True)
            st.markdown("""
            <div class="dossier">
                <div class="dossier-label">Final report</div>
            """, unsafe_allow_html=True)
            st.markdown(r["writer"])
            st.markdown("</div></div>", unsafe_allow_html=True)

            col1, col2 = st.columns([1, 1])
            with col1:
                st.download_button(
                    label="Download (.md)",
                    data=r["writer"],
                    file_name=f"research_report_{int(time.time())}.md",
                    mime="text/markdown",
                )
            with col2:
                with st.popover("Copy text"):
                    st.code(r["writer"], language=None)
        else:
            st.caption("Still writing — the report will appear here once the writer step finishes.")

    if "critic" in r:
        with tab_map["Critic feedback"]:
            score = ""
            first_line = r["critic"].strip().splitlines()[0] if r["critic"].strip() else ""
            if "/10" in first_line:
                score = first_line.split(":")[-1].strip()
            if score:
                st.markdown(f'<div class="stamp-wrap"><div class="stamp">{score}</div></div>', unsafe_allow_html=True)
            st.markdown('<div class="verdict-panel">', unsafe_allow_html=True)
            st.markdown(r["critic"])
            st.markdown('</div>', unsafe_allow_html=True)

    if "search" in r:
        with tab_map["Sources"]:
            sources = extract_sources(r["search"])
            if sources:
                rows = ""
                for title, url in sources:
                    rows += f'<div class="source-row"><span class="source-title">{title}</span> — <a href="{url}" target="_blank">{url}</a></div>'
                st.markdown(rows, unsafe_allow_html=True)
            else:
                st.caption("No structured sources found in the search output.")

    if "search" in r or "reader" in r:
        with tab_map["Raw notes"]:
            if "search" in r:
                with st.expander("Search notes", expanded=False):
                    st.markdown(f'<div class="field-note step-search">{collapse_blank_lines(r["search"])}</div>', unsafe_allow_html=True)
            if "reader" in r:
                with st.expander("Scraped notes", expanded=False):
                    st.markdown(f'<div class="field-note step-reader">{collapse_blank_lines(r["reader"])}</div>', unsafe_allow_html=True)

st.markdown('<div class="desk-footer">A four-agent pipeline built with LangChain.</div>', unsafe_allow_html=True)