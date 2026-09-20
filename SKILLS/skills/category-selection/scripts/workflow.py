#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品類選品分析主工作流指令碼 v4.0
一鍵執行完整的品類分析流程

主要改進 (v4.0):
1. ✅ 從 .mcp.json 自動讀取 API Key（無需設定環境變數）
2. ✅ 修復 JSON 字串值中未轉義的控制字元（\n, \r, \t）
3. ✅ 改進類目搜尋策略（支援模糊匹配和關鍵詞變體）
4. ✅ 增強錯誤處理和除錯資訊
5. ✅ 更詳細的執行狀態跟蹤
6. ✅ 支援繼續執行（部分資料獲取失敗不影響整體流程）

主要改進 (v3.1):
1. 修復 Mojibake 編碼問題
2. 改進 JSON 解析（支援 Python dict 格式）
3. 更詳細的錯誤除錯資訊
4. 新增括號匹配演算法
"""

import os
import sys
import json
import subprocess
import re
import codecs
from datetime import datetime
from collections import Counter

# ============================================================================
# API 配置 - 多源支援
# ============================================================================

def get_project_root_early():
    """早期獲取專案根目錄（在 PROJECT_ROOT 全域性變數定義之前）"""
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.basename(path) == '.claude':
            return os.path.dirname(path)
        path = os.path.dirname(path)
    return os.getcwd()

def get_api_key():
    """
    獲取 Sorftime API Key
    優先順序: 環境變數 > .mcp.json 配置檔案
    """
    # 1. 嘗試環境變數
    api_key = os.environ.get('SORFTIME_API_KEY', '')
    if api_key:
        return api_key

    # 2. 嘗試從 .mcp.json 讀取
    project_root = get_project_root_early()
    mcp_config_path = os.path.join(project_root, '.mcp.json')

    if os.path.exists(mcp_config_path):
        try:
            with open(mcp_config_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            config = json.loads(content)

            # 從 URL 中提取 API key: https://mcp.sorftime.com?key=XXX
            sorftime_url = config.get('mcpServers', {}).get('sorftime', {}).get('url', '')
            if 'key=' in sorftime_url:
                api_key = sorftime_url.split('key=')[-1]
                if api_key:
                    print(f"  ✓ 從 .mcp.json 讀取 API Key")
                    return api_key
        except Exception as e:
            print(f"  ⚠ 讀取 .mcp.json 失敗: {e}")

    return ''


API_KEY = get_api_key()
API_URL = f'https://mcp.sorftime.com?key={API_KEY}'

# 專案路徑
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_project_root():
    """獲取專案根目錄（.claude 的父目錄）"""
    path = os.path.abspath(__file__)
    # 從指令碼位置向上查詢 .claude 目錄
    while path != os.path.dirname(path):
        if os.path.basename(path) == '.claude':
            return os.path.dirname(path)
        path = os.path.dirname(path)
    # 如果找不到，使用當前工作目錄
    return os.getcwd()

PROJECT_ROOT = get_project_root()


# ============================================================================
# 資料處理工具函式
# ============================================================================

def safe_int(value, default=0):
    """安全轉換為整數"""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        # 移除常見的非數字字元
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return int(float(cleaned)) if cleaned else default
        except ValueError:
            return default
    return default


def safe_float(value, default=0.0):
    """安全轉換為浮點數"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def fix_mojibake(text):
    """
    修復 Mojibake 編碼問題 (UTF-8/Latin-1 雙重編碼)

    問題: UTF-8 位元組被錯誤解釋為 Latin-1
    解決: 將錯誤編碼的字串重新編碼為 Latin-1，然後用 UTF-8 解碼
    """
    if isinstance(text, str):
        try:
            return text.encode('latin-1').decode('utf-8')
        except:
            return text
    elif isinstance(text, dict):
        return {fix_mojibake(k): fix_mojibake(v) for k, v in text.items()}
    elif isinstance(text, list):
        return [fix_mojibake(item) for item in text]
    return text


def escape_control_chars_in_json_strings(json_str):
    """
    轉義 JSON 字串值中的控制字元

    問題: API 返回的 JSON 字串值中包含原始的換行符、製表符等控制字元
    解決: 在保持 JSON 結構不變的情況下，只跳脫字元串值內的控制字元

    Args:
        json_str: 可能包含未轉義控制字元的 JSON 字串

    Returns:
        修復後的 JSON 字串
    """
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        c = json_str[i]

        if escape_next:
            # 已轉義，直接新增
            result.append(c)
            escape_next = False
            i += 1
            continue

        if c == '\\':
            result.append(c)
            escape_next = True
            i += 1
            continue

        if c == '"':
            in_string = not in_string
            result.append(c)
            i += 1
            continue

        # 在字串值內部，轉義控制字元
        if in_string:
            if c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            elif ord(c) < 32:
                # 其他控制字元 - 替換為空格或刪除
                result.append(' ')
            else:
                result.append(c)
        else:
            # 字串外部，保持不變
            result.append(c)

        i += 1

    return ''.join(result)


def clean_json_string(s):
    """清理 JSON 字串中的控制字元"""
    # 跳脫字元串值內的控制字元
    s = escape_control_chars_in_json_strings(s)

    # 移除所有剩餘的控制字元（保留必要的空白）
    s = ''.join(c for c in s if c == '\n' or c == '\t' or c == '\r' or c >= ' ')

    # 替換轉義序列
    s = s.replace('\\r\\n', ' ').replace('\\n', ' ').replace('\\t', ' ')
    return s


def python_dict_to_json(text):
    """將 Python dict 格式（單引號）轉換為 JSON 格式（雙引號）"""
    # 先替換 Python 字面量
    text = text.replace('True', 'true')
    text = text.replace('False', 'false')
    text = text.replace('None', 'null')

    # 轉換單引號為雙引號（注意不要處理字串內的單引號）
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(text):
        c = text[i]

        if escape_next:
            result.append(c)
            escape_next = False
            i += 1
            continue

        if c == '\\':
            result.append(c)
            escape_next = True
            i += 1
            continue

        if c == '"':
            in_string = not in_string
            result.append(c)
            i += 1
            continue

        # 只在非字串內的單引號轉換為雙引號
        if c == "'" and not in_string:
            result.append('"')
            i += 1
            continue

        result.append(c)
        i += 1

    return ''.join(result)


# ============================================================================
# 評分和分析函式
# ============================================================================

def calculate_hhi(products):
    """計算赫芬達爾-赫希曼指數 (HHI)"""
    if not products:
        return 0

    total_sales = sum(safe_int(p.get('月銷量', 0)) for p in products)
    if total_sales == 0:
        return 0

    hhi = sum((safe_int(p.get('月銷量', 0)) / total_sales) ** 2 for p in products)
    return round(hhi * 10000, 2)


def calculate_cr(products, n=3):
    """計算前 N 大品牌集中度 (CR)"""
    if not products:
        return 0

    total_sales = sum(safe_int(p.get('月銷量', 0)) for p in products)
    if total_sales == 0:
        return 0

    brand_sales = {}
    for p in products:
        brand = p.get('品牌', 'Unknown')
        brand_sales[brand] = brand_sales.get(brand, 0) + safe_int(p.get('月銷量', 0))

    top_brands = sorted(brand_sales.values(), reverse=True)[:n]
    cr = sum(top_brands) / total_sales * 100
    return round(cr, 2)


def analyze_brand_distribution(products):
    """分析品牌分佈"""
    brand_data = {}
    for p in products:
        brand = p.get('品牌', 'Unknown')
        if brand not in brand_data:
            brand_data[brand] = {'count': 0, 'sales': 0, 'revenue': 0}
        brand_data[brand]['count'] += 1
        brand_data[brand]['sales'] += safe_int(p.get('月銷量', 0))
        brand_data[brand]['revenue'] += safe_float(p.get('月銷額', 0))

    sorted_brands = sorted(brand_data.items(), key=lambda x: x[1]['sales'], reverse=True)
    return sorted_brands


def analyze_seller_source(products):
    """分析賣家來源"""
    seller_stats = {'Amazon': 0, '美國': 0, '中國': 0, '其他': 0}
    for p in products:
        source = p.get('賣家來源', p.get('賣家', '其他'))
        if 'Amazon' in str(source):
            seller_stats['Amazon'] += 1
        elif '美國' in str(source):
            seller_stats['美國'] += 1
        elif '中國' in str(source) or 'CN' in str(source) or '中國香港' in str(source):
            seller_stats['中國'] += 1
        else:
            seller_stats['其他'] += 1

    total = len(products)
    return {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in seller_stats.items()}


def calculate_five_dimension_score(data):
    """
    計算五維評分 (標準版本 - 與需求文件一致)

    評分標準:
    - 市場規模 (20分): >$10M=20, >$5M=17, >$1M=14, 其他=10
    - 增長潛力 (25分): 低評論產品佔比>40%=22, >20%=18, 其他=14
    - 競爭烈度 (20分): Top3品牌佔比<30%=18, <50%=14, 其他=8
    - 進入壁壘 (20分): Amazon佔比<20%且新品>40%=20, 其他組合6-18分
    - 利潤空間 (15分): 均價>$300=12, >$150=10, >$50=7, 其他=4
    """
    products = data.get('Top100產品', [])
    # 支援兩種鍵名
    stats = data.get('類目統計報告', data.get('統計資料', {}))

    scores = {}

    # 1. 市場規模 (20分) - 基於類目月銷額
    monthly_revenue = safe_float(stats.get('top100產品月銷額', stats.get('類目月銷額', 0)))
    if monthly_revenue > 10000000:
        scores['市場規模'] = 20
    elif monthly_revenue > 5000000:
        scores['市場規模'] = 17
    elif monthly_revenue > 1000000:
        scores['市場規模'] = 14
    else:
        scores['市場規模'] = 10

    # 2. 增長潛力 (25分) - 基於低評論產品佔比 (評論數<100)
    low_review_products = sum(1 for p in products if safe_int(p.get('評論數', 0)) < 100)
    low_review_ratio = low_review_products / len(products) * 100 if products else 0

    if low_review_ratio > 40:
        scores['增長潛力'] = 22
    elif low_review_ratio > 20:
        scores['增長潛力'] = 18
    else:
        scores['增長潛力'] = 14

    # 3. 競爭烈度 (20分) - 基於 Top3 品牌佔比 (CR3)
    cr3 = calculate_cr(products, 3)
    if cr3 < 30:
        scores['競爭烈度'] = 18
    elif cr3 < 50:
        scores['競爭烈度'] = 14
    else:
        scores['競爭烈度'] = 8

    # 4. 進入壁壘 (20分) - Amazon 佔比 + 新品機會
    amazon_count = sum(1 for p in products if p.get('賣家') == 'Amazon' or 'Amazon' in str(p.get('賣家', '')))
    amazon_ratio = amazon_count / len(products) * 100 if products else 0

    # Amazon 佔比評分 (0-10分): 佔比越低，壁壘越小
    if amazon_ratio < 20:
        amazon_score = 10
    elif amazon_ratio < 40:
        amazon_score = 6
    else:
        amazon_score = 3

    # 新品機會評分 (0-10分): 新品越多，壁壘越小
    if low_review_ratio > 40:
        new_product_score = 10
    elif low_review_ratio > 20:
        new_product_score = 6
    else:
        new_product_score = 3

    scores['進入壁壘'] = amazon_score + new_product_score

    # 5. 利潤空間 (15分) - 基於平均價格
    avg_price = sum(safe_float(p.get('價格', 0)) for p in products) / len(products) if products else 0
    if avg_price > 300:
        scores['利潤空間'] = 12
    elif avg_price > 150:
        scores['利潤空間'] = 10
    elif avg_price > 50:
        scores['利潤空間'] = 7
    else:
        scores['利潤空間'] = 4

    total_score = sum(scores.values())
    return scores, total_score


def get_rating(total_score):
    """獲取評級"""
    if total_score >= 80:
        return "優秀", "強烈推薦進入"
    elif total_score >= 70:
        return "良好", "可以考慮進入"
    elif total_score >= 50:
        return "一般", "謹慎進入"
    else:
        return "較差", "不建議進入"


def generate_markdown_report(data, scores, total_score, category_name, site):
    """生成 Markdown 報告"""
    products = data.get('Top100產品', [])
    stats = data.get('類目統計報告', data.get('統計資料', {}))

    hhi = calculate_hhi(products)
    cr3 = calculate_cr(products, 3)
    brand_distribution = analyze_brand_distribution(products)
    seller_source = analyze_seller_source(products)

    rating, recommendation = get_rating(total_score)
    top10 = products[:10]

    avg_price = sum(safe_float(p.get('價格', 0)) for p in products) / len(products) if products else 0
    monthly_revenue = safe_float(stats.get('top100產品月銷額', stats.get('類目月銷額', 0)))
    monthly_sales = sum(safe_int(p.get('月銷量', 0)) for p in products)
    avg_reviews = sum(safe_int(p.get('評論數', 0)) for p in products) / len(products) if products else 0
    avg_rating = sum(safe_float(p.get('星級', 0)) for p in products) / len(products) if products else 0

    # Amazon 佔比
    amazon_count = sum(1 for p in products if p.get('賣家') == 'Amazon' or 'Amazon' in str(p.get('賣家', '')))
    amazon_ratio = amazon_count / len(products) * 100 if products else 0

    # 低評論產品佔比
    low_review_products = sum(1 for p in products if safe_int(p.get('評論數', 0)) < 100)
    low_review_ratio = low_review_products / len(products) * 100 if products else 0

    report = f"""# {category_name} ({site}) 品類選品分析報告

> 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 資料來源: Sorftime Amazon 資料服務

---

## 一、執行摘要

| 評估維度 | 得分 | 滿分 |
|---------|------|------|
| **市場規模** | {scores.get('市場規模', 0)}/20 | 20 |
| **增長潛力** | {scores.get('增長潛力', 0)}/25 | 25 |
| **競爭烈度** | {scores.get('競爭烈度', 0)}/20 | 20 |
| **進入壁壘** | {scores.get('進入壁壘', 0)}/20 | 20 |
| **利潤空間** | {scores.get('利潤空間', 0)}/15 | 15 |
| **總分** | **{total_score}/100** | 100 |

**評級**: {rating}
**選品建議**: {recommendation}

---

## 二、市場概況

### 2.1 類目基本資訊
- **類目名稱**: {category_name}
- **Amazon 站點**: {site}

### 2.2 關鍵指標

| 指標 | 數值 |
|------|------|
| 類目月銷量 | {monthly_sales:,} |
| 類目月銷額 | ${monthly_revenue:,.2f} |
| 分析產品數量 | {len(products)} |
| 平均價格 | ${avg_price:.2f} |
| 平均評論數 | {avg_reviews:.0f} |
| 平均星級 | {avg_rating:.2f} |

### 2.3 市場集中度
- **HHI 指數**: {hhi} ({'低集中度' if hhi < 1500 else '中等集中度' if hhi < 2500 else '高集中度'})
- **CR3 (前三品牌集中度)**: {cr3}%
- **Amazon 自營佔比**: {amazon_ratio:.1f}%
- **低評論產品佔比** (評論數<100): {low_review_ratio:.1f}%

---

## 三、品牌分析

### 3.1 Top 品牌 (按銷量)

| 排名 | 品牌 | 產品數 | 月銷量 | 月銷額 |
|------|------|--------|--------|--------|
"""

    for i, (brand, info) in enumerate(brand_distribution[:10], 1):
        report += f"| {i} | {brand} | {info['count']} | {info['sales']:,} | ${info['revenue']:,.2f} |\n"

    report += f"""

### 3.2 賣家來源分佈

| 來源 | 佔比 |
|------|------|
| Amazon 自營 | {seller_source['Amazon']}% |
| 美國賣家 | {seller_source['美國']}% |
| 中國賣家 | {seller_source['中國']}% |
| 其他/未知 | {seller_source['其他']}% |

---

## 四、Top 10 熱銷產品

| 排名 | ASIN | 產品標題 | 價格 | 月銷量 | 月銷額 | 評論數 | 星級 | 品牌 |
|------|------|----------|------|--------|--------|--------|------|------|
"""

    for i, p in enumerate(top10, 1):
        title = p.get('標題', 'N/A')[:60] + '...' if len(p.get('標題', '')) > 60 else p.get('標題', 'N/A')
        price = safe_float(p.get('價格', 0))
        sales = safe_int(p.get('月銷量', 0))
        revenue = safe_float(p.get('月銷額', 0))
        reviews = safe_int(p.get('評論數', 0))
        rating = safe_float(p.get('星級', 0))
        asin = p.get('ASIN', 'N/A')
        report += f"| {i} | [{asin}](https://www.amazon.com/dp/{asin}) | {title} | ${price:.2f} | {sales:,} | ${revenue:,.2f} | {reviews:,} | {rating:.1f} | {p.get('品牌', 'N/A')} |\n"

    report += f"""

---

## 五、選品建議

### 5.1 市場機會
- 該品類市場規模{'較大' if scores.get('市場規模', 0) >= 17 else '中等' if scores.get('市場規模', 0) >= 14 else '較小'}
- 競爭{'相對溫和' if cr3 < 40 else '較為激烈'}
- {'存在' if seller_source['中國'] > 20 else '較少'}中國賣家機會
- 低評論產品佔比 {low_review_ratio:.1f}%，{'新品機會較大' if low_review_ratio > 30 else '新品有一定機會' if low_review_ratio > 15 else '新品機會較少'}

### 5.2 進入策略
- 建議定價範圍: ${avg_price * 0.7:.2f} - ${avg_price * 1.3:.2f}
- 關注差異化產品和細分市場
- 重視產品質量以獲取好評
- {'Amazon 佔比較高，需注意價格競爭' if amazon_ratio > 30 else 'Amazon 佔比較低，第三方賣家機會較大'}

### 5.3 風險提示
- {'Amazon 自營佔比較高，需注意價格競爭' if amazon_ratio > 30 else 'Amazon 自營佔比較低'}
- 頭部品牌已建立一定優勢（CR3 = {cr3}%）
- 新產品需要投入營銷獲取初期銷量
- 平均評論數 {avg_reviews:.0f}，{'評論門檻較高' if avg_reviews > 500 else '評論門檻適中' if avg_reviews > 100 else '評論門檻較低'}

---

*本報告由 Claude Code 自動生成 | 資料來源: Sorftime*
"""

    return report


# ============================================================================
# 主工作流類
# ============================================================================

class CategoryAnalysisWorkflow:
    """品類選品分析工作流 v4.0"""

    def __init__(self, category: str, site: str = 'US', limit: int = 20, node_id: str = None):
        self.category = category
        self.site = site.upper()
        self.limit = limit
        self.node_id = node_id
        self.output_dir = ''
        self.request_id = 0
        self.data = None  # 儲存解析後的完整資料
        self.execution_log = []  # 執行日誌

    def log(self, message: str, level: str = 'INFO'):
        """記錄日誌"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.execution_log.append(log_entry)
        print(f"  {message}")

    def check_api_key(self):
        """檢查 API Key 是否可用"""
        if not API_KEY:
            self.log("❌ API Key 未設定", "ERROR")
            self.log("請設定 SORFTIME_API_KEY 環境變數，或在 .mcp.json 中配置", "ERROR")
            return False
        self.log(f"✓ API Key 已配置 (長度: {len(API_KEY)})")
        return True

    def _curl_request(self, tool_name: str, arguments: dict) -> dict:
        """執行 curl 請求，返回解析後的結果"""
        self.request_id += 1
        args_str = json.dumps(arguments, ensure_ascii=False)

        cmd = [
            'curl', '-s', '-X', 'POST', API_URL,
            '-H', 'Content-Type: application/json',
            '-d', f'{{"jsonrpc":"2.0","id":{self.request_id},"method":"tools/call","params":{{"name":"{tool_name}","arguments":{args_str}}}}}'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding='utf-8', errors='ignore')
            return self._parse_sse_response(result.stdout)
        except subprocess.TimeoutExpired:
            self.log(f"⏱ 請求超時 (tool: {tool_name})", "WARN")
            return {'text': '', 'error': 'Timeout', 'has_error': True}
        except Exception as e:
            self.log(f"✗ 請求失敗: {e}", "ERROR")
            return {'text': '', 'error': str(e), 'has_error': True}

    def _parse_sse_response(self, response: str) -> dict:
        """解析 SSE 響應，返回文字內容"""
        result = {'text': '', 'error': None, 'has_error': False}

        for line in response.split('\n'):
            if line.startswith('data: '):
                json_text = line[6:]
                try:
                    data = json.loads(json_text)
                    result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                    if result_text:
                        # 解碼 Unicode 轉義
                        decoded = codecs.decode(result_text, 'unicode-escape')
                        # 修復 Mojibake
                        decoded = fix_mojibake(decoded)
                        result['text'] = decoded
                        return result
                except json.JSONDecodeError as e:
                    result['error'] = str(e)
                    result['has_error'] = True

        # 檢查錯誤響應
        if 'error' in response.lower() or 'isError' in response or 'Authentication required' in response:
            result['has_error'] = True
            if 'Authentication required' in response:
                result['error'] = 'Authentication failed - Invalid API Key'

        return result

    def _parse_business_data(self, text_content: str) -> dict:
        """
        從 API 返回的文字內容中解析業務資料

        處理多種可能的格式:
        1. 純 JSON 格式
        2. 帶字首的 JSON
        3. Python dict 格式（單引號）
        4. 需要清理控制字元的 JSON
        """
        # 1. 跳脫字元串值內的控制字元（關鍵修復）
        text_content = escape_control_chars_in_json_strings(text_content)

        # 2. 清理剩餘控制字元
        text_content = clean_json_string(text_content)

        # 3. 找到 JSON 開始位置
        json_start = text_content.find('{')
        if json_start == -1:
            self.log("未找到 JSON 資料", "ERROR")
            return None

        # 4. 使用括號匹配提取完整的 JSON/Python dict
        json_str = self._extract_braced_content(text_content, json_start)
        if not json_str:
            self.log("無法提取完整的 JSON 資料", "ERROR")
            return None

        # 5. 轉換 Python dict 格式為 JSON 格式
        json_str = python_dict_to_json(json_str)

        # 6. 嘗試解析
        try:
            data = json.loads(json_str)
            # 修復所有字串的編碼
            data = fix_mojibake(data)
            return data
        except json.JSONDecodeError as e:
            self.log(f"⚠ JSON 解析失敗: {e}", "ERROR")
            # 儲存解析失敗的文字用於除錯
            debug_file = os.path.join(self.output_dir, 'parse_debug.txt')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(f"Error: {e}\n")
                f.write(f"JSON start: {json_start}\n")
                f.write(f"JSON length: {len(json_str)}\n")
                f.write(f"First 500 chars:\n{json_str[:500]}\n")
            self.log(f"除錯資訊已儲存: {debug_file}", "DEBUG")
            return None

    def _extract_braced_content(self, text: str, start: int) -> str:
        """使用括號匹配提取花括號內容"""
        if start >= len(text) or text[start] != '{':
            return None

        depth = 0
        in_string = False
        escape_next = False

        for i in range(start, len(text)):
            c = text[i]

            if escape_next:
                escape_next = False
                continue

            if c == '\\':
                escape_next = True
                continue

            if c == '"':
                in_string = not in_string
                continue

            if not in_string:
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        return text[start:i+1]

        return None

    def step1_search_category(self):
        """步驟1: 搜尋類目獲取 nodeId"""
        print(f"\n{'='*70}")
        print(f"步驟1: 搜尋類目 '{self.category}'")
        print('='*70)

        # 如果已提供 NodeID，跳過搜尋
        if self.node_id:
            self.log(f"使用提供的 NodeId: {self.node_id}")
            return True

        result = self._curl_request('category_name_search', {
            'amzSite': self.site,
            'searchName': self.category
        })

        text = result.get('text', '')

        if 'Authentication required' in text or 'Authentication failed' in str(result.get('error', '')):
            self.log("認證失敗，請檢查 API Key", "ERROR")
            return False

        # 嘗試多種搜尋策略
        search_variants = [
            self.category,
            self.category.replace(' & ', ' '),
            self.category.split(' ')[0],  # 第一個詞
            self.category.rstrip('s'),  # 移除複數
        ]

        for variant in search_variants:
            if variant == self.category:
                continue  # 已經嘗試過

            if '未查詢到對應類目' in text or not text:
                self.log(f"嘗試搜尋變體: '{variant}'")
                result = self._curl_request('category_name_search', {
                    'amzSite': self.site,
                    'searchName': variant
                })
                text = result.get('text', '')
                if text and '未查詢到對應類目' not in text:
                    self.category = variant
                    self.log(f"找到匹配類目: {variant}")
                    break

        if '未查詢到對應類目' in text or not text:
            self.log(f"未找到類目: {self.category}", "ERROR")
            return False

        # 提取 NodeID
        match = re.search(r'"NodeId":"?(\d+)"?', text)
        if match:
            self.node_id = match.group(1)
            self.log(f"找到類目 NodeId: {self.node_id}")
            return True

        # 檢查是否返回了多個類目
        if '"Name"' in text and '"NodeId"' in text:
            self.log("API 返回了多個類目，請選擇更具體的類目名稱", "WARN")
            # 嘗試提取第一個類目
            matches = re.findall(r'"Name":"([^"]+)","NodeId":"(\d+)"', text)
            if matches:
                self.log("找到以下類目選項:", "INFO")
                for i, (name, nid) in enumerate(matches[:5], 1):
                    self.log(f"  {i}. {name} (NodeID: {nid})")
                # 使用第一個
                self.node_id = matches[0][1]
                self.category = matches[0][0]
                self.log(f"使用第一個類目: {self.category}")
                return True

        self.log("未找到匹配的類目", "ERROR")
        return False

    def step2_get_category_report(self):
        """步驟2: 獲取並解析類目報告"""
        print(f"\n{'='*70}")
        print("步驟2: 獲取類目報告 (Top100 + 統計資料)")
        print('='*70)

        response = self._curl_request('category_report', {
            'amzSite': self.site,
            'nodeId': self.node_id
        })

        text = response.get('text', '')

        if 'Authentication required' in text:
            self.log("認證失敗，請檢查 API Key", "ERROR")
            return False

        if '沒有相關資料' in text or not text:
            self.log(f"該類目暫無資料: {self.node_id}", "ERROR")
            return False

        # 儲存原始響應（用於除錯）
        temp_file = os.path.join(self.output_dir, 'category_report_raw.txt')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write("event: message\n")
            f.write(f"data: {{\"result\":{{\"content\":[{{\"type\":\"text\",\"text\":\"{text}\"}}]}}}}\n")
        self.log(f"原始響應已儲存: {temp_file}")

        # 解析業務資料
        self.log("正在解析業務資料...")
        self.data = self._parse_business_data(text)

        if not self.data:
            self.log("資料解析失敗", "ERROR")
            return False

        products = self.data.get('Top100產品', [])
        stats = self.data.get('類目統計報告', self.data.get('統計資料', {}))

        self.log(f"✓ 解析成功")
        self.log(f"  - Top100產品數量: {len(products)}")
        monthly_revenue = safe_float(stats.get('top100產品月銷額', stats.get('類目月銷額', 0)))
        self.log(f"  - 類目月銷額: ${monthly_revenue:,.2f}")

        return True

    def step3_generate_report(self):
        """步驟3: 生成分析報告"""
        print(f"\n{'='*70}")
        print("步驟3: 生成分析報告")
        print('='*70)

        if not self.data:
            self.log("沒有可用的資料", "ERROR")
            return False

        # 計算五維評分
        scores, total_score = calculate_five_dimension_score(self.data)
        print(f"\n五維評分: {total_score}/100")
        for k, v in scores.items():
            print(f"  - {k}: {v}")

        # 生成 Markdown 報告
        report = generate_markdown_report(self.data, scores, total_score, self.category, self.site)
        report_file = os.path.join(self.output_dir, "report.md")

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        self.log(f"✓ 報告已生成: {report_file}")

        # 儲存資料
        data_file = os.path.join(self.output_dir, "data.json")
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        self.log(f"✓ 資料已儲存: {data_file}")

        # 儲存評分
        scores_file = os.path.join(self.output_dir, "scores.json")
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump({"scores": scores, "total_score": total_score}, f, ensure_ascii=False, indent=2)
        self.log(f"✓ 評分已儲存: {scores_file}")

        # 儲存 TopN 產品
        products = self.data.get('Top100產品', [])
        top_n = products[:self.limit]
        top_n_file = os.path.join(self.output_dir, "top_products.json")
        with open(top_n_file, 'w', encoding='utf-8') as f:
            json.dump(top_n, f, ensure_ascii=False, indent=2)
        self.log(f"✓ Top{self.limit} 產品已儲存: {top_n_file}")

        return True

    def run(self):
        """執行完整工作流"""
        print("\n" + "="*70)
        print(f"品類選品分析: {self.category} ({self.site})")
        print("="*70)

        # 檢查 API Key
        if not self.check_api_key():
            return False

        # 建立輸出目錄
        date_str = datetime.now().strftime('%Y%m%d')
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', self.category).replace(' ', '_')
        safe_name = safe_name[:50]
        self.output_dir = os.path.join(PROJECT_ROOT, 'category-reports', f'{safe_name}_{self.site}_{date_str}')
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"\n輸出目錄: {self.output_dir}")

        # 執行工作流
        success = True
        if not self.step1_search_category():
            self.log("類目搜尋失敗", "ERROR")
            success = False

        if success and not self.step2_get_category_report():
            self.log("獲取類目報告失敗", "ERROR")
            success = False

        if success and not self.step3_generate_report():
            self.log("報告生成失敗", "ERROR")
            success = False

        # 儲存執行日誌
        log_file = os.path.join(self.output_dir, "execution.log")
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.execution_log))

        # 列印總結
        print("\n" + "="*70)
        if success:
            print("✓ 分析完成!")
            print(f"報告位置: {self.output_dir}/report.md")
        else:
            print("✗ 分析失敗，請檢視錯誤資訊")
        print("="*70)

        return success


# ============================================================================
# 命令列入口
# ============================================================================

def main():
    if len(sys.argv) < 3:
        print("用法: python workflow.py <品類名稱|NodeID> <站點> [分析數量]")
        print("示例: python workflow.py \"Sofas\" US 20")
        print("示例: python workflow.py 679394011 US 20")
        sys.exit(1)

    # 解析引數
    category_or_nodeid = sys.argv[1]
    site = sys.argv[2] if len(sys.argv) > 2 else 'US'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    # 判斷是品類名稱還是 NodeID
    node_id = None
    category = category_or_nodeid

    if category_or_nodeid.isdigit():
        node_id = category_or_nodeid
        category = f"NodeID_{category_or_nodeid}"

    # 執行工作流
    workflow = CategoryAnalysisWorkflow(category, site, limit, node_id)
    success = workflow.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
