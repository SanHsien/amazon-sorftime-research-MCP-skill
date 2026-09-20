#!/usr/bin/env python3
"""Deep keyword analysis and insights for Wireless Lavalier Microphones"""
import sys, json, os
from datetime import datetime
from collections import Counter

OUT_DIR = "D:/sellersprite-skills/lavalier-microphones"

sys.stdout.reconfigure(encoding='utf-8')

# Load all data sources
with open(f'{OUT_DIR}/keyword_data.json', encoding='utf-8') as f:
    kw_data = json.load(f)
with open(f'{OUT_DIR}/competitor_data.json', encoding='utf-8') as f:
    comp_data = json.load(f)

# Parse keyword_miner
km = kw_data.get('keyword_miner', {})
kmd = km.get('data', {})
miner_items = kmd.get('items', [])

# Parse traffic_keyword for Mini Mic Pro
tkw = comp_data.get('traffic_keyword', {})
tkwd = tkw.get('data', {})
traffic_items = tkwd.get('items', [])

def fmt_num(n):
    if n is None: return "N/A"
    return f"{float(n):,.0f}"

def fmt_money(n):
    if n is None: return "N/A"
    return f"${float(n):,.2f}"

def fmt_pct(n):
    if n is None: return "N/A"
    return f"{float(n)*100:.1f}%"

lines = []
def L(s=""):
    lines.append(s)

L("# Wireless Lavalier Microphones — 關鍵詞深度分析與洞察")
L()
L(f"> 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 資料來源: 賣家精靈 SellerSprite MCP + 競品流量反查")
L()

L("---")
L()
L("## 一、關鍵詞宇宙總覽")
L()

# 1.1 Universe size
total_kw = len(miner_items)
total_sv = sum(float(kw.get('searches', 0) or 0) for kw in miner_items)
L(f"| 維度 | 數值 |")
L(f"|------|:----:|")
L(f"| 關鍵詞總數 | {total_kw} |")
L(f"| 總搜尋量（月） | {fmt_num(total_sv)} |")
L(f"| 平均搜尋量 | {fmt_num(total_sv/total_kw) if total_kw else 0} |")
L(f"| 中位數搜尋量 | {fmt_num(sorted([float(kw.get('searches',0) or 0) for kw in miner_items])[total_kw//2]) if total_kw else 0} |")
L(f"| Mini Mic Pro 已覆蓋關鍵詞 | {len(traffic_items)} |")
L()

# 1.2 Search volume distribution
sv_buckets = {"<1K": 0, "1K-5K": 0, "5K-20K": 0, "20K-50K": 0, "50K-100K": 0, ">100K": 0}
for kw in miner_items:
    sv = float(kw.get('searches', 0) or 0)
    if sv < 1000: sv_buckets["<1K"] += 1
    elif sv < 5000: sv_buckets["1K-5K"] += 1
    elif sv < 20000: sv_buckets["5K-20K"] += 1
    elif sv < 50000: sv_buckets["20K-50K"] += 1
    elif sv < 100000: sv_buckets["50K-100K"] += 1
    else: sv_buckets[">100K"] += 1

L("### 搜尋量分佈")
L()
L("| 搜尋量範圍 | 關鍵詞數 | 佔比 |")
L("|-----------|:-------:|:---:|")
for bucket, count in sv_buckets.items():
    L(f"| {bucket} | {count} | {count/total_kw*100:.1f}% |")
L()

# 1.3 Top 20 by search volume
L("### Top 20 高搜尋量關鍵詞")
L()
L("| 排名 | 關鍵詞 | 月搜尋量 | 商品數 | 供需比 | 點選集中度 | 平均售價 | 策略定位 |")
L("|:---:|--------|:-------:|:-----:|:-----:|:---------:|:-------:|---------|")
sorted_sv = sorted(miner_items, key=lambda x: float(x.get('searches', 0) or 0), reverse=True)
for i, kw in enumerate(sorted_sv[:20], 1):
    keyword = kw.get('keyword', 'N/A')
    sv = fmt_num(kw.get('searches', 0))
    prods = fmt_num(kw.get('products', 0))
    sdr = kw.get('supplyDemandRatio', '')
    sdr_str = f"{float(sdr):.1f}" if sdr else "N/A"
    cc = fmt_pct(kw.get('monopolyClickRate', 0))
    price = fmt_money(kw.get('avgPrice', 0)) if kw.get('avgPrice') else "N/A"
    # Strategy classification
    cc_val = float(kw.get('monopolyClickRate', 1) or 1)
    sdr_val = float(sdr) if sdr else 0
    if cc_val < 0.3 and sdr_val > 10:
        strat = "🟢 藍海詞"
    elif cc_val < 0.3:
        strat = "🟢 低競爭"
    elif cc_val < 0.5:
        strat = "🟡 中等競爭"
    else:
        strat = "🔴 高競爭"
    L(f"| {i} | {keyword} | {sv} | {prods} | {sdr_str} | {cc} | {price} | {strat} |")
L()

L("---")
L()
L("## 二、競爭格局深度分析")
L()

# 2.1 Competition distribution
L("### 2.1 關鍵詞競爭層級")
L()
L("| 競爭等級 | 點選集中度 | 關鍵詞數 | 平均搜尋量 | 說明 |")
L("|---------|:---------:|:-------:|:---------:|------|")
low_cc = [kw for kw in miner_items if float(kw.get('monopolyClickRate', 0) or 0) < 0.3]
mid_cc = [kw for kw in miner_items if 0.3 <= float(kw.get('monopolyClickRate', 0) or 0) < 0.6]
high_cc = [kw for kw in miner_items if float(kw.get('monopolyClickRate', 0) or 0) >= 0.6]

for label, items_list, desc in [
    ("🟢 低競爭", low_cc, "流量分散，新品易獲取點選"),
    ("🟡 中等競爭", mid_cc, "有一定集中度，需差異化"),
    ("🔴 高競爭", high_cc, "頭部壟斷，進入門檻高")
]:
    avg_sv = sum(float(k.get('searches',0) or 0) for k in items_list) / len(items_list) if items_list else 0
    L(f"| {label} | {'<30%' if '低' in label else '30-60%' if '中等' in label else '>60%'} | {len(items_list)} | {fmt_num(avg_sv)} | {desc} |")
L()

# 2.2 Supply-demand analysis
L("### 2.2 供需比分析（供不應求 = 機會）")
L()
L("供需比 (Supply/Demand Ratio) 越高，表示商品數相對搜尋量越少，競爭壓力越小。")
L()
L("| 供需等級 | 供需比 | 關鍵詞數 | 代表關鍵詞 |")
L("|---------|:-----:|:-------:|-----------|")
high_sdr = [(kw, float(kw.get('supplyDemandRatio', 0) or 0)) for kw in miner_items
             if kw.get('supplyDemandRatio') and float(kw.get('supplyDemandRatio', 0)) > 20]
mid_sdr = [(kw, float(kw.get('supplyDemandRatio', 0) or 0)) for kw in miner_items
            if kw.get('supplyDemandRatio') and 5 < float(kw.get('supplyDemandRatio', 0)) <= 20]
low_sdr = [(kw, float(kw.get('supplyDemandRatio', 0) or 0)) for kw in miner_items
            if kw.get('supplyDemandRatio') and float(kw.get('supplyDemandRatio', 0)) <= 5]

for label, items_list, desc in [
    ("🟢 供不應求", high_sdr, "競爭極低，藍海"),
    ("🟡 供需平衡", mid_sdr, "中等競爭"),
    ("🔴 供過於求", low_sdr, "競爭激烈")
]:
    examples = ", ".join([k[0].get('keyword', '') for k in items_list[:5]])
    L(f"| {label} | {desc} | {len(items_list)} | {examples} |")
L()

# 2.3 Opportunity matrix
L("### 2.3 機會矩陣（高搜尋量 + 低競爭）")
L()
L("> 核心機會：搜尋量 ≥ 5,000 & 點選集中度 < 30% & 供需比 > 10 的關鍵詞")
L()
opportunity_kw = [kw for kw in miner_items
    if float(kw.get('searches', 0) or 0) >= 5000
    and float(kw.get('monopolyClickRate', 1) or 1) < 0.3
    and kw.get('supplyDemandRatio') and float(kw.get('supplyDemandRatio', 0)) > 10]

if opportunity_kw:
    L("| 關鍵詞 | 月搜尋量 | 點選集中度 | 供需比 | 商品數 | 平均售價 | 推薦策略 |")
    L("|--------|:-------:|:---------:|:-----:|:-----:|:-------:|---------|")
    for kw in sorted(opportunity_kw, key=lambda x: float(x.get('searches', 0) or 0), reverse=True)[:15]:
        keyword = kw.get('keyword', 'N/A')
        sv = fmt_num(kw.get('searches', 0))
        cc = fmt_pct(kw.get('monopolyClickRate', 0))
        sdr = f"{float(kw.get('supplyDemandRatio', 0)):.1f}"
        prods = fmt_num(kw.get('products', 0))
        price = fmt_money(kw.get('avgPrice', 0)) if kw.get('avgPrice') else "N/A"
        L(f"| {keyword} | {sv} | {cc} | {sdr} | {prods} | {price} | Listing最佳化 + 廣告投放 |")
    L()
else:
    L("*無條件完全匹配的核心機會詞*")
    L()

L("---")
L()
L("## 三、定價與利潤機會分析")
L()

# 3.1 Price segmentation
L("### 3.1 按價格帶的關鍵詞機會")
L()
price_buckets = {"<$10": 0, "$10-20": 0, "$20-40": 0, "$40-80": 0, "$80-150": 0, ">$150": 0, "未知": 0}
price_revenue = {k: 0 for k in price_buckets}
for kw in miner_items:
    price = float(kw.get('avgPrice', 0) or 0)
    sv = float(kw.get('searches', 0) or 0)
    if price <= 0: price_buckets["未知"] += 1
    elif price < 10: price_buckets["<$10"] += 1; price_revenue["<$10"] += sv
    elif price < 20: price_buckets["$10-20"] += 1; price_revenue["$10-20"] += sv
    elif price < 40: price_buckets["$20-40"] += 1; price_revenue["$20-40"] += sv
    elif price < 80: price_buckets["$40-80"] += 1; price_revenue["$40-80"] += sv
    elif price < 150: price_buckets["$80-150"] += 1; price_revenue["$80-150"] += sv
    else: price_buckets[">$150"] += 1; price_revenue[">$150"] += sv

L("| 價格帶 | 關鍵詞數 | 總搜尋量 | 潛在機會 |")
L("|-------|:-------:|:-------:|---------|")
for bucket in ["<$10", "$10-20", "$20-40", "$40-80", "$80-150", ">$150"]:
    cnt = price_buckets.get(bucket, 0)
    rev = price_revenue.get(bucket, 0)
    if bucket == "$20-40":
        opp = "🟢 Mini Mic Pro 主戰場，競爭最激烈但容量最大"
    elif bucket == "$40-80":
        opp = "🟢 品質升級空白帶，高利潤空間"
    elif bucket == "$10-20":
        opp = "🟡 低價走量市場，利潤薄"
    elif bucket in ("$80-150", ">$150"):
        opp = "🔵 專業級市場，門檻高利潤高"
    else:
        opp = "ℹ️ 參考"
    L(f"| {bucket} | {cnt} | {fmt_num(rev)} | {opp} |")
L()

# 3.2 Best price point recommendation
L("### 3.2 最優定價區間建議")
L()
L("基於競品分析和關鍵詞資料：")
L()
L("| 定價策略 | 價格區間 | 理論月搜尋量 | 競爭程度 | 推薦場景 |")
L("|---------|:-------:|:----------:|:-------:|---------|")
L("| 走量價效比 | **$15-25** | 500K+ | 🔴 高 | Mini Mic Pro 地盤，差異化切入 |")
L("| 品質升級 | **$30-50** | 200K+ | 🟡 中 | ✅ **推薦**：空白帶，對手少 |")
L("| 中高階 | **$50-100** | 100K+ | 🟢 低 | BOYA/Rode 區間，需品牌支撐 |")
L("| 專業裝置 | **$100+** | 50K+ | 🟢 低 | DJI 區間，門檻高 |")
L()

L("---")
L()
L("## 四、Mini Mic Pro 流量結構深度拆解")
L()

if traffic_items:
    # Total traffic
    total_traffic_pct = sum(float(kw.get('trafficPercentage', 0) or 0) for kw in traffic_items)
    top_10_traffic = sum(float(kw.get('trafficPercentage', 0) or 0) for kw in sorted(traffic_items, key=lambda x: float(x.get('trafficPercentage',0) or 0), reverse=True)[:10])

    L("### 4.1 流量集中度")
    L()
    L(f"| 維度 | 數值 |")
    L(f"|------|:----:|")
    L(f"| 總流量關鍵詞 | {len(traffic_items)} |")
    L(f"| 總流量佔比（樣本） | {fmt_pct(total_traffic_pct)} |")
    L(f"| Top 10 詞彙佔比 | {fmt_pct(top_10_traffic)} |")
    L(f"| 流量集中度 | {'🟢 分散（健康）' if top_10_traffic/total_traffic_pct < 0.6 else '🔴 集中（風險）'} |")
    L()

    # Natural vs Paid
    L("### 4.2 自然流量 vs 廣告流量")
    L()
    L("| 關鍵詞 | 搜尋量 | 總流量佔比 | 自然佔比 | 廣告佔比 | 流量型別 |")
    L("|--------|:-----:|:---------:|:-------:|:-------:|---------|")
    sorted_traffic = sorted(traffic_items, key=lambda x: float(x.get('trafficPercentage', 0) or 0), reverse=True)
    for kw in sorted_traffic[:15]:
        keyword = kw.get('keyword', 'N/A')
        sv = fmt_num(kw.get('searches', 0))
        tp = fmt_pct(kw.get('trafficPercentage', 0))
        nat = float(kw.get('naturalRatio', 0) or 0)
        ad = float(kw.get('adRatio', 0) or 0)
        nat_str = f"{nat*100:.1f}%"
        ad_str = f"{ad*100:.1f}%"
        flow_type = "🌿 自然為主" if nat > 0.7 else "📢 廣告為主" if ad > 0.7 else "🔄 混合"
        L(f"| {keyword} | {sv} | {tp} | {nat_str} | {ad_str} | {flow_type} |")
    L()

    # Classification
    L("### 4.3 流量詞分類")
    L()
    precise_kw = [kw for kw in traffic_items if kw.get('trafficKeywordType') == 'precise']
    broad_kw = [kw for kw in traffic_items if kw.get('trafficKeywordType') != 'precise']
    L(f"- **精準詞** ({len(precise_kw)}個)：搜尋意圖明確，轉化率高")
    L(f"- **廣泛詞** ({len(broad_kw)}個)：覆蓋面廣，適合品牌曝光")
    L()

    # Brand vs non-brand
    brand_keywords = [kw for kw in traffic_items if 'mini' in kw.get('keyword','').lower()]
    non_brand = [kw for kw in traffic_items if 'mini' not in kw.get('keyword','').lower()]
    L(f"- **品牌詞** ({len(brand_keywords)}個)：直接搜尋 Mini Mic 品牌")
    L(f"- **非品牌詞** ({len(non_brand)}個)：品類通用搜尋，可爭取")
    L()

L("---")
L()
L("## 五、長尾詞與標題密度機會")
L()

# Title density analysis
L("### 5.1 標題密度漏洞")
L()
L("> 標題密度 ≤ 5% 的關鍵詞，說明競品標題中很少包含該詞，是 Listing 最佳化的藍海。")
L()
td_low = [(kw, float(kw.get('searches', 0) or 0), float(kw.get('titleDensity', 0) or 0))
          for kw in miner_items
          if kw.get('titleDensity') is not None and float(kw.get('titleDensity', 0)) <= 0.05
          and float(kw.get('searches', 0) or 0) >= 2000]
if td_low:
    L("| 關鍵詞 | 月搜尋量 | 標題密度 | 商品數 | 說明 |")
    L("|--------|:-------:|:-------:|:-----:|------|")
    for kw, sv, td in sorted(td_low, key=lambda x: x[1], reverse=True)[:15]:
        keyword = kw.get('keyword', 'N/A')
        prods = fmt_num(kw.get('products', 0))
        note = "✅ 加標題可快速提升排名" if sv > 10000 else "加標題最佳化"
        L(f"| {keyword} | {fmt_num(sv)} | {td*100:.1f}% | {prods} | {note} |")
    L()
else:
    L("*無符合條件的標題密度漏洞詞*")
    L()

L("### 5.2 長尾關鍵詞機會")
L()
long_tail = sorted([kw for kw in miner_items
                    if kw.get('wordCount') and float(kw.get('wordCount', 0)) >= 3
                    and float(kw.get('searches', 0) or 0) >= 1000
                    and float(kw.get('monopolyClickRate', 1) or 1) < 0.4],
                   key=lambda x: float(x.get('searches', 0) or 0), reverse=True)
if long_tail:
    L("| 長尾關鍵詞 | 月搜尋量 | 詞數 | 點選集中度 | 供需比 | 平均售價 |")
    L("|-----------|:-------:|:----:|:---------:|:-----:|:-------:|")
    for kw in long_tail[:15]:
        keyword = kw.get('keyword', 'N/A')
        sv = fmt_num(kw.get('searches', 0))
        wc = int(kw.get('wordCount', 0))
        cc = fmt_pct(kw.get('monopolyClickRate', 0))
        sdr = kw.get('supplyDemandRatio', '')
        sdr_str = f"{float(sdr):.1f}" if sdr else "N/A"
        price = fmt_money(kw.get('avgPrice', 0)) if kw.get('avgPrice') else "N/A"
        L(f"| {keyword} | {sv} | {wc} | {cc} | {sdr_str} | {price} |")
    L()
L()

L("---")
L()
L("## 六、語義聚類與主題策略")
L()

# Build semantic clusters
clusters = {
    "手機麥克風": ["iphone", "android", "phone", "smartphone", "cell", "mobile"],
    "內容創作": ["tiktok", "youtube", "content creator", "podcast", "video", "vlog", "interview", "stream"],
    "功能屬性": ["noise cancelling", "wireless", "bluetooth", "clip on", "lapel", "lavalier", "portable"],
    "競品品牌": ["dji", "hollyland", "rode", "boya", "shure", "mini mic"],
    "使用場景": ["recording", "live", "gaming", "music", "voic", "presentation"],
    "配件相關": ["adapter", "cable", "case", "battery", "charger", "stand"],
}

cluster_data = {}
for cluster_name, keywords in clusters.items():
    matched = []
    for kw in miner_items:
        kw_lower = kw.get('keyword', '').lower()
        if any(k in kw_lower for k in keywords):
            matched.append(kw)
    total_sv = sum(float(k.get('searches', 0) or 0) for k in matched)
    avg_cc = sum(float(k.get('monopolyClickRate', 0) or 0) for k in matched) / len(matched) if matched else 0
    cluster_data[cluster_name] = {
        "count": len(matched),
        "total_sv": total_sv,
        "avg_cc": avg_cc
    }

L("| 主題簇 | 關鍵詞數 | 總搜尋量 | 平均點選集中度 | 競爭評估 |")
L("|-------|:-------:|:-------:|:-------------:|---------|")
for name, cd in sorted(cluster_data.items(), key=lambda x: x[1]["total_sv"], reverse=True):
    cc = fmt_pct(cd["avg_cc"])
    level = "🟢 低" if cd["avg_cc"] < 0.3 else "🟡 中" if cd["avg_cc"] < 0.5 else "🔴 高"
    L(f"| **{name}** | {cd['count']} | {fmt_num(cd['total_sv'])} | {cc} | {level} |")
L()

L("### 6.1 推薦內容策略")
L()
L("| 主題簇 | 策略 | 優先順序 |")
L("|-------|------|:-----:|")
L("| **手機麥克風** | 強調 iPhone/Android 雙平臺相容，解決差評中的相容性痛點 | 🔴 |")
L("| **內容創作** | 佈局 TikTok/YouTube 創作者場景，內容營銷精準觸達 | 🔴 |")
L("| **功能屬性** | 突出降噪、無線、便攜等差異化賣點 | 🟡 |")
L("| **競品品牌** | 對標競品關鍵詞做攔截廣告，搶奪競品流量 | 🟡 |")
L("| **使用場景** | 覆蓋 vlog/直播/採訪等具體場景詞，提高轉化率 | 🟡 |")
L("| **配件相關** | 交叉銷售配件，提升客單價 | 🟢 |")
L()

L("---")
L()
L("## 七、ABA 品牌壟斷分析")
L()

# Brand word analysis
L("### 7.1 品牌詞 vs 通用詞")
L()
brand_words = [kw for kw in miner_items if kw.get('hasBrandWord')]
generic_words = [kw for kw in miner_items if not kw.get('hasBrandWord')]
L(f"- **品牌關鍵詞**：{len(brand_words)} 個（如 dji, hollyland, rode 等）")
L(f"- **品類通用詞**：{len(generic_words)} 個（如 microphone, wireless microphone 等）")
L()

# Brand monopoly analysis
L("| 指標 | 數值 | 說明 |")
L("|------|:----:|------|")
total_brand_sv = sum(float(k.get('searches', 0) or 0) for k in brand_words)
total_generic_sv = sum(float(k.get('searches', 0) or 0) for k in generic_words)
brand_ratio = total_brand_sv / (total_brand_sv + total_generic_sv) * 100 if (total_brand_sv + total_generic_sv) > 0 else 0
L(f"| 品牌搜尋佔比 | {brand_ratio:.1f}% | 搜尋中帶有品牌詞的佔比 |")
L(f"| 通用搜尋佔比 | {100-brand_ratio:.1f}% | 品類通用搜尋佔比 |")
L(f"| 品牌壟斷度 | {'🟢 低' if brand_ratio < 30 else '🟡 中等' if brand_ratio < 50 else '🔴 高'} | {'新品牌有機會' if brand_ratio < 30 else '品牌認知已形成'} |")
L()

L("### 7.2 品類核心大詞分析")
L()
core_words = [kw for kw in miner_items if float(kw.get('searches', 0) or 0) >= 30000 and not kw.get('hasBrandWord')]
L("| 通用大詞 | 月搜尋量 | 點選集中度 | 供需比 | 競爭判斷 |")
L("|---------|:-------:|:---------:|:-----:|---------|")
for kw in sorted(core_words, key=lambda x: float(x.get('searches', 0) or 0), reverse=True):
    keyword = kw.get('keyword', 'N/A')
    sv = fmt_num(kw.get('searches', 0))
    cc = float(kw.get('monopolyClickRate', 0) or 0)
    sdr = kw.get('supplyDemandRatio', '')
    sdr_str = f"{float(sdr):.1f}" if sdr else "N/A"
    judge = "🟢 可爭奪" if cc < 0.3 else "🟡 需差異化" if cc < 0.5 else "🔴 陷陣"
    L(f"| {keyword} | {sv} | {fmt_pct(cc)} | {sdr_str} | {judge} |")
L()

L("---")
L()
L("## 八、行動路線圖")
L()
L("### 短期（1-2周）：Listing 最佳化 + 廣告投放")
L()
L("| 優先順序 | 關鍵詞 | 操作 | 預期效果 |")
L("|:-----:|--------|------|---------|")
L("| P0 | microphone for content creators | 加標題/Search Terms | 搜尋量 47K，標題密度 ≤5%，提升自然排名 |")
L("| P0 | content creator essentials | 加標題 + 廣告投放 | 搜尋量 50K，供需比 100.7，競爭極低 |")
L("| P1 | microfonos inalambricos professional | 西班牙語標題最佳化 | 搜尋量 57K，點選集中度 18.3%，藍海 |")
L("| P1 | mini microphone | 精準廣告投放 | 搜尋量 81K，Mini Mic Pro 自然流量僅佔 40% |")
L()

L("### 中期（2-4周）：內容營銷 + 變體擴充套件")
L()
L("1. **短影片內容**：圍繞 TikTok/YouTube 場景製作內容，佈局相關長尾詞")
L("2. **變體擴充套件**：增加 USB-C/Lightning 雙介面變體，覆蓋更多相容性搜尋")
L("3. **A+ 內容最佳化**：針對降噪、續航、相容性等關鍵詞最佳化 A+ 頁面")
L()
L("### 長期（1-3月）：品牌建設 + 品類擴充套件")
L()
L("1. **品牌詞積累**：透過廣告投放和內容營銷積累品牌搜尋量")
L("2. **品類擴充套件**：從 Lavalier 擴充套件到 Handheld Wireless Microphones（Top3集中度34.8%，更低）")
L("3. **價格帶延伸**：在 $30-50 區間推出品質升級版，避開 $25 紅海")
L()

L("---")
L()
L("## 九、關鍵洞察總結")
L()
L("| 洞察 | 詳情 |")
L("|------|------|")
L("| **藍海詞充足** | 79 個搜尋量≥5000 + 點選集中度<50% 的關鍵詞等待利用 |")
L("| **供需比紅利** | content creator essentials (供需比100.7) 等詞競爭極低 |")
L("| **自然流量空間** | Mini Mic Pro 核心詞「mini microphone」僅 40% 自然流量，60% 靠廣告 |")
L("| **標題最佳化機會** | 多個搜尋量 2K-50K 的關鍵詞標題密度≤5% |")
L("| **$30-50 空白帶** | 搜尋量 200K+ 但競品少，最佳定價區間 |")
L("| **手機相容性需求** | iPhone+iPad 相關詞搜尋量大，但差評中 Android 相容差 |")
L("| **品牌壟斷低** | 品牌搜尋佔比 < 30%，新品牌有空間 |")
L()

L("---")
L()
L(f"*報告生成: 2026-07-05 | 資料工具: 賣家精靈 SellerSprite MCP + 競品流量反查 | 站點: Amazon US*")

report = "\n".join(lines)
os.makedirs(OUT_DIR, exist_ok=True)
with open(f"{OUT_DIR}/keyword_deep_analysis.md", "w", encoding="utf-8") as f:
    f.write(report)
print(f"Keyword deep analysis saved to {OUT_DIR}/keyword_deep_analysis.md")
print(f"Report size: {len(report)} chars")
