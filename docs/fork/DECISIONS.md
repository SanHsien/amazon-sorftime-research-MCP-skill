# Fork 決策紀錄 (DECISIONS.md)

本文件記錄本 fork 相對於上游的所有架構決策、取捨與已審核變更。

---

## 2026-10-26: 全庫繁體化波及 API 比對鍵，真實回應解析不到資料

- **缺陷來歷**: 初始 commit 用 opencc `s2twp` 轉換整個 repo，連程式裡「讀 Sorftime 回應用的鍵名」（`类目统计报告`、`Top100产品`、`top100产品月销额`…）也被改成繁體；Sorftime 實際回應仍是簡體鍵，上游 `568be29` 的真實樣本為證。結果：真實回應 `Top100產品` 取不到、產品數 0，欄位 `.get('標題')` 退回預設值，五維評分在月銷額 8,168 萬美元時只給市場規模 10 分（應為 20）。
- **修法**: 在資料進入點把簡體鍵名正規化成程式使用的繁體鍵名（`sorftime_keys.py`，`normalize_keys` 轉解析後的 JSON，`normalize_text` 轉原始 JSON 文字裡的 `"鍵":`）。簡體、繁體輸入都對得上，只轉鍵名，值與輸出文字不動。入口：`analyze_category`、`parse_sorftime_sse`、`sse_decoder`、`parse_category_report`、`extract_top_products`、`keywords_parser`、`trend_parser`、`workflow`、`data_adapter`、`generate_markdown_report`、keyword-research `data_parser`、product-research `api_client`。
- **對照表**: （限制：程式內的鍵若在上游來源找不到，簡體形式以 t2s 還原，可能與 API 實際用字不同；守門測試只檢查「有沒有在表裡」。）由 `tools/generate_sorftime_key_map.py --upstream 568be29` 產生（上游簡體原始碼與真實樣本鍵，以 `s2twp` 轉換；再補上現行程式裡 t2s 可還原的鍵），三個技能各放一份相同的 `sorftime_keys.py`。`tests/test_sorftime_keys.py` 確保程式內每個繁體鍵都在表裡、三份一致；新增鍵名沒進表會紅燈，重跑產生腳本即可。
- **已知未涵蓋**: `keyword_collector._parse_product_info` 以 `：` 分行比對標籤（上游本來就比對簡體，且回應多半是 JSON，未動）；其他廠商（Sif、西柚洞察、賣家精靈）的回應與舊版已存檔的簡體 JSON（只有 `data_adapter`、`generate_markdown_report` 讀檔時會轉）；回應裡「值」的簡體標籤（如 `销量最大产品月销量:10533`）不轉。
- **上游觀察（不改）**: stats 中 `top3_brands_sales_volume_share` 等值帶中文標籤前綴（`销量前三的品牌月销量占比:84.11%`），`analyze_category._calculate_scores` 的 `safe_float` 解析不了而退回 0，競爭烈度恆為 18 分。屬上游邏輯，列入觀察清單。

---

## 2026-10-25: `.mcp.json` 內的上游金鑰維持原樣

- **事實**: `.mcp.json` 含四把廠商金鑰，對應 sorftime、sif、xydc（西柚洞察）、sellersprite（賣家精靈）。值與上游 `liangdabiao` 版相同，自本 fork 初始 commit 起就存在。這些是上游作者的金鑰，不是本 fork 維護者的。
- **決策 (Keep as-is)**: 維護者決定維持原樣，不改、不刪、不改寫歷史。理由：上游已公開這些值，本 fork 即使移除也收不回。
- **觸發條件**: 上游輪替或移除金鑰時，本 fork 跟著同步。若有人要用本 fork 實際呼叫廠商服務，請把 `.mcp.json` 內的值換成自己的金鑰（`.env.example` 列出需要哪些憑證）。
- **備註**: 本文件刻意不重複列出金鑰值。

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

## 2026-10-24: 上游 commit 48dd966、568be29 與 Issue #7 審查

### 上游 commit（只動 README.md）
- `48dd966`（fix）：簡介改成「基於 Sorftime，Sif，賣家精靈，西柚等 MCP 服務」，並加入作者其他 skill 站點的推廣連結。
- `568be29`（Fix typo）：同一句的「Claude Skills」改為「Agent Skills」。
- **審查決策 (Skip)**：不引用。本 fork 早已整合四個 MCP 服務（Sorftime、Sif、西柚洞察、賣家精靈；見 `.mcp.json`、`AGENTS.md`、`FORK.md`），並以繁體中文說明；上游這段只是簡體版簡介改寫，沒有新資訊。推廣連結屬上游宣傳內容，本 fork 不保留。兩個 commit 都沒有程式碼變更。


### 7. Issue #7: 賣家精靈子帳號不能配置密鑰，能否直接登入亞馬遜商城讓 skill 去調用分析
- **問題本質**: Issue 內文為空；依標題，用戶只有賣家精靈子帳號、無法配置金鑰，詢問能否改由登入亞馬遜前台、讓 skill 直接抓頁面分析。上游作者回覆建議改用各 agent 的 RPA／瀏覽器控制外掛。
- **審查決策 (Not Adopted)**:
  - **不予採納，不改程式碼**。本專案的資料來源是各服務的 MCP（含賣家精靈 MCP）；改成登入亞馬遜前台抓頁面，等於換掉整個資料層，不在本 fork 範圍內，也有違反平台使用條款與帳號被封的風險。
  - 子帳號拿不到金鑰時，需向該服務申請 MCP 金鑰；邏輯與既有 Issue #5 的 FAQ（網頁會員需另申請 MCP 憑證）相同，不另加文件。

---

## 2026-09-20: 繁體中文全庫在地化與 Windows 專屬改造

- **決策**: 將全倉庫 378 個檔案全面翻譯為標準繁體中文（台灣跨境電商習慣用語），包含代碼註解、.mcp.json、SKILLS、提示詞與報表範例。
- **檔名正名**: 11 處簡體中文檔名/目錄透過 git mv 重新命名並同步更新程式碼引用。
- **平台專注**: 清除非 Windows 平台冗餘腳本與指令，專注 **Windows 11 + PowerShell** 開發與運營環境。
