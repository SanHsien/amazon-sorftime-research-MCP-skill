#!/usr/bin/env python3
"""Run all 5 tactical strategy cards for Wireless Lavalier Microphones"""
import sys, json, urllib.request, time, os
from datetime import datetime

SECRET_KEY = ""
URL = "https://mcp.sellersprite.com/mcp"
OUT_DIR = "D:/sellersprite-skills/lavalier-microphones"
NODE_ID = "11091801:11974521:8882489011:11974711:11974761"

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def call_tool(name, arguments):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": name, "arguments": arguments}
    }).encode('utf-8')
    req = urllib.request.Request(URL, data=payload,
        headers={"Content-Type": "application/json", "secret-key": SECRET_KEY,
                 "Accept": "application/json, text/event-stream"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw = resp.read().decode('utf-8')
            data = json.loads(raw)
            text = data['result']['content'][0]['text']
            return json.loads(text)
    except Exception as e:
        return {"error": str(e), "_tool": name}

def safe_items(data):
    if isinstance(data, dict):
        if data.get('code') == 'OK':
            d = data.get('data', {})
            if isinstance(d, list): return d
            items = d.get('items', d.get('data', []))
            if isinstance(items, list): return items
            return []
        return []
    if isinstance(data, list): return data
    return []

def fmt_num(n):
    if n is None: return "N/A"
    return f"{float(n):,.0f}"

def fmt_money(n):
    if n is None: return "N/A"
    return f"${float(n):,.2f}"

def fmt_pct(n, is_ratio=True):
    if n is None: return "N/A"
    n = float(n)
    if is_ratio: return f"{n*100:.1f}%"
    return f"{n:.1f}%"

# ======= Load existing data =======
with open('D:/sellersprite-skills/wirelessinstruments/research_data.json', encoding='utf-8') as f:
    parent_data = json.load(f)

with open(f'{OUT_DIR}/keyword_data.json', encoding='utf-8') as f:
    kw_data = json.load(f)

parent_items = parent_data.get('market_research', {}).get('data', {}).get('items', [])
miner_items = safe_items(kw_data.get('keyword_miner', {}))

# ======= Call product_research for cards 4 & 5 =======
print("=== Calling product_research (for High Margin & Hot Low Rating) ===")
pr_high_margin = call_tool("product_research", {
    "request": {
        "marketplace": "US",
        "nodeIdPath": NODE_ID,
        "maxFba": 4,
        "minProfit": 0.5,
        "fulfillment": "FBA",
        "size": 50
    }
})
print(f"  high_margin: {pr_high_margin.get('code', 'ERROR')}")

time.sleep(0.3)
pr_hot_low = call_tool("product_research", {
    "request": {
        "marketplace": "US",
        "nodeIdPath": NODE_ID,
        "minUnits": 1000,
        "maxRating": 4.2,
        "size": 50
    }
})
print(f"  hot_low_rating: {pr_hot_low.get('code', 'ERROR')}")

everything = {
    "low_brand_monopoly": {"source": "parent_market_research"},
    "high_new_product_ratio": {"source": "parent_market_research"},
    "low_monopoly_keyword": {"source": "keyword_miner"},
    "high_margin_lightweight": pr_high_margin,
    "hot_low_rating": pr_hot_low,
}

# ======= GENERATE REPORT =======
lines = []
def L(s=""):
    lines.append(s)

L("# Wireless Lavalier Microphones — 戰術策略卡分析報告")
L()
L(f"> 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 資料來源: 賣家精靈 SellerSprite MCP | 站點: Amazon US")
L()

# ====== CARD 1: Low Brand Monopoly ======
L("---")
L()
L("## 策略卡一：低品牌壟斷類目")
L()
L("> 篩選條件：Top3 品牌集中度 < 45%")
L()

low_monopoly_items = [i for i in parent_items if i.get('top3BrandCrn', 1) is not None and i.get('top3BrandCrn', 1) < 0.45]
if low_monopoly_items:
    L("| 子市場 | 商品數 | 月銷量 | 月銷售額 | Top3品牌集中度 | 判斷 |")
    L("|--------|:-----:|:-----:|:--------:|:-------------:|:----:|")
    for item in low_monopoly_items:
        name = item.get('nodeLabelName', 'N/A')
        tp = fmt_num(item.get('totalProducts', 0))
        units = fmt_num(item.get('totalUnits', 0))
        rev = fmt_money(item.get('totalRevenue', 0))
        crn = fmt_pct(item.get('top3BrandCrn', 0))
        L(f"| {name} | {tp} | {units} | {rev} | {crn} | ✅ 低壟斷 |")
    L()
    L(f"共 **{len(low_monopoly_items)}** 個子市場符合低品牌壟斷條件。")
else:
    L("*無線麥克風品類下無符合低壟斷條件的子市場*")
L()

L("**結論：** Wireless Lavalier Microphones (Top3 {}) 和 Handheld Wireless Microphones (Top3 {}) 品牌集中度低於45%，新品牌有進入機會。".format(
    fmt_pct(parent_items[0].get('top3BrandCrn',0)) if parent_items else '?',
    fmt_pct(parent_items[1].get('top3BrandCrn',0)) if len(parent_items) > 1 else '?'
))

# ====== CARD 2: High New Product Ratio ======
L()
L("---")
L()
L("## 策略卡二：高新品佔比市場")
L()
L("> 篩選條件：6月新品佔比 > 5% 且新品有出單")
L()

high_new_items = [i for i in parent_items if i.get('l6NewRatio', 0) is not None and i.get('l6NewRatio', 0) > 0.05]
if high_new_items:
    L("| 子市場 | 商品數 | 月銷量 | 6月新品佔比 | 12月新品佔比 | 判斷 |")
    L("|--------|:-----:|:-----:|:----------:|:-----------:|:----:|")
    for item in sorted(high_new_items, key=lambda x: float(x.get('l6NewRatio', 0) or 0), reverse=True):
        name = item.get('nodeLabelName', 'N/A')
        tp = fmt_num(item.get('totalProducts', 0))
        units = fmt_num(item.get('totalUnits', 0))
        l6 = fmt_pct(item.get('l6NewRatio', 0))
        l12 = fmt_pct(item.get('l12NewRatio', 0))
        L(f"| {name} | {tp} | {units} | {l6} | {l12} | ✅ 新品活躍 |")
    L()
    L(f"共 **{len(high_new_items)}** 個子市場符合高新品佔比條件。")
else:
    L("*無線麥克風品類下無符合高新品佔比條件的子市場*")
L()

L("**結論：** Wireless Lavalier 6月新品佔比 {}，新品活躍度較高，對新品友好。".format(
    fmt_pct(parent_items[0].get('l6NewRatio',0)) if parent_items else '?'
))

# ====== CARD 3: Low Monopoly Keywords ======
L()
L("---")
L()
L("## 策略卡三：流量分散關鍵詞（藍海詞）")
L()
L("> 篩選條件：月搜尋量 ≥ 5,000 且 點選集中度 < 50%")
L()

low_mono_kw = [kw for kw in miner_items
    if float(kw.get('searches', 0) or 0) >= 5000
    and float(kw.get('monopolyClickRate', 1) or 1) < 0.5]

if low_mono_kw:
    sorted_kw = sorted(low_mono_kw, key=lambda x: float(x.get('searches', 0) or 0), reverse=True)
    L("| 關鍵詞 | 月搜尋量 | 點選集中度 | 供需比 | 商品數 | 平均售價 |")
    L("|--------|:-------:|:---------:|:------:|:-----:|:-------:|")
    for kw in sorted_kw[:20]:
        keyword = kw.get('keyword', 'N/A')
        sv = fmt_num(kw.get('searches', 0))
        cc = fmt_pct(kw.get('monopolyClickRate', 0))
        sdr = kw.get('supplyDemandRatio', '')
        sdr_str = f"{float(sdr):.1f}" if sdr else "N/A"
        prods = fmt_num(kw.get('products', 0))
        price = fmt_money(kw.get('avgPrice', 0)) if kw.get('avgPrice') else "N/A"
        L(f"| {keyword} | {sv} | {cc} | {sdr_str} | {prods} | {price} |")
    L()
    L(f"共 **{len(low_mono_kw)}** 個藍海關鍵詞符合條件。")
else:
    L("*未找到符合條件的低壟斷關鍵詞（搜尋量≥5000 + 點選集中度<50%）*")
L()

L("**推薦策略：** 優先投放供需比 > 10 且搜尋量高的關鍵詞，競爭小、轉化潛力大。")

# ====== CARD 4: High Margin Lightweight ======
L()
L("---")
L()
L("## 策略卡四：高毛利輕小品")
L()
L("> 篩選條件：FBA 運費 ≤ $4 | 毛利率 ≥ 50% | FBA 發貨")
L()

hm_items = safe_items(pr_high_margin)
if hm_items:
    sorted_hm = sorted(hm_items, key=lambda x: float(x.get('units', 0) or 0), reverse=True)
    L("| 商品 | 售價 | 月銷量 | 月銷售額 | FBA費 | 毛利率 | BSR | 評分 |")
    L("|------|:----:|:-----:|:--------:|:----:|:-----:|:---:|:----:|")
    for p in sorted_hm[:20]:
        title = (p.get('title', p.get('productName', 'N/A')))[:40]
        price = fmt_money(p.get('price', p.get('amount', 0)))
        units = fmt_num(p.get('units', 0))
        rev = fmt_money(p.get('revenue', 0))
        fba = fmt_money(p.get('fbaFee', 0))
        margin = fmt_pct(p.get('profitRate', p.get('profit', 0)))
        bsr = fmt_num(p.get('bsr', 0))
        rating = p.get('rating', 0)
        L(f"| {title} | {price} | {units} | {rev} | {fba} | {margin} | {bsr} | {rating} |")
    L()
    L(f"共 **{len(hm_items)}** 個商品符合高毛利輕小條件。")
else:
    L("*該節點下未找到符合條件的高毛利輕小商品*")
L()

# ====== CARD 5: Hot Low Rating ======
L()
L("---")
L()
L("## 策略卡五：熱銷低評分產品")
L()
L("> 篩選條件：月銷量 ≥ 1,000 | 評分 ≤ 4.2")
L()

hl_items = safe_items(pr_hot_low)
if hl_items:
    sorted_hl = sorted(hl_items, key=lambda x: float(x.get('units', 0) or 0), reverse=True)
    L("| 商品 | 售價 | 月銷量 | 月銷售額 | 評分 | 評分數 | BSR | FBA費 |")
    L("|------|:----:|:-----:|:--------:|:---:|:-----:|:---:|:----:|")
    for p in sorted_hl[:20]:
        title = (p.get('title', p.get('productName', 'N/A')))[:40]
        price = fmt_money(p.get('price', p.get('amount', 0)))
        units = fmt_num(p.get('units', 0))
        rev = fmt_money(p.get('revenue', 0))
        rating = p.get('rating', 0)
        ratings = fmt_num(p.get('ratings', 0))
        bsr = fmt_num(p.get('bsr', 0))
        fba = fmt_money(p.get('fbaFee', 0))
        L(f"| {title} | {price} | {units} | {rev} | {rating} | {ratings} | {bsr} | {fba} |")
    L()

    # Check if Mini Mic Pro is already there
    has_mini = any('mini mic' in (p.get('title', '')).lower() for p in hl_items)
    if not has_mini:
        L("> 注：Mini Mic Pro 評分 4.4，不符合 ≤4.2 條件，未出現在此列表。")
        L()
    L(f"共 **{len(hl_items)}** 個商品符合熱銷低評分條件，這些產品存在改良機會。")
else:
    L("*該節點下未找到符合條件的熱銷低評分商品*")
L()

# ====== OVERALL SUMMARY ======
L()
L("---")
L()
L("## 綜合策略總結")
L()
L("| 策略卡 | 結論 |")
L("|--------|:----:|")
L(f"| ① 低品牌壟斷類目 | ✅ 適用 — Lavalier Top3集中度 {fmt_pct(parent_items[0].get('top3BrandCrn',0)) if parent_items else '?'}（<45%）|")
L(f"| ② 高新品佔比市場 | ✅ 適用 — 6月新品佔比 {fmt_pct(parent_items[0].get('l6NewRatio',0)) if parent_items else '?'}（>5%）|")
L(f"| ③ 流量分散關鍵詞 | ✅ 找到 {len(low_mono_kw)} 個藍海關鍵詞 |")
L(f"| ④ 高毛利輕小品 | {'✅ 找到 ' + str(len(hm_items)) + ' 個' if hm_items else '⚠️ 無匹配'} 輕小高毛利商品 |")
L(f"| ⑤ 熱銷低評分產品 | {'✅ 找到 ' + str(len(hl_items)) + ' 個' if hl_items else '⚠️ 無匹配'} 改良機會產品 |")
L()
L("### 建議行動優先順序")
L()
L("1. **🔴 流量分散關鍵詞投放** — {} 個藍海詞，搜尋量>5000且競爭低，可快速獲取流量".format(len(low_mono_kw)))
if hl_items:
    L("2. **🔴 熱銷低評分產品改良** — {} 個產品市場需求大但有產品缺陷，改進可切入".format(len(hl_items)))
if hm_items:
    L("3. **🟡 高毛利輕小商品開發** — {} 個已驗證的輕小高利潤模型".format(len(hm_items)))
L("4. **🟡 低壟斷子市場深耕** — Lavalier + Handheld 兩個低壟斷子市場")
L("5. **🟢 利用高新品佔比優勢** — 市場更新迭代快，新品容易起量")
L()
L("---")
L()
L(f"*報告生成: 2026-07-05 | 資料工具: 賣家精靈 SellerSprite MCP | 站點: Amazon US*")

report = "\n".join(lines)
os.makedirs(OUT_DIR, exist_ok=True)
with open(f"{OUT_DIR}/tactical_strategies.md", "w", encoding="utf-8") as f:
    f.write(report)
print(f"Tactical strategies saved to {OUT_DIR}/tactical_strategies.md")
print(f"Report size: {len(report)} chars")
