#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 Sorftime category_report 響應中提取 Top N 產品
處理大資料檔案 (>25000 tokens) 的標準工具
"""

import re
import sys
import json
from typing import List, Dict, Optional


def extract_top_products(file_path: str, limit: int = 100) -> List[Dict]:
    """
    從 Sorftime 響應檔案中提取 Top N 產品

    Args:
        file_path: Sorftime API 響應檔案路徑
        limit: 提取產品數量

    Returns:
        產品列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"錯誤: 檔案不存在 {file_path}")
        return []
    except Exception as e:
        print(f"錯誤: 讀取檔案失敗 - {e}")
        return []

    # 使用正規表示式提取產品資訊
    # 模式：ASIN + 標題 + 價格 + 銷量 + 評分 + 品牌
    # 這種模式可以處理 Unicode 轉義的中文
    products = []

    # 方法1: 匹配完整的產品塊
    product_pattern = r'\{"ASIN":"([A-Z0-9]{10})"[^\}]*?"月銷量":"?(\d+)"?[^\}]*?"月銷額":"?([\d.]+)"?[^\}]*?"標題":"([^"]{30,150})"[^\}]*?"價格":"?([\d.]+)"?[^\}]*?"星級":"?([\d.]+)"?[^\}]*?"品牌":"([^"]+?)"[^\}]*?\}'

    for match in re.finditer(product_pattern, content):
        asin, sales, revenue, title, price, rating, brand = match.groups()

        products.append({
            'ASIN': asin,
            '標題': title,
            '價格': float(price),
            '月銷量': int(sales),
            '月銷額': float(revenue),
            '評分': float(rating),
            '品牌': brand
        })

        if len(products) >= limit:
            break

    # 如果方法1沒有找到足夠產品，嘗試方法2（更寬鬆的模式）
    if len(products) < limit:
        # 方法2: 逐個欄位提取
        asin_pattern = r'"ASIN":"([A-Z0-9]{10})"'
        asins = list(set(re.findall(asin_pattern, content)))

        for asin in asins:
            if len(products) >= limit:
                break

            # 找到這個 ASIN 附近的資料塊
            asin_pos = content.find(f'"ASIN":"{asin}"')
            if asin_pos == -1:
                continue

            # 提取 ASIN 周圍 2000 字元的資料
            chunk = content[max(0, asin_pos - 100):asin_pos + 2000]

            # 從 chunk 中提取其他欄位
            title_match = re.search(r'"標題":"([^"]{30,100})"', chunk)
            price_match = re.search(r'"價格":([\d.]+)', chunk)
            sales_match = re.search(r'"月銷量":"?(\d+)"?', chunk)
            rating_match = re.search(r'"星級":"?([\d.]+)"?', chunk)
            brand_match = re.search(r'"品牌":"([^"]+?)"', chunk)

            if title_match and price_match:
                products.append({
                    'ASIN': asin,
                    '標題': title_match.group(1),
                    '價格': float(price_match.group(1)),
                    '月銷量': int(sales_match.group(1)) if sales_match else 0,
                    '評分': float(rating_match.group(1)) if rating_match else 0,
                    '品牌': brand_match.group(1) if brand_match else 'Unknown'
                })

    return products


def print_products_table(products: List[Dict]):
    """列印產品表格"""
    if not products:
        print("未找到產品資料")
        return

    print(f"\n=== Top {len(products)} 產品 ===")
    print("-" * 100)
    print(f"{'排名':<4} {'ASIN':<12} {'品牌':<15} {'價格':<8} {'月銷量':<10} {'評分':<6} {'標題'}")
    print("-" * 100)

    for i, p in enumerate(products, 1):
        title = p.get('標題', 'N/A')[:50]
        print(f"{i:<4} {p.get('ASIN', ''):<12} {p.get('品牌', ''):<15} "
              f"${p.get('價格', 0):<7.2f} {p.get('月銷量', 0):<10,} "
              f"{p.get('評分', 0):<5.1f} {title}...")

    print("-" * 100)


def analyze_products(products: List[Dict]) -> Dict:
    """分析產品資料"""
    if not products:
        return {}

    total_sales = sum(p.get('月銷量', 0) for p in products)
    total_revenue = sum(p.get('月銷額', 0) for p in products)
    avg_price = sum(p.get('價格', 0) for p in products) / len(products)
    avg_rating = sum(p.get('評分', 0) for p in products) / len(products)

    # 品牌統計
    brands = {}
    for p in products:
        brand = p.get('品牌', 'Unknown')
        brands[brand] = brands.get(brand, 0) + 1

    # 排序品牌
    top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        '總銷量': total_sales,
        '總銷額': total_revenue,
        '平均價格': avg_price,
        '平均評分': avg_rating,
        '品牌數量': len(brands),
        'Top品牌': top_brands
    }


def main():
    """命令列入口"""
    if len(sys.argv) < 2:
        print("用法: python extract_top_products.py <響應檔案路徑> [數量]")
        print("\n示例:")
        print("  python extract_top_products.py temp_response.txt 100")
        print("\n選項:")
        print("  --json    輸出 JSON 格式")
        print("  --analyze 分析產品資料")
        sys.exit(1)

    file_path = sys.argv[1]
    limit = 100

    # 解析引數
    for arg in sys.argv[2:]:
        if arg.isdigit():
            limit = int(arg)

    # 提取產品
    products = extract_top_products(file_path, limit)

    if not products:
        print("未找到產品資料")
        sys.exit(1)

    # 列印表格
    print_products_table(products)

    # 分析資料
    if '--analyze' in sys.argv:
        analysis = analyze_products(products)

        print("\n=== 產品分析 ===")
        for key, value in analysis.items():
            if key == 'Top品牌':
                print(f"\n{key}:")
                for brand, count in value:
                    print(f"  - {brand}: {count} 個產品")
            else:
                print(f"  {key}: {value}")

    # 輸出 JSON
    if '--json' in sys.argv:
        print("\n=== JSON 輸出 ===")
        print(json.dumps(products, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
