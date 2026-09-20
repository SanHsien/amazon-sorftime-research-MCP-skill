#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime SSE 響應快速解碼器 v6.0 - Mojibake 修復版
專門處理 category_report 的 SSE 響應格式

主要改進:
1. 修復 Unicode-escape + Mojibake 雙重編碼問題
2. 在 Unicode 解碼後立即應用 Mojibake 修復
3. 更健壯的控制字元處理
4. 改進的括號匹配演算法
5. 更詳細的除錯資訊
6. 支援 Python dict 格式轉 JSON
"""

import re
import json
import codecs
import sys
import os
from datetime import datetime


def safe_float(value, default=0.0):
    """安全地轉換為浮點數"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # 移除常見的非數字字元
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def safe_int(value, default=0):
    """安全地轉換為整數"""
    return int(safe_float(value, default))


def clean_json_string(json_str: str) -> str:
    """
    清理 JSON 字串中的控制字元和轉義序列
    """
    # 替換常見的轉義換行符（在 JSON 字串中）
    json_str = json_str.replace('\\r\\n', ' ')
    json_str = json_str.replace('\\r', ' ')
    json_str = json_str.replace('\\n', ' ')

    # 移除實際的控制字元（解碼後產生的）
    json_str = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', json_str)

    return json_str


def fix_mojibake_text(text: str) -> str:
    """
    修復 Mojibake (UTF-8/Latin-1 雙重編碼)

    當 UTF-8 位元組被錯誤地解釋為 Latin-1 時會產生亂碼
    修復方法: encode as Latin-1, then decode as UTF-8
    """
    if not isinstance(text, str):
        return text

    # 檢測 Mojibake: 如果包含 Latin-1 擴充套件字元範圍，可能是 Mojibake
    # Latin-1 擴充套件字元: \xc0-\xff (À-ÿ)
    has_latin1_extended = any(0xC0 <= ord(c) <= 0xFF for c in text if c != '\r' and c != '\n' and c != '\t')

    if has_latin1_extended:
        try:
            # 嘗試修復: Latin-1 -> UTF-8
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    return text


def decode_sse_response(file_path: str, verbose: bool = False) -> dict:
    """
    解碼 Sorftime SSE 響應檔案

    支援多種格式:
    1. 標準 SSE 格式 (event: message, data: {...})
    2. 直接 JSON 格式
    3. 巢狀轉義的 JSON 格式

    Args:
        file_path: SSE 響應檔案路徑
        verbose: 是否顯示詳細除錯資訊

    Returns:
        dict: 解碼後的完整 JSON 資料
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if verbose:
        print(f"[DEBUG] 檔案大小: {len(content)} 位元組")
        print(f"[DEBUG] 檔案前200字元: {content[:200]}")

    # 策略 1: 標準 SSE 格式解析
    if verbose:
        print("\n[策略1] 嘗試標準 SSE 格式解析...")

    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 字首
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # 關鍵修復: 先清理，再 Unicode 解碼，再 Mojibake 修復
                    cleaned_text = clean_json_string(result_text)

                    # 解碼 Unicode 轉義
                    decoded = codecs.decode(cleaned_text, 'unicode-escape')

                    # 立即修復 Mojibake
                    decoded = fix_mojibake_text(decoded)

                    # 再次清理（解碼後可能產生新的控制字元）
                    decoded = clean_json_string(decoded)

                    # 提取 JSON 物件（使用括號匹配）
                    json_obj = extract_json_object(decoded)
                    if json_obj:
                        if verbose:
                            print("[策略1] ✓ 成功")
                        return json_obj
            except Exception as e:
                if verbose:
                    print(f"[策略1] 失敗: {e}")
                continue

    # 策略 2: 直接 JSON 解析（用於已經提取好的 JSON）
    if verbose:
        print("\n[策略2] 嘗試直接 JSON 解析...")

    try:
        # 先嚐試 Mojibake 修復整個內容
        fixed_content = fix_mojibake_text(content)
        data = json.loads(fixed_content)
        if verbose:
            print("[策略2] ✓ 直接解析成功")
        return data
    except Exception as e:
        if verbose:
            print(f"[策略2] 失敗: {e}")

    # 策略 3: 正規表示式直接提取 JSON
    if verbose:
        print("\n[策略3] 嘗試正規表示式提取...")

    # 查詢 JSON 開始標記
    patterns = [
        r'(\{"Top100產品":)',
        r'(\{"Top100\\u[0-9a-f]{4}[0-9a-f]{4}:)',
        r'("Top100產品":)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            start = match.start()
            if content[start] != '{':
                start = content.rfind('{', 0, start)

            # 使用括號匹配找到完整的 JSON
            json_obj = extract_json_from_text(content, start)
            if json_obj:
                if verbose:
                    print("[策略3] ✓ 成功")
                return json_obj

    raise ValueError("無法解析 SSE 響應檔案 - 所有策略均失敗")


def extract_json_object(text: str) -> dict:
    """
    從文字中提取完整的 JSON 物件
    使用括號匹配來處理巢狀結構
    """
    start = text.find('{')
    if start == -1:
        return None

    json_str = extract_json_from_text(text, start)
    if not json_str:
        return None

    # 轉換 Python dict 格式為 JSON 格式
    json_str = python_dict_to_json(json_str)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失敗: {e}")


def extract_json_from_text(text: str, start: int = 0) -> str:
    """
    從文字中提取完整的 JSON/Python dict 字串
    使用括號匹配演算法
    """
    if start >= len(text):
        return None

    if text[start] != '{':
        # 找到下一個 '{'
        start = text.find('{', start)
        if start == -1:
            return None

    depth = 0
    in_string = False
    escape_next = False
    end = -1

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
                    end = i + 1
                    break

    if end == -1:
        return None

    return text[start:end]


def python_dict_to_json(text: str) -> str:
    """
    將 Python dict 格式（單引號）轉換為 JSON 格式（雙引號）
    同時處理 True/False/None
    """
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


def save_decoded_data(data: dict, output_dir: str):
    """儲存解碼後的資料"""
    os.makedirs(output_dir, exist_ok=True)

    # 儲存完整 JSON
    output_file = os.path.join(output_dir, 'data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return output_file


def extract_category_stats(data: dict) -> dict:
    """提取類目統計資料"""
    # 嘗試不同的鍵名
    stats = data.get('類目統計報告', {})

    if not stats:
        # 如果沒有統計資料，從產品列表計算
        products = data.get('Top100產品', data.get('產品列表', []))
        if products:
            total_revenue = sum(safe_float(p.get('月銷額', 0)) for p in products)
            total_sales = sum(safe_int(p.get('月銷量', 0)) for p in products)
            avg_price = total_revenue / total_sales if total_sales > 0 else 0

            stats = {
                'top100產品月銷額': str(total_revenue),
                'top100產品月銷量': str(total_sales),
                'average_price': str(avg_price),
            }

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
    # 嘗試不同的鍵名
    products_list = data.get('Top100產品', data.get('產品列表', data.get('products', [])))

    result = []
    for p in products_list[:limit]:
        # 安全提取和轉換資料
        monthly_sales = safe_int(p.get('月銷量', '0'))
        price = safe_float(p.get('價格', 0))
        monthly_revenue = safe_float(p.get('月銷額', price * monthly_sales))

        result.append({
            'ASIN': p.get('ASIN', ''),
            '標題': p.get('標題', '')[:80],
            '價格': price,
            '月銷量': monthly_sales,
            '月銷額': monthly_revenue,
            '評分': safe_float(p.get('星級', p.get('評分', 0))),
            '品牌': p.get('品牌', 'Unknown'),
            '評論數': safe_int(p.get('評論數', 0)),
            '賣家來源': p.get('賣家來源', ''),
            '賣家': p.get('賣家', ''),
            '上架天數': safe_int(p.get('上架天數', p.get('上線天數', 0))),
            '類目排名': p.get('類目排名', p.get('所處類目排名', '')),
            '圖片': p.get('圖片', ''),
        })

    return result


def calculate_five_dimension_score(stats: dict, products: list = None) -> dict:
    """
    計算五維評分 (標準版本)

    評分標準:
    - 市場規模 (20分): >10M=20, >5M=17, >1M=14, 其他=10
    - 增長潛力 (25分): 低評論佔比>40%=22, >20%=18, 其他=14
    - 競爭烈度 (20分): Top3<30%=18, <50%=14, 其他=8
    - 進入壁壘 (20分): Amazon佔比+新品機會組合評分
    - 利潤空間 (15分): 均價>$300=12, >$150=10, >$50=7, 其他=4
    """
    scores = {}

    # 從產品列表計算統計資料（如果 stats 中沒有）
    if products and not stats.get('top3_brands_sales_volume_share'):
        total_revenue = sum(p.get('月銷額', 0) for p in products)
        if total_revenue > 0:
            # 計算品牌份額
            brand_revenue = {}
            for p in products:
                brand = p.get('品牌', 'Unknown')
                brand_revenue[brand] = brand_revenue.get(brand, 0) + p.get('月銷額', 0)

            # Top3 份額
            sorted_brands = sorted(brand_revenue.values(), reverse=True)
            top3_share = sum(sorted_brands[:3]) / total_revenue * 100 if sorted_brands else 0
            stats['top3_brands_sales_volume_share'] = str(top3_share)

            # Amazon 份額
            amazon_revenue = sum(p.get('月銷額', 0) for p in products if p.get('賣家') == 'Amazon')
            amazon_share = amazon_revenue / total_revenue * 100
            stats['amazonOwned_sales_volume_share'] = str(amazon_share)

            # 低評論產品份額
            low_review_revenue = sum(p.get('月銷額', 0) for p in products if p.get('評論數', 0) < 300)
            low_review_share = low_review_revenue / total_revenue * 100
            stats['low_reviews_sales_volume_share'] = str(low_review_share)

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
    scores = calculate_five_dimension_score(stats, products)
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
        print("用法: python sse_decoder.py <SSE響應檔案> [輸出目錄] [產品數量] [--verbose]")
        print("\n示例:")
        print("  python sse_decoder.py response.txt")
        print("  python sse_decoder.py response.txt ./output 50")
        print("  python sse_decoder.py response.txt ./output 20 --verbose")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 20
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    try:
        # 解碼 SSE 響應
        print(f"\n正在解析檔案: {file_path}")
        data = decode_sse_response(file_path, verbose=verbose)

        # 儲存完整資料
        saved_file = save_decoded_data(data, output_dir)
        print(f"\n✓ 完整資料已儲存到: {saved_file}")

        # 提取統計資料
        stats = extract_category_stats(data)

        # 提取產品列表
        products = extract_top_products(data, limit)

        # 列印摘要
        print_summary(stats, products)

        # 計算並儲存評分
        scores = calculate_five_dimension_score(stats, products)
        scores_file = os.path.join(output_dir, 'scores.json')
        with open(scores_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 五維評分已儲存到: {scores_file}")

        # 儲存產品列表到單獨檔案
        products_file = os.path.join(output_dir, 'top_products.json')
        with open(products_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        print(f"✓ Top {len(products)} 產品已儲存到: {products_file}")

    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
