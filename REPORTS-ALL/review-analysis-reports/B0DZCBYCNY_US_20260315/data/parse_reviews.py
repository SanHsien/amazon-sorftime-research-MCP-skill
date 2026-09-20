#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析 Sorftime 評論 SSE 響應並生成差評分析"""

import json
import codecs
from datetime import datetime
from collections import defaultdict

# 讀取原始 SSE 檔案
sse_file = "D:/amazon-mcp/review-analysis-reports/B0DZCBYCNY_US_20260315/data/raw_reviews_sse.txt"

with open(sse_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 SSE 資料中的 JSON
start_idx = content.find('data: ')
if start_idx == -1:
    print("錯誤: 未找到 SSE 資料格式")
    exit(1)

json_str = content[start_idx + 6:]  # 跳過 "data: "
try:
    data = json.loads(json_str)
except json.JSONDecodeError:
    # 如果第一個解析失敗，嘗試找到完整的 JSON 結束
    end_idx = json_str.find('}\n\n')
    if end_idx != -1:
        json_str = json_str[:end_idx + 1]
        data = json.loads(json_str)
    else:
        print("錯誤: 無法解析 JSON")
        exit(1)

# 提取評論文字
text = data['result']['content'][0]['text']

# 查詢評論陣列起始位置
reviews_start = text.find('[{')
if reviews_start == -1:
    print("錯誤: 未找到評論陣列")
    exit(1)

reviews_json = text[reviews_start:]
reviews = json.loads(reviews_json)

print(f"總評論數: {len(reviews)}")

# 過濾 1-3 星評論
negative_reviews = [r for r in reviews if float(r.get('評星', 5)) <= 3.0]
print(f"差評數 (1-3星): {len(negative_reviews)}")

# 列印前5條評論以便檢查
print("\n前5條差評:")
for i, review in enumerate(negative_reviews[:5]):
    print(f"\n[{i+1}] {review.get('評星', 'N/A')}星 - {review.get('標題', 'N/A')}")
    print(f"評論: {review.get('評論', 'N/A')[:200]}...")

# 儲存解析後的評論
with open("D:/amazon-mcp/review-analysis-reports/B0DZCBYCNY_US_20260315/data/parsed_reviews.json", 'w', encoding='utf-8') as f:
    json.dump(negative_reviews, f, ensure_ascii=False, indent=2)

print(f"\n解析後的評論已儲存到 parsed_reviews.json")
