#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""驗證分類對映"""

import json

# 讀取原始關鍵詞
with open('keywords_raw.json', 'r', encoding='utf-8') as f:
    keywords = json.load(f)

# 讀取分類結果
with open('categorized_result.json', 'r', encoding='utf-8') as f:
    categorized = json.load(f)

# 構建分類對映
category_map = {}
for category, kw_list in categorized.items():
    for kw in kw_list:
        category_map[kw.lower()] = category

# 驗證每個關鍵詞是否都被正確分類
print('驗證分類對映:')
print('=' * 60)

for kw in keywords:
    keyword = kw['keyword']
    normalized = keyword.lower()
    category = category_map.get(normalized, 'UNCATEGORIZED')

    # 只顯示前10個和後10個
    idx = keywords.index(kw)
    if idx < 10 or idx >= len(keywords) - 5:
        print(f'{keyword:45} -> {category}')

# 統計
print('=' * 60)
print('分類統計:')
for cat in categorized:
    print(f'  {cat}: {len(categorized[cat])} 個')

uncategorized_count = sum(1 for kw in keywords if kw['keyword'].lower() not in category_map)
print(f'  UNCATEGORIZED: {uncategorized_count} 個')

# 檢查是否有重複分類
print('=' * 60)
print('檢查重複分類:')
all_categorized = set()
for cat, kw_list in categorized.items():
    for kw in kw_list:
        if kw.lower() in all_categorized:
            print(f'警告: 關鍵詞 "{kw}" 被重複分類!')
        all_categorized.add(kw.lower())

print('驗證完成!')
