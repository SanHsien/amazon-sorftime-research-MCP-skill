# `keyword_miner` — 關鍵詞挖掘 / 種子詞擴充套件

對應網頁：關鍵詞最佳化 → 關鍵詞挖掘（`POST /v3/api/keyword-miner`）

## 用途
輸入種子詞（或 ASIN），挖掘相關長尾詞及需求/競爭指標。

## 請求引數

| 引數 | 型別 | 說明 |
|------|------|------|
| `marketplace` | string | 站點（1=US,2=CA,...見下文） |
| `keyword` | string | 種子詞或 ASIN |
| `month` / `historyDate` | string | yyyyMM |
| `page/size` | int | 分頁 |
| `order.field` / `order.desc` | string/bool | 預設 searches |
| `filterRootWord` | int | 0=全部 1=僅詞根 |
| `includeKeywords/excludeKeywords` | string | 包含/排除關鍵詞 |
| `keywordList` | string | 批次精確查詢 |
| `minRelevancy/minSearchRank/minSearch` | 區間篩選 | 服務端直名引數 |
| `minPurchases/minPurchasesRate/minSPR` | 區間篩選 | |
| `minTitleDensity/minProducts` | 區間篩選 | |
| `minSupplyDemandRatio/minAdProducts` | 區間篩選 | |
| `minMonopolyClickRate/minBid/minWordCount` | 區間篩選 | |

### 市場編碼
1=US 2=CA 3=UK 4=DE 5=FR 6=IT 7=ES 8=JP 9=IN 10=MX 11=BR 12=AU 13=AE

### 客戶端兜底篩選（MCP 無對應區間引數）
`impressions`、`clicks`、`cvsShareRate`：在客戶端對響應過濾

## 響應欄位

| 欄位 | 說明 | 刻度 |
|------|------|------|
| `keyword` | 關鍵詞 | |
| `searches/purchases` | 搜尋量/購買量 | |
| `purchaseRate` | 購買率 | **0~1，展示×100** |
| `products/adProducts` | 商品數/廣告商品數 | |
| `supplyDemandRatio` | 供需比 | **真實比值** |
| `avgPrice/avgRating` | 均價/平均評分 | |
| `bid/bidMin/bidMax` | PPC 競價 | |
| `cvsShareRate` | 轉化份額 | **0~1，展示×100** |
| `titleDensity` | 標題密度 | |
| `spr` | SPR 值 | |
| `monopolyClickRate` | 點選集中度 | **0~1，展示×100** |
| `clicks/impressions` | 點選/曝光 | |
| `wordCount` | 詞數 | |
| `departments` | 所屬類目 | |

## 陷阱
1. `purchaseRate/cvsShareRate/monopolyClickRate` 為 0~1，展示 ×100
2. `supplyDemandRatio` 真實比值不換算
3. 種子詞擴充套件用 `keyword_miner`；類目關鍵詞選品用 `keyword_research`
