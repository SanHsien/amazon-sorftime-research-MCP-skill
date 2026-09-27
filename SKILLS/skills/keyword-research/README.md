# Keyword Research Skill

亞馬遜關鍵詞深度調研與智慧分類分析技能。

## 功能特點

- 基於 **Sorftime MCP** 資料採集 2000+ 關鍵詞
- 透過 **LLM Agent** 按 8 維度智慧分類
- 生成 Markdown 報告、CSV 詞庫和 HTML 儀表板

## 8 維分類模型

| 分類 | 說明 | 應用策略 |
|------|------|----------|
| NEGATIVE | 否定/敏感詞 | 直接新增為否定關鍵詞 |
| BRAND | 品牌詞 | 競品打法或否定 |
| MATERIAL | 材質詞 | 精準片語匹配 |
| SCENARIO | 使用場景詞 | 按場景拆分廣告組 |
| ATTRIBUTE | 屬性修飾詞 | 長尾精準匹配 |
| FUNCTION | 功能詞 | 廣泛匹配擴流 |
| CORE | 核心產品詞 | 大詞投放佔領坑位 |
| OTHER | 其他 | 補充埋詞 |

## 使用方法

### 透過 Skill 觸發

```bash
/keyword-research B07PWTJ4H1 US
```

### 命令列直接執行

```bash
# 基礎用法
python .claude/skills/keyword-research/scripts/workflow.py B07PWTJ4H1 US

# 帶產品資訊
python .claude/skills/keyword-research/scripts/workflow.py B07PWTJ4H1 US --product-info product.json

# 指定長尾詞擴充套件數量
python .claude/skills/keyword-research/scripts/workflow.py B07PWTJ4H1 US --long-tail-limit 20
```

## 產品資訊檔案（可選）

```json
{
  "product_name": "Coat Rack Wall Mount",
  "material": "Wood",
  "features": ["Wall Mount", "5 Hooks", "16.5 inches", "Heavy Duty"],
  "use_cases": ["Entryway", "Bathroom", "Mudroom"],
  "negative_features": ["Freestanding", "Over Door", "Floor"]
}
```

## 輸出檔案

```
keyword-reports/
└── {ASIN}_{Site}_{YYYYMMDD}/
    ├── report.md                    # Markdown 分析報告
    ├── keywords.csv                 # 完整詞庫（分類後）
    ├── keywords_negative.csv        # 否定詞專用
    ├── negative_words.txt           # 否定詞清單
    ├── brand_words.txt              # 品牌詞清單
    ├── categorized_summary.json     # 分類統計
    ├── dashboard.html               # HTML 儀表板
    └── execution.log                # 執行日誌
```

## 資料採集流程

1. **產品流量詞** (product_traffic_terms): 50-200 個
2. **競品佈局詞** (competitor_product_keywords): 100-500 個
3. **類目核心詞** (category_keywords): 100-500 個
4. **長尾詞擴充套件** (keyword_related_words): 1000-2000 個

## API 依賴

本技能使用 Sorftime MCP 以下介面：

- `product_traffic_terms` - 產品流量關鍵詞
- `competitor_product_keywords` - 競品佈局關鍵詞
- `category_keywords` - 類目核心關鍵詞
- `keyword_related_words` - 長尾詞擴充套件
- `product_detail` - 產品詳情（獲取 NodeID）

## 注意事項

1. **API Key**: 自動從 `.mcp.json` 讀取
2. **分類方式**: 使用 LLM Agent 批次分類（每批 150 個關鍵詞）
3. **資料去重**: 自動歸一化處理（小寫、去除特殊字元）
4. **編碼**: UTF-8，支援中文和特殊字元

## 故障排查

### API 認證失敗
```
❌ Authentication required - Invalid API Key
```
**解決**: 檢查 `.mcp.json` 中的 API Key 是否正確

### 產品未找到
```
未查詢到對應產品
```
**解決**: 確認 ASIN 是否存在於 Sorftime 資料庫

### 分類結果不準確
**解決**: 提供產品資訊 JSON 檔案以提高分類準確性

## 檔案結構

```
.claude/skills/keyword-research/
├── SKILL.md                          # 技能定義
├── README.md                         # 本檔案
├── scripts/
│   ├── workflow.py                   # 主工作流
│   ├── keyword_collector.py          # 關鍵詞采集
│   ├── data_parser.py                # SSE 資料解析
│   ├── csv_generator.py              # CSV 生成
│   ├── generate_markdown_report.py   # Markdown 報告
│   └── generate_html_dashboard.py    # HTML 儀表板
└── templates/
    └── dashboard_template.html       # HTML 模板
```

## 版本

v1.0 - 2026-03-13
