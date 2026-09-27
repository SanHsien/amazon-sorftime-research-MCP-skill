import json
import py_compile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_mcp_config_validity():
    mcp_file = REPO_ROOT / ".mcp.json"
    assert mcp_file.is_file(), ".mcp.json must exist"
    data = json.loads(mcp_file.read_text(encoding="utf-8"))
    assert "mcpServers" in data, ".mcp.json must contain mcpServers"
    servers = data["mcpServers"]
    for expected in ["sorftime", "sif-mcp", "xydc-mcp", "sellersprite"]:
        assert expected in servers, f"mcpServers must define {expected}"


def test_upstream_baseline_validity():
    baseline_file = REPO_ROOT / "tools" / "upstream_baseline.json"
    assert baseline_file.is_file(), "tools/upstream_baseline.json must exist"
    baseline = json.loads(baseline_file.read_text(encoding="utf-8"))
    assert len(baseline["reviewed_through"]) == 40, "reviewed_through must be 40-char SHA"
    assert baseline["track"] in ["commit", "release"]


def test_skills_exist():
    skills_root = REPO_ROOT / "SKILLS" / "skills"
    assert skills_root.is_dir(), "SKILLS/skills must exist"
    expected_skills = [
        "amazon-analyse",
        "category-selection",
        "keyword-research",
        "product-research",
        "review-analysis",
        "sellersprite-amazon-research",
        "amazon-listing-builder",
        "sif-amazon-research",
        "xiyou-insight",
    ]
    for skill in expected_skills:
        skill_dir = skills_root / skill
        assert skill_dir.is_dir(), f"Skill directory {skill} missing"
        has_skill_md = (skill_dir / "SKILL.md").is_file() or (skill_dir / "skill.md").is_file()
        assert has_skill_md, f"Skill file SKILL.md/skill.md missing in {skill}"


def test_python_syntax_all():
    failed = []
    for py_file in REPO_ROOT.rglob("*.py"):
        if ".git" in py_file.parts or ".venv" in py_file.parts:
            continue
        try:
            py_compile.compile(str(py_file), doraise=True)
        except Exception as e:
            failed.append((str(py_file), str(e)))
    assert not failed, f"Syntax errors in python files: {failed}"

