#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 報告生成器
"""

import os
from datetime import datetime


def generate_markdown_report(asin: str, site: str, keywords: list,
                            categorized: dict, output_dir: str,
                            product_info: dict = None) -> str:
    """
    生成 Markdown 分析報告

    Args:
        asin: 產品 ASIN
        site: 站點
        keywords: 完整關鍵詞列表
        categorized: 分類後的關鍵詞
        output_dir: 輸出目錄
        product_info: 產品資訊（可選）

    Returns:
        str: 報告檔案路徑
    """
    report_file = os.path.join(output_dir, 'report.md')

    # 計算統計資料
    stats = calculate_statistics(keywords, categorized)

    # 生成報告內容
    content = build_report_content(asin, site, keywords, categorized,
                                   stats, product_info)

    # 寫入檔案
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)

    return report_file


def calculate_statistics(keywords: list, categorized: dict) -> dict:
    """計算統計資料"""
    total_keywords = len(keywords)
    total_search_volume = sum(kw.get('search_volume', 0) for kw in keywords)
    total_cpc = sum(kw.get('cpc', 0) for kw in keywords)

    # 計算分類後的總關鍵詞數（用於佔比計算）
    total_categorized = sum(len(kw_list) for kw_list in categorized.values())

    # 分類統計
    category_stats = {}
    for category, kw_list in categorized.items():
        search_volumes = []
        for kw in kw_list:
            if isinstance(kw, dict):
                search_volumes.append(kw.get('search_volume', 0))
            elif isinstance(kw, str):
                # 在 keywords 中查詢
                for original_kw in keywords:
                    if original_kw['keyword'].lower() == kw.lower():
                        search_volumes.append(original_kw.get('search_volume', 0))
                        break

        # 使用分類後的總數計算佔比
        category_stats[category] = {
            'count': len(kw_list),
            'percentage': round(len(kw_list) / total_categorized * 100, 1) if total_categorized > 0 else 0,
            'total_search_volume': sum(search_volumes),
            'avg_search_volume': round(sum(search_volumes) / len(search_volumes), 0) if search_volumes else 0
        }

    return {
        'total_keywords': total_keywords,
        'total_search_volume': total_search_volume,
        'avg_cpc': round(total_cpc / total_keywords, 2) if total_keywords > 0 else 0,
        'category_stats': category_stats,
        'total_categorized': total_categorized
    }


def build_report_content(asin: str, site: str, keywords: list,
                        categorized: dict, stats: dict,
                        product_info: dict = None) -> str:
    """構建報告內容"""

    # 獲取產品名稱
    product_name = product_info.get('product_name', '') if product_info else ''
    if not product_name:
        # 從關鍵詞中推斷產品名稱
        core_keywords = categorized.get('CORE', [])[:10]
        product_name = infer_product_name(core_keywords)

    content = f"""# 關鍵詞調研分析報告

## 分析概覽

| 專案 | 詳情 |
|------|------|
| **ASIN** | [{asin}](https://www.amazon.com/dp/{asin}) |
| **產品名稱** | {product_name} |
| **亞馬遜站點** | {site} |
| **分析時間** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
| **詞庫規模** | {stats.get('total_categorized', stats['total_keywords']):,} 個關鍵詞（原始：{stats['total_keywords']:,}個） |
| **總搜尋量** | {stats['total_search_volume']:,} |
| **平均 CPC** | ${stats['avg_cpc']:.2f} |

---

## 分類統計

| 分類 | 數量 | 佔比 | 總搜尋量 | 平均搜尋量 | 應用策略 |
|------|------|------|----------|-----------|----------|
"""

    # 分類統計表格
    category_order = ['NEGATIVE', 'BRAND', 'MATERIAL', 'SCENARIO',
                     'ATTRIBUTE', 'FUNCTION', 'CORE', 'CHARACTER', 'OTHER']

    for cat in category_order:
        if cat not in stats['category_stats']:
            continue
        cat_stat = stats['category_stats'][cat]
        cat_name = get_category_display_name(cat)
        strategy = get_application_strategy(cat)

        content += f"| **{cat_name}** | {cat_stat['count']:,} | {cat_stat['percentage']}% | {cat_stat['total_search_volume']:,} | {cat_stat['avg_search_volume']:,} | {strategy} |\n"

    content += f"""

---

## 各分類 Top 關鍵詞

### 核心產品詞 (CORE)

{generate_top_keywords_table(categorized.get('CORE', []), keywords, limit=20)}

**應用建議**: 這些是產品的核心大詞，流量大但競爭激烈。建議用於廣泛匹配佔領坑位，配合高預算和強Listing實力。

---

### 否定/敏感詞 (NEGATIVE)

{generate_top_keywords_table(categorized.get('NEGATIVE', []), keywords, limit=30)}

**應用建議**: 以上 {len(categorized.get('NEGATIVE', []))} 個詞與產品不相關，請直接新增為否定關鍵詞（片語否定），避免浪費廣告費。

---

### 品牌詞 (BRAND)

{generate_top_keywords_table(categorized.get('BRAND', []), keywords, limit=20)}

**應用建議**: 競品品牌詞。如果做競品狙擊，可以單獨建立廣告組；否則直接新增為否定詞。

---

### 材質詞 (MATERIAL)

{generate_top_keywords_table(categorized.get('MATERIAL', []), keywords, limit=20)}

**應用建議**: 材質詞轉化率通常較高，建議用於精準匹配或片語匹配。

---

### 使用場景詞 (SCENARIO)

{generate_top_keywords_table(categorized.get('SCENARIO', []), keywords, limit=25)}

**應用建議**: 按場景拆分廣告組（如：entryway 組、bathroom 組），提高廣告相關性。

---

### 屬性修飾詞 (ATTRIBUTE)

{generate_top_keywords_table(categorized.get('ATTRIBUTE', []), keywords, limit=25)}

**應用建議**: 長尾精準詞，競爭小轉化率高。建議用於精確匹配或片語匹配。

---

### 功能詞 (FUNCTION)

{generate_top_keywords_table(categorized.get('FUNCTION', []), keywords, limit=20)}

**應用建議**: 功能相關詞，用於廣泛匹配擴流，但需注意過濾不相關的詞。

---

## 廣告投放策略建議

### 1. 否定關鍵詞策略

直接複製 `negative_words.txt` 檔案中的所有詞，新增到廣告活動的否定關鍵詞列表中。

**否定數量**: {len(categorized.get('NEGATIVE', []))} 個
**操作方式**: 片語否定 (Phrase Match)

### 2. 精準匹配組（高轉化）

**組合策略**: 材質詞 + 屬性修飾詞

推薦組合（以產品為核心）:
"""

    # 生成精準組合建議
    material_kws = [get_kw_string(k) for k in categorized.get('MATERIAL', [])[:10]]
    attribute_kws = [get_kw_string(k) for k in categorized.get('ATTRIBUTE', [])[:15]]

    if material_kws and attribute_kws:
        content += f"""
| 材質 | 屬性 | 組合示例 |
|------|------|----------|
| {' / '.join(material_kws[:3])} | {' / '.join(attribute_kws[:3])} | 組合使用 |

**投放方式**: 精確匹配 (Exact Match)
**預期**: 高轉化率，低 CPC
"""

    content += f"""

### 3. 場景廣告組

按使用場景拆分廣告組，提高廣告相關性:

"""

    # 場景詞分組建議
    scenarios = categorized.get('SCENARIO', [])[:10]
    if scenarios:
        for i, scenario in enumerate(scenarios[:5], 1):
            scenario_kw = get_kw_string(scenario)
            content += f"- **場景組 {i}**: 圍繞 `{scenario_kw}` 展開投放\n"

    content += f"""

**投放方式**: 片語匹配 (Phrase Match)
**預期**: 中等轉化，中等流量

### 4. 廣泛匹配組（擴流）

**關鍵詞**: 核心產品詞 + 功能詞

推薦:
"""
    core_kws = [get_kw_string(k) for k in categorized.get('CORE', [])[:10]]
    function_kws = [get_kw_string(k) for k in categorized.get('FUNCTION', [])[:10]]

    for kw in core_kws[:5]:
        content += f"- `{kw}`\n"

    content += f"""

**投放方式**: 廣泛匹配 (Broad Match)
**預期**: 大流量，需密切監控否定詞

---

## 詞庫檔案說明

| 檔案 | 說明 | 用途 |
|------|------|------|
| `keywords.csv` | 完整詞庫（含分類、搜尋量、CPC） | Excel 開啟分析 |
| `keywords_negative.csv` | 否定詞專用 | 直接複製到廣告後臺 |
| `keywords_brand.csv` | 品牌詞列表 | 競品分析或否定 |
| `keywords_material.csv` | 材質詞 | 精準組投放 |
| `keywords_scenario.csv` | 場景詞 | 場景組投放 |
| `keywords_attribute.csv` | 屬性修飾詞 | 長尾精準投放 |
| `keywords_function.csv` | 功能詞 | 廣泛匹配投放 |
| `keywords_core.csv` | 核心產品詞 | 大詞投放 |
| `negative_words.txt` | 否定詞清單（每行一個） | 直接複製使用 |
| `brand_words.txt` | 品牌詞清單 | 品牌分析 |

---

## 資料來源

本報告基於 **Sorftime Amazon 資料服務** 生成，資料採集自:
- 產品流量關鍵詞分析
- 競品關鍵詞佈局分析
- 類目核心關鍵詞分析
- 長尾詞智慧擴充套件

資料更新頻率: 實時更新
資料時效: 約 1-7 天延遲

---

*本報告由 Claude Code 自動生成 | 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return content


def generate_top_keywords_table(keywords: list, all_keywords: list, limit: int = 20) -> str:
    """生成 Top 關鍵詞表格"""
    if not keywords:
        return "*暫無資料*"

    # 構建搜尋量和 CPC 對映
    search_map = {kw['keyword'].lower(): kw.get('search_volume', 0)
                 for kw in all_keywords}
    cpc_map = {kw['keyword'].lower(): kw.get('cpc', 0)
               for kw in all_keywords}

    # 排序
    sorted_kws = sorted(keywords,
                       key=lambda k: search_map.get(k.lower() if isinstance(k, str) else k.get('keyword', '').lower(), 0),
                       reverse=True)[:limit]

    table = "| 排名 | 關鍵詞 | 搜尋量 | CPC |\n|------|--------|--------|-----|\n"

    for i, kw in enumerate(sorted_kws, 1):
        if isinstance(kw, str):
            keyword = kw
            search_vol = search_map.get(kw.lower(), 0)
            cpc = cpc_map.get(kw.lower(), 0)
        else:
            keyword = kw.get('keyword', '')
            search_vol = kw.get('search_volume', 0)
            cpc = kw.get('cpc', 0)

        table += f"| {i} | `{keyword}` | {search_vol:,} | ${cpc:.2f} |\n"

    return table


def get_kw_string(kw) -> str:
    """獲取關鍵詞字串"""
    if isinstance(kw, str):
        return kw
    return kw.get('keyword', '')


def get_category_display_name(category: str) -> str:
    """獲取分類顯示名稱"""
    names = {
        'NEGATIVE': '否定/敏感詞',
        'BRAND': '品牌詞',
        'MATERIAL': '材質詞',
        'SCENARIO': '使用場景詞',
        'ATTRIBUTE': '屬性修飾詞',
        'FUNCTION': '功能詞',
        'CORE': '核心產品詞',
        'CHARACTER': '角色詞',
        'OTHER': '其他'
    }
    return names.get(category, category)


def get_application_strategy(category: str) -> str:
    """獲取應用策略"""
    strategies = {
        'NEGATIVE': '直接否定',
        'BRAND': '競品打法/否定',
        'MATERIAL': '精準匹配',
        'SCENARIO': '場景分組',
        'ATTRIBUTE': '長尾精準',
        'FUNCTION': '廣泛匹配',
        'CORE': '大詞投放',
        'OTHER': '補充埋詞'
    }
    return strategies.get(category, '')


def infer_product_name(core_keywords: list) -> str:
    """從核心關鍵詞推斷產品名稱"""
    if not core_keywords:
        return "Unknown Product"

    # 取第一個核心詞
    first_kw = get_kw_string(core_keywords[0])

    # 簡單的名稱推斷
    if first_kw:
        # 首字母大寫
        return first_kw.title()

    return "Unknown Product"


def main():
    """測試入口"""
    import sys
    import json

    if len(sys.argv) < 5:
        print("用法: python generate_markdown_report.py <asin> <site> <keywords.json> <categorized.json> [output_dir]")
        sys.exit(1)

    asin = sys.argv[1]
    site = sys.argv[2]
    keywords_file = sys.argv[3]
    categorized_file = sys.argv[4]
    output_dir = sys.argv[5] if len(sys.argv) > 5 else '.'

    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords = json.load(f)

    with open(categorized_file, 'r', encoding='utf-8') as f:
        categorized = json.load(f)

    report_file = generate_markdown_report(asin, site, keywords, categorized, output_dir)
    print(f"✓ 報告已生成: {report_file}")


if __name__ == "__main__":
    main()
