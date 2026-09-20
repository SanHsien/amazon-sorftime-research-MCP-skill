#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sorftime SSE 響應解析器 - 關鍵詞專用版本
複用 category-selection 的解析邏輯，適配關鍵詞資料格式
"""

import json
import codecs
import re


def fix_mojibake(text):
    """
    修復 Mojibake 編碼問題 (UTF-8/Latin-1 雙重編碼)
    """
    if isinstance(text, str):
        try:
            return text.encode('latin-1').decode('utf-8')
        except:
            return text
    elif isinstance(text, dict):
        return {fix_mojibake(k): fix_mojibake(v) for k, v in text.items()}
    elif isinstance(text, list):
        return [fix_mojibake(item) for item in text]
    return text


def escape_control_chars_in_json(json_str):
    """Escape control characters only within JSON string values"""
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        c = json_str[i]

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

        if in_string:
            # Within a string, escape control characters
            if c == '\r':
                result.append('\\r')
            elif c == '\n':
                result.append('\\n')
            elif c == '\t':
                result.append('\\t')
            elif ord(c) < 32:
                # Other control chars - replace with space
                result.append(' ')
            else:
                result.append(c)
        else:
            result.append(c)

        i += 1

    return ''.join(result)


def escape_control_chars_in_json_strings(json_str):
    """轉義 JSON 字串值中的控制字元"""
    result = []
    i = 0
    in_string = False
    escape_next = False

    while i < len(json_str):
        c = json_str[i]

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

        if in_string:
            if c == '\n':
                result.append('\\n')
            elif c == '\r':
                result.append('\\r')
            elif c == '\t':
                result.append('\\t')
            elif ord(c) < 32:
                result.append(' ')
            else:
                result.append(c)
        else:
            result.append(c)

        i += 1

    return ''.join(result)


def parse_sse_response(response: str) -> dict:
    """
    解析 Sorftime SSE 響應

    Args:
        response: curl 返回的 SSE 格式響應

    Returns:
        dict: 解析後的資料
    """
    result = {'text': '', 'data': None, 'has_error': False, 'error': None}

    # 提取 SSE data 行
    for line in response.split('\n'):
        if line.startswith('data: '):
            json_text = line[6:]
            try:
                # 先轉義控制字元，再解析 JSON
                escaped_json = escape_control_chars_in_json(json_text)
                data = json.loads(escaped_json)
                result_text = data.get('result', {}).get('content', [{}])[0].get('text', '')
                if result_text:
                    # 解碼 Unicode 轉義
                    decoded = codecs.decode(result_text, 'unicode-escape')
                    # 修復 Mojibake
                    decoded = fix_mojibake(decoded)
                    result['text'] = decoded

                    # 嘗試解析為 JSON 資料
                    try:
                        result['data'] = parse_json_data(decoded)
                    except:
                        pass

                    return result
            except json.JSONDecodeError as e:
                result['error'] = str(e)
                result['has_error'] = True

    # 檢查錯誤響應
    if 'error' in response.lower() or 'Authentication required' in response:
        result['has_error'] = True
        result['error'] = response

    return result


def parse_json_data(text: str):
    """
    從文字中提取並解析 JSON 資料

    Args:
        text: 可能包含 JSON 的文字

    Returns:
        dict or list: 解析後的資料（陣列或物件）
    """
    # 轉義控制字元
    text = escape_control_chars_in_json_strings(text)

    # 找到 JSON 開始位置（優先查詢陣列，因為 Sorftime 返回陣列）
    json_start = text.find('[')
    if json_start == -1:
        # 嘗試查詢物件開始
        json_start = text.find('{')
        if json_start == -1:
            return {}

    # 使用括號匹配提取完整內容
    bracket_start = text[json_start]
    depth = 0
    in_string = False
    escape_next = False
    end = -1

    for i in range(json_start, len(text)):
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
            if c == bracket_start:
                depth += 1
            elif c == ('}' if bracket_start == '{' else ']'):
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break

    if end == -1:
        return {}

    json_str = text[json_start:end]

    # 嘗試解析
    try:
        data = json.loads(json_str)
        return fix_mojibake(data)
    except json.JSONDecodeError:
        return {}


def safe_int(value, default=0):
    """安全地轉換為整數"""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return int(float(cleaned)) if cleaned else default
        except ValueError:
            return default
    return default


def safe_float(value, default=0.0):
    """安全地轉換為浮點數"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r'[^\d.-]', '', value)
        try:
            return float(cleaned) if cleaned else default
        except ValueError:
            return default
    return default


def extract_keywords_from_response(response_data: dict) -> list:
    """
    從 API 響應中提取關鍵詞列表

    支援多種可能的響應格式:
    1. {"關鍵詞": [...]}  - 中文鍵名
    2. {"keywords": [...]} - 英文鍵名
    3. 直接是陣列
    """
    if not response_data:
        return []

    # 如果是陣列，直接返回
    if isinstance(response_data, list):
        return response_data

    # 查詢關鍵詞列表
    keywords = []

    # 可能的鍵名
    possible_keys = [
        '關鍵詞', 'keywords', 'Keywords', '流量詞', 'traffic_terms',
        'related_words', '延伸詞', 'result', 'data', 'items'
    ]

    for key in possible_keys:
        if key in response_data:
            value = response_data[key]
            if isinstance(value, list):
                keywords = value
                break

    return keywords


def normalize_keyword_data(raw_keyword: dict or str) -> dict:
    """
    標準化關鍵詞資料格式

    Args:
        raw_keyword: 原始關鍵詞資料（可能是字串或字典）

    Returns:
        dict: 標準化的關鍵詞資料
    """
    if isinstance(raw_keyword, str):
        return {
            'keyword': raw_keyword.strip(),
            'search_volume': 0,
            'cpc': 0,
            'competition': 'unknown'
        }

    if isinstance(raw_keyword, dict):
        # 標準化鍵名
        keyword = (
            raw_keyword.get('關鍵詞') or
            raw_keyword.get('keyword') or
            raw_keyword.get('Keyword') or
            raw_keyword.get('text') or
            ''
        ).strip()

        # 搜尋量可能的鍵名
        search_volume = 0
        for key in ['月搜尋量', 'monthlySearchVolume', 'search_volume', '搜尋量', 'volume']:
            if key in raw_keyword:
                search_volume = safe_int(raw_keyword[key])
                break

        # CPC 可能的鍵名
        cpc = 0
        for key in ['推薦競價', 'CPC競價', 'cpc', 'CPC', 'cpc_bid', 'suggested_bid']:
            if key in raw_keyword:
                cpc = safe_float(raw_keyword[key])
                break

        # 競爭度
        competition = raw_keyword.get('competition', raw_keyword.get('競爭度', 'unknown'))

        return {
            'keyword': keyword,
            'search_volume': search_volume,
            'cpc': cpc,
            'competition': competition
        }

    return {
        'keyword': '',
        'search_volume': 0,
        'cpc': 0,
        'competition': 'unknown'
    }
