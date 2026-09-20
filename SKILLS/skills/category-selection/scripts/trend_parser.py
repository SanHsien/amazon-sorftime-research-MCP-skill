#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime 類目趨勢資料解析器
解析 category_trend API 返回的 SSE 格式資料
"""

import re
import json
import codecs
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional


def decode_sse_trend(file_path: str) -> dict:
    """
    解碼 Sorftime category_trend SSE 響應

    Args:
        file_path: SSE 響應檔案路徑

    Returns:
        dict: 解碼後的趨勢資料
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

    # 方法2: 直接搜尋 JSON 模式
    # 趨勢資料通常包含 "趨勢日期" 或 "trendDate" 欄位
    patterns = [
        r'"趨勢日期":\[([^\]]+)\]',
        r'"trendDate":\[([^\]]+)\]',
        r'"趨勢值":\[([^\]]+)\]',
        r'"trendValue":\[([^\]]+)\]'
    ]

    result = {}
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            key = 'dates' if '日期' in pattern or 'Date' in pattern else 'values'
            # 提取陣列內容
            array_content = match.group(1)
            # 簡單解析（假設是字串陣列）
            if array_content:
                result[key] = [item.strip('"') for item in array_content.split(',')]

    return result


def extract_trend_data(data: dict, trend_type: str) -> dict:
    """
    從解碼資料中提取趨勢資訊

    Args:
        data: 解碼後的 JSON 資料
        trend_type: 趨勢型別

    Returns:
        dict: 包含日期和值的趨勢資料
    """
    # 趨勢資料可能的欄位名
    date_field_candidates = ['趨勢日期', 'trendDate', 'dates', 'date']
    value_field_candidates = ['趨勢值', 'trendValue', 'values', 'data', 'value']

    dates = []
    values = []

    for field in date_field_candidates:
        if field in data:
            dates = data[field]
            break

    for field in value_field_candidates:
        if field in data:
            values = data[field]
            break

    # 如果資料是巢狀結構，嘗試提取
    if not dates or not values:
        # 檢查是否有類目趨勢欄位
        if '類目趨勢' in data:
            trend_info = data['類目趨勢']
            dates = trend_info.get('趨勢日期', trend_info.get('trendDate', []))
            values = trend_info.get('趨勢值', trend_info.get('trendValue', []))

    return {
        'type': trend_type,
        'dates': dates,
        'values': values
    }


def save_trend_json(trend_data: dict, output_dir: str, filename: str = 'trend_data.json'):
    """儲存合併後的趨勢資料到 JSON 檔案"""
    output_file = os.path.join(output_dir, filename)

    # 如果檔案已存在，讀取併合並
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        existing_data.update(trend_data)
        trend_data = existing_data

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)

    return output_file


def parse_all_trends(input_dir: str) -> dict:
    """
    解析目錄中的所有趨勢檔案

    Args:
        input_dir: 包含趨勢原始檔案的目錄

    Returns:
        dict: 所有趨勢資料的字典
    """
    trend_files = {
        '類目月銷量趨勢': 'trend_類目月銷量趨勢_raw.txt',
        '平均售價趨勢': 'trend_平均售價趨勢_raw.txt',
        '平均星級趨勢': 'trend_平均星級趨勢_raw.txt',
        '品牌數量趨勢': 'trend_品牌數量趨勢_raw.txt'
    }

    all_trends = {}

    for trend_type, filename in trend_files.items():
        file_path = os.path.join(input_dir, filename)
        if not os.path.exists(file_path):
            print(f"  跳過: {filename} (檔案不存在)")
            continue

        try:
            decoded = decode_sse_trend(file_path)
            trend = extract_trend_data(decoded, trend_type)

            # 轉換資料格式為圖表所需格式
            if trend['dates'] and trend['values']:
                # 清理資料
                dates = [str(d).strip('"').strip("'") for d in trend['dates']]
                values = [float(v) if isinstance(v, (int, float, str)) else 0 for v in trend['values']]

                # 根據趨勢型別儲存到不同的鍵
                if trend_type == '類目月銷量趨勢':
                    all_trends['sales_trend'] = {'dates': dates, 'sales': values}
                elif trend_type == '平均售價趨勢':
                    all_trends['price_trend'] = {'dates': dates, 'prices': values}
                elif trend_type == '平均星級趨勢':
                    all_trends['rating_trend'] = {'dates': dates, 'ratings': values}
                elif trend_type == '品牌數量趨勢':
                    all_trends['brand_count_trend'] = {'dates': dates, 'count': values}

                print(f"  ✓ {trend_type}: {len(dates)} 個資料點")

        except Exception as e:
            print(f"  ✗ {trend_type} 解析失敗: {e}")

    return all_trends


def main():
    if len(sys.argv) < 2:
        print("用法: python trend_parser.py <資料目錄>")
        print("\n示例:")
        print("  python trend_parser.py category-reports/Sofas_US_20260304")
        sys.exit(1)

    input_dir = sys.argv[1]

    print("\n" + "="*60)
    print("類目趨勢資料解析")
    print("="*60)

    # 解析所有趨勢檔案
    all_trends = parse_all_trends(input_dir)

    if all_trends:
        # 儲存合併資料
        output_file = save_trend_json(all_trends, input_dir)
        print(f"\n趨勢資料已儲存到: {output_file}")

        # 列印摘要
        print("\n資料摘要:")
        for key, data in all_trends.items():
            print(f"  - {key}: {len(data.get('dates', []))} 個月")
    else:
        print("\n警告: 未找到有效的趨勢資料")


if __name__ == "__main__":
    main()
