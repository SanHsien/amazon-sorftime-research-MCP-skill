#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
競品流量及廣告策略分析工作流

場景5: 精準拆解競品流量以及廣告策略

使用方式:
    python workflow_competitor_analysis.py <asin> <site> <output_dir>
    
示例:
    python workflow_competitor_analysis.py B07PQFT83F US ./reports
"""

import os
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_aggregator import DataAggregator
from scripts.report_generator import ReportGenerator
from scripts.dashboard_generator import DashboardGenerator


class CompetitorAnalysisWorkflow:
    """競品分析工作流"""

    def __init__(self):
        self.aggregator = DataAggregator()
        self.report_generator = ReportGenerator()
        self.dashboard_generator = DashboardGenerator()

    def run(self, asin: str, site: str = 'US', output_dir: str = None) -> Dict[str, Any]:
        """
        執行競品分析工作流

        Args:
            asin: 競品ASIN
            site: 站點
            output_dir: 輸出目錄

        Returns:
            dict: 分析結果
        """
        if not output_dir:
            date_str = datetime.now().strftime('%Y%m%d')
            output_dir = os.path.join('xiyou-insight-reports', f'competitor_analysis_{asin}_{site}_{date_str}')
        os.makedirs(output_dir, exist_ok=True)

        print(f"🚀 開始競品分析: {asin} ({site})")
        print(f"📁 輸出目錄: {output_dir}")

        raw_data = self._collect_data(asin, site)
        
        aggregated_data = self.aggregator.aggregate(raw_data, scenario='流量廣告策略')
        aggregated_data['target'] = asin
        aggregated_data['site'] = site
        aggregated_data['title'] = f'競品分析 - {asin}'

        insights = self._generate_insights(aggregated_data)
        aggregated_data['insights'] = insights

        data_file = os.path.join(output_dir, 'data.json')
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(aggregated_data, f, ensure_ascii=False, indent=2)

        self.aggregator.save_raw_data(raw_data, output_dir)

        report_file = self.report_generator.generate(
            aggregated_data, 
            scenario='流量廣告策略', 
            target=asin, 
            site=site,
            output_dir=output_dir
        )

        dashboard_file = os.path.join(output_dir, 'dashboard.html')
        self.dashboard_generator.render(aggregated_data, dashboard_file)

        print(f"\n✅ 分析完成!")
        print(f"   📊 資料檔案: {data_file}")
        print(f"   📝 報告檔案: {report_file}")
        print(f"   📈 Dashboard: {dashboard_file}")

        return aggregated_data

    def _collect_data(self, asin: str, site: str) -> Dict[str, Any]:
        """
        收集資料（模擬MCP呼叫）
        
        注意: 實際使用時，這些資料需要透過LLM呼叫MCP工具獲取
        這裡提供資料結構模板和示例資料
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        end_month = datetime.now().strftime('%Y-%m')
        start_month = (datetime.now() - timedelta(days=90)).strftime('%Y-%m')

        return {
            'asin_info': [
                {
                    'asin': asin,
                    'title': '示例產品標題 - Wireless Bluetooth Headphones with Noise Cancelling',
                    'price': '59.99',
                    'currency': 'USD',
                    'stars': 4.5,
                    'ratings': 12580,
                    'url': f'https://www.amazon.com/dp/{asin}',
                    'image': 'https://example.com/image.jpg'
                }
            ],
            'asin_variations': {
                asin: {
                    'parent_asin': asin,
                    'children': [asin],
                    'variation_data': {'type': 'single'}
                }
            },
            'asin_keywords': {
                asin: [
                    {'keyword': 'bluetooth headphones', 'natural_rank': 3, 'ad_rank': 2, 'traffic': 15000, 'traffic_share': '25%', 'traffic_growth': '+12%', 'search_volume': 500000, 'competitive_difficulty': 75, 'cpc': 2.5},
                    {'keyword': 'wireless headphones', 'natural_rank': 5, 'ad_rank': 3, 'traffic': 12000, 'traffic_share': '20%', 'traffic_growth': '+8%', 'search_volume': 450000, 'competitive_difficulty': 72, 'cpc': 2.3},
                    {'keyword': 'noise cancelling headphones', 'natural_rank': 8, 'ad_rank': 5, 'traffic': 8000, 'traffic_share': '13%', 'traffic_growth': '+15%', 'search_volume': 300000, 'competitive_difficulty': 78, 'cpc': 2.8},
                    {'keyword': 'bluetooth earbuds', 'natural_rank': 12, 'ad_rank': 8, 'traffic': 5000, 'traffic_share': '8%', 'traffic_growth': '-3%', 'search_volume': 280000, 'competitive_difficulty': 70, 'cpc': 2.1},
                    {'keyword': 'wireless earbuds', 'natural_rank': 15, 'ad_rank': 10, 'traffic': 4000, 'traffic_share': '7%', 'traffic_growth': '+5%', 'search_volume': 250000, 'competitive_difficulty': 68, 'cpc': 1.9}
                ]
            },
            'asin_traffic': [
                {
                    'asin': asin,
                    'natural_traffic': 85.5,
                    'ad_traffic': 42.3,
                    'total_traffic': 127.8,
                    'keyword_count': 156,
                    'natural_traffic_share': 66.9,
                    'ad_traffic_share': 33.1,
                    'traffic_growth': 12.5
                }
            ],
            'asin_traffic_trends': {
                asin: [
                    {'date': (datetime.now() - timedelta(days=13)).strftime('%Y-%m-%d'), 'natural_traffic': 70, 'ad_traffic': 35, 'total_traffic': 105},
                    {'date': (datetime.now() - timedelta(days=12)).strftime('%Y-%m-%d'), 'natural_traffic': 72, 'ad_traffic': 36, 'total_traffic': 108},
                    {'date': (datetime.now() - timedelta(days=11)).strftime('%Y-%m-%d'), 'natural_traffic': 75, 'ad_traffic': 38, 'total_traffic': 113},
                    {'date': (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d'), 'natural_traffic': 78, 'ad_traffic': 40, 'total_traffic': 118},
                    {'date': (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d'), 'natural_traffic': 80, 'ad_traffic': 39, 'total_traffic': 119},
                    {'date': (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d'), 'natural_traffic': 79, 'ad_traffic': 41, 'total_traffic': 120},
                    {'date': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'), 'natural_traffic': 81, 'ad_traffic': 40, 'total_traffic': 121},
                    {'date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'), 'natural_traffic': 82, 'ad_traffic': 41, 'total_traffic': 123},
                    {'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), 'natural_traffic': 83, 'ad_traffic': 42, 'total_traffic': 125},
                    {'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'), 'natural_traffic': 84, 'ad_traffic': 42, 'total_traffic': 126},
                    {'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'), 'natural_traffic': 85, 'ad_traffic': 42, 'total_traffic': 127},
                    {'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 'natural_traffic': 85, 'ad_traffic': 42, 'total_traffic': 127},
                    {'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), 'natural_traffic': 85, 'ad_traffic': 42, 'total_traffic': 127},
                    {'date': end_date, 'natural_traffic': 85.5, 'ad_traffic': 42.3, 'total_traffic': 127.8}
                ]
            },
            'asin_ad_change_trends': {
                asin: {
                    'daily_changes': [
                        {'date': (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d'), 'added': 2, 'removed': 1},
                        {'date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), 'added': 1, 'removed': 0},
                        {'date': (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'), 'added': 0, 'removed': 2},
                        {'date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'), 'added': 3, 'removed': 1},
                        {'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), 'added': 1, 'removed': 1},
                        {'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'), 'added': 2, 'removed': 0},
                        {'date': end_date, 'added': 0, 'removed': 1}
                    ],
                    'summary': {'total_added': 9, 'total_removed': 6, 'net_change': 3}
                }
            },
            'keyword_info': {
                'bluetooth headphones': {'keyword': 'bluetooth headphones', 'weekly_search_volume': 500000, 'search_frequency_rank': 50, 'competitive_difficulty': 75, 'cost_per_click': 2.5, 'click_conversion_rate': 8.5, 'natural_scroll_rate': 12},
                'wireless headphones': {'keyword': 'wireless headphones', 'weekly_search_volume': 450000, 'search_frequency_rank': 65, 'competitive_difficulty': 72, 'cost_per_click': 2.3, 'click_conversion_rate': 8.2, 'natural_scroll_rate': 10},
                'noise cancelling headphones': {'keyword': 'noise cancelling headphones', 'weekly_search_volume': 300000, 'search_frequency_rank': 120, 'competitive_difficulty': 78, 'cost_per_click': 2.8, 'click_conversion_rate': 9.0, 'natural_scroll_rate': 8}
            },
            'keyword_asin_analysis': {
                'bluetooth headphones': [
                    {'asin': 'B0XXXXXXXX1', 'title': 'Competitor A - Premium Bluetooth Headphones', 'price': '79.99', 'stars': 4.7, 'natural_rank': 1, 'ad_rank': 1, 'traffic': 25000, 'traffic_share': '40%'},
                    {'asin': 'B0XXXXXXXX2', 'title': 'Competitor B - Wireless Headphones Pro', 'price': '69.99', 'stars': 4.6, 'natural_rank': 2, 'ad_rank': 2, 'traffic': 18000, 'traffic_share': '28%'},
                    {'asin': asin, 'title': 'Target Product', 'price': '59.99', 'stars': 4.5, 'natural_rank': 3, 'ad_rank': 3, 'traffic': 15000, 'traffic_share': '24%'}
                ]
            }
        }

    def _generate_insights(self, data: Dict[str, Any]) -> List[str]:
        """
        生成關鍵洞察
        
        注意: 實際使用時，這些洞察由LLM生成
        這裡提供示例洞察
        """
        insights = []

        if data.get('traffic'):
            asin_traffic = list(data['traffic'].values())[0] if data['traffic'] else {}
            natural_share = asin_traffic.get('natural_traffic_share', 0)
            if natural_share > 60:
                insights.append(f"自然流量佔比達{natural_share}%，說明產品在自然搜尋方面表現優秀，品牌認知度較高")
            else:
                insights.append(f"自然流量佔比{natural_share}%，廣告流量依賴度較高，建議最佳化Listing提升自然排名")

        if data.get('keywords'):
            asin_keywords = list(data['keywords'].values())[0] if data['keywords'] else []
            if asin_keywords:
                top_keyword = asin_keywords[0]
                insights.append(f"核心關鍵詞 '{top_keyword['keyword']}' 貢獻了{top_keyword['traffic_share']}的流量，是主要流量來源")

        if data.get('ad_trends'):
            ad_trends = list(data['ad_trends'].values())[0] if data['ad_trends'] else {}
            summary = ad_trends.get('summary', {})
            if summary.get('net_change', 0) > 0:
                insights.append(f"近7天廣告活動淨增{summary['net_change']}個，競品正在加大廣告投放力度")
            elif summary.get('net_change', 0) < 0:
                insights.append(f"近7天廣告活動淨減{abs(summary['net_change'])}個，競品可能在調整廣告策略")

        if data.get('traffic_trends'):
            trends = list(data['traffic_trends'].values())[0] if data['traffic_trends'] else []
            if len(trends) >= 7:
                recent_avg = sum(t['total_traffic'] for t in trends[-7:]) / 7
                earlier_avg = sum(t['total_traffic'] for t in trends[:7]) / 7 if len(trends) >= 14 else recent_avg
                if recent_avg > earlier_avg * 1.1:
                    insights.append("近7天流量呈上升趨勢，競品可能在進行促銷活動或廣告加投")

        insights.append("建議重點關注競品的核心關鍵詞佈局，尋找流量缺口")
        insights.append("持續監控競品廣告活動變化，及時調整自身廣告策略")

        return insights


def main():
    if len(sys.argv) < 2:
        print("Usage: python workflow_competitor_analysis.py <asin> [site] [output_dir]")
        print("\n示例:")
        print("  python workflow_competitor_analysis.py B07PQFT83F")
        print("  python workflow_competitor_analysis.py B07PQFT83F US ./reports")
        sys.exit(1)

    asin = sys.argv[1]
    site = sys.argv[2] if len(sys.argv) > 2 else 'US'
    output_dir = sys.argv[3] if len(sys.argv) > 3 else None

    workflow = CompetitorAnalysisWorkflow()
    workflow.run(asin, site, output_dir)


if __name__ == "__main__":
    main()
