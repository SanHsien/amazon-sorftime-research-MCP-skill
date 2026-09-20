#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime category_report 完整解析指令碼
一鍵提取統計資料、產品列表、計算評分
"""

import re
import sys
import json
import codecs
from typing import Dict, List, Optional


class CategoryReportParser:
    """類目報告解析器"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = None
        self.statistics = {}
        self.products = []
        self.scores = {}

    def load(self) -> bool:
        """載入檔案"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            print(f"錯誤: 無法讀取檔案 - {e}")
            return False

    def extract_statistics(self) -> Dict[str, str]:
        """提取統計資料"""
        if not self.content:
            return {}

        # 先解碼 Unicode 轉義
        decoded_content = self._decode_unicode_escapes(self.content)

        # 使用 Unicode 轉義格式的鍵名（如 \u0022\u6807\u9898\u0022 = "標題"）
        # 以及普通格式的鍵名
        patterns = [
            # Unicode 轉義格式
            (r'\\u0022top100\u4ea7\u54c1\u6708\u9500\u91cf\\u0022:\\u0022?(\d+)\\u0022?', '總銷量'),
            (r'\\u0022top100\u4ea7\u54c1\u6708\u9500\u989d\\u0022:\\u0022?([\d.]+)\\u0022?', '總銷額'),
            (r'\\u0022average_price\\u0022:\\u0022?([\d.]+)\\u0022?', '平均價格'),
            (r'\\u0022median_price\\u0022:\\u0022?([\d.]+)\\u0022?', '中位數價格'),
            (r'\\u0022top3_brands_sales_volume_share\\u0022:\\u0022?([\d.]+%?)\\u0022?', 'Top3品牌佔比'),
            (r'\\u0022amazonOwned_sales_volume_share\\u0022:\\u0022?([\d.]+%?)\\u0022?', 'Amazon自營佔比'),
            (r'\\u0022low_reviews_sales_volume_share\\u0022:\\u0022?([\d.]+%?)\\u0022?', '低評論佔比'),
            # 普通格式（如果已解碼）
            (r'"top100產品月銷量":"?(\d+)"?', '總銷量'),
            (r'"top100產品月銷額":"?([\d.]+)"?', '總銷額'),
            (r'"average_price":"?([\d.]+)"?', '平均價格'),
            (r'"top3_brands_sales_volume_share":"?([\d.]+%?)"?', 'Top3品牌佔比'),
            (r'"amazonOwned_sales_volume_share":"?([\d.]+%?)"?', 'Amazon自營佔比'),
            (r'"low_reviews_sales_volume_share":"?([\d.]+%?)"?', '低評論佔比'),
        ]

        results = {}
        for pattern, name in patterns:
            match = re.search(pattern, decoded_content)
            if match:
                results[name] = match.group(1)
            elif name not in results:  # 只在第一次嘗試未找到時記錄
                results[name] = "未找到"

        self.statistics = results
        return results

    def _decode_unicode_escapes(self, text: str) -> str:
        """解碼 Unicode 跳脫字元"""
        # 處理 SSE 格式
        decoded = text
        for line in decoded.split('\n'):
            if line.startswith('data: '):
                json_text = line[6:]
                try:
                    data = json.loads(json_text)
                    result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                    if result_text:
                        # 解碼 Unicode 轉義
                        return codecs.decode(result_text, 'unicode-escape')
                except:
                    pass
        return decoded

    def extract_products(self, limit: int = 100) -> List[Dict]:
        """提取 Top N 產品"""
        if not self.content:
            return []

        # 先解碼 Unicode 轉義
        decoded_content = self._decode_unicode_escapes(self.content)

        products = []

        # Unicode 轉義格式的鍵名
        # \u0022ASIN\u0022 = "ASIN", \u0022\u6807\u9898\u0022 = "標題", etc.
        # 匹配完整的產品物件
        product_pattern = r'\{\\u0022ASIN\\u0022:\\u0022([A-Z0-9]{10})\\u0022[^\}]*?\\u0022\u6708\u9500\u91cf\\u0022:\\u0022?(\d+)\\u0022?[^\}]*?\\u0022\u6807\u9898\\u0022:\\u0022([^\\u0022]{30,150})\\u0022[^\}]*?\\u0022\u4ef7\u683c\\u0022:([\d.]+)[^\}]*?\\u0022\u661f\u7ea7\\u0022:\\u0022?([\d.]+)\\u0022?[^\}]*?\\u0022\u54c1\u724c\\u0022:\\u0022([^\\u0022]+?)\\u0022[^\}]*?\}'

        for match in re.finditer(product_pattern, decoded_content):
            asin, sales, title, price, rating, brand = match.groups()

            products.append({
                'ASIN': asin,
                '標題': title,
                '價格': float(price),
                '月銷量': int(sales),
                '評分': float(rating),
                '品牌': brand
            })

            if len(products) >= limit:
                break

        # 如果 Unicode 格式沒找到，嘗試普通格式
        if len(products) < limit:
            product_pattern2 = r'\{"ASIN":"([A-Z0-9]{10})"[^\}]*?"月銷量":"?(\d+)"?[^\}]*?"標題":"([^"]{30,150})"[^\}]*?"價格":"?([\d.]+)"?[^\}]*?"星級":"?([\d.]+)"?[^\}]*?"品牌":"([^"]+?)"[^\}]*?\}'
            for match in re.finditer(product_pattern2, decoded_content):
                asin, sales, title, price, rating, brand = match.groups()
                # 避免重複新增
                if not any(p['ASIN'] == asin for p in products):
                    products.append({
                        'ASIN': asin,
                        '標題': title,
                        '價格': float(price),
                        '月銷量': int(sales),
                        '評分': float(rating),
                        '品牌': brand
                    })
                    if len(products) >= limit:
                        break

        self.products = products
        return products

    def calculate_scores(self) -> Dict[str, float]:
        """計算五維評分"""
        if not self.statistics:
            return {}

        def safe_float(value, default=0):
            try:
                return float(str(value).replace('%', '').replace(',', ''))
            except:
                return default

        revenue = safe_float(self.statistics.get('總銷額', 0))
        top3_share = safe_float(self.statistics.get('Top3品牌佔比', 0))
        amazon_share = safe_float(self.statistics.get('Amazon自營佔比', 0))
        low_review_share = safe_float(self.statistics.get('低評論佔比', 0))
        avg_price = safe_float(self.statistics.get('平均價格', 0))

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

        self.scores = scores
        return scores

    def parse(self, limit: int = 100) -> Dict:
        """完整解析"""
        if not self.load():
            return {'error': '無法載入檔案'}

        self.extract_statistics()
        self.extract_products(limit)
        self.calculate_scores()

        return {
            'statistics': self.statistics,
            'products': self.products,
            'scores': self.scores
        }

    def print_report(self):
        """列印報告"""
        print("=" * 70)
        print("類目選品分析報告")
        print("=" * 70)

        # 統計資料
        if self.statistics:
            print("\n【統計資料】")
            for name, value in self.statistics.items():
                print(f"  {name}: {value}")

        # 評分
        if self.scores:
            print("\n【五維評分】")
            for key, value in self.scores.items():
                if key not in ['總分', '評級']:
                    print(f"  {key}: {value}")
            print(f"\n  總分: {self.scores.get('總分', 0)}/100")
            print(f"  評級: {self.scores.get('評級', '未知')}")

        # 產品列表
        if self.products:
            print(f"\n【Top {len(self.products)} 產品】")
            print("-" * 100)
            for i, p in enumerate(self.products, 1):
                print(f"{i}. {p.get('ASIN')} | {p.get('品牌')} | "
                      f"${p.get('價格', 0):.2f} | {p.get('月銷量', 0):,}銷量 | "
                      f"{p.get('評分', 0):.1f}★")
                title = p.get('標題', '')[:60]
                print(f"   {title}...")
            print("-" * 100)


def main():
    """命令列入口"""
    if len(sys.argv) < 2:
        print("用法: python parse_category_report.py <響應檔案路徑> [產品數量]")
        print("\n示例:")
        print("  python parse_category_report.py temp_response.txt 100")
        print("\n選項:")
        print("  --json    輸出 JSON 格式")
        print("  --save    儲存為 JSON 檔案")
        sys.exit(1)

    file_path = sys.argv[1]
    limit = 100

    # 解析引數
    for arg in sys.argv[2:]:
        if arg.isdigit():
            limit = int(arg)

    # 解析報告
    parser = CategoryReportParser(file_path)
    result = parser.parse(limit)

    if 'error' in result:
        print(f"錯誤: {result['error']}")
        sys.exit(1)

    # 列印報告
    parser.print_report()

    # JSON 輸出
    if '--json' in sys.argv:
        print("\n" + "=" * 70)
        print("JSON 格式輸出")
        print("=" * 70)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # 儲存檔案
    if '--save' in sys.argv:
        output_file = file_path.replace('.txt', '_parsed.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n已儲存到: {output_file}")


if __name__ == "__main__":
    main()
