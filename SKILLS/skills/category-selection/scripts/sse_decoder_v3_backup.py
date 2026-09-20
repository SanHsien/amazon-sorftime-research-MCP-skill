#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime SSE 響應快速解碼器 v3.0
專門處理 category_report 的 SSE 響應格式
"""

import re
import json
import codecs
import sys
import os
from datetime import datetime


def decode_sse_response(file_path: str) -> dict:
    """
    解碼 Sorftime SSE 響應檔案

    Args:
        file_path: SSE 響應檔案路徑

    Returns:
        dict: 解碼後的完整 JSON 資料
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 方法1: 提取 SSE data 行中的 JSON
    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 字首
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # 解碼 Unicode 轉義
                    decoded = codecs.decode(result_text, 'unicode-escape')
                    # 提取 JSON 物件
                    start = decoded.find('{')
                    if start != -1:
                        # 找到匹配的結束括號
                        depth = 0
                        end = -1
                        for i in range(start, len(decoded)):
                            if decoded[i] == '{':
                                depth += 1
                            elif decoded[i] == '}':
                                depth -= 1
                                if depth == 0:
                                    end = i + 1
                                    break
                        if end != -1:
                            json_str = decoded[start:end]
                            return json.loads(json_str)
            except:
                continue

    # 方法2: 直接搜尋 JSON 陣列模式
    array_match = re.search(r'\[{"[^"]*"[^}]{50,}', content)
    if array_match:
        # 找到完整的資料範圍
        raw_content = content
        # 查詢第一個 { 和最後一個 }
        start = raw_content.find('{"Top100產品"')
        if start == -1:
            start = raw_content.find('{"類目統計報告"')
        if start == -1:
            start = raw_content.find('{\\"關鍵詞\\"')

        if start != -1:
            # 手動解析
            bracket_count = 0
            in_string = False
            escape_next = False
            end = -1

            for i in range(start, len(raw_content)):
                c = raw_content[i]

                if escape_next:
                    escape_next = False
                    continue

                if c == '\\':
                    escape_next = True
                    continue

                if c == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if c == '{':
                        bracket_count += 1
                    elif c == '}':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = i + 1
                            break

            if end != -1:
                # 提取並解碼
                raw_json = raw_content[start:end]
                # 解碼 unicode escapes like \u0022
                decoded = codecs.decode(raw_json, 'unicode-escape')
                return json.loads(decoded)

    raise ValueError("無法解析 SSE 響應檔案")


def fix_mojibake(obj):
    """
    修復 UTF-8/Latin-1 雙重編碼問題 (Mojibake)

    當 UTF-8 位元組被錯誤地解釋為 Latin-1 時會產生亂碼:
    - 'æ ' 應該是 '標' (E6 A0 87)
    - 'é¢' 應該是 '題' (E9 A2 98)

    解決方法: encode('latin-1') → decode('utf-8')
    """
    if isinstance(obj, dict):
        return {fix_mojibake(k): fix_mojibake(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_mojibake(item) for item in obj]
    elif isinstance(obj, str):
        # 檢查是否包含典型 Mojibake 模式
        mojibake_patterns = ['æ ', 'é¢', 'å ', 'ä»£', 'åç']
        if any(p in obj for p in mojibake_patterns):
            try:
                return obj.encode('latin-1').decode('utf-8')
            except:
                return obj
        return obj
    else:
        return obj


def save_decoded_data(data: dict, output_dir: str):
    """儲存解碼後的資料，自動修復編碼問題"""
    os.makedirs(output_dir, exist_ok=True)

    # 修復可能的 Mojibake 編碼問題
    fixed_data = fix_mojibake(data)

    # 儲存完整 JSON
    output_file = os.path.join(output_dir, 'data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    return output_file


def extract_category_stats(data: dict) -> dict:
    """提取類目統計資料"""
    stats = data.get('類目統計報告', {})

    return {
        'nodeid': stats.get('nodeid', ''),
        '類目名稱': stats.get('類目名稱', ''),
        'top100產品月銷量': stats.get('top100產品月銷量', '0'),
        'top100產品月銷額': stats.get('top100產品月銷額', '0'),
        'average_price': stats.get('average_price', '0'),
        'median_price': stats.get('median_price', '0'),
        'top3_brands_sales_volume_share': stats.get('top3_brands_sales_volume_share', '0'),
        'amazonOwned_sales_volume_share': stats.get('amazonOwned_sales_volume_share', '0'),
        'high_rated_sales_volume_share': stats.get('high_rated_sales_volume_share', '0'),
        'low_reviews_sales_volume_share': stats.get('low_reviews_sales_volume_share', '0'),
    }


def extract_top_products(data: dict, limit: int = 20) -> list:
    """提取 Top N 產品"""
    products_list = data.get('Top100產品', [])

    result = []
    for p in products_list[:limit]:
        # 提取月銷量（處理字串格式的數字）
        monthly_sales = p.get('月銷量', '0')
        if isinstance(monthly_sales, str):
            # 移除非數字字元
            monthly_sales = re.sub(r'[^\d.]', '', monthly_sales)

        # 提取價格
        price = float(p.get('價格', 0))

        # 計算月銷額 = 價格 * 月銷量
        monthly_sales_num = int(float(monthly_sales)) if monthly_sales else 0
        monthly_revenue = price * monthly_sales_num

        result.append({
            'ASIN': p.get('ASIN', ''),
            '標題': p.get('標題', '')[:80],
            '價格': price,
            '月銷量': monthly_sales_num,
            '月銷額': monthly_revenue,  # 新增：計算得出
            '評分': float(p.get('星級', 0)),
            '品牌': p.get('品牌', 'Unknown'),
            '評論數': int(p.get('評論數', 0)),
            '賣家來源': p.get('賣家來源', ''),
            '賣家': p.get('賣家', ''),  # 新增：賣家名稱
            '上架天數': p.get('上架天數', 0),  # 新增：如果有此欄位
            '類目排名': p.get('類目排名', ''),  # 新增：類目排名
            '圖片': p.get('圖片', ''),  # 新增：產品圖片URL
        })

    return result


def calculate_five_dimension_score(stats: dict) -> dict:
    """
    計算五維評分 (標準版本)

    評分標準:
    - 市場規模 (20分): >10M=20, >5M=17, >1M=14, 其他=10
    - 增長潛力 (25分): 低評論佔比>40%=22, >20%=18, 其他=14
    - 競爭烈度 (20分): Top3<30%=18, <50%=14, 其他=8
    - 進入壁壘 (20分): Amazon佔比+新品機會組合評分
    - 利潤空間 (15分): 均價>$300=12, >$150=10, >$50=7, 其他=4
    """
    def safe_float(value, default=0):
        try:
            return float(str(value).replace('%', '').replace(',', '').replace('$', ''))
        except:
            return default

    scores = {}

    # 1. 市場規模 (20分)
    revenue = safe_float(stats.get('top100產品月銷額', 0))
    if revenue > 10_000_000:
        scores['市場規模'] = 20
    elif revenue > 5_000_000:
        scores['市場規模'] = 17
    elif revenue > 1_000_000:
        scores['市場規模'] = 14
    else:
        scores['市場規模'] = 10

    # 2. 增長潛力 (25分)
    low_review_share = safe_float(stats.get('low_reviews_sales_volume_share', 0))
    if low_review_share > 40:
        scores['增長潛力'] = 22
    elif low_review_share > 20:
        scores['增長潛力'] = 18
    else:
        scores['增長潛力'] = 14

    # 3. 競爭烈度 (20分)
    top3_share = safe_float(stats.get('top3_brands_sales_volume_share', 0))
    if top3_share < 30:
        scores['競爭烈度'] = 18
    elif top3_share < 50:
        scores['競爭烈度'] = 14
    else:
        scores['競爭烈度'] = 8

    # 4. 進入壁壘 (20分)
    amazon_share = safe_float(stats.get('amazonOwned_sales_volume_share', 0))

    barrier_score = 0
    # Amazon 佔比越低，壁壘越小
    if amazon_share < 20:
        barrier_score += 10
    elif amazon_share < 40:
        barrier_score += 6
    else:
        barrier_score += 3

    # 新品機會越大，壁壘越小
    if low_review_share > 40:
        barrier_score += 10
    elif low_review_share > 20:
        barrier_score += 6
    else:
        barrier_score += 3

    scores['進入壁壘'] = barrier_score

    # 5. 利潤空間 (15分)
    avg_price = safe_float(stats.get('average_price', 0))
    if avg_price > 300:
        scores['利潤空間'] = 12
    elif avg_price > 150:
        scores['利潤空間'] = 10
    elif avg_price > 50:
        scores['利潤空間'] = 7
    else:
        scores['利潤空間'] = 4

    # 總分
    scores['總分'] = sum(scores.values())

    # 評級
    if scores['總分'] >= 80:
        scores['評級'] = '優秀'
    elif scores['總分'] >= 70:
        scores['評級'] = '良好'
    elif scores['總分'] >= 50:
        scores['評級'] = '一般'
    else:
        scores['評級'] = '較差'

    return scores


def print_summary(stats: dict, products: list):
    """列印摘要資訊"""
    print("\n" + "=" * 70)
    print("類目資料解碼成功")
    print("=" * 70)

    print(f"\n類目: {stats.get('類目名稱', 'Unknown')}")
    print(f"NodeID: {stats.get('nodeid', 'N/A')}")

    total_sales = stats.get('top100產品月銷量', '0')
    total_revenue = stats.get('top100產品月銷額', '0')
    avg_price = stats.get('average_price', '0')

    print(f"\nTop100 月銷量: {total_sales}")
    print(f"Top100 月銷額: ${total_revenue}")
    print(f"平均價格: ${avg_price}")

    print(f"\nTop3 品牌佔比: {stats.get('top3_brands_sales_volume_share', 'N/A')}")
    print(f"Amazon 自營: {stats.get('amazonOwned_sales_volume_share', 'N/A')}")
    print(f"新品機會(<300評論): {stats.get('low_reviews_sales_volume_share', 'N/A')}")

    # 計算並顯示五維評分
    scores = calculate_five_dimension_score(stats)
    print(f"\n【五維評分】")
    for key, value in scores.items():
        if key not in ['總分', '評級']:
            print(f"  {key}: {value}")
    print(f"  總分: {scores['總分']}/100")
    print(f"  評級: {scores['評級']}")

    print(f"\n【Top {len(products)} 產品】")
    print("-" * 100)
    for i, p in enumerate(products, 1):
        print(f"{i:2}. {p['ASIN']} | {p['品牌']:<15} | ${p['價格']:7.2f} | "
              f"銷量:{p['月銷量']:5} | 評分:{p['評分']:3.1f}★")
    print("-" * 100)


def main():
    if len(sys.argv) < 2:
        print("用法: python sse_decoder.py <SSE響應檔案> [輸出目錄] [產品數量]")
        print("\n示例:")
        print("  python sse_decoder.py response.txt")
        print("  python sse_decoder.py response.txt ./output 50")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 20

    try:
        # 解碼 SSE 響應
        data = decode_sse_response(file_path)

        # 儲存完整資料
        saved_file = save_decoded_data(data, output_dir)
        print(f"\n完整資料已儲存到: {saved_file}")

        # 提取統計資料
        stats = extract_category_stats(data)

        # 提取產品列表
        products = extract_top_products(data, limit)

        # 列印摘要
        print_summary(stats, products)

        # 計算並儲存評分
        scores = calculate_five_dimension_score(stats)
        scores_file = os.path.join(output_dir, 'scores.json')
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        print(f"\n五維評分已儲存到: {scores_file}")

        # 儲存產品列表到單獨檔案
        products_file = os.path.join(output_dir, 'top_products.json')
        with open(products_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"Top {len(products)} 產品已儲存到: {products_file}")

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
