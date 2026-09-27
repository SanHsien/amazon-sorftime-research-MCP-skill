# Fork 維護說明

本 repo fork 自 [`liangdabiao/amazon-sorftime-research-MCP-skill`](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill)。

## 為什麼維護此 fork

- **整合與實踐**: 專為亞馬遜跨境賣家打造的開源智慧選品與運營工具集，深入整合 Sorftime、Sif、西柚洞察、賣家精靈等四大電商 MCP 服務。
- **Windows-first 開發環境**: Windows 11 + PowerShell 為主要開發、驗證與部署環境。
- **正體中文在地化**: 提供繁體中文主要文件與英文映象，最佳化跨境電商術語對齊。
- **自動化治理與質量閘門**: 建立可重現的 Windows 開發 gate（`tools/dev_check.ps1`）、上游更新水位監控（`tools/check_upstream_updates.py`）與自動化 CI 測試。
- **安全憑證管理**: 規範環境變數模板（`.env.example`），防止正式 API Key 外洩。

**原則明確：修的是上游的 bug 且獲明確同意才送回去；這裡獨創的檔案、測試與 Windows 維護骨架留在這裡。**

## 與上游的差異對照

| 專案 | 說明 |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | 本 fork 的 AI 代理協作規範與操作指引 |
| `NOTICE.md` / `FORK.md` | 來源、授權與本 fork 定位說明 |
| `tools/dev_check.ps1` | Windows 本地一鍵 gate（Python Syntax + Tests + UpstreamCheck） |
| `tools/check_upstream_updates.py` | 上游 commit / PR / Issue 增量查驗工具 |
| `tools/upstream_baseline.json` | 上游已審核水位基準檔 |
| `.github/workflows/dev-check.yml` | GitHub Actions 自動化 CI 測試與語法檢查 |
| `.github/workflows/upstream-check.yml` | 定期與 upstream 檢查新 commit 與 ticket |
| `docs/fork/DECISIONS.md` / `UPSTREAM.md` | fork 決策紀錄與上游同步指引 |
| `.cursor/rules/no-upstream-pr.mdc` | 代理規範：嚴禁向未授權的上游開 PR 或推程式碼 |

## 分支與 remote

- `origin/main`：`SanHsien/amazon-sorftime-research-MCP-skill`，主要維護線。
- `upstream/main`：`liangdabiao/amazon-sorftime-research-MCP-skill` 原作者倉庫，只追蹤、不推送。
- 日常修改在透過 gate（`pwsh -NoProfile -File tools/dev_check.ps1 -Quick`）後推送到 `origin/main`。

不要 `git push upstream`。同步方式見 [`docs/fork/UPSTREAM.md`](docs/fork/UPSTREAM.md)。

## 開發環境快速啟動

```powershell
git clone https://github.com/SanHsien/amazon-sorftime-research-MCP-skill.git
cd amazon-sorftime-research-MCP-skill
gh repo set-default SanHsien/amazon-sorftime-research-MCP-skill
pip install -r requirements.txt
pwsh -NoProfile -File tools/dev_check.ps1 -Quick
```

