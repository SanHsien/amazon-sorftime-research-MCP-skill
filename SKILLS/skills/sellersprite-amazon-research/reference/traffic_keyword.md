# `traffic_keyword` — 關鍵詞反查 / ASIN 流量詞

對應網頁：關鍵詞最佳化 → 關鍵詞反查（`POST /v3/api/relation/reversing`）

## 用途
輸入 ASIN，返回其實際獲得曝光/流量的關鍵詞列表。

## 請求引數

| 引數 | 型別 | 說明 |
|------|------|------|
| `marketplace` | string | 站點 |
| `asin` | string | ASIN（單值） |
| `month` | string | yyyyMM |
| `keyword` | string | 關鍵詞過濾 |
| `size/page` | int | 分頁 |
| `badges` | string | 多選，大小寫不敏感 |
| `order.field` / `order.desc` | string/bool | 排序，預設 trafficPercentage |

### 配套工具
- `traffic_extend`：支援區間篩選，但欄位不全
- 推薦做法：`traffic_keyword` 全欄位取數，客戶端過濾

## 響應欄位（零改名）

| 欄位 | 說明 | 刻度 |
|------|------|------|
| `keyword` | 關鍵詞 | |
| `searches` | 搜尋量 | |
| `purchases` | 購買量 | |
| `purchaseRate` | 購買率 | **0~1，展示×100** |
| `bid/bidMin/bidMax` | PPC 競價 | |
| `rankPosition` | 自然排名物件 `{page,index,position}` | 取 `.position` |
| `adPosition` | 廣告排名物件 | 取 `.position` |
| `supplyDemandRatio` | 供需比 | **真實比值** |
| `trafficPercentage` | 流量佔比 | **0~1，展示×100** |
| `naturalRatio/adRatio` | 自然/廣告佔比 | **0~1，展示×100** |
| `monopolyClickRate` | 點選集中度 | **0~1，展示×100** |
| `top3ClickingRate/top3ConversionRate` | Top3 點選/轉化率 | **0~1，展示×100** |
| `clicks/impressions` | 點選/曝光 | |
| `products` | 商品數 | |
| `calculatedWeeklySearches` | 周均搜尋量 | |

## 陷阱
1. `purchaseRate/trafficPercentage/naturalRatio/adRatio` 為 0~1，展示 ×100
2. `supplyDemandRatio` 真實比值不換算
3. `rankPosition`/`adPosition` 是物件，取 `.position` 展示
4. 別用 `keyword_order` 當反查全集（欄位少）
