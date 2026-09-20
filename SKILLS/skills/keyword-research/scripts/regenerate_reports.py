#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成報告，使用已有的分類結果

使用方式:
1. 從報告目錄內執行（自動檢測）:
   python regenerate_reports.py

2. 指定 ASIN 和站點:
   python regenerate_reports.py --asin B0FG6QG8C8 --site US

3. 指定完整輸出目錄:
   python regenerate_reports.py --dir "D:\\amazon-mcp\\keyword-reports\\B0FG6QG8C8_US_20260314"

4. 列出所有可用的報告目錄:
   python regenerate_reports.py --list
"""
import os
import sys
import json
import argparse
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from workflow import KeywordResearchWorkflow
from csv_generator import generate_csv_files
from generate_markdown_report import generate_markdown_report
from generate_html_dashboard import generate_html_dashboard


def list_available_reports(base_dir=None):
    """列出所有可用的報告目錄"""
    if base_dir is None:
        # 從當前目錄向上查詢 keyword-reports 目錄
        current_dir = os.path.abspath(os.getcwd())
        if 'keyword-reports' in current_dir:
            base_dir = current_dir
        else:
            # 嘗試相對路徑
            base_dir = os.path.join(os.path.dirname(SCRIPT_DIR), '..', '..', '..', 'keyword-reports')
            base_dir = os.path.abspath(base_dir)

    if not os.path.exists(base_dir):
        print(f"❌ 報告目錄不存在: {base_dir}")
        return

    print(f"📂 可用的報告目錄: {base_dir}\n")

    # 列出所有 ASIN_開頭的目錄
    dirs = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and '_' in item:
            # 檢查是否有 keywords_raw.json
            if os.path.exists(os.path.join(item_path, 'keywords_raw.json')):
                dirs.append(item)

    if not dirs:
        print("  沒有找到任何報告目錄")
        return

    # 按修改時間排序
    dirs_with_time = []
    for d in dirs:
        d_path = os.path.join(base_dir, d)
        mtime = os.path.getmtime(d_path)
        dirs_with_time.append((d, mtime))

    dirs_with_time.sort(key=lambda x: x[1], reverse=True)

    for d, mtime in dirs_with_time:
        # 解析 ASIN 和站點
        parts = d.split('_')
        if len(parts) >= 2:
            asin = parts[0]
            site = parts[1]
            # 檢查分類檔案
            d_path = os.path.join(base_dir, d)
            has_categorized = os.path.exists(os.path.join(d_path, 'categorized_result.json'))
            status = "✓ LLM分類" if has_categorized else "○ 規則分類"
            mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            print(f"  {d:40s} | {status:10s} | {mtime_str}")

    print(f"\n使用方法:")
    print(f"  python regenerate_reports.py --asin <ASIN> --site <SITE>")
    print(f"  cd {base_dir}\\<目錄名> && python ..\\..\\..\\.claude\\skills\\keyword-research\\scripts\\regenerate_reports.py")


def parse_output_dir(output_dir):
    """從輸出目錄路徑解析 ASIN 和站點"""
    basename = os.path.basename(output_dir)
    # 格式: ASIN_SITE_YYYYMMDD
    parts = basename.split('_')
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


def find_output_dir_from_cwd():
    """從當前工作目錄查詢輸出目錄"""
    cwd = os.path.abspath(os.getcwd())

    # 檢查當前目錄是否有 keywords_raw.json
    if os.path.exists(os.path.join(cwd, 'keywords_raw.json')):
        return cwd

    # 檢查是否在 keyword-reports 目錄下
    if 'keyword-reports' in cwd:
        # 可能在某個報告目錄的子目錄中
        parts = cwd.split('keyword-reports')
        if len(parts) > 1:
            base_path = parts[0] + 'keyword-reports'
            remainder = parts[1].lstrip(os.sep)
            # 嘗試找到包含 keywords_raw.json 的目錄
            current = remainder
            while current:
                test_path = os.path.join(base_path, current)
                if os.path.exists(os.path.join(test_path, 'keywords_raw.json')):
                    return test_path
                # 向上移動
                parts = current.split(os.sep)
                parts.pop()
                current = os.sep.join(parts) if parts else ''
                if not current or current == remainder:
                    break

    return None


def main():
    parser = argparse.ArgumentParser(
        description='重新生成關鍵詞報告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python regenerate_reports.py --list                          # 列出所有報告
  python regenerate_reports.py --asin B0FG6QG8C8 --site US    # 指定 ASIN
  python regenerate_reports.py --dir "path\\to\\report"       # 指定目錄
  cd report_dir && python regenerate_reports.py               # 從報告目錄執行
        """
    )
    parser.add_argument('--asin', help='ASIN')
    parser.add_argument('--site', default='US', help='Amazon 站點 (預設: US)')
    parser.add_argument('--dir', help='輸出目錄路徑')
    parser.add_argument('--list', action='store_true', help='列出所有可用的報告目錄')
    parser.add_argument('--base-dir', help='報告根目錄 (用於 --list)')

    args = parser.parse_args()

    # 列出所有報告
    if args.list:
        list_available_reports(args.base_dir)
        return 0

    # 確定輸出目錄
    output_dir = None
    asin = None
    site = args.site

    if args.dir:
        # 直接指定目錄
        output_dir = args.dir
        asin, site = parse_output_dir(output_dir)
        if not asin:
            print(f"❌ 無法從目錄名解析 ASIN: {output_dir}")
            return 1
    elif args.asin:
        # 指定 ASIN
        asin = args.asin
        site = args.site
        # 查詢匹配的目錄
        base_dir = os.path.join(os.path.dirname(SCRIPT_DIR), '..', '..', '..', 'keyword-reports')
        base_dir = os.path.abspath(base_dir)
        for item in os.listdir(base_dir):
            if item.startswith(f"{asin}_{site}"):
                output_dir = os.path.join(base_dir, item)
                break
        if not output_dir:
            print(f"❌ 未找到 ASIN {asin} ({site}) 的報告目錄")
            print(f"   搜尋路徑: {base_dir}")
            print(f"   使用 --list 檢視所有可用報告")
            return 1
    else:
        # 嘗試從當前目錄檢測
        output_dir = find_output_dir_from_cwd()
        if not output_dir:
            print("❌ 無法確定輸出目錄")
            print("\n請使用以下方式之一:")
            print("  1. 從報告目錄內執行此指令碼")
            print("  2. 使用 --asis <ASIN> --site <SITE> 指定")
            print("  3. 使用 --dir <路徑> 指定完整目錄")
            print("  4. 使用 --list 檢視所有可用報告")
            return 1
        asin, site = parse_output_dir(output_dir)
        if not asin:
            print(f"❌ 無法從目錄名解析 ASIN: {output_dir}")
            return 1
        print(f"📂 自動檢測到輸出目錄: {output_dir}")

    # 驗證目錄存在
    if not os.path.exists(output_dir):
        print(f"❌ 輸出目錄不存在: {output_dir}")
        return 1

    # 驗證必要檔案存在
    keywords_file = os.path.join(output_dir, 'keywords_raw.json')
    if not os.path.exists(keywords_file):
        print(f"❌ 關鍵詞檔案不存在: {keywords_file}")
        return 1

    # 建立工作流
    workflow = KeywordResearchWorkflow(asin, site, None, 0)
    workflow.output_dir = output_dir

    # 載入關鍵詞
    with open(os.path.join(workflow.output_dir, 'keywords_raw.json'), 'r', encoding='utf-8') as f:
        workflow.all_keywords = json.load(f)

    # 載入產品資訊
    product_info_file = os.path.join(workflow.output_dir, 'product_info.json')
    if os.path.exists(product_info_file):
        with open(product_info_file, 'r', encoding='utf-8') as f:
            workflow.product_info = json.load(f)

    print(f"\n{'='*60}")
    print(f"重新生成報告: {asin} ({site})")
    print(f"{'='*60}")
    print(f"輸出目錄: {workflow.output_dir}")
    print(f"已載入 {len(workflow.all_keywords)} 個關鍵詞")

    # 載入分類結果
    workflow.categorized_keywords = workflow._load_categorized_result()

    if workflow.categorized_keywords:
        total = sum(len(v) for v in workflow.categorized_keywords.values())
        print(f"✓ 成功載入分類結果：{total} 個關鍵詞")
        for cat, kws in workflow.categorized_keywords.items():
            print(f"  - {cat}: {len(kws)} 個")
    else:
        print("✗ 未找到分類結果，使用規則分類")
        workflow.categorized_keywords = workflow._smart_classify()

    # 生成 CSV
    print("\n生成 CSV 檔案...")
    csv_files = generate_csv_files(
        workflow.all_keywords,
        workflow.categorized_keywords,
        workflow.output_dir
    )
    print(f"✓ 生成 {len(csv_files)} 個 CSV 檔案")

    # 生成 Markdown 報告
    print("\n生成 Markdown 報告...")
    report_file = generate_markdown_report(
        workflow.asin,
        workflow.site,
        workflow.all_keywords,
        workflow.categorized_keywords,
        workflow.output_dir,
        workflow.product_info
    )
    print(f"✓ 報告已生成：{report_file}")

    # 生成 HTML 儀表板
    print("\n生成 HTML 儀表板...")
    dashboard_file = generate_html_dashboard(
        workflow.asin,
        workflow.site,
        workflow.all_keywords,
        workflow.categorized_keywords,
        workflow.output_dir,
        workflow.product_info
    )
    print(f"✓ 儀表板已生成：{dashboard_file}")

    print("\n" + "="*60)
    print("✓ 所有報告生成完成!")
    print("="*60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
