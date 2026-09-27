#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
選品分析主指令碼 - 整合資料採集、分析和報告生成

最佳化版本 v3.1 - 完全通用化（移除硬編碼類別詞）

使用方法:
    python run_analysis.py "keyword" US
    python run_analysis.py "keyword" US --no-reviews
"""
import sys
import os
import json
import argparse
from datetime import datetime
from collections import defaultdict

# 新增指令碼目錄到路徑
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from collect_data import collect_data, create_output_dir, save_json
from api_client import SorftimeClient


def get_project_root():
    """獲取專案根目錄"""
    # 從 scripts/ 向上四級到達專案根目錄
    # 指令碼路徑：.claude/skills/product-research/scripts/
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))


def analyze_market_data(raw_dir, output_dir):
    """分析市場資料（價格區間、品牌、形態等）"""
    print("\n[分析] 市場資料分析...")

    # 讀取 Top100 資料
    top100_path = os.path.join(raw_dir, 'top100.json')
    if not os.path.exists(top100_path):
        print("  ✗ top100.json 不存在")
        return None

    with open(top100_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('Top100產品', [])
    stats = data.get('類目統計報告', {})

    if not products:
        print("  ✗ 產品資料為空")
        return None

    print(f"  ✓ 產品數量: {len(products)}")

    # 價格區間分析
    price_ranges = defaultdict(lambda: {'count': 0, 'sales': 0})
    for p in products:
        price = float(p.get('價格', 0))
        sales = float(p.get('月銷量', 0))

        if price < 30:
            price_ranges['0-30']['count'] += 1
            price_ranges['0-30']['sales'] += sales
        elif price < 60:
            price_ranges['30-60']['count'] += 1
            price_ranges['30-60']['sales'] += sales
        elif price < 100:
            price_ranges['60-100']['count'] += 1
            price_ranges['60-100']['sales'] += sales
        elif price < 150:
            price_ranges['100-150']['count'] += 1
            price_ranges['100-150']['sales'] += sales
        elif price < 200:
            price_ranges['150-200']['count'] += 1
            price_ranges['150-200']['sales'] += sales
        else:
            price_ranges['200+']['count'] += 1
            price_ranges['200+']['sales'] += sales

    # 品牌分析
    brand_sales = defaultdict(float)
    brand_count = defaultdict(int)
    for p in products:
        brand = p.get('品牌', 'Unknown')
        sales = float(p.get('月銷量', 0))
        brand_sales[brand] += sales
        brand_count[brand] += 1

    # 賣家來源分析
    seller_source_sales = defaultdict(float)
    seller_source_count = defaultdict(int)
    for p in products:
        source = p.get('賣家來源', 'Unknown')
        sales = float(p.get('月銷量', 0))
        seller_source_sales[source] += sales
        seller_source_count[source] += 1

    # 彙總分析結果
    # 注意：產品形態分析由 LLM 在報告生成階段完成，不在此處硬編碼
    analysis = {
        'price_ranges': dict(price_ranges),
        'top_brands': dict(sorted(brand_sales.items(), key=lambda x: x[1], reverse=True)[:10]),
        'brand_counts': dict(brand_count),
        'seller_sources': dict(seller_source_sales),
        'seller_counts': dict(seller_source_count),
        'top20_products': products[:20]
    }

    # 儲存分析結果
    analysis_path = os.path.join(output_dir, 'market_analysis.json')
    save_json(analysis, analysis_path)
    print(f"  ✓ 分析結果已儲存: {analysis_path}")

    return analysis


def collect_competitor_reviews(node_id, site, raw_dir, max_reviews=6):
    """收集競品差評資料"""
    print("\n[資料採集] 競品差評分析...")

    client = SorftimeClient()

    # 讀取 Top100 資料，選擇代表性競品
    top100_path = os.path.join(raw_dir, 'top100.json')
    if not os.path.exists(top100_path):
        print("  ✗ top100.json 不存在，跳過差評分析")
        return False

    with open(top100_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    products = data.get('Top100產品', [])

    # 按銷量排序，選擇不同價格帶的代表性產品
    sorted_products = sorted(products, key=lambda x: float(x.get('月銷量', 0)), reverse=True)

    # 輔助函式：相容中英文鍵名
    def get_field(product, field_name, cn_field_name):
        """獲取產品欄位，相容中英文鍵名"""
        return product.get(field_name) or product.get(cn_field_name, '')

    def get_asin(p):
        return get_field(p, 'ASIN', '產品ASIN碼')

    def get_brand(p):
        return get_field(p, '品牌', 'Brand')

    # 選擇策略：Top3 + 不同價格帶代表
    competitors = []

    # 量級標杆（Top3）
    for p in sorted_products[:3]:
        asin = get_asin(p)
        brand = get_brand(p)
        if asin:
            competitors.append((asin, f"{brand} - 量級標杆"))

    # 中價位代表 ($30-60)
    mid_price = [p for p in sorted_products if 30 <= float(p.get('價格', 0)) < 60]
    if mid_price:
        asin = get_asin(mid_price[0])
        brand = get_brand(mid_price[0])
        if asin:
            competitors.append((asin, f"{brand} - 中價位"))

    # 低價位代表 ($0-30)
    low_price = [p for p in sorted_products if float(p.get('價格', 0)) < 30]
    if low_price:
        asin = get_asin(low_price[0])
        brand = get_brand(low_price[0])
        if asin:
            competitors.append((asin, f"{brand} - 低價位"))

    # 高價位代表 ($100+)
    high_price = [p for p in sorted_products if float(p.get('價格', 0)) >= 100]
    if high_price:
        asin = get_asin(high_price[0])
        brand = get_brand(high_price[0])
        if asin:
            competitors.append((asin, f"{brand} - 高價位"))

    # 去重
    seen = set()
    competitors = [x for x in competitors if not (x[0] in seen or seen.add(x[0]))]

    # 限制數量
    competitors = competitors[:max_reviews]

    print(f"  選擇競品數量: {len(competitors)}")

    all_reviews = {}
    for asin, desc in competitors:
        print(f"  - {asin} ({desc})...", end=' ', flush=True)
        try:
            reviews, raw = client.get_product_reviews(site, asin, 'Negative')
            if reviews:
                if isinstance(reviews, list):
                    review_count = len(reviews)
                    sample = reviews[:20] if len(reviews) > 20 else reviews
                else:
                    review_count = 'data'
                    sample = reviews

                all_reviews[asin] = {
                    'description': desc,
                    'review_count': review_count,
                    'reviews': sample
                }
                print(f"✓ {review_count}條")
            else:
                print("✗ 無資料")
        except Exception as e:
            print(f"✗ {str(e)[:40]}")

    # 儲存
    if all_reviews:
        reviews_path = os.path.join(raw_dir, 'competitor_reviews.json')
        save_json(all_reviews, reviews_path)
        print(f"  ✓ 差評資料已儲存: {reviews_path}")
        return True

    return False


def update_data_json(raw_dir, output_dir):
    """
    更新 data.json - 將分析資料合併到 Dashboard 需要的格式

    這個函式解決了資料結構不匹配的問題：
    - collect_data.py 生成的基礎 data.json 只有後設資料
    - render_dashboard.py 期望完整的資料結構
    - 本函式將 market_analysis.json 等分析結果合併到 data.json
    """
    print("\n[更新] 合併分析資料到 data.json...")

    data_json_path = os.path.join(output_dir, 'data.json')
    market_analysis_path = os.path.join(output_dir, 'market_analysis.json')
    top100_path = os.path.join(raw_dir, 'top100.json')
    trend_path = os.path.join(raw_dir, 'trend.json')
    keywords_path = os.path.join(raw_dir, 'keywords.json')

    # 讀取現有的 data.json
    if not os.path.exists(data_json_path):
        print("  ✗ data.json 不存在")
        return False

    with open(data_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 讀取並處理 market_analysis.json
    if os.path.exists(market_analysis_path):
        with open(market_analysis_path, 'r', encoding='utf-8') as f:
            market_analysis = json.load(f)

        # 轉換價格區間資料為 Dashboard 期望的列表格式
        if 'price_ranges' in market_analysis:
            price_ranges_dict = market_analysis['price_ranges']
            price_ranges_list = []
            total_sales = sum(p['sales'] for p in price_ranges_dict.values())

            for range_name, range_data in price_ranges_dict.items():
                count = range_data['count']
                sales = range_data['sales']
                share = sales / total_sales if total_sales > 0 else 0
                price_ranges_list.append({
                    'range': f'${range_name}',
                    'count': count,
                    'share': share,
                    'sales': sales
                })

            data['price_ranges'] = price_ranges_list

        # 轉換品牌資料
        if 'top_brands' in market_analysis:
            top_brands = []
            for brand, sales in market_analysis['top_brands'].items():
                brand_count = market_analysis.get('brand_counts', {}).get(brand, 0)
                top_brands.append({
                    'brand': brand,
                    'sales': int(sales),
                    'revenue': int(sales * 50),  # 估算收入
                    'count': brand_count
                })
            data['top_brands'] = top_brands[:10]

        # 轉換競品資料
        if 'top20_products' in market_analysis:
            competitors = []
            for p in market_analysis['top20_products'][:10]:
                competitors.append({
                    'asin': p.get('ASIN', ''),
                    'brand': p.get('品牌', ''),
                    'title': p.get('標題', ''),
                    'price': float(p.get('價格', 0)),
                    'monthly_sales': int(float(p.get('月銷量', 0))),
                    'reviews': int(float(p.get('評論數', 0))),
                    'rating': float(p.get('星級', 0)),
                    'type': '競品',
                    'launch_date': p.get('上線日期', '')
                })
            data['competitors'] = competitors

    # 讀取並處理 trend.json
    if os.path.exists(trend_path):
        with open(trend_path, 'r', encoding='utf-8') as f:
            trend_data = json.load(f)

        if 'trend_data' in trend_data:
            data['trend_data'] = trend_data['trend_data']

    # 讀取並處理 keywords.json
    if os.path.exists(keywords_path):
        with open(keywords_path, 'r', encoding='utf-8') as f:
            keywords_data = json.load(f)

        # 轉換為 Dashboard 期望的格式
        keywords_summary = {}
        for kw_name, kw_data in keywords_data.items():
            if isinstance(kw_data, dict) and '關鍵詞' in kw_data:
                keywords_summary[kw_name] = {
                    'monthly_search': int(float(kw_data.get('月搜尋量', 0))),
                    'weekly_search': int(float(kw_data.get('周搜尋量', 0))),
                    'cpc': float(kw_data.get('推薦cpc競價', 0)),
                    'competition_count': int(float(kw_data.get('搜尋結果競品數量', 0)))
                }

        data['keywords'] = keywords_summary

    # 計算市場概覽指標（從 top100 資料）
    if os.path.exists(top100_path):
        with open(top100_path, 'r', encoding='utf-8') as f:
            top100_data = json.load(f)

        products = top100_data.get('Top100產品', [])
        stats = top100_data.get('類目統計報告', {})

        if products and stats:
            total_sales = sum(float(p.get('月銷量', 0)) for p in products)
            total_revenue = sum(float(p.get('月銷額', 0)) for p in products)

            # 計算品牌集中度
            brand_sales = {}
            for p in products:
                brand = p.get('品牌', 'Unknown')
                sales = float(p.get('月銷量', 0))
                brand_sales[brand] = brand_sales.get(brand, 0) + sales

            sorted_brands = sorted(brand_sales.items(), key=lambda x: x[1], reverse=True)
            top3_brand_sales = sum(sales for _, sales in sorted_brands[:3])
            top10_brand_sales = sum(sales for _, sales in sorted_brands[:10])

            data['market_overview'] = {
                'top100_monthly_sales': int(total_sales),
                'top100_monthly_revenue': int(total_revenue),
                'avg_price': total_revenue / total_sales if total_sales > 0 else 0,
                'median_price': sorted([float(p.get('價格', 0)) for p in products])[len(products)//2] if products else 0,
                'top3_product_concentration': 0,  # 簡化
                'top3_brand_concentration': top3_brand_sales / total_sales if total_sales > 0 else 0,
                'top10_brand_concentration': top10_brand_sales / total_sales if total_sales > 0 else 0,
                'amazon_share': 0,  # 需要從賣家資料計算
                'china_seller_share': 0,
                'new_product_share': 0,
                'keyword_monthly_search': data.get('keywords', {}).get(data.get('metadata', {}).get('keyword', ''), {}).get('monthly_search', 0)
            }

    # 儲存更新後的 data.json
    save_json(data, data_json_path)
    print(f"  ✓ data.json 已更新")
    return True


def render_dashboard_html(output_dir, check_complete=False):
    """
    渲染 Dashboard HTML

    Args:
        output_dir: 輸出目錄
        check_complete: 是否檢查分析資料完整性（用於 --final 模式）
    """
    print("\n[Dashboard] 渲染視覺化看板...")

    # 匯入 render_dashboard
    try:
        from render_dashboard import DashboardRenderer

        data_json_path = os.path.join(output_dir, 'data.json')
        dashboard_path = os.path.join(output_dir, 'dashboard.html')

        # 檢查 data.json 是否存在
        if not os.path.exists(data_json_path):
            print(f"  ✗ data.json 不存在，無法渲染 Dashboard")
            return False

        # 如果是 --final 模式，先檢查資料完整性
        if check_complete:
            print(f"  檢查分析資料完整性...")
            with open(data_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            is_complete, missing = DashboardRenderer.validate_analysis_data(data)

            if not is_complete:
                print(f"  ✗ 分析資料不完整，缺少: {', '.join(missing)}")
                print(f"  ℹ️ 請先完成 LLM 分析（屬性標註、交叉分析、VOC、決策評估）")
                return False

            print(f"  ✓ 資料完整，渲染最終版 Dashboard")

        # 渲染 Dashboard
        renderer = DashboardRenderer()
        result_path = renderer.render(data_json_path, dashboard_path)

        print(f"  ✓ Dashboard 已生成: {result_path}")
        return True

    except ImportError as e:
        print(f"  ✗ 無法匯入 render_dashboard: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Dashboard 渲染失敗: {e}")
        return False


def generate_report(keyword, site, output_dir, raw_dir, check_complete=False):
    """
    生成分析報告（Markdown + Dashboard）

    Args:
        keyword: 關鍵詞
        site: 站點
        output_dir: 輸出目錄
        raw_dir: 原始資料目錄
        check_complete: 是否檢查分析資料完整性（用於 --final 模式）
    """
    print("\n[報告生成] 生成分析報告...")

    report_path = os.path.join(output_dir, 'report.md')
    dashboard_path = os.path.join(output_dir, 'dashboard.html')

    # 檢查是否已有報告
    if os.path.exists(report_path):
        print(f"  ✓ 報告已存在: {report_path}")
    else:
        print(f"  ⚠ 報告需要 LLM 生成: {report_path}")

    # 自動渲染 Dashboard（如果 data.json 存在）
    if os.path.exists(dashboard_path) and not check_complete:
        print(f"  ✓ Dashboard 已存在: {dashboard_path}")
    else:
        # 嘗試自動渲染
        render_dashboard_html(output_dir, check_complete=check_complete)

    return True


def main():
    parser = argparse.ArgumentParser(
        description="選品分析主指令碼（通用版本）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程：資料採集 + 分析
  python run_analysis.py "speaker" US

  # 僅資料採集，不生成報告
  python run_analysis.py "speaker" US --collect-only

  # 跳過差評採集
  python run_analysis.py "speaker" US --no-reviews

  # 最終渲染：LLM 分析完成後生成完整報告
  python run_analysis.py "speaker" US --final
        """
    )

    parser.add_argument('keyword', help='產品/類目關鍵詞')
    parser.add_argument('site', nargs='?', default='US', help='站點程式碼 (預設: US)')
    parser.add_argument('--keywords', '-k', type=int, default=3, help='採集關鍵詞數量 (預設: 3)')
    parser.add_argument('--no-reviews', action='store_true', help='跳過差評採集')
    parser.add_argument('--no-analysis', action='store_true', help='跳過市場分析')
    parser.add_argument('--collect-only', action='store_true', help='僅資料採集，不生成報告')
    parser.add_argument('--final', action='store_true', help='最終渲染模式：檢查資料完整性後生成完整版 Dashboard')

    args = parser.parse_args()

    print("=" * 60)
    print(f"🔍 選品分析: {args.keyword} ({args.site})")
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # --final 模式：僅渲染，不執行資料採集
    if args.final:
        output_dir, raw_dir, date_str = create_output_dir(args.keyword, args.site)

        data_json_path = os.path.join(output_dir, 'data.json')
        if not os.path.exists(data_json_path):
            print(f"\n✗ data.json 不存在: {data_json_path}")
            print(f"ℹ️ 請先執行資料採集: python run_analysis.py \"{args.keyword}\" {args.site}")
            return 1

        print(f"\n[最終渲染模式]")
        print(f"  檢查分析資料完整性...")

        # 讀取並驗證資料
        from render_dashboard import DashboardRenderer
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        is_complete, missing = DashboardRenderer.validate_analysis_data(data)

        if not is_complete:
            print(f"  ✗ 分析資料不完整，缺少: {', '.join(missing)}")
            print(f"  ℹ️ 請先完成 LLM 分析：")
            print(f"     1. 屬性標註（從 Top100 提取差異化維度）")
            print(f"     2. 交叉分析（發現供需缺口）")
            print(f"     3. VOC 分析（競品差評維度歸類）")
            print(f"     4. 決策評估（五維評分）")
            print(f"  ℹ️ 分析完成後，再次執行此命令")
            return 1

        print(f"  ✓ 資料完整，生成最終版 Dashboard")

        # 更新 data.json（確保最新）
        update_data_json(raw_dir, output_dir)

        # 生成最終報告
        generate_report(args.keyword, args.site, output_dir, raw_dir, check_complete=True)

        print("\n" + "=" * 60)
        print(f"✓ 最終報告生成完成!")
        print(f"輸出目錄: {output_dir}")
        print(f"完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        return 0

    # 正常模式：資料採集流程
    # Step 1: 資料採集
    collect_result = collect_data(args.keyword, args.site, args.keywords)

    if not collect_result.get('steps_completed'):
        print("\n✗ 資料採集失敗，無法繼續")
        return 1

    # 獲取輸出目錄
    output_dir, raw_dir, date_str = create_output_dir(args.keyword, args.site)

    # Step 2: 市場分析
    if not args.no_analysis and not args.collect_only:
        analysis = analyze_market_data(raw_dir, output_dir)

    # Step 3: 競品差評採集
    if not args.no_reviews and not args.collect_only:
        node_id = collect_result.get('node_id')
        if node_id:
            collect_competitor_reviews(node_id, args.site, raw_dir)

    # Step 4: 更新 data.json (合併分析資料)
    if not args.collect_only:
        update_data_json(raw_dir, output_dir)

    # Step 5: 生成報告
    if not args.collect_only:
        generate_report(args.keyword, args.site, output_dir, raw_dir)

    print("\n" + "=" * 60)
    print(f"✓ 資料採集完成!")
    print(f"輸出目錄: {output_dir}")
    print(f"完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nℹ️ 下一步：完成 LLM 分析後，執行以下命令生成最終報告:")
    print(f"   python run_analysis.py \"{args.keyword}\" {args.site} --final")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
