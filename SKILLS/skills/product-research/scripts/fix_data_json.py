#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料驗證和修復指令碼 - 確保 data.json 結構正確

用法:
    python fix_data_json.py path/to/data.json
    python fix_data_json.py path/to/data.json --fix
"""

import sys
import os
import json
import argparse
from datetime import datetime
from pathlib import Path


def validate_data(data: dict) -> tuple[bool, list[str]]:
    """驗證資料結構"""
    errors = []
    warnings = []

    # 必需欄位檢查
    required_fields = ['metadata', 'market_overview']
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需欄位: {field}")

    # metadata 檢查
    if 'metadata' in data:
        metadata = data['metadata']
        required_metadata = ['category', 'site', 'date']
        for field in required_metadata:
            if field not in metadata:
                warnings.append(f"metadata 缺少欄位: {field}")

    # market_overview 檢查
    if 'market_overview' in data:
        mo = data['market_overview']
        required_mo = ['top100_monthly_sales', 'top100_monthly_revenue', 'avg_price']
        for field in required_mo:
            if field not in mo:
                warnings.append(f"market_overview 缺少欄位: {field}")

    # go_nogo 檢查
    if 'go_nogo' not in data:
        errors.append("缺少 go_nogo 欄位")
    else:
        gogono = data['go_nogo']
        if 'overall_score' not in gogono and 'total_score' not in gogono:
            warnings.append("go_nogo 缺少評分欄位")
        if 'decision' not in gogono and 'verdict' not in gogono:
            warnings.append("go_nogo 缺少決策欄位")

    # dimensions 檢查
    if 'dimensions' in data and data['dimensions']:
        # 檢查每個維度是否有正確的結構
        for i, dim in enumerate(data['dimensions']):
            if 'dimension' not in dim and 'name' not in dim:
                warnings.append(f"dimensions[{i}] 缺少 'dimension' 或 'name' 欄位")

    # voc_analysis 檢查
    if 'voc_analysis' in data and data['voc_analysis']:
        voc = data['voc_analysis']
        if 'dimensions' not in voc:
            warnings.append("voc_analysis 缺少 'dimensions' 欄位")

    is_valid = len(errors) == 0
    return is_valid, errors + warnings


def fix_data(data: dict) -> dict:
    """修復常見的資料結構問題"""
    # 修復 go_nogo 欄位名稱
    if 'go_nogo' in data:
        gogono = data['go_nogo']
        if 'verdict' in gogono and 'decision' not in gogono:
            gogono['decision'] = gogono['verdict']
        if 'total_score' in gogono and 'overall_score' not in gogono:
            gogono['overall_score'] = gogono['total_score']

    # 確保必需欄位存在
    if 'market_overview' not in data:
        data['market_overview'] = {}

    mo = data['market_overview']
    if 'top3_product_concentration' not in mo and 'top3_concentration' in mo:
        mo['top3_product_concentration'] = mo['top3_concentration']

    return data


def main():
    parser = argparse.ArgumentParser(description="資料驗證和修復指令碼")
    parser.add_argument("data_file", help="data.json 檔案路徑")
    parser.add_argument("--fix", action="store_true", help="自動修復問題")
    parser.add_argument("--output", "-o", help="輸出檔案路徑（預設覆蓋原檔案）")

    args = parser.parse_args()

    data_path = Path(args.data_file)
    if not data_path.exists():
        print(f"✗ 檔案不存在: {data_path}")
        return 1

    # 讀取資料
    print(f"讀取資料: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 驗證資料
    is_valid, messages = validate_data(data)

    print("\n驗證結果:")
    for msg in messages:
        prefix = "✗" if "錯誤" in msg or "缺少" in msg else "⚠"
        print(f"  {prefix} {msg}")

    if is_valid:
        print("\n✓ 資料結構驗證透過")
    else:
        print("\n✗ 資料結構存在問題")
        if not args.fix:
            print("  提示: 使用 --fix 引數嘗試自動修復")
            return 1

    # 修復資料
    if args.fix:
        print("\n修復資料...")
        data = fix_data(data)

        # 重新驗證
        is_valid_after, messages_after = validate_data(data)
        if is_valid_after:
            print("✓ 資料修復成功")
        else:
            print("⚠ 部分問題無法自動修復")

        # 儲存
        output_path = Path(args.output) if args.output else data_path
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 已儲存: {output_path}")

    return 0 if is_valid else 1


if __name__ == '__main__':
    sys.exit(main())
