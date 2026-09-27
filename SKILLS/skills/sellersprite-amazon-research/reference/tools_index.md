# SellerSprite MCP 工具清單（43 個）

> 實際工具數 43，文件原標 38。2026-07-05 實測驗證。

## ASIN 分析（7）
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `asin_detail` | ASIN 詳情查詢 | `marketplace`, `asin` |
| `asin_prediction` | 銷量預測 | `marketplace`, `asin` |
| `asin_sales_trend` | 銷量趨勢 | `marketplace`, `asin` |
| `asin_coupon_trend` | 優惠趨勢 | `marketplace`, `asin` |
| `asin_detail_with_coupon_trend` | 詳情+優惠整合 | `marketplace`, `asin` |
| `keepa_info` | Keepa 歷史趨勢 | `marketplace`, `asin` |
| `bsr_prediction` | BSR 銷量預估 | `marketplace`, `bsr`, `categoryId` |

## 商品與競品（3）
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `product_research` | 選產品/高階篩選 | `request`（巢狀物件） |
| `competitor_lookup` | 查競品列表 | `request`（巢狀物件） |
| `product_node` | 類目節點查詢 | `request`（巢狀物件） |

## 關鍵詞（4）
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `keyword_miner` | 關鍵詞挖掘（種子詞擴充套件） | `request`（巢狀物件） |
| `keyword_research` | 關鍵詞研究（帶增長率） | `request`（巢狀物件） |
| `keyword_research_trends` | 關鍵詞趨勢 | `marketplace`, `keyword` |
| `keyword_order` | 關鍵詞排名與轉化質量 | `request`（巢狀物件） |

## 流量（6）
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `traffic_keyword` | 關鍵詞反查（ASIN 流量詞） | `request`（巢狀物件） |
| `traffic_keyword_stat` | 關鍵詞流量統計 | `marketplace`, `asin` |
| `traffic_source` | 流量來源分析 | `marketplace`, `asin`, **`q`**（扁平引數） |
| `traffic_listing_stat` | Listing 流量統計 | `marketplace`, `asin` |
| `traffic_listing` | Listing 流量詳情 | `request`（巢狀物件） |
| `traffic_extend` | 關鍵詞拓展（區間篩選） | `request`（巢狀物件） |

> ⚠️ `traffic_source` 雖然文件標為 `request` 巢狀，但實際需用**扁平引數** + `"q": "asin"`：`{"marketplace":"US","asin":"B0XXX","q":"asin"}`。`q` 值為 `"asin"` 時查詢該 ASIN 的流量來源結構。

## 市場研究（15）
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `market_research` | 市場全景資料 | `request`（巢狀物件） |
| `market_research_statistics` | 市場深入統計 | `request`（巢狀物件） |
| `market_price_distribution` | 價格區間分佈 | `request`（巢狀物件） |
| `market_brand_concentration` | 品牌集中度 | `request`（巢狀物件） |
| `market_product_concentration` | 商品集中度 | `request`（巢狀物件） |
| `market_seller_concentration` | 賣家集中度 | `request`（巢狀物件） |
| `market_rating_distribution` | 評分值分佈 | `request`（巢狀物件） |
| `market_ratings_count_distribution` | 評分數分佈 | `request`（巢狀物件） |
| `market_listing_date_distribution` | 上架時間分佈 | `request`（巢狀物件） |
| `market_listing_trend_distribution` | 上架趨勢分佈 | `request`（巢狀物件） |
| `market_seller_country_distribution` | 賣家所屬地分佈 | `request`（巢狀物件） |
| `market_seller_type_concentration` | 發貨型別分佈 | `request`（巢狀物件） |
| `market_ebc_distribution` | A+頁面與影片分佈 | `request`（巢狀物件） |
| `market_product_demand_trend` | 需求趨勢 | `request`（巢狀物件） |

## ABA/趨勢（4）
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `aba_research_weekly` | ABA 週資料 | `request`（巢狀物件） |
| `aba_research_monthly` | ABA 月資料 | `request`（巢狀物件） |
| `aba_research_trend` | ABA 趨勢 | `marketplace`, `keyword` |
| `google_trend` | Google 趨勢 | `request`（巢狀物件） |

## 評論（1）
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `review` | 評論資料 | `marketplace`, `asin` |

## 商標（4）🆕
| 工具名 | 用途 | 必填引數 |
|--------|------|---------|
| `trademark_list` | 商標列表查詢 | `request`（巢狀物件） |
| `trademark_detail` | 商標詳情 | `office`, `brandId` |
| `trademark_stats` | 商標統計 | `request`（巢狀物件） |
| `trademark_country_list` | 商標國家列表 | 無 |

## 引數模式說明

### 模式 A：扁平引數
工具直接在頂層接受 `marketplace`, `asin`, `keyword` 等欄位。

### 模式 B：`request` 巢狀物件（最常用）
絕大多數篩選類工具使用 `request` 引數，內部結構如：
```json
{
  "marketplace": "US",
  "nodeIdPath": "11091801:11974521:8882489011:11974711",
  "topNum": 10,
  "size": 50
}
```
呼叫時將欄位全部包裹在 `request` 鍵下。
