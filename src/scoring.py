"""
RepoLens AI — Scoring Engine
Calculates composite scores for documentation, structure, maintainability,
and product-readiness.
"""


def calculate_composite_scores(
    readme_analysis: dict,
    structure_analysis: dict,
    stack: list[str],
    files: dict,
    repo_info: dict | None = None,
) -> dict:
    """
    Calculate multi-dimensional scores:
    - Documentation Score (README quality)
    - Structure Score (project organization)
    - Maintainability Score (CI, tests, changelog, etc.)
    - Product-Readiness Score (Docker, env, license, etc.)
    - Overall Score (weighted average)
    """

    # Documentation: mostly from README analysis
    doc_score = readme_analysis["score"]

    # Structure: from file presence analysis
    struct_score = structure_analysis["score"]

    # Maintainability: CI, tests, changelog, security policy
    maint_checks = {
        "ci": any(
            f in files
            for f in [
                ".github/workflows/ci.yml",
                ".github/workflows/main.yml",
                ".github/workflows/test.yml",
                ".github/workflows/deploy.yml",
                ".github/workflows/build.yml",
            ]
        ),
        "dockerfile": "Dockerfile" in files,
        "changelog": "CHANGELOG.md" in files,
        "security": "SECURITY.md" in files,
        "contributing": "CONTRIBUTING.md" in files,
        "gitignore": ".gitignore" in files,
        "env_example": any(
            f in files for f in [".env.example", ".env.sample"]
        ),
    }
    maint_score = int(
        sum(maint_checks.values()) / len(maint_checks) * 100
    )

    # Product-readiness: license, deps, docker, env
    prod_checks = {
        "license": any(
            f in files for f in ["LICENSE", "LICENSE.md"]
        ),
        "dependencies": any(
            f in files
            for f in [
                "requirements.txt",
                "package.json",
                "pyproject.toml",
                "go.mod",
                "Cargo.toml",
            ]
        ),
        "docker": "Dockerfile" in files,
        "env_template": any(
            f in files for f in [".env.example", ".env.sample"]
        ),
        "readme": "README.md" in files,
        "has_stack": len(stack) > 0,
    }
    prod_score = int(
        sum(prod_checks.values()) / len(prod_checks) * 100
    )

    # Bonus: GitHub API metadata
    bonus = 0
    if repo_info:
        if repo_info.get("stars", 0) > 100:
            bonus += 5
        if repo_info.get("stars", 0) > 1000:
            bonus += 5
        if repo_info.get("topics"):
            bonus += 3

    # Overall: weighted average with bonus
    overall = int(
        doc_score * 0.25
        + struct_score * 0.25
        + maint_score * 0.25
        + prod_score * 0.25
        + bonus
    )
    overall = min(overall, 100)

    return {
        "documentation": doc_score,
        "structure": struct_score,
        "maintainability": maint_score,
        "product_readiness": prod_score,
        "overall": overall,
        "details": {
            "maintainability_checks": maint_checks,
            "product_readiness_checks": prod_checks,
            "bonus_points": bonus,
        },
    }


def get_score_grade(score: int) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def get_score_emoji(score: int) -> str:
    """Get emoji for score range."""
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    elif score >= 40:
        return "🟠"
    else:
        return "🔴"
