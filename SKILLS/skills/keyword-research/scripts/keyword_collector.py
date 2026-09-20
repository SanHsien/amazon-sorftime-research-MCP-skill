#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
關鍵詞采集器 - 使用 Sorftime MCP API
最佳化版本：更好的錯誤處理、重試機制和除錯輸出
"""

import os
import sys
import json
import subprocess
import re
import time
from datetime import datetime
from collections import Counter

# 匯入資料解析工具
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from data_parser import (
    parse_sse_response,
    extract_keywords_from_response,
    normalize_keyword_data,
    safe_int,
    safe_float
)


class KeywordCollector:
    """從 Sorftime 採集關鍵詞"""

    # API 請求配置
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # 秒
    REQUEST_TIMEOUT = 120  # 秒

    def __init__(self, asin: str, site: str = 'US', verbose: bool = True):
        self.asin = asin.upper()
        self.site = site.upper()
        self.verbose = verbose
        self.api_url = self._get_api_url()
        self.request_id = 0
        self.collected_keywords = []
        self.errors = []  # 記錄錯誤資訊
        self.product_detail = None  # 儲存產品詳情

    def _log(self, message: str, level: str = 'INFO'):
        """輸出日誌"""
        if self.verbose:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"  [{timestamp}] [{level}] {message}")

    def _get_api_url(self) -> str:
        """從 .mcp.json 讀取 API URL"""
        # 獲取專案根目錄
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
        mcp_file = os.path.join(project_root, '.mcp.json')

        if not os.path.exists(mcp_file):
            # 嘗試從當前工作目錄向上查詢
            cwd = os.getcwd()
            while cwd != os.path.dirname(cwd):
                mcp_file = os.path.join(cwd, '.mcp.json')
                if os.path.exists(mcp_file):
                    break
                cwd = os.path.dirname(cwd)

        try:
            with open(mcp_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config['mcpServers']['sorftime']['url']
        except Exception as e:
            self._log(f"無法讀取 .mcp.json: {e}", 'ERROR')
            return None

    def _curl_request(self, tool_name: str, arguments: dict, retry: int = 0) -> dict:
        """
        執行 Sorftime API 請求（帶重試機制）

        Args:
            tool_name: API 工具名稱
            arguments: 請求引數
            retry: 當前重試次數

        Returns:
            dict: 解析後的響應資料
        """
        if not self.api_url:
            return {'has_error': True, 'error': 'API URL 未配置'}

        self.request_id += 1
        args_str = json.dumps(arguments, ensure_ascii=False)

        cmd = [
            'curl', '-s', '-X', 'POST', self.api_url,
            '-H', 'Content-Type: application/json',
            '-d', f'{{"jsonrpc":"2.0","id":{self.request_id},"method":"tools/call","params":{{"name":"{tool_name}","arguments":{args_str}}}}}'
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                   timeout=self.REQUEST_TIMEOUT, encoding='utf-8', errors='ignore')
            response = parse_sse_response(result.stdout)

            # 檢查是否有錯誤
            if response.get('has_error'):
                error_msg = response.get('error', 'Unknown error')
                self._log(f"API 返回錯誤: {error_msg}", 'WARN')

                # 如果是臨時錯誤，嘗試重試
                if retry < self.MAX_RETRIES and self._is_retryable_error(error_msg):
                    self._log(f"重試 {retry + 1}/{self.MAX_RETRIES}...", 'WARN')
                    time.sleep(self.RETRY_DELAY)
                    return self._curl_request(tool_name, arguments, retry + 1)

                return response

            # 檢查是否有資料
            if not response.get('data'):
                # 有些 API 返回空資料是正常的
                self._log(f"API 無返回資料", 'DEBUG')
                return response

            return response

        except subprocess.TimeoutExpired:
            error_msg = 'Request timeout'
            self._log(f"請求超時", 'ERROR')
            if retry < self.MAX_RETRIES:
                self._log(f"重試 {retry + 1}/{self.MAX_RETRIES}...", 'WARN')
                time.sleep(self.RETRY_DELAY)
                return self._curl_request(tool_name, arguments, retry + 1)
            return {'has_error': True, 'error': error_msg}

        except Exception as e:
            error_msg = str(e)
            self._log(f"請求異常: {error_msg}", 'ERROR')
            if retry < self.MAX_RETRIES and self._is_retryable_error(error_msg):
                self._log(f"重試 {retry + 1}/{self.MAX_RETRIES}...", 'WARN')
                time.sleep(self.RETRY_DELAY)
                return self._curl_request(tool_name, arguments, retry + 1)
            return {'has_error': True, 'error': error_msg}

    def _is_retryable_error(self, error_msg: str) -> bool:
        """判斷錯誤是否可以重試"""
        retryable_patterns = [
            'timeout', 'connection', 'network', 'temporary',
            '503', '502', '500', '429'  # HTTP 狀態碼
        ]
        error_lower = error_msg.lower()
        return any(pattern in error_lower for pattern in retryable_patterns)

    def collect_traffic_terms(self) -> list:
        """採集產品流量關鍵詞"""
        print(f"  [1/4] 採集產品流量詞...")
        response = self._curl_request('product_traffic_terms', {
            'amzSite': self.site,
            'asin': self.asin
        })

        if response.get('has_error'):
            print(f"    ⚠ 流量詞采集失敗: {response.get('error')}")
            self.errors.append({'step': 'traffic_terms', 'error': response.get('error')})
            return []

        keywords_data = extract_keywords_from_response(response.get('data', {}))
        keywords = [normalize_keyword_data(kw) for kw in keywords_data]
        keywords = [kw for kw in keywords if kw['keyword']]  # 過濾空關鍵詞

        print(f"    ✓ 採集到 {len(keywords)} 個流量詞")
        return keywords

    def collect_competitor_keywords(self) -> list:
        """採集競品佈局關鍵詞"""
        print(f"  [2/4] 採集競品佈局詞...")
        response = self._curl_request('competitor_product_keywords', {
            'amzSite': self.site,
            'asin': self.asin
        })

        if response.get('has_error'):
            print(f"    ⚠ 競品詞采集失敗: {response.get('error')}")
            self.errors.append({'step': 'competitor_keywords', 'error': response.get('error')})
            return []

        keywords_data = extract_keywords_from_response(response.get('data', {}))
        keywords = [normalize_keyword_data(kw) for kw in keywords_data]
        keywords = [kw for kw in keywords if kw['keyword']]

        print(f"    ✓ 採集到 {len(keywords)} 個競品詞")
        return keywords

    def collect_category_keywords(self, node_id: str = None) -> list:
        """採集類目核心關鍵詞"""
        print(f"  [3/4] 採集類目核心詞...")

        # 如果沒有提供 NodeID，先獲取產品詳情
        if not node_id:
            node_id = self._get_product_node_id()
            if not node_id:
                print(f"    ⚠ 無法獲取產品 NodeID，跳過類目詞采集")
                return []

        response = self._curl_request('category_keywords', {
            'amzSite': self.site,
            'nodeId': node_id
        })

        if response.get('has_error'):
            print(f"    ⚠ 類目詞采集失敗: {response.get('error')}")
            self.errors.append({'step': 'category_keywords', 'error': response.get('error')})
            return []

        keywords_data = extract_keywords_from_response(response.get('data', {}))
        keywords = [normalize_keyword_data(kw) for kw in keywords_data]
        keywords = [kw for kw in keywords if kw['keyword']]

        print(f"    ✓ 採集到 {len(keywords)} 個類目詞")
        return keywords

    def collect_long_tail_keywords(self, core_keywords: list, limit: int = 30) -> list:
        """
        透過分頁獲取更多關鍵詞（使用 product_traffic_terms 和 competitor_product_keywords 的多頁資料）

        Args:
            core_keywords: 核心關鍵詞列表（用於確定採集數量）
            limit: 嘗試獲取的額外頁數
        """
        print(f"  [4/4] 擴充套件長尾詞（透過分頁）...")

        long_tail = []
        success_count = 0
        fail_count = 0

        # 策略1: 獲取 product_traffic_terms 的多頁資料
        print(f"    策略1: 獲取產品流量詞的額外頁面...")
        max_pages = limit
        for page in range(2, max_pages + 2):
            print(f"    獲取流量詞第 {page} 頁...", end='', flush=True)

            response = self._curl_request('product_traffic_terms', {
                'amzSite': self.site,
                'asin': self.asin,
                'page': page
            })

            if not response.get('has_error') and response.get('data'):
                keywords_data = extract_keywords_from_response(response.get('data', {}))
                words = [normalize_keyword_data(kw) for kw in keywords_data]
                words = [w for w in words if w['keyword']]

                if words:
                    # 檢查是否與已有資料重複
                    unique_words = [w for w in words if w['keyword'].lower() not in [kw['keyword'].lower() for kw in long_tail]]
                    if unique_words:
                        long_tail.extend(unique_words)
                        success_count += 1
                        print(f" ✓ ({len(unique_words)} 個新詞)")
                    else:
                        print(f" (全部重複，停止)")
                        break
                else:
                    print(f" (無資料)")
                    break
            else:
                fail_count += 1
                print(f" ✗")
                break

        # 策略2: 獲取 competitor_product_keywords 的多頁資料
        print(f"    策略2: 獲取競品關鍵詞的額外頁面...")
        for page in range(2, max_pages + 2):
            print(f"    獲取競品詞第 {page} 頁...", end='', flush=True)

            response = self._curl_request('competitor_product_keywords', {
                'amzSite': self.site,
                'asin': self.asin,
                'page': page
            })

            if not response.get('has_error') and response.get('data'):
                keywords_data = extract_keywords_from_response(response.get('data', {}))
                words = [normalize_keyword_data(kw) for kw in keywords_data]
                words = [w for w in words if w['keyword']]

                if words:
                    # 檢查是否與已有資料重複
                    unique_words = [w for w in words if w['keyword'].lower() not in [kw['keyword'].lower() for kw in long_tail]]
                    if unique_words:
                        long_tail.extend(unique_words)
                        success_count += 1
                        print(f" ✓ ({len(unique_words)} 個新詞)")
                    else:
                        print(f" (全部重複，停止)")
                        break
                else:
                    print(f" (無資料)")
                    break
            else:
                fail_count += 1
                print(f" ✗")
                break

        print(f"    ✓ 擴充套件完成，共獲得 {len(long_tail)} 個長尾詞")
        if fail_count > 0:
            print(f"    ⚠ {fail_count} 個請求失敗")

        return long_tail

    def _get_product_node_id(self) -> str:
        """從產品詳情中獲取 NodeID"""
        self._log("獲取產品 NodeID...", 'DEBUG')
        response = self._curl_request('product_detail', {
            'amzSite': self.site,
            'asin': self.asin
        })

        if response.get('has_error'):
            self._log(f"獲取產品詳情失敗: {response.get('error')}", 'WARN')
            return None

        data = response.get('data', {})
        if isinstance(data, dict):
            # 查詢 NodeID 欄位
            for key in ['nodeId', 'NodeID', '類目ID', 'category_id', '所在nodeid']:
                if key in data:
                    node_id = str(data[key])
                    self._log(f"找到 NodeID: {node_id}", 'DEBUG')
                    return node_id

            # 嘗試從類目資訊中提取
            data_str = str(data)
            if '類目' in data_str or 'category' in data_str.lower():
                # 查詢 nodeId 模式
                match = re.search(r'nodeId["\']?\s*:\s*["\']?(\d+)', data_str, re.IGNORECASE)
                if match:
                    node_id = match.group(1)
                    self._log(f"從文字提取 NodeID: {node_id}", 'DEBUG')
                    return node_id

        self._log("未找到 NodeID", 'WARN')
        return None

    def get_product_detail(self) -> dict:
        """
        獲取產品詳情

        Returns:
            dict: 包含原始響應和解析後的資料
        """
        self._log("獲取產品詳情...", 'DEBUG')
        response = self._curl_request('product_detail', {
            'amzSite': self.site,
            'asin': self.asin
        })

        if response.get('has_error'):
            self._log(f"獲取產品詳情失敗: {response.get('error')}", 'WARN')
            return None

        # 儲存完整的響應（包含 text 和 data 欄位）
        self.product_detail = response
        return response

    def collect_all(self, long_tail_limit: int = 30) -> tuple:
        """
        採集所有關鍵詞

        Args:
            long_tail_limit: 長尾詞擴充套件的核心詞數量（0 表示跳過長尾詞擴充套件）

        Returns:
            tuple: (去重後的完整關鍵詞列表, 產品資訊字典)
        """
        print(f"\n開始採集關鍵詞: {self.asin} ({self.site})")
        print("-" * 50)

        all_keywords = []
        self.errors = []  # 清空錯誤記錄

        # Step 0: 獲取產品詳情（用於後續分類）
        product_info = self.get_product_detail()
        if product_info:
            print(f"  ✓ 產品名稱: {product_info.get('product_name', 'Unknown')}")
            print(f"  ✓ 品牌: {product_info.get('brand', 'Unknown')}")

        # Step 1: 基礎採集
        traffic = self.collect_traffic_terms()
        competitor = self.collect_competitor_keywords()
        category = self.collect_category_keywords()

        all_keywords.extend(traffic)
        all_keywords.extend(competitor)
        all_keywords.extend(category)

        # Step 2: 去重並選擇核心詞
        unique_keywords = self._deduplicate_keywords(all_keywords)
        self._log(f"Step 2 去重後: {len(unique_keywords)} 個關鍵詞", 'INFO')

        # Step 3: 長尾詞擴充套件（如果 limit > 0）
        if long_tail_limit > 0 and unique_keywords:
            core_for_expansion = sorted(unique_keywords,
                                       key=lambda x: x.get('search_volume', 0),
                                       reverse=True)
            long_tail = self.collect_long_tail_keywords(core_for_expansion, long_tail_limit)
            self._log(f"Step 3 獲得了 {len(long_tail)} 個長尾詞", 'INFO')
            all_keywords.extend(long_tail)
            self._log(f"Step 3 新增長尾詞後: {len(all_keywords)} 個關鍵詞（包含重複）", 'INFO')

        # Step 4: 最終去重
        final_keywords = self._deduplicate_keywords(all_keywords)
        self._log(f"Step 4 最終去重後: {len(final_keywords)} 個關鍵詞", 'INFO')

        print("-" * 50)
        print(f"✓ 採集完成: 共 {len(final_keywords)} 個關鍵詞\n")

        # 輸出錯誤摘要
        if self.errors:
            print(f"⚠ 發生 {len(self.errors)} 個錯誤（已跳過）:")
            for err in self.errors[:3]:  # 只顯示前 3 個
                print(f"  - {err.get('step')}: {err.get('error')}")
            if len(self.errors) > 3:
                print(f"  ... 還有 {len(self.errors) - 3} 個錯誤")
            print()

        # 解析產品資訊為結構化格式
        parsed_product_info = self._parse_product_info(product_info) if product_info else {}

        return final_keywords, parsed_product_info

    def _parse_product_info(self, product_detail_response: dict) -> dict:
        """
        解析產品詳情為結構化格式

        Args:
            product_detail_response: API 返回的完整響應（parse_sse_response 格式）

        Returns:
            dict: 結構化的產品資訊
        """
        parsed = {
            'product_name': '',
            'brand': '',
            'materials': [],
            'features': [],
            'use_cases': [],
            'negative_features': [],
            'description': '',
            'category': ''
        }

        if not product_detail_response:
            return parsed

        # 從響應中提取文字（parse_sse_response 返回的格式）
        raw_text = product_detail_response.get('text', '')

        if not raw_text:
            self._log("產品詳情文字為空", 'DEBUG')
            return parsed

        # 文字已經在 parse_sse_response 中解碼過了，直接使用
        decoded_text = raw_text
        parsed['description'] = decoded_text

        # 解析鍵值對（格式：中文鍵名：值）
        lines = decoded_text.split('\n')
        for line in lines:
            line = line.strip()
            if '：' in line or ': ' in line:
                # 分割鍵值對（同時支援中文冒號和英文冒號）
                if '：' in line:
                    parts = line.split('：', 1)
                else:
                    parts = line.split(': ', 1)

                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    # 解析各個欄位
                    if key in ['標題', 'Title', 'title', '產品名稱']:
                        parsed['product_name'] = value
                    elif key in ['品牌', 'Brand', 'brand']:
                        parsed['brand'] = value
                    elif key in ['分類', 'Category', 'category']:
                        parsed['category'] = value
                    elif key in ['產品描述', '描述', 'Description', 'description']:
                        parsed['description'] = value

        # 從產品名稱和描述中提取更多資訊
        combined_text = (parsed['product_name'] + ' ' + parsed['description']).lower()

        # 材質（從描述中提取常見材質詞）
        materials_list = ['wood', 'wooden', 'metal', 'aluminum', 'bamboo',
                         'plastic', 'steel', 'iron', 'ceramic', 'glass',
                         'fabric', 'leather', 'canvas', 'paper', 'cotton',
                         'silicone', 'rubber', 'foam', 'polyester', 'abs',
                         'pvc', 'electronic']
        for material in materials_list:
            if material in combined_text:
                parsed['materials'].append(material.title())

        # 特性（從標題或描述中提取）
        feature_keywords = ['waterproof', 'foldable', 'adjustable', 'portable',
                           'heavy duty', 'rustic', 'vintage', 'expandable',
                           'multi-functional', 'easy to use', 'remote control',
                           'rechargeable', 'battery operated', 'electronic',
                           'interactive', 'realistic', 'imitates', 'walking',
                           'sounds', 'shaking head', 'wagging tail', 'demonstration',
                           'one-touch', 'sing', '2.4g', '8-channel', 'large capacity']
        for feature in feature_keywords:
            if feature in combined_text:
                parsed['features'].append(feature.title())

        # 使用場景（常見場景詞）
        scenarios = ['entryway', 'bathroom', 'mudroom', 'garage', 'bedroom',
                    'kitchen', 'living room', 'office', 'outdoor', 'indoor',
                    'patio', 'deck', 'baby', 'kids', 'children', 'toddler',
                    'birthday', 'christmas', 'halloween', 'gift', 'party']
        for scenario in scenarios:
            if scenario in combined_text:
                parsed['use_cases'].append(scenario.title())

        # 否定特徵（基於常見不匹配特徵推斷）
        # 如果產品是 dinosaur/animal toy，排除其他型別的玩具
        if 'dinosaur' in combined_text or 'velociraptor' in combined_text:
            parsed['negative_features'].extend([
                'Car Toys', 'Building Blocks', 'Dolls', 'Stuffed Animals',
                'Board Games', 'Puzzles', 'Art Supplies'
            ])

        # 如果是 remote control，排除非電動玩具
        if 'remote control' in combined_text:
            parsed['negative_features'].extend([
                'Manual', 'Hand Crank', 'Wind Up', 'Pull Back'
            ])

        return parsed

    def _deduplicate_keywords(self, keywords: list) -> list:
        """
        去重併合並資料

        如果有重複關鍵詞，保留搜尋量最高的版本
        """
        keyword_map = {}

        for kw in keywords:
            normalized = kw['keyword'].lower().strip()
            if not normalized:
                continue

            # 如果已存在，保留搜尋量更高的
            if normalized in keyword_map:
                existing = keyword_map[normalized]
                if kw.get('search_volume', 0) > existing.get('search_volume', 0):
                    keyword_map[normalized] = kw
            else:
                keyword_map[normalized] = kw

        # 轉換回列表，恢復原始大小寫
        seen = set()
        unique = []
        for kw in keywords:
            normalized = kw['keyword'].lower().strip()
            if normalized in keyword_map and normalized not in seen:
                # 使用去重後資料（可能搜尋量更高）
                unique.append(keyword_map[normalized])
                seen.add(normalized)

        return unique


def main():
    """命令列測試入口"""
    if len(sys.argv) < 3:
        print("用法: python keyword_collector.py <ASIN> <站點> [長尾詞擴充套件數量]")
        print("示例: python keyword_collector.py B07PWTJ4H1 US 30")
        print("      python keyword_collector.py B07PWTJ4H1 US 0  # 跳過長尾詞擴充套件")
        sys.exit(1)

    asin = sys.argv[1]
    site = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 30

    collector = KeywordCollector(asin, site, verbose=True)
    keywords, product_info = collector.collect_all(long_tail_limit=limit)

    # 輸出產品資訊
    if product_info:
        print(f"\n產品資訊:")
        print(f"  名稱: {product_info.get('product_name', 'Unknown')}")
        print(f"  品牌: {product_info.get('brand', 'Unknown')}")
        if product_info.get('materials'):
            print(f"  材質: {', '.join(product_info['materials'])}")
        if product_info.get('features'):
            print(f"  特性: {', '.join(product_info['features'])}")

    # 輸出統計
    print(f"\n關鍵詞統計:")
    print(f"  總數: {len(keywords)}")
    print(f"  總搜尋量: {sum(kw.get('search_volume', 0) for kw in keywords):,}")

    # Top 20 關鍵詞
    print(f"\nTop 20 關鍵詞:")
    print("-" * 80)
    sorted_kw = sorted(keywords, key=lambda x: x.get('search_volume', 0), reverse=True)[:20]
    for i, kw in enumerate(sorted_kw, 1):
        print(f"  {i:2}. {kw['keyword']:<40} | 搜尋量: {kw.get('search_volume', 0):,}")
    print("-" * 80)


if __name__ == "__main__":
    main()
