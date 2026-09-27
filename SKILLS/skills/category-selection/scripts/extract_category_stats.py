#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
從 Sorftime category_report 響應中提取統計資料
處理大資料檔案 (>25000 tokens) 的標準工具
"""

import re
import sys
import json
from typing import Dict, Optional


def extract_statistics(file_path: str) -> Dict[str, str]:
    """
    從 Sorftime 響應檔案中提取類目統計資料

    Args:
        file_path: Sorftime API 響應檔案路徑

    Returns:
        包含統計資料的字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"錯誤: 檔案不存在 {file_path}")
        return {}
    except Exception as e:
        print(f"錯誤: 讀取檔案失敗 - {e}")
        return {}

    # 定義需要提取的欄位模式
    patterns = {
        '總銷量': r'"top100產品月銷量":"?(\d+)"?',
        '總銷額': r'"top100產品月銷額":"?([\d.]+)"?',
        '平均價格': r'"average_price":"?([\d.]+)"?',
        '中位數價格': r'"median_price":"?([\d.]+)"?',
        'Top3品牌佔比': r'"top3_brands_sales_volume_share":"?([\d.]+%?)"?',
        'Amazon自營佔比': r'"amazonOwned_sales_volume_share":"?([\d.]+%?)"?',
        '高評分佔比': r'"high_rated_sales_volume_share":"?([\d.]+%?)"?',
        '低評論佔比': r'"low_reviews_sales_volume_share":"?([\d.]+%?)"?',
    }

    results = {}
    for name, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            results[name] = match.group(1)
        else:
            results[name] = "未找到"

    return results


def calculate_scores_from_stats(stats: Dict[str, str]) -> Dict[str, float]:
    """
    基於統計資料計算五維評分

    Args:
        stats: 從 extract_statistics 返回的統計資料

    Returns:
        五維評分字典
    """
    # 輔助函式：安全提取數值
    def safe_float(value, default=0):
        try:
            return float(str(value).replace('%', '').replace(',', ''))
        except:
            return default

    # 提取數值
    revenue = safe_float(stats.get('總銷額', 0))
    top3_share = safe_float(stats.get('Top3品牌佔比', 0))
    amazon_share = safe_float(stats.get('Amazon自營佔比', 0))
    low_review_share = safe_float(stats.get('低評論佔比', 0))
    avg_price = safe_float(stats.get('平均價格', 0))

    scores = {}

    # 1. 市場規模 (20分)
    if revenue > 10000000:
        scores['市場規模'] = 20
    elif revenue > 5000000:
        scores['市場規模'] = 17
    elif revenue > 1000000:
        scores['市場規模'] = 14
    else:
        scores['市場規模'] = 10

    # 2. 增長潛力 (25分) - 基於低評論產品佔比 (新品機會)
    if low_review_share > 40:
        scores['增長潛力'] = 22
    elif low_review_share > 20:
        scores['增長潛力'] = 18
    else:
        scores['增長潛力'] = 14

    # 3. 競爭烈度 (20分) - 基於 Top3 品牌佔比
    if top3_share < 30:
        scores['競爭烈度'] = 18  # 低度集中
    elif top3_share < 50:
        scores['競爭烈度'] = 14  # 中度集中
    else:
        scores['競爭烈度'] = 8   # 高度集中

    # 4. 進入壁壘 (20分)
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
    if avg_price > 300:
        scores['利潤空間'] = 12
    elif avg_price > 150:
        scores['利潤空間'] = 10
    elif avg_price > 50:
        scores['利潤空間'] = 7
    else:
        scores['利潤空間'] = 4

    # 計算總分
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


def main():
    """命令列入口"""
    if len(sys.argv) < 2:
        print("用法: python extract_category_stats.py <響應檔案路徑>")
        print("\n示例:")
        print("  python extract_category_stats.py temp_response.txt")
        print("\n或者從標準輸入讀取:")
        print("  cat temp_response.txt | python extract_category_stats.py -")
        sys.exit(1)

    file_path = sys.argv[1]

    # 提取統計資料
    stats = extract_statistics(file_path)

    if not stats:
        print("未能提取到統計資料")
        sys.exit(1)

    print("=" * 60)
    print("類目統計資料")
    print("=" * 60)

    # 列印統計資料
    for name, value in stats.items():
        if value != "未找到":
            print(f"  {name}: {value}")

    # 計算評分
    scores = calculate_scores_from_stats(stats)

    print("\n" + "=" * 60)
    print("五維評分")
    print("=" * 60)

    for dimension, score in scores.items():
        if dimension not in ['總分', '評級']:
            print(f"  {dimension}: {score}")

    print(f"\n  總分: {scores['總分']}/100")
    print(f"  評級: {scores['評級']}")

    # 輸出 JSON 格式 (便於指令碼使用)
    if '--json' in sys.argv:
        output = {
            'statistics': stats,
            'scores': scores
        }
        print("\n" + "=" * 60)
        print("JSON 格式輸出")
        print("=" * 60)
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
