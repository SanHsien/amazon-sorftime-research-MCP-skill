#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
西柚洞察報告生成器

將MCP獲取的資料聚合為Markdown報告

使用方式:
    from scripts.report_generator import ReportGenerator
    generator = ReportGenerator()
    report = generator.generate(data, scenario, asin, site)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


class ReportGenerator:
    """報告生成器"""

    def generate(self, data: Dict[str, Any], scenario: str, 
                 target: str, site: str, output_dir: str = None) -> str:
        """
        生成報告

        Args:
            data: 結構化資料
            scenario: 場景名稱
            target: ASIN或關鍵詞
            site: 站點
            output_dir: 輸出目錄

        Returns:
            str: 報告內容
        """
        report_content = self._build_report(data, scenario, target, site)

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            report_file = os.path.join(output_dir, 'report.md')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return report_file

        return report_content

    def _build_report(self, data: Dict[str, Any], scenario: str, 
                      target: str, site: str) -> str:
        """構建報告內容"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        scenario_titles = {
            '廣告監控': '實時監控廣告投放效果分析報告',
            '流量缺口': '高價效比流量缺口分析報告',
            '競品拆解': '對標競對打法拆解報告',
            '新品推廣': '新品推廣效率分析報告',
            '流量廣告策略': '競品流量及廣告策略深度分析報告',
            '廣告預算': '競品廣告策略和預算分析報告',
            '關鍵詞庫': '關鍵詞庫搭建報告'
        }

        title = scenario_titles.get(scenario, f'{scenario}分析報告')

        content = f"""# {title}

## 分析概覽

| 專案 | 詳情 |
|------|------|
| 分析場景 | {scenario} |
| 分析物件 | {target} |
| 目標站點 | {site} |
| 生成時間 | {timestamp} |

"""

        if scenario == '流量廣告策略' or scenario == '競品拆解':
            content += self._build_competitor_analysis(data)
        elif scenario == '廣告監控':
            content += self._build_ad_monitoring(data)
        elif scenario == '流量缺口':
            content += self._build_traffic_gap(data)
        elif scenario == '新品推廣':
            content += self._build_new_product(data)
        elif scenario == '廣告預算':
            content += self._build_ad_budget(data)
        elif scenario == '關鍵詞庫':
            content += self._build_keyword_database(data)
        else:
            content += self._build_general_analysis(data)

        return content

    def _build_competitor_analysis(self, data: Dict[str, Any]) -> str:
        """構建競品分析報告"""
        content = ""

        if data.get('asin_info'):
            content += "## 競品基礎資訊\n\n"
            for asin, info in data['asin_info'].items():
                content += f"### {asin}\n\n"
                content += f"- **標題**: {info.get('title', '-')}\n"
                content += f"- **價格**: {info.get('price', '-')} {info.get('currency', '')}\n"
                content += f"- **評分**: {info.get('stars', '-')} ({info.get('ratings', '-')}條評論)\n"
                content += f"- **連結**: [Amazon]({info.get('url', '#')})\n\n"

        if data.get('variations'):
            content += "## 變體關係分析\n\n"
            for asin, var in data['variations'].items():
                content += f"### {asin} 變體結構\n\n"
                content += f"- **父體**: {var.get('parent_asin', '-')}\n"
                content += f"- **子體數量**: {len(var.get('children', []))}\n"
                content += "- **子體列表**: " + ", ".join(var.get('children', [])) + "\n\n"

        if data.get('traffic'):
            content += "## 流量分析\n\n"
            content += "### 流量得分對比\n\n"
            content += "| ASIN | 自然流量 | 廣告流量 | 總流量 | 關鍵詞數量 |\n"
            content += "|------|----------|----------|--------|------------|\n"
            for asin, traffic in data['traffic'].items():
                content += f"| {asin} | {traffic.get('natural_traffic', '-')} | {traffic.get('ad_traffic', '-')} | {traffic.get('total_traffic', '-')} | {traffic.get('keyword_count', '-')} |\n"
            content += "\n"

        if data.get('keywords'):
            content += "## 關鍵詞佈局分析\n\n"
            for asin, keywords in data['keywords'].items():
                content += f"### {asin} 關鍵詞分佈\n\n"
                if keywords:
                    content += "| 關鍵詞 | 自然排名 | 廣告排名 | 流量 | 流量佔比 |\n"
                    content += "|--------|----------|----------|------|----------|\n"
                    for kw in keywords[:10]:
                        content += f"| {kw.get('keyword', '-')} | {kw.get('natural_rank', '-')} | {kw.get('ad_rank', '-')} | {kw.get('traffic', '-')} | {kw.get('traffic_share', '-')} |\n"
                    content += f"\n*顯示前10個關鍵詞，共{len(keywords)}個*\n\n"

        if data.get('ad_trends'):
            content += "## 廣告策略分析\n\n"
            for asin, trends in data['ad_trends'].items():
                content += f"### {asin} 廣告活動變化\n\n"
                if trends.get('daily_changes'):
                    content += "| 日期 | 新增活動 | 移除活動 |\n"
                    content += "|------|----------|----------|\n"
                    for day in trends['daily_changes'][-7:]:
                        content += f"| {day.get('date', '-')} | {day.get('added', 0)} | {day.get('removed', 0)} |\n"
                    content += "\n"

        if data.get('insights'):
            content += "## 關鍵洞察\n\n"
            for insight in data['insights']:
                content += f"- {insight}\n"
            content += "\n"

        return content

    def _build_ad_monitoring(self, data: Dict[str, Any]) -> str:
        """構建廣告監控報告"""
        content = ""

        if data.get('hourly_rank'):
            content += "## 小時級排名監控\n\n"
            content += f"### {data.get('keyword', '')} 小時級排名變化\n\n"
            content += "| 時間 | 自然排名 | 廣告排名 |\n"
            content += "|------|----------|----------|\n"
            for hour in data['hourly_rank']:
                content += f"| {hour.get('hour', '-')}:00 | {hour.get('natural_rank', '-')} | {hour.get('ad_rank', '-')} |\n"
            content += "\n"

        if data.get('rank_trends'):
            content += "## 日排名趨勢\n\n"
            content += "| 日期 | 自然排名 | 廣告排名 |\n"
            content += "|------|----------|----------|\n"
            for day in data['rank_trends'][-14:]:
                content += f"| {day.get('date', '-')} | {day.get('natural_rank', '-')} | {day.get('ad_rank', '-')} |\n"
            content += "\n"

        if data.get('ad_changes'):
            content += "## 廣告活動變化\n\n"
            content += "| 日期 | 新增活動 | 移除活動 |\n"
            content += "|------|----------|----------|\n"
            for day in data['ad_changes'][-7:]:
                content += f"| {day.get('date', '-')} | {day.get('added', 0)} | {day.get('removed', 0)} |\n"
            content += "\n"

        if data.get('effect_evaluation'):
            content += "## 廣告效果評估\n\n"
            eval_data = data['effect_evaluation']
            content += f"- **評估結果**: {eval_data.get('result', '-')}\n"
            content += f"- **自然排名變化**: {eval_data.get('natural_rank_change', '-')}\n"
            content += f"- **廣告排名變化**: {eval_data.get('ad_rank_change', '-')}\n"
            content += f"- **評估理由**: {eval_data.get('reason', '-')}\n\n"

        return content

    def _build_traffic_gap(self, data: Dict[str, Any]) -> str:
        """構建流量缺口分析報告"""
        content = ""

        if data.get('keyword_comparison'):
            content += "## 關鍵詞覆蓋對比\n\n"
            content += "| 關鍵詞 | 自身排名 | 競品A排名 | 競品B排名 | 搜尋量 | 競爭難度 |\n"
            content += "|--------|----------|-----------|-----------|--------|----------|\n"
            for kw in data['keyword_comparison'][:20]:
                content += f"| {kw.get('keyword', '-')} | {kw.get('own_rank', '-')} | {kw.get('competitor_a_rank', '-')} | {kw.get('competitor_b_rank', '-')} | {kw.get('search_volume', '-')} | {kw.get('competitive_difficulty', '-')} |\n"
            content += "\n"

        if data.get('traffic_gaps'):
            content += "## 流量缺口分析\n\n"
            content += f"共發現 **{len(data['traffic_gaps'])}** 個流量缺口關鍵詞\n\n"
            content += "| 優先順序 | 關鍵詞 | 競品排名 | 自身排名 | 搜尋量 | 競爭難度 | 建議競價 |\n"
            content += "|--------|--------|----------|----------|--------|----------|----------|\n"
            for gap in data['traffic_gaps'][:15]:
                priority = '🔴高' if gap.get('priority') == 'high' else '🟡中' if gap.get('priority') == 'medium' else '🟢低'
                content += f"| {priority} | {gap.get('keyword', '-')} | {gap.get('competitor_rank', '-')} | {gap.get('own_rank', '-')} | {gap.get('search_volume', '-')} | {gap.get('competitive_difficulty', '-')} | ${gap.get('cpc', '-')} |\n"
            content += "\n"

        if data.get('recommendations'):
            content += "## 最佳化建議\n\n"
            for rec in data['recommendations']:
                content += f"- {rec}\n"
            content += "\n"

        return content

    def _build_new_product(self, data: Dict[str, Any]) -> str:
        """構建新品推廣分析報告"""
        content = ""

        if data.get('traffic_stage'):
            content += "## 流量分配階段判斷\n\n"
            stage = data['traffic_stage']
            stage_name = {'sparse': '稀疏期', 'oscillating': '震盪期', 'stable': '穩定期'}.get(stage.get('stage', ''), '未知')
            content += f"### 當前階段: **{stage_name}**\n\n"
            content += f"- **判斷依據**: {stage.get('reason', '-')}\n"
            content += f"- **流量得分**: {stage.get('traffic_score', '-')}\n"
            content += f"- **關鍵詞數量**: {stage.get('keyword_count', '-')}\n\n"

        if data.get('traffic_trends'):
            content += "## 流量趨勢\n\n"
            content += "| 日期 | 自然流量 | 廣告流量 | 總流量 |\n"
            content += "|------|----------|----------|--------|\n"
            traffic_trends = data['traffic_trends']
            if isinstance(traffic_trends, dict):
                for asin, trends in traffic_trends.items():
                    for day in trends[-14:] if isinstance(trends, list) else []:
                        content += f"| {day.get('date', '-')} | {day.get('natural_traffic', '-')} | {day.get('ad_traffic', '-')} | {day.get('total_traffic', '-')} |\n"
            elif isinstance(traffic_trends, list):
                for day in traffic_trends[-14:]:
                    content += f"| {day.get('date', '-')} | {day.get('natural_traffic', '-')} | {day.get('ad_traffic', '-')} | {day.get('total_traffic', '-')} |\n"
            content += "\n"

        if data.get('異動關鍵詞'):
            content += "## 異動關鍵詞分析\n\n"
            
            if data['異動關鍵詞'].get('新增'):
                content += "### 📈 新增關鍵詞\n\n"
                content += "| 關鍵詞 | 自然排名 | 搜尋量 |\n"
                content += "|--------|----------|--------|\n"
                for kw in data['異動關鍵詞']['新增'][:10]:
                    content += f"| {kw.get('keyword', '-')} | {kw.get('natural_rank', '-')} | {kw.get('search_volume', '-')} |\n"
                content += "\n"

            if data['異動關鍵詞'].get('流失'):
                content += "### 📉 流失關鍵詞\n\n"
                content += "| 關鍵詞 | 搜尋量 |\n"
                content += "|--------|--------|\n"
                for kw in data['異動關鍵詞']['流失'][:10]:
                    content += f"| {kw.get('keyword', '-')} | {kw.get('search_volume', '-')} |\n"
                content += "\n"

            if data['異動關鍵詞'].get('流量升檔'):
                content += "### 🚀 流量升檔\n\n"
                content += "| 關鍵詞 | 檔位變化 | 搜尋量 |\n"
                content += "|--------|----------|--------|\n"
                for kw in data['異動關鍵詞']['流量升檔'][:10]:
                    content += f"| {kw.get('keyword', '-')} | {kw.get('change', '-')} | {kw.get('search_volume', '-')} |\n"
                content += "\n"

        if data.get('recommendations'):
            content += "## 最佳化建議\n\n"
            for rec in data['recommendations']:
                content += f"- {rec}\n"
            content += "\n"

        return content

    def _build_ad_budget(self, data: Dict[str, Any]) -> str:
        """構建廣告預算分析報告"""
        content = ""

        if data.get('ad_type_share'):
            content += "## 廣告型別分佈\n\n"
            content += "| 廣告型別 | 流量佔比 |\n"
            content += "|----------|----------|\n"
            for ad_type, share in data['ad_type_share'].items():
                content += f"| {ad_type} | {share}% |\n"
            content += "\n"

        if data.get('ad_activities'):
            content += "## 廣告活動分析\n\n"
            content += "| 活動ID | 流量貢獻 | 展示時長趨勢 |\n"
            content += "|--------|----------|--------------|\n"
            for activity in data['ad_activities'][:10]:
                content += f"| {activity.get('id', '-')} | {activity.get('traffic_share', '-')} | {activity.get('duration_trend', '-')} |\n"
            content += "\n"

        if data.get('core_keywords'):
            content += "## 核心廣告關鍵詞\n\n"
            content += "| 關鍵詞 | 流量佔比 | 搜尋量 | 建議競價 |\n"
            content += "|--------|----------|--------|----------|\n"
            for kw in data['core_keywords'][:15]:
                content += f"| {kw.get('keyword', '-')} | {kw.get('traffic_share', '-')} | {kw.get('search_volume', '-')} | ${kw.get('cpc', '-')} |\n"
            content += "\n"

        if data.get('budget_inference'):
            content += "## 預算推斷\n\n"
            budget = data['budget_inference']
            content += f"- **預算趨勢**: {budget.get('trend', '-')}\n"
            content += f"- **主要投放時段**: {budget.get('peak_hours', '-')}\n"
            content += f"- **預算調整節點**: {budget.get('adjustment_dates', '-')}\n"
            content += f"- **預估月預算**: ${budget.get('estimated_monthly', '-')}\n\n"

        return content

    def _build_keyword_database(self, data: Dict[str, Any]) -> str:
        """構建關鍵詞庫報告"""
        content = ""

        if data.get('keyword_stats'):
            stats = data['keyword_stats']
            content += "## 關鍵詞統計\n\n"
            content += f"- **總關鍵詞數**: {stats.get('total', 0)}\n"
            content += f"- **強相關**: {stats.get('strong', 0)} ({round(stats.get('strong', 0)/stats.get('total', 1)*100, 1)}%)\n"
            content += f"- **高相關**: {stats.get('high', 0)} ({round(stats.get('high', 0)/stats.get('total', 1)*100, 1)}%)\n"
            content += f"- **中相關**: {stats.get('medium', 0)} ({round(stats.get('medium', 0)/stats.get('total', 1)*100, 1)}%)\n"
            content += f"- **低相關**: {stats.get('low', 0)} ({round(stats.get('low', 0)/stats.get('total', 1)*100, 1)}%)\n\n"

        if data.get('categorized_keywords'):
            content += "## 關鍵詞分類\n\n"
            for category, keywords in data['categorized_keywords'].items():
                content += f"### {category} ({len(keywords)}個)\n\n"
                content += "| 關鍵詞 | 搜尋量 | 競爭難度 | 建議競價 |\n"
                content += "|--------|--------|----------|----------|\n"
                for kw in keywords[:10]:
                    content += f"| {kw.get('keyword', '-')} | {kw.get('search_volume', '-')} | {kw.get('competitive_difficulty', '-')} | ${kw.get('cpc', '-')} |\n"
                if len(keywords) > 10:
                    content += f"\n*顯示前10個，共{len(keywords)}個*\n"
                content += "\n"

        if data.get('negative_keywords'):
            content += "## 否定詞庫\n\n"
            content += f"共 **{len(data['negative_keywords'])}** 個否定關鍵詞\n\n"
            content += "| 關鍵詞 | 相關性 | 原因 |\n"
            content += "|--------|--------|------|\n"
            for kw in data['negative_keywords'][:20]:
                content += f"| {kw.get('keyword', '-')} | {kw.get('relevance', '-')} | {kw.get('reason', '-')} |\n"
            content += "\n"

        return content

    def _build_general_analysis(self, data: Dict[str, Any]) -> str:
        """構建通用分析報告"""
        content = ""

        if data.get('summary'):
            content += "## 分析摘要\n\n"
            content += data['summary'] + "\n\n"

        if data.get('details'):
            content += "## 詳細資料\n\n"
            for key, value in data['details'].items():
                content += f"### {key}\n\n"
                if isinstance(value, list):
                    for item in value[:20]:
                        if isinstance(item, dict):
                            content += "- " + ", ".join(f"{k}: {v}" for k, v in item.items()) + "\n"
                        else:
                            content += f"- {item}\n"
                    if len(value) > 20:
                        content += f"\n*顯示前20條，共{len(value)}條*\n"
                elif isinstance(value, dict):
                    content += "| 欄位 | 值 |\n"
                    content += "|------|------|\n"
                    for k, v in value.items():
                        content += f"| {k} | {v} |\n"
                else:
                    content += f"{value}\n"
                content += "\n"

        return content


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <data_json_path>")
        sys.exit(1)

    data_path = sys.argv[1]
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    scenario = data.get('scenario', '通用分析')
    target = data.get('target', '')
    site = data.get('site', '')

    generator = ReportGenerator()
    output_dir = os.path.dirname(data_path)
    report_file = generator.generate(data, scenario, target, site, output_dir)

    print(f"✅ 報告已生成: {report_file}")
