"""Focused regressions found by the four-tool audit.

All mutating-tool tests use disposable fixtures; they never invoke a tool against
the checked-out repository.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name: str):
    """Load one tool under a distinct test-only module name."""
    spec = importlib.util.spec_from_file_location(f"audit_{name}", ROOT / "tools" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


freshness = load_tool("check_dependency_freshness")
upstream = load_tool("check_upstream_updates")
localizer = load_tool("localize_traditional_chinese")


class DependencyFreshnessRegressionTests(unittest.TestCase):
    def test_malformed_registry_version_is_a_failed_check(self) -> None:
        package = {
            "name": "demo",
            "minimum": "1.0",
            "requirement": "demo>=1.0",
            "source": "pyproject.toml",
            "hold": "",
            "kind": "pypi",
        }

        (row,) = freshness.collect_status([package], lambda _name: "not-a-version", {})

        self.assertTrue(row["check_failed"])


class UpstreamUpdateRegressionTests(unittest.TestCase):
    def test_website_payload_without_version_is_not_reported_as_current(self) -> None:
        class Response:
            status = 200

            def read(self) -> bytes:
                return b"{}"

            def __enter__(self):
                return self

            def __exit__(self, *_args) -> None:
                return None

        baseline = {"website": "https://example.invalid", "reviewed_website_version": ""}
        with mock.patch.object(upstream.urllib.request, "urlopen", return_value=Response()):
            result = upstream.check_upstream_website(baseline)

        assert result is not None
        self.assertIn("error", result)


class MutatingToolRegressionTests(unittest.TestCase):
    def run_localizer(self, root: Path, tracked_path: str) -> None:
        with (
            mock.patch.object(localizer, "REPO_ROOT", root),
            mock.patch.object(localizer.subprocess, "check_output", return_value=tracked_path + "\n"),
        ):
            localizer.convert_text_files()

    def test_localizer_preserves_generated_sorftime_map_contract(self) -> None:
        original = "KEY_MAP = {'产品': '產品'}\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "SKILLS" / "skills" / "category-selection" / "scripts" / "sorftime_keys.py"
            path.parent.mkdir(parents=True)
            path.write_text(original, encoding="utf-8")

            self.run_localizer(root, path.relative_to(root).as_posix())

            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_localizer_does_not_rewrite_utf8_binary_payloads(self) -> None:
        original = b"\x00binary-header:\xe4\xb8\xad\xe5\x9b\xbd"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "payload.bin"
            path.write_bytes(original)

            self.run_localizer(root, path.name)

            self.assertEqual(path.read_bytes(), original)
