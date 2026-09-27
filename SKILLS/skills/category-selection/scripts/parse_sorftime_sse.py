#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime category_report 健壯解析器 v2.0
處理 SSE 響應 + Unicode 轉義的複雜格式
"""

import re
import sys
import json
import codecs


def fix_chinese_keys(obj):
    """
    修復中文鍵名的編碼問題

    當 UTF-8 編碼的中文被錯誤地當作 Latin-1 解碼時，會產生亂碼。
    例如: "產品" -> "äº§å"
    修復方法: encode('latin-1') -> decode('utf-8')
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            # 修復鍵名
            if isinstance(key, str):
                # 檢測是否包含 UTF-8 被當作 Latin-1 解碼的亂碼
                if any(0x80 <= ord(c) <= 0xFF for c in key):
                    try:
                        fixed_key = key.encode('latin-1').decode('utf-8')
                    except:
                        fixed_key = key
                else:
                    fixed_key = key
            else:
                fixed_key = key

            # 遞迴修復值
            new_dict[fixed_key] = fix_chinese_keys(value)
        return new_dict
    elif isinstance(obj, list):
        return [fix_chinese_keys(item) for item in obj]
    else:
        return obj


def parse_sorftime_sse(file_path: str, limit: int = 100):
    """
    完整解析 Sorftime SSE 響應檔案

    Args:
        file_path: 響應檔案路徑
        limit: 提取產品數量

    Returns:
        dict: {statistics, products, scores}
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: 提取 SSE data 行
    result_text = None
    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]  # 去掉 'data: ' 字首
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    break
            except:
                continue

    if not result_text:
        return {'error': '無法提取 SSE data'}

    # Step 2: 解碼 Unicode 轉義
    # result_text 包含類似 {\u0022Top100\u4ea7\u54c1\u0022:[...]}
    # 需要先解碼 Unicode 轉義，再解析 JSON
    try:
        decoded = codecs.decode(result_text, 'unicode-escape')
    except:
        # 如果解碼失敗，嘗試直接使用
        decoded = result_text

    # Step 3: 提取 JSON 物件
    # 查詢第一個 { 和匹配的 }
    start = decoded.find('{')
    if start == -1:
        return {'error': '未找到 JSON 開始'}

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

    if end == -1:
        return {'error': '未找到 JSON 結束'}

    json_str = decoded[start:end]

    # Step 4: 解析 JSON (修復編碼問題)
    try:
        # 嘗試直接解析
        parsed = json.loads(json_str)
    except json.JSONDecodeError as e:
        # 清理控制字元後重試
        json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
        try:
            parsed = json.loads(json_str)
        except:
            return {'error': f'JSON 解析失敗: {e}'}

    # Step 4.5: 修復中文鍵名編碼問題
    parsed = fix_chinese_keys(parsed)

    # Step 5: 提取統計資料
    stats = extract_stats_from_parsed(parsed)

    # Step 6: 提取產品列表
    products = extract_products_from_parsed(parsed, limit)

    # Step 7: 計算評分
    scores = calculate_scores(stats)

    return {
        'statistics': stats,
        'products': products,
        'scores': scores
    }


def extract_stats_from_parsed(parsed: dict) -> dict:
    """從已解析的資料中提取統計資料"""
    stats = {}

    # 查詢類目統計報告
    category_stats = parsed.get('類目統計報告', {})

    if not category_stats:
        # 嘗試其他可能的鍵名
        for key in parsed.keys():
            if '統計' in key or 'stats' in key.lower():
                category_stats = parsed[key]
                break

    # 提取欄位
    field_mappings = {
        '總銷量': ['top100產品月銷量', '總銷量', 'total_sales'],
        '總銷額': ['top100產品月銷額', '總銷額', 'total_revenue'],
        '平均價格': ['average_price', '平均價格', 'avg_price'],
        '中位數價格': ['median_price', '中位數價格'],
        'Top3品牌佔比': ['top3_brands_sales_volume_share', 'Top3品牌佔比'],
        'Amazon自營佔比': ['amazonOwned_sales_volume_share', 'Amazon自營佔比'],
        '低評論佔比': ['low_reviews_sales_volume_share', '低評論佔比'],
    }

    for stat_name, possible_keys in field_mappings.items():
        for key in possible_keys:
            if key in category_stats:
                raw_value = category_stats[key]
                # 清理數值：從描述中提取數字
                stats[stat_name] = extract_numeric_value(raw_value)
                break
        if stat_name not in stats:
            stats[stat_name] = '未找到'

    return stats


def extract_numeric_value(raw_value):
    """
    從可能包含中文描述的值中提取數值
    例如: "銷量前的80%產品平均價格：17.239" -> "17.239"
    """
    if isinstance(raw_value, (int, float)):
        return raw_value

    if isinstance(raw_value, str):
        # 嘗試提取數字（包括小數和百分比）
        # 查詢所有數字模式
        patterns = [
            r'(\d+\.?\d*)%?',  # 數字 + 可選小數 + 可選百分號
            r':\s*(\d+\.?\d*)',  # 冒號後的數字
        ]

        for pattern in patterns:
            matches = re.findall(pattern, raw_value)
            if matches:
                # 取最後一個數字（通常是實際值）
                value = matches[-1]
                # 如果是百分比且小於100，可能需要處理
                try:
                    return float(value)
                except:
                    continue

        # 如果沒有找到，返回原始值
        return raw_value

    return raw_value


def extract_products_from_parsed(parsed: dict, limit: int) -> list:
    """從已解析的資料中提取產品列表"""
    products = []

    # 查詢產品列表
    products_key = None
    for key in parsed.keys():
        if 'Top100' in key or 'top100' in key or 'product' in key.lower():
            products_key = key
            break

    if not products_key:
        return []

    raw_products = parsed[products_key]
    if not isinstance(raw_products, list):
        return []

    for p in raw_products[:limit]:
        products.append({
            'ASIN': p.get('ASIN', ''),
            '標題': p.get('標題', p.get('title', '')),
            '價格': float(p.get('價格', p.get('price', 0))),
            '月銷量': int(p.get('月銷量', p.get('monthly_sales', 0))),
            '評分': float(p.get('星級', p.get('rating', 0))),
            '品牌': p.get('品牌', p.get('brand', 'Unknown'))
        })

    return products


def calculate_scores(stats: dict) -> dict:
    """計算五維評分"""
    def safe_float(value, default=0):
        try:
            return float(str(value).replace('%', '').replace(',', ''))
        except:
            return default

    revenue = safe_float(stats.get('總銷額', 0))
    top3_share = safe_float(stats.get('Top3品牌佔比', 0))
    amazon_share = safe_float(stats.get('Amazon自營佔比', 0))
    low_review_share = safe_float(stats.get('低評論佔比', 0))
    avg_price = safe_float(stats.get('平均價格', 0))

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


def print_report(result: dict):
    """列印報告"""
    if 'error' in result:
        print(f"錯誤: {result['error']}")
        return

    print("=" * 70)
    print("類目選品分析報告")
    print("=" * 70)

    # 統計資料
    if result.get('statistics'):
        print("\n【統計資料】")
        for name, value in result['statistics'].items():
            print(f"  {name}: {value}")

    # 評分
    if result.get('scores'):
        print("\n【五維評分】")
        scores = result['scores']
        for key, value in scores.items():
            if key not in ['總分', '評級']:
                print(f"  {key}: {value}")
        print(f"\n  總分: {scores.get('總分', 0)}/100")
        print(f"  評級: {scores.get('評級', '未知')}")

    # 產品列表
    if result.get('products'):
        print(f"\n【Top {len(result['products'])} 產品】")
        print("-" * 100)
        for i, p in enumerate(result['products'], 1):
            print(f"{i}. {p.get('ASIN')} | {p.get('品牌')} | "
                  f"${p.get('價格', 0):.2f} | {p.get('月銷量', 0):,}銷量 | "
                  f"{p.get('評分', 0):.1f}★")
            title = p.get('標題', '')[:60]
            print(f"   {title}...")
        print("-" * 100)


def main():
    """命令列入口"""
    if len(sys.argv) < 2:
        print("用法: python parse_sorftime_sse.py <響應檔案路徑> [產品數量] [--生成報告]")
        print("\n示例:")
        print("  python parse_sorftime_sse.py temp_response.txt 100")
        print("  python parse_sorftime_sse.py temp_response.txt 100 --生成報告")
        sys.exit(1)

    file_path = sys.argv[1]
    limit = 100
    generate_reports_flag = False

    for arg in sys.argv[2:]:
        if arg.isdigit():
            limit = int(arg)
        elif arg == '--生成報告' or arg == '--generate':
            generate_reports_flag = True

    result = parse_sorftime_sse(file_path, limit)
    print_report(result)

    if '--json' in sys.argv:
        print("\n" + "=" * 70)
        print("JSON 格式輸出")
        print("=" * 70)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    # 生成報告
    if generate_reports_flag:
        print("\n" + "=" * 70)
        print("正在生成報告...")
        print("=" * 70)

        try:
            from generate_reports import CategoryReportGenerator
            generator = CategoryReportGenerator(result)
            report_files = generator.generate_all()

            print("\n報告已儲存到:", generator.output_dir)
        except ImportError:
            print("報告生成模組未找到，跳過")


if __name__ == "__main__":
    main()
