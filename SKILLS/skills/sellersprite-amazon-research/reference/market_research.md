# `market_research` — 選市場 / 市場全景分析

對應網頁：大資料選品 → 選市場（`POST /v2/market-research`）

## 用途
給父類目（節點/關鍵詞）+ 多維篩選，返回細分市場列表及 ~100 個市場級指標。

## 請求引數

| 引數 | 型別 | 說明 |
|------|------|------|
| `marketplace` | string | 站點 |
| `nodeIdPath` | string | 類目節點 `parentId:childId`（優先） |
| `keyword` / `departmentKeyword` | string | 類目關鍵詞 |
| `month` | string | yyyyMM |
| `newProduct` | int | 新品定義月數：1/3/6/12，預設 6 |
| `topNum` | int | 頭部商品數，預設 10 |
| `sellerLocation` | string | 賣家所屬地（僅單值有效） |
| `size` | int | 返回條數 |

### 篩選引數刻度
- 集中度（`*Crn`）/佔比（`*Proportion`）：**0~1 小數**
  - 網頁按百分比填則需 ÷100

## 響應欄位

| 欄位 | 含義 | 刻度 |
|------|------|------|
| `nodeLabelName/path` | 細分市場名/路徑 | |
| `topProducts/brands/sellers` | 樣本商品/品牌/賣家數 | |
| `totalProducts` | 類目在售商品總數 | |
| `totalUnits/totalRevenue` | 樣本月總銷量/銷售額 | |
| `avgUnits/avgRevenue/avgPrice/avgBsr/avgRating/avgRatings` | 各項均值 | |
| `top{3,5,10,20}{Product,Brand,Seller}Crn` | 分層集中度 | **0~1，展示×100** |
| `fbaProportion/fbmProportion/amazonSelfProportion` | 賣家結構 | **已是百分數** |
| `returnRatio` | 退貨率 | **已是百分數** |
| `l{1,3,6,12}NewRatio` / `NewCount` | 新品佔比/數量 | Ratio **0~1，展示×100** |

## 網頁→MCP 改名
`HeadListing*→Top*`、`*Ratio→*Proportion`、`*Sales→*Units`、`*Reviews→*Ratings`、`*TotalProducts→*GoodsCount`、`marketId→marketplace`、`monthName→month`、`topn→topNum`、`newReleaseNum→newProduct`

## 市場分佈工具集

| 工具 | 用途 |
|------|------|
| `market_price_distribution` | 價格區間分佈 |
| `market_brand_concentration` | 品牌集中度 |
| `market_product_concentration` | 商品集中度 |
| `market_seller_concentration` | 賣家集中度 |
| `market_rating_distribution` | 評分值分佈 |
| `market_ratings_count_distribution` | 評分數分佈 |
| `market_listing_date_distribution` | 上架時間分佈 |
| `market_seller_country_distribution` | 賣家所屬地分佈 |
| `market_seller_type_concentration` | 發貨型別分佈 |
| `market_ebc_distribution` | A+頁面與影片分佈 |
| `market_product_demand_trend` | 需求趨勢 |
| `market_research_statistics` | 市場深入統計 |

## 分佈工具實際欄位名（實測，避開陷阱）

分佈工具返回的 `data` 是**直接陣列**（非 `{items: [...]}`），欄位名與 `market_research` 完全不同。

### 公共欄位
大多數分佈工具共用以下欄位（注意不是 `totalProducts` / `totalProductsProportion`）：

| 工具返回欄位 | 含義 | 刻度 |
|------------|------|------|
| `products` / `asinNum` | ASIN/商品數 | 整數 |
| `units` | 樣本銷量 | 整數 |
| `revenue` | 樣本銷售額 | float |
| `unitsRatio` | 銷量佔比 | **0~1 小數**，展示 ×100 |
| `revenueRatio` | 銷售額佔比 | **0~1 小數**，展示 ×100 |
| `asinRatio` | ASIN佔比（配送型別專用） | **0~1 小數**，展示 ×100 |
| `productsRatio` | ASIN佔比（A+專用） | **已是百分數**，不換算 |

### 各工具獨有欄位

| 工具 | 獨有欄位 | 說明 |
|------|---------|------|
| `market_price_distribution` | `label`(價格帶如"0-150"), `products`, `units`, `revenue`, `unitsRatio` | label 是價格區間字串 |
| `market_brand_concentration` | `brand`, `ranking`, `products`, `newProducts`, `avgPrice`, `ratings`, `rating`, `totalUnits`, `totalRevenue`, `totalUnitsRatio` | **`totalUnits` 不是 `units`** |
| `market_seller_concentration` | `sellerName`, `sellerId`, `totalUnits`, `totalRevenue`, `totalUnitsRatio` | 與品牌結構類似 |
| `market_seller_country_distribution` | `country`(=label), `products`, `units`, `revenue`, `unitsRatio` | 用 `country` 欄位 |
| `market_seller_type_concentration` | `asinNum`, `asinRatio`, `units`, `unitsRatio`, `productNum` | 用 `asinNum` 非 `products` |
| `market_rating_distribution` | `label`(評分割槽間), `products`, `units`, `unitsRatio` | |
| `market_ratings_count_distribution` | `label`(評分數區間), `products`, `units`, `unitsRatio` | |
| `market_listing_date_distribution` | `label`(時間), `products`, `units`, `unitsRatio` | 樣本較小時可能全 0 |
| `market_ebc_distribution` | `label`, `products`, `productsRatio`, `units`, `unitsRatio` | `productsRatio` 已是 % |
| `market_product_demand_trend` | `label`(月份), `products`, `units`, `revenue` | |
| `market_product_concentration` | `label`, `asinNum`, `unitsRatio` | |

## 陷阱
1. 根節點統計全 0，必須選葉子節點
2. 集中度 0~1 展示 ×100；`returnRatio`/`*Proportion` 不換算
3. `sellerLocation` 多選無效，需拆單值再並集
4. 月份未就緒取最近自然月
