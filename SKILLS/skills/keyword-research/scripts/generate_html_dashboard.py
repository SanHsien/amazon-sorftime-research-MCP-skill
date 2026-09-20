#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 視覺化儀表板生成器
"""

import os
import json
from datetime import datetime


def generate_html_dashboard(asin: str, site: str, keywords: list,
                           categorized: dict, output_dir: str,
                           product_info: dict = None) -> str:
    """
    生成 HTML 視覺化儀表板

    Args:
        asin: 產品 ASIN
        site: 站點
        keywords: 完整關鍵詞列表
        categorized: 分類後的關鍵詞
        output_dir: 輸出目錄
        product_info: 產品資訊（可選）

    Returns:
        str: HTML 檔案路徑
    """
    html_file = os.path.join(output_dir, 'dashboard.html')

    # 讀取模板
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'templates', 'dashboard_template.html'
    )

    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    else:
        template = get_default_template()

    # 計算統計資料
    stats = calculate_statistics(keywords, categorized)

    # 準備圖表資料
    chart_data = prepare_chart_data(categorized, stats, keywords)

    # 準備表格資料
    table_data = prepare_table_data(keywords, categorized)

    # 準備篩選按鈕（只顯示有資料的分類）
    filter_buttons = prepare_filter_buttons(categorized)

    # 獲取產品名稱
    product_name = product_info.get('product_name', '') if product_info else ''
    if not product_name:
        core_keywords = categorized.get('CORE', [])[:10]
        product_name = infer_product_name(core_keywords)

    # 替換模板變數
    html_content = template.replace('{{ASIN}}', asin)
    html_content = html_content.replace('{{PRODUCT_NAME}}', product_name)
    html_content = html_content.replace('{{SITE}}', site)
    html_content = html_content.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # 替換統計資料
    html_content = html_content.replace('{{TOTAL_KEYWORDS}}', f"{stats['total_keywords']:,}")
    html_content = html_content.replace('{{TOTAL_SEARCH_VOLUME}}', f"{stats['total_search_volume']:,}")
    html_content = html_content.replace('{{AVG_CPC}}', f"${stats['avg_cpc']:.2f}")

    # 替換圖表資料
    html_content = html_content.replace('{{CATEGORY_DATA}}', chart_data['category'])
    html_content = html_content.replace('{{SEARCH_VOLUME_DATA}}', chart_data['search_volume'])
    html_content = html_content.replace('{{CPC_DATA}}', chart_data['cpc'])

    # 替換表格資料
    html_content = html_content.replace('{{KEYWORD_TABLE_ROWS}}', table_data)
    html_content = html_content.replace('{{FILTER_BUTTONS}}', filter_buttons)

    # 寫入檔案
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return html_file


def calculate_statistics(keywords: list, categorized: dict) -> dict:
    """計算統計資料"""
    total_keywords = len(keywords)
    total_search_volume = sum(kw.get('search_volume', 0) for kw in keywords)
    total_cpc = sum(kw.get('cpc', 0) for kw in keywords)

    return {
        'total_keywords': total_keywords,
        'total_search_volume': total_search_volume,
        'avg_cpc': round(total_cpc / total_keywords, 2) if total_keywords > 0 else 0
    }


def prepare_chart_data(categorized: dict, stats: dict, keywords: list = None) -> dict:
    """準備圖表資料"""
    # 分類資料
    category_labels = []
    category_data = []

    category_order = [
        ('NEGATIVE', '否定詞'),
        ('BRAND', '品牌詞'),
        ('MATERIAL', '材質詞'),
        ('SCENARIO', '場景詞'),
        ('ATTRIBUTE', '屬性詞'),
        ('FUNCTION', '功能詞'),
        ('CORE', '核心詞'),
        ('CHARACTER', '角色詞'),
        ('OTHER', '其他')
    ]

    for cat_code, cat_name in category_order:
        if cat_code in categorized:
            category_labels.append(cat_name)
            category_data.append(len(categorized[cat_code]))

    category_json = json.dumps({
        'labels': category_labels,
        'data': category_data
    }, ensure_ascii=False)

    # 搜尋量分佈資料 - 使用完整的 keywords 資料
    search_volume_labels = ['高 (>10K)', '中 (1K-10K)', '低 (<1K)']
    search_volume_data = [0, 0, 0]

    if keywords:
        for kw in keywords:
            vol = kw.get('search_volume', 0)
            if vol > 10000:
                search_volume_data[0] += 1
            elif vol > 1000:
                search_volume_data[1] += 1
            else:
                search_volume_data[2] += 1

    search_volume_json = json.dumps({
        'labels': search_volume_labels,
        'data': search_volume_data
    }, ensure_ascii=False)

    # CPC 分佈資料 - 使用完整的 keywords 資料
    cpc_labels = ['高 (>$2)', '中 ($1-2)', '低 (<$1)']
    cpc_data = [0, 0, 0]

    if keywords:
        for kw in keywords:
            cpc = kw.get('cpc', 0)
            if cpc > 2:
                cpc_data[0] += 1
            elif cpc > 1:
                cpc_data[1] += 1
            elif cpc > 0:
                cpc_data[2] += 1

    cpc_json = json.dumps({
        'labels': cpc_labels,
        'data': cpc_data
    }, ensure_ascii=False)

    return {
        'category': category_json,
        'search_volume': search_volume_json,
        'cpc': cpc_json
    }


def prepare_filter_buttons(categorized: dict) -> str:
    """準備篩選按鈕 - 只顯示有資料的分類"""
    # 分類按鈕配置（保持原有順序）
    button_config = [
        ('NEGATIVE', '否定詞'),
        ('BRAND', '品牌詞'),
        ('MATERIAL', '材質詞'),
        ('SCENARIO', '場景詞'),
        ('ATTRIBUTE', '屬性詞'),
        ('FUNCTION', '功能詞'),
        ('CORE', '核心詞'),
        ('OTHER', '其他')
    ]

    # 生成按鈕（只包含有資料的分類）
    buttons = ['<button class="filter-btn all active" data-category="all">全部</button>']
    for cat_code, cat_name in button_config:
        if cat_code in categorized and len(categorized[cat_code]) > 0:
            buttons.append(f'<button class="filter-btn" data-category="{cat_code}">{cat_name}</button>')

    return '\n                        '.join(buttons)


def prepare_table_data(keywords: list, categorized: dict) -> str:
    """準備表格資料 - 返回所有關鍵詞的 JSON 資料用於 JavaScript 篩選"""
    import html
    import re

    # 構建分類對映 - 使用集合來避免重複
    category_map = {}
    for category, kw_list in categorized.items():
        for kw in kw_list:
            normalized = kw.lower() if isinstance(kw, str) else kw.get('keyword', '').lower()
            category_map[normalized] = category

    # 去重關鍵詞（按關鍵詞字串去重）
    seen_keywords = {}
    for kw in keywords:
        keyword = kw.get('keyword', '').strip()
        if keyword and keyword not in seen_keywords:
            seen_keywords[keyword] = kw

    # 按搜尋量排序
    unique_keywords = list(seen_keywords.values())
    sorted_keywords = sorted(unique_keywords, key=lambda x: x.get('search_volume', 0), reverse=True)

    rows = []
    for kw in sorted_keywords:  # 去重後的所有關鍵詞
        keyword = kw.get('keyword', '')
        # 清理特殊字元
        keyword_clean = keyword.replace('\ufffc', '').replace('￼', '').strip()
        # 移除所有非字母數字和空格的字元，防止 HTML 屬性解析問題
        keyword_safe = re.sub(r'[^a-zA-Z0-9\s\u4e00-\u9fff]', '', keyword_clean)
        keyword_safe_lower = keyword_safe.lower()
        
        normalized = keyword_clean.lower()
        category = category_map.get(normalized, 'UNCATEGORIZED')
        category_name = get_category_display_name(category)
        category_class = get_category_class(category)

        # 格式化搜尋量顯示
        search_volume = kw.get('search_volume', 0)
        search_volume_display = format_search_volume(search_volume)

        # HTML 轉義關鍵詞，防止特殊字元導致屬性值錯誤
        keyword_escaped = html.escape(keyword_clean)

        # 使用 JSON 編碼的 data 屬性，避免引號等問題
        # 將搜尋關鍵詞儲存到 data-search 屬性，僅用於篩選
        rows.append(f'<tr data-category="{category}" data-search="{html.escape(keyword_safe_lower)}"><td>{keyword_escaped}</td><td><span class="badge {category_class}">{category_name}</span></td><td data-volume="{search_volume}">{search_volume_display}</td><td>${kw.get("cpc", 0):.2f}</td><td>{get_application_strategy_short(category)}</td></tr>\n')

    return ''.join(rows)


def format_search_volume(volume: int) -> str:
    """格式化搜尋量顯示為 K/M/B 格式"""
    if volume >= 1000000:
        return f"{volume / 1000000:.1f}M"
    elif volume >= 1000:
        return f"{volume / 1000:.1f}K"
    else:
        return str(volume)


def get_category_display_name(category: str) -> str:
    """獲取分類顯示名稱"""
    names = {
        'NEGATIVE': '否定詞',
        'BRAND': '品牌詞',
        'MATERIAL': '材質詞',
        'SCENARIO': '場景詞',
        'ATTRIBUTE': '屬性詞',
        'FUNCTION': '功能詞',
        'CORE': '核心詞',
        'CHARACTER': '角色詞',
        'OTHER': '其他',
        'UNCATEGORIZED': '未分類'
    }
    return names.get(category, category)


def get_category_class(category: str) -> str:
    """獲取分類 CSS 類名"""
    class_map = {
        'NEGATIVE': 'badge-negative',
        'BRAND': 'badge-brand',
        'MATERIAL': 'badge-material',
        'SCENARIO': 'badge-scenario',
        'ATTRIBUTE': 'badge-attribute',
        'FUNCTION': 'badge-function',
        'CORE': 'badge-core',
        'CHARACTER': 'badge-character',
        'OTHER': 'badge-other',
        'UNCATEGORIZED': 'badge-other'
    }
    return class_map.get(category, 'badge-other')


def get_application_strategy_short(category: str) -> str:
    """獲取簡短應用策略"""
    strategies = {
        'NEGATIVE': '直接否定',
        'BRAND': '競品/否定',
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

    first_kw = core_keywords[0] if isinstance(core_keywords[0], str) else core_keywords[0].get('keyword', '')
    return first_kw.title() if first_kw else "Unknown Product"


def get_default_template() -> str:
    """獲取預設 HTML 模板"""
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>關鍵詞調研分析 - {{ASIN}} ({{SITE}})</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 { margin-bottom: 10px; }
        .header .meta { opacity: 0.9; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-card .label { color: #6c757d; font-size: 14px; margin-bottom: 5px; }
        .stat-card .value { font-size: 32px; font-weight: bold; color: #2c3e50; }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-card h3 { margin-bottom: 15px; color: #2c3e50; }
        .table-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .table-card h3 { margin-bottom: 15px; color: #2c3e50; }

        /* 篩選控制元件樣式 */
        .filter-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 20px;
            align-items: center;
        }
        .filter-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 600;
            color: #495057;
            font-size: 14px;
        }
        .filter-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .filter-btn {
            padding: 8px 16px;
            border: 1px solid #dee2e6;
            background: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }
        .filter-btn:hover {
            background: #f8f9fa;
        }
        .filter-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .filter-btn.all {
            background: #6c757d;
            color: white;
            border-color: #6c757d;
        }
        .filter-btn.all.active {
            background: #495057;
        }
        .search-box {
            padding: 8px 12px;
            border: 1px solid #dee2e6;
            border-radius: 20px;
            font-size: 14px;
            width: 250px;
        }
        .search-box:focus {
            outline: none;
            border-color: #667eea;
        }
        .result-count {
            color: #6c757d;
            font-size: 14px;
            margin-left: auto;
        }

        .table-container {
            max-height: 800px;
            overflow-y: auto;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
            font-size: 14px;
        }
        th { background: #f8f9fa; font-weight: 600; color: #495057; position: sticky; top: 0; }
        tbody tr { transition: background 0.2s; }
        tbody tr:hover { background: #f8f9fa; }
        tbody tr.hidden { display: none; }
        .badge {
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }
        .badge-negative { background: #fee; color: #c33; }
        .badge-brand { background: #eef; color: #36c; }
        .badge-material { background: #efe; color: #3c3; }
        .badge-scenario { background: #ffe; color: #c90; }
        .badge-attribute { background: #fef; color: #90c; }
        .badge-function { background: #eff; color: #09c; }
        .badge-core { background: #ecf; color: #90f; }
        .badge-character { background: #fec; color: #f60; }
        .badge-other { background: #eee; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>關鍵詞調研分析儀表板</h1>
            <div class="meta">
                ASIN: <a href="https://www.amazon.com/dp/{{ASIN}}" target="_blank" style="color: white;">{{ASIN}}</a> |
                產品: {{PRODUCT_NAME}} |
                站點: {{SITE}} |
                生成時間: {{DATE}}
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">總關鍵詞數</div>
                <div class="value">{{TOTAL_KEYWORDS}}</div>
            </div>
            <div class="stat-card">
                <div class="label">總搜尋量</div>
                <div class="value">{{TOTAL_SEARCH_VOLUME}}</div>
            </div>
            <div class="stat-card">
                <div class="label">平均 CPC</div>
                <div class="value">{{AVG_CPC}}</div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="chart-card">
                <h3>分類分佈</h3>
                <canvas id="categoryChart" height="300"></canvas>
            </div>
            <div class="chart-card">
                <h3>搜尋量分佈</h3>
                <canvas id="searchVolumeChart" height="300"></canvas>
            </div>
        </div>

        <div class="table-card">
            <h3>所有關鍵詞列表</h3>
            <div class="filter-controls">
                <div class="filter-group">
                    <span class="filter-label">分類篩選:</span>
                    <div class="filter-buttons">
                        {{FILTER_BUTTONS}}
                    </div>
                </div>
                <div class="filter-group">
                    <span class="filter-label">搜尋:</span>
                    <input type="text" class="search-box" id="searchInput" placeholder="輸入關鍵詞篩選...">
                </div>
                <div class="result-count">
                    顯示 <span id="visibleCount">0</span> / 共 <span id="totalCount">0</span> 個關鍵詞
                </div>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>關鍵詞</th>
                            <th>分類</th>
                            <th>搜尋量</th>
                            <th>CPC</th>
                            <th>應用建議</th>
                        </tr>
                    </thead>
                    <tbody id="keywordTableBody">
                        {{KEYWORD_TABLE_ROWS}}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // 分類分佈圖
        const categoryData = {{CATEGORY_DATA}};
        new Chart(document.getElementById('categoryChart'), {
            type: 'doughnut',
            data: {
                labels: categoryData.labels,
                datasets: [{
                    data: categoryData.data,
                    backgroundColor: [
                        '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
                        '#9b59b6', '#1abc9c', '#9b59b6', '#95a5a6'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });

        // 搜尋量分佈圖
        const searchVolumeData = {{SEARCH_VOLUME_DATA}};
        new Chart(document.getElementById('searchVolumeChart'), {
            type: 'bar',
            data: {
                labels: searchVolumeData.labels,
                datasets: [{
                    label: '關鍵詞數量',
                    data: searchVolumeData.data,
                    backgroundColor: '#3498db'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        // 篩選功能 - 使用事件委託和防抖最佳化效能
        const tableBody = document.getElementById('keywordTableBody');
        const filterButtons = document.querySelectorAll('.filter-btn');
        const searchInput = document.getElementById('searchInput');
        const visibleCountSpan = document.getElementById('visibleCount');
        const totalCountSpan = document.getElementById('totalCount');

        // 快取所有行的資料，避免重複查詢 DOM
        const allRows = Array.from(tableBody.querySelectorAll('tr'));
        const rowData = allRows.map(row => ({
            element: row,
            category: row.dataset.category,
            search: row.dataset.search || ''
        }));

        // 初始化總數
        totalCountSpan.textContent = allRows.length;
        updateVisibleCount();

        // 分類篩選 - 使用事件委託
        tableBody.addEventListener('click', (e) => {
            const btn = e.target.closest('.filter-btn');
            if (!btn) return;
            
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filterByCategory(btn.dataset.category);
        });

        // 搜尋篩選 - 使用防抖最佳化
        let searchTimeout = null;
        searchInput.addEventListener('input', () => {
            if (searchTimeout) clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const activeCategory = document.querySelector('.filter-btn.active').dataset.category;
                filterByCategoryAndSearch(activeCategory, searchInput.value.toLowerCase().trim());
            }, 150);
        });

        function filterByCategory(category) {
            filterByCategoryAndSearch(category, searchInput.value.toLowerCase().trim());
        }

        function filterByCategoryAndSearch(category, searchTerm) {
            const categoryMatch = category === 'all';
            
            rowData.forEach(data => {
                const searchMatch = !searchTerm || data.search.includes(searchTerm);
                const match = (categoryMatch || data.category === category) && searchMatch;
                data.element.classList.toggle('hidden', !match);
            });

            updateVisibleCount();
        }

        function updateVisibleCount() {
            const visibleRows = tableBody.querySelectorAll('tr:not(.hidden)');
            visibleCountSpan.textContent = visibleRows.length;
        }
    </script>
</body>
</html>"""


def main():
    """測試入口"""
    import sys
    import json

    if len(sys.argv) < 5:
        print("用法: python generate_html_dashboard.py <asin> <site> <keywords.json> <categorized.json> [output_dir]")
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

    html_file = generate_html_dashboard(asin, site, keywords, categorized, output_dir)
    print(f"✓ HTML 儀表板已生成: {html_file}")


if __name__ == "__main__":
    main()
