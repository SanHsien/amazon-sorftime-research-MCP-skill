# AGENTS.md

給 Codex、Claude Code、Cursor 與其他自動化代理在本專案工作時的指引。

## 專案定位

這是 [`liangdabiao/amazon-sorftime-research-MCP-skill`](https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill) 的 fork。
專案核心為專為亞馬遜跨境賣家打造的開源智慧選品與運營工具箱，整合四大電商 MCP（Sorftime、Sif、西柚洞察、賣家精靈）數據，提供包含全品類分析、競品拆解、差評挖掘、關鍵詞調研與 8 步爆款 Listing 生成等九大 AI 技能。

`origin` 是 `SanHsien/amazon-sorftime-research-MCP-skill`，`upstream` 是原作者 repo，預設分支皆為 `main`。
本 fork 的維護差異記在 [`FORK.md`](FORK.md) 與 [`docs/fork/DECISIONS.md`](docs/fork/DECISIONS.md)。

主要開發與完整驗收環境是 **Windows 11 + PowerShell**。

## 硬性邊界

- **對外只打主人的 repo。** PR、push、release 一律指向 `SanHsien/amazon-sorftime-research-MCP-skill`。
  對上游開 PR 或 push 預設絕對禁止，除非維護者在當次對話明確同意。
- 每個工作環境先確認 `gh repo set-default SanHsien/amazon-sorftime-research-MCP-skill`。
- 日常開發推送到 `origin/main` 前，必須通過 Windows 閘門：
  `pwsh -NoProfile -File tools/dev_check.ps1 -Quick`（或完整無參數版本）。
- 保持乾淨工作目錄，不隨意刪除上游核心數據與報表範例。

## 核心技能與架構

本專案支援 9 大核心分析與選品運營技能，位於 `SKILLS/skills/`：
1. **amazon-analyse**: 競品 Listing 全維度穿透分析 (`/amazon-analyse {ASIN} {SITE}`)
2. **category-selection**: 品類自動化選品五維評分模型 (`/category-select "{品類}" {SITE}`)
3. **keyword-research**: 關鍵詞深度調研與 8 維智慧分類 (`/keyword-research {ASIN} {SITE}`)
4. **review-analysis**: 買家差評深度挖掘與痛點改善建議 (`/review-analysis {ASIN} {SITE}`)
5. **product-research**: LLM 驅動選品深度調研與決策 (`/product-research "{產品詞}" {SITE}`)
6. **sif-amazon-research**: Sif MCP 流量診斷、廣告審查與增長優化 (`/sif-amazon-research`)
7. **xiyou-insight**: 西柚洞察 7 大場景分析：廣告監控、流量缺口、競品拆解等 (`/xiyou-insight`)
8. **sellersprite-amazon-research**: 賣家精靈 43 個工具鏈，全鏈路選品與藍海挖掘
9. **amazon-listing-builder**: Cosmo 語義算法 + Rufus/Alexa 8 步工作流打造爆款 Listing

## 開發與驗證命令

```powershell
# 1. 執行本地開發與完整性測試
python -m pytest tests -v

# 2. 查驗上游更新水位
python tools/check_upstream_updates.py --strict

# 3. 完整 Windows 閘門檢查
pwsh -NoProfile -File tools/dev_check.ps1 -Quick
```

