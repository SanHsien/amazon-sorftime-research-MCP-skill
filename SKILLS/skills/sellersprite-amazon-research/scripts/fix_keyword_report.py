#!/usr/bin/env python3
"""Fix keyword report - correct field names"""
import sys, json
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
OUT_DIR = "D:/sellersprite-skills/lavalier-microphones"

with open(f"{OUT_DIR}/keyword_data.json", encoding='utf-8') as f:
    data = json.load(f)

def safe_items(api_result):
    if isinstance(api_result, dict):
        if api_result.get('code') != 'OK':
            return []
        d = api_result.get('data', {})
        if isinstance(d, list): return d
        items = d.get('items', d.get('data', []))
        if isinstance(items, list): return items
        return []
    return []

def fmt_num(n):
    if n is None: return "N/A"
    return f"{float(n):,.0f}"

def fmt_pct(n):
    if n is None: return "N/A"
    n = float(n)
    return f"{n*100:.1f}%"

def fmt_money(n):
    if n is None: return "N/A"
    return f"${float(n):,.2f}"

lines = []
def L(s=""):
    lines.append(s)

L("# Wireless Lavalier Microphones — 關鍵詞研究報告")
L()
L(f"> 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M')} | 資料來源: 賣家精靈 SellerSprite MCP")
L()
L("---")
L()

# ====== Keyword Miner ======
L("## 一、關鍵詞挖掘（Keyword Miner）")
L()
L("關鍵詞挖掘從種子詞「lavalier microphone wireless」擴充套件，返回相關關鍵詞的搜尋量、競爭度和供需關係。")
L()
miner_items = sorted(safe_items(data.get('keyword_miner', {})),
                     key=lambda x: float(x.get('searches', 0) or 0), reverse=True)

if miner_items:
    L("| 關鍵詞 | 月搜尋量 | 商品數 | 供需比 | 點選集中度 | 標題密度 | 平均售價 | 平均評分 |")
    L("|--------|:-------:|:-----:|:------:|:---------:|:--------:|:-------:|:-------:|")
    for kw in miner_items[:40]:
        keyword = kw.get('keyword', 'N/A')
        sv = fmt_num(kw.get('searches', 0))
        prods = fmt_num(kw.get('products', 0))
        sdr = kw.get('supplyDemandRatio', '')
        sdr_str = f"{float(sdr):.1f}" if sdr else "N/A"
        click_crn = fmt_pct(kw.get('monopolyClickRate', 0))
        td = kw.get('titleDensity', 0)
        td_str = f"{float(td):.1f}%" if td else "N/A"
        price = fmt_money(kw.get('avgPrice', 0)) if kw.get('avgPrice') else "N/A"
        rating = round(kw.get('avgRating', 0), 1) if kw.get('avgRating') else "N/A"
        L(f"| {keyword} | {sv} | {prods} | {sdr_str} | {click_crn} | {td_str} | {price} | {rating} |")
    L()

L("---")
L()

# ====== Keyword Research ======
L("## 二、關鍵詞研究（Keyword Research）")
L()
L("> 注意：Keyword Research 返回類目級別相關關鍵詞，使用父類目資料。")
L()
research_items = safe_items(data.get('keyword_research', {}))
if research_items:
    L("| 關鍵詞 | 月搜尋量 | 月銷量 | 搜尋增長率 | 供需比 | 點選集中度 | 平均售價 | 平均評分 |")
    L("|--------|:-------:|:-----:|:---------:|:------:|:---------:|:-------:|:-------:|")
    for kw in sorted(research_items, key=lambda x: float(x.get('searches', 0) or 0), reverse=True)[:40]:
        keyword = kw.get('keywords', kw.get('keyword', 'N/A'))
        sv = fmt_num(kw.get('searches', 0))
        purchases = fmt_num(kw.get('purchases', 0))
        growth = kw.get('growth', '')
        growth_str = f"{float(growth):.1f}%" if growth != '' else "N/A"
        sdr = kw.get('supplyDemandRatio', '')
        sdr_str = f"{float(sdr):.1f}" if sdr else "N/A"
        click_crn = fmt_pct(kw.get('araClickRate', kw.get('monopolyClickRate', 0)))
        price = fmt_money(kw.get('avgPrice', 0)) if kw.get('avgPrice') else "N/A"
        rating = round(kw.get('avgRating', 0), 1) if kw.get('avgRating') else "N/A"
        L(f"| {keyword} | {sv} | {purchases} | {growth_str} | {sdr_str} | {click_crn} | {price} | {rating} |")
    L()

L("---")
L()

# ====== ABA Trends ======
L("## 三、ABA 趨勢分析")
L()
aba_results = data.get('aba_trends', {})
if aba_results:
    for keyword, aba_data in aba_results.items():
        L(f"### 「{keyword}」ABA 趨勢")
        L()
        aba_items = safe_items(aba_data)
        if aba_items:
            L("| 時間 | 搜尋頻率排名 | 點選份額 | 轉化份額 |")
            L("|------|:----------:|:--------:|:--------:|")
            for item in aba_items[-12:]:
                time_label = item.get('label', item.get('month', 'N/A'))
                rank = item.get('rank', '')
                cs = fmt_pct(item.get('clickShareRate', item.get('clickShare', 0)))
                cvs = fmt_pct(item.get('conversionShareRate', item.get('conversionShare', 0)))
                L(f"| {time_label} | {rank} | {cs} | {cvs} |")
        else:
            L("*暫無 ABA 趨勢資料*")
        L()
else:
    L("*ABA 趨勢資料未獲取到*")
    L()

L("---")
L()

# ====== Opportunities ======
L("## 四、低競爭高潛力關鍵詞推薦")
L()
opportunities = []
for kw in miner_items:
    sv = float(kw.get('searches', 0) or 0)
    click_crn = float(kw.get('monopolyClickRate', 1) or 1)
    if sv >= 300 and click_crn < 0.5:
        opportunities.append(kw)

if opportunities:
    L("| 關鍵詞 | 月搜尋量 | 供需比 | 點選集中度 | 平均售價 | 策略 |")
    L("|--------|:-------:|:------:|:---------:|:-------:|------|")
    for kw in sorted(opportunities, key=lambda x: float(x.get('searches', 0) or 0), reverse=True)[:15]:
        keyword = kw.get('keyword', 'N/A')
        sv = fmt_num(kw.get('searches', 0))
        sdr = kw.get('supplyDemandRatio', '')
        sdr_str = f"{float(sdr):.1f}" if sdr else "N/A"
        cc = fmt_pct(kw.get('monopolyClickRate', 0))
        price = fmt_money(kw.get('avgPrice', 0)) if kw.get('avgPrice') else "N/A"
        L(f"| {keyword} | {sv} | {sdr_str} | {cc} | {price} | 廣告投放 + Listing 最佳化 |")
    L()
else:
    L("*暫無符合條件的低競爭高潛力關鍵詞（搜尋量≥300 且 點選集中度<50%）*")
    L()

L("---")
L()
L("## 五、戰術策略推薦")
L()
L("1. **ABA 高增長趨勢詞** — 近 3 月持續增長的關鍵詞重點投放")
L("2. **流量分散關鍵詞** — 點選集中度 < 50%，競爭分散易於切入")
L("3. **標題密度漏洞** — 標題密度 ≤ 5 的長尾詞，最佳化 Listing 標題")
L("4. **高客單長尾詞** — 均價 ≥ $80 且有合理搜尋量的關鍵詞")
L()
L("---")
L()
L(f"*報告生成: 2026-07-05 | 資料來源: 賣家精靈 SellerSprite MCP | 站點: Amazon US*")

report = "\n".join(lines)
with open(f"{OUT_DIR}/keyword_report.md", "w", encoding="utf-8") as f:
    f.write(report)
print(f"Keyword report regenerated to {OUT_DIR}/keyword_report.md")
print(f"Total keywords in miner: {len(miner_items)}")
print(f"Opportunities found: {len(opportunities)}")
print(f"Report size: {len(report)} chars")
