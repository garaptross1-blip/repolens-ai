"""
RepoLens AI — GitHub Repository Fetcher
Fetches common config/doc files from public GitHub repositories via raw URLs.
"""

import re
import requests
from typing import Optional

RAW_BASE = "https://raw.githubusercontent.com"

COMMON_FILES = [
    "README.md",
    "README.rst",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "LICENSE",
    "LICENSE.md",
    ".env.example",
    ".env.sample",
    ".gitignore",
    "Makefile",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "composer.json",
    "pom.xml",
    "build.gradle",
    "Gemfile",
    "CMakeLists.txt",
    "tsconfig.json",
    "jest.config.js",
    "vitest.config.ts",
    ".eslintrc.json",
    ".prettierrc",
    "CONTRIBUTING.md",
    "CHANGELOG.md",
    "SECURITY.md",
    ".github/workflows/ci.yml",
    ".github/workflows/main.yml",
    ".github/workflows/test.yml",
    ".github/workflows/deploy.yml",
    ".github/workflows/build.yml",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/CODEOWNERS",
    "docs/README.md",
    "docs/index.md",
]

BRANCH_CANDIDATES = ["main", "master", "dev", "develop"]


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract owner and repo name from a GitHub URL."""
    url = url.strip().rstrip("/")

    # Handle various URL formats
    patterns = [
        r"github\.com/([^/]+)/([^/\?#]+)",
        r"github\.com/([^/]+)/([^/\?#]+)\.git",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2).replace(".git", "")
            return owner, repo

    raise ValueError(
        f"Invalid GitHub URL: {url}\n"
        "Expected format: https://github.com/owner/repo"
    )


def fetch_raw_file(
    owner: str,
    repo: str,
    branch: str,
    path: str,
    timeout: int = 10,
) -> Optional[str]:
    """Fetch a single file from GitHub raw content."""
    url = f"{RAW_BASE}/{owner}/{repo}/{branch}/{path}"
    try:
        resp = requests.get(url, timeout=timeout, headers={
            "User-Agent": "RepoLens-AI/1.0"
        })
        if resp.status_code == 200:
            return resp.text
    except requests.RequestException:
        pass
    return None


def detect_default_branch(owner: str, repo: str) -> str:
    """Try to detect the default branch by probing common names."""
    for branch in BRANCH_CANDIDATES:
        test_url = f"{RAW_BASE}/{owner}/{repo}/{branch}/README.md"
        try:
            resp = requests.head(test_url, timeout=8, headers={
                "User-Agent": "RepoLens-AI/1.0"
            })
            if resp.status_code == 200:
                return branch
        except requests.RequestException:
            continue
    return "main"  # fallback


def fetch_repo_files(repo_url: str) -> dict:
    """
    Fetch all common files from a GitHub repository.
    Returns dict with owner, repo, branch, and files content.
    """
    owner, repo = parse_github_url(repo_url)
    branch = detect_default_branch(owner, repo)

    found_files = {}

    for file_path in COMMON_FILES:
        content = fetch_raw_file(owner, repo, branch, file_path)
        if content and len(content.strip()) > 0:
            found_files[file_path] = content

    return {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "url": f"https://github.com/{owner}/{repo}",
        "files": found_files,
        "files_count": len(found_files),
    }


def fetch_repo_info_api(owner: str, repo: str) -> Optional[dict]:
    """
    Optional: Fetch repo metadata via GitHub public API (no auth needed).
    Returns stars, forks, issues, description, language, etc.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "RepoLens-AI/1.0",
            "Accept": "application/vnd.github.v3+json",
        })
        if resp.status_code == 200:
            data = resp.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "description": data.get("description", ""),
                "language": data.get("language", ""),
                "created_at": data.get("created_at", ""),
                "updated_at": data.get("updated_at", ""),
                "topics": data.get("topics", []),
                "default_branch": data.get("default_branch", "main"),
                "size_kb": data.get("size", 0),
                "license": (
                    data.get("license", {}).get("spdx_id", "Unknown")
                    if data.get("license") else "None"
                ),
                "homepage": data.get("homepage", ""),
                "archived": data.get("archived", False),
            }
    except requests.RequestException:
        pass
    return None
