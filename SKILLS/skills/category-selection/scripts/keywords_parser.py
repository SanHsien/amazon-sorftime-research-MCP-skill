#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime 關鍵詞 SSE 響應解析器 v3.0 - 穩定增強版

支援多種關鍵詞資料格式:
1. 中文鍵名: [{"關鍵詞": "...", "月搜尋量": "..."}]
2. 英文鍵名: [{"keyword": "...", "monthlySearchVolume": "..."}]
3. 巢狀轉義格式
4. 直接從 SSE data: 行提取

主要改進:
1. 更好的錯誤處理
2. 支援直接 JSON 格式
3. 自動格式標準化
"""

import re
import json
import codecs
import sys
import os


def safe_int(value, default=0):
    """安全地轉換為整數"""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # 移除非數字字元
        cleaned = re.sub(r'[^\d]', '', value)
        try:
            return int(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def parse_keywords_sse(file_path: str, verbose: bool = False) -> list:
    """
    解析關鍵詞 SSE 響應檔案

    Args:
        file_path: SSE 響應檔案路徑
        verbose: 是否顯示除錯資訊

    Returns:
        list: 解析後的關鍵詞列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if verbose:
        print(f"[DEBUG] 檔案大小: {len(content)} 位元組")
        print(f"[DEBUG] 檔案前200字元: {content[:200]}")

    keywords = []

    # 策略 1: 標準 SSE 格式
    if verbose:
        print("\n[策略1] 嘗試標準 SSE 格式...")

    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # 嘗試直接解析
                    try:
                        keywords = json.loads(result_text)
                        if isinstance(keywords, list) and keywords:
                            if verbose:
                                print(f"[策略1] ✓ 成功，找到 {len(keywords)} 個關鍵詞")
                            return keywords
                    except json.JSONDecodeError:
                        # 嘗試 Unicode 解碼
                        decoded = codecs.decode(result_text, 'unicode-escape')
                        keywords = json.loads(decoded)
                        if isinstance(keywords, list) and keywords:
                            if verbose:
                                print(f"[策略1] ✓ Unicode 解碼成功，找到 {len(keywords)} 個關鍵詞")
                            return keywords
            except Exception as e:
                if verbose:
                    print(f"[策略1] 失敗: {e}")
                continue

    # 策略 2: 直接 JSON 解析（已解碼的檔案）
    if verbose:
        print("\n[策略2] 嘗試直接 JSON 解析...")

    try:
        keywords = json.loads(content)
        if isinstance(keywords, list) and keywords:
            if verbose:
                print(f"[策略2] ✓ 成功，找到 {len(keywords)} 個關鍵詞")
            return keywords
    except:
        pass

    # 策略 3: 直接 JSON 陣列提取
    if verbose:
        print("\n[策略3] 嘗試直接 JSON 陣列提取...")

    # 查詢陣列開始
    patterns = [
        r'(\[{\"?關鍵詞\"?)',
        r'(\[{\"?keyword\"?)',
        r'(\[.*\"?關鍵詞\"?)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            # 找到陣列開始位置
            start = match.start()
            # 手動解析括號匹配
            bracket_count = 0
            in_string = False
            escape_next = False
            end = -1

            for i in range(start, len(content)):
                c = content[i]

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
                    if c == '[':
                        bracket_count += 1
                    elif c == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            end = i + 1
                            break

            if end != -1:
                raw_json = content[start:end]

                try:
                    keywords = json.loads(raw_json)
                    if isinstance(keywords, list) and keywords:
                        if verbose:
                            print(f"[策略3] ✓ 成功，找到 {len(keywords)} 個關鍵詞")
                        return keywords
                except json.JSONDecodeError:
                    # 嘗試 Unicode 解碼
                    try:
                        decoded = codecs.decode(raw_json, 'unicode-escape')
                        keywords = json.loads(decoded)
                        if isinstance(keywords, list) and keywords:
                            if verbose:
                                print(f"[策略3] ✓ Unicode 解碼成功，找到 {len(keywords)} 個關鍵詞")
                            return keywords
                    except:
                        pass

    raise ValueError("無法解析關鍵詞資料 - 所有策略均失敗")


def normalize_keywords(keywords: list) -> list:
    """標準化關鍵詞資料格式"""
    normalized = []

    for kw in keywords:
        if not isinstance(kw, dict):
            continue

        normalized_kw = {}

        # 標準化鍵名
        normalized_kw['關鍵詞'] = kw.get('關鍵詞') or kw.get('keyword', '')

        # 搜尋量欄位可能的鍵名
        for key in ['月搜尋量', 'monthlySearchVolume', '月搜', 'monthlySearch']:
            if key in kw:
                normalized_kw['月搜尋量'] = safe_int(kw[key])
                break
        if '月搜尋量' not in normalized_kw:
            normalized_kw['月搜尋量'] = 0

        # 周搜尋量
        for key in ['周搜尋量', 'weeklySearchVolume', '周搜', 'weeklySearch']:
            if key in kw:
                normalized_kw['周搜尋量'] = safe_int(kw[key])
                break
        if '周搜尋量' not in normalized_kw:
            normalized_kw['周搜尋量'] = 0

        # 其他常用欄位
        normalized_kw['周搜尋排名'] = kw.get('周搜尋排名', kw.get('weeklySearchRank', ''))
        normalized_kw['CPC競價'] = kw.get('CPC競價', kw.get('cpc精準競價', kw.get('cpcBid', kw.get('cpc', ''))))

        normalized.append(normalized_kw)

    return normalized


def main():
    if len(sys.argv) < 2:
        print("用法: python keywords_parser.py <SSE響應檔案> [輸出目錄] [產品數量] [--verbose]")
        print("\n示例:")
        print("  python keywords_parser.py keywords_raw.txt")
        print("  python keywords_parser.py keywords_raw.txt ./output 50")
        print("  python keywords_parser.py keywords_raw.txt ./output 20 --verbose")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 50
    verbose = '--verbose' in sys.argv or '-v' in sys.argv

    try:
        print(f"\n正在解析關鍵詞檔案: {file_path}")

        # 解析關鍵詞
        keywords = parse_keywords_sse(file_path, verbose=verbose)

        # 標準化格式
        normalized = normalize_keywords(keywords)

        print(f"\n✓ 成功解析 {len(normalized)} 個關鍵詞")

        # 儲存
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'keywords.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)

        print(f"✓ 關鍵詞已儲存到: {output_file}")

        # 顯示 Top 10
        display_count = min(10, len(normalized))
        print(f"\n【Top {display_count} 關鍵詞】")
        print("-" * 80)
        for i, kw in enumerate(normalized[:display_count], 1):
            print(f"{i:2}. {kw['關鍵詞']:<30} | 月搜尋: {kw['月搜尋量']:,} | 周搜尋: {kw['周搜尋量']:,}")
        print("-" * 80)

    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
