#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
獲取競品差評資料（通用版本）

使用方法:
    python get_reviews.py --output-dir "product-research/xxx_YYYYMMDD"

注意：此指令碼從 top100.json 中自動選擇代表性競品
"""
import json
import os
import sys
from datetime import datetime

# 新增指令碼目錄到路徑
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from api_client import SorftimeClient

def get_project_root():
    """獲取專案根目錄"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 從 scripts/ 向上四級到達專案根目錄
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

def main():
    import argparse
    parser = argparse.ArgumentParser(description="獲取競品差評資料（通用版本）")
    parser.add_argument("--output-dir", "-o", required=True, help="輸出目錄（包含 top100.json 的目錄）")
    parser.add_argument("--site", default="US", help="站點程式碼")
    parser.add_argument("--max-reviews", type=int, default=6, help="最大競品數量")
    args = parser.parse_args()

    # 檢查 top100.json 是否存在
    top100_path = os.path.join(args.output_dir, 'raw', 'top100.json')
    if not os.path.exists(top100_path):
        print(f"✗ 錯誤：找不到 {top100_path}")
        print("  請確保輸出目錄中存在 raw/top100.json 檔案")
        return 1

    client = SorftimeClient()

    # 讀取 Top100 資料
    with open(top100_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('Top100產品', []) or data.get('Top100 產品', [])

    if not products:
        print("✗ 錯誤：top100.json 中沒有產品資料")
        return 1

    print(f"📊 從 {len(products)} 個產品中選擇代表性競品...")

    # 按銷量排序
    sorted_products = sorted(products, key=lambda x: float(x.get('月銷量', 0)), reverse=True)

    # 選擇策略：Top3 + 不同價格帶代表
    competitors = []

    # 量級標杆（Top3）
    for i, p in enumerate(sorted_products[:3]):
        competitors.append((p['ASIN'], f"Top{i+1} - {p.get('品牌', 'Unknown')}"))

    # 按價格分組選擇
    price_groups = {
        'low': [p for p in sorted_products if float(p.get('價格', 0)) < 30],
        'mid': [p for p in sorted_products if 30 <= float(p.get('價格', 0)) < 60],
        'high': [p for p in sorted_products if float(p.get('價格', 0)) >= 60]
    }

    # 各價位代表
    for price_name, price_list in [('低價', price_groups['low']), ('中價', price_groups['mid']), ('高價', price_groups['high'])]:
        for p in price_list:
            if p['ASIN'] not in [c[0] for c in competitors]:
                competitors.append((p['ASIN'], f"{price_name}代表 - {p.get('品牌', 'Unknown')}"))
                break

    # 去重
    seen = set()
    competitors = [x for x in competitors if not (x[0] in seen or seen.add(x[0]))]

    # 限制數量
    competitors = competitors[:args.max_reviews]

    print(f"  選擇了 {len(competitors)} 個競品進行差評分析")

    all_reviews = {}
    for asin, desc in competitors:
        print(f"  - {asin} ({desc})...", end=' ', flush=True)
        try:
            reviews, raw = client.get_product_reviews(args.site, asin, 'Negative')
            if reviews:
                if isinstance(reviews, list):
                    review_count = len(reviews)
                    sample = reviews[:20] if len(reviews) > 20 else reviews
                else:
                    review_count = 'data'
                    sample = reviews

                all_reviews[asin] = {
                    'description': desc,
                    'review_count': review_count,
                    'reviews': sample
                }
                print(f"✓ {review_count}條")
            else:
                print("✗ 無資料")
        except Exception as e:
            print(f"✗ {str(e)[:40]}")

    # 儲存結果
    if all_reviews:
        reviews_path = os.path.join(args.output_dir, 'raw', 'competitor_reviews.json')
        os.makedirs(os.path.dirname(reviews_path), exist_ok=True)

        with open(reviews_path, 'w', encoding='utf-8') as f:
            json.dump(all_reviews, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 差評資料已儲存: {reviews_path}")
        return 0
    else:
        print("\n✗ 未獲取到任何差評資料")
        return 1

if __name__ == "__main__":
    sys.exit(main())
