#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新生成 Markdown 和 HTML 報告，跳過 CSV
"""
import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from workflow import KeywordResearchWorkflow
from generate_markdown_report import generate_markdown_report
from generate_html_dashboard import generate_html_dashboard

# 建立工作流
workflow = KeywordResearchWorkflow('B09QSGWCLG', 'US', None, 0)
workflow.output_dir = r'D:\amazon-mcp\keyword-reports\B09QSGWCLG_US_20260314'

# 載入關鍵詞
with open(os.path.join(workflow.output_dir, 'keywords_raw.json'), 'r', encoding='utf-8') as f:
    workflow.all_keywords = json.load(f)

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

# 生成 Markdown 報告
print("\n生成 Markdown 報告...")
try:
    report_file = generate_markdown_report(
        workflow.asin,
        workflow.site,
        workflow.all_keywords,
        workflow.categorized_keywords,
        workflow.output_dir,
        workflow.product_info
    )
    print(f"✓ 報告已生成：{report_file}")
except Exception as e:
    print(f"✗ Markdown 報告生成失敗：{e}")

# 生成 HTML 儀表板
print("\n生成 HTML 儀表板...")
try:
    dashboard_file = generate_html_dashboard(
        workflow.asin,
        workflow.site,
        workflow.all_keywords,
        workflow.categorized_keywords,
        workflow.output_dir,
        workflow.product_info
    )
    print(f"✓ 儀表板已生成：{dashboard_file}")
except Exception as e:
    print(f"✗ HTML 儀表板生成失敗：{e}")

print("\n✓ 報告生成完成!")
