from .base import BaseScenario
from typing import Dict, List, Any


class CompetitorAnalysisScenario(BaseScenario):
    """競品流量及廣告策略深度分析"""

    NAME = "competitor_analysis"
    DESCRIPTION = "精準拆解競品流量以及廣告策略"
    REQUIRED_PARAMS = ['asin', 'site']

    def get_mcp_tools(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        asin = params['asin']
        site = params['site']
        end_date = params.get('end_date', self.default_end_date)
        start_date = params.get('start_date', self.default_start_date)
        end_month = params.get('end_month', self.default_end_month)
        start_month = params.get('start_month', self.default_start_month)

        tools = [
            {
                'tool_name': 'get_asin_info',
                'arguments': {
                    'asins': [asin],
                    'country': site,
                    'intent_summary': f'競品分析：獲取{asin}基礎資訊'
                }
            },
            {
                'tool_name': 'get_asin_variations',
                'arguments': {
                    'asin': asin,
                    'country': site,
                    'intent_summary': f'競品分析：獲取{asin}變體關係'
                }
            },
            {
                'tool_name': 'get_asin_keywords',
                'arguments': {
                    'asin': asin,
                    'country': site,
                    'page': 1,
                    'page_size': 50,
                    'sort_field': 'traffic',
                    'sort_order': 'desc',
                    'intent_summary': f'競品分析：獲取{asin}關鍵詞列表'
                }
            },
            {
                'tool_name': 'get_asin_traffic',
                'arguments': {
                    'asins': [asin],
                    'country': site,
                    'intent_summary': f'競品分析：獲取{asin}流量得分'
                }
            },
            {
                'tool_name': 'get_asin_traffic_trends',
                'arguments': {
                    'asin': asin,
                    'country': site,
                    'start_date': start_date,
                    'end_date': end_date,
                    'intent_summary': f'競品分析：獲取{asin}流量趨勢'
                }
            },
            {
                'tool_name': 'get_asin_ad_change_trends',
                'arguments': {
                    'asin': asin,
                    'country': site,
                    'start_date': start_date,
                    'end_date': end_date,
                    'intent_summary': f'競品分析：獲取{asin}廣告活動變化'
                }
            }
        ]

        keywords = params.get('keywords', [])
        if keywords:
            tools.append({
                'tool_name': 'get_keyword_info',
                'arguments': {
                    'keywords': keywords[:10],
                    'country': site,
                    'intent_summary': f'競品分析：獲取關鍵詞資訊'
                }
            })

            for keyword in keywords[:3]:
                tools.append({
                    'tool_name': 'get_keyword_asin_analysis',
                    'arguments': {
                        'keyword': keyword,
                        'country': site,
                        'page': 1,
                        'page_size': 20,
                        'intent_summary': f'競品分析：分析關鍵詞{keyword}競爭格局'
                    }
                })

        return tools

    def aggregate_data(self, raw_data: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        asin = params['asin']
        site = params['site']

        data = {
            'title': f'競品分析 - {asin}',
            'target': asin,
            'site': site,
            'scenario': '流量廣告策略'
        }

        if raw_data.get('get_asin_info'):
            data['asin_info'] = self._process_asin_info(raw_data['get_asin_info'])

        if raw_data.get('get_asin_variations'):
            data['variations'] = self._process_variations(raw_data['get_asin_variations'], asin)

        if raw_data.get('get_asin_keywords'):
            data['keywords'] = self._process_keywords(raw_data['get_asin_keywords'], asin)

        if raw_data.get('get_asin_traffic'):
            data['traffic'] = self._process_traffic(raw_data['get_asin_traffic'])
            data['overview'] = self._build_overview(data['traffic'])

        if raw_data.get('get_asin_traffic_trends'):
            data['traffic_trends'] = self._process_traffic_trends(raw_data['get_asin_traffic_trends'], asin)

        if raw_data.get('get_asin_ad_change_trends'):
            data['ad_trends'] = self._process_ad_trends(raw_data['get_asin_ad_change_trends'], asin)

        if raw_data.get('get_keyword_info'):
            data['keyword_info'] = self._process_keyword_info(raw_data['get_keyword_info'])

        if raw_data.get('get_keyword_asin_analysis'):
            data['keyword_competition'] = self._process_keyword_competition(raw_data['get_keyword_asin_analysis'])

        return data

    def generate_insights(self, data: Dict[str, Any]) -> List[str]:
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

    def _process_asin_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        items = result.get('data', result.get('result', result))
        if isinstance(items, dict):
            items = [items]

        result_dict = {}
        for item in items:
            asin = item.get('asin', item.get('ASIN', 'unknown'))
            result_dict[asin] = {
                'title': item.get('title', item.get('Title', '')),
                'price': item.get('price', item.get('Price', '')),
                'currency': item.get('currency', item.get('Currency', '')),
                'stars': item.get('stars', item.get('Stars', '')),
                'ratings': item.get('ratings', item.get('Ratings', '')),
                'url': item.get('url', item.get('Url', '')),
                'image': item.get('image', item.get('Image', ''))
            }
        return result_dict

    def _process_variations(self, result: Dict[str, Any], asin: str) -> Dict[str, Any]:
        data = result.get('data', result.get('result', result))
        return {
            asin: {
                'parent_asin': data.get('parent_asin', data.get('parentASIN', '')),
                'children': data.get('children', data.get('childASINs', [])),
                'variation_data': {}
            }
        }

    def _process_keywords(self, result: Dict[str, Any], asin: str) -> Dict[str, List[Dict[str, Any]]]:
        items = result.get('data', result.get('result', result))
        if isinstance(items, dict):
            items = items.get('keywords', items.get('data', []))

        keywords = []
        for kw in items:
            keywords.append({
                'keyword': kw.get('keyword', kw.get('Keyword', '')),
                'natural_rank': kw.get('natural_rank', kw.get('naturalRank', kw.get('natural_rank', ''))),
                'ad_rank': kw.get('ad_rank', kw.get('adRank', kw.get('ad_rank', ''))),
                'traffic': kw.get('traffic', kw.get('Traffic', '')),
                'traffic_share': kw.get('traffic_share', kw.get('trafficShare', '')),
                'traffic_growth': kw.get('traffic_growth', kw.get('trafficGrowth', '')),
                'search_volume': kw.get('search_volume', kw.get('searchVolume', '')),
                'competitive_difficulty': kw.get('competitive_difficulty', kw.get('competitiveDifficulty', '')),
                'cpc': kw.get('cpc', kw.get('costPerClick', ''))
            })

        return {asin: keywords}

    def _process_traffic(self, result: Dict[str, Any]) -> Dict[str, Any]:
        items = result.get('data', result.get('result', result))
        if isinstance(items, dict):
            items = [items]

        result_dict = {}
        for item in items:
            asin = item.get('asin', item.get('ASIN', 'unknown'))
            result_dict[asin] = {
                'natural_traffic': item.get('natural_traffic', item.get('naturalTraffic', 0)),
                'ad_traffic': item.get('ad_traffic', item.get('adTraffic', 0)),
                'total_traffic': item.get('total_traffic', item.get('totalTraffic', 0)),
                'keyword_count': item.get('keyword_count', item.get('keywordCount', 0)),
                'natural_traffic_share': item.get('natural_traffic_share', item.get('naturalTrafficShare', 0)),
                'ad_traffic_share': item.get('ad_traffic_share', item.get('adTrafficShare', 0)),
                'traffic_growth': item.get('traffic_growth', item.get('trafficGrowth', 0))
            }
        return result_dict

    def _process_traffic_trends(self, result: Dict[str, Any], asin: str) -> Dict[str, List[Dict[str, Any]]]:
        items = result.get('data', result.get('result', result))
        if isinstance(items, dict):
            items = items.get('trends', items.get('data', []))

        trends = []
        for day in items:
            trends.append({
                'date': day.get('date', day.get('Date', '')),
                'natural_traffic': day.get('natural_traffic', day.get('naturalTraffic', 0)),
                'ad_traffic': day.get('ad_traffic', day.get('adTraffic', 0)),
                'total_traffic': day.get('total_traffic', day.get('totalTraffic', 0))
            })

        return {asin: trends}

    def _process_ad_trends(self, result: Dict[str, Any], asin: str) -> Dict[str, Any]:
        data = result.get('data', result.get('result', result))
        daily_changes = data.get('daily_changes', data.get('dailyChanges', []))
        summary = data.get('summary', {})

        processed_changes = []
        for day in daily_changes:
            processed_changes.append({
                'date': day.get('date', day.get('Date', '')),
                'added': day.get('added', day.get('addedCount', 0)),
                'removed': day.get('removed', day.get('removedCount', 0))
            })

        return {
            asin: {
                'daily_changes': processed_changes[-7:] if len(processed_changes) > 7 else processed_changes,
                'summary': {
                    'total_added': summary.get('total_added', 0),
                    'total_removed': summary.get('total_removed', 0),
                    'net_change': summary.get('net_change', summary.get('total_added', 0) - summary.get('total_removed', 0))
                }
            }
        }

    def _process_keyword_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        items = result.get('data', result.get('result', result))
        if isinstance(items, dict):
            items = [items]

        result_dict = {}
        for item in items:
            keyword = item.get('keyword', item.get('Keyword', 'unknown'))
            result_dict[keyword] = {
                'keyword': keyword,
                'weekly_search_volume': item.get('weekly_search_volume', item.get('weeklySearchVolume', 0)),
                'search_frequency_rank': item.get('search_frequency_rank', item.get('searchFrequencyRank', 0)),
                'competitive_difficulty': item.get('competitive_difficulty', item.get('competitiveDifficulty', 0)),
                'cpc': item.get('cost_per_click', item.get('cpc', item.get('costPerClick', 0))),
                'click_conversion_rate': item.get('click_conversion_rate', item.get('clickConversionRate', 0)),
                'natural_scroll_rate': item.get('natural_scroll_rate', item.get('naturalScrollRate', 0))
            }
        return result_dict

    def _process_keyword_competition(self, results: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        result_dict = {}
        for result in results:
            keyword = result.get('keyword', result.get('Keyword', 'unknown'))
            items = result.get('data', result.get('result', result))
            if isinstance(items, dict):
                items = items.get('asins', items.get('data', []))

            asins = []
            for item in items:
                asins.append({
                    'asin': item.get('asin', item.get('ASIN', '')),
                    'title': item.get('title', item.get('Title', '')),
                    'price': item.get('price', item.get('Price', '')),
                    'stars': item.get('stars', item.get('Stars', '')),
                    'natural_rank': item.get('natural_rank', item.get('naturalRank', '')),
                    'ad_rank': item.get('ad_rank', item.get('adRank', '')),
                    'traffic': item.get('traffic', item.get('Traffic', '')),
                    'traffic_share': item.get('traffic_share', item.get('trafficShare', ''))
                })

            result_dict[keyword] = asins

        return result_dict

    def _build_overview(self, traffic: Dict[str, Any]) -> Dict[str, Any]:
        overview = {}
        for asin, data in traffic.items():
            overview[f"{asin} - 自然流量"] = data['natural_traffic']
            overview[f"{asin} - 廣告流量"] = data['ad_traffic']
            overview[f"{asin} - 總流量"] = data['total_traffic']
            overview[f"{asin} - 關鍵詞數"] = data['keyword_count']
        return overview
