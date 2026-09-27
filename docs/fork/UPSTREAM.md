# 上游同步指引 (UPSTREAM.md)

## 上游 Remote 設定

```powershell
git remote -v
# 應確認包含：
# origin    https://github.com/SanHsien/amazon-sorftime-research-MCP-skill.git
# upstream  https://github.com/liangdabiao/amazon-sorftime-research-MCP-skill.git
```

## 檢查上游更新

```powershell
python tools/check_upstream_updates.py
```

- 若上游有新 commit 或 Issue 更新，報告會產出在 `upstream-review-report.md`。
- 逐筆審閱後，在 `docs/fork/DECISIONS.md` 記錄採納／略過決策。
- 推進 `tools/upstream_baseline.json` 的水位線，並執行 `tools/dev_check.ps1` 驗證。
