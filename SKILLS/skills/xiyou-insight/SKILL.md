---
name: xiyou-insight
description: 基於西柚洞察MCP的亞馬遜競品分析與廣告策略工具。提供7大核心工作場景：實時監控廣告投放效果、快速找到高價效比流量缺口、快速拆解對標競對打法、提升新品推廣效率、精準拆解競品流量以及廣告策略、透視競品廣告策略和預算、高效搭建關鍵詞庫。適用於亞馬遜賣家進行競品分析、廣告最佳化和關鍵詞研究。
argument-hint: "[場景名稱] [ASIN/關鍵詞] [站點]"
user-invocable: true
---

# 西柚洞察 (Xiyou Insight)

## 定位

基於 **西柚洞察MCP** 的亞馬遜競品分析與廣告策略工具。LLM Agent 直接呼叫 MCP 工具獲取資料，指令碼僅負責資料後處理、報告生成和視覺化渲染。

**核心特點**：
- **MCP驅動**：所有資料獲取透過 xydc-mcp 直接呼叫
- **場景化工作流**：7大核心場景，覆蓋廣告監控、流量分析、競品拆解、新品推廣、關鍵詞庫搭建
- **輕量指令碼**：僅用於資料聚合、報告生成和 Dashboard 渲染

---

## MCP 工具速查表

### ASIN 基礎資訊

| 工具名稱 | 功能 | 引數 |
|----------|------|------|
| `get_asin_info` | 獲取ASIN基礎資訊（標題、價格、評分、評論數、主圖） | `asins`, `country` |
| `get_asin_variations` | 查詢父子變體關係 | `asin`, `country` |
| `get_asin_info_trends` | 商品資訊日趨勢（價格、評分、評論數變化） | `asin`, `country`, `start_date`, `end_date` |

### ASIN 關鍵詞分析

| 工具名稱 | 功能 | 引數 |
|----------|------|------|
| `get_asin_keywords` | ASIN反查關鍵詞（近7天） | `asin`, `country`, `page`, `page_size`, `sort_field`, `sort_order` |
| `get_asin_keywords_monthly` | ASIN反查關鍵詞（月度歷史） | `asin`, `country`, `start_month`, `end_month`, `page`, `page_size` |
| `get_asin_keyword_rank_trends` | 關鍵詞日排名趨勢 | `asin`, `keyword`, `country`, `start_date`, `end_date` |
| `get_asin_keyword_rank_hourly` | 關鍵詞小時級排名（僅US/UK/DE） | `asin`, `keyword`, `country`, `date` |
| `get_asin_keyword_traffic_trends` | 關鍵詞日流量趨勢 | `asin`, `keyword`, `country`, `start_date`, `end_date` |

### ASIN 流量與銷量

| 工具名稱 | 功能 | 引數 |
|----------|------|------|
| `get_asin_traffic` | 近7天流量得分（自然/廣告流量佔比） | `asins`, `country` |
| `get_asin_traffic_trends` | 日流量趨勢（自然/廣告/位置維度） | `asin`, `country`, `start_date`, `end_date` |
| `get_asin_order_trends` | 月訂單量趨勢 | `asin`, `country`, `start_month`, `end_month` |
| `get_asin_bsr_trends` | BSR類目排名日趨勢 | `asin`, `country`, `start_date`, `end_date` |

### ASIN 廣告分析

| 工具名稱 | 功能 | 引數 |
|----------|------|------|
| `get_asin_ad_change_trends` | 廣告投放變化日趨勢（新增/移除廣告活動） | `asin`, `country`, `start_date`, `end_date` |

### 關鍵詞分析

| 工具名稱 | 功能 | 引數 |
|----------|------|------|
| `get_keyword_info` | 關鍵詞基礎指標（搜尋量、競爭難度、建議競價） | `keywords`, `country` |
| `get_keyword_aba_trends` | ABA搜尋量周趨勢（最長52周） | `keywords`, `country`, `start_week`, `end_week` |
| `get_keyword_asin_analysis` | 關鍵詞反查ASIN（近7天競爭格局） | `keyword`, `country`, `page`, `page_size`, `sort_field`, `sort_order` |
| `get_keyword_analysis_monthly` | 關鍵詞競爭格局月度歷史 | `keyword`, `country`, `start_month`, `end_month`, `page`, `page_size` |

---

## 7大核心工作場景

### 場景1：實時監控廣告投放效果

**目標**：透過小時級排名變化和廣告放映機，實時監控廣告投放效果

**工作流程**：

```
Step 1: 獲取ASIN基礎資訊
  → get_asin_info(asin)
  
Step 2: 查詢小時級排名（僅US/UK/DE）
  → get_asin_keyword_rank_hourly(asin, keyword, date)
  分析廣告排名位置和持續時間
  
Step 3: 查詢日排名趨勢
  → get_asin_keyword_rank_trends(asin, keyword, start_date, end_date)
  判斷廣告投放帶動自然排名上升情況
  
Step 4: 查詢廣告投放變化
  → get_asin_ad_change_trends(asin, start_date, end_date)
  分析廣告活動新增/移除情況
  
Step 5: 生成分析報告
  → 評估廣告投放效率，判斷是否帶來自然排名提升
```

**輸出**：廣告投放效果分析報告

---

### 場景2：快速找到高價效比流量缺口

**目標**：透過多ASIN對比和關鍵詞分析，找到競爭對手有排名但自身沒有的流量缺口

**工作流程**：

```
Step 1: 獲取多個ASIN基礎資訊
  → get_asin_info(asins)
  
Step 2: 獲取各ASIN關鍵詞列表
  → get_asin_keywords(asin1)
  → get_asin_keywords(asin2)
  → ...
  
Step 3: 對比關鍵詞覆蓋差異
  → 找出競品有排名但自身沒有的關鍵詞
  
Step 4: 分析關鍵詞競爭程度
  → get_keyword_info(keywords)
  判斷搜尋量、競爭難度、建議競價
  
Step 5: 分析關鍵詞下ASIN競爭格局
  → get_keyword_asin_analysis(keyword)
  判斷自然位滾動率、廣告位競爭難度
  
Step 6: 篩選高價效比流量缺口
  → 綜合評估：搜尋量中等、競爭難度低、競品有排名但自身無排名
```

**輸出**：流量缺口分析報告，包含推薦補充的關鍵詞列表

---

### 場景3：快速拆解對標競對打法

**目標**：全面分析競品的關鍵詞覆蓋差異、流量結構和廣告策略

**工作流程**：

```
Step 1: 獲取競品基礎資訊
  → get_asin_info(competitor_asins)
  
Step 2: 確認主推變體
  → get_asin_variations(asin)
  確定父體下流量最大的變體
  
Step 3: 分析流量結構
  → get_asin_keywords(asin)
  → get_asin_traffic(asin)
  分析頭部詞、腰部詞、長尾詞貢獻的展示量
  
Step 4: 分析廣告策略
  → get_asin_ad_change_trends(asin, start_date, end_date)
  → get_asin_traffic_trends(asin, start_date, end_date)
  瞭解廣告流量構成和廣告展示位置關鍵詞
  
Step 5: 趨勢分析
  → get_asin_keyword_rank_trends(asin, keyword, start_date, end_date)
  洞察競品廣告投放策略和節奏
  
Step 6: 綜合對比分析
  → 關鍵詞覆蓋差異、流量份額、廣告策略對比
```

**輸出**：競品打法拆解報告

---

### 場景4：提升新品推廣效率

**目標**：分析新品流量分配階段（稀疏期→震盪期→穩定期），把握異動關鍵詞機會

**工作流程**：

```
Step 1: 獲取ASIN基礎資訊
  → get_asin_info(asin)
  
Step 2: 分析流量趨勢
  → get_asin_traffic_trends(asin, start_date, end_date)
  判斷流量分配階段：稀疏期/震盪期/穩定期
  
Step 3: 分析關鍵詞排名變化
  → get_asin_keywords(asin)
  → get_asin_keyword_rank_trends(asin, keyword, start_date, end_date)
  
Step 4: 識別異動關鍵詞
  - 新增：昨日無排名今日出現排名
  - 流失：昨日有排名今日消失
  - 流量升檔：自然流量上升（稀疏→震盪→穩定）
  - 流量降檔：自然流量下降
  
Step 5: 把握流量視窗機會
  → 針對新增和流量升檔關鍵詞加大投放
  → 針對流失和流量降檔關鍵詞分析原因並調整
```

**輸出**：新品推廣分析報告，包含流量階段判斷和異動關鍵詞建議

---

### 場景5：精準拆解競品流量以及廣告策略

**目標**：深度分析競品的關鍵詞佈局、流量來源和廣告投放策略

**工作流程**：

```
Step 1: 獲取競品基礎資訊
  → get_asin_info(competitor_asins)
  
Step 2: 確認主推變體
  → get_asin_variations(asin)
  
Step 3: 分析關鍵詞佈局
  → get_asin_keywords(asin)
  → get_asin_keywords_monthly(asin, start_month, end_month)
  瞭解關鍵詞覆蓋廣度和月度變化
  
Step 4: 分析流量結構
  → get_asin_traffic(asin)
  → get_asin_traffic_trends(asin, start_date, end_date)
  自然/廣告流量佔比、位置維度拆解
  
Step 5: 分析廣告策略
  → get_asin_ad_change_trends(asin, start_date, end_date)
  → get_asin_keyword_traffic_trends(asin, keyword, start_date, end_date)
  
Step 6: 關鍵詞競爭分析
  → get_keyword_info(keywords)
  → get_keyword_asin_analysis(keyword)
  分析競品核心關鍵詞的競爭格局
  
Step 7: 生成綜合分析報告
  → 關鍵詞覆蓋差異、流量結構、廣告策略洞察
```

**輸出**：競品流量與廣告策略深度分析報告

---

### 場景6：透視競品廣告策略和預算

**目標**：分析競品的廣告型別分佈、活動結構、預算分佈和核心廣告關鍵詞

**工作流程**：

```
Step 1: 獲取競品基礎資訊
  → get_asin_info(asin)
  
Step 2: 確認主推變體
  → get_asin_variations(asin)
  
Step 3: 分析廣告活動變化
  → get_asin_ad_change_trends(asin, start_date, end_date)
  識別新增/移除的廣告活動，分析投放節奏
  
Step 4: 分析流量趨勢
  → get_asin_traffic_trends(asin, start_date, end_date)
  判斷SP/SB/SBV廣告流量佔比
  
Step 5: 分析關鍵詞流量貢獻
  → get_asin_keywords(asin)
  → get_asin_keyword_traffic_trends(asin, keyword, start_date, end_date)
  找出核心廣告關鍵詞及其流量佔比
  
Step 6: 推斷預算分佈
  → 根據廣告展示時長和關鍵詞流量變化推斷預算調整
  → 分析廣告投放的週期性規律
  
Step 7: 生成廣告策略分析報告
  → 廣告型別分佈、活動結構、核心關鍵詞、預算推斷
```

**輸出**：競品廣告策略和預算分析報告

---

### 場景7：高效搭建關鍵詞庫

**目標**：透過反查競品流量詞和以詞找詞，搭建完整的關鍵詞庫

**工作流程**：

```
Step 1: 廣泛收集關鍵詞
  → 方式1：反查競品流量詞
    get_asin_keywords(competitor_asin) × 多個競品
  → 方式2：關鍵詞基礎資訊
    get_keyword_info(core_keywords)
  
Step 2: 關鍵詞拓展
  → get_keyword_aba_trends(keywords, start_week, end_week)
  分析搜尋量趨勢和季節性
  
Step 3: 關鍵詞競爭分析
  → get_keyword_asin_analysis(keyword)
  判斷每個關鍵詞下的競爭格局
  
Step 4: 按相關性篩選
  → 強/高/中相關 → 加入關鍵詞庫
  → 低/極低相關 → 加入否定詞庫
  
Step 5: 關鍵詞分類
  → 資料維度：搜尋量（大/中/小）、競爭難度（超難/難/中等/簡單）、轉化率（高/中/低）
  → 屬性維度：人群受眾、使用場景、產品維度、價值維度
  
Step 6: 輸出關鍵詞庫
  → 結構化關鍵詞列表，包含分類標籤和優先順序
```

**輸出**：完整關鍵詞庫，包含關鍵詞分類和優先順序標註

---

## Script Directory

| 指令碼 | 用途 | 何時呼叫 |
|------|------|---------|
| `report_generator.py` | **報告生成器**：將MCP資料聚合為Markdown報告 | 每個場景完成後 |
| `dashboard_generator.py` | **Dashboard渲染**：生成視覺化看板HTML | 報告生成後 |
| `data_aggregator.py` | **資料聚合器**：合併多個ASIN/關鍵詞資料 | 多ASIN對比場景 |

**指令碼職責**：
- **不做API呼叫**：所有資料獲取由LLM透過MCP直接呼叫
- **僅做資料處理**：聚合、清洗、格式化
- **報告渲染**：生成Markdown和HTML報告

---

## 執行流程

### 通用執行模式

```
1. 使用者輸入場景和引數（ASIN/關鍵詞/站點）
2. LLM根據場景選擇對應MCP工具組合
3. 呼叫MCP工具獲取資料
4. 使用指令碼進行資料後處理和報告生成
5. 輸出Markdown報告和Dashboard看板
```

### 資料輸出目錄

```
xiyou-insight-reports/
└── {scenario}_{asin_or_keyword}_{site}_{YYYYMMDD}/
    ├── report.md              # Markdown完整報告
    ├── data.json              # 結構化資料
    ├── dashboard.html         # 視覺化看板
    └── raw/                   # 原始MCP響應資料
        ├── asin_info.json
        ├── keywords.json
        ├── traffic.json
        └── ad_trends.json
```

---

## 資料欄位命名規範

| 欄位名 | 說明 | 示例 |
|--------|------|------|
| `natural_traffic` | 自然流量得分 | 85.5 |
| `ad_traffic` | 廣告流量得分 | 42.3 |
| `total_traffic` | 總流量得分 | 127.8 |
| `keyword_count` | 關鍵詞數量 | 156 |
| `natural_rank` | 自然排名位置 | 5 |
| `ad_rank` | 廣告排名位置 | 2 |
| `weekly_search_volume` | 周搜尋量 | 125000 |
| `competitive_difficulty` | 競爭難度(0-100) | 72 |
| `cost_per_click` | 建議競價 | 2.35 |

---

## 支援的站點

US, CA, MX, BR, UK, DE, FR, ES, IT, JP, AE, AU, SA

**注意**：小時級排名(`get_asin_keyword_rank_hourly`)僅支援 US/UK/DE 站點

---

## 注意事項

1. **API限流**：每批請求建議控制併發數量，避免觸發限流
2. **資料時效**：近7天資料實時性較好，歷史資料可能有延遲
3. **消耗提示**：查詢日期範圍越長，API消耗越高
4. **intent_summary**：所有MCP呼叫必須包含脫敏的業務意圖描述，禁止包含使用者原始prompt、賬號、手機號、郵箱或完整ASIN

---

## 與其他Skills的關係

```
category-selection (品類篩選)
        ↓
product-research (深度選品調研)
        ↓
xiyou-insight (競品分析與廣告策略) ← 本Skill
        ↓
review-analysis (評論深度分析)
```

**區別**：
- `category-selection`：品類級別的快速篩選
- `product-research`：指定品類的深度調研
- `xiyou-insight`：競品流量分析和廣告策略拆解
- `review-analysis`：評論的深度痛點分析

---

*版本: v1.0 (7場景工作流) | 最後更新: 2026-07-04*
