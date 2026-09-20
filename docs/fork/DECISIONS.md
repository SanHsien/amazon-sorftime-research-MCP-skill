# Fork 決策紀錄 (DECISIONS.md)

本檔案記錄本 fork 相對於上游的所有架構決策、取捨與已審核變更。

## 2026-09-20: Fork 建立與 Windows 開發環境初始化

- **背景**：Fork `liangdabiao/amazon-sorftime-research-MCP-skill`，建立 Windows-first 治理與自動化驗證機制。
- **基準版本**：Commit `1b7afac85afc8d84529233698b5ea22fd3414e1e` (Date: 2026-07-08)。
- **治理決策**：
  1. 對外只打主人的 repo（`SanHsien/amazon-sorftime-research-MCP-skill`），嚴禁自動向上遊開 PR 或 push。
  2. 設定 `gh repo set-default SanHsien/amazon-sorftime-research-MCP-skill`，並透過 `gh repo set-default --view` 驗證。
  3. 建立 `tools/dev_check.ps1`，包含 Python 語法檢驗、依賴檢驗、MCP 與 Skills 結構檢查及上游水位線查驗。
  4. 建立每週自動執行的 `upstream-check.yml` 與 CI `dev-check.yml`，對齊 `hypit` 與其他 repo 的上游查驗水位線架構。
  5. 補充 `requirements.txt`、`pyproject.toml` 與 `.env.example`，標準化 Python 開發環境。

## 2026-09-20: 語系繁體化與上游 PR/Issue 水位審查

### 1. 繁體中文與語系重整
- **README 重構**：
  - `README.md` 改以繁體中文（臺灣跨境電商習慣用語）為主。
  - 保留英文版為 `README.en.md`。
  - 補充四大電商 MCP（Sorftime、Sif、西柚洞察、賣家精靈）與九大 AI 選品運營技能的詳細功能、斜線指令與使用案例。
- **版權與來源致敬**：
  - 新增 `NOTICE.md` 標明原作者 `liangdabiao` 與來源倉庫。
  - 建立 `FORK.md` 說明本 fork 定位與 Windows-first 改良。

### 2. 上游 Issues #1 ~ #6 審查紀錄
- **#1 1688成本獲取失敗**：第三方供應鏈 API 介面逾時或 Cookie 需更新，本 fork 保留原邏輯並於相關 script 加入容錯。
- **#2 諮詢個問題** / **#5 大佬 我想問個問題**：一般使用問題，無需程式碼變更。
- **#3 加一個 product-research Skill 的快速體驗入口**：上游已在後續 commit 補齊 product-research。
- **#4 VOKO 專案自薦**：外部專案推廣，不予採納。
- **#6 大佬，codex要怎麼用這套skill啊**：本 fork 完善了 Codex 與 Claude Code 的整合指引，支援在 `.codex` / Skills 目錄下使用。

