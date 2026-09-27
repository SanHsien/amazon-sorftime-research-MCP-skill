# 貢獻指南 (Contributing Guide)

感謝您對本專案的關注！本專案致力於為亞馬遜跨境電商賣家提供高品質的 AI 選品與運營工具集。

## 核心原則

1. **對外只打主人的 repo**: 本 repo 的 PR、push 與 release 一律指向 `SanHsien/amazon-sorftime-research-MCP-skill`。未經當次對話明確授權，嚴禁向上遊倉庫發起 PR 或推送。
2. **Windows-first 開發環境**: 所有程式碼與指令碼應在 Windows 11 + PowerShell 環境下驗證透過。
3. **提交前驗收閘門**: 所有變更在提交或合併前，必須透過本地驗證閘門：
   ```powershell
   pwsh -NoProfile -File tools/dev_check.ps1 -Quick
   ```

## 開發流程

1. Fork 本倉庫到您自己的 GitHub 帳號。
2. Clone 到本地並安裝 Python 依賴：
   ```powershell
   pip install -r requirements.txt
   ```
3. 建立功能分支進行修改。
4. 撰寫或更新相應的單元測試。
5. 執行 `pwsh -NoProfile -File tools/dev_check.ps1` 確保所有測試與檢查均為綠燈。
6. 向 `SanHsien/amazon-sorftime-research-MCP-skill` 的 `main` 分支發起 Pull Request。

