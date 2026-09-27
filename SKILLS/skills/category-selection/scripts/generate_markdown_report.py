#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品類選品 Markdown 分析報告生成器 v2.0 - 穩定增強版

生成完整的品類分析 Markdown 報告，包含:
- 五維評分分析
- 關鍵市場指標
- 品牌分析
- Top 產品列表
- 關鍵詞分析
- 選品建議

主要改進:
1. 支援直接從 data.json 讀取產品資料
2. 自動從產品列表計算統計資料
3. 更健壯的資料處理
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any


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


def safe_int(value, default=0):
    """安全地轉換為整數"""
    return int(safe_float(value, default))


class MarkdownReportGenerator:
    """Markdown 報告生成器"""

    def __init__(self, data_dir: str, category_name: str, site: str = 'US'):
        """
        初始化報告生成器

        Args:
            data_dir: 資料目錄路徑
            category_name: 品類名稱
            site: 站點程式碼
        """
        self.data_dir = data_dir
        self.category_name = category_name
        self.site = site.upper()
        self.raw_data = {}
        self.products = []
        self.scores = {}
        self.keywords = []

    def load_data(self):
        """載入所有資料檔案"""
        # 載入主資料檔案
        data_file = os.path.join(self.data_dir, 'data.json')
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)

            # 從 raw_data 中提取產品列表
            # 支援多種可能的鍵名
            for key in ['Top100產品', '產品列表', 'products', 'items']:
                if key in self.raw_data and isinstance(self.raw_data[key], list):
                    raw_products = self.raw_data[key]
                    # 標準化產品資料
                    self.products = self._normalize_products(raw_products)
                    break

            # 如果沒有找到產品列表，直接從 raw_data 處理
            if not self.products:
                # 檢查是否是產品列表格式
                if isinstance(self.raw_data, list):
                    self.products = self._normalize_products(self.raw_data)
                # 檢查是否是單個產品物件
                elif 'ASIN' in self.raw_data or 'asin' in self.raw_data:
                    self.products = self._normalize_products([self.raw_data])

        # 載入單獨的產品檔案（如果有）
        if not self.products:
            products_file = os.path.join(self.data_dir, 'top_products.json')
            if os.path.exists(products_file):
                with open(products_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)

        # 載入評分資料
        scores_file = os.path.join(self.data_dir, 'scores.json')
        if os.path.exists(scores_file):
            with open(scores_file, 'r', encoding='utf-8') as f:
                self.scores = json.load(f)

        # 載入關鍵詞資料
        keywords_file = os.path.join(self.data_dir, 'keywords.json')
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r', encoding='utf-8') as f:
                self.keywords = json.load(f)

    def _normalize_products(self, raw_products: list) -> list:
        """標準化產品資料格式"""
        normalized = []
        for p in raw_products:
            if not isinstance(p, dict):
                continue

            # 提取標準化的欄位
            product = {
                'ASIN': p.get('ASIN', ''),
                '標題': p.get('標題', p.get('title', ''))[:80],
                '價格': safe_float(p.get('價格', p.get('price', 0))),
                '月銷量': safe_int(p.get('月銷量', p.get('monthlySales', 0))),
                '月銷額': safe_float(p.get('月銷額', p.get('monthlyRevenue', 0))),
                '評分': safe_float(p.get('星級', p.get('評分', p.get('rating', 0)))),
                '品牌': p.get('品牌', p.get('brand', 'Unknown')),
                '評論數': safe_int(p.get('評論數', p.get('reviews', 0))),
                '賣家來源': p.get('賣家來源', p.get('sellerSource', '')),
                '賣家': p.get('賣家', p.get('seller', '')),
            }

            # 如果月銷額為0但有價格和銷量，計算月銷額
            if product['月銷額'] == 0 and product['價格'] > 0 and product['月銷量'] > 0:
                product['月銷額'] = product['價格'] * product['月銷量']

            # 如果月銷額為0但只有價格，估算
            if product['月銷額'] == 0 and product['價格'] > 0:
                # 使用平均銷量估算
                product['月銷額'] = product['價格'] * 100  # 保守估計

            normalized.append(product)

        return normalized

    def calculate_metrics(self) -> Dict[str, Any]:
        """從產品列表計算市場指標"""
        metrics = {}

        if not self.products:
            return metrics

        # 計算總銷額和銷量
        total_revenue = sum(p.get('月銷額', 0) for p in self.products)
        total_sales = sum(p.get('月銷量', 0) for p in self.products)

        # 計算平均值
        prices = [p.get('價格', 0) for p in self.products if p.get('價格', 0) > 0]
        ratings = [p.get('評分', 0) for p in self.products if p.get('評分', 0) > 0]

        avg_price = sum(prices) / len(prices) if prices else 0
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        # 價格區間
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        # 品牌分析
        brand_stats = {}
        for p in self.products:
            brand = p.get('品牌', 'Unknown')
            if brand not in brand_stats:
                brand_stats[brand] = {'count': 0, 'revenue': 0}
            brand_stats[brand]['count'] += 1
            brand_stats[brand]['revenue'] += p.get('月銷額', 0)

        # 按銷額排序
        sorted_brands = sorted(brand_stats.items(), key=lambda x: x[1]['revenue'], reverse=True)

        # Top3 品牌份額
        top3_revenue = sum(v['revenue'] for k, v in sorted_brands[:3])
        top3_share = top3_revenue / total_revenue * 100 if total_revenue > 0 else 0

        # HHI 計算
        brand_shares = {k: v['revenue'] / total_revenue * 100 for k, v in brand_stats.items()} if total_revenue > 0 else {}
        hhi = sum(s**2 for s in brand_shares.values())

        # Amazon 佔比
        amazon_products = [p for p in self.products if p.get('賣家', '') == 'Amazon']
        amazon_revenue = sum(p.get('月銷額', 0) for p in amazon_products)
        amazon_share = amazon_revenue / total_revenue * 100 if total_revenue > 0 else 0

        # 低評論產品佔比
        low_review_products = [p for p in self.products if p.get('評論數', 0) < 300]
        low_review_revenue = sum(p.get('月銷額', 0) for p in low_review_products)
        low_review_share = low_review_revenue / total_revenue * 100 if total_revenue > 0 else 0

        # 賣家來源分析
        seller_sources = {}
        for p in self.products:
            source = p.get('賣家來源', '其他')
            if not source:
                # 根據賣家名稱推斷來源
                seller = p.get('賣家', '')
                if 'Amazon' in seller:
                    source = 'Amazon自營'
                elif any(kw in seller.lower() for kw in ['china', 'cn', 'chinese']):
                    source = '中國賣家'
                elif any(kw in seller.lower() for kw in ['usa', 'us', 'american']):
                    source = '美國賣家'
                else:
                    source = '其他'

            if source not in seller_sources:
                seller_sources[source] = {'count': 0, 'revenue': 0}
            seller_sources[source]['count'] += 1
            seller_sources[source]['revenue'] += p.get('月銷額', 0)

        return {
            'total_revenue': total_revenue,
            'total_sales': total_sales,
            'avg_price': avg_price,
            'avg_rating': avg_rating,
            'min_price': min_price,
            'max_price': max_price,
            'product_count': len(self.products),
            'brand_count': len(brand_stats),
            'sorted_brands': sorted_brands,
            'top3_share': top3_share,
            'hhi': hhi,
            'amazon_share': amazon_share,
            'low_review_share': low_review_share,
            'seller_sources': seller_sources,
        }

    def generate(self) -> str:
        """生成完整的 Markdown 報告"""
        self.load_data()
        metrics = self.calculate_metrics()

        # 使用評分資料（如果有）或計算新評分
        if self.scores:
            scores = self.scores
            total_score = safe_int(scores.get('總分', 0))
            rating = scores.get('評級', '未知')
        else:
            # 計算評分
            scores = self._calculate_scores(metrics)
            total_score = scores['total']
            rating = scores['rating']

        report = f"""# {self.category_name} 品類選品分析報告

**站點**: {self.site} | **分析日期**: {datetime.now().strftime('%Y-%m-%d')}

---

## 執行摘要

| 指標 | 數值 |
|------|------|
| **總分** | **{total_score}/100** |
| **評級** | **{rating}** |
| **建議** | **{self._get_recommendation(total_score)}** |
| 月市場規模 | \\${metrics.get('total_revenue', 0):,.0f} |
| Top100 月銷量 | {metrics.get('total_sales', 0):,} |
| 平均價格 | \\${metrics.get('avg_price', 0):.2f} |
| 平均評分 | {metrics.get('avg_rating', 0):.2f} |

---

## 五維評分分析

### 評分概覽

| 維度 | 得分 | 滿分 | 說明 |
|------|------|------|------|
| 市場規模 | {scores.get('市場規模', 0)}/20 | 20 | {self._get_market_size_desc(metrics.get('total_revenue', 0))} |
| 增長潛力 | {scores.get('增長潛力', 0)}/25 | 25 | 低評論產品佔比: {metrics.get('low_review_share', 0):.1f}% |
| 競爭烈度 | {scores.get('競爭烈度', 0)}/20 | 20 | Top3 品牌佔比: {metrics.get('top3_share', 0):.1f}% |
| 進入壁壘 | {scores.get('進入壁壘', 0)}/20 | 20 | Amazon 佔比: {metrics.get('amazon_share', 0):.1f}% |
| 利潤空間 | {scores.get('利潤空間', 0)}/15 | 15 | 平均價格: \\${metrics.get('avg_price', 0):.2f} |

### 詳細分析

#### 1. 市場規模 (得分: {scores.get('市場規模', 0)}/20)
- **月總銷額**: \\${metrics.get('total_revenue', 0):,.0f}
- **月總銷量**: {metrics.get('total_sales', 0):,}
- **市場規模評估**: {self._get_market_size_desc(metrics.get('total_revenue', 0))}

#### 2. 增長潛力 (得分: {scores.get('增長潛力', 0)}/25)
- **低評論產品銷額佔比**: {metrics.get('low_review_share', 0):.1f}%
- **新品機會**: {'較高' if metrics.get('low_review_share', 0) > 20 else '一般'}
- **分析**: 低評論產品佔比{'較高' if metrics.get('low_review_share', 0) > 20 else '較低'}，說明{'存在較多新品機會' if metrics.get('low_review_share', 0) > 20 else '市場較成熟，新品進入難度大'}

#### 3. 競爭烈度 (得分: {scores.get('競爭烈度', 0)}/20)
- **HHI 指數**: {metrics.get('hhi', 0):.1f} ({'高度集中' if metrics.get('hhi', 0) > 1800 else '中度集中' if metrics.get('hhi', 0) > 1000 else '低度集中'})
- **Top3 品牌份額**: {metrics.get('top3_share', 0):.1f}%
- **品牌數量**: {metrics.get('brand_count', 0)} 個

**競爭格局**: {'高度壟斷，競爭激烈' if metrics.get('top3_share', 0) > 50 else '中度集中，有一定機會' if metrics.get('top3_share', 0) > 30 else '競爭分散，機會較多'}

#### 4. 進入壁壘 (得分: {scores.get('進入壁壘', 0)}/20)
- **Amazon 自營佔比**: {metrics.get('amazon_share', 0):.1f}%

**進入難度**: {'較低' if metrics.get('amazon_share', 0) < 20 else '中等' if metrics.get('amazon_share', 0) < 40 else '較高'}

#### 5. 利潤空間 (得分: {scores.get('利潤空間', 0)}/15)
- **平均價格**: \\${metrics.get('avg_price', 0):.2f}
- **價格區間**: \\${metrics.get('min_price', 0):.2f} - \\${metrics.get('max_price', 0):.2f}
- **利潤評估**: {self._get_profit_desc(metrics.get('avg_price', 0))}

---

## 品牌分析

### Top 10 品牌

| 排名 | 品牌 | 產品數 | 月銷額 | 市場份額 |
|------|------|--------|--------|----------|
"""

        # 新增品牌資料
        sorted_brands = metrics.get('sorted_brands', [])
        total_revenue = metrics.get('total_revenue', 1)

        for i, (brand, stats) in enumerate(sorted_brands[:10], 1):
            share = stats['revenue'] / total_revenue * 100 if total_revenue > 0 else 0
            report += f"| {i} | {brand} | {stats['count']} | \\${stats['revenue']:,.0f} | {share:.2f}% |\n"

        report += f"""

### 品牌集中度分析

- **CR3 (Top3 集中度)**: {metrics.get('top3_share', 0):.2f}% - {'高度壟斷' if metrics.get('top3_share', 0) > 50 else '中度集中' if metrics.get('top3_share', 0) > 30 else '競爭分散'}
- **HHI 指數**: {metrics.get('hhi', 0):.1f}

**主要競爭者**:
"""

        for i, (brand, stats) in enumerate(sorted_brands[:5], 1):
            share = stats['revenue'] / total_revenue * 100 if total_revenue > 0 else 0
            report += f"{i}. **{brand}**: 市場份額 {share:.2f}%, {stats['count']} 款產品\n"

        report += f"""

---

## Top 20 產品詳情

| 排名 | ASIN | 品牌 | 價格 | 月銷量 | 月銷額 | 評分 | 評論數 |
|------|------|------|------|--------|--------|------|--------|
"""

        for i, p in enumerate(self.products[:20], 1):
            asin = p.get('ASIN', 'N/A')
            brand = p.get('品牌', 'N/A')[:15]
            price = p.get('價格', 0)
            sales = p.get('月銷量', 0)
            revenue = p.get('月銷額', 0)
            rating = p.get('評分', 0)
            reviews = p.get('評論數', 0)

            report += f"| {i} | {asin} | {brand} | \\${price:.2f} | {sales:,} | \\${revenue:,.0f} | {rating} | {reviews} |\n"

        report += f"""

---

## 賣家來源分析

| 來源 | 產品數 | 銷額佔比 |
|------|--------|----------|
"""

        seller_sources = metrics.get('seller_sources', {})
        total_revenue = metrics.get('total_revenue', 1)

        for source, stats in sorted(seller_sources.items(), key=lambda x: x[1]['revenue'], reverse=True):
            share = stats['revenue'] / total_revenue * 100 if total_revenue > 0 else 0
            report += f"| {source} | {stats['count']} | {share:.2f}% |\n"

        # 新增關鍵詞分析（如果有）
        if self.keywords:
            report += f"""

---

## 關鍵詞分析

### Top 15 核心關鍵詞

| 排名 | 關鍵詞 | 月搜尋量 | 周搜尋量 |
|------|--------|----------|----------|
"""
            for i, kw in enumerate(self.keywords[:15], 1):
                kw_name = kw.get('關鍵詞', kw.get('keyword', 'N/A'))
                monthly = safe_int(kw.get('月搜尋量', kw.get('monthlySearchVolume', 0)))
                weekly = safe_int(kw.get('周搜尋量', kw.get('weeklySearchVolume', 0)))
                report += f"| {i} | {kw_name} | {monthly:,} | {weekly:,} |\n"

        report += f"""

---

## 市場機會與策略建議

### 優勢
{self._generate_advantages(metrics)}

### 劣勢
{self._generate_disadvantages(metrics)}

### 機會
{self._generate_opportunities(metrics)}

### 威脅
{self._generate_threats(metrics)}

### 選品建議
{self._generate_recommendations(metrics, scores)}

---

## 結論

**綜合評分**: {total_score}/100 ({rating})

**最終建議**: {self._get_recommendation(total_score)}

**理由**:
{self._generate_conclusion(metrics, rating)}

**適合賣家**: {self._get_suitable_seller_profile(metrics, total_score)}

**不適合賣家**: {self._get_unsuitable_seller_profile(metrics, total_score)}

---

*報告生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*資料來源: Sorftime MCP*
"""

        return report

    def _calculate_scores(self, metrics: Dict) -> Dict:
        """計算五維評分"""
        scores = {}

        # 市場規模
        revenue = metrics.get('total_revenue', 0)
        if revenue > 10_000_000:
            scores['市場規模'] = 20
        elif revenue > 5_000_000:
            scores['市場規模'] = 17
        elif revenue > 1_000_000:
            scores['市場規模'] = 14
        else:
            scores['市場規模'] = 10

        # 增長潛力
        low_review_share = metrics.get('low_review_share', 0)
        if low_review_share > 40:
            scores['增長潛力'] = 22
        elif low_review_share > 20:
            scores['增長潛力'] = 18
        else:
            scores['增長潛力'] = 14

        # 競爭烈度
        top3_share = metrics.get('top3_share', 0)
        if top3_share < 30:
            scores['競爭烈度'] = 18
        elif top3_share < 50:
            scores['競爭烈度'] = 14
        else:
            scores['競爭烈度'] = 8

        # 進入壁壘
        amazon_share = metrics.get('amazon_share', 0)
        barrier_score = 0
        if amazon_share < 20:
            barrier_score += 10
        elif amazon_share < 40:
            barrier_score += 6
        else:
            barrier_score += 3
        if low_review_share > 40:
            barrier_score += 10
        elif low_review_share > 20:
            barrier_score += 6
        else:
            barrier_score += 3
        scores['進入壁壘'] = barrier_score

        # 利潤空間
        avg_price = metrics.get('avg_price', 0)
        if avg_price > 300:
            scores['利潤空間'] = 12
        elif avg_price > 150:
            scores['利潤空間'] = 10
        elif avg_price > 50:
            scores['利潤空間'] = 7
        else:
            scores['利潤空間'] = 4

        scores['total'] = sum(scores.values())

        if scores['total'] >= 80:
            scores['rating'] = '優秀'
        elif scores['total'] >= 70:
            scores['rating'] = '良好'
        elif scores['total'] >= 50:
            scores['rating'] = '一般'
        else:
            scores['rating'] = '較差'

        return scores

    def _get_market_size_desc(self, revenue: float) -> str:
        """獲取市場規模描述"""
        if revenue > 10_000_000:
            return '> $10M (優秀)'
        elif revenue > 5_000_000:
            return '> $5M (良好)'
        elif revenue > 1_000_000:
            return '> $1M (一般)'
        return '< $1M (較差)'

    def _get_profit_desc(self, avg_price: float) -> str:
        """獲取利潤空間描述"""
        if avg_price > 300:
            return '高價值品類，利潤空間大'
        elif avg_price > 150:
            return '中高價值，利潤可觀'
        elif avg_price > 50:
            return '中低端，利潤一般'
        return '低價品類，利潤空間小'

    def _get_recommendation(self, score: int) -> str:
        """獲取建議"""
        if score >= 80:
            return '強烈推薦進入'
        elif score >= 70:
            return '可以考慮進入'
        elif score >= 50:
            return '謹慎進入'
        return '不建議進入'

    def _generate_advantages(self, metrics: Dict) -> str:
        """生成優勢分析"""
        advantages = []
        revenue = metrics.get('total_revenue', 0)
        avg_price = metrics.get('avg_price', 0)

        if revenue > 10_000_000:
            advantages.append(f"1. **市場規模巨大**: 月銷額超過 \\${revenue/1_000_000:.1f}M，屬於高流量品類")
        elif revenue > 1_000_000:
            advantages.append(f"1. **市場規模可觀**: 月銷額達 \\${revenue/1_000_000:.1f}M")

        price_range = f"\\${metrics.get('min_price', 0):.0f}-\\${metrics.get('max_price', 0):.0f}"
        advantages.append(f"2. **價格帶豐富**: {price_range} 價格區間，滿足不同消費需求")

        return '\n'.join(advantages) if advantages else "暫無明顯優勢"

    def _generate_disadvantages(self, metrics: Dict) -> str:
        """生成劣勢分析"""
        disadvantages = []
        top3_share = metrics.get('top3_share', 0)

        if top3_share > 50:
            disadvantages.append(f"1. **品牌集中度極高**: Top3 品牌佔據 {top3_share:.1f}% 市場份額")

        amazon_share = metrics.get('amazon_share', 0)
        if amazon_share > 20:
            disadvantages.append(f"2. **Amazon 競爭**: Amazon 自營佔比 {amazon_share:.1f}%")

        low_review_share = metrics.get('low_review_share', 0)
        if low_review_share < 20:
            disadvantages.append("3. **新品機會有限**: 市場成熟，低評論產品佔比低")

        return '\n'.join(disadvantages) if disadvantages else "暫無明顯劣勢"

    def _generate_opportunities(self, metrics: Dict) -> str:
        """生成機會分析"""
        opportunities = []
        low_review_share = metrics.get('low_review_share', 0)

        if low_review_share > 20:
            opportunities.append("1. **新品機會**: 低評論產品佔比較高，存在新品進入空間")
        else:
            opportunities.append("1. **細分市場**: 尋找未被滿足的細分需求")

        top3_share = metrics.get('top3_share', 0)
        if top3_share < 50:
            opportunities.append("2. **品牌分散**: 競爭格局相對分散，有機會脫穎而出")

        avg_price = metrics.get('avg_price', 0)
        if avg_price > 100:
            opportunities.append("3. **中端市場**: \\$$100-\\$$300 價格區間有一定機會")

        return '\n'.join(opportunities) if opportunities else "需要深入調研尋找機會"

    def _generate_threats(self, metrics: Dict) -> str:
        """生成威脅分析"""
        threats = []

        top3_share = metrics.get('top3_share', 0)
        if top3_share > 70:
            threats.append("1. **頭部品牌壟斷**: 市場被少數品牌主導，新進入者競爭困難")

        amazon_share = metrics.get('amazon_share', 0)
        if amazon_share > 30:
            threats.append("2. **Amazon 自營壓力**: 與 Amazon 自營產品直接競爭")

        avg_price = metrics.get('avg_price', 0)
        if avg_price < 50:
            threats.append("3. **價格戰風險**: 低價品類利潤空間小，容易陷入價格戰")

        return '\n'.join(threats) if threats else "暫無明顯威脅"

    def _generate_recommendations(self, metrics: Dict, scores: Dict) -> str:
        """生成選品建議"""
        total_score = scores.get('total', 0)
        avg_price = metrics.get('avg_price', 0)

        if total_score >= 70:
            return """**可以考慮的方向**:
- 該品類綜合評分較高，值得深入研究
- 建議從中端價格區間切入
- 關注差異化產品定位

**注意事項**:
- 注意避開頭部品牌強勢產品線
- 確保供應鏈有成本優勢"""
        elif total_score >= 50:
            return f"""**謹慎考慮的方向**:
- \\${avg_price:.0f}-\\${avg_price*1.5:.0f} 價格區間的產品
- 尋找細分市場機會

**建議謹慎**:
- 競爭較激烈，需要仔細評估
- 建議先小規模測試"""
        else:
            return """**不建議進入**:
- 該品類綜合評分較低
- 建議尋找其他更合適的品類

**如仍想嘗試**:
- 需要有強大的供應鏈優勢
- 建議從配件或細分市場入手"""

    def _generate_conclusion(self, metrics: Dict, rating: str) -> str:
        """生成結論"""
        revenue = metrics.get('total_revenue', 0)
        top3_share = metrics.get('top3_share', 0)
        avg_price = metrics.get('avg_price', 0)

        if revenue > 1_000_000:
            desc = f"月銷額達 \\${revenue/1_000_000:.1f}M+"
        else:
            desc = f"月銷額達 \\${revenue:,.0f}"

        competition = "極其激烈" if top3_share > 50 else "較為激烈" if top3_share > 30 else "相對分散"
        value = "高價值" if avg_price > 300 else "中高價值" if avg_price > 150 else "中低端"

        return f"""{self.category_name} 品類是一個{value}市場，{desc}。但市場競爭{competition}{'，頭部品牌佔據主導地位' if top3_share > 50 else '，仍有進入機會'}。"""

    def _get_suitable_seller_profile(self, metrics: Dict, score: int) -> str:
        """獲取適合的賣家畫像"""
        if score >= 70:
            return "有一定資金實力、有供應鏈資源、有運營經驗的賣家"
        elif score >= 50:
            return "有特定品類經驗、能找到差異化定位的賣家"
        return "不推薦新手賣家進入"

    def _get_unsuitable_seller_profile(self, metrics: Dict, score: int) -> str:
        """獲取不適合的賣家畫像"""
        return "新手賣家、無供應鏈資源的小賣家、資金有限的賣家"

    def save(self, output_file: str = None):
        """儲存報告到檔案"""
        if output_file is None:
            output_file = os.path.join(self.data_dir, 'report.md')

        report = self.generate()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        return output_file


def main():
    import sys

    if len(sys.argv) < 2:
        print("用法: python generate_markdown_report.py <資料目錄> [品類名稱] [站點] [輸出檔案]")
        print("\n示例:")
        print("  python generate_markdown_report.py category-reports/Sofas_US_20260304")
        print("  python generate_markdown_report.py category-reports/Sofas_US_20260304 'Sofas' US report.md")
        sys.exit(1)

    data_dir = sys.argv[1]
    category_name = sys.argv[2] if len(sys.argv) > 2 else 'Unknown Category'
    site = sys.argv[3] if len(sys.argv) > 3 else 'US'
    output_file = sys.argv[4] if len(sys.argv) > 4 else None

    generator = MarkdownReportGenerator(data_dir, category_name, site)
    saved_file = generator.save(output_file)

    print(f"✓ 報告已生成: {saved_file}")


if __name__ == "__main__":
    main()
