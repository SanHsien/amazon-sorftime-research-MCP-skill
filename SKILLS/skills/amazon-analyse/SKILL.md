---
name: "amazon-analyse"
description: "對亞馬遜競品Listing進行全維度穿透分析，包括文案邏輯、評論分析、關鍵詞分析、市場動態等。分析完成後自動儲存為Markdown報告文件到reports/目錄。Invoke when user uses /amazon-analyse command with a product ASIN."
---

# 亞馬遜競品Listing全維度穿透分析

## 快速參考

| 步驟 | 工具/操作 | 用途 |
|------|----------|------|
| 1. 驗證ASIN | `product_search` | 確認產品存在 |
| 2. 產品詳情 | `product_detail` | 獲取基礎資料 |
| 3. 流量關鍵詞 | `product_traffic_terms` | 分析流量來源 |
| 4. 競品關鍵詞 | `competitor_product_keywords` | 分析競品佈局 |
| 5. 使用者評論 | `product_reviews` | 評論情感分析 |
| 6. 歷史趨勢 | `product_trend` | 銷量趨勢分析 |
| 7. 生成報告 | 綜合分析 | 輸出完整報告 |
| 8. 儲存文件 | `Write` 工具 | 儲存為 MD 檔案 |

**呼叫格式**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

## 觸發條件
當使用者使用 `/amazon-analyse` 命令並提供一個亞馬遜競品 ASIN 時，立即啟動此分析流程。

## 角色設定
你是一位擁有10年經驗的"亞馬遜頂級運營總監"和"品牌戰略官"。你不僅精通A9和Rufus演算法，更擅長解析品牌背後的營銷心理學與競爭策略。你的任務是透過產品資料表面現象，還原對手的戰略佈局、運營套路和市場定位。

## 資料來源

本分析使用 **Sorftime MCP** 服務獲取亞馬遜資料。

**Sorftime MCP 是一個流式 HTTP 服務**，使用 Server-Sent Events (SSE) 協議返回資料。

**可用工具**：
| 工具名 | 功能 |
|--------|------|
| `product_search` | 產品搜尋（驗證ASIN用） |
| `product_detail` | 產品詳情 |
| `product_reviews` | 使用者評論（最多100條） |
| `product_traffic_terms` | 流量關鍵詞 |
| `competitor_product_keywords` | 競品關鍵詞佈局 |
| `product_trend` | 歷史趨勢（銷量/價格/排名） |
| `keyword_detail` | 關鍵詞詳情 |
| `category_tree` | 類目結構 |

**重要提示**：
- 所有資料需透過 curl POST 請求獲取
- 返回格式為 SSE (event: message + data: JSON)
- 中文內容使用 Unicode 轉義，需要解碼
- 大資料量會儲存到臨時檔案

## 分析流程

### 第一步：資訊收集與資料抓取

#### 預檢查：ASIN 有效性驗證

**重要**：在獲取資料前，先驗證 ASIN 是否存在於 Sorftime 資料庫中。

```bash
# 驗證 ASIN 是否存在
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

**如果返回 "未查詢到對應產品"**：
1. 使用 product_search 工具搜尋該 ASIN 或相關關鍵詞
2. 提示使用者確認 ASIN 是否正確
3. 檢查是否是正確的亞馬遜站點

#### 資料獲取方式

Sorftime MCP 使用 **Server-Sent Events (SSE)** 協議，需要透過 curl POST 請求呼叫。

**通用呼叫格式**：
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

**關鍵點**：
- `id` 每次請求遞增 (1, 2, 3...)
- 返回格式為 SSE: `event: message\ndata: {...}\n\n`
- 資料中的中文是 Unicode 轉義格式，需要解碼
- 大量資料會被儲存到臨時檔案，需用 Read 工具讀取

#### 1. 提取使用者輸入
   - ASIN (必填)
   - 亞馬遜站點 (預設 US，可選：US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA)
   - 使用者的產品核心優勢（用於生成針對性反擊建議）

#### 資料獲取步驟

按照以下順序獲取資料（可併發執行以提高效率）：

1. **product_detail** - 產品詳情
2. **product_reviews** - 使用者評論
3. **product_traffic_terms** - 流量關鍵詞
4. **competitor_product_keywords** - 競品關鍵詞佈局
5. **product_trend** - 歷史銷量趨勢

> 具體呼叫格式見下方 **Sorftime MCP 工具參考** 章節

### 第二步：執行四大維度分析

#### 第一部分：文案構建邏輯與關鍵詞分析 (The Brain)

**構建邏輯與方法論：**
- 拆解標題、五點描述的文字構建策略
- 分析是基於"痛點觸發"、"場景驅動"還是"引數壓制"
- 識別使用的敘事模板

**關鍵詞情報：**
- 從 `product_traffic_terms` 提取產品的核心流量詞
- 從 `competitor_product_keywords` 分析競品在各核心詞下的曝光位置
- 識別競品的自然曝光能力和獲流策略

**資料使用：**
- 使用 `product_traffic_terms` 資料分析產品流量來源
- 使用 `competitor_product_keywords` 評估競品關鍵詞佈局
- 使用 `keyword_detail` 深入分析核心詞指標

#### 第二部分：產品表現與市場定位 (The Face)

**產品基礎資料：**
- 價格、評分、評論數、類目排名
- 月銷量、銷售額估算
- FBA/FBM 配送方式

**市場表現：**
- 使用 `product_trend` 分析歷史銷量/價格趨勢
- 識別季節性波動和促銷活動影響
- 評估產品生命週期階段

**競爭力分析：**
- 使用 `product_report` 評估產品在類目中的位置
- Top100排名變化趨勢
- 與競品的價格/功能對比

#### 第三部分：評論定量與定性分析 (The Voice)

**量化資料概覽：**
- 明確分析樣本量（最多100條評論）
- 統計好評（4-5星）與差評（1-3星）分佈

**定性穿透分析：**
- **優勢聚類：** 使用者評論中反覆提到的優點
- **差評穿透：** 差評主要體現的核心問題（產品缺陷、描述不符、體驗問題）

**核心總結 (Top 3)：**
- 3條核心優勢（使用者為何購買）
- 3條核心痛點（使用者為何退貨/差評）
- 3條改進建議（我方產品最佳化方向）

#### 第四部分：市場動態與盲區掃描 (The Pulse)

**關鍵詞佈局分析：**
- 從 `competitor_product_keywords` 識別競品主要獲流詞
- 分析競品在熱搜詞下的排名能力
- 發現競品的長尾詞佈局策略

**市場機會識別：**
- 識別競品尚未覆蓋的高價值關鍵詞
- 發現評論中使用者提到但產品未滿足的需求
- 分析類目趨勢和競爭格局

**盲區掃描：**
- 識別潛在威脅（新品、價格戰、品牌差異化）
- 發現未被充分滿足的使用者痛點

### 第三步：輸出結構化報告

#### 報告輸出方式

1. **終端輸出**：直接在對話中展示完整報告
2. **文件儲存**：將報告儲存為 Markdown 檔案供後續查閱

**報告檔案命名規則**：
```
analysis_{ASIN}_{站點}_{日期}.md
例如: analysis_B07PQFT83F_US_20260302.md
```

**儲存位置**：
```
專案目錄/reports/
```

**儲存命令**：
```bash
# 1. 先檢查/建立 reports 目錄
mkdir -p reports/

# 2. 生成報告檔案路徑（使用當前日期）
FILENAME="reports/analysis_${ASIN}_${站點}_$(date +%Y%m%d).md"

# 3. 使用 Write 工具儲存完整報告內容
Write $FILENAME
```

**報告儲存最佳實踐**：
1. 每次分析都儲存獨立檔案，便於歷史對比
2. 檔名包含日期，支援多次分析同一產品
3. 報告開頭包含分析時間戳，確保資料時效性
4. 建議定期整理舊報告，歸檔到 `reports/archive/` 目錄

#### 按照以下結構輸出完整分析報告：

```markdown
# 亞馬遜競品Listing全維度穿透分析報告

## 分析物件
- ASIN: [ASIN]
- 亞馬遜站點: [站點]
- 分析時間: [時間]
- 資料來源: Sorftime MCP

## 第一部分：產品基礎資料
### 核心指標
- 產品標題: [標題]
- 品牌: [品牌]
- 價格: [價格]
- 評分: [評分] / 5.0
- 評論數: [評論數]
- 月銷量估算: [銷量]
- 類目排名: [排名]
- 配送方式: [FBA/FBM]

### 市場表現
- 歷史銷量趨勢: [分析]
- 價格波動規律: [分析]
- 生命週期階段: [判斷]

## 第二部分：關鍵詞佈局分析 (The Brain)
### 流量關鍵詞
- 核心流量詞列表
- 流量來源分佈
- 自然曝光能力

### 競品關鍵詞佈局
- 各熱搜詞下的排名位置
- 獲流關鍵詞數量
- 排名競爭力分析

### 文案構建邏輯
- 標題策略分析
- 五點描述策略
- 關鍵詞埋點策略

## 第三部分：評論定性分析 (The Voice)
### 評論資料概覽
- 總評分數: [評分]
- 好評率: [百分比]
- 分析樣本: [評論數量]

### 核心優勢 Top 3
1. [優勢1]
2. [優勢2]
3. [優勢3]

### 核心痛點 Top 3
1. [痛點1]
2. [痛點2]
3. [痛點3]

### 改進建議 Top 3
1. [建議1]
2. [建議2]
3. [建議3]

## 第四部分：競爭策略分析 (The Pulse)
### 競爭優勢
- [分析]

### 競爭劣勢
- [分析]

### 市場機會
- [分析]

### 潛在威脅
- [分析]

## 戰略反擊建議
基於使用者產品核心優勢，提供針對性的競爭策略建議。

### 關鍵詞策略
- [建議]

### 定價策略
- [建議]

### 產品最佳化方向
- [建議]

### Listing最佳化建議
- [建議]
```

---

## 參考文件

- [API 工具參考](references/api-tools-reference.md) - 完整的 curl 呼叫格式和故障排查
- [報告管理](references/report-management.md) - 報告生命週期管理和歸檔策略
- [Sorftime MCP API](references/sorftime-mcp-api.md) - 完整 API 介面文件

### 快速工具參考

| 工具 | 用途 | 呼叫消耗 |
|------|------|----------|
| `product_detail` | 產品詳情 | 1 |
| `product_reviews` | 使用者評論(最多100條) | 1 |
| `product_traffic_terms` | 流量關鍵詞反查 | 1 |
| `competitor_product_keywords` | 競品關鍵詞佈局 | 1 |
| `product_trend` | 歷史趨勢 | 1 |
| `keyword_detail` | 關鍵詞詳情 | 1 |

### 支援的站點
US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

### 注意事項
1. **ASIN格式**：確保ASIN格式正確，通常為10位字母數字組合
2. **站點選擇**：預設使用US站點
3. **評論資料**：最多返回100條評論
4. **併發請求**：可以同時發起多個請求提高效率
5. **API Key安全**：不要在程式碼中硬編碼API Key

---

---

## 參考資料

### Sorftime MCP 完整 API 文件
詳細的介面文件已儲存在 `references/sorftime-mcp-api.md`，包含：

#### 產品相關介面 (9個)
| 介面 | 用途 | 呼叫消耗 |
|------|------|----------|
| `product_detail` | 產品詳情 | 1 |
| `product_variations` | 產品子體明細 | 1 |
| `product_trend` | 歷史(銷量/價格/排名)趨勢 | 1 |
| `product_reviews` | 使用者評論(最多100條) | 1 |
| `product_traffic_terms` | 流量關鍵詞反查 | 1 |
| `competitor_product_keywords` | 競品關鍵詞佈局 | 1 |
| `product_keyword_rank_trend` | 關鍵詞排名趨勢 | 1 |
| `product_search` | 產品搜尋/篩選 | 1 |
| `potential_product_search` | 潛力產品搜尋 | 1 |

#### 類目相關介面 (7個)
| 介面 | 用途 | 呼叫消耗 |
|------|------|----------|
| `category_name_search` | 類目名稱搜尋(獲取nodeid) | 1 |
| `category_tree` | 類目樹結構 | 5 |
| `category_report` | 類目實時報告(Top100) | 1 |
| `category_history_report` | 類目歷史報告(最長40天) | 1 |
| `category_trend` | 類目趨勢(11種趨勢型別) | 1 |
| `category_market_search` | 類目市場搜尋/篩選 | 1 |
| `category_keywords` | 類目核心關鍵詞 | 1 |

#### 關鍵詞相關介面 (4個)
| 介面 | 用途 | 呼叫消耗 |
|------|------|----------|
| `keyword_detail` | 關鍵詞詳情 | 1 |
| `keyword_search_result` | 關鍵詞搜尋結果自然位 | 1 |
| `keyword_trend` | 關鍵詞歷史趨勢 | 1 |
| `keyword_related_words` | 關鍵詞延伸詞/長尾詞 | 1 |

#### 關鍵詞詞庫管理 (5個)
| 介面 | 用途 | 呼叫消耗 |
|------|------|----------|
| `add_keyword` | 新增關鍵詞收藏 | 1 |
| `move_keyword` | 移動到收藏夾 | 1 |
| `remove_keyword` | 刪除關鍵詞 | 1 |
| `query_keyword_dict_list` | 查詢收藏夾列表 | 1 |
| `query_keyword_dict` | 查詢收藏的詞 | 1 |

#### 1688 供貨平臺 (1個)
| 介面 | 用途 | 呼叫消耗 |
|------|------|----------|
| `ali1688_similar_product` (原 `products_1688`) | 1688產品搜尋/採購成本分析 | 1 |

#### TikTok 電商平臺 (8個)
| 介面 | 用途 | 呼叫消耗 |
|------|------|----------|
| `tiktok_product_search` | TikTok產品搜尋 | 1 |
| `tiktok_product_detail` | TikTok產品詳情 | 1 |
| `tiktok_product_videos` | TikTok帶貨影片 | 1 |
| `tiktok_product_influencers` | TikTok帶貨達人分析 | 1 |
| `tiktok_product_trend` | TikTok產品趨勢 | 1 |
| `tiktok_influencer_search` | TikTok達人搜尋 | 1 |
| `tiktok_category_name_search` | TikTok類目搜尋 | 1 |
| `tiktok_category_report` | TikTok類目報告 | 1 |

### 調研維度與介面對照表

當使用者需要調研特定維度時，使用以下介面：

#### 亞馬遜產品調研
| 調研維度 | 使用介面 | 關鍵引數 |
|----------|----------|----------|
| **產品基礎資訊** | `product_detail` | asin |
| **銷量/價格趨勢** | `product_trend` | asin, productTrendType |
| **使用者評價** | `product_reviews` | asin, reviewType |
| **流量來源** | `product_traffic_terms` | asin |
| **競品關鍵詞佈局** | `competitor_product_keywords` | asin |
| **關鍵詞排名監控** | `product_keyword_rank_trend` | asin, keyword |
| **子體明細** | `product_variations` | asin |

#### 亞馬遜關鍵詞調研
| 調研維度 | 使用介面 | 關鍵引數 |
|----------|----------|----------|
| **關鍵詞資料分析** | `keyword_detail` | keyword |
| **關鍵詞搜尋結果** | `keyword_search_result` | searchKeyword |
| **關鍵詞歷史趨勢** | `keyword_trend` | searchKeyword |
| **長尾詞挖掘** | `keyword_related_words` | searchKeyword |

#### 亞馬遜類目調研
| 調研維度 | 使用介面 | 關鍵引數 |
|----------|----------|----------|
| **類目搜尋(獲nodeid)** | `category_name_search` | searchName |
| **類目分析** | `category_report` | nodeId |
| **類目趨勢** | `category_trend` | nodeId, trendIndex |
| **類目關鍵詞** | `category_keywords` | nodeId |
| **類目市場篩選** | `category_market_search` | 多種篩選引數 |

#### 亞馬遜選品調研
| 調研維度 | 使用介面 | 關鍵引數 |
|----------|----------|----------|
| **產品搜尋/篩選** | `product_search` | searchName + 篩選引數 |
| **潛力產品挖掘** | `potential_product_search` | searchName, price_range等 |

#### TikTok 跨平臺調研
| 調研維度 | 使用介面 | 關鍵引數 |
|----------|----------|----------|
| **相似產品分析** | `tiktok_product_search` | site, searchName |
| **TikTok產品詳情** | `tiktok_product_detail` | site, productId |
| **帶貨影片分析** | `tiktok_product_videos` | site, productId |
| **帶貨達人分析** | `tiktok_product_influencers` | site, productId |
| **產品趨勢追蹤** | `tiktok_product_trend` | site, productId |
| **達人搜尋** | `tiktok_influencer_search` | site, searchName |
| **TikTok類目分析** | `tiktok_category_report` | site, nodeId |

#### 供應鏈成本調研
| 調研維度 | 使用介面 | 關鍵引數 |
|----------|----------|----------|
| **1688採購成本** | `ali1688_similar_product` (原 `products_1688`) | searchName |

### 支援的平臺站點

| 平臺 | 站點數量 | 支援站點 |
|------|----------|----------|
| **亞馬遜** | 14個 | US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA |
| **TikTok** | 6個 | US, GB, MY, PH, VN, ID |
| **1688** | - | 國內批發採購平臺 |

---

*本技能文件版本: v2.2 | 最後更新: 2026-03-03*
