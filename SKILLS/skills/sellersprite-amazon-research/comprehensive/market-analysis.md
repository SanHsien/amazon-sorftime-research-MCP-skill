# 市場全景分析

對指定的 Amazon 類目進行全面分析，評估市場吸引力、競爭強度和進入可行性。

## 使用方式

```
/market-analysis [類目關鍵詞或節點ID] [站點]
```

引數: 第1個為類目關鍵詞/nodeIdPath（必填），第2個為站點（可選，預設US）

## 執行步驟

### 第1步: 獲取類目節點

呼叫 `product_node` 查詢類目節點：
- `marketplace`: 指定站點
- `keyword`: 使用者輸入的關鍵詞（建議用英文，中文翻譯 nodeLabelLocale 不可靠）

⚠️ **必須找到葉子節點**（有具體商品數量的節點），根節點統計全 0。

輸出示例：
```json
{"nodeIdPath": "11091801:11974521:8882489011:11974711",
 "nodeLabelPath": "Musical Instruments:Microphones & Accessories:Microphones:Wireless Microphones & Systems",
 "products": 8885}
```

### 第2步: 並行獲取市場核心資料

**同時呼叫：**

1. `market_research` — 市場整體資料
   - 引數模式：`request` 巢狀物件
   - `nodeIdPath`: 第1步獲取的節點路徑
   - `topNum`: 10
   - `size`: 50

2. `market_research_statistics` — 深入統計
   - 引數模式：`request` 巢狀物件
   - `topN`: 10
   - `newProduct`: 預設6

### 第3步: 並行多維分佈分析

並行呼叫以下 12 個工具（無資料依賴）：
1. `market_price_distribution` — 價格區間分佈
2. `market_brand_concentration` — 品牌集中度
3. `market_product_concentration` — 商品集中度
4. `market_seller_concentration` — 賣家集中度
5. `market_rating_distribution` — 評分值分佈
6. `market_ratings_count_distribution` — 評分數分佈
7. `market_listing_date_distribution` — 上架時間分佈
8. `market_seller_country_distribution` — 賣家所屬地分佈
9. `market_seller_type_concentration` — 發貨型別分佈
10. `market_ebc_distribution` — A+與影片分佈
11. `market_product_demand_trend` — 需求趨勢
12. `market_listing_trend_distribution` — 上架趨勢分佈（🆕新增工具）

### 第4步: 生成並儲存市場分析報告

**儲存兩份檔案（必須，禁止僅列印到控制檯）：**

1. **原始資料** → `{類別目錄}/research_data.json`
   - 所有工具呼叫的原始返回 JSON，方便後續複查
2. **分析報告** → `{類別目錄}/market_report.md`
   - 結構化 Markdown 報告

**報告結構：**
1. **市場概覽** — 商品總數、品牌數、賣家數、月總銷量/銷售額、均價、平均評分
2. **市場吸引力評分**（1-10分各維度）：市場規模、增長性、利潤空間、競爭強度、新品友好度、進入門檻 → 綜合評分
3. **競爭格局** — 頭部集中度、品牌/賣家結構
4. **價格與利潤分析** — 各價格帶分佈、最佳定價建議
5. **新品進入評估** — 新品佔比、評論門檻、內容投入建議
6. **風險與機會** — 主要風險和差異化方向
7. **結論與建議** — 是否推薦進入、策略建議

### 刻度陷阱
- 集中度 `top*Crn` / 新品佔比 `l*NewRatio` 為 0~1，展示 ×100
- `returnRatio`/`fbaProportion` 已是百分數，不再換算
- 根節點統計全 0，必須選葉子節點
- `sellerLocation` 多選需拆單值再並集
- `nodeLabelLocale`（中文翻譯）不可靠，以英文 `nodeLabelPath` 為準

### 資料解析要點

`market_research` 返回的 `data.items` 既包含子市場，也可能包含父節點自身彙總行。
可透過 `ranking` 欄位排序，過濾 `totalProducts` 資料異常的條目。

分佈類工具（market_brand_concentration 等）的 `data` 結構不統一：
- 部分直接返回陣列：`data: [{...}]`
- 部分返回物件：`data: { items: [{...}] }`
- 安全取值：先判 `isinstance(data, dict)` 再 `.get('items', [])`
