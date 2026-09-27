#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime API 客戶端 - 統一的資料採集介面

v2.2 - 修復大檔案 JSON 解析問題

為 product-research Skill 提供簡潔的 API 呼叫方法:
- 自動從 .mcp.json 讀取 API Key
- SSE 響應解析
- Mojibake 編碼修復
- 控制字元轉義（在 Unicode 解碼後執行）
- 返回乾淨的 Python dict

使用示例:
    from scripts.api_client import SorftimeClient

    client = SorftimeClient()

    # 獲取類目 Top100
    top100 = client.get_category_report(site="US", node_id=12345)

    # 獲取關鍵詞詳情
    keyword = client.get_keyword_detail(site="US", keyword="your keyword")

    # 獲取產品詳情
    product = client.get_product_detail(site="US", asin="B0XXXXXXXX")

    # 獲取產品評論
    reviews = client.get_product_reviews(site="US", asin="B0XXXXXXXX", review_type="Negative")
"""

import os
import json
import re
import codecs
import subprocess
import sys
from datetime import datetime
from typing import Optional, Dict, List, Any
from pathlib import Path


# ============================================================================
# API 配置
# ============================================================================

def get_project_root():
    """獲取專案根目錄（.claude 的父目錄）"""
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.basename(path) == '.claude':
            return os.path.dirname(path)
        path = os.path.dirname(path)
    return os.getcwd()


def get_api_key():
    """
    從 .mcp.json 讀取 Sorftime API Key

    Returns:
        str: API Key
    """
    project_root = get_project_root()
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
                    return api_key
        except Exception as e:
            print(f"⚠ 讀取 .mcp.json 失敗: {e}")

    # 嘗試環境變數
    api_key = os.environ.get('SORFTIME_API_KEY', '')
    if api_key:
        return api_key

    raise ValueError(
        "API Key 未找到。請確保:\n"
        "1. .mcp.json 檔案存在幷包含 sorftime 配置，或\n"
        "2. 設定環境變數 SORFTIME_API_KEY"
    )


# ============================================================================
# 資料處理工具函式
# ============================================================================

def safe_int(value, default=0):
    """安全轉換為整數"""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
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
    """
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        c = json_str[i]

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

        if in_string:
            if c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            elif ord(c) < 32:
                result.append(' ')
            else:
                result.append(c)
        else:
            result.append(c)
        i += 1

    return ''.join(result)


def extract_json_object(text):
    """
    從文字中提取完整的 JSON 物件

    使用括號匹配演算法，支援巢狀結構
    """
    stack = []
    start_idx = None

    for i, char in enumerate(text):
        if char in '{[':
            if not stack:
                start_idx = i
            stack.append(char)
        elif char in '}]':
            if stack:
                expected = '}' if char == '}' else ']'
                opening = '{' if expected == '}' else '['
                if stack[-1] == opening:
                    stack.pop()
                    if not stack:
                        json_str = text[start_idx:i+1]
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue

    return None


def decode_sse_response(content):
    """
    解碼 Sorftime SSE 響應

    處理流程:
    1. 清理控制字元
    2. 解析 SSE 格式 (event: message, data: {...})
    3. Unicode 解碼
    4. Mojibake 修復
    5. 提取 JSON 物件

    Args:
        content: SSE 響應內容（字串）

    Returns:
        dict: 解碼後的資料
    """
    # 清理控制字元
    content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', content)

    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 字首
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # Unicode 解碼
                    decoded = codecs.decode(result_text, 'unicode-escape')

                    # Mojibake 修復
                    decoded = fix_mojibake(decoded)

                    # 轉義 JSON 字串值內的控制字元（關鍵步驟！）
                    decoded = escape_control_chars_in_json_strings(decoded)

                    # 清理剩餘的控制字元
                    decoded = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', decoded)

                    # 提取 JSON
                    json_obj = extract_json_object(decoded)
                    if json_obj:
                        return json_obj
            except Exception:
                continue

    # 如果 SSE 解析失敗，嘗試直接解析
    try:
        return json.loads(content)
    except:
        pass

    return None


# ============================================================================
# Sorftime API 客戶端
# ============================================================================

class SorftimeClient:
    """
    Sorftime API 客戶端

    提供簡潔的方法呼叫 Sorftime MCP API
    """

    # API 工具名稱對映
    TOOLS = {
        # 類目相關
        'search_categories_broadly': 'search_categories_broadly',  # 多維度廣泛搜尋類目
        'category_name_search': 'category_name_search',  # 按類目名稱搜尋（使用 searchName 引數）
        'category_report': 'category_report',
        'category_trend': 'category_trend',
        'category_keywords': 'category_keywords',

        # 關鍵詞相關
        'keyword_detail': 'keyword_detail',
        'keyword_search_results': 'keyword_search_results',
        'keyword_extends': 'keyword_extends',
        'keyword_trend': 'keyword_trend',

        # 產品相關
        'product_detail': 'product_detail',
        'product_reviews': 'product_reviews',
        'product_traffic_terms': 'product_traffic_terms',
        'product_trend': 'product_trend',
        'product_search': 'product_search',

        # 選品相關
        'potential_product': 'potential_product',
        'competitor_product_keywords': 'competitor_product_keywords',

        # 供應鏈
        'ali1688': 'ali1688_similar_product',
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客戶端

        Args:
            api_key: Sorftime API Key，如果不提供則從 .mcp.json 讀取
        """
        self.api_key = api_key or get_api_key()
        self.api_url = f'https://mcp.sorftime.com?key={self.api_key}'
        self.request_id = 0

    def _call(self, tool_name: str, arguments: Dict[str, Any]) -> tuple:
        """
        呼叫 Sorftime API

        Args:
            tool_name: API 工具名稱
            arguments: API 引數

        Returns:
            tuple: (解析後的資料 dict, 原始響應 str)
        """
        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            result = subprocess.run(
                ['curl', '-s', '-X', 'POST', self.api_url,
                 '-H', 'Content-Type: application/json',
                 '-H', 'Accept: application/json, text/event-stream',
                 '-d', json.dumps(payload)],
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )

            # 返回原始響應和解析後的資料
            raw_response = result.stdout
            data = decode_sse_response(raw_response)

            if data is None:
                # 即使解析失敗，也返回原始響應供除錯
                return None, raw_response

            return data, raw_response

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"API 呼叫失敗: {e}")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"API 呼叫超時")

    # ========================================================================
    # 類目相關 API
    # ========================================================================

    def search_category_by_product_name(
        self,
        site: str,
        product_name: str
    ) -> Dict[str, Any]:
        """
        按產品名稱搜尋類目

        Args:
            site: 站點 (US, GB, DE, FR, IT, ES, CA, JP, etc.)
            product_name: 產品名稱

        Returns:
            dict: 搜尋結果，包含類目列表
        """
        return self._call(
            self.TOOLS['category_name_search'],
            {"amzSite": site, "searchName": product_name}  # 注意: 引數是 searchName
        )

    def search_category_by_name(
        self,
        site: str,
        category_name: str
    ) -> Dict[str, Any]:
        """
        按類目名稱搜尋（別名方法，與 search_category_by_product_name 相同）

        Args:
            site: 站點
            category_name: 類目名稱

        Returns:
            dict: 搜尋結果
        """
        return self.search_category_by_product_name(site, category_name)

    def search_categories_broadly(
        self,
        site: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        多維度廣泛搜尋類目（新增 - 用於藍海發現）

        Args:
            site: 站點 (US, GB, DE, FR, IT, ES, CA, JP, etc.)
            filters: 篩選條件（可選）
                - top3Product_sales_share: Top3 產品銷量佔比上限（如 0.4 表示<40%）
                - top3Brands_sales_share: Top3 品牌銷量佔比上限
                - newProductSalesAmountShare: 新品銷量佔比下限（如 0.15 表示>15%）
                - brandCount: 品牌數量下限（如 80 表示>80 個品牌）
                - priceRange_min: 價格範圍下限
                - priceRange_max: 價格範圍上限
                - monthlySales_min: 月銷量下限
                - monthlySales_max: 月銷量上限

        Returns:
            dict: 類目列表，包含：
                - categories: 類目列表
                - total: 總數
        """
        params = {"amzSite": site}
        if filters:
            params.update(filters)
        return self._call(
            self.TOOLS['search_categories_broadly'],
            params
        )

    def get_category_report(
        self,
        site: str,
        node_id: int
    ) -> Dict[str, Any]:
        """
        獲取類目 Top100 報告

        Args:
            site: 站點
            node_id: 類目 Node ID

        Returns:
            dict: Top100 產品資料
        """
        return self._call(
            self.TOOLS['category_report'],
            {"amzSite": site, "nodeId": str(node_id)}
        )

    def get_category_trend(
        self,
        site: str,
        node_id: int,
        trend_index: str = "NewProductSalesAmountShare"
    ) -> Dict[str, Any]:
        """
        獲取類目趨勢資料

        Args:
            site: 站點
            node_id: 類目 Node ID
            trend_index: 趨勢型別
                - NewProductSalesAmountShare: 新品銷量佔比
                - NewProductProductShare: 新品數量佔比
                - etc.

        Returns:
            dict: 結構化趨勢資料
                {
                    "trend_data": [
                        {"date": "2024-03", "value": 33.35},
                        ...
                    ],
                    "metric": "新品佔比",
                    "node_id": "99530371011"
                }
        """
        raw_data, raw_response = self._call(
            self.TOOLS['category_trend'],
            {"amzSite": site, "nodeId": str(node_id), "trendIndex": trend_index}
        )

        # 轉換原始格式為結構化格式
        # 原始格式: ["2024年03月=33.35", "2024年04月=27.94", ...]
        # 目標格式: {"trend_data": [{"date": "2024-03", "value": 33.35}, ...]}
        if isinstance(raw_data, list):
            trend_data = []
            for item in raw_data:
                if isinstance(item, str) and '=' in item:
                    # 解析 "2024年03月=33.35" 格式
                    date_str, value_str = item.split('=', 1)
                    # 轉換日期格式: "2024年03月" -> "2024-03"
                    date_match = re.search(r'(\d{4})年(\d{2})月', date_str)
                    if date_match:
                        year, month = date_match.groups()
                        formatted_date = f"{year}-{month}"
                        try:
                            value = float(value_str)
                            trend_data.append({
                                "date": formatted_date,
                                "value": value
                            })
                        except ValueError:
                            continue

            # 指標名稱對映
            metric_names = {
                "NewProductSalesAmountShare": "新品銷量佔比",
                "NewProductProductShare": "新品數量佔比",
            }

            return {
                "trend_data": trend_data,
                "metric": metric_names.get(trend_index, trend_index),
                "node_id": str(node_id),
                "site": site
            }

        return raw_data

    def get_category_keywords(
        self,
        site: str,
        node_id: int,
        page: int = 1
    ) -> Dict[str, Any]:
        """
        獲取類目關鍵詞

        Args:
            site: 站點
            node_id: 類目 Node ID
            page: 頁碼

        Returns:
            dict: 關鍵詞資料
        """
        return self._call(
            self.TOOLS['category_keywords'],
            {"amzSite": site, "nodeId": str(node_id), "page": page}
        )

    # ========================================================================
    # 關鍵詞相關 API
    # ========================================================================

    def get_keyword_detail(
        self,
        site: str,
        keyword: str
    ) -> Dict[str, Any]:
        """
        獲取關鍵詞詳情

        Args:
            site: 站點
            keyword: 關鍵詞

        Returns:
            dict: 關鍵詞詳情（搜尋量、CPC、自然位產品等）
        """
        return self._call(
            self.TOOLS['keyword_detail'],
            {"amzSite": site, "keyword": keyword}
        )

    def get_keyword_search_results(
        self,
        site: str,
        keyword: str
    ) -> Dict[str, Any]:
        """
        獲取關鍵詞搜尋結果（自然位產品）

        Args:
            site: 站點
            keyword: 關鍵詞

        Returns:
            dict: 自然位產品列表
        """
        return self._call(
            self.TOOLS['keyword_search_results'],
            {"amzSite": site, "searchKeyword": keyword}
        )

    def get_keyword_extends(
        self,
        site: str,
        keyword: str
    ) -> Dict[str, Any]:
        """
        獲取關鍵詞延伸詞

        Args:
            site: 站點
            keyword: 關鍵詞

        Returns:
            dict: 延伸詞列表
        """
        return self._call(
            self.TOOLS['keyword_extends'],
            {"amzSite": site, "keyword": keyword}
        )

    # ========================================================================
    # 產品相關 API
    # ========================================================================

    def get_product_detail(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        獲取產品詳情

        Args:
            site: 站點
            asin: 產品 ASIN

        Returns:
            dict: 產品詳情
        """
        return self._call(
            self.TOOLS['product_detail'],
            {"amzSite": site, "asin": asin}
        )

    def get_product_reviews(
        self,
        site: str,
        asin: str,
        review_type: str = "Both"
    ) -> Dict[str, Any]:
        """
        獲取產品評論

        Args:
            site: 站點
            asin: 產品 ASIN
            review_type: 評論型別 (Both, Positive, Negative)

        Returns:
            dict: 評論列表
        """
        return self._call(
            self.TOOLS['product_reviews'],
            {"amzSite": site, "asin": asin, "reviewType": review_type}
        )

    def get_product_traffic_terms(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        獲取產品流量關鍵詞（反查）

        Args:
            site: 站點
            asin: 產品 ASIN

        Returns:
            dict: 流量關鍵詞列表
        """
        return self._call(
            self.TOOLS['product_traffic_terms'],
            {"amzSite": site, "asin": asin}
        )

    def get_product_trend(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        獲取產品趨勢

        Args:
            site: 站點
            asin: 產品 ASIN

        Returns:
            dict: 趨勢資料
        """
        return self._call(
            self.TOOLS['product_trend'],
            {"amzSite": site, "asin": asin}
        )

    def search_products(
        self,
        site: str,
        search_name: str,
        **filters
    ) -> Dict[str, Any]:
        """
        搜尋產品

        Args:
            site: 站點
            search_name: 搜尋關鍵詞
            **filters: 篩選條件

        Returns:
            dict: 搜尋結果
        """
        params = {"amzSite": site, "searchName": search_name}
        params.update(filters)
        return self._call(self.TOOLS['product_search'], params)

    # ========================================================================
    # 選品相關 API
    # ========================================================================

    def get_potential_products(
        self,
        site: str,
        search_name: str,
        **filters
    ) -> Dict[str, Any]:
        """
        獲取潛力產品

        Args:
            site: 站點
            search_name: 搜尋關鍵詞
            **filters: 篩選條件

        Returns:
            dict: 潛力產品列表
        """
        params = {"amzSite": site, "searchName": search_name}
        params.update(filters)
        return self._call(self.TOOLS['potential_product'], params)

    def get_competitor_keywords(
        self,
        site: str,
        asin: str
    ) -> Dict[str, Any]:
        """
        獲取競品關鍵詞佈局

        Args:
            site: 站點
            asin: 產品 ASIN

        Returns:
            dict: 競品關鍵詞佈局
        """
        return self._call(
            self.TOOLS['competitor_product_keywords'],
            {"amzSite": site, "asin": asin}
        )

    # ========================================================================
    # 供應鏈 API
    # ========================================================================

    def get_1688_products(
        self,
        search_name: str
    ) -> Dict[str, Any]:
        """
        獲取 1688 相似產品

        Args:
            search_name: 搜尋關鍵詞

        Returns:
            dict: 1688 產品列表
        """
        return self._call(
            self.TOOLS['ali1688'],
            {"searchName": search_name}
        )


# ============================================================================
# 便捷函式
# ============================================================================

def create_client() -> SorftimeClient:
    """建立 Sorftime 客戶端（便捷函式）"""
    return SorftimeClient()


# ============================================================================
# 命令列介面
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sorftime API 客戶端")
    parser.add_argument("tool", choices=[
        "category_report", "keyword_detail", "product_detail",
        "product_reviews", "category_trend"
    ], help="API 工具名稱")
    parser.add_argument("--site", default="US", help="站點")
    parser.add_argument("--node-id", type=int, help="類目 Node ID")
    parser.add_argument("--keyword", help="關鍵詞")
    parser.add_argument("--asin", help="產品 ASIN")
    parser.add_argument("--output", "-o", help="輸出檔案路徑")

    args = parser.parse_args()

    client = SorftimeClient()

    if args.tool == "category_report":
        if not args.node_id:
            parser.error("--node-id 是必需的")
        result = client.get_category_report(args.site, args.node_id)

    elif args.tool == "keyword_detail":
        if not args.keyword:
            parser.error("--keyword 是必需的")
        result = client.get_keyword_detail(args.site, args.keyword)

    elif args.tool == "product_detail":
        if not args.asin:
            parser.error("--asin 是必需的")
        result = client.get_product_detail(args.site, args.asin)

    elif args.tool == "product_reviews":
        if not args.asin:
            parser.error("--asin 是必需的")
        result = client.get_product_reviews(args.site, args.asin)

    elif args.tool == "category_trend":
        if not args.node_id:
            parser.error("--node-id 是必需的")
        result = client.get_category_trend(args.site, args.node_id)

    # 輸出結果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✓ 結果已儲存到: {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
