#!/usr/bin/env python3
"""
資料採集指令碼 - product-research 技能

最佳化版本 v3.1 - 完全通用化（移除硬編碼類別詞）

使用方法:
    python collect_data.py "your keyword" US

或直接匯入:
    from collect_data import collect_data
    result = collect_data("your keyword", "US")
"""

import sys
import os
import json
import re
from datetime import datetime

# 新增指令碼目錄到路徑
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from api_client import SorftimeClient


def create_output_dir(keyword, site):
    """建立輸出目錄（使用專案根目錄）"""
    date_str = datetime.now().strftime('%Y%m%d')
    safe_keyword = keyword.replace(' ', '_').replace('/', '_')

    # 獲取專案根目錄
    # 指令碼路徑：.claude/skills/product-research/scripts/collect_data.py
    # 需要向上四級：scripts → product-research → skills → .claude → amazon-mcp
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

    output_dir = os.path.join(project_root, 'product-research-reports', f'{safe_keyword}_{site}_{date_str}')
    raw_dir = os.path.join(output_dir, 'raw')
    os.makedirs(raw_dir, exist_ok=True)
    return output_dir, raw_dir, date_str


def save_json(data, filepath):
    """安全儲存 JSON 檔案"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"  ✗ 儲存失敗：{e}")
        return False


def discover_blue_ocean_categories(client, site, keyword, max_categories=5):
    """
    【新增】藍海市場發現 - 使用 search_categories_broadly

    Args:
        client: SorftimeClient 例項
        site: 站點
        keyword: 產品關鍵詞（用於篩選相關類目）
        max_categories: 返回的類目數量

    Returns:
        list: 符合條件的類目列表
    """
    print("\n[Step 0.5] 藍海市場發現...")

    # 篩選條件：適合新賣家的藍海市場
    filters = {
        # 低集中度
        "top3Product_sales_share": 0.4,  # Top3 產品銷量佔比 < 40%
        "top3Brands_sales_share": 0.5,   # Top3 品牌銷量佔比 < 50%
        # 新品活躍
        "newProductSalesAmountShare": 0.15,  # 新品銷量佔比 > 15%
        # 市場分散
        "brandCount": 50,  # 品牌數量 > 50
        # 價格適中
        "priceRange_min": 10,
        "priceRange_max": 50,
        # 有一定規模
        "monthlySales_min": 5000,
    }

    try:
        result, _ = client.search_categories_broadly(site, filters)

        if result and isinstance(result, dict):
            categories = result.get('categories', [])

            # 過濾與關鍵詞相關的類目
            if keyword:
                keyword_lower = keyword.lower()
                related_categories = []
                for cat in categories:
                    cat_name = cat.get('categoryName', '').lower()
                    if keyword_lower in cat_name or keyword_lower in cat.get('description', '').lower():
                        related_categories.append(cat)

                categories = related_categories[:max_categories]
            else:
                categories = categories[:max_categories]

            print(f"  ✓ 發現 {len(categories)} 個潛力類目:")
            for i, cat in enumerate(categories, 1):
                print(f"    {i}. {cat.get('categoryName', 'N/A')} "
                      f"(新品佔比：{cat.get('newProductSalesAmountShare', 0)*100:.1f}%, "
                      f"Top3 佔比：{cat.get('top3Product_sales_share', 0)*100:.1f}%)")

            return categories
        else:
            print(f"  ⚠ 未找到符合條件的類目")
            return []

    except Exception as e:
        print(f"  ⚠ 藍海發現失敗：{e} (非關鍵，繼續執行)")
        return []


def find_potential_products(client, site, keyword, max_products=20):
    """
    【新增】潛力產品發現 - 使用 potential_product

    Args:
        client: SorftimeClient 例項
        site: 站點
        keyword: 產品關鍵詞
        max_products: 返回的產品數量

    Returns:
        list: 潛力產品列表
    """
    print(f"\n[Step 1.3] 潛力產品發現：{keyword}...")

    # 篩選條件：有潛力的新品
    filters = {
        "monthlySales_min": 500,    # 月銷量 > 500
        "price_min": 10,            # 價格 > $10
        "price_max": 50,            # 價格 < $50
        "rating_min": 4.0,          # 評分 > 4.0
        "daysOnMarket_max": 180,    # 上架時間 < 6 個月
    }

    try:
        result, _ = client.get_potential_products(site, keyword, **filters)

        if result and isinstance(result, dict):
            products = result.get('products', []) or result.get('productList', [])

            if not products:
                # 嘗試不同的返回格式
                products = result.get('list', [])

            print(f"  ✓ 發現 {len(products)} 個潛力產品")

            # 顯示 Top 5
            for i, p in enumerate(products[:5], 1):
                asin = p.get('ASIN', 'N/A')
                brand = p.get('品牌', 'N/A')
                sales = p.get('月銷量', 'N/A')
                price = p.get('價格', 'N/A')
                rating = p.get('星級', 'N/A')
                days = p.get('上線天數', 'N/A')
                print(f"    {i}. {asin} | {brand} | 月銷{sales} | ${price} | {rating}星 | {days}天")

            return products[:max_products]
        else:
            print(f"  ⚠ 未找到潛力產品")
            return []

    except Exception as e:
        print(f"  ⚠ 潛力產品發現失敗：{e} (非關鍵，繼續執行)")
        return []


def get_keyword_extends_data(client, site, keyword):
    """
    【新增】獲取關鍵詞延伸詞 - 用於維度發現

    Args:
        client: SorftimeClient 例項
        site: 站點
        keyword: 關鍵詞

    Returns:
        dict: 延伸詞資料
    """
    print(f"\n[Step 1.4] 獲取關鍵詞延伸詞：{keyword}...")

    try:
        result, _ = client.get_keyword_extends(site, keyword)

        if result:
            # 解析延伸詞
            extends = result.get('extends', []) or result.get('keywords', []) or result.get('list', [])

            if isinstance(extends, list) and len(extends) > 0:
                print(f"  ✓ 獲取 {len(extends)} 個延伸詞")

                # 提取高頻修飾詞（用於維度發現）
                modifiers = []
                for item in extends:
                    if isinstance(item, dict):
                        word = item.get('keyword', item.get('word', ''))
                        search_volume = item.get('searchVolume', item.get('monthly_search', 0))
                    else:
                        word = str(item)
                        search_volume = 0

                    # 過濾掉品類通用詞
                    if word and keyword.lower() not in word.lower():
                        modifiers.append({
                            'word': word,
                            'search_volume': search_volume
                        })

                # 按搜尋量排序
                modifiers.sort(key=lambda x: x['search_volume'], reverse=True)

                print(f"  ✓ 提取 {len(modifiers)} 個修飾詞（用於維度發現）")
                if modifiers:
                    print(f"    Top 5 修飾詞：{', '.join([m['word'] for m in modifiers[:5]])}")

                return {
                    'extends': extends,
                    'modifiers': modifiers[:20]  # 保留 Top 20
                }

        print(f"  ⚠ 延伸詞資料為空")
        return {}

    except Exception as e:
        print(f"  ⚠ 延伸詞獲取失敗：{e} (非關鍵，繼續執行)")
        return {}


def collect_data(keyword, site='US', max_keywords=3, use_blue_ocean=False):
    """
    執行完整的資料採集流程

    Args:
        keyword: 產品/類目關鍵詞
        site: 站點程式碼 (US, GB, DE, etc.)
        max_keywords: 採集關鍵詞數量
        use_blue_ocean: 是否啟用藍海發現模式

    Returns:
        dict: 採集結果摘要
    """
    print(f"🔍 選品資料採集：{keyword} ({site})")
    print("=" * 60)

    # 初始化
    client = SorftimeClient()
    output_dir, raw_dir, date_str = create_output_dir(keyword, site)

    # 結果摘要
    result = {
        'keyword': keyword,
        'site': site,
        'date': date_str,
        'category_name': None,
        'node_id': None,
        'steps_completed': [],
        'errors': [],
        'blue_ocean_categories': [],
        'potential_products': [],
        'keyword_extends': {}
    }

    # ========== Step 0.5: 藍海市場發現（可選） ==========
    if use_blue_ocean:
        blue_ocean_cats = discover_blue_ocean_categories(client, site, keyword)
        if blue_ocean_cats:
            result['blue_ocean_categories'] = blue_ocean_cats
            save_json(blue_ocean_cats, os.path.join(raw_dir, 'blue_ocean_categories.json'))
            result['steps_completed'].append('blue_ocean_discovery')

    # ========== Step 1: 搜尋類目 ==========
    print("\n[Step 1] 搜尋類目...")

    category_result = None
    used_keyword = keyword

    try:
        print(f"  搜尋: '{keyword}'...", end=' ')
        category_result, raw = client.search_category_by_product_name(site, keyword)

        if category_result and isinstance(category_result, list) and len(category_result) > 0:
            print(f"✓ 找到 {len(category_result)} 個類目")
        else:
            error_msg = f"類目搜尋失敗：未找到與 '{keyword}' 匹配的類目。請使用該類別最通用的核心名詞（如使用 'camera' 而非 'digital wireless camera'）"
            print(f"  ✗ {error_msg}")
            raise Exception(error_msg)
    except Exception as e:
        print(f"  ✗ 錯誤: {str(e)}")
        raise

    # 使用找到的類目
    first_cat = category_result[0]
    node_id = first_cat.get('nodeId') or first_cat.get('NodeId')
    category_name = first_cat.get('categoryName') or first_cat.get('Name')

    result['category_name'] = category_name
    result['node_id'] = str(node_id)
    result['searched_keyword'] = used_keyword  # 記錄實際使用的搜尋詞

    print(f"  ✓ 最終類目：{category_name}")
    print(f"  ✓ Node ID: {node_id}")
    if used_keyword != keyword:
        print(f"  ℹ 使用搜尋詞: '{used_keyword}' (原詞: '{keyword}')")

    save_json(category_result, os.path.join(raw_dir, 'category_info.json'))
    result['steps_completed'].append('category_search')

    # ========== Step 2: 獲取 Top100 ==========
    print(f"\n[Step 2] 獲取 Top100 產品資料...")
    top100 = None
    try:
        top100, raw_response = client.get_category_report(site, result['node_id'])

        # 檢查返回的資料是否有效
        if top100 is None or not isinstance(top100, dict) or len(top100) == 0:
            raise ValueError("category_report 返回無效資料")

        products = top100.get('Top100產品', []) or top100.get('Top100 產品', []) or top100.get('products', [])
        stats = top100.get('類目統計報告', {})

        print(f"  ✓ 產品數量：{len(products)}")
        if stats:
            monthly_revenue = stats.get('top100 產品月銷額', 0)
            print(f"  ✓ 類目月銷額：${monthly_revenue}")

        save_json(top100, os.path.join(raw_dir, 'top100.json'))
        result['steps_completed'].append('top100')

    except Exception as e:
        # category_report 不可用時，使用 product_search 作為替代
        print(f"  ⚠ category_report 不可用，嘗試使用 product_search 替代...")
        try:
            # 使用 product_search 工具獲取產品資料
            search_result, _ = client._call('product_search', {
                'amzSite': site,
                'searchName': keyword,
                'page': 1
            })

            if isinstance(search_result, list) and len(search_result) > 0:
                # 構造類似 top100 的資料結構
                products = search_result

                # 計算類目統計資料
                total_monthly_sales = sum(p.get('月銷量', 0) for p in products)
                total_monthly_revenue = sum(p.get('月銷額', 0) for p in products)
                avg_price = total_monthly_revenue / len(products) if products else 0

                top100_data = {
                    'Top100產品': products,
                    '類目統計報告': {
                        'top100 產品月銷額': total_monthly_revenue,
                        'top100 產品月銷量': total_monthly_sales,
                        '平均價格': avg_price,
                        '產品數量': len(products),
                        '資料來源': 'product_search (替代 category_report)'
                    }
                }

                print(f"  ✓ 產品數量：{len(products)}")
                print(f"  ✓ 類目月銷額：${total_monthly_revenue:,.2f}")
                print(f"  ℹ 注意：使用 product_search 資料（非完整 Top100）")

                save_json(top100_data, os.path.join(raw_dir, 'top100.json'))
                result['steps_completed'].append('top100')
            else:
                error_msg = f"product_search 返回空資料"
                print(f"  ✗ {error_msg}")
                result['errors'].append(error_msg)

        except Exception as e2:
            error_msg = f"Top100 獲取失敗（category_report 和 product_search 都失敗）：{e}, {e2}"
            print(f"  ✗ {error_msg}")
            result['errors'].append(error_msg)

    # ========== Step 3: 獲取趨勢資料 ==========
    print(f"\n[Step 3] 獲取類目趨勢...")
    try:
        trend = client.get_category_trend(site, result['node_id'])
        if trend:
            print(f"  ✓ 趨勢資料已獲取")
            save_json(trend, os.path.join(raw_dir, 'trend.json'))
            result['steps_completed'].append('trend')
        else:
            print(f"  ⚠ 趨勢資料為空（非關鍵）")
    except Exception as e:
        error_msg = f"趨勢獲取失敗：{e}"
        print(f"  ⚠ {error_msg} (非關鍵)")
        result['errors'].append(error_msg)

    # ========== Step 4: 獲取關鍵詞詳情（通用關鍵詞生成） ==========
    print(f"\n[Step 4] 獲取關鍵詞詳情...")
    keywords_data = {}

    def generate_keyword_variants(base_kw, max_count=5):
        """
        通用關鍵詞變體生成策略

        策略：
        1. 原始詞
        2. 嘗試生成複數形式
        3. 新增常見修飾字首
        """
        variants = [base_kw]

        # 複數形式生成（通用規則）
        # 規則1: 新增 's'
        if not base_kw.endswith('s'):
            variants.append(base_kw + 's')
        # 規則2: 以 y 結尾，變 'ies'
        if base_kw.endswith('y') and len(base_kw) > 1:
            variants.append(base_kw[:-1] + 'ies')
        # 規則3: 以 s, x, ch, sh 結尾，新增 'es'
        if base_kw.endswith(('s', 'x', 'ch', 'sh')):
            variants.append(base_kw + 'es')

        # 新增常見修飾字首（完全通用）
        common_prefixes = ['portable', 'wireless', 'digital', 'smart']
        for prefix in common_prefixes:
            variants.append(f"{prefix} {base_kw}")

        # 去重並限制數量
        seen = set()
        unique_variants = []
        for v in variants:
            v_lower = v.lower().strip()
            if v_lower and v_lower not in seen and len(unique_variants) < max_count:
                seen.add(v_lower)
                unique_variants.append(v)

        return unique_variants

    base_keywords = generate_keyword_variants(keyword, max_keywords)

    for kw in base_keywords:
        try:
            print(f"  - {kw}...", end=' ', flush=True)
            kw_data, _ = client.get_keyword_detail(site, kw)
            if kw_data:
                keywords_data[kw] = kw_data
                print("✓")
            else:
                print("✗ (空響應)")
        except Exception as e:
            print(f"✗ ({str(e)[:50]})")

    if keywords_data:
        save_json(keywords_data, os.path.join(raw_dir, 'keywords.json'))
        result['steps_completed'].append('keywords')
        print(f"  ✓ 成功：{len(keywords_data)}/{len(base_keywords)} 個關鍵詞")

    # ========== Step 5: 獲取關鍵詞延伸詞（新增） ==========
    extends_data = get_keyword_extends_data(client, site, keyword)
    if extends_data:
        result['keyword_extends'] = extends_data
        save_json(extends_data, os.path.join(raw_dir, 'keyword_extends.json'))
        result['steps_completed'].append('keyword_extends')

    # ========== Step 6: 發現潛力產品（新增） ==========
    potential_products = find_potential_products(client, site, keyword)
    if potential_products:
        result['potential_products'] = potential_products
        save_json(potential_products, os.path.join(raw_dir, 'potential_products.json'))
        result['steps_completed'].append('potential_products')

    # ========== Step 7: 儲存彙總資料 ==========
    print(f"\n[Step 7] 儲存彙總資料...")

    summary = {
        "metadata": {
            "keyword": keyword,
            "site": site,
            "date": date_str,
            "node_id": result['node_id'],
            "category_name": result['category_name'],
            "collected_at": datetime.now().isoformat()
        },
        "files": {
            "category_info": "raw/category_info.json",
            "top100": "raw/top100.json",
            "trend": "raw/trend.json",
            "keywords": "raw/keywords.json",
            "keyword_extends": "raw/keyword_extends.json" if extends_data else None,
            "potential_products": "raw/potential_products.json" if potential_products else None,
            "blue_ocean_categories": "raw/blue_ocean_categories.json" if result['blue_ocean_categories'] else None
        },
        "status": "success" if len(result['errors']) == 0 else "partial",
        "steps_completed": result['steps_completed'],
        "errors": result['errors'],
        # 預留 Dashboard 需要的資料結構（初始為空，由後續分析填充）
        "market_overview": {},
        "price_ranges": [],
        "product_types": [],
        "cross_analysis": {"price_type_matrix": []},
        "top_brands": [],
        "competitors": [],
        "voc_analysis": {"dimensions": [], "summary": ""},
        "barriers": [],
        "decision": {},
        "trend_data": [],
        "keywords": {}
    }

    save_json(summary, os.path.join(output_dir, 'data.json'))

    # ========== 完成 ==========
    print("\n" + "=" * 60)
    print(f"✓ 資料採集完成!")
    print(f"  輸出目錄：{output_dir}")
    print(f"  完成步驟：{', '.join(result['steps_completed'])}")

    if result['errors']:
        print(f"\n⚠ 錯誤 ({len(result['errors'])}):")
        for err in result['errors']:
            print(f"  - {err}")

    print("=" * 60)

    return result


# ============================================================================
# 命令列介面
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="product-research 資料採集指令碼（通用版本）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python collect_data.py "speaker" US
  python collect_data.py "sofa" DE --keywords 5
  python collect_data.py "mat" US --blue-ocean  # 啟用藍海發現
        """
    )

    parser.add_argument('keyword', help='產品/類目關鍵詞')
    parser.add_argument('site', nargs='?', default='US', help='站點程式碼 (預設：US)')
    parser.add_argument('--keywords', '-k', type=int, default=3, help='採集關鍵詞數量 (預設：3)')
    parser.add_argument('--blue-ocean', action='store_true', help='啟用藍海發現模式')

    args = parser.parse_args()

    collect_data(args.keyword, args.site, args.keywords, use_blue_ocean=args.blue_ocean)
