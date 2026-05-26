"""
RepoLens AI — AI Engine
Generates intelligent analysis reports using LLM (OpenAI / Groq / local).
"""

import os
from dotenv import load_dotenv

load_dotenv()


def build_analysis_prompt(
    repo_name: str,
    files: dict,
    stack: list[str],
    readme_score: int,
    structure_score: int,
    scores: dict,
    repo_info: dict | None = None,
) -> str:
    """Build the analysis prompt for the LLM."""

    readme = files.get("README.md", files.get("README.rst", ""))
    if len(readme) > 8000:
        readme = readme[:8000] + "\n\n[... truncated ...]"

    # Build file tree summary
    file_list = "\n".join(f"- {f}" for f in sorted(files.keys()))

    # Repo metadata section
    meta_section = ""
    if repo_info:
        meta_section = f"""
Repository Metadata:
- Stars: {repo_info.get('stars', 'N/A')}
- Forks: {repo_info.get('forks', 'N/A')}
- Open Issues: {repo_info.get('open_issues', 'N/A')}
- Primary Language: {repo_info.get('language', 'N/A')}
- License: {repo_info.get('license', 'N/A')}
- Last Updated: {repo_info.get('updated_at', 'N/A')}
- Topics: {', '.join(repo_info.get('topics', [])) or 'None'}
"""

    return f"""You are a senior software engineer, open-source maintainer, and DevOps expert.
Analyze this GitHub repository and provide actionable feedback.

Repository: {repo_name}
{meta_section}
Detected Tech Stack:
{', '.join(stack) if stack else 'Not detected'}

Files Found ({len(files)}):
{file_list}

Scores:
- README Quality: {readme_score}/100
- Project Structure: {structure_score}/100
- Documentation: {scores['documentation']}/100
- Maintainability: {scores['maintainability']}/100
- Product-Readiness: {scores['product_readiness']}/100
- Overall: {scores['overall']}/100

README Content:
```
{readme}
```

Provide your analysis in the following Markdown structure. Be specific, actionable, and honest.

## 📋 Project Summary
(2-3 sentences: what it does, who it's for, current state)

## 🏗️ Tech Stack Analysis
(Break down the detected stack, note any version concerns or missing pieces)

## 💪 Strengths
(What the project does well — be specific)

## ⚠️ Weaknesses & Gaps
(What's missing or could be improved — be specific and prioritized)

## 🔒 Security & Config Review
(Any concerns about secrets, env handling, dependencies)

## 📝 Suggested GitHub Issues
(Create 5-7 specific, actionable issues with labels)
Format each as:
- **[Label]** Issue title — Description

## 🗺️ 7-Day Improvement Roadmap
(Day-by-day plan, each day with a concrete deliverable)
- Day 1: ...
- Day 2: ...
(etc.)

## 🎯 Portfolio Readiness Assessment
(Is this portfolio-ready? What would make it stand out?)

## 📊 Final Verdict
(One paragraph summary with specific recommendations)
"""


def generate_ai_report(
    repo_name: str,
    files: dict,
    stack: list[str],
    readme_score: int,
    structure_score: int,
    scores: dict,
    repo_info: dict | None = None,
) -> str:
    """Generate AI analysis report using OpenAI API."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "⚠️ **AI Analysis Unavailable**\n\n"
            "No `OPENAI_API_KEY` found in environment.\n"
            "Create a `.env` file with your API key to enable AI analysis.\n\n"
            "```\nOPENAI_API_KEY=sk-your-key-here\n```"
        )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        prompt = build_analysis_prompt(
            repo_name=repo_name,
            files=files,
            stack=stack,
            readme_score=readme_score,
            structure_score=structure_score,
            scores=scores,
            repo_info=repo_info,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict but helpful senior software engineer "
                        "and open-source maintainer. Be specific, actionable, "
                        "and honest in your assessments. Use Markdown formatting."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4000,
        )

        return response.choices[0].message.content

    except ImportError:
        return "⚠️ OpenAI package not installed. Run: `pip install openai`"
    except Exception as e:
        return f"⚠️ AI Analysis Error: {str(e)}"


def generate_with_groq(
    repo_name: str,
    files: dict,
    stack: list[str],
    readme_score: int,
    structure_score: int,
    scores: dict,
    repo_info: dict | None = None,
) -> str:
    """Alternative: Generate using Groq API (faster, free tier)."""

    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return generate_ai_report(
            repo_name, files, stack, readme_score,
            structure_score, scores, repo_info
        )

    try:
        import requests

        prompt = build_analysis_prompt(
            repo_name=repo_name,
            files=files,
            stack=stack,
            readme_score=readme_score,
            structure_score=structure_score,
            scores=scores,
            repo_info=repo_info,
        )

        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a strict but helpful senior software engineer."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 4000,
            },
            timeout=60,
        )

        if resp.status_code == 200:
            return resp.json()["choices"][0]["message"]["content"]
        else:
            # Fallback to OpenAI
            return generate_ai_report(
                repo_name, files, stack, readme_score,
                structure_score, scores, repo_info
            )

    except Exception:
        return generate_ai_report(
            repo_name, files, stack, readme_score,
            structure_score, scores, repo_info
        )
