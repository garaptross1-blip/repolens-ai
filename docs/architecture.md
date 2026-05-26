# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                     │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │  Input   │→│ Analysis  │→│  Scores   │→│  Report   │ │
│  │  URL     │  │  Display  │  │ Dashboard │  │ Download │ │
│  └─────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                   Analysis Pipeline                       │
│                                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │ GitHub       │───→│  Analyzer    │───→│  Scoring   │ │
│  │ Fetcher      │    │  Module      │    │  Engine    │ │
│  └──────┬───────┘    └──────────────┘    └────────────┘ │
│         │                                                │
│  ┌──────▼───────┐    ┌──────────────┐    ┌────────────┐ │
│  │ GitHub API   │    │  AI Engine   │───→│  Report    │ │
│  │ (metadata)   │    │  (OpenAI)    │    │  Builder   │ │
│  └──────────────┘    └──────────────┘    └────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### `github_fetcher.py`
- Parse GitHub URLs (multiple formats)
- Fetch raw files via `raw.githubusercontent.com`
- Detect default branch (main/master/dev)
- Fetch repo metadata via GitHub API (stars, forks, issues)

### `analyzer.py`
- Tech stack detection (file-based + content-based)
- README quality analysis (12-point weighted checklist)
- Project structure analysis (file presence scoring)
- Security/config checklist generation

### `scoring.py`
- Composite scoring: Documentation, Structure, Maintainability, Product-Readiness
- Weighted average for Overall score
- Letter grade and emoji mapping

### `ai_engine.py`
- Build analysis prompt with all context
- OpenAI API integration (GPT-4o-mini)
- Groq API fallback (Llama 3.3)
- Error handling for missing API keys

### `report_builder.py`
- Assemble complete Markdown report
- Include all analysis sections
- Timestamp and metadata

## Data Flow

```
GitHub URL
    │
    ├──→ Raw File Fetcher ──→ File Contents
    │                              │
    ├──→ GitHub API ──→ Metadata   │
    │                     │        │
    │                     ▼        ▼
    │              ┌──────────────────┐
    │              │    Analyzer      │
    │              │  - Stack detect  │
    │              │  - README score  │
    │              │  - Structure     │
    │              │  - Security      │
    │              └────────┬─────────┘
    │                       │
    │                       ▼
    │              ┌──────────────────┐
    │              │    Scoring       │
    │              │  - Composite     │
    │              │  - Grades        │
    │              └────────┬─────────┘
    │                       │
    │                       ▼
    │              ┌──────────────────┐
    │              │   AI Engine      │
    │              │  - Prompt build  │
    │              │  - LLM call      │
    │              └────────┬─────────┘
    │                       │
    │                       ▼
    │              ┌──────────────────┐
    │              │  Report Builder  │
    │              │  - Markdown      │
    │              │  - JSON          │
    │              └──────────────────┘
    │
    ▼
 Streamlit UI
```
