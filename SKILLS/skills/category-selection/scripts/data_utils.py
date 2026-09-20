#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品類選品資料處理工具
包含: HHI計算、價格/評分分組、新產品篩選、增長率計算等
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


class DataProcessor:
    """品類資料處理工具類"""

    @staticmethod
    def calculate_hhi(brand_shares: Dict[str, float]) -> float:
        """
        計算HHI指數 (Herfindahl-Hirschman Index)

        Args:
            brand_shares: {品牌名: 市場份額百分比}

        Returns:
            HHI指數
        """
        hhi = 0
        for share in brand_shares.values():
            hhi += share ** 2
        return round(hhi, 2)

    @staticmethod
    def calculate_cr(brand_shares: Dict[str, float], top_n: int = 3) -> float:
        """
        計算CRn集中度 (Concentration Ratio)

        Args:
            brand_shares: {品牌名: 市場份額百分比}
            top_n: 前n個品牌

        Returns:
            CRn百分比
        """
        # 按市場份額降序排序
        sorted_brands = sorted(brand_shares.items(), key=lambda x: x[1], reverse=True)
        top_shares = sorted_brands[:top_n]
        cr = sum(share for _, share in top_shares)
        return round(cr, 2)

    @staticmethod
    def group_by_price_range(products: List[Dict], ranges: List[Dict] = None) -> List[Dict]:
        """
        按價格區間分組產品

        Args:
            products: 產品列表
            ranges: 自定義價格區間，預設為5個區間

        Returns:
            分組結果
        """
        if ranges is None:
            ranges = [
                {"name": "超低價", "min": 0, "max": 20},
                {"name": "低價", "min": 20, "max": 50},
                {"name": "中價", "min": 50, "max": 100},
                {"name": "高價", "min": 100, "max": 200},
                {"name": "超高價", "min": 200, "max": float('inf')},
            ]

        result = []
        for range_def in ranges:
            group = {
                "range": f"{range_def['name']} (${range_def['min']}-{range_def['max'] if range_def['max'] != float('inf') else '+'})",
                "count": 0,
                "sales": 0,
                "revenue": 0,
                "ratings": [],
                "products": []
            }

            for product in products:
                price = product.get("price", 0)
                if range_def['min'] <= price < range_def['max']:
                    group["count"] += 1
                    group["sales"] += product.get("monthly_sales", 0)
                    group["revenue"] += product.get("monthly_revenue", 0)
                    if product.get("rating"):
                        group["ratings"].append(product["rating"])
                    group["products"].append(product)

            # 計算佔比和平均評分
            total_products = len(products)
            total_revenue = sum(p.get("monthly_revenue", 0) for p in products)

            group["percentage"] = round(group["count"] / total_products * 100, 1) if total_products > 0 else 0
            group["avg_rating"] = round(sum(group["ratings"]) / len(group["ratings"]), 2) if group["ratings"] else 0

            result.append(group)

        return result

    @staticmethod
    def group_by_rating_range(products: List[Dict], ranges: List[Dict] = None) -> List[Dict]:
        """
        按評分割槽間分組產品

        Args:
            products: 產品列表
            ranges: 自定義評分割槽間，預設為5個區間

        Returns:
            分組結果
        """
        if ranges is None:
            ranges = [
                {"name": "低分", "min": 0, "max": 3.5},
                {"name": "中低分", "min": 3.5, "max": 4.0},
                {"name": "中等", "min": 4.0, "max": 4.3},
                {"name": "中高分", "min": 4.3, "max": 4.7},
                {"name": "高分", "min": 4.7, "max": 5.0},
            ]

        result = []
        for range_def in ranges:
            group = {
                "range": f"{range_def['name']} ({range_def['min']}-{range_def['max']})",
                "count": 0,
                "sales": 0,
                "sales_percentage": 0
            }

            for product in products:
                rating = product.get("rating", 0)
                if range_def['min'] <= rating < range_def['max']:
                    group["count"] += 1
                    group["sales"] += product.get("monthly_sales", 0)

            # 計算佔比
            total_sales = sum(p.get("monthly_sales", 0) for p in products)
            group["sales_percentage"] = round(group["sales"] / total_sales * 100, 1) if total_sales > 0 else 0
            group["percentage"] = round(group["count"] / len(products) * 100, 1) if products else 0

            result.append(group)

        return result

    @staticmethod
    def filter_new_products(products: List[Dict], days_threshold: int = 90) -> List[Dict]:
        """
        篩選新產品 (上架時間小於指定天數)

        Args:
            products: 產品列表
            days_threshold: 天數閾值，預設90天(3個月)

        Returns:
            新產品列表
        """
        today = datetime.now()
        threshold_date = today - timedelta(days=days_threshold)

        new_products = []
        for product in products:
            days_online = product.get("days_online", 0)
            if days_online and days_online <= days_threshold:
                new_products.append(product)

        return new_products

    @staticmethod
    def analyze_brand_distribution(products: List[Dict]) -> List[Dict]:
        """
        分析品牌分佈

        Args:
            products: 產品列表

        Returns:
            品牌分析列表，按市場份額降序排序
        """
        brand_data = {}

        for product in products:
            brand = product.get("brand", "Unknown")
            if brand not in brand_data:
                brand_data[brand] = {
                    "brand": brand,
                    "product_count": 0,
                    "monthly_sales": 0,
                    "monthly_revenue": 0,
                    "ratings": []
                }

            brand_data[brand]["product_count"] += 1
            brand_data[brand]["monthly_sales"] += product.get("monthly_sales", 0)
            brand_data[brand]["monthly_revenue"] += product.get("monthly_revenue", 0)
            if product.get("rating"):
                brand_data[brand]["ratings"].append(product["rating"])

        # 計算總銷額
        total_revenue = sum(b["monthly_revenue"] for b in brand_data.values())

        # 計算市場份額和平均評分
        for brand in brand_data.values():
            brand["market_share"] = round(brand["monthly_revenue"] / total_revenue * 100, 2) if total_revenue > 0 else 0
            brand["avg_rating"] = round(sum(brand["ratings"]) / len(brand["ratings"]), 2) if brand["ratings"] else 0

        # 按市場份額降序排序
        sorted_brands = sorted(brand_data.values(), key=lambda x: x["market_share"], reverse=True)

        return sorted_brands

    @staticmethod
    def analyze_seller_distribution(products: List[Dict]) -> Dict[str, Dict]:
        """
        分析賣家來源分佈

        Args:
            products: 產品列表

        Returns:
            按來源地分組的統計資料
        """
        source_data = {
            "中國": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "美國": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "品牌": {"seller_count": set(), "product_count": 0, "revenue": 0},
            "其他": {"seller_count": set(), "product_count": 0, "revenue": 0}
        }

        for product in products:
            seller = product.get("seller", "")
            source = product.get("seller_source", "其他")

            if source in source_data:
                source_data[source]["seller_count"].add(seller)
                source_data[source]["product_count"] += 1
                source_data[source]["revenue"] += product.get("monthly_revenue", 0)

        # 轉換為列表格式
        result = []
        total_revenue = sum(s["revenue"] for s in source_data.values())

        for source, data in source_data.items():
            result.append({
                "source": source,
                "seller_count": len(data["seller_count"]),
                "product_count": data["product_count"],
                "revenue": data["revenue"],
                "percentage": round(data["revenue"] / total_revenue * 100, 1) if total_revenue > 0 else 0
            })

        # 按銷額降序排序
        result.sort(key=lambda x: x["revenue"], reverse=True)

        return result

    @staticmethod
    def calculate_growth_rate(trend_data: List[Dict], period_months: int = 3) -> Dict[str, float]:
        """
        計算增長率和環比

        Args:
            trend_data: 趨勢資料列表，每個元素包含 {date, value}
            period_months: 對比周期月數

        Returns:
            {同比增長率, 環比增長率}
        """
        if len(trend_data) < period_months + 1:
            return {"yoy": 0, "mom": 0}

        current_avg = sum(d["value"] for d in trend_data[-period_months:]) / period_months
        previous_avg = sum(d["value"] for d in trend_data[-(period_months*2+1):-period_months]) / period_months

        yoy = round((current_avg - previous_avg) / previous_avg * 100, 2) if previous_avg > 0 else 0

        # 環比 (上個月 vs 這個月)
        if len(trend_data) >= 2:
            last_month = trend_data[-1]["value"]
            prev_month = trend_data[-2]["value"]
            mom = round((last_month - prev_month) / prev_month * 100, 2) if prev_month > 0 else 0
        else:
            mom = 0

        return {"yoy": yoy, "mom": mom}

    @staticmethod
    def calculate_five_dimension_score(data: Dict) -> Dict[str, float]:
        """
        計算五維評分 (標準版本 - 與需求文件一致)

        評分標準:
        - 市場規模 (20分): >10M=20, >5M=17, >1M=14, 其他=10
        - 增長潛力 (25分): 低評論佔比>40%=22, >20%=18, 其他=14
        - 競爭烈度 (20分): Top3<30%=18, <50%=14, 其他=8
        - 進入壁壘 (20分): Amazon佔比+新品機會組合評分
        - 利潤空間 (15分): 均價>$300=12, >$150=10, >$50=7, 其他=4

        Args:
            data: 包含所有市場資料的字典

        Returns:
            五維評分結果
        """
        scores = {}

        # 1. 市場規模 (20分) - 標準版本
        total_revenue = data.get("total_monthly_revenue", 0)
        if total_revenue > 10_000_000:
            scores["market_size"] = 20
        elif total_revenue > 5_000_000:
            scores["market_size"] = 17
        elif total_revenue > 1_000_000:
            scores["market_size"] = 14
        else:
            scores["market_size"] = 10

        # 2. 增長潛力 (25分) - 基於低評論產品佔比
        low_review_share = data.get("low_reviews_sales_volume_share", 0)
        if low_review_share > 40:
            scores["growth_potential"] = 22
        elif low_review_share > 20:
            scores["growth_potential"] = 18
        else:
            scores["growth_potential"] = 14

        # 3. 競爭烈度 (20分) - 基於 Top3 品牌佔比
        top3_share = data.get("top3_brands_sales_volume_share", 0)
        if top3_share < 30:
            scores["competition"] = 18
        elif top3_share < 50:
            scores["competition"] = 14
        else:
            scores["competition"] = 8

        # 4. 進入壁壘 (20分) - Amazon 佔比 + 新品機會
        amazon_share = data.get("amazonOwned_sales_volume_share", 0)
        low_review_share = data.get("low_reviews_sales_volume_share", 0)

        barrier_score = 0
        # Amazon 佔比越低，壁壘越小 (0-10分)
        if amazon_share < 20:
            barrier_score += 10
        elif amazon_share < 40:
            barrier_score += 6
        else:
            barrier_score += 3

        # 新品機會越大，壁壘越小 (0-10分)
        if low_review_share > 40:
            barrier_score += 10
        elif low_review_share > 20:
            barrier_score += 6
        else:
            barrier_score += 3

        scores["entry_barrier"] = barrier_score

        # 5. 利潤空間 (15分) - 基於平均價格
        avg_price = data.get("average_price", 0)
        if avg_price > 300:
            scores["profit_margin"] = 12
        elif avg_price > 150:
            scores["profit_margin"] = 10
        elif avg_price > 50:
            scores["profit_margin"] = 7
        else:
            scores["profit_margin"] = 4

        # 計算總分
        scores["total"] = (
            scores["market_size"] +
            scores["growth_potential"] +
            scores["competition"] +
            scores["entry_barrier"] +
            scores["profit_margin"]
        )

        # 評級
        if scores["total"] >= 80:
            scores["rating"] = "優秀"
        elif scores["total"] >= 70:
            scores["rating"] = "良好"
        elif scores["total"] >= 50:
            scores["rating"] = "一般"
        else:
            scores["rating"] = "較差"

        return scores

    @staticmethod
    def prepare_html_data(data: Dict) -> Dict:
        """
        準備HTML報告所需的資料格式

        Args:
            data: 原始資料

        Returns:
            HTML模板變數字典
        """
        return {
            # 基礎資訊
            "CATEGORY_NAME": data.get("category_name", ""),
            "SITE": data.get("site", "US"),
            "DATA_DATE": datetime.now().strftime("%Y-%m-%d"),

            # 五維評分
            "MARKET_SIZE_SCORE": data.get("scores", {}).get("market_size", 0),
            "MARKET_SIZE_PERCENT": int(data.get("scores", {}).get("market_size", 0) / 20 * 100),
            "GROWTH_POTENTIAL_SCORE": data.get("scores", {}).get("growth_potential", 0),
            "GROWTH_POTENTIAL_PERCENT": int(data.get("scores", {}).get("growth_potential", 0) / 25 * 100),
            "COMPETITION_SCORE": data.get("scores", {}).get("competition", 0),
            "COMPETITION_PERCENT": int(data.get("scores", {}).get("competition", 0) / 20 * 100),
            "ENTRY_BARRIER_SCORE": data.get("scores", {}).get("entry_barrier", 0),
            "ENTRY_BARRIER_PERCENT": int(data.get("scores", {}).get("entry_barrier", 0) / 20 * 100),
            "PROFIT_MARGIN_SCORE": data.get("scores", {}).get("profit_margin", 0),
            "PROFIT_MARGIN_PERCENT": int(data.get("scores", {}).get("profit_margin", 0) / 15 * 100),
            "TOTAL_SCORE": data.get("scores", {}).get("total", 0),
            "RATING": data.get("rating", ""),
            "RECOMMENDATION": data.get("recommendation", ""),

            # KPI
            "TOTAL_PRODUCTS": data.get("total_products", 0),
            "AVG_PRICE": f"${data.get("avg_price", 0):.2f}",
            "AVG_SALES": f"{data.get("avg_sales", 0):.0f}",
            "AVG_RATING": f"{data.get("avg_rating", 0):.2f}",
            "TOTAL_SALES": f"${data.get("total_sales", 0):,.0f}",
            "CR3": f"{data.get("cr3", 0):.2f}",

            # 趨勢資料 (需要JSON序列化)
            "SALES_TREND_DATA": json.dumps(data.get("sales_trend", {"dates": [], "sales": []})),
            "PRICE_TREND_DATA": json.dumps(data.get("price_trend", {"dates": [], "prices": []})),
            "PRICE_DIST_DATA": json.dumps(data.get("price_dist", [])),
            "RATING_DIST_DATA": json.dumps(data.get("rating_dist", {"ranges": [], "counts": []})),
            "BRAND_SHARE_DATA": json.dumps(data.get("brand_share", {"brands": [], "shares": []})),
            "SELLER_SOURCE_DATA": json.dumps(data.get("seller_source", [])),
            "BRAND_RATING_TREND_DATA": json.dumps(data.get("brand_rating_trend", {"brands": [], "dates": [], "data": {}})),
            "TOP50_PRODUCTS": json.dumps(data.get("top50_products", [])),

            # 關鍵發現
            "CONCENTRATION_LEVEL": data.get("concentration_level", ""),
            "HHI": f"{data.get('hhi', 0):.2f}",
            "CR3_RAW": f"{data.get('cr3_raw', 0)}",
            "CONCLUSION_CR3": data.get("conclusion_cr3", ""),
            "BRAND_COUNT": data.get("brand_count", 0),
            "BRAND_DIVERSITY": data.get("brand_diversity", ""),
            "NEW_PRODUCT_PERCENT": f"{data.get('new_product_percent', 0)}%",
            "NEW_PRODUCT_CONCLUSION": data.get("new_product_conclusion", ""),
            "SELLER_DISTRIBUTION": data.get("seller_distribution", ""),
            "COMPETITION_CONCLUSION": data.get("competition_conclusion", ""),
            "STRATEGY": data.get("strategy", ""),
            "GENERATED_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# 使用示例
if __name__ == "__main__":
    # 示例產品資料
    sample_products = [
        {"asin": "B001", "brand": "Sony", "price": 150, "rating": 4.5, "monthly_sales": 1000,
         "monthly_revenue": 150000, "seller": "Amazon", "seller_source": "品牌", "days_online": 45},
        {"asin": "B002", "brand": "Samsung", "price": 120, "rating": 4.2, "monthly_sales": 800,
         "monthly_revenue": 96000, "seller": "Seller1", "seller_source": "中國", "days_online": 200},
        {"asin": "B003", "brand": "LG", "price": 180, "rating": 4.6, "monthly_sales": 500,
         "monthly_revenue": 90000, "seller": "Seller2", "seller_source": "韓國", "days_online": 30},
    ]

    processor = DataProcessor()

    # 品牌分佈分析
    brands = processor.analyze_brand_distribution(sample_products)
    print("品牌分佈:", brands)

    # 價格分組
    price_groups = processor.group_by_price_range(sample_products)
    print("價格分組:", price_groups)

    # 評分分組
    rating_groups = processor.group_by_rating_range(sample_products)
    print("評分分組:", rating_groups)

    # 新產品篩選
    new_products = processor.filter_new_products(sample_products)
    print("新產品:", new_products)
