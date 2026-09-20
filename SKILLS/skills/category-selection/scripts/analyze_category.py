#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品類選品一體化分析指令碼
一個命令完成：API 呼叫 → 資料解析 → 報告生成
"""

import os
import sys
import json
import re
import codecs
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CategoryAnalyzer:
    """品類選品一體化分析器"""

    def __init__(self, api_key: Optional[str] = None):
        """初始化分析器"""
        self.api_key = api_key or self._load_api_key()
        self.base_url = "https://mcp.sorftime.com"
        self.request_id = 0
        self.category_name = None
        self.site = "US"
        self.limit = 100

    def _load_api_key(self) -> str:
        """從配置檔案載入 API Key"""
        config_file = Path(".mcp.json")
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                url = config['mcpServers']['sorftime']['url']
                return url.split('key=')[-1]
        raise FileNotFoundError("找不到 .mcp.json 配置檔案")

    def _get_next_id(self) -> int:
        """獲取下一個請求 ID"""
        self.request_id += 1
        return self.request_id

    def _call_api(self, tool_name: str, arguments: Dict) -> Optional[Dict]:
        """呼叫 Sorftime MCP API"""
        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            'jsonrpc': '2.0',
            'id': self._get_next_id(),
            'method': 'tools/call',
            'params': {
                'name': tool_name,
                'arguments': arguments
            }
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code != 200:
                print(f"  ✗ HTTP {response.status_code}")
                return None

            # 解析 SSE 響應
            return self._parse_sse_response(response.text)

        except Exception as e:
            print(f"  ✗ 異常: {e}")
            return None

    def _parse_sse_response(self, raw_text: str):
        """解析 SSE 響應，支援物件和陣列"""
        try:
            lines = raw_text.split('\n')
            for line in lines:
                if line.startswith('data: '):
                    json_data = line[6:]  # 去掉 'data: ' 字首
                    data = json.loads(json_data)

                    if 'error' in data:
                        return None

                    if 'result' in data:
                        result = data['result']
                        if 'content' in result and len(result['content']) > 0:
                            content = result['content'][0]
                            if 'text' in content:
                                text = content['text']
                                if not text:
                                    continue

                                # JSON 已經自動解碼了 Unicode 轉義，不需要再用 codecs.decode
                                # 直接使用 text 即可
                                decoded = text

                                # 查詢第一個完整的 JSON 物件（包含產品資料）
                                first_obj_start = decoded.find('{')
                                if first_obj_start != -1:
                                    depth = 0
                                    end = -1
                                    for i in range(first_obj_start, len(decoded)):
                                        if decoded[i] == '{':
                                            depth += 1
                                        elif decoded[i] == '}':
                                            depth -= 1
                                            if depth == 0:
                                                end = i + 1
                                                break

                                    if end != -1:
                                        json_str = decoded[first_obj_start:end]
                                        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                                        return json.loads(json_str)

                                # 如果沒找到物件，嘗試陣列
                                first_arr_start = decoded.find('[')
                                if first_arr_start != -1:
                                    depth = 0
                                    end = -1
                                    for i in range(first_arr_start, len(decoded)):
                                        if decoded[i] == '[':
                                            depth += 1
                                        elif decoded[i] == ']':
                                            depth -= 1
                                            if depth == 0:
                                                end = i + 1
                                                break

                                    if end != -1:
                                        json_str = decoded[first_arr_start:end]
                                        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                                        return json.loads(json_str)

            return None

        except Exception as e:
            print(f"  ✗ SSE 解析異常: {e}")
            return None

    def _fix_chinese_keys(self, obj):
        """修復中文鍵名的編碼問題"""
        if isinstance(obj, dict):
            new_dict = {}
            for key, value in obj.items():
                fixed_key = self._fix_key(key)
                new_dict[fixed_key] = self._fix_chinese_keys(value)
            return new_dict
        elif isinstance(obj, list):
            return [self._fix_chinese_keys(item) for item in obj]
        else:
            return obj

    def _fix_key(self, key: str) -> str:
        """修復單個鍵名的編碼問題"""
        if not isinstance(key, str):
            return key

        # 檢查是否包含高位元組字元 (可能是編碼問題)
        if not any(0x80 <= ord(c) <= 0xFF for c in key):
            return key

        # 方法1: 嘗試 latin-1 -> utf-8
        try:
            return key.encode('latin-1').decode('utf-8')
        except:
            pass

        # 方法2: 嘗試 ISO-8859-1 -> utf-8
        try:
            return key.encode('iso-8859-1').decode('utf-8')
        except:
            pass

        # 方法3: 嘗試 cp1252 -> utf-8
        try:
            return key.encode('cp1252').decode('utf-8')
        except:
            pass

        # 都失敗了，返回原鍵
        return key

    def search_category(self, category_name: str, site: str = "US") -> Optional[str]:
        """搜尋品類獲取 nodeId"""
        print(f"[1/6] 搜尋類目: {category_name} ({site})")

        result = self._call_api('category_name_search', {
            'amzSite': site,
            'searchName': category_name
        })

        if not result:
            print(f"  ✗ 未找到類目: {category_name}")
            return None

        # 處理不同的返回格式
        categories = []
        if isinstance(result, list):
            categories = result
        elif isinstance(result, str):
            # 如果是字串，嘗試解析為 JSON
            try:
                categories = json.loads(result)
            except:
                print(f"  ✗ 無法解析類目資料")
                return None
        elif isinstance(result, dict):
            # 如果是字典，可能是單條結果
            categories = [result]

        if not categories:
            print(f"  ✗ 類目列表為空")
            return None

        # 選擇第一個類目
        selected = categories[0]
        node_id = selected.get('NodeId') or selected.get('nodeId')
        name = selected.get('Name') or selected.get('name')

        # 儲存品類名稱
        self.category_name = name if name else category_name

        print(f"  ✓ 找到類目: {self.category_name} (nodeId: {node_id})")

        return node_id

    def get_category_report(self, node_id: str) -> Optional[Dict]:
        """獲取類目報告"""
        print(f"[2/6] 獲取類目報告...")

        result = self._call_api('category_report', {
            'amzSite': self.site,
            'nodeId': node_id
        })

        if not result:
            print(f"  ✗ 獲取類目報告失敗")
            return None

        result = self._fix_chinese_keys(result)

        # 統計資訊
        stats = result.get('類目統計報告', {})
        products = result.get('Top100產品', [])

        print(f"  ✓ 類目報告獲取成功")
        print(f"    - 產品數量: {len(products)}")

        return result

    def extract_and_analyze(self, report_data: Dict) -> Dict:
        """提取資料並分析"""
        print(f"[3/6] 提取和分析資料...")

        # 提取統計資料
        stats = report_data.get('類目統計報告', {})

        # 提取產品列表
        products = report_data.get('Top100產品', [])[:self.limit]

        # 計算評分
        scores = self._calculate_scores(stats)

        print(f"  ✓ 資料提取完成")
        print(f"    - 總銷量: {stats.get('top100產品月銷量', 'N/A')}")
        print(f"    - 平均價格: {stats.get('average_price', 'N/A')}")

        return {
            'category_name': self.category_name,
            'site': self.site,
            'limit': self.limit,
            'statistics': stats,
            'products': products,
            'scores': scores,
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_scores(self, stats: Dict) -> Dict:
        """計算五維評分"""
        def safe_float(value, default=0):
            try:
                return float(str(value).replace('%', '').replace(',', ''))
            except:
                return default

        revenue = safe_float(stats.get('top100產品月銷額', 0))
        top3_share = safe_float(stats.get('top3_brands_sales_volume_share', 0))
        amazon_share = safe_float(stats.get('amazonOwned_sales_volume_share', 0))
        low_review_share = safe_float(stats.get('low_reviews_sales_volume_share', 0))
        avg_price = safe_float(stats.get('average_price', 0))

        scores = {}

        # 市場規模
        if revenue > 10000000:
            scores['市場規模'] = 20
        elif revenue > 5000000:
            scores['市場規模'] = 17
        elif revenue > 1000000:
            scores['市場規模'] = 14
        else:
            scores['市場規模'] = 10

        # 增長潛力
        if low_review_share > 40:
            scores['增長潛力'] = 22
        elif low_review_share > 20:
            scores['增長潛力'] = 18
        else:
            scores['增長潛力'] = 14

        # 競爭烈度
        if top3_share < 30:
            scores['競爭烈度'] = 18
        elif top3_share < 50:
            scores['競爭烈度'] = 14
        else:
            scores['競爭烈度'] = 8

        # 進入壁壘
        barrier_score = 0
        if amazon_share < 20:
            barrier_score += 10
        elif amazon_share < 40:
            barrier_score += 6
        else:
            barrier_score += 3

        if low_review_share > 40:
            barrier_score += 10
        elif low_review_share > 20:
            barrier_score += 6
        else:
            barrier_score += 3

        scores['進入壁壘'] = barrier_score

        # 利潤空間
        if avg_price > 300:
            scores['利潤空間'] = 12
        elif avg_price > 150:
            scores['利潤空間'] = 10
        elif avg_price > 50:
            scores['利潤空間'] = 7
        else:
            scores['利潤空間'] = 4

        scores['總分'] = sum(scores.values())

        if scores['總分'] >= 80:
            scores['評級'] = '優秀'
        elif scores['總分'] >= 70:
            scores['評級'] = '良好'
        elif scores['總分'] >= 50:
            scores['評級'] = '一般'
        else:
            scores['評級'] = '較差'

        return scores

    def generate_reports(self, data: Dict) -> Path:
        """生成所有格式的報告"""
        print(f"[4/6] 生成報告...")

        # 匯入報告生成器
        try:
            from generate_reports import CategoryReportGenerator
        except ImportError:
            print("  ✗ 報告生成模組未找到")
            return None

        # 建立輸出目錄
        date_str = datetime.now().strftime('%Y/%m')
        safe_name = self._sanitize_filename(self.category_name)
        output_dir = Path('category-reports') / date_str / f"{safe_name}_{self.site}"

        # 生成報告
        generator = CategoryReportGenerator(data, str(output_dir))
        report_files = generator.generate_all()

        print(f"  ✓ 報告已儲存到: {output_dir}")

        # 列印檔案列表
        for format_type, path in report_files.items():
            print(f"    [{format_type.upper()}] {path}")

        return output_dir

    def _sanitize_filename(self, name: str) -> str:
        """清理檔名"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            name = name.replace(char, '_')
        name = name.replace(' ', '_')
        return name[:50]

    def analyze(self, category_name: str, site: str = "US", limit: int = 100) -> bool:
        """
        執行完整的品類分析

        Args:
            category_name: 品類名稱
            site: 亞馬遜站點
            limit: 分析產品數量

        Returns:
            是否成功
        """
        start_time = datetime.now()

        print("=" * 70)
        print(f"品類選品分析")
        print("=" * 70)
        print(f"品類: {category_name}")
        print(f"站點: {site}")
        print(f"分析數量: Top{limit}")
        print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        self.site = site
        self.limit = limit

        # 步驟 1: 搜尋品類
        node_id = self.search_category(category_name, site)
        if not node_id:
            return False

        # 步驟 2: 獲取類目報告
        report_data = self.get_category_report(node_id)
        if not report_data:
            return False

        # 步驟 3: 提取和分析資料
        data = self.extract_and_analyze(report_data)

        # 步驟 4: 生成報告
        output_dir = self.generate_reports(data)

        # 完成
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print("\n" + "=" * 70)
        print("分析完成！")
        print("=" * 70)
        print(f"總耗時: {duration:.1f} 秒")
        print(f"輸出目錄: {output_dir}")
        print(f"資料時間: {data.get('timestamp', '')}")
        print(f"綜合評級: {data['scores'].get('評級', 'N/A')} ({data['scores'].get('總分', 0)}/100)")
        print("=" * 70)

        return True


def main():
    """命令列入口"""
    if len(sys.argv) < 2:
        print("用法: python analyze_category.py <品類名稱> [站點] [分析數量]")
        print("\n示例:")
        print("  python analyze_category.py \"Phone Cases\" US 20")
        print("  python analyze_category.py Sofas US 50")
        print("\n引數:")
        print("  品類名稱  - 必填，要分析的品類名稱")
        print("  站點       - 可選，預設 US")
        print("  分析數量   - 可選，預設 100")
        sys.exit(1)

    category_name = sys.argv[1]
    site = sys.argv[2] if len(sys.argv) > 2 else "US"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    # 執行分析
    analyzer = CategoryAnalyzer()
    success = analyzer.analyze(category_name, site, limit)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
