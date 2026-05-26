# Analysis Workflow

## Step-by-Step Process

### 1. URL Parsing
- Extract owner/repo from various GitHub URL formats
- Support: `github.com/owner/repo`, with/without `.git`, trailing slashes

### 2. Branch Detection
- Probe common branches: `main`, `master`, `dev`, `develop`
- Use HEAD request to `raw.githubusercontent.com` to find which branch has README.md

### 3. File Fetching
- Fetch 40+ common config/doc files via raw URLs
- Parallel-safe, with timeout handling
- Track which files exist and their content

### 4. Tech Stack Detection
Two-phase approach:

**Phase 1: File-based detection**
- `requirements.txt` → Python
- `package.json` → JavaScript/Node.js
- `Dockerfile` → Docker
- `.github/workflows/*.yml` → GitHub Actions
- etc.

**Phase 2: Content-based detection**
- Parse `package.json` dependencies for React, Next.js, Vue, etc.
- Parse `requirements.txt` for Django, Flask, FastAPI, etc.
- Parse `pyproject.toml` for Poetry

### 5. README Quality Analysis
12-point weighted checklist:
- Title (15 pts)
- Description (15 pts)
- Installation (15 pts)
- Usage (10 pts)
- Features (10 pts)
- Environment Variables (5 pts)
- License (5 pts)
- Contributing (5 pts)
- Badges (5 pts)
- Screenshots (5 pts)
- API Docs (5 pts)
- Testing (5 pts)

### 6. Project Structure Scoring
Check for presence of key files:
- README (15 pts)
- License (10 pts)
- .gitignore (5 pts)
- Dependencies (10 pts)
- .env.example (8 pts)
- Dockerfile (10 pts)
- CI/CD (10 pts)
- Contributing (5 pts)
- Changelog (5 pts)
- Security (5 pts)

### 7. Composite Scoring
Four dimensions, equally weighted (25% each):
- **Documentation** — README quality
- **Structure** — File organization
- **Maintainability** — CI, Docker, changelog, security
- **Product-Readiness** — License, deps, Docker, env template

Bonus points for high stars, topics, etc.

### 8. AI Analysis
- Build comprehensive prompt with all scores and file content
- Call OpenAI API (GPT-4o-mini) with low temperature (0.3)
- Generate: summary, strengths, weaknesses, issues, roadmap, verdict

### 9. Report Assembly
- Combine static analysis + AI analysis
- Format as clean Markdown
- Include score dashboard, checklists, and metadata
- Enable download as .md or .json

## Error Handling

| Scenario | Handling |
|----------|----------|
| Invalid URL | Show error, suggest format |
| Private repo | Show "no files found" message |
| No README | Score 0, continue analysis |
| No API key | Show static analysis only, skip AI |
| API timeout | Retry once, then show partial results |
| Rate limit | Show cached results or error message |
