"""Regression checks for credentials in category reports and console output."""

import importlib.util
import sys
import types
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parent.parent / "SKILLS" / "skills" / "category-selection" / "scripts"
sys.path.insert(0, str(SCRIPTS))
if importlib.util.find_spec("requests") is None:
    sys.modules["requests"] = types.ModuleType("requests")
    sys.modules["requests"].post = None

from analyze_category import CategoryAnalyzer  # noqa: E402
from generate_reports import CategoryReportGenerator  # noqa: E402
from report_safety import redact_report_data  # noqa: E402


def test_redacts_credential_fields_and_key_values():
    secret = "sample-secret/123"
    payload = {
        "category_name": f"Sofas {secret}",
        "statistics": {"月銷量": 100, "apiKey": secret, "nested": {"password": secret}},
        "products": [{"標題": f"See https://example.test?key={secret}&site=US"}],
    }

    clean = redact_report_data(payload, secret)

    assert secret not in str(clean)
    assert clean["statistics"]["月銷量"] == 100
    assert clean["statistics"]["apiKey"] == "[REDACTED]"
    assert clean["statistics"]["nested"]["password"] == "[REDACTED]"
    assert payload["statistics"]["apiKey"] == secret


def test_analyzer_does_not_print_request_exception_with_key(monkeypatch, capsys):
    secret = "sample-secret-456"
    analyzer = CategoryAnalyzer(api_key=secret)

    def fail(*args, **kwargs):
        raise RuntimeError(f"https://mcp.sorftime.com?key={secret}")

    monkeypatch.setattr("analyze_category.requests.post", fail)
    assert analyzer._call_api("category_report", {}) is None
    assert secret not in capsys.readouterr().out


def test_report_files_and_logs_do_not_contain_key(tmp_path, capsys):
    secret = "sample-secret-789"
    data = {
        "category_name": f"Sofas {secret}",
        "statistics": {"月銷量": 100, "password": secret},
        "products": [{"ASIN": "B000000001", "標題": f"Sofa {secret}", "價格": 10, "月銷量": 2}],
        "scores": {"市場規模": 10, "總分": 10, "評級": "一般"},
    }
    generator = CategoryReportGenerator(data, str(tmp_path / "reports"), api_key=secret)
    generated = generator.generate_all()

    assert {"markdown", "csv", "html", "json"} <= set(generated)
    assert secret not in capsys.readouterr().out
    for path in (tmp_path / "reports").rglob("*"):
        if path.is_file():
            assert secret.encode() not in path.read_bytes(), str(path)


def test_direct_generator_redacts_duplicated_password(tmp_path):
    secret = "sample-secret-direct"
    data = {
        "category_name": "Sofas",
        "statistics": {"password": secret, "note": f"Credential: {secret}"},
        "products": [],
        "scores": {},
    }
    generator = CategoryReportGenerator(data, str(tmp_path / "reports"))
    generator.generate_json()

    assert secret not in (tmp_path / "reports" / "data" / "raw_data.json").read_text(encoding="utf-8")


def test_direct_generator_redacts_token_field_variants(tmp_path):
    secrets = ["sample-token-one", "sample-token-two", "sample-token-three", "sample-token-four"]
    data = {
        "category_name": "Sofas",
        "statistics": {
            "token": secrets[0],
            "accessToken": secrets[1],
            "authToken": secrets[2],
            "refresh_token": secrets[3],
            "note": " ".join(secrets),
        },
        "products": [],
        "scores": {},
    }
    generator = CategoryReportGenerator(data, str(tmp_path / "reports"))
    generator.generate_json()
    output = (tmp_path / "reports" / "data" / "raw_data.json").read_text(encoding="utf-8")

    assert all(secret not in output for secret in secrets)
