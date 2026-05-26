"""
🧠 RepoLens AI — AI-Powered GitHub Repository Auditor

Analyzes any public GitHub repository and generates:
- Quality report with scores
- Tech stack detection
- README quality analysis
- Security checklist
- AI-powered recommendations
- Suggested GitHub issues
- 7-day improvement roadmap
- Downloadable Markdown report

Usage:
    streamlit run app.py
"""

import json
import streamlit as st

from src.github_fetcher import fetch_repo_files, fetch_repo_info_api, parse_github_url
from src.analyzer import detect_stack, analyze_readme, analyze_structure, security_checklist
from src.scoring import calculate_composite_scores, get_score_grade, get_score_emoji
from src.ai_engine import generate_ai_report
from src.report_builder import build_full_report


# ── Page Config ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="RepoLens AI — GitHub Repository Auditor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ───────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Global font */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* Hero section */
    .hero {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 50%, #34d399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        letter-spacing: -1px;
    }
    .hero p {
        color: #8b949e;
        font-size: 1.15rem;
        margin-bottom: 0.5rem;
    }
    .hero .badges {
        margin-top: 0.8rem;
    }

    /* Score cards */
    .score-container {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
        margin: 1.5rem 0;
    }
    .score-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2333 100%);
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 1.2rem 1.8rem;
        text-align: center;
        min-width: 140px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .score-card:hover {
        transform: translateY(-2px);
        border-color: #58a6ff;
    }
    .score-card .score-value {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
    .score-card .score-label {
        font-size: 0.75rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
    }
    .score-card .score-grade {
        font-size: 0.85rem;
        margin-top: 0.2rem;
    }
    .score-green { color: #3fb950; }
    .score-yellow { color: #d29922; }
    .score-orange { color: #db6d28; }
    .score-red { color: #f85149; }

    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #21262d;
    }
    .section-header h2 {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e6edf3;
        margin: 0;
    }

    /* Stack pills */
    .stack-pills {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin: 0.5rem 0;
    }
    .stack-pill {
        background: rgba(56, 139, 253, 0.1);
        border: 1px solid rgba(56, 139, 253, 0.3);
        border-radius: 20px;
        padding: 0.35rem 1rem;
        font-size: 0.85rem;
        color: #58a6ff;
        font-weight: 500;
    }

    /* Checklist items */
    .check-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 0;
        font-size: 0.9rem;
    }
    .check-pass { color: #3fb950; }
    .check-fail { color: #f85149; }

    /* Repo info bar */
    .info-bar {
        display: flex;
        gap: 2rem;
        justify-content: center;
        flex-wrap: wrap;
        padding: 1rem;
        background: #161b22;
        border-radius: 12px;
        border: 1px solid #21262d;
        margin: 1rem 0;
    }
    .info-item {
        text-align: center;
    }
    .info-item .info-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e6edf3;
    }
    .info-item .info-label {
        font-size: 0.7rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Report container */
    .report-container {
        background: #0d1117;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }

    /* Download buttons */
    .download-row {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0 1rem 0;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: #0d1117;
        border: 2px solid #30363d;
        border-radius: 12px;
        color: #e6edf3;
        font-size: 1rem;
        padding: 0.8rem 1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 2px rgba(56, 139, 253, 0.2);
    }

    /* Example buttons */
    .example-grid {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        justify-content: center;
        margin: 0.5rem 0 1.5rem 0;
    }
    .example-chip {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0.4rem 0.8rem;
        font-size: 0.8rem;
        color: #8b949e;
        cursor: pointer;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #484f58;
        font-size: 0.85rem;
        border-top: 1px solid #21262d;
        margin-top: 3rem;
    }
    .footer a {
        color: #58a6ff;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)


# ── Hero Section ─────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <h1>🧠 RepoLens AI</h1>
    <p>AI-powered GitHub repository auditor for developers, founders, and open-source maintainers</p>
    <div class="badges">
        <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white" />
        <img src="https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white" />
        <img src="https://img.shields.io/badge/AI-Powered-10A37F?style=flat&logo=openai&logoColor=white" />
        <img src="https://img.shields.io/badge/License-MIT-2EA043?style=flat" />
    </div>
</div>
""", unsafe_allow_html=True)


# ── Input Section ────────────────────────────────────────────────────

col_input, col_btn = st.columns([5, 1])

with col_input:
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/fastapi/fastapi",
        label_visibility="collapsed",
    )

with col_btn:
    analyze_clicked = st.button("🔍 Analyze", type="primary", use_container_width=True)

# ── Example Repos ────────────────────────────────────────────────────

st.markdown("""
<div class="example-grid">
    <span style="color:#484f58;font-size:0.8rem;line-height:2;">Try:</span>
</div>
""", unsafe_allow_html=True)

example_cols = st.columns(6)
examples = [
    ("⚡ FastAPI", "https://github.com/fastapi/fastapi"),
    ("▲ Next.js", "https://github.com/vercel/next.js"),
    ("🦜 LangChain", "https://github.com/langchain-ai/langchain"),
    ("🎨 Streamlit", "https://github.com/streamlit/streamlit"),
    ("🔥 Hono", "https://github.com/honojs/hono"),
    ("🦀 Tauri", "https://github.com/tauri-apps/tauri"),
]
for i, (name, url) in enumerate(examples):
    with example_cols[i]:
        if st.button(name, key=f"ex_{i}", use_container_width=True):
            repo_url = url
            analyze_clicked = True


# ── Analysis Pipeline ────────────────────────────────────────────────

if analyze_clicked and repo_url:
    # Validate URL
    try:
        owner, repo_name = parse_github_url(repo_url)
    except ValueError as e:
        st.error(f"❌ {e}")
        st.stop()

    # Step 1: Fetch files
    with st.spinner(f"📡 Fetching files from `{owner}/{repo_name}`..."):
        repo_data = fetch_repo_files(repo_url)

    if not repo_data["files"]:
        st.error(
            "❌ No supported files found. "
            "Make sure the repository is **public** and contains standard config files."
        )
        st.stop()

    # Step 2: Fetch metadata
    with st.spinner("📊 Fetching repository metadata..."):
        repo_info = fetch_repo_info_api(owner, repo_name)

    # Step 3: Run analysis pipeline
    files = repo_data["files"]

    stack = detect_stack(files)

    readme_content = files.get("README.md", files.get("README.rst", ""))
    readme_analysis = analyze_readme(readme_content) if readme_content else {
        "score": 0, "checks": {}, "total_weight": 100, "earned_weight": 0,
    }

    structure_analysis = analyze_structure(files)
    security_items = security_checklist(files)

    scores = calculate_composite_scores(
        readme_analysis=readme_analysis,
        structure_analysis=structure_analysis,
        stack=stack,
        files=files,
        repo_info=repo_info,
    )

    # ── Score Dashboard ──────────────────────────────────────────────

    overall = scores["overall"]
    grade = get_score_grade(overall)

    def score_color(s):
        if s >= 80: return "score-green"
        elif s >= 60: return "score-yellow"
        elif s >= 40: return "score-orange"
        return "score-red"

    st.markdown(f"""
    <div class="score-container">
        <div class="score-card">
            <div class="score-value {score_color(overall)}">{overall}</div>
            <div class="score-label">Overall</div>
            <div class="score-grade {score_color(overall)}">{grade}</div>
        </div>
        <div class="score-card">
            <div class="score-value {score_color(scores['documentation'])}">{scores['documentation']}</div>
            <div class="score-label">Documentation</div>
            <div class="score-grade {score_color(scores['documentation'])}">{get_score_grade(scores['documentation'])}</div>
        </div>
        <div class="score-card">
            <div class="score-value {score_color(scores['structure'])}">{scores['structure']}</div>
            <div class="score-label">Structure</div>
            <div class="score-grade {score_color(scores['structure'])}">{get_score_grade(scores['structure'])}</div>
        </div>
        <div class="score-card">
            <div class="score-value {score_color(scores['maintainability'])}">{scores['maintainability']}</div>
            <div class="score-label">Maintainability</div>
            <div class="score-grade {score_color(scores['maintainability'])}">{get_score_grade(scores['maintainability'])}</div>
        </div>
        <div class="score-card">
            <div class="score-value {score_color(scores['product_readiness'])}">{scores['product_readiness']}</div>
            <div class="score-label">Product-Ready</div>
            <div class="score-grade {score_color(scores['product_readiness'])}">{get_score_grade(scores['product_readiness'])}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Repo Info Bar ────────────────────────────────────────────────

    if repo_info:
        topics_html = ""
        if repo_info.get("topics"):
            topics_html = " ".join(
                f'<span style="background:rgba(56,139,253,0.1);border:1px solid rgba(56,139,253,0.3);'
                f'border-radius:12px;padding:2px 8px;font-size:0.7rem;color:#58a6ff;margin-right:4px;">{t}</span>'
                for t in repo_info["topics"][:8]
            )

        st.markdown(f"""
        <div class="info-bar">
            <div class="info-item">
                <div class="info-value">⭐ {repo_info.get('stars', 0):,}</div>
                <div class="info-label">Stars</div>
            </div>
            <div class="info-item">
                <div class="info-value">🍴 {repo_info.get('forks', 0):,}</div>
                <div class="info-label">Forks</div>
            </div>
            <div class="info-item">
                <div class="info-value">📋 {repo_info.get('open_issues', 0)}</div>
                <div class="info-label">Issues</div>
            </div>
            <div class="info-item">
                <div class="info-value">💻 {repo_info.get('language', 'N/A')}</div>
                <div class="info-label">Language</div>
            </div>
            <div class="info-item">
                <div class="info-value">📄 {repo_info.get('license', 'N/A')}</div>
                <div class="info-label">License</div>
            </div>
            <div class="info-item">
                <div class="info-value">📦 {repo_info.get('size_kb', 0):,} KB</div>
                <div class="info-label">Size</div>
            </div>
        </div>
        {f'<div style="text-align:center;margin-top:0.5rem;">{topics_html}</div>' if topics_html else ''}
        """, unsafe_allow_html=True)

    # ── Tech Stack ───────────────────────────────────────────────────

    st.markdown('<div class="section-header"><h2>🏗️ Detected Tech Stack</h2></div>', unsafe_allow_html=True)

    if stack:
        pills = "".join(f'<span class="stack-pill">{tech}</span>' for tech in stack)
        st.markdown(f'<div class="stack-pills">{pills}</div>', unsafe_allow_html=True)
    else:
        st.info("No tech stack detected from config files.")

    # ── Two-column: README + Structure ───────────────────────────────

    col_readme, col_struct = st.columns(2)

    with col_readme:
        st.markdown('<div class="section-header"><h2>📝 README Quality</h2></div>', unsafe_allow_html=True)

        r_score = readme_analysis["score"]
        st.markdown(f"""
        <div style="text-align:center;margin:1rem 0;">
            <span style="font-size:3rem;font-weight:800;" class="{score_color(r_score)}">{r_score}</span>
            <span style="font-size:1.2rem;color:#8b949e;">/100</span>
            <span style="font-size:1rem;margin-left:0.5rem;" class="{score_color(r_score)}">{get_score_grade(r_score)}</span>
        </div>
        """, unsafe_allow_html=True)

        for key, check in readme_analysis["checks"].items():
            icon = "✅" if check["found"] else "❌"
            color = "#3fb950" if check["found"] else "#f85149"
            st.markdown(
                f'<div class="check-item"><span style="color:{color}">{icon}</span> '
                f'<span>{check["label"]}</span> '
                f'<span style="color:#484f58;font-size:0.75rem;margin-left:auto;">{check["weight"]}pts</span></div>',
                unsafe_allow_html=True,
            )

    with col_struct:
        st.markdown('<div class="section-header"><h2>🗂️ Project Structure</h2></div>', unsafe_allow_html=True)

        s_score = structure_analysis["score"]
        st.markdown(f"""
        <div style="text-align:center;margin:1rem 0;">
            <span style="font-size:3rem;font-weight:800;" class="{score_color(s_score)}">{s_score}</span>
            <span style="font-size:1.2rem;color:#8b949e;">/100</span>
            <span style="font-size:1rem;margin-left:0.5rem;" class="{score_color(s_score)}">{get_score_grade(s_score)}</span>
        </div>
        """, unsafe_allow_html=True)

        for file_name, check in structure_analysis["checks"].items():
            icon = "✅" if check["exists"] else "❌"
            color = "#3fb950" if check["exists"] else "#f85149"
            st.markdown(
                f'<div class="check-item"><span style="color:{color}">{icon}</span> '
                f'<span>{check["label"]}</span> '
                f'<span style="color:#484f58;font-size:0.75rem;margin-left:auto;">{check["earned"]}/{check["weight"]}pts</span></div>',
                unsafe_allow_html=True,
            )

    # ── Security Checklist ───────────────────────────────────────────

    st.markdown('<div class="section-header"><h2>🔒 Security & Config</h2></div>', unsafe_allow_html=True)

    sec_cols = st.columns(len(security_items))
    for i, item in enumerate(security_items):
        with sec_cols[i]:
            icon = "✅" if item["present"] else "⚠️"
            border_color = "#238636" if item["present"] else "#9e6a03"
            bg_color = "rgba(35,134,54,0.08)" if item["present"] else "rgba(158,106,3,0.08)"
            st.markdown(f"""
            <div style="background:{bg_color};border:1px solid {border_color}40;border-radius:10px;
                        padding:0.8rem;text-align:center;min-height:80px;display:flex;
                        flex-direction:column;justify-content:center;align-items:center;">
                <div style="font-size:1.5rem;">{icon}</div>
                <div style="font-size:0.75rem;color:#8b949e;margin-top:0.3rem;">{item['file']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Files Detected ───────────────────────────────────────────────

    with st.expander(f"📁 All Files Detected ({len(files)})", expanded=False):
        file_cols = st.columns(3)
        sorted_files = sorted(files.keys())
        for i, f in enumerate(sorted_files):
            with file_cols[i % 3]:
                size = len(files[f])
                st.markdown(
                    f'<div style="font-size:0.8rem;padding:0.2rem 0;font-family:monospace;">'
                    f'<span style="color:#58a6ff;">📄</span> {f} '
                    f'<span style="color:#484f58;">({size:,} chars)</span></div>',
                    unsafe_allow_html=True,
                )

    # ── AI Analysis ──────────────────────────────────────────────────

    st.markdown('<div class="section-header"><h2>🤖 AI Maintainer Analysis</h2></div>', unsafe_allow_html=True)

    with st.spinner("🧠 Generating AI analysis... (this may take 15-30 seconds)"):
        ai_report = generate_ai_report(
            repo_name=f"{owner}/{repo_name}",
            files=files,
            stack=stack,
            readme_score=readme_analysis["score"],
            structure_score=structure_analysis["score"],
            scores=scores,
            repo_info=repo_info,
        )

    st.markdown(f'<div class="report-container">', unsafe_allow_html=True)
    st.markdown(ai_report)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Download Section ─────────────────────────────────────────────

    st.markdown('<div class="section-header"><h2>📥 Export Report</h2></div>', unsafe_allow_html=True)

    full_report = build_full_report(
        repo_data=repo_data,
        stack=stack,
        readme_analysis=readme_analysis,
        structure_analysis=structure_analysis,
        scores=scores,
        security_items=security_items,
        repo_info=repo_info,
        ai_report=ai_report,
    )

    json_data = json.dumps({
        "repository": f"{owner}/{repo_name}",
        "url": repo_data["url"],
        "scores": scores,
        "stack": stack,
        "readme_score": readme_analysis["score"],
        "structure_score": structure_analysis["score"],
        "files_detected": list(files.keys()),
        "security_checklist": security_items,
    }, indent=2)

    dl1, dl2, dl3 = st.columns([1, 1, 2])

    with dl1:
        st.download_button(
            label="📄 Markdown Report",
            data=full_report,
            file_name=f"repolens_{owner}_{repo_name}.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )

    with dl2:
        st.download_button(
            label="📊 JSON Scores",
            data=json_data,
            file_name=f"repolens_{owner}_{repo_name}.json",
            mime="application/json",
            use_container_width=True,
        )


# ── Footer ───────────────────────────────────────────────────────────

st.markdown("""
<div class="footer">
    <b>RepoLens AI</b> — Built with Python, Streamlit & OpenAI<br>
    <small>Analyze any public GitHub repository in seconds</small><br>
    <a href="https://github.com/garaptross1-blip/repolens-ai">⭐ Star on GitHub</a>
</div>
""", unsafe_allow_html=True)
