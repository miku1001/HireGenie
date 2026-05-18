import streamlit as st
from orchestrator import run_pipeline

st.set_page_config(
    page_title="HireGenie — Tailor Your Resume",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CUSTOM CSS ===
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=IBM+Plex+Sans:wght@300;400;500&display=swap');
/* === ROOT VARIABLES === */
:root {
    --bg:        #0a0a0f;
    --surface:   #13131a;
    --surface2:  #1c1c26;
    --border:    #2a2a38;
    --accent:    #6c63ff;
    --accent2:   #a78bfa;
    --success:   #34d399;
    --warning:   #fbbf24;
    --danger:    #f87171;
    --text:      #e8e8f0;
    --muted:     #6b7280;
} 

/* === GLOBAL === */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* === HIDE STREAMLIT DEFAULTS === */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    max-width: 1200px !important;
}

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* === HEADINGS === */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    letter-spacing: -0.02em !important;
}
h1 { font-size: 2.8rem !important; font-weight: 800 !important; }
h2 { font-size: 1.6rem !important; font-weight: 700 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }

/* === FILE UPLOADER === */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* === TEXT AREA === */
textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s !important;
}
textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15) !important;
}

/* === PRIMARY BUTTON === */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(108, 99, 255, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(108, 99, 255, 0.45) !important;
}
.stButton > button:disabled {
    background: var(--surface2) !important;
    color: var(--muted) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* === METRIC CARDS === */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.2rem !important;
    text-align: center !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--accent2) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--muted) !important;
}

/* === EXPANDER === */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--accent) !important;
}

/* === ALERTS === */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border: none !important;
}

/* === SUCCESS / WARNING / ERROR === */
.stSuccess {
    background: rgba(52, 211, 153, 0.08) !important;
    border: 1px solid rgba(52, 211, 153, 0.25) !important;
    border-radius: 10px !important;
    color: var(--success) !important;
}
.stWarning {
    background: rgba(251, 191, 36, 0.08) !important;
    border: 1px solid rgba(251, 191, 36, 0.25) !important;
    border-radius: 10px !important;
}
.stError {
    background: rgba(248, 113, 113, 0.08) !important;
    border: 1px solid rgba(248, 113, 113, 0.25) !important;
    border-radius: 10px !important;
}

/* === INFO BOX === */
.stInfo {
    background: rgba(108, 99, 255, 0.08) !important;
    border: 1px solid rgba(108, 99, 255, 0.25) !important;
    border-radius: 10px !important;
    color: var(--accent2) !important;
}

/* === PROGRESS BAR === */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
    border-radius: 99px !important;
}

/* === DIVIDER === */
hr {
    border-color: var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* === CUSTOM CARDS === */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.skill-tag {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 500;
    margin: 0.2rem;
}
.tag-matched {
    background: rgba(52, 211, 153, 0.12);
    border: 1px solid rgba(52, 211, 153, 0.3);
    color: #34d399;
}
.tag-partial {
    background: rgba(251, 191, 36, 0.12);
    border: 1px solid rgba(251, 191, 36, 0.3);
    color: #fbbf24;
}
.tag-missing {
    background: rgba(248, 113, 113, 0.12);
    border: 1px solid rgba(248, 113, 113, 0.3);
    color: #f87171;
}
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.badge {
    display: inline-block;
    background: rgba(108, 99, 255, 0.15);
    border: 1px solid rgba(108, 99, 255, 0.3);
    color: var(--accent2);
    font-size: 0.72rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 99px;
    font-family: 'Syne', sans-serif;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


# === SIDEBAR ===
with st.sidebar:
    st.markdown("""
    <div style='padding: 0.5rem 0 1.5rem'>
        <div style='font-family: Syne, sans-serif; font-size: 1.4rem; font-weight: 800; color: #e8e8f0;'>
            Resume<span style='color: #6c63ff;'>AI</span>
        </div>
        <div style='font-size: 0.8rem; color: #6b7280; margin-top: 0.3rem;'>
            Powered by LangGraph + OpenRouter
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class='section-label'>How it works</div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Upload your resume PDF"),
        ("02", "Paste the job description"),
        ("03", "AI analyzes and rewrites"),
        ("04", "Download tailored resume"),
    ]
    for num, label in steps:
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:0.75rem; margin-bottom:0.75rem;'>
            <div style='font-family:Syne,sans-serif; font-size:0.7rem; font-weight:700;
                        color:#6c63ff; background:rgba(108,99,255,0.12);
                        border:1px solid rgba(108,99,255,0.25); border-radius:6px;
                        padding:0.15rem 0.4rem; min-width:28px; text-align:center;'>
                {num}
            </div>
            <div style='font-size:0.85rem; color:#c4c4d4;'>{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class='section-label'>Agents</div>
    """, unsafe_allow_html=True)

    agents = ["JD Analyzer", "Resume Parser", "Skills Matcher", "Rewriter", "Reviewer"]
    for agent in agents:
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;'>
            <div style='width:6px; height:6px; border-radius:50%;
                        background:#6c63ff; flex-shrink:0;'></div>
            <div style='font-size:0.82rem; color:#9090a8;'>{agent}</div>
        </div>
        """, unsafe_allow_html=True)


# === HERO ===
st.markdown("""
<div style='margin-bottom: 0.5rem;'>
    <span class='badge'>AI-Powered · LangGraph Agents</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<h1 style='margin-bottom: 0.25rem;'>
    Tailor Your Resume<br>
    <span style='color: #6c63ff;'>to Any Job.</span>
</h1>
<p style='color: #6b7280; font-size: 1rem; margin-bottom: 2rem;'>
    Upload your resume, paste a job description — our AI agents rewrite and optimize it for ATS.
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# === INPUT COLUMNS ===
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("<div class='section-label'>Your Resume</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Only PDF files are supported",
        label_visibility="collapsed"
    )
    if uploaded_file:
        st.markdown(f"""
        <div style='display:flex; align-items:center; gap:0.5rem; margin-top:0.5rem;
                    background:rgba(52,211,153,0.08); border:1px solid rgba(52,211,153,0.2);
                    border-radius:8px; padding:0.6rem 1rem;'>
            <span style='color:#34d399; font-size:0.85rem;'>✓ {uploaded_file.name}</span>
            <span style='color:#6b7280; font-size:0.75rem; margin-left:auto;'>
                {round(uploaded_file.size/1024, 1)} KB
            </span>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.markdown("<div class='section-label'>Job Description</div>", unsafe_allow_html=True)
    jd_text = st.text_area(
        "Paste JD",
        height=220,
        placeholder="We are looking for a Python Backend Developer with experience in FastAPI...",
        label_visibility="collapsed"
    )
    if jd_text.strip():
        word_count = len(jd_text.split())
        st.markdown(f"""
        <div style='font-size:0.75rem; color:#6b7280; text-align:right; margin-top:0.3rem;'>
            {word_count} words
        </div>
        """, unsafe_allow_html=True)

# === VALIDATION ===
st.markdown("---")
ready = uploaded_file is not None and jd_text.strip() != ""

if uploaded_file is None and jd_text.strip() == "":
    st.markdown("""
    <div style='text-align:center; color:#6b7280; font-size:0.9rem; padding:0.5rem 0;'>
        Upload your resume and paste a job description to continue
    </div>
    """, unsafe_allow_html=True)
elif uploaded_file is None:
    st.warning("📄 Upload your resume to continue.")
elif jd_text.strip() == "":
    st.warning("💼 Paste a job description to continue.")

# === BUTTON ===
is_running = st.session_state.get("pipeline_running", False)
customize_btn = st.button(
    "✦ Customize My Resume",
    disabled=not ready or is_running,
    use_container_width=True
)

# === PIPELINE ===
if customize_btn:
    st.session_state["pipeline_running"] = True

    with st.status("Running pipeline...", expanded=True) as status:

        def update_status(message: str):
            status.update(label=message)
            st.write(message)

        try:
            result = run_pipeline(
                resume_file=uploaded_file,
                jd_text=jd_text,
                status_callback=update_status
            )

            status.update(label="✦ Complete!", state="complete")
            st.session_state["result"] = result
            st.session_state["has_result"] = True

        except Exception as e:
            status.update(label="Pipeline failed.", state="error")
            st.error(f"Something went wrong: {str(e)}")
            st.stop()
        finally:
            st.session_state["pipeline_running"] = False


# === RESULTS ===
if st.session_state.get("has_result"):
    result = st.session_state["result"]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='display:flex; align-items:center; gap:0.75rem; margin-bottom:1.5rem;'>
        <h2 style='margin:0;'>Results</h2>
        <span class='badge'>Analysis Complete</span>
    </div>
    """, unsafe_allow_html=True)

    # === SCORE METRICS ===
    st.markdown("<div class='section-label'>Match Scores</div>", unsafe_allow_html=True)
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1: st.metric("Overall",  f"{result['review']['overall_score']}%")
    with s2: st.metric("ATS",      f"{result['review']['scores']['ats']}%")
    with s3: st.metric("Clarity",  f"{result['review']['scores']['clarity']}%")
    with s4: st.metric("Tone",     f"{result['review']['scores']['tone']}%")
    with s5: st.metric("Keywords", f"{result['review']['scores']['keyword']}%")

    st.markdown("---")

    # === SKILLS BREAKDOWN ===
    st.markdown("<div class='section-label'>Skills Breakdown</div>", unsafe_allow_html=True)

    matched_tags = "".join([f"<span class='skill-tag tag-matched'>{s}</span>"
                            for s in result["match"]["matched"] if s])
    partial_tags = "".join([f"<span class='skill-tag tag-partial'>{s}</span>"
                            for s in result["match"]["partial"] if s])
    missing_tags = "".join([f"<span class='skill-tag tag-missing'>{s}</span>"
                            for s in result["match"]["missing"] if s])

    sk1, sk2, sk3 = st.columns(3)
    with sk1:
        st.markdown(f"""
        <div class='card'>
            <div class='section-label' style='color:#34d399;'>✓ Matched</div>
            <div>{matched_tags if matched_tags else "<span style='color:#6b7280;font-size:0.85rem;'>None</span>"}</div>
        </div>
        """, unsafe_allow_html=True)
    with sk2:
        st.markdown(f"""
        <div class='card'>
            <div class='section-label' style='color:#fbbf24;'>⚡ Partial</div>
            <div>{partial_tags if partial_tags else "<span style='color:#6b7280;font-size:0.85rem;'>None</span>"}</div>
        </div>
        """, unsafe_allow_html=True)
    with sk3:
        st.markdown(f"""
        <div class='card'>
            <div class='section-label' style='color:#f87171;'>✕ Missing</div>
            <div>{missing_tags if missing_tags else "<span style='color:#6b7280;font-size:0.85rem;'>None</span>"}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # === REWRITTEN RESUME ===
    st.markdown("<div class='section-label'>Rewritten Resume</div>", unsafe_allow_html=True)

    # summary
    st.markdown("""
    <div style='font-family:Syne,sans-serif; font-size:0.85rem;
                font-weight:600; color:#9090a8; margin-bottom:0.5rem;'>
        Professional Summary
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div class='card' style='border-left: 3px solid #6c63ff;'>
        <p style='margin:0; line-height:1.7; color:#c4c4d4; font-size:0.92rem;'>
            {result["rewritten"]["summary"]}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # experience
    st.markdown("""
    <div style='font-family:Syne,sans-serif; font-size:0.85rem;
                font-weight:600; color:#9090a8; margin:1.25rem 0 0.5rem;'>
        Work Experience
    </div>
    """, unsafe_allow_html=True)
    for job in result["rewritten"]["experience"]:
        with st.expander(f"{job['title']}  ·  {job['company']}  ·  {job['duration']}"):
            for bullet in job["bullets"]:
                st.markdown(f"""
                <div style='display:flex; gap:0.6rem; margin-bottom:0.4rem;'>
                    <span style='color:#6c63ff; margin-top:0.1rem;'>▸</span>
                    <span style='font-size:0.88rem; color:#c4c4d4; line-height:1.6;'>{bullet.lstrip("-").strip()}</span>
                </div>
                """, unsafe_allow_html=True)

    # projects
    st.markdown("""
    <div style='font-family:Syne,sans-serif; font-size:0.85rem;
                font-weight:600; color:#9090a8; margin:1.25rem 0 0.5rem;'>
        Projects
    </div>
    """, unsafe_allow_html=True)
    for project in result["rewritten"]["projects"]:
        with st.expander(f"{project['name']}  ·  {project['tech']}"):
            for bullet in project["bullets"]:
                st.markdown(f"""
                <div style='display:flex; gap:0.6rem; margin-bottom:0.4rem;'>
                    <span style='color:#a78bfa; margin-top:0.1rem;'>▸</span>
                    <span style='font-size:0.88rem; color:#c4c4d4; line-height:1.6;'>{bullet.lstrip("-").strip()}</span>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # === SUGGESTIONS ===
    st.markdown("<div class='section-label'>Suggestions for Improvement</div>", unsafe_allow_html=True)
    for i, suggestion in enumerate(result["review"]["suggestions"]):
        st.markdown(f"""
        <div class='card' style='border-left: 3px solid #fbbf24; margin-bottom:0.5rem;'>
            <div style='display:flex; gap:0.75rem; align-items:flex-start;'>
                <span style='font-family:Syne,sans-serif; font-size:0.7rem; font-weight:700;
                             color:#fbbf24; background:rgba(251,191,36,0.12);
                             border:1px solid rgba(251,191,36,0.25); border-radius:4px;
                             padding:0.1rem 0.4rem; margin-top:0.1rem; flex-shrink:0;'>
                    {str(i+1).zfill(2)}
                </span>
                <span style='font-size:0.88rem; color:#c4c4d4; line-height:1.6;'>
                    {suggestion.lstrip("-").strip()}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)