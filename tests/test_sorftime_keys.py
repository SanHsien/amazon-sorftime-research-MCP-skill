"""Sorftime answers with simplified keys; the scripts read traditional keys.

The fork-wide opencc conversion rewrote the key literals the scripts use to read responses,
so live (simplified) responses produced empty products and wrong scores. These tests pin the
key normalization at the data entry points and keep the key map in step with the code.
"""

import importlib.util
import json
import sys
import types
from pathlib import Path

import opencc
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "SKILLS" / "skills"
CATEGORY = SKILLS_ROOT / "category-selection" / "scripts"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "sorftime_category_report_live.json"
KEY_SKILLS = ("category-selection", "keyword-research", "product-research")

sys.path.insert(0, str(CATEGORY))
sys.path.insert(0, str(REPO_ROOT / "tools"))
if "requests" not in sys.modules and importlib.util.find_spec("requests") is None:
    sys.modules["requests"] = types.ModuleType("requests")
    sys.modules["requests"].post = None

import generate_sorftime_key_map as keygen  # noqa: E402
from analyze_category import CategoryAnalyzer  # noqa: E402
from sorftime_keys import KEY_MAP, normalize_keys, normalize_text  # noqa: E402

T2S = opencc.OpenCC("t2s")


def live_report():
    """A real Sorftime category_report answer: simplified keys, as the API sends them."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_really_uses_simplified_keys():
    assert "类目统计报告" in live_report()


def test_analyzer_reads_live_category_report():
    analyzer = CategoryAnalyzer(api_key="test-key")
    analyzer.category_name = "Cell Phones"
    analyzer.site = "US"
    analyzer._call_api = lambda tool, arguments: live_report()

    report = analyzer.get_category_report("7072561011")
    result = analyzer.extract_and_analyze(report)

    assert len(result["products"]) == 3
    # Monthly revenue is about 81.7M, so the market-size dimension must be the top tier.
    assert result["scores"]["市場規模"] == 20


def test_normalize_keys_accepts_simplified_and_traditional():
    simplified = {"类目统计报告": {"top100产品月销额": "1"}, "Top100产品": [{"标题": "t", "价格": 1}]}
    traditional = {"類目統計報告": {"top100產品月銷額": "1"}, "Top100產品": [{"標題": "t", "價格": 1}]}
    expected = traditional

    assert normalize_keys(simplified) == expected
    assert normalize_keys(traditional) == expected


def test_normalize_keys_leaves_values_alone():
    data = {"标题": "销量 产品 Top100产品", "list": ["类目统计报告"], "n": 1}
    assert normalize_keys(data) == {"標題": "销量 产品 Top100产品", "list": ["类目统计报告"], "n": 1}


def test_normalize_text_only_rewrites_quoted_keys():
    text = '{"类目统计报告": {"类目名称":"类目统计报告 ok"}, "n":1}'
    assert normalize_text(text) == '{"類目統計報告": {"類目名稱":"类目统计报告 ok"}, "n":1}'
    assert normalize_text('{"類目統計報告":1}') == '{"類目統計報告":1}'


@pytest.mark.parametrize("skill", KEY_SKILLS)
def test_every_key_in_scripts_is_in_the_map(skill):
    """A traditional key the scripts read must be reachable from its simplified API form."""
    known = set(KEY_MAP) | set(KEY_MAP.values())
    missing = []
    for path in sorted((SKILLS_ROOT / skill / "scripts").glob("*.py")):
        if path.name == "sorftime_keys.py":
            continue
        for key in keygen.collect_code_keys(path.read_text(encoding="utf-8")):
            if T2S.convert(key) != key and key not in known:
                missing.append(f"{path.name}: {key}")
    assert not missing, "run tools/generate_sorftime_key_map.py: " + ", ".join(missing)


def test_map_values_are_what_the_converter_produces():
    s2t = opencc.OpenCC("s2twp")
    wrong = {k: v for k, v in KEY_MAP.items() if s2t.convert(k) != v and T2S.convert(v) != k}
    assert not wrong


def test_key_module_is_identical_in_every_skill():
    texts = {
        skill: (SKILLS_ROOT / skill / "scripts" / "sorftime_keys.py").read_text(encoding="utf-8")
        for skill in KEY_SKILLS
    }
    assert len(set(texts.values())) == 1


def _load_script(skill, name):
    """Import a skill script under a unique module name, with its folder importable."""
    scripts = SKILLS_ROOT / skill / "scripts"
    spec = importlib.util.spec_from_file_location(f"{skill.replace('-', '_')}_{name}", scripts / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(scripts))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(scripts))
    return module


def _sse_file(tmp_path, payload):
    """The Sorftime wire format: an SSE line whose text field holds unicode-escaped JSON."""
    inner = json.dumps(payload, ensure_ascii=True, separators=(",", ":"))
    line = json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"content": [{"type": "text", "text": inner}]}})
    path = tmp_path / "response.txt"
    path.write_text("event: message\ndata: " + line + "\n\n", encoding="utf-8")
    return path


def test_parse_sorftime_sse_reads_live_statistics_and_products(tmp_path):
    module = _load_script("category-selection", "parse_sorftime_sse")
    result = module.parse_sorftime_sse(str(_sse_file(tmp_path, live_report())))

    assert result["statistics"]["總銷額"] == 81687183.19
    assert result["products"][0]["標題"].startswith("Motorola Moto G Play")
    assert result["products"][0]["月銷量"] == 10533


def test_sse_decoder_returns_traditional_keys(tmp_path):
    module = _load_script("category-selection", "sse_decoder")
    data = module.decode_sse_response(str(_sse_file(tmp_path, live_report())))

    assert "類目統計報告" in data
    assert len(data["Top100產品"]) == 3


def test_category_report_parser_reads_live_statistics(tmp_path):
    module = _load_script("category-selection", "parse_category_report")
    stats = module.CategoryReportParser(str(_sse_file(tmp_path, live_report()))).parse(10)["statistics"]

    assert stats["總銷額"] == "81687183.19"


def test_keywords_parser_returns_traditional_keys(tmp_path):
    module = _load_script("category-selection", "keywords_parser")
    path = _sse_file(tmp_path, [{"关键词": "sofa", "月搜索量": 1200}])

    assert module.parse_keywords_sse(str(path)) == [{"關鍵詞": "sofa", "月搜尋量": 1200}]


def test_trend_parser_returns_traditional_keys(tmp_path):
    module = _load_script("category-selection", "trend_parser")
    path = _sse_file(tmp_path, {"趋势日期": ["2026-01"], "趋势值": [1]})

    assert module.decode_sse_trend(str(path)) == {"趨勢日期": ["2026-01"], "趨勢值": [1]}


def test_keyword_research_parser_returns_traditional_keys():
    module = _load_script("keyword-research", "data_parser")

    assert module.parse_json_data('[{"关键词": "sofa", "月搜索量": 5}]') == [{"關鍵詞": "sofa", "月搜尋量": 5}]


def test_product_research_client_returns_traditional_keys(tmp_path):
    module = _load_script("product-research", "api_client")
    content = _sse_file(tmp_path, live_report()).read_text(encoding="utf-8")
    data = module.decode_sse_response(content)

    assert "類目統計報告" in data


def test_extract_top_products_reads_live_response_text(tmp_path):
    module = _load_script("category-selection", "extract_top_products")
    path = tmp_path / "top100.json"
    path.write_text(json.dumps(live_report(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    products = module.extract_top_products(str(path), 10)

    # The script's fallback walks a set, so the order is not stable; compare as a set.
    assert sorted(p["ASIN"] for p in products) == sorted(item["ASIN"] for item in live_report()["Top100产品"])
