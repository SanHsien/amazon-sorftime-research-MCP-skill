---
name: sellersprite-amazon-research
description: 賣家精靈 Amazon 全鏈路資料調研 Skill。透過 43 個 MCP 資料工具完成選品分析、關鍵詞研究、競品監控、市場分析、定價策略、評論分析、廣告最佳化、流量分析、Listing 最佳化和藍海機會挖掘。觸發場景：(1) 使用者詢問 Amazon 選品/市場/競品分析 (2) 使用者輸入 /product-research, /market-analysis, /competitor-analysis, /keyword-research, /listing-optimizer, /traffic-analysis, /opportunity-finder, /review-insights, /pricing-strategy, /ad-optimizer 等命令 (3) 使用者提及新品爆發、隱形爆款、ABA 增長詞、低品牌壟斷、評論分析等選品策略。適用於跨境電商賣家、Amazon 運營和產品開發決策。
---

# 賣家精靈 Amazon 資料調研

## 重要：MCP 連線配置

`.mcp.json` 必須使用以下格式（⚠️ 金鑰透過 header 傳入，不是 URL 引數）：

```json
{
  "mcpServers": {
    "sellersprite": {
      "url": "https://mcp.sellersprite.com/mcp",
      "headers": {
        "secret-key": "你的金鑰"
      }
    }
  }
}
```

| 配置項 | 正確值 | 錯誤值 |
|--------|--------|--------|
| URL | `https://mcp.sellersprite.com/mcp` | `.../sse` 或 `.../mcp?key=xxx` |
| 認證方式 | `headers.secret-key` | URL 查詢引數 `?key=` |

---

## 工具呼叫方式

### 方式 A：透過 MCP 客戶端（推薦）

MCP 客戶端直接呼叫工具：

```
mcp__sellersprite__<tool_name>
```

例: `mcp__sellersprite__product_research`

### 方式 B：透過 curl（無 MCP 客戶端時備用）

```bash
curl -s -X POST "https://mcp.sellersprite.com/mcp" \
  -H "Content-Type: application/json" \
  -H "secret-key: <YOUR_KEY>" \
  -d '{
    "jsonrpc": "2.0", "id": 1, "method": "tools/call",
    "params": {
      "name": "<tool_name>",
      "arguments": { <扁平引數或{"request":{...}}> }
    }
  }'
```

### 方式 C：透過 Python（批次呼叫場景）

```python
import json, urllib.request
payload = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"market_research","arguments":{"request":{
        "marketplace":"US","nodeIdPath":"...","topNum":10}}}}).encode()
req = urllib.request.Request("https://mcp.sellersprite.com/mcp", data=payload,
    headers={"Content-Type":"application/json","secret-key":"<KEY>"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    result = json.loads(data['result']['content'][0]['text'])
```

### 方式 D：透過 mcp_call.py 工具指令碼（專案內預置）

```bash
python3 mcp_call.py <tool_name> '{"param1":"value1"}'
```

---

## 關鍵：引數傳遞模式

### 模式 A："扁平引數"（少部分工具）

直接在頂層傳欄位。例如 `asin_detail`、`keyword_research_trends`、`review`：

```json
{"marketplace": "US", "asin": "B0XXXXX"}
```

### 模式 B："request 巢狀物件"（大部分工具）

絕大多數篩選/搜尋類工具（market_research、product_research、keyword_miner 等）的**唯一必填引數是 `request`**，其值為一個巢狀物件：

```json
{
  "request": {
    "marketplace": "US",
    "nodeIdPath": "11091801:11974521:8882489011:11974711",
    "topNum": 10,
    "size": 50
  }
}
```

**MCP 客戶端呼叫時**，`arguments` 寫為 `{"request": {...}}`。

### 識別方法
檢視工具的 `required` 欄位：
- `required=["marketplace","asin"]` → 扁平引數
- `required=["request"]` → 巢狀物件

---

## 全域性引數預設值

| 引數 | 預設值 | 說明 |
|------|--------|------|
| `marketplace` | `US` | 目標站點：US/JP/UK/DE/FR/IT/ES/CA/IN |
| `matchType` | `2` | 1=片語匹配 2=模糊匹配 3=精準匹配 |
| `size` | `50` | 每頁返回條數（最大 100） |

---

## 欄位對映與刻度陷阱（重要）

### 改名規律（網頁 API → MCP 響應）
- `totalUnits` → **`units`**（月銷量）
- `totalAmount` → **`revenue`**（月銷售額）
- `reviews` → **`ratings`**（評分數）
- `bsrRank` → **`bsr`**（BSR 排名）
- `sellerType` → **`fulfillment`**（配送方式）
- `*Ratio` → `*Proportion`，`HeadListing*` → `Top*`

### 刻度陷阱
- **集中度欄位**（`top*Crn`/`l*NewRatio`）為 **0~1 小數**，展示需 ×100
- **`returnRatio`/`*Proportion`** 已是 0~100 百分數，不再換算
- **`purchaseRate`/`cvsShareRate`/`monopolyClickRate`** 為 0~1，展示 ×100
- **`supplyDemandRatio`** 已是真實比值（如 78.88），不換算
- **多值引數**（brands/sellers/fulfillment）傳逗號字串，非陣列

### 類名翻譯陷阱 ⚠️
product_node 返回的 `nodeLabelLocale`（中文翻譯）**不可靠**，常見錯誤：
| 英文名 | 錯誤翻譯 |
|--------|---------|
| Microphones | 顯微鏡 ❌ |
| Microphone Accessories | 輔料 ❌ |
| Hand Percussion | 手部打擊樂 ❌ |
| Stands | 攤位 ❌ |
| Sound | 聲音 ❌ |

**始終以 `nodeLabelPath`（英文完整路徑）為準。**

---

## MCP 響應解析要點

### 標準響應結構
```json
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "content": [{"type": "text", "text": "{\"code\":\"OK\",\"data\":...}"}],
    "isError": false
  }
}
```

`result.content[0].text` 是賣家精靈 API 的 JSON 字串，**需二次解析**。

### 資料組織結構差異
| 工具型別 | data 結構 | 示例 |
|---------|-----------|------|
| `market_research` | `{ items: [...] }` | 子市場陣列在 `items` |
| `market_brand_concentration` | `[{...}]`（直接陣列） | 品牌列表直接返回 |
| `market_price_distribution` | `{ items: [...] }`（巢狀） | 價格區間在 `items` |
| `product_node` | `[{...}]`（直接陣列） | 節點列表直接返回 |

**安全取值**：
```python
def safe_items(data):
    if isinstance(data, dict): return data.get('items', [])
    if isinstance(data, list): return data
    return []
```

### ⚠️ 實際 API 響應欄位陷阱（實測發現，與文件不一致）

部分工具的 JSON 響應欄位名與文件描述不同，**必須按實際響應取值**：

| 工具 | 你以為的欄位 | 實際欄位 | 後果 |
|------|------------|---------|------|
| `keyword_research_trends` | `month`, `searches` | **`time`**, **`search`** | 全顯示 N/A |
| `keyword_research_trends` | `growth`, `change` | **`chainGrowth`**(環比), **`yearlyGrowth`**(同比) | 無增長率 |
| `keyword_research_trends` | `purchaseCount` | **`purchase`** | 無購買資料 |
| `aba_research_trend` | `clickShareRate`, `conversionShareRate` | **沒有這兩個欄位** | 全顯示 0% |
| `aba_research_trend` | `month` | **`label`**, `date`, `searches`, `rank` | 無趨勢 |
| `traffic_keyword_stat` | `searchTotal`, `naturalTotal` | **`keywords`**(總數), **`ranks`**(有排名), **`ads`**(有廣告) | 全顯示空 |
| `review` | `body`, `createTime` | **`content`**, **`date`** | 評論內容為空 |
| `keepa_info` | `currentPrice`, `bsrHistory` | **`buyBox`**([{timePoint,value}]), **`bsr`**([{timePoint,value}]) | 全顯示空 |
| `traffic_source` | `request` 巢狀物件 | 實際需**扁平引數** + `"q": "asin"` | HTTP 200 但返回 `q is required` |
| `keyword_research` | 傳入 `keyword` 引數 | 返回按搜尋量排序的全域性關鍵詞，無視篩選 | 資料全為不相關詞 |

### review 工具取樣限制（重要）
- `review` 工具 **每次最多返回 20 條**（size=100 也會被限制）
- 所以評分分佈是 **樣本**，不代表總體
- 報告中必須註明："⚠️ 僅展示最近 20 條評論，不代表總體分佈"
- 情感分析和差評主題也要加"基於樣本"限定

### keepa 時間序列資料提取
keepa_info 返回的價格/BSR 均為 `[{timePoint: timestamp, value: number}]` 格式陣列：
```python
price_data = keepa.get('buyBox', [])
if price_data:
    prices = [p['value'] for p in price_data if p.get('value', 0) > 10]
    current_price = prices[-1] if prices else 'N/A'
    avg_price = sum(prices)/len(prices) if prices else 'N/A'
```

### HTML 實體解碼
API 返回的標題/描述中可能包含 `&amp;` `&quot;` `&lt;` 等 HTML 實體，必須解碼：
```python
import html
clean_title = html.unescape(raw_title)
```

---

## 一、綜合分析工作流

透過 `/命令` 呼叫，執行多步驟分析。詳細步驟見 `comprehensive/` 下對應檔案。

| 命令 | 名稱 | 核心工具 | 詳見 |
|------|------|----------|------|
| `/product-research` | 智慧選品助手 | `product_research` + `product_node` | `comprehensive/product-research.md` |
| `/market-analysis` | 市場全景分析 | `market_research` + 分佈工具集 | `comprehensive/market-analysis.md` |
| `/competitor-analysis` | 競品深度拆解 | `asin_detail` + `traffic_keyword` | `comprehensive/competitor-analysis.md` |
| `/keyword-research` | 關鍵詞選品研究 | `keyword_research` + `keyword_miner` | `comprehensive/keyword-research.md` |
| `/listing-optimizer` | Listing 最佳化診斷 | `traffic_listing` + `keyword_order` | `comprehensive/listing-optimizer.md` |
| `/traffic-analysis` | 流量結構分析 | `traffic_source` + `traffic_keyword_stat` | `comprehensive/traffic-analysis.md` |
| `/opportunity-finder` | 藍海機會挖掘 | `aba_research_trend` + `google_trend` | `comprehensive/opportunity-finder.md` |
| `/review-insights` | 買家評論洞察 | `review` + NLP 分析 | `comprehensive/review-insights.md` |
| `/pricing-strategy` | 定價策略分析 | `market_price_distribution` | `comprehensive/pricing-strategy.md` |
| `/ad-optimizer` | 廣告投放最佳化 | `keyword_order` + `traffic_keyword` | `comprehensive/ad-optimizer.md` |

---

## 二、戰術選品策略卡

對話中引用名稱觸發。詳細引數見 `tactical/` 下對應檔案。

### 新品爆發型
| 策略 | 核心工具 | 邏輯 | 詳見 |
|------|----------|------|------|
| 新品快速爆發 | `product_research` | 上架≤2月+銷量≥300+Review≤100 | `tactical/new-product-burst.md` |
| 隱形爆款 | `product_research` | 上架≤3月+銷量≥500+Review≤50 | `tactical/hidden-bestseller.md` |

### 關鍵詞趨勢型
| 策略 | 核心工具 | 邏輯 | 詳見 |
|------|----------|------|------|
| ABA 高增長趨勢詞 | `keyword_research` | 近3月持續增長+點選不集中 | `tactical/aba-high-growth-trend.md` |
| 流量分散關鍵詞 | `keyword_miner` | 搜尋≥5000+集中度<50% | `tactical/low-monopoly-keyword.md` |
| 標題密度漏洞 | `keyword_miner` | 標題密度≤5的長尾詞 | `tactical/title-density-gap.md` |

### 產品缺陷型
| 策略 | 核心工具 | 邏輯 | 詳見 |
|------|----------|------|------|
| 熱銷低評分產品 | `product_research` | 月銷≥1000+評分≤4.2 | `tactical/hot-low-rating.md` |
| 評論語義分析 | `review` | 差評NLP聚類→改良指南 | `tactical/review-sentiment.md` |

### 類目結構型
| 策略 | 核心工具 | 邏輯 | 詳見 |
|------|----------|------|------|
| 低品牌壟斷類目 | `market_research` | 品牌集中度<45% | `tactical/low-brand-monopoly.md` |
| 高新品佔比市場 | `market_research` | 新品佔比>5%+新品仍出單 | `tactical/high-new-product-ratio.md` |
| 高毛利輕小品 | `product_research` | FBA≤$4+毛利≥50% | `tactical/high-margin-lightweight.md` |

### 流量防偽型
| 策略 | 核心工具 | 邏輯 | 詳見 |
|------|----------|------|------|
| 自然流量反查 | `traffic_source` | 自然流量佔比>60% | `tactical/natural-traffic-audit.md` |
| 變體拆解模型 | `asin_detail` | 找未被覆蓋的變體缺口 | `tactical/variant-gap-analysis.md` |

### 機會捕捉型
| 策略 | 核心工具 | 邏輯 | 詳見 |
|------|----------|------|------|
| 本土溢價降維 | `product_research` | 美國賣家+高價+高銷 | `tactical/local-premium-disruption.md` |
| FBM 攔截 | `product_research` | FBM發貨+月銷≥300 | `tactical/fbm-intercept.md` |
| 低質量 Listing 高銷量 | `product_research` | LQS≤60+月銷≥400 | `tactical/poor-listing-winner.md` |
| 高客單長尾 | `keyword_miner` | 均價≥$80+搜尋量適中 | `tactical/high-ticket-long-tail.md` |
| 季節前置爆破 | `keyword_miner` | 歷史同期環比增長>100% | `tactical/seasonal-prepositioning.md` |

---

## 三、MCP 工具參考

詳細引數、響應欄位對映和陷阱見 `reference/` 下檔案：

| 參考檔案 | 對應工具 | 已驗證 |
|----------|----------|--------|
| `reference/product_research.md` | `product_research` | ✅ |
| `reference/market_research.md` | `market_research` + 11 分佈工具 | ✅ |
| `reference/traffic_keyword.md` | `traffic_keyword` + `traffic_extend` | ✅ |
| `reference/competitor_lookup.md` | `competitor_lookup` | ✅ |
| `reference/keyword_miner.md` | `keyword_miner` + `keyword_research` | ✅ |
| `reference/asin_detail.md` | `asin_detail` + `keepa_info` 等 ASIN 工具 | |
| `reference/tools_index.md` | 全部 42 個工具清單 + 引數模式 | ✅ 已更新 |

---

## 四、輸出格式（必讀：必須儲存為檔案）

### HTML 視覺化報告生成（固定步驟，不可跳過）

完成 `market_report.md` 後，**必須自動生成**對應的 `market_report.html`：

1. **資料來源** — 以剛完成的 `market_report.md` 為資料來源，不額外調 API
2. **全面展示** — 覆蓋報告的每個核心維度（概覽、銷量、流量、關鍵詞、競爭、市場、評論、價格、SWOT、行動建議）
3. **圖表呈現** — 關鍵資料用 Canvas 圖表展示（價格/BSR 趨勢、對比柱狀圖、趨勢線等）
4. **設計風格** — 深色專業主題、配色統一、響應式適配、互動流暢
5. **輸出** — 儲存到與 MD 相同的目錄 `{類別名}/market_report.html`

> 如果使用者明確說"不需要 HTML"可以跳過，否則必須生成。

### 鐵律：報告禁止僅列印到控制檯

所有分析報告**必須儲存為檔案**，不得只 `print`/`echo` 到控制檯。使用者看不到控制檯輸出。

### 檔案儲存規範

| 檔案 | 必存 | 命名規則 | 說明 |
|------|:----:|---------|------|
| 分析報告 | ✅ 必須 | `{類別名}/market_report.md` | 結構化 Markdown，使用者可直接閱讀 |
| HTML 視覺化報告 | ✅ **必須**（新增） | `{類別名}/market_report.html` | **生成 MD 報告後自動配套生成**，單檔案純 HTML+CSS+JS，基於 MD 資料，無需額外 API 呼叫 |
| 原始資料 | ✅ 必須 | `{類別名}/research_data.json` | API 原始返回，供後續二次分析 |

**目錄命名**：以調研的類別名為目錄名，如 `wirelessinstruments/`、`bluetooth-speaker/`。

### ⚡ 鐵律：MD 報告完成後必須生成 HTML 報告

每次完成 `market_report.md` 後，**必須立即** 基於 MD 內容生成對應的 `market_report.html`。這是不可跳過的步驟，原因：

1. **使用者體驗** — HTML 報告包含視覺化圖表（Canvas 折線圖/柱狀圖/趨勢圖），比純文字直觀得多
2. **資料驗證** — 圖表能暴露 Markdown 表格中不易察覺的資料異常
3. **分享便利** — 非技術背景的團隊成員可直接在瀏覽器開啟檢視

> 注意：HTML 報告是 MD 報告的 **視覺化增強版本**，不是替代。兩者共存，各有用途。

### 報告內容結構

所有報告必須包含：
1. **篩選口徑** — 工具引數、資料月份、ASIN/關鍵詞、Review 取樣說明
2. **KPI 摘要** — 關鍵指標高亮
3. **多維分析** — 表格 + 評分卡 + 洞察
4. **分級結論** — 推薦/謹慎/不推薦

### 報告質量檢查清單（生成後必須自查）

報告儲存前，逐項檢查以下內容，確保沒有質量問題：

| # | 檢查項 | 說明 |
|---|--------|------|
| 1 | **標題/描述 HTML 實體** | 檢查 `&amp;` `&quot;` 等是否用 `html.unescape()` 解碼 |
| 2 | **銷量彙總有重疊** | 多賣家/多變體疊加的合計要加⚠️註解 |
| 3 | **流量來源工具容錯** | `traffic_source` 可能不返回資料，必須有 fallback |
| 4 | **ABA 欄位正確** | 用 `searches`/`rank`，不要用不存在的 `clickShareRate` |
| 5 | **趨勢欄位正確** | 用 `time`/`search`/`chainGrowth`/`yearlyGrowth` |
| 6 | **Review 樣本說明** | 必須註明"僅 20 條樣本"，評分分佈不能代表總體 |
| 7 | **關鍵詞相關性過濾** | 高價值/藍海詞列表必須排除不相關泛詞 |
| 8 | **品牌詞不要列為機會** | 純品牌詞（"dji"等）不應出現在藍海表中 |
| 9 | **Keepa 資料展示** | 呼叫 keepa_info 後必須在報告中展示 |
| 10 | **ASIN vs 市場資料區分** | 每個表格註明資料是 ASIN 自身的還是搜尋市場的 |

### 數值格式化

銷量/銷售額千分位（`12,345`）、佔比/評分 1 位小數（`23.4%`）、價格 `$X.XX`。注意 0~1 刻度換算。

---

## 五、推薦組合鏈路

```
品類掃描 -> 低品牌壟斷 / 高新品佔比（找藍海類目）
    ↓
關鍵詞挖掘 -> ABA增長詞 / 流量分散詞 / 標題密度漏洞（找增長詞）
    ↓
競品鎖定 -> 新品爆發 / 隱形爆款 / 熱銷低評分（找目標競品）
    ↓
競品驗真 -> 自然流量反查（流量防偽）
    ↓
痛點提煉 -> 評論語義分析（產品改進）
    ↓
產品開發 -> 變體拆解 + 高毛利輕小（利潤驗證）
```

---

## 六、實操技巧（實測經驗）

### 類目節點查詢技巧
- 用英文關鍵詞搜尋（`"wireless microphone"` 比 `"無線麥克風"` 結果更準）
- 找到後記錄 `nodeIdPath` 供後續呼叫
- 父節點資料可能包含自身彙總行，取資料時注意過濾

### 批處理策略
- 市場全景分析至少呼叫 13 個工具（market_research + 12 分佈工具）
- 工具間無資料依賴，可以全並行
- 關注響應中的 `code: "OK"` 欄位判斷呼叫成功

### 常見故障排查
| 現象 | 原因 | 解決方法 |
|------|------|---------|
| 返回 `secret_invalid` | key 配置錯誤 | 檢查 header 名是 `secret-key`，非 `Authorization` |
| 資料全是 0 | 節點是根節點 | 必須使用葉子節點 nodeIdPath |
| HTTP 400 | 請求格式錯誤 | 檢查 `request` 巢狀是否正確 |
| **`q is required`** | `traffic_source` 用了 `request` 巢狀 | 改用**扁平引數** + `"q": "asin"` |
| **返回不相關資料** | `keyword_research` 傳了 keyword 但忽略篩選 | 該工具會忽略 keyword 引數，改用 `keyword_miner` 替代 |
| 翻譯名稱怪 | `nodeLabelLocale` 不可靠 | 使用英文 `nodeLabelPath` |
| 報告顯示 N/A 或全 0 | 欄位名與文件不符 | 查本文「實際 API 響應欄位陷阱」表，用實際欄位名 |
| ABA/趨勢資料空白 | 用了 `clickShareRate`/`conversionShareRate` | 實際只有 `searches`/`rank` 欄位 |
| 評論只有 20 條 | review 工具取樣限制 | size 引數無效，最多返回 20 條 |
| 趨勢月份顯示 N/A | 用了 `month` 或 `label` | keyword_research_trends 用 `time` |
| 報告中有 `&amp;` | HTML 實體未解碼 | 必須用 `html.unescape()` |
| Keepa 資料空白 | 用了 `currentPrice` 等不存在欄位 | 用 `buyBox` / `bsr` 陣列，內部是 `{timePoint, value}` |

---

## 七、實測經驗與引數陷阱

> 以下為 2026-07-05 JOYO JW-03 深度調研中實測發現的工具行為差異，已修復到文件中。記錄在此供未來快速參考。

### 7.1 連線與認證

| 經驗 | 說明 |
|------|------|
| **Accept header 必須** | 呼叫 MCP endpoint 時必須傳 `Accept: application/json, text/event-stream`，僅傳 `application/json` 會 HTTP 400 |
| **金鑰傳 header** | `secret-key` 放 headers，非 URL 引數，非 `Authorization` |
| **SSE 方案不可用** | SDK SSE 連線 /sse → 阿里雲 Tengine CDN session affinity 導致 302/504 Gateway Timeout，放棄。始終用 HTTP POST 到 `/mcp` |

### 7.2 工具引數模式實測糾正

| 工具 | 文件聲稱 | 實測正確方式 | 後果 |
|------|---------|-------------|------|
| `traffic_source` | `request` 巢狀物件 | **扁平引數** + `"q": "asin"`：`{"marketplace":"US","asin":"B0XXX","q":"asin"}` | HTTP 200 但返回 `q is required` |
| `traffic_keyword_stat` | `request` 巢狀物件 | **扁平引數**：`{"marketplace":"US","asin":"B0XXX"}` | 空資料 |
| `keyword_research` | 傳 `keyword` 篩選 | **該工具完全忽略 keyword 引數**，返回全域性熱詞按搜尋量排序 | 資料全為不相關詞 |

### 7.3 流量工具注意事項

- `traffic_source` 即使呼叫成功，`asinInfo` 也可能返回**無關產品的流量**（實測返回了空氣清淨機、SD 卡等），資料不可信賴
- 流量來源分析建議使用 `traffic_keyword` + `traffic_keyword_stat` 組合來代替
- `traffic_listing_stat` 和 `traffic_listing` 正常工作，可用 `request` 巢狀物件

### 7.4 評論工具缺陷

- `review` 工具 **size 引數無效**，最多永遠返回 20 條
- 所以評分分佈永遠是樣本，報告中必須註明"僅最近 20 條樣本"
- 欄位名：`content`（非 `body`）、`date`（非 `createTime`）

### 7.5 Keepa 資料處理

- `keepa_info` 返回的是時間序列陣列：`buyBox: [{timePoint, value}]`、`bsr: [{timePoint, value}]`
- 不存在 `currentPrice` 或 `bsrHistory` 欄位
- 提取當前價：取 `buyBox` 陣列最後一個 `value`；BSR 同理

### 7.6 類目節點注意事項

- `product_node` 返回的 `nodeLabelLocale`（中文翻譯）**經常錯誤**（Microphones → 顯微鏡）
- 始終以 `nodeLabelPath`（英文完整路徑）為準
- 必須使用**葉子節點** `nodeIdPath`，父節點返回全 0 資料

### 7.7 混合類目識別

某些子類目下混合了不同型別的商品（如 "Electric Guitar Electronics" 下既有 $5-15 的電子元件，也有 $40+ 的無線吉他系統）。分析時需注意：

1. **價格分佈會兩極分化** — 不代表目標產品的合理定價區間
2. **品牌集中度可能失真** — 高價品牌銷售額佔比虛高
3. **解決方法**：手動標註類目內真實競品，單獨圈定可比價格區間

### 7.8 資料質量標註規範

報告中凡是遇到以下情況，必須加 ⚠️ 標註：

| 場景 | ⚠️ 原因 |
|------|---------|
| 多 ASIN 銷量彙總 | 多變體/多賣家合計可能重疊 |
| 價格 vs 銷量交叉表合計不一致 | 統計口徑不同或重複計數 |
| 品牌集中度工具間差異 | `market_research` 和 `market_brand_concentration` 可能口徑不同 |
| Google Trends 異常峰值 | 可能是短期事件（新品釋出/KOL），不代表長期趨勢 |
| 評論評分分佈 | review 僅 20 條樣本，不能代表總體 |
| 關聯流量資料 | `traffic_listing_stat` 關聯流量為快照值，非月度累計 |

---

## 八、報告質量檢查清單

> 報告儲存前，逐項檢查以下內容，確保沒有質量問題。此清單為生產報告的最後一道門禁。

### 8.1 資料完整性檢查

| # | 檢查項 | 說明 |
|---|--------|------|
| 1 | **報告和原始資料均已儲存** | `market_report.md` + `research_data.json` 都必須在 `{類別目錄}/` 下 |
| 2 | **至少呼叫 3+ 工具** | 單一工具的報告結論不可靠，must cross-reference |
| 3 | **流量來源資料有 fallback** | `traffic_source` 可能失敗，必須有替代方案（traffic_keyword + traffic_keyword_stat） |
| 4 | **Keepa 資料已展示** | 呼叫 `keepa_info` 後必須在報告中展示價格/BSR 歷史 |
| 5 | **谷歌趨勢已呼叫** | 大型調研必須包含 Google Trends 資料進行外部驗證 |

### 8.2 欄位正確性檢查

| # | 檢查項 | 說明 |
|---|--------|------|
| 6 | **趨勢欄位使用正確** | 用 `time`/`search` 非 `month`/`searches`；`chainGrowth`(環比) 非 `growth` |
| 7 | **ABA 欄位使用正確** | 用 `searches`/`rank`，**不要**用 `clickShareRate`/`conversionShareRate`（不存在） |
| 8 | **刻度轉換正確** | 集中度 0~1 → ×100；`purchaseRate` 0~1 → ×100；`returnRatio` 已是百分數不再換算 |
| 9 | **HTML 實體已解碼** | `&amp;` `&quot;` 等必須用 `html.unescape()` 解碼 |
| 10 | **Review 樣本已註明** | 必須標註"僅最近 20 條樣本"，評分分佈不具總體代表性 |

### 8.3 邏輯正確性檢查

| # | 檢查項 | 說明 |
|---|--------|------|
| 11 | **關鍵詞列表排除了品牌詞** | 純品牌詞（"dji"、"lekato"等）不應列為藍海機會 |
| 12 | **關鍵詞列表排除了不相關泛詞** | 高價值/藍海詞列表必須人工過濾無關詞 |
| 13 | **ASIN vs 市場資料區分** | 每個表格註明資料是 ASIN 自身的還是搜尋市場的 |
| 14 | **混合類目已識別並標註** | 如 $5-15 元件 + $40+ 系統的混合類目，需加 ⚠️ 說明 |
| 15 | **銷量彙總重疊已標註** | 多賣家/多變體疊加的合計要加 ⚠️ |

### 8.4 格式規範檢查

| # | 檢查項 | 說明 |
|---|--------|------|
| 16 | **數值格式化** | 銷量/銷售額千分位（`12,345`），佔比/評分 1 位小數（`23.4%`），價格 `$X.XX` |
| 17 | **表格可讀性** | Markdown 表格對齊（`:---` 左對齊 `:---:` 居中 `---:` 右對齊） |
| 18 | **標題層級合理** | 使用 `##` / `###` / `####` 層級結構，不超過 4 級 |
| 19 | **篩查口徑已記錄** | 報告中必須標註：呼叫工具列表、資料月份、ASIN/關鍵詞、取樣說明 |
| 20 | **資料質量警告** | 資料異常處必須使用 ⚠️ 標註（參考 7.8 節） |

### 8.5 釋出前最終確認

- [ ] 以上 20 項檢查已逐項透過
- [ ] `research_data.json` 已儲存且包含所有 API 原始返回
- [ ] 報告包含篩選口徑、KPI 摘要、多維分析、分級結論四要素
- [ ] 無僅列印到控制檯的除錯輸出
- [ ] **`market_report.html` 已生成** — 在 `market_report.md` 同級目錄，包含圖表視覺化
