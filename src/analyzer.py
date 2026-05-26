"""
RepoLens AI — Repository Analyzer
Detects tech stack, analyzes README quality, and inspects project structure.
"""

import json
import re
from typing import Optional


# ── Tech Stack Detection ─────────────────────────────────────────────

STACK_SIGNALS = {
    # Languages (by config file presence)
    "Python": ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "Pipfile"],
    "JavaScript": ["package.json"],
    "TypeScript": ["tsconfig.json"],
    "Go": ["go.mod"],
    "Rust": ["Cargo.toml"],
    "PHP": ["composer.json"],
    "Java": ["pom.xml", "build.gradle"],
    "Ruby": ["Gemfile"],
    "C/C++": ["CMakeLists.txt"],

    # Frameworks (detected from package.json content)
    "React": ["react"],
    "Next.js": ["next"],
    "Vue.js": ["vue"],
    "Nuxt.js": ["nuxt"],
    "Angular": ["angular"],
    "Svelte": ["svelte"],
    "Express": ["express"],
    "Fastify": ["fastify"],
    "NestJS": ["@nestjs"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Streamlit": ["streamlit"],

    # DevOps & Infra
    "Docker": ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"],
    "GitHub Actions": [
        ".github/workflows/ci.yml",
        ".github/workflows/main.yml",
        ".github/workflows/test.yml",
        ".github/workflows/deploy.yml",
        ".github/workflows/build.yml",
    ],

    # Testing
    "Jest": ["jest.config.js", "jest.config.ts"],
    "Vitest": ["vitest.config.ts", "vitest.config.js"],
    "ESLint": [".eslintrc.json", ".eslintrc.js"],
    "Prettier": [".prettierrc", ".prettierrc.json"],
}


def detect_stack(files: dict) -> list[str]:
    """Detect tech stack from file presence and content."""
    stack = []
    file_names = set(files.keys())

    # Check file-based signals
    for tech, indicators in STACK_SIGNALS.items():
        for indicator in indicators:
            if indicator in file_names:
                stack.append(tech)
                break

    # Check package.json for JS framework dependencies
    if "package.json" in files:
        try:
            pkg = json.loads(files["package.json"])
            all_deps = {}
            all_deps.update(pkg.get("dependencies", {}))
            all_deps.update(pkg.get("devDependencies", {}))

            js_frameworks = {
                "React": ["react", "react-dom"],
                "Next.js": ["next"],
                "Vue.js": ["vue"],
                "Nuxt.js": ["nuxt"],
                "Angular": ["@angular/core"],
                "Svelte": ["svelte"],
                "Express": ["express"],
                "Fastify": ["fastify"],
                "NestJS": ["@nestjs/core"],
                "Tailwind CSS": ["tailwindcss"],
                "Prisma": ["prisma", "@prisma/client"],
                "tRPC": ["@trpc/server"],
                "Socket.IO": ["socket.io"],
                "Redux": ["redux", "@reduxjs/toolkit"],
                "Zustand": ["zustand"],
                "Vite": ["vite"],
                "Webpack": ["webpack"],
            }

            for fw_name, fw_packages in js_frameworks.items():
                if fw_name not in stack:
                    if any(pkg_name in all_deps for pkg_name in fw_packages):
                        stack.append(fw_name)
        except json.JSONDecodeError:
            pass

    # Check requirements.txt for Python packages
    if "requirements.txt" in files:
        reqs = files["requirements.txt"].lower()
        py_frameworks = {
            "Django": "django",
            "Flask": "flask",
            "FastAPI": "fastapi",
            "Streamlit": "streamlit",
            "Celery": "celery",
            "SQLAlchemy": "sqlalchemy",
            "PyTorch": "torch",
            "TensorFlow": "tensorflow",
            "LangChain": "langchain",
            "Pandas": "pandas",
            "NumPy": "numpy",
        }
        for fw_name, fw_keyword in py_frameworks.items():
            if fw_name not in stack and fw_keyword in reqs:
                stack.append(fw_name)

    # Check pyproject.toml
    if "pyproject.toml" in files:
        pyproj = files["pyproject.toml"].lower()
        if "poetry" in pyproj:
            stack.append("Poetry")

    return sorted(set(stack))


# ── README Quality Analysis ──────────────────────────────────────────

README_SECTIONS = {
    "title": {
        "label": "Project Title",
        "patterns": [r"^#\s+\w"],
        "weight": 15,
    },
    "description": {
        "label": "Description",
        "patterns": [r"about", r"overview", r"description", r"what is"],
        "weight": 15,
        "min_length": 200,
    },
    "installation": {
        "label": "Installation Guide",
        "patterns": [r"install", r"getting\s+started", r"setup", r"quick\s+start"],
        "weight": 15,
    },
    "usage": {
        "label": "Usage Instructions",
        "patterns": [r"usage", r"how\s+to\s+use", r"example", r"getting\s+started"],
        "weight": 10,
    },
    "features": {
        "label": "Features List",
        "patterns": [r"feature", r"what\s+it\s+does", r"capabilities"],
        "weight": 10,
    },
    "env_vars": {
        "label": "Environment Variables",
        "patterns": [r"\.env", r"environment", r"config", r"configuration"],
        "weight": 5,
    },
    "license_info": {
        "label": "License",
        "patterns": [r"license", r"mit", r"apache", r"gpl"],
        "weight": 5,
    },
    "contributing": {
        "label": "Contributing Guide",
        "patterns": [r"contribut", r"how\s+to\s+contribute", r"pull\s+request"],
        "weight": 5,
    },
    "badges": {
        "label": "Badges/Shields",
        "patterns": [r"shields\.io", r"badge", r"img\.shields"],
        "weight": 5,
    },
    "screenshots": {
        "label": "Screenshots/Media",
        "patterns": [r"screenshot", r"demo", r"gif", r"\.png", r"\.jpg", r"!\["],
        "weight": 5,
    },
    "api_docs": {
        "label": "API Documentation",
        "patterns": [r"api", r"endpoint", r"route", r"swagger", r"openapi"],
        "weight": 5,
    },
    "tests": {
        "label": "Testing Instructions",
        "patterns": [r"test", r"pytest", r"jest", r"coverage"],
        "weight": 5,
    },
}


def analyze_readme(readme: str) -> dict:
    """Analyze README quality and return score with checklist."""
    if not readme or len(readme.strip()) < 10:
        return {"score": 0, "checks": {}, "total_weight": 100}

    readme_lower = readme.lower()
    checks = {}
    earned = 0
    total = 0

    for key, config in README_SECTIONS.items():
        weight = config["weight"]
        total += weight
        found = False

        # Check regex patterns
        for pattern in config["patterns"]:
            if re.search(pattern, readme_lower):
                found = True
                break

        # Additional length check for description
        if key == "description" and found:
            if config.get("min_length") and len(readme) < config["min_length"]:
                found = False

        checks[key] = {
            "label": config["label"],
            "found": found,
            "weight": weight,
            "earned": weight if found else 0,
        }

        if found:
            earned += weight

    score = int((earned / total) * 100) if total > 0 else 0

    return {
        "score": score,
        "checks": checks,
        "total_weight": total,
        "earned_weight": earned,
    }


# ── Project Structure Analysis ───────────────────────────────────────

STRUCTURE_CHECKS = {
    "README.md": {"label": "README", "weight": 15},
    "LICENSE": {"label": "License File", "weight": 10},
    "LICENSE.md": {"label": "License File", "weight": 10, "alias": True},
    ".gitignore": {"label": ".gitignore", "weight": 5},
    "requirements.txt": {"label": "Python Dependencies", "weight": 10},
    "package.json": {"label": "Node Dependencies", "weight": 10},
    "pyproject.toml": {"label": "Python Project Config", "weight": 10},
    ".env.example": {"label": "Env Example File", "weight": 8},
    ".env.sample": {"label": "Env Example File", "weight": 8, "alias": True},
    "Dockerfile": {"label": "Docker Support", "weight": 10},
    "docker-compose.yml": {"label": "Docker Compose", "weight": 5},
    ".github/workflows/ci.yml": {"label": "CI/CD Pipeline", "weight": 10},
    ".github/workflows/main.yml": {"label": "CI/CD Pipeline", "weight": 10, "alias": True},
    ".github/workflows/test.yml": {"label": "CI/CD Pipeline", "weight": 10, "alias": True},
    "CONTRIBUTING.md": {"label": "Contributing Guide", "weight": 5},
    "CHANGELOG.md": {"label": "Changelog", "weight": 5},
    "SECURITY.md": {"label": "Security Policy", "weight": 5},
    "Makefile": {"label": "Build Automation", "weight": 3},
}


def analyze_structure(files: dict) -> dict:
    """Analyze project structure and return score with breakdown."""
    checks = {}
    earned = 0
    total = 0
    seen_groups = set()

    for file_name, config in STRUCTURE_CHECKS.items():
        label = config["label"]

        # Skip if we already counted this group (e.g., LICENSE and LICENSE.md)
        if label in seen_groups:
            continue

        is_alias = config.get("alias", False)
        exists = file_name in files

        # If this is an alias and the main file exists, skip
        if is_alias and not exists:
            continue

        seen_groups.add(label)
        weight = config["weight"]
        total += weight

        checks[file_name] = {
            "label": label,
            "exists": exists,
            "weight": weight,
            "earned": weight if exists else 0,
        }

        if exists:
            earned += weight

    score = int((earned / total) * 100) if total > 0 else 0

    return {
        "score": score,
        "checks": checks,
        "total_weight": total,
        "earned_weight": earned,
    }


# ── Security Checklist ───────────────────────────────────────────────

SECURITY_CHECKS = {
    ".env.example": "Environment variable template exists",
    ".gitignore": "Gitignore prevents committing secrets",
    "SECURITY.md": "Security policy documented",
    "LICENSE": "License clearly defined",
    "Dockerfile": "Containerized (reproducible builds)",
}


def security_checklist(files: dict) -> list[dict]:
    """Generate a security/config checklist."""
    results = []
    for file_name, description in SECURITY_CHECKS.items():
        results.append({
            "file": file_name,
            "description": description,
            "present": file_name in files,
        })
    return results
