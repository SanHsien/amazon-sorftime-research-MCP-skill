# `competitor_lookup` — 查競品 / 商品列表查詢

對應網頁：大資料選品 → 查競品（`POST /v3/api/competing-lookup`）

## 用途
按 ASIN / 關鍵詞 / 品牌 / 賣家 / 類目 查詢 Amazon 商品列表。

## 請求引數

| 引數 | 型別 | 說明 |
|------|------|------|
| `marketplace` | string | 站點 |
| `asins` | array | ASIN 陣列，最多 40 |
| `keyword` | string | 關鍵詞 |
| `month` | string | yyyyMM |
| `brand` | string | 品牌名 |
| `sellerName` | string | 賣家名 |
| `nodeIdPath/nodeIdPaths` | string/array | 類目節點 |
| `matchType` | int | 1=片語 2=模糊 3=精準 |
| `page/size` | int | 分頁 |
| `variation` | string | "Y" 去重 |
| `order.field` / `order.desc` | string/bool | 排序 |

## 響應欄位改名

| 網頁 API | MCP 欄位 |
|----------|----------|
| `totalUnits` | **`units`** |
| `totalAmount` | **`revenue`** |
| `reviews` | **`ratings`** |
| `bsrRank` | **`bsr`** |
| `sellerType` | **`fulfillment`** |

## 陷阱
1. ASIN 須真實存在，否則 `total=0`
2. 響應讀 MCP 名（units/revenue/ratings/bsr）
3. 注意：這是列表查詢，與單 ASIN 深度分析（asin_detail）不同
