# Amazon Analyse Skill

> 亞馬遜競品Listing全維度穿透分析工具

對亞馬遜競品進行深度分析，包括文案邏輯、評論情感、關鍵詞佈局、市場動態等，生成專業競品情報報告並自動儲存為文件。

---

## 功能特性

| 功能模組 | 說明 |
|----------|------|
| **產品基礎分析** | 價格、評分、排名、銷量等核心指標 |
| **關鍵詞佈局** | 流量來源、自然曝光、競品關鍵詞分析 |
| **評論情感分析** | 優勢聚類、痛點挖掘、改進建議 |
| **市場動態** | 銷量趨勢、季節性波動、競爭格局 |
| **戰略建議** | 關鍵詞策略、定價建議、Listing最佳化 |
| **報告儲存** | 自動生成Markdown文件 |

---

## 快速開始

### 命令格式

```
/amazon-analyse <ASIN> [站點]
```

### 引數說明

| 引數 | 說明 | 可選值 | 預設值 |
|------|------|--------|--------|
| ASIN | 亞馬遜產品標識碼（10位） | - | 必填 |
| 站點 | 亞馬遜站點 | US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA | US |

### 使用示例

```bash
# 分析美國站產品
/amazon-analyse B07PQFT83F US

# 分析德國站產品
/amazon-analyse B08N5WRWNW DE

# 分析日本站產品
/amazon-analyse B09XXX JP
```

---

## 分析報告內容

### 報告結構

```
1. 產品基礎資料
   ├── 核心指標（價格、評分、排名）
   └── 市場表現（銷量趨勢、生命週期）

2. 關鍵詞佈局分析 (The Brain)
   ├── 流量關鍵詞列表
   ├── 競品關鍵詞佈局
   └── 文案構建邏輯

3. 評論定性分析 (The Voice)
   ├── 評論資料概覽
   ├── 核心優勢 Top 3
   ├── 核心痛點 Top 3
   └── 改進建議 Top 3

4. 競爭策略分析 (The Pulse)
   ├── 競爭優勢
   ├── 競爭劣勢
   ├── 市場機會
   └── 潛在威脅

5. 戰略反擊建議
   ├── 關鍵詞策略
   ├── 定價策略
   ├── 產品最佳化方向
   └── Listing最佳化建議
```

---

## 輸出檔案

### 檔案位置

```
專案目錄/reports/
```

### 命名規則

```
analysis_{ASIN}_{站點}_{日期}.md

例如: analysis_B07PQFT83F_US_20260302.md
```

### 報告示例

```markdown
# 亞馬遜競品Listing全維度穿透分析報告

## 分析物件
- ASIN: B07PQFT83F
- 亞馬遜站點: US
- 分析時間: 2026-03-02
- 資料來源: Sorftime MCP

## 第一部分：產品基礎資料
### 核心指標
- 產品標題: Disney Store Official Buzz Lightyear...
- 品牌: Disney Store
- 價格: $39.95
- 評分: 4.70 / 5.0
- 評論數: 47,400
- 類目排名: #1 in Action Figures

...
```

---

## 資料來源

本工具使用 **Sorftime MCP** 服務獲取亞馬遜資料：

- 支援亞馬遜14大站點
- 實時產品搜尋與詳情
- 使用者評論分析（最多100條）
- 流量關鍵詞資料
- 歷史銷量趨勢

### Sorftime MCP API

```bash
curl -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{...}}'
```

---

## 配置

### API Key 配置

編輯 `專案目錄/.mcp.json`：

```json
{
  "mcpServers": {
    "sorftime": {
      "type": "streamableHttp",
      "url": "https://mcp.sorftime.com?key=YOUR_API_KEY",
      "name": "Sorftime MCP",
      "description": "Sorftime 跨境電商平臺資料服務"
    }
  }
}
```

### Sorftime API Key 獲取

1. 訪問 [Sorftime官網](https://www.sorftime.com)
2. 註冊賬號並申請API Key
3. 將API Key配置到 `.mcp.json` 檔案

---

## 目錄結構

```
專案目錄/
├── .claude/
│   └── skills/
│       └── amazon-analyse/
│           ├── SKILL.md           # 技能定義檔案
│           └── README.md          # 本文件
├── reports/                        # 分析報告輸出目錄
│   ├── analysis_xxx_US_20260302.md
│   └── archive/
│       ├── 2026/
│       └── 2025/
└── .mcp.json                       # MCP配置檔案
```

---

## 故障排查

### 問題：ASIN未找到

**原因**：ASIN不在Sorftime資料庫或已下架

**解決**：
1. 確認ASIN格式正確（10位字母數字）
2. 使用product_search工具驗證
3. 檢查產品是否在該站點上架

### 問題：API請求超時

**原因**：網路問題或API服務異常

**解決**：
1. 檢查網路連線
2. 驗證API Key是否有效
3. 增加超時時間：`curl --max-time 30`

### 問題：中文顯示為亂碼

**原因**：Unicode跳脫字元未解碼

**解決**：現代工具會自動解碼，或使用Python解碼：
```python
import json
print(json.loads('"\\u4EA7\\u54C1"'))
```

---

## 最佳實踐

### 1. 定期追蹤競品

建議每月分析一次核心競品，監控其策略變化：

```bash
# 1月分析
/amazon-analyse B07PQFT83F US  # → analysis_xxx_US_20260115.md

# 2月分析
/amazon-analyse B07PQFT83F US  # → analysis_xxx_US_20260220.md

# 對比兩次分析
diff reports/analysis_xxx_US_20260115.md reports/analysis_xxx_US_20260220.md
```

### 2. 多站點對比

同一產品在不同站點的表現可能不同：

```bash
/amazon-analyse B07PQFT83F US  # 美國站
/amazon-analyse B07PQFT83F DE  # 德國站
/amazon-analyse B07PQFT83F JP  # 日本站
```

### 3. 報告歸檔管理

定期整理舊報告：

```bash
# 歸檔6個月前的報告
mkdir -p reports/archive/2025/
mv reports/analysis_*_2025*.md reports/archive/2025/
```

---

## 版本歷史

| 版本 | 日期 | 更新內容 |
|------|------|----------|
| v2.0 | 2026-03-02 | 新增報告儲存功能、故障排查、最佳實踐 |
| v1.0 | 2026-02-20 | 初始版本 |

---

## 相關連結

- [Sorftime官網](https://www.sorftime.com)
- [Amazon MWS文件](https://developer.amazonservices.com/)
- [Claude Code文件](https://claude.com/claude-code)

---

## 許可證

MIT License

---

*最後更新: 2026-03-02*
