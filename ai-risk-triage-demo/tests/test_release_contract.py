from __future__ import annotations

import re
import tomllib
from pathlib import Path

from app import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata_and_static_assets_are_coherent():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["version"] == __version__
    assert project["project"]["requires-python"] == ">=3.11"
    assert project["tool"]["setuptools"]["package-data"]["app"] == [
        "static/*.html",
        "static/*.css",
        "static/*.js",
    ]
    dependencies = "\n".join(project["project"]["dependencies"])
    assert "jinja2" not in dependencies
    assert "python-multipart" not in dependencies


def test_local_ui_assets_are_versioned_and_never_served_as_mixed_releases():
    html = (ROOT / "app" / "static" / "index.html").read_text(encoding="utf-8")
    main = (ROOT / "app" / "main.py").read_text(encoding="utf-8")
    versions = (ROOT / "app" / "versions.py").read_text(encoding="utf-8")

    assert "/static/styles.css?v=__UI_ASSET_VERSION__" in html
    assert "/static/app.js?v=__UI_ASSET_VERSION__" in html
    assert "UI_ASSET_VERSION" in versions
    assert 'html.replace("__UI_ASSET_VERSION__", UI_ASSET_VERSION)' in main
    assert "prevent_stale_demo_assets" in main
    assert 'response.headers["Cache-Control"] = "no-store, max-age=0"' in main


def test_local_markdown_links_resolve():
    markdown_files = [
        ROOT / "README.md",
        ROOT / "AIRO_Agentic_Case_Coordinator_Reference_Design.md",
        *(ROOT / "docs").glob("*.md"),
    ]
    broken: list[str] = []
    for document in markdown_files:
        text = document.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            path = (document.parent / target.split("#", 1)[0]).resolve()
            if not path.exists():
                broken.append(f"{document.relative_to(ROOT)} -> {target}")

    assert broken == []


def test_generated_and_secret_files_are_ignored():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for pattern in (
        ".env",
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        ".ruff_cache/",
        "*.egg-info/",
        "data/*.db",
        "data/*.db-wal",
        "data/*.db-shm",
    ):
        assert pattern in ignore
