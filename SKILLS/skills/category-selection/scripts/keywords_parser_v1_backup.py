#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime 類目關鍵詞解析器
處理 category_keywords 返回的 SSE 響應
"""

import re
import json
import codecs
import sys
import os


def fix_mojibake(obj):
    """
    修復 UTF-8/Latin-1 雙重編碼問題 (Mojibake)

    當 UTF-8 位元組被錯誤地解釋為 Latin-1 時會產生亂碼:
    解決方法: encode('latin-1') → decode('utf-8')
    """
    if isinstance(obj, dict):
        return {fix_mojibake(k): fix_mojibake(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_mojibake(item) for item in obj]
    elif isinstance(obj, str):
        # 檢查是否包含典型 Mojibake 模式
        mojibake_patterns = ['æ ', 'é¢', 'å ', 'ä»£', 'åç', 'å³']
        if any(p in obj for p in mojibake_patterns):
            try:
                return obj.encode('latin-1').decode('utf-8')
            except:
                return obj
        return obj
    else:
        return obj


def decode_keywords_response(file_path: str) -> list:
    """
    解碼 category_keywords SSE 響應檔案

    Args:
        file_path: SSE 響應檔案路徑

    Returns:
        list: 關鍵詞資料列表
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 方法 1: 查詢 SSE data 行
    for line in content.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]
            try:
                data = json.loads(json_text)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text and ('關鍵詞' in result_text or 'keyword' in result_text.lower()):
                    # 解碼 Unicode 轉義
                    decoded = codecs.decode(result_text, 'unicode-escape')

                    # 提取 JSON 陣列 - 支援多種格式
                    # 格式 1: [{"關鍵詞": 或格式 2: [{"keyword":
                    start = decoded.find('[{"關鍵詞"')
                    if start == -1:
                        start = decoded.find('[{"keyword"')
                    if start == -1:
                        start = decoded.find('[{')

                    if start != -1:
                        # 找到匹配的結束括號
                        bracket_count = 0
                        in_string = False
                        escape_next = False
                        end = -1

                        for i in range(start, len(decoded)):
                            c = decoded[i]

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
                            json_str = decoded[start:end]
                            result = json.loads(json_str)
                            # 修復可能的編碼問題
                            return fix_mojibake(result)
            except Exception as e:
                print(f"方法1解析失敗: {e}")
                continue

    # 方法 2: 備用方法 - 直接從原始內容提取
    # 查詢包含關鍵詞的 JSON 陣列片段
    bracket_count = 0
    in_array = False
    start = -1
    end = -1

    for i, c in enumerate(content):
        if c == '[':
            if not in_array:
                # 檢查這是否是關鍵詞陣列的開始
                lookahead = content[i:i+200]
                if ('關鍵詞' in lookahead or 'keyword' in lookahead.lower()):
                    in_array = True
                    start = i
            bracket_count += 1
        elif c == ']':
            bracket_count -= 1
            if in_array and bracket_count == 0:
                end = i + 1
                break

    if start != -1 and end != -1:
        raw_json = content[start:end]
        try:
            # 清理並解碼
            decoded = codecs.decode(raw_json, 'unicode-escape')
            result = json.loads(decoded)
            return fix_mojibake(result)
        except Exception as e:
            print(f"方法2解析失敗: {e}")

    # 方法 3: 使用正規表示式提取關鍵詞陣列
    try:
        # 查詢 [{...}] 模式
        array_pattern = r'\[\{[^\]]*?"關鍵詞"[^\]]*?\}'
        matches = re.findall(array_pattern, content, re.DOTALL)
        for match in matches:
            try:
                decoded = codecs.decode(match, 'unicode-escape')
                result = json.loads(decoded)
                if isinstance(result, list) and len(result) > 0:
                    return fix_mojibake(result)
            except:
                continue
    except Exception as e:
        print(f"方法3解析失敗: {e}")

    raise ValueError("無法解析關鍵詞資料 - 請檢查檔案格式是否正確")


def format_keyword_data(kw: dict) -> dict:
    """格式化單個關鍵詞資料"""
    return {
        '關鍵詞': kw.get('關鍵詞', ''),
        '周搜尋排名': kw.get('周搜尋排名', '0'),
        '周搜尋量': kw.get('周搜尋量', '0'),
        '月搜尋量': kw.get('月搜尋量', '0'),
        'CPC競價': kw.get('cpc精準競價', '0'),
        '搜尋結果數': kw.get('搜尋結果數', '0'),
        '新品佔比': kw.get('搜尋結果前3頁產品中上線3個月內產品數量佔比', '0'),
    }


def print_keywords_table(keywords: list, limit: int = 20):
    """列印關鍵詞表格"""
    print("\n" + "=" * 90)
    print(f"類目核心關鍵詞 Top {min(len(keywords), limit)}")
    print("=" * 90)
    print(f"{'排名':<6}{'關鍵詞':<25}{'月搜尋量':<15}{'周排名':<10}{'CPC競價':<10}{'新品佔比':<10}")
    print("-" * 90)

    for i, kw in enumerate(keywords[:limit], 1):
        keyword = kw.get('關鍵詞', 'N/A')
        monthly = kw.get('月搜尋量', '0')
        rank = kw.get('周搜尋排名', '0')
        cpc = kw.get('CPC競價', '0')
        new_pct = kw.get('新品佔比', '0')

        # 格式化數字
        try:
            monthly = f"{int(float(monthly)):,}"
        except:
            pass

        try:
            cpc = f"${float(cpc):.2f}"
        except:
            cpc = f"${cpc}"

        try:
            new_pct = f"{new_pct}%"
        except:
            pass

        print(f"{i:<6}{keyword:<25}{monthly:<15}{rank:<10}{cpc:<10}{new_pct:<10}")


def save_keywords(keywords: list, output_file: str):
    """儲存關鍵詞到檔案"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("類目核心關鍵詞\n")
        f.write("=" * 90 + "\n")
        f.write(f"{'排名':<6}{'關鍵詞':<25}{'月搜尋量':<15}{'周排名':<10}{'CPC競價':<10}{'新品佔比':<10}\n")
        f.write("-" * 90 + "\n")

        for i, kw in enumerate(keywords, 1):
            keyword = kw.get('關鍵詞', 'N/A')
            monthly = kw.get('月搜尋量', '0')
            rank = kw.get('周搜尋排名', '0')
            cpc = kw.get('CPC競價', '0')
            new_pct = kw.get('新品佔比', '0')

            try:
                monthly = f"{int(float(monthly)):,}"
            except:
                pass
            try:
                cpc = f"${float(cpc):.2f}"
            except:
                pass
            try:
                new_pct = f"{new_pct}%"
            except:
                pass

            f.write(f"{i:<6}{keyword:<25}{monthly:<15}{rank:<10}{cpc:<10}{new_pct:<10}\n")


def main():
    if len(sys.argv) < 2:
        print("用法: python keywords_parser.py <SSE響應檔案> [輸出目錄] [顯示數量]")
        print("\n示例:")
        print("  python keywords_parser.py keywords_response.txt")
        print("  python keywords_parser.py keywords_response.txt ./output 50")
        sys.exit(1)

    file_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '.'
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 20

    try:
        # 解碼關鍵詞響應
        keywords_raw = decode_keywords_response(file_path)

        # 格式化資料
        keywords = [format_keyword_data(kw) for kw in keywords_raw]

        # 列印表格
        print_keywords_table(keywords, limit)

        # 儲存到檔案
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'keywords.txt')
        save_keywords(keywords, output_file)
        print(f"\n關鍵詞已儲存到: {output_file}")

        # 儲存 JSON 格式
        json_file = os.path.join(output_dir, 'keywords.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(keywords, f, ensure_ascii=False, indent=2)
        print(f"JSON 格式已儲存到: {json_file}")

    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
