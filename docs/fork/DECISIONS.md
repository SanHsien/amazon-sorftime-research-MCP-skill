# Fork 決策紀錄 (DECISIONS.md)

本文件記錄本 fork 相對於上游的所有架構決策、取捨與已審核變更。

---

## 2026-09-20: 分支清理與 Release 發布

- **決策**: 依規範清理多餘分支，僅保留主分支 main。
- **分支清理**:
  - origin/test 分支經查證 commit 歷史（55c6ffa），已完全為 main 所包含（ahead 0），且落後 main 21+ 個 commit，已安全刪除遠端分支。
  - 目前本地與遠端皆只保留唯一的 main 分支。
- **版本發布**: 為本 Fork 打上初始穩定標籤 0.1.0，發布首個正式 Release。

---

## 2026-09-20: 上游 Issues #1 ~ #6 深度審查與引進處理

依上游倉庫 [\liangdabiao/amazon-sorftime-research-MCP-skill\](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill) 之 Issue 水位線，已全面審閱至 #6，審查結論如下：

### 1. Issue #1: 1688成本獲取失敗
- **問題本質**: 用戶呼叫 products_1688 工具時返回 Unknown tool: 'ali1688_similar_product'。
- **技術調查**:
  - 經對比上游代碼演進，發現 Sorftime 官方 MCP 介面已將供應鏈工具重命名為 li1688_similar_product，而早期文檔與部分腳本仍記載舊名稱。
  - 此外，1688 介面有時存在供應商維護或獨立授權限制。
- **處置方案 (Adopt & Fix)**:
  1. 將文檔與 API 參考中的工具名稱更新為 li1688_similar_product。
  2. 在供應鏈數據獲取流程中實作防禦性容錯：若 1688 工具不可用，自動輸出友善降級提示並跳過供應鏈環節，避免中斷主體分析流程。

### 2. Issue #2: 諮詢個問題（TOOL_NAME 來源與流量關鍵詞精確度）
- **問題本質**: 用戶困惑找不到具體 TOOL_NAME，且發現流量關鍵詞中包含非該 ASIN 下的詞彙。
- **處置方案 (Documented & Handled)**:
  1. 完善 SKILLS/skills/amazon-analyse/references/api-tools-reference.md 與各 Skill 的 API 工具對照表。
  2. 於文檔中標明說明：亞馬遜自然流量與推薦演算法會將關聯競品詞、變體詞與大盤熱搜詞納入流量來源，若需精準聚焦該 ASIN，可由 LLM 結合產品詳情執行二次關聯性過濾。

### 3. Issue #3: 加一個 product-research Skill 的快速體驗入口
- **問題本質**: 第三方平台 (ClawMama) 提出在 README 中加入外部導流試用連結。
- **審查決策 (Reject)**:
  - **不予採納**。本專案為完全開源、本地執行的工具集，不依賴或導流至第三方商業 SaaS 平台，避免外部依賴失效與隱私風險。本專案直接在本地提供完備的快速體驗指引。

### 4. Issue #4: VOKO 項目自薦：AI Agent 的跨平台通信與協作層
- **問題本質**: 外部專案自薦與宣傳。
- **審查決策 (Reject)**:
  - **不予採納**。無關本專案亞馬遜跨境電商選品定位，關閉並記錄。

### 5. Issue #5: Sorftime 會員能否使用本工具集
- **問題本質**: 用戶詢問一般 Sorftime 網頁版會員是否可直接使用，或需透過 WebBridge。
- **處置方案 (Documented in FAQ)**:
  - 於 README.md 與 CLAUDE.md 新增 FAQ 說明：本專案依賴 MCP 協議通訊，必須配置相應的 MCP API Key；若僅有網頁端會員，需向官方申請 MCP 服務憑證。

### 6. Issue #6: Codex 要怎麼用這套 skill 啊
- **問題本質**: 用戶詢問 Codex (Desktop / CLI) 環境下的安裝與調用方法。上游缺乏具體引導。
- **處置方案 (Adopt & Implement)**:
  - **重要增強**！於 README.md、README.en.md、CLAUDE.md 與 AGENTS.md 中正式補齊 **Codex 專屬整合指引**：
    1. **全域安裝**: 支援將 SKILLS/skills/* 掛載至 ~/.codex/skills/（Windows: %USERPROFILE%\.codex\skills\）。
    2. **專案本地執行**: 在本倉庫根目錄直接啟動 codex，代理將自動識別並執行本專案 Skills。
    3. **MCP 配置**: 指引如何將 .mcp.json 整合進 Codex 的設定檔中。

---

## 2026-09-20: 繁體中文全庫在地化與 Windows 專屬改造

- **決策**: 將全倉庫 378 個檔案全面翻譯為標準繁體中文（台灣跨境電商習慣用語），包含代碼註解、.mcp.json、SKILLS、提示詞與報表範例。
- **檔名正名**: 11 處簡體中文檔名/目錄透過 git mv 重新命名並同步更新程式碼引用。
- **平台專注**: 清除非 Windows 平台冗餘腳本與指令，專注 **Windows 11 + PowerShell** 開發與運營環境。
