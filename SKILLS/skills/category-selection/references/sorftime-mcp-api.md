# Sorftime MCP API 介面文件

## 呼叫方式
```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{...}}}'
```

---

## 一、產品相關介面

### 1.1 產品詳情 (product_detail)
**呼叫消耗**: 1

**用途**: 查詢亞馬遜電商平臺上產品的詳情資料

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | 是 | 亞馬遜站點 US/GB/DE/FR/IN/CA/JP/ES/IT/MX/AE/AU/BR/SA |
| asin | string | 是 | 產品ASIN |

**返回資料**: 標題、價格、評分、評論數、品牌、類目、排名、銷量等

---

### 1.2 產品子體明細 (product_variations)
**呼叫消耗**: 1

**用途**: 查詢亞馬遜電商平臺產品的子體明細

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | 是 | 亞馬遜站點 |
| asin | string | 是 | 產品ASIN（僅支援單ASIN） |

---

### 1.3 產品歷史趨勢 (product_trend)
**呼叫消耗**: 1

**用途**: 查詢產品的歷史趨勢資料，支援月銷量/月銷額/價格/排名趨勢

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| asin | string | 是 | 產品ASIN |
| productTrendType | string | 否 | 月銷量趨勢/月銷額趨勢/價格趨勢/所屬大類排名趨勢 |

---

### 1.4 產品評論 (product_reviews)
**呼叫消耗**: 1

**用途**: 查詢產品近一年的使用者留評，最多返回100條

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| asin | string | 是 | 產品ASIN |
| reviewType | string | 否 | 全部（不限星級）/積極評論（4-5星）/消極評論（1-3星） |

---

### 1.5 產品流量關鍵詞 (product_traffic_terms)
**呼叫消耗**: 1

**用途**: 產品反查關鍵詞，返回產品在哪些關鍵詞前3頁中曝光

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| asin | string | 是 | 產品ASIN |
| page | int | 否 | 頁碼索引，預設第1頁，每頁50條 |

---

### 1.6 競品關鍵詞佈局 (competitor_product_keywords)
**呼叫消耗**: 1

**用途**: 獲取競品在各核心關鍵詞下的曝光位置（自然曝光）

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| asin | string | 是 | 產品ASIN |
| page | int | 否 | 頁碼索引，預設第1頁 |

---

### 1.7 產品關鍵詞排名趨勢 (product_keyword_rank_trend)
**呼叫消耗**: 1

**用途**: 產品在指定關鍵詞下曝光的排名趨勢

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| asin | string | 是 | 產品ASIN |
| keyword | string | 是 | 關鍵詞 |
| page | int | 否 | 頁碼索引，預設第1頁 |

---

### 1.8 產品搜尋 (product_search)
**呼叫消耗**: 1

**用途**: 搜尋或篩選亞馬遜產品，支援多維度篩選實現選品功能

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| searchName | string | 否 | 搜尋產品名稱 |
| brand | string | 否 | 篩選品牌 |
| delivery_type | string | 否 | 發貨方式 |
| month_sales_volume_range | string | 否 | 月銷量範圍[x,y] |
| price_range | string | 否 | 價格範圍[x,y] |
| property_name | string | 否 | 標題或屬性包含詞 |
| ratings_count_range | string | 否 | 評論數量範圍[x,y] |
| ratings_range | string | 否 | 星級範圍[x,y] |
| seasonal_popular_product | string | 否 | 熱銷旺季產品 |
| seller_name | string | 否 | 賣家名稱 |
| subcategory_rank_range | string | 否 | 細分類目排名範圍[x,y] |
| variation_count_range | string | 否 | 子體數量範圍[x,y] |
| sortby_potential_index | string | 否 | 按潛力指數排序 |

---

### 1.9 潛力產品搜尋 (potential_product_search)
**呼叫消耗**: 1

**用途**: 搜尋亞馬遜平臺上的潛力產品

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 支援的站點 US/GB/DE |
| searchName | string | 否 | 產品名稱 |
| price_range | string | 否 | 價格範圍[x,y] |
| month_sales_volume_range | string | 否 | 月銷量範圍[x,y] |
| delivery_type | string | 否 | 發貨方式 |

---

## 二、類目相關介面

### 2.1 類目名稱搜尋 (category_name_search)
**呼叫消耗**: 1

**用途**: 基於名稱查詢細分類目市場，返回nodeid和name

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| searchName | string | 是 | 類目市場名稱 |

---

### 2.2 類目樹結構 (category_tree)
**呼叫消耗**: 5

**用途**: 查詢類目產品的特點

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| searchName | string | 是 | 類目名稱 |

---

### 2.3 細分類目報告 (category_report)
**呼叫消耗**: 1

**用途**: 細分類目實時資料包告，基於Top100產品統計

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| nodeId | string | 否 | 細分類目nodeid |

---

### 2.4 細分類目歷史報告 (category_history_report)
**呼叫消耗**: 1

**用途**: 細分類目歷史指定時間段資料包告

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| nodeId | string | 否 | 細分類目nodeid |
| startDate | string | 是 | 起始時間(yyyy-MM-dd) |
| endDate | string | 否 | 截止時間，最長40天 |

---

### 2.5 類目趨勢 (category_trend)
**呼叫消耗**: 1

**用途**: 查詢類目市場趨勢資料，基於Top100統計

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| nodeId | string | 是 | 細分類目nodeid |
| trendIndex | string | 是 | 趨勢型別（見下方） |

**趨勢型別 (trendIndex)**:
- 類目月銷量趨勢
- 品牌數量趨勢
- 賣家數量趨勢
- 平均售價趨勢
- 平均評論數量趨勢
- 平均星級趨勢
- 上架3個月內新品銷量佔比趨勢
- 亞馬遜自營銷量佔比趨勢
- 銷量前3的產品銷量佔比趨勢
- 銷量前3的品牌銷量佔比趨勢
- 銷量前3的賣家銷量佔比趨勢

---

### 2.6 類目市場搜尋 (category_market_search)
**呼叫消耗**: 1

**用途**: 查詢或搜尋細分類目市場

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| searchName | string | 否 | 類目市場名稱 |
| month_sales_volume_range | string | 否 | 月銷量範圍[x,y] |
| ratings_range | string | 否 | 星級範圍[x,y] |
| ratings_count_range | string | 否 | 評論數範圍[x,y] |
| price_range | string | 否 | 平均銷售價範圍[x,y] |
| seasonal_popular_product | string | 否 | 熱銷旺季 |
| top3Product_sales_share | string | 否 | Top3產品銷量佔比[x,y](0-1) |
| amazonOwned_sales_share | string | 否 | 亞馬遜自營佔比[x,y](0-1) |
| top100_top400_sales_share | string | 否 | Top100在Top400佔比[x,y](0-1) |
| newproduct_sales_share | string | 否 | 新品銷量佔比[x,y](0-1) |

---

### 2.7 類目核心關鍵詞 (category_keywords)
**呼叫消耗**: 1

**用途**: 查詢細分類目市場的核心關鍵詞

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| nodeId | string | 是 | 細分類目nodeid |
| page | int | 否 | 頁碼索引，預設第1頁 |

---

## 三、關鍵詞相關介面

### 3.1 關鍵詞詳情 (keyword_detail)
**呼叫消耗**: 1

**用途**: 查詢熱搜關鍵詞詳情

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| keyword | string | 是 | 查詢的關鍵詞 |

---

### 3.2 關鍵詞搜尋結果 (keyword_search_result)
**呼叫消耗**: 1

**用途**: 查詢關鍵詞搜尋結果自然位產品清單

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| searchKeyword | string | 是 | 查詢的關鍵詞 |
| page | int | 否 | 頁碼索引，預設第1頁 |

---

### 3.3 關鍵詞歷史趨勢 (keyword_trend)
**呼叫消耗**: 1

**用途**: 查詢關鍵詞歷史趨勢（搜尋量/搜尋排名/CPC價格）

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| searchKeyword | string | 是 | 查詢的關鍵詞 |

---

### 3.4 關鍵詞延伸詞 (keyword_related_words)
**呼叫消耗**: 1

**用途**: 查詢關鍵詞的延伸詞，用於發現長尾詞

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | 亞馬遜站點 |
| searchKeyword | string | 是 | 查詢的關鍵詞 |
| page | int | 否 | 頁碼索引，預設第1頁 |

---

## 四、關鍵詞詞庫管理介面

### 4.1 新增關鍵詞收藏 (add_keyword)
**呼叫消耗**: 1

**引數**: site, keyword, dict(可選)

---

### 4.2 移動關鍵詞到收藏夾 (move_keyword)
**呼叫消耗**: 1

**引數**: site, keyword, toDict, fromDict(可選)

---

### 4.3 刪除關鍵詞收藏 (remove_keyword)
**呼叫消耗**: 1

**引數**: site, keyword, dict(可選)

---

### 4.4 查詢收藏夾列表 (query_keyword_dict_list)
**呼叫消耗**: 1

**引數**: site, page

---

### 4.5 查詢收藏的詞 (query_keyword_dict)
**呼叫消耗**: 1

**引數**: site, dict(可選，all查詢全部), page

---

## 五、1688 供貨平臺介面

### 5.1 1688產品搜尋 (products_1688)
**呼叫消耗**: 1

**用途**: 透過1688平臺找產品的採購貨源，分析產品採購成本價

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| searchName | string | 是 | 查詢的產品名稱 |
| page | int | 否 | 頁碼索引，預設第1頁，每頁50條 |

---

## 六、TikTok 電商平臺介面

### 6.1 TikTok產品搜尋 (tiktok_product_search)
**呼叫消耗**: 1

**用途**: 查詢產品在TikTok平臺上的相似產品，分析銷售情況

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| searchName | string | 是 | 查詢的產品名稱 |
| page | int | 是 | 頁碼索引，預設第1頁，每頁50條 |

---

### 6.2 TikTok產品詳情 (tiktok_product_detail)
**呼叫消耗**: 1

**用途**: 查詢TikTok平臺產品詳情

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 產品ID |

---

### 6.3 TikTok帶貨影片 (tiktok_product_videos)
**呼叫消耗**: 1

**用途**: 查詢TikTok平臺產品的帶貨影片

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 產品ID |
| page | int | 是 | 頁碼索引，預設第1頁，每頁50條 |

---

### 6.4 TikTok帶貨達人分析 (tiktok_product_influencers)
**呼叫消耗**: 1

**用途**: TikTok平臺產品的帶貨達人分析

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 產品ID |

---

### 6.5 TikTok產品趨勢 (tiktok_product_trend)
**呼叫消耗**: 1

**用途**: 查詢TikTok平臺產品趨勢，返回銷量、價格、星級、評論數量、新增帶貨影片數、新增帶貨達人數

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 產品ID |

---

### 6.6 TikTok達人搜尋 (tiktok_influencer_search)
**呼叫消耗**: 1

**用途**: 按產品名稱搜尋相關帶貨達人

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| searchName | string | 是 | 搜尋的產品名稱 |
| page | int | 是 | 頁碼索引，預設第1頁，每頁50條 |

---

### 6.7 TikTok類目搜尋 (tiktok_category_name_search)
**呼叫消耗**: 1

**用途**: 按名稱搜尋TikTok上相關類目市場，返回類目市場名稱和nodeid

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| searchName | string | 是 | 搜尋的產品名稱 |

---

### 6.8 TikTok類目報告 (tiktok_category_report)
**呼叫消耗**: 1

**用途**: 查詢TikTok電商平臺指定類目的類目資料包告

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站點 US/GB/MY/PH/VN/ID |
| nodeId | string | 是 | 類目市場nodeid，可透過tiktok_category_name_search獲得 |

---

## 支援的平臺站點

### 亞馬遜 (14個站點)
`US`, `GB`, `DE`, `FR`, `IN`, `CA`, `JP`, `ES`, `IT`, `MX`, `AE`, `AU`, `BR`, `SA`

### TikTok (6個站點)
`US`, `GB`, `MY`, `PH`, `VN`, `ID`

### 1688 供貨平臺
國內批發採購平臺

## 呼叫限制
- 大部分介面呼叫消耗: 1
- category_tree: 5
- 返回資料為SSE格式，需解析

---

*最後更新: 2026-03-03*
