# amazon-sorftime-research：開源亞馬遜 AI 選品與運營工具集

[English](README.en.md) | **繁體中文**

> **專為亞馬遜跨境賣家打造的開源智慧選品分析工具箱。用斜線指令自動完成競品拆解、差評挖掘與爆款 Listing 打造。**

---

## 專案亮點

- **四大電商 MCP 資料深度整合**：全面串接 **Sorftime**、**賣家精靈 (SellerSprite)**、**西柚洞察 (Xiyou)** 與 **Sif** 四大跨境電商資料來源。
- **全球 14 大站點支援與跨平臺帶貨分析**：涵蓋美國、歐洲、日本等 14 大亞馬遜站點，並延伸支援 TikTok 帶貨影片、達人分析與 1688 供應鏈採購成本拆解。
- **用斜線指令自動完成競品拆解**：透過簡潔的斜線指令（如 `/amazon-analyse`、`/product-research`），代理自動排程多源 API，端到端完成全維度穿透分析。
- **自動挖掘買家差評並給出改善建議**：自動抓取千條買家評論，提煉 6 維痛點分佈（產品質量、功能缺陷、包裝物流、尺寸規格等），生成具體產品迭代策略與售後範本。
- **內建 8 步工作流打造爆款產品頁**：由關鍵詞庫、問題庫、證據庫出發，一步步生成黃金標題、五點描述 (Bullet Points)、A+ 詳情頁、搜尋詞 (Search Terms) 與問答設計。
- **全面適配新版對話式購物搜尋演演算法**：適配亞馬遜 Cosmo 語義演算法與 Rufus / Alexa AI 購物助手搜尋邏輯，最大化自然流量曝光。
- **自動輸出視覺化圖表與 Excel 深度報告**：自動生成互動式 HTML 儀錶板、專業 Excel 資料分析表與詳盡的 Markdown 戰略報告。
- **配置 MCP 金鑰搭配 Claude Code / Codex 就能跑**：一鍵設定 `.mcp.json`，隨插即用。

---

## 九大核心技能與完整指令清單

本專案將複雜的跨境電商分析工作流封裝為 9 個可直接在 Claude Code 或 Codex 執行的 AI 技能（位於 `SKILLS/skills/`）：

| 技能模組 | 分析物件 | 斜線指令 (Slash Command) | 核心功能與輸出 |
|---|---|---|---|
| **amazon-analyse** | 單個 Listing | `/amazon-analyse {ASIN} {SITE}` | 競品 Listing 全維度穿透分析：銷額估算、流量來源、關鍵詞分佈、差評情感聚類與 1688 供應鏈成本拆解。 |
| **category-selection** | 整體品類大盤 | `/category-select "{品類}" {SITE}` | 品類自動化選品分析：Top100 資料、五維評分模型（市場規模、增長潛力、競爭烈度、壁壘、利潤空間），輸出 Markdown + Excel + HTML 報表。 |
| **keyword-research** | 關鍵詞詞庫 | `/keyword-research {ASIN} {SITE}` | 關鍵詞深度調研：採集 1500+ 詞彙，執行 8 維智慧分類（品牌詞、材質詞、場景詞、功能詞、否定詞等），匯出廣告精準投放清單。 |
| **review-analysis** | 買家評價 | `/review-analysis {ASIN} {SITE}` | 買家差評深度挖掘：解析真實買家不滿，建立痛點矩陣與改進方案，附贈防差評客服郵件範本。 |
| **product-research** | 產品深度調研 | `/product-research "{產品關鍵詞}" {SITE}` | LLM 驅動選品決策：市場痛點、使用者畫像、價格帶分佈、市場切入點與風險預警。 |
| **sif-amazon-research** | 電商綜合研究 | `/sif-amazon-research` | 基於 Sif MCP 資料：市場驗證、競品流量滲透率診斷、廣告結構審查與發布增長策略。 |
| **xiyou-insight** | 流量與廣告場景 | `/xiyou-insight` | 西柚洞察 7 大場景分析：廣告監控、流量缺口挖掘、競品廣告策略拆解、新品推廣預算規劃。 |
| **sellersprite-amazon-research** | 全鏈路資料工具 | `/sellersprite-research` (及各專項指令) | 呼叫賣家精靈 43 項工具：藍海市場挖掘、關鍵詞反查、競品流量動態、定價分析與利潤核算。 |
| **amazon-listing-builder** | Listing 最佳化生成 | `/listing-builder` | Cosmo 語義演算法 + Rufus 對話式搜尋 8 步全鏈路打造爆款 Listing，涵蓋標題、五點、A+ 與 ST。 |

---

## 8 步工作流：打造符合 Cosmo + Rufus 的爆款 Listing

`amazon-listing-builder` 技能內建標準化的 8 步工作流程：

```text
1. 關鍵詞庫建置 (Step 1: Layered Keyword Library)
   └── 核心大詞、長尾詞、場景詞、高轉化詞、隱私屬性詞
2. 使用者問題庫 (Step 2: Customer Question Library)
   └── 模擬買家在對話式 AI (Rufus) 中的自然語言提問
3. 證據矩陣建立 (Step 3: Evidence & Proof Library)
   └── 引數驗證、實驗資料、安全認證、實測場景
4. 黃金標題設計 (Step 4: Title Design)
   └── 兼顧手機端前 60 字元閱讀與全標題權重佈局
5. 五點描述撰寫 (Step 5: Feature Bullet Points)
   └── 痛點場景化 + 解決方案 + 證據支撐
6. A+ 頁面與品牌故事 (Step 6: Description & A+ Content)
   └── 模組化視覺文案與對話搜尋語義埋詞
7. 後臺搜尋詞 (Step 7: Search Terms - ST)
   └── 嚴格控制 250 位元組，絕不重複前臺詞彙，最大化涵蓋漏斗詞
8. 智慧問答設計 (Step 8: Q&A Strategic Design)
   └── 主動覆蓋潛在客訴與高頻疑慮，提升下單轉換率
```

---

## 快速開始

### 1. 安裝與環境準備

本專案專為 Windows 11 + PowerShell 開發與運營環境打造，提供完整自動化檢驗：

```powershell
# Clone 本倉庫
git clone https://github.com/SanHsien/amazon-sorftime-research-MCP-skill.git
cd amazon-sorftime-research-MCP-skill

# 設定預設 GitHub 倉庫
gh repo set-default SanHsien/amazon-sorftime-research-MCP-skill

# 安裝 Python 依賴
pip install -r requirements.txt
```

### 2. 配置 MCP 伺服器

在專案根目錄的 `.mcp.json` 中設定您所屬服務的 API 金鑰（可參考 `.env.example` 進行安全保管）：

```json
{
  "mcpServers": {
    "sorftime": {
      "type": "streamableHttp",
      "url": "https://mcp.sorftime.com?key=YOUR_SORFTIME_API_KEY",
      "name": "Sorftime MCP"
    },
    "sif-mcp": {
      "type": "http",
      "url": "https://mcp.sif.com/mcp",
      "headers": {
        "secret-key": "YOUR_SIF_SECRET_KEY"
      }
    },
    "xydc-mcp": {
      "type": "http",
      "url": "https://mcp.xydc.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_XIYOU_TOKEN"
      },
      "name": "西柚洞察MCP"
    },
    "sellersprite": {
      "url": "https://mcp.sellersprite.com/mcp",
      "headers": {
        "secret-key": "YOUR_SELLERSPRITE_SECRET_KEY"
      },
      "name": "賣家精靈MCP"
    }
  }
}
```

### 3. 搭配 Claude Code / Codex 執行

啟動 Claude Code 或 Codex：
```bash
claude
```

在對話中直接輸入斜線指令即可開始分析：
```text
> /amazon-analyse B0D9ZTW7PS US
> /category-select "Wireless Earbuds" US
> /keyword-research B0D9ZTW7PS US
> /listing-builder
```

---

## Windows 開發環境與質量閘門

本 fork 提供嚴格的本地驗收閘門與上游增量水位追蹤機制：

```powershell
# 1. 執行單元測試與完整性檢查
python -m pytest tests -v

# 2. 查驗上游更新水位
python tools/check_upstream_updates.py --strict

# 3. 執行 Windows 一鍵驗收 Gate
pwsh -NoProfile -File tools/dev_check.ps1 -Quick
```

---

## Fork 與開源致敬

- 本專案 fork 自原作者 **liangdabiao** 的開源專案 [`liangdabiao/amazon-sorftime-research-MCP-skill`](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill)。
- 本 Fork 由 [SanHsien](https://github.com/SanHsien) 維護，針對 Windows 11 開發環境、正體中文在地化、自動化測試與程式碼質量治理進行了完整擴充套件。
- 詳細決策與架構記錄請參閱 [`FORK.md`](FORK.md) 與 [`docs/fork/DECISIONS.md`](docs/fork/DECISIONS.md)。

