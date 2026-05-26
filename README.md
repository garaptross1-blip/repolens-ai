# RepoLens AI

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![AI](https://img.shields.io/badge/AI-Powered-9B59B6?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![PRs](https://img.shields.io/badge/PRs-Welcome-brightgreen)

**AI-powered GitHub repository auditor that turns any public repo into a quality report, roadmap, and improvement plan.**

RepoLens AI analyzes any public GitHub repository and generates comprehensive quality scores, tech stack detection, README analysis, security checklists, AI-powered recommendations, suggested GitHub issues, and a 7-day improvement roadmap — all in one click.

---

## 🚀 Features

- **📊 Multi-Dimensional Scoring** — Documentation, Structure, Maintainability, and Product-Readiness scores
- **🏗️ Tech Stack Detection** — Auto-detects languages, frameworks, DevOps tools, and dependencies
- **📝 README Quality Analysis** — 12-point checklist with weighted scoring
- **🔒 Security & Config Checklist** — Checks for .env templates, .gitignore, security policies, and more
- **🤖 AI Maintainer Report** — LLM-powered analysis with actionable recommendations
- **📋 Suggested GitHub Issues** — Auto-generated issues with labels
- **🗺️ 7-Day Roadmap** — Day-by-day improvement plan tailored to the repo
- **📥 Export Reports** — Download as Markdown or JSON

---

## 📸 How It Works

```
1. Paste a GitHub URL    →    2. RepoLens fetches & analyzes    →    3. Get your report
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.10+ |
| AI Engine | OpenAI API (GPT-4o-mini) |
| Data Source | GitHub Raw URLs + GitHub API |
| Parsing | requests, BeautifulSoup, regex |
| Output | Markdown + JSON |

---

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Installation

```bash
git clone https://github.com/garaptross1-blip/repolens-ai.git
cd repolens-ai

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📊 Scoring System

### README Quality (0-100)
Checks for: Title, Description, Installation, Usage, Features, Environment Variables, License, Contributing, Badges, Screenshots, API Docs, Testing.

### Project Structure (0-100)
Checks for: README, License, .gitignore, Dependencies, .env.example, Dockerfile, CI/CD, Contributing Guide, Changelog, Security Policy.

### Composite Scores
- **Documentation** — README quality weighted score
- **Structure** — File presence and organization
- **Maintainability** — CI, Docker, changelog, security policy
- **Product-Readiness** — License, deps, Docker, env template
- **Overall** — Weighted average of all dimensions

---

## 💡 Example Repos to Try

| Repository | What to Look For |
|-----------|-----------------|
| `fastapi/fastapi` | Gold standard Python project |
| `vercel/next.js` | Enterprise-grade JS framework |
| `langchain-ai/langchain` | AI/ML project structure |
| `streamlit/streamlit` | Well-documented Python tool |

---

## 📁 Project Structure

```
repolens-ai/
├── app.py                    # Streamlit main application
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template
├── README.md                 # This file
├── LICENSE                   # MIT License
├── src/
│   ├── __init__.py
│   ├── github_fetcher.py     # GitHub file fetching & URL parsing
│   ├── analyzer.py           # Tech stack, README, structure analysis
│   ├── scoring.py            # Composite scoring engine
│   ├── ai_engine.py          # LLM-powered analysis (OpenAI/Groq)
│   └── report_builder.py     # Markdown report assembly
├── examples/
│   └── sample_report.md      # Example output report
├── assets/
│   └── banner.png            # Project banner
└── docs/
    ├── architecture.md       # System architecture
    └── workflow.md            # Analysis workflow
```

---

## 🗺️ Roadmap

- [x] GitHub raw file fetching
- [x] Tech stack detection
- [x] README quality analysis
- [x] Multi-dimensional scoring
- [x] AI-powered analysis
- [x] Markdown & JSON export
- [ ] GitHub API integration (issues, PRs)
- [ ] Batch repository comparison
- [ ] Local LLM support (Ollama)
- [ ] GitHub Action for CI/CD integration
- [ ] Repository trend tracking
- [ ] Custom scoring weights
- [ ] API endpoint for programmatic access

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# Fork the repo
git clone https://github.com/garaptross1-blip/repolens-ai.git
cd repolens-ai

# Create a feature branch
git checkout -b feature/your-feature

# Make your changes and test
streamlit run app.py

# Submit a PR
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [OpenAI](https://openai.com/) for the GPT API
- [GitHub API](https://docs.github.com/en/rest) for repository data
- The open-source community for inspiration

---

<div align="center">

**Built with 🧠 by developers, for developers**

[Report Bug](https://github.com/garaptross1-blip/repolens-ai/issues) · [Request Feature](https://github.com/garaptross1-blip/repolens-ai/issues) · [Star this Repo](https://github.com/garaptross1-blip/repolens-ai)

</div>
