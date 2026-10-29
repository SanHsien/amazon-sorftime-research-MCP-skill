# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `a76414844362` 查的快照，開工前先重查 GitHub。

## 現況

這是 liangdabiao/amazon-sorftime-research-MCP-skill（亞馬遜選品 MCP skill 工具集）的繁中、Windows-first 維護 fork。維護面健康：`main` 上 CodeQL、Dependency freshness、Dev Check、Upstream check 最近一次皆 success，open PR 0 筆、Dependabot 與 Code scanning 告警 0 筆；issue 功能已停用，issue 數「未查到」不是 0（2026-10-29 `gh` 查詢）。上游在 2026-10-28 又推了一個 commit `99c65df845e3`（只改 `README.md`，+2 行），而本 fork 水位 `reviewed_through` 停在 `568be294b159`（`tools/upstream_baseline.json`），所以有一項待審；`Dev Check` 會嚴格比對上游，所以推送後它在 `main` 轉紅，這是「上游有未審項目」的提醒，不是新故障（2026-10-29 run 結果）。

## 近期：可以直接動手

| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 審上游 commit `99c65df845e3` 並推進水位 | 上游最後 push 晚於本 fork 水位；內容僅 README 兩行，多半只需判斷「是否同步到繁中 README」 | 在 `docs/fork/DECISIONS.md` 記一則審查結論；`tools/upstream_baseline.json` 的 `reviewed_through` 更新；`python tools/check_upstream_updates.py --strict` exit 0；跑完還原被改寫的 `upstream-review-report.md` | Claude Haiku | `gh api repos/liangdabiao/amazon-sorftime-research-MCP-skill/commits?per_page=3`；`tools/upstream_baseline.json` |
| 決定修或不修兩個上游邏輯錯誤：`analyze_category._calculate_scores` 讀不到帶中文標籤前綴的占比值（競爭烈度恆 18 分）、`parse_category_report.extract_products` regex 欄位順序與真實回應相反（恆得 0 產品） | 深掃報告發現 `top3_brands_sales_volume_share` 的值帶前綴，`safe_float` 解析不了而退回 0；`extract_products` 的 regex 欄位順序與真實回應相反。兩者同屬「上游邏輯錯誤是否由 fork 修」的取捨，一起決定；目前沒有人決定修不修 | 對每一個二擇一：(a) 加重現測試（修前紅、修後綠）並在 `docs/fork/DECISIONS.md` 記錄偏離上游；(b) 在 `docs/fork/DECISIONS.md` 新增一則「決定不修」並附理由。不論哪個，`pytest` 綠 | Claude Opus | `docs/fork/DECISIONS.md:13`（`analyze_category` 相關）；深掃報告（2026-10-26） |

## 中期：等條件成立再做

| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 把 ruff 納入 lint gate，並取消 ruff 延後 | 維護者決定在 CI 或 `dev_check.ps1` 跑 ruff；或 ruff 超過 `deferredLatest`（延後自動到期） | CI 實際執行 `ruff check` 且綠；`.github/dependency-deferrals.json` 的 ruff 條目移除或更新；`check_dependency_freshness.py --strict` exit 0 | Codex | `.github/dependency-deferrals.json`（ruff 條目） |
| 補 Sif、西柚洞察、賣家精靈三技能的回應鍵名簡繁相容 | 維護者實際使用這三個廠商之一，或拿到真實回應樣本（目前只驗證過 Sorftime） | 以真實回應樣本寫測試，修前紅修後綠；DECISIONS「已知未涵蓋」該項更新 | Claude Sonnet | `docs/fork/DECISIONS.md:12`；深掃報告「未涵蓋」 |
| 對真實 Sorftime API 實機跑一次選品流程 | 維護者提供可用的付費 Sorftime 金鑰並同意消耗額度 | 一份完整選品流程的實際輸出（產品數、市場規模評分非預設值）貼入 `docs/fork/DECISIONS.md` | 維護者 | `docs/fork/DECISIONS.md:7`（鍵名事故以離線樣本驗證，未實機） |

## 刻意不做

| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 動 `.mcp.json` 內的上游金鑰 | 維護者決定維持原樣（`docs/fork/DECISIONS.md:17`） | 維護者改變決定，或該金鑰被確認為有效的私人憑證 |
| 轉換回應「值」裡的簡體標籤（如 `销量最大产品月销量:10533`） | 影響小，且值屬 API 內容不是鍵名（`docs/fork/DECISIONS.md:12`） | 下游報告因此出現使用者看得到的錯字或解析錯誤 |
| 修改 `keyword_collector._parse_product_info` 的簡體標籤比對 | 上游本就比對簡體、回應多半是 JSON | 實測該路徑在真實回應下取不到資料 |
| 對上游開 PR／回貢 | 預設只打 `SanHsien/` 名下 repo | 維護者在新的對話中明確要求回貢 |

## 維護方式

fork：以 `Upstream check` workflow 為訊號（failure＝上游有未審項目），審完在 `docs/fork/DECISIONS.md` 記採用或不採用的理由並推進水位。本機跑 `check_upstream_updates.py --strict` 會改寫 `upstream-review-report.md`，跑完要還原，不要提交。
