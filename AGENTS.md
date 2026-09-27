# AGENTS.md

給 Codex、Claude Code、Cursor 與其他自動化代理在本專案工作時的指引。

## 專案定位

這是 [`liangdabiao/amazon-sorftime-research-MCP-skill`](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill) 的 fork。
專案核心為專為亞馬遜跨境賣家打造的開源智慧選品與運營工具箱，整合四大電商 MCP（Sorftime、Sif、西柚洞察、賣家精靈）資料，提供包含全品類分析、競品拆解、差評挖掘、關鍵詞調研與 8 步爆款 Listing 生成等九大 AI 技能。

`origin` 是 `SanHsien/amazon-sorftime-research-MCP-skill`，`upstream` 是原作者 repo，預設分支皆為 `main`。
本 fork 的維護差異記在 [`FORK.md`](FORK.md) 與 [`docs/fork/DECISIONS.md`](docs/fork/DECISIONS.md)。

主要開發與完整驗收環境是 **Windows 11 + PowerShell**。

## 硬性邊界

- **對外只打主人的 repo。** PR、push、release 一律指向 `SanHsien/amazon-sorftime-research-MCP-skill`。
  對上游開 PR 或 push 預設絕對禁止，除非維護者在當次對話明確同意。
- 每個工作環境先確認 `gh repo set-default SanHsien/amazon-sorftime-research-MCP-skill`。
- 日常開發推送到 `origin/main` 前，必須透過 Windows 閘門：
  `pwsh -NoProfile -File tools/dev_check.ps1 -Quick`（或完整無引數版本）。
- 保持乾淨工作目錄，不隨意刪除上游核心資料與報表範例。

## 核心技能與架構

本專案支援 9 大核心分析與選品運營技能，位於 `SKILLS/skills/`：
1. **amazon-analyse**: 競品 Listing 全維度穿透分析 (`/amazon-analyse {ASIN} {SITE}`)
2. **category-selection**: 品類自動化選品五維評分模型 (`/category-select "{品類}" {SITE}`)
3. **keyword-research**: 關鍵詞深度調研與 8 維智慧分類 (`/keyword-research {ASIN} {SITE}`)
4. **review-analysis**: 買家差評深度挖掘與痛點改善建議 (`/review-analysis {ASIN} {SITE}`)
5. **product-research**: LLM 驅動選品深度調研與決策 (`/product-research "{產品詞}" {SITE}`)
6. **sif-amazon-research**: Sif MCP 流量診斷、廣告審查與增長最佳化 (`/sif-amazon-research`)
7. **xiyou-insight**: 西柚洞察 7 大場景分析：廣告監控、流量缺口、競品拆解等 (`/xiyou-insight`)
8. **sellersprite-amazon-research**: 賣家精靈 43 個工具鏈，全鏈路選品與藍海挖掘
9. **amazon-listing-builder**: Cosmo 語義演算法 + Rufus/Alexa 8 步工作流打造爆款 Listing

## 開發與驗證命令

```powershell
# 1. 執行本地開發與完整性測試
python -m pytest tests -v

# 2. 查驗上游更新水位
python tools/check_upstream_updates.py --strict

# 3. 完整 Windows 閘門檢查
pwsh -NoProfile -File tools/dev_check.ps1 -Quick
```

## 技術細節（原 CLAUDE.md）

以下為各技能與 Sorftime MCP 整合的實作細節，原文為英文，保留原樣以避免翻譯失真。

### Sorftime MCP Integration

**API Configuration**
- Config file: `.mcp.json` - stores API key and endpoint
- Endpoint: `https://mcp.sorftime.com?key={API_KEY}`
- Protocol: `streamableHttp` using Server-Sent Events (SSE)
- Get API key: https://sorftime.com/zh-cn/mcp

**SSE Response Handling**
All Sorftime responses return as SSE format: `event: message\ndata: {JSON}\n\n`

Critical patterns:
- Chinese text is Unicode-escaped (`\u4ea7\u54c1`) → use `codecs.decode(text, 'unicode-escape')` or `json.loads()` with proper encoding
- Large responses (>25KB) are saved to temp files → use `Read` tool with offset/limit or `Grep` for extraction
- Increment `id` field for each request in a session (1, 2, 3...)

Direct curl invocation (when MCP unavailable):
```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

### Skills 架構

Skills located in `SKILLS/skills/skill-name/`:
- `SKILL.md` - YAML frontmatter + instructions (trigger mechanism)
- `scripts/` - Executable Python utilities
- `references/` - API docs, patterns loaded on-demand
- `assets/` - Templates for output files (HTML, Excel templates)

**category-selection Skill Updates (v6.0 - 2026-03-04)**

Recent Improvements:
- 自動編碼修復：整合 Mojibake (UTF-8/Latin-1 雙重編碼) 自動檢測和修復
- 錯誤容錯機制：趨勢 API 失敗時不影響整體流程
- Markdown 報告：新增自動生成 Markdown 分析報告
- 執行狀態跟蹤：顯示每步執行狀態和最終總結
- 關鍵詞解析增強：3 種解析策略支援更多資料格式
- 獨立編碼修復工具：`fix_encoding.py` 可修復現有 JSON 檔案

故障排查：
- 如遇亂碼: 執行 `python SKILLS/skills/category-selection/scripts/fix_encoding.py <json_file>`
- 如遇解析失敗: 檢視 `SKILLS/skills/category-selection/SKILL.md` 中的故障排查章節

### 各技能執行細節

**amazon-analyse (`/amazon-analyse {ASIN} {SITE}`)**

Trigger: User provides ASIN for competitor listing analysis

Analysis stages:
1. ASIN validation via `product_detail`
2. Data collection: product, reviews, traffic terms, competitor keywords, trends
3. SWOT analysis and strategic recommendations
4. Report saved to `reports/analysis_{ASIN}_{SITE}_{date}.md`

Key tools: `product_detail`, `product_reviews`, `product_traffic_terms`, `competitor_product_keywords`, `product_trend`

**category-selection (`/category-select "{Category}" {SITE} --limit N`)**

Trigger: User requests category analysis (default Top 20 products)

Five-dimensional scoring model (100 points total):
| Dimension | Points | Metric |
|-----------|--------|--------|
| Market Size | 20 | Category monthly revenue |
| Growth Potential | 25 | Year-over-year growth rate |
| Competition | 20 | HHI index, CR3 concentration |
| Entry Barrier | 20 | Avg review count, Amazon share, new product % |
| Profit Margin | 15 | 1688 cost comparison |

Rating thresholds: 80-100 (優秀), 60-79 (良好), 40-59 (一般), 0-39 (較差)

Analysis stages:
1. Search category → get nodeId via `category_name_search`
2. Fetch Top100 products + stats via `category_report`
3. (Optional) Fetch individual product details via `product_detail`
4. Calculate scores and generate three report formats:
   - Markdown: `category-reports/{Category}_{Site}_{date}/report.md`
   - Excel: `category-reports/{Category}_{Site}_{date}/category_report_*.xlsx`
   - HTML Dashboard: `category-reports/{Category}_{Site}_{date}/dashboard.html`

Report output structure:
```
category-reports/
└── {Category}_{Site}_{YYYYMMDD}/
    ├── index.html        # Navigation page
    ├── dashboard.html    # Interactive dashboard with charts
    ├── report.md         # Full markdown analysis
    ├── category_report_*.xlsx  # Excel with multiple sheets
    └── data.json         # Raw data for further processing
```

### Data Processing Utilities

Located in `SKILLS/skills/category-selection/scripts/`:

`data_utils.py` - Core data processor class with:
- `calculate_hhi()` - Herfindahl-Hirschman Index for market concentration
- `calculate_cr()` - Concentration Ratio (CR3, CR5)
- `group_by_price_range()` - Price distribution analysis
- `group_by_rating_range()` - Rating distribution analysis
- `filter_new_products()` - New product identification (days_online threshold)
- `analyze_brand_distribution()` - Brand market share calculation
- `analyze_seller_distribution()` - Seller source analysis (CN/US/Brand)
- `calculate_five_dimension_score()` - Scoring algorithm
- `prepare_html_data()` - Format data for HTML template rendering

`parse_sorftime_sse.py` - SSE response parser
- Extracts JSON data from SSE format
- Decodes Unicode-escaped Chinese text
- Handles large responses saved to temp files

### Report Generation Patterns

**Excel Report Generation**
Use `xlsxwriter` library (not `openpyxl` - simpler for large files):
```python
wb = xlsxwriter.Workbook(output_file)
header_fmt = wb.add_format({'bold': True, 'bg_color': '#4472C4', 'font_color': 'white'})
ws = wb.add_worksheet("Sheet Name")
ws.write(row, col, value, format)
chart = wb.add_chart({'type': 'column'})
ws.insert_chart('A1', chart)
wb.close()
```

**HTML Dashboard Template**
Located in `SKILLS/skills/category-selection/assets/dashboard_template.html`
Uses Chart.js for visualizations. Template variables are replaced using:
- Direct substitution for scalars
- `json.dumps()` for arrays/objects passed to JavaScript

### Common Issues and Solutions

**Unicode-decoded Chinese text in responses**
Sorftime returns `\u4ea7\u54c1` format. Solution:
```python
import codecs
decoded_text = codecs.decode(encoded_text, 'unicode-escape')
# Or for mojibake (UTF-8 decoded as Latin-1):
fixed_text = bad_text.encode('latin-1').decode('utf-8')
```

**Large responses saved to temp files**
When tool returns "Output too large... saved to: {path}":
```python
# Use Grep to extract specific patterns
grep('"月銷量":"(\\d+)"' /path/to/tempfile)

# Or use Read with offset/limit for file sections
Read(file_path, offset=1, limit=500)
```

**ASIN not found in Sorftime**
Always validate ASIN first with `product_detail`. If "未查詢到對應產品":
- Retry with `product_search` using ASIN or keywords
- Check if correct Amazon site
- Ask user to verify ASIN

### Supported Sites

**Amazon**: US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA
**TikTok**: US, GB, MY, PH, VN, ID
**1688**: China wholesale platform

### Python Dependencies

Scripts in this project require:
- `xlsxwriter` - Excel report generation
- Standard library: `json`, `codecs`, `re`, `datetime`, `sys`

Install with: `pip install xlsxwriter`

### Report Naming Conventions

| Report Type | Pattern | Example |
|-------------|---------|---------|
| Product analysis | `analysis_{ASIN}_{SITE}_{YYYYMMDD}.md` | `analysis_B07PWTJ4H1_US_20260302.md` |
| Category reports | `{Category}_{Site}_{YYYYMMDD}/` | `Sofas_US_20260303/` |

