# `product_research` — 選產品 / 高階商品篩選

對應網頁：大資料選品 → 選產品（`POST /v3/api/product-research`）

## 用途
按關鍵詞 + 多維條件（銷量/價格/BSR/評分/利潤/配送/賣家等）篩選 Amazon 商品。

## 請求引數

| 引數 | 型別 | 說明 |
|------|------|------|
| `marketplace` | string | 站點（US/JP/UK/DE/FR/IT/ES/CA/IN） |
| `keyword` | string | 搜尋關鍵詞 |
| `matchType` | int | 1=片語 2=模糊 3=精準 |
| `month` | string | yyyyMM |
| `minUnits/maxUnits` | int | 月銷量區間 |
| `minRevenue/maxRevenue` | float | 月銷售額區間 |
| `minPrice/maxPrice` | float | 價格區間 |
| `minSubBsrRank/maxSubBsrRank` | int | 子類 BSR 排名 |
| `minRating/maxRating` | float | 評分割槽間 |
| `minRatings/maxRatings` | int | 評分數區間 |
| `minRatingsCv` | int | 月新增評分數 |
| `minUnitsCr` | float | 月銷量增長率 |
| `minFba` | float | 最低 FBA 運費 |
| `minLqs` | int | Listing 質量分 |
| `minProfit/maxProfit` | float | 利潤區間 |
| `fulfillment` | string | FBA,FBM,AMZ（逗號字串） |
| `includeBrands/excludeBrands` | string | 品牌白/黑名單（逗號字串） |
| `includeSellers/excludeSellers` | string | 賣家白/黑名單（逗號字串） |
| `sellerNation` | string | 賣家所屬地 |
| `badgeAC/badgeBS/badgeNR` | string | "Y" 過濾 |
| `page/size` | int | 分頁，size 預設 50 最大 100 |
| `order.field` / `order.desc` | string/bool | 排序欄位和方向 |

## 響應欄位改名

| 網頁 API | MCP 欄位 | 說明 |
|----------|----------|------|
| `totalUnits` | **`units`** | 月銷量 |
| `totalAmount` | **`revenue`** | 月銷售額 |
| `reviews` | **`ratings`** | 評分數 |
| `bsrRank` | **`bsr`** | BSR 排名 |
| `sellerType` | **`fulfillment`** | FBA/FBM/AMZ |
| `averagePrice` | `averagePrice` | 均價 |
| `amzUnit` | `amzUnit` | 亞馬遜自營銷量 |

## 陷阱
1. 響應欄位讀 MCP 名（units/revenue/ratings/bsr），不用網頁 API 名
2. 當前月 `units/revenue` 可能為 None，取最近自然月
3. 黑白名單/配送方式傳逗號字串；badges 傳 "Y"
