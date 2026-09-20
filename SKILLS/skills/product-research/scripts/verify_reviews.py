#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
驗證 Reviews 資料完整性
"""
import json
import os
import sys

def verify_reviews_data(reviews_path):
    """驗證 Reviews 資料"""
    if not os.path.exists(reviews_path):
        print(f"✗ 檔案不存在: {reviews_path}")
        return False

    with open(reviews_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"=== Reviews 資料驗證 ===")
    print(f"檔案路徑: {reviews_path}")
    print(f"檔案大小: {os.path.getsize(reviews_path)/1024:.1f} KB")
    print()

    print(f"競品數量: {len(data)}")

    total_reviews = 0
    for asin, info in data.items():
        desc = info.get('description', 'N/A')
        count = info.get('review_count', 0)
        reviews = info.get('reviews', [])

        if isinstance(count, int):
            total_reviews += count

        review_count = len(reviews) if isinstance(reviews, list) else 0
        print(f"  - {asin}: {desc} ({count} 條，儲存 {review_count} 條)")

    print()
    print(f"總差評數: {total_reviews}")
    print("✓ 資料驗證透過")

    return True


def find_all_reviews_dirs():
    """查詢所有 Reviews 資料目錄"""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # 可能的目錄位置
    search_paths = [
        os.path.join(project_root, 'product-research-reports'),  # 新的輸出目錄
        # os.path.join(project_root, 'product-research'),  # 舊的輸出目錄（已廢棄）
    ]

    print(f"=== 搜尋 Reviews 資料目錄 ===")
    print(f"專案根目錄: {project_root}")
    print()

    found = []
    for base_path in search_paths:
        if not os.path.exists(base_path):
            continue

        for root, dirs, files in os.walk(base_path):
            if 'competitor_reviews.json' in files:
                # 如果在 raw 目錄，記錄父目錄
                if os.path.basename(root) == 'raw':
                    found.append(os.path.dirname(root))
                    print(f"✓ 找到: {os.path.dirname(root)}")
                else:
                    found.append(root)
                    print(f"✓ 找到: {root}")

    return found


if __name__ == '__main__':
    # 查詢所有 Reviews 資料
    dirs = find_all_reviews_dirs()

    if not dirs:
        print("\n未找到任何 Reviews 資料")
        sys.exit(1)

    print(f"\n共找到 {len(dirs)} 個資料目錄")

    # 驗證最新的資料
    latest_dir = max(dirs, key=lambda x: os.path.getmtime(x))
    reviews_path = os.path.join(latest_dir, 'raw', 'competitor_reviews.json')

    print(f"\n驗證最新資料: {latest_dir}")
    print()

    verify_reviews_data(reviews_path)
