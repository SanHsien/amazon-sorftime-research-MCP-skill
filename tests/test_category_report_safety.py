"""Regression checks for credentials in category reports and console output."""

import importlib.util
import json
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


def test_analyzer_passes_key_as_encoded_query_parameter(monkeypatch):
    secret = "sample/secret?&=+"
    analyzer = CategoryAnalyzer(api_key=secret)
    seen = {}

    def respond(url, **kwargs):
        seen["url"] = url
        seen["params"] = kwargs.get("params")
        return types.SimpleNamespace(status_code=200, text='data: {"result": {"content": []}}')

    monkeypatch.setattr("analyze_category.requests.post", respond)
    analyzer._call_api("category_report", {})

    assert seen == {"url": "https://mcp.sorftime.com", "params": {"key": secret}}


def test_report_files_and_logs_do_not_contain_key(tmp_path, capsys):
    secret = "sample-secret-789"
    fixture = Path(__file__).parent / "fixtures" / "category_report_credentials.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    generator = CategoryReportGenerator(data, str(tmp_path / "reports"))
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


def test_calculate_scores_ignores_chinese_label_prefix_on_values():
    """A prefixed value must score exactly like the bare number (no silent 0 fallback)."""
    analyzer = CategoryAnalyzer(api_key="sample-key")

    def stats(prefix):
        return {
            "top100產品月銷額": f"{prefix}1,500,000",
            "top3_brands_sales_volume_share": f"{prefix}84.11%",
            "amazonOwned_sales_volume_share": f"{prefix}5%",
            "low_reviews_sales_volume_share": f"{prefix}45%",
            "average_price": f"{prefix}99.5",
        }

    expected = analyzer._calculate_scores(stats(""))
    for prefix in ("销量前三的品牌月销量占比:", "占比：", "top3品牌占比: "):
        assert analyzer._calculate_scores(stats(prefix)) == expected, prefix

    # Unparseable text still falls back to the default instead of raising.
    assert analyzer._calculate_scores({"top3_brands_sales_volume_share": "n/a"})["競爭烈度"] == 18


def test_calculate_scores_does_not_misread_values_float_already_handled():
    """The regex fallback must not turn '.5', '3e5' or an ASIN's digits into other numbers."""
    analyzer = CategoryAnalyzer(api_key="sample-key")

    def scores(**kw):
        return analyzer._calculate_scores(kw)

    assert scores(average_price=".5") == scores(average_price="0.5")
    assert scores(average_price="3e5") == scores(average_price="300000")
    assert scores(top3_brands_sales_volume_share="B0ABC12345") == scores(top3_brands_sales_volume_share="n/a")
