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
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0;
    }
    .main-header p {
        color: #888;
        font-size: 1.1rem;
    }
    .score-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #333;
    }
    .score-card h2 {
        font-size: 2.5rem;
        margin: 0;
    }
    .score-card p {
        color: #aaa;
        margin: 0;
    }
    .stMetric > div {
        background: #1a1a2e;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>🧠 RepoLens AI</h1>
    <p>AI-powered GitHub repository auditor for developers, founders, and open-source maintainers</p>
</div>
""", unsafe_allow_html=True)


# ── Input Section ────────────────────────────────────────────────────

col_input, col_btn = st.columns([4, 1])

with col_input:
    repo_url = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/fastapi/fastapi",
        label_visibility="collapsed",
    )

with col_btn:
    analyze_clicked = st.button("🔍 Analyze", type="primary", use_container_width=True)

# ── Examples ─────────────────────────────────────────────────────────

with st.expander("💡 Try these examples"):
    example_cols = st.columns(4)
    examples = [
        ("FastAPI", "https://github.com/fastapi/fastapi"),
        ("Next.js", "https://github.com/vercel/next.js"),
        ("LangChain", "https://github.com/langchain-ai/langchain"),
        ("Streamlit", "https://github.com/streamlit/streamlit"),
    ]
    for i, (name, url) in enumerate(examples):
        with example_cols[i]:
            if st.button(f"📌 {name}", key=f"ex_{i}", use_container_width=True):
                repo_url = url
                analyze_clicked = True


# ── Analysis Pipeline ────────────────────────────────────────────────

if analyze_clicked and repo_url:
    # Validate URL
    try:
        owner, repo_name = parse_github_url(repo_url)
    except ValueError as e:
        st.error(str(e))
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

    # Step 3: Analysis
    files = repo_data["files"]

    stack = detect_stack(files)

    readme_content = files.get("README.md", files.get("README.rst", ""))
    readme_analysis = analyze_readme(readme_content) if readme_content else {
        "score": 0,
        "checks": {},
        "total_weight": 100,
        "earned_weight": 0,
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

    # ── Display: Score Dashboard ─────────────────────────────────────

    st.markdown("---")

    overall = scores["overall"]
    grade = get_score_grade(overall)
    emoji = get_score_emoji(overall)

    score_cols = st.columns(5)
    score_items = [
        ("Overall", overall, emoji),
        ("Documentation", scores["documentation"], get_score_emoji(scores["documentation"])),
        ("Structure", scores["structure"], get_score_emoji(scores["structure"])),
        ("Maintainability", scores["maintainability"], get_score_emoji(scores["maintainability"])),
        ("Product-Ready", scores["product_readiness"], get_score_emoji(scores["product_readiness"])),
    ]

    for i, (label, score, em) in enumerate(score_items):
        with score_cols[i]:
            st.metric(
                label=f"{em} {label}",
                value=f"{score}/100",
                help=f"Grade: {get_score_grade(score)}",
            )

    # ── Display: Repo Info ───────────────────────────────────────────

    if repo_info:
        st.markdown("---")
        info_cols = st.columns(6)
        info_items = [
            ("⭐ Stars", f"{repo_info.get('stars', 0):,}"),
            ("🍴 Forks", f"{repo_info.get('forks', 0):,}"),
            ("📋 Issues", str(repo_info.get('open_issues', 0))),
            ("💻 Language", repo_info.get('language', 'N/A')),
            ("📄 License", repo_info.get('license', 'N/A')),
            ("📦 Size", f"{repo_info.get('size_kb', 0):,} KB"),
        ]
        for i, (label, value) in enumerate(info_items):
            with info_cols[i]:
                st.metric(label=label, value=value)

    # ── Display: Tech Stack ──────────────────────────────────────────

    st.markdown("---")
    st.subheader("🏗️ Detected Tech Stack")
    if stack:
        stack_html = " ".join(
            f'<span style="background:#1a1a2e;border:1px solid #444;'
            f'border-radius:20px;padding:4px 12px;margin:2px;'
            f'display:inline-block;font-size:0.9rem;">{tech}</span>'
            for tech in stack
        )
        st.markdown(stack_html, unsafe_allow_html=True)
    else:
        st.info("No tech stack detected from config files.")

    # ── Display: README Quality ──────────────────────────────────────

    st.markdown("---")
    readme_cols = st.columns([1, 2])

    with readme_cols[0]:
        st.subheader("📝 README Quality")
        st.metric("Score", f"{readme_analysis['score']}/100")

    with readme_cols[1]:
        st.subheader("Checklist")
        for key, check in readme_analysis["checks"].items():
            icon = "✅" if check["found"] else "❌"
            st.markdown(f"{icon} **{check['label']}** — {check['weight']} pts")

    # ── Display: Project Structure ───────────────────────────────────

    st.markdown("---")
    struct_cols = st.columns([1, 2])

    with struct_cols[0]:
        st.subheader("🗂️ Project Structure")
        st.metric("Score", f"{structure_analysis['score']}/100")

    with struct_cols[1]:
        st.subheader("Breakdown")
        for file_name, check in structure_analysis["checks"].items():
            icon = "✅" if check["exists"] else "❌"
            st.markdown(f"{icon} **{check['label']}** (`{file_name}`) — {check['earned']}/{check['weight']} pts")

    # ── Display: Security Checklist ──────────────────────────────────

    st.markdown("---")
    st.subheader("🔒 Security & Config Checklist")
    for item in security_items:
        icon = "✅" if item["present"] else "⚠️"
        st.markdown(f"{icon} {item['description']} (`{item['file']}`)")

    # ── Display: Files Detected ──────────────────────────────────────

    with st.expander(f"📁 All Files Detected ({len(files)})"):
        for f in sorted(files.keys()):
            size = len(files[f])
            st.code(f"{f}  ({size:,} chars)", language=None)

    # ── AI Analysis ──────────────────────────────────────────────────

    st.markdown("---")
    st.subheader("🤖 AI Maintainer Analysis")

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

    st.markdown(ai_report)

    # ── Download Report ──────────────────────────────────────────────

    st.markdown("---")

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

    dl_cols = st.columns([1, 1, 2])

    with dl_cols[0]:
        st.download_button(
            label="📥 Download Full Report (.md)",
            data=full_report,
            file_name=f"repolens_{owner}_{repo_name}.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )

    with dl_cols[1]:
        import json
        json_data = json.dumps({
            "repository": f"{owner}/{repo_name}",
            "scores": scores,
            "stack": stack,
            "readme_score": readme_analysis["score"],
            "structure_score": structure_analysis["score"],
            "files_detected": list(files.keys()),
        }, indent=2)

        st.download_button(
            label="📥 Download Scores (.json)",
            data=json_data,
            file_name=f"repolens_{owner}_{repo_name}.json",
            mime="application/json",
            use_container_width=True,
        )

# ── Footer ───────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    """
    <div style="text-align:center;color:#666;padding:1rem;">
        <b>RepoLens AI</b> — Built with Python, Streamlit & OpenAI<br>
        <small>Analyze any public GitHub repository in seconds</small>
    </div>
    """,
    unsafe_allow_html=True,
)
