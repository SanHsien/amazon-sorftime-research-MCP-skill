# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `a76414844362` 查的快照，開工前先重查 GitHub。

## 現況

這是 liangdabiao/amazon-sorftime-research-MCP-skill（亞馬遜選品 MCP skill 工具集）的繁中、Windows-first 維護 fork。維護面健康：`main` 上 CodeQL、Dependency freshness、Dev Check、Upstream check 最近一次皆 success，open PR 0 筆、Dependabot 與 Code scanning 告警 0 筆（2026-11-08 重查 open 告警各 0）；issue 功能已停用，issue 數「未查到」不是 0（2026-10-29 `gh` 查詢）。上游 2026-10-28 的 `99c65df`（只在 README 加推廣連結）已於 2026-10-29 審為不引用，水位推進到該 commit（`tools/upstream_baseline.json`、`docs/fork/DECISIONS.md`）；`Dev Check` 會嚴格比對上游，上游再前進時會轉紅提醒。兩項上游邏輯錯誤已於 2026-10-31 決策：`analyze_category` 的占比前綴解析已修正（先紅後綠測試 `tests/test_category_report_safety.py`），`parse_category_report` 的 regex 欄位順序仍不修，皆載明於 `docs/fork/DECISIONS.md`。

`tools/dev_check.ps1` 與 CI 的 Dev Check 會跑 `ruff check tools tests`；上游的技能腳本與歷史報表保持原樣以利同步，不在 lint 範圍內（全 repo 掃描有 353 個既有問題，都在上游檔案）。

## 近期：可以直接動手

目前沒有可直接動手的列；卡在外部條件的列在下面「中期」。

## 中期：等條件成立再做

| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 實測賣家精靈 MCP v2 是否破壞現有串接 | 維護者提供有效的賣家精靈金鑰，或賣家精靈公布 v2 變更說明（沒有金鑰，工具清單與欄位無法驗證；本 fork 不使用 `.mcp.json` 內的上游金鑰） | 用該金鑰跑一次賣家精靈的呼叫（端點、認證、欄位對映）；相容就在 `docs/fork/DECISIONS.md` 補實測結果與日期，不相容就列出要改的檔 | 維護者 | `docs/fork/DECISIONS.md` 2026-11-02、2026-11-08；上游 issue #8（2026-11-08 查仍 open）；`.mcp.json:27`；2026-11-08 無金鑰探測：`https://mcp.sellersprite.com/mcp` 的 `initialize` 回 200，`serverInfo` 為 `sellersprite-mcp-server` 1.0.0，無金鑰的 `tools/list` 只回單一工具 `secret_invalid` |
| 補 Sif、西柚洞察、賣家精靈三技能的回應鍵名簡繁相容 | 維護者實際使用這三個廠商之一，或拿到真實回應樣本（目前只驗證過 Sorftime） | 以真實回應樣本寫測試，修前紅修後綠；DECISIONS「已知未涵蓋」該項更新 | Claude Sonnet | `docs/fork/DECISIONS.md:12`；深掃報告「未涵蓋」 |
| 對真實 Sorftime API 實機跑一次選品流程 | 維護者提供可用的付費 Sorftime 金鑰並同意消耗額度 | 一份完整選品流程的實際輸出（產品數、市場規模評分非預設值）貼入 `docs/fork/DECISIONS.md` | 維護者 | `docs/fork/DECISIONS.md:7`（鍵名事故以離線樣本驗證，未實機） |

## 刻意不做

| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 動 `.mcp.json` 內的上游金鑰 | 維護者決定維持原樣（`docs/fork/DECISIONS.md:17`） | 維護者改變決定，或該金鑰被確認為有效的私人憑證 |
| 轉換回應「值」裡的簡體標籤（如 `销量最大产品月销量:10533`） | 影響小，且值屬 API 內容不是鍵名（`docs/fork/DECISIONS.md:12`） | 下游報告因此出現使用者看得到的錯字或解析錯誤 |
| 修改 `keyword_collector._parse_product_info` 的簡體標籤比對 | 上游本就比對簡體、回應多半是 JSON | 實測該路徑在真實回應下取不到資料 |
| 對上游開 PR／回貢 | 預設只打 `SanHsien/` 名下 repo | 維護者在新的對話中明確要求回貢 |
| 修補 `parse_category_report.extract_products` 的 regex 欄位順序錯誤（真實回應下恆得 0 產品） | 屬上游獨立輔助腳本、非標準入口 `workflow.py`；要修實質是改用 `json.loads` 重寫，會擴大與上游的分歧（`analyze_category` 因會誤導選品評級，已另行修正，見 `docs/fork/DECISIONS.md` 2026-10-31） | 上游官方釋出修正，或維護者需要依賴該獨立腳本作為主力選品流程 |

## 維護方式

fork：以 `Upstream check` workflow 為訊號（failure＝上游有未審項目），審完在 `docs/fork/DECISIONS.md` 記採用或不採用的理由並推進水位。本機跑 `check_upstream_updates.py --strict` 會改寫 `upstream-review-report.md`，跑完要還原，不要提交。
