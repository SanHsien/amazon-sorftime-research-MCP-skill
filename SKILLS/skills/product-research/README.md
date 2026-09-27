# Product Research Skill

基於 **Sorftime MCP + LLM Agent** 的 Amazon 選品深度調研技能。

## 核心特點

- **LLM 驅動**：分析、洞察、決策全部由 LLM 完成
- **互動式執行**：逐步推進，使用者可中途干預
- **輕量指令碼**：僅用於 API 呼叫和 Dashboard 渲染
- **簡化資料**：不用複雜的 unified payload 結構

## 使用方法

```
/product-research [產品關鍵詞] [站點]
```

示例：
- `/product-research "bluetooth speaker" US`
- `/product-research laptop backpack GB`

## 執行流程

```
Step 0: 資訊收集（確認站點、場景、約束）
   ↓
Step 1: 資料採集（Top100、關鍵詞、趨勢、競品）
   ↓
Step 2: 屬性標註（LLM 從標題提取維度）
   ↓
Step 3: 交叉分析（LLM 發現供需缺口）
   ↓
Step 4: 競品與 VOC（LLM 選擇競品、歸類差評）
   ↓
Step 5: 評估決策（壁壘評估 + 選品決策評分）
   ↓
Step 6: 報告輸出（Markdown + Dashboard）
```

## 輸出

- `report.md` - Markdown 完整報告（LLM 直接撰寫）
- `data.json` - 結構化資料（供 Dashboard 使用）
- `dashboard.html` - 視覺化看板（指令碼渲染）

## 與其他 Skills 的關係

```
category-selection (品類篩選五維評分)
        ↓
product-research (深度選品調研) ← 本技能
        ↓
amazon-analyse (競品 Listing 深挖)
        ↓
review-analysis (評論深度分析)
```

## 指令碼架構（極簡）

```
scripts/
├── api_client.py          # Sorftime API 呼叫 + SSE 解析
└── render_dashboard.py    # Dashboard 視覺化渲染
```

**設計原則**：
- 指令碼不做分析判斷（由 LLM 完成）
- 指令碼不做複雜計算（讓 LLM 從資料中發現）
- 指令碼僅做資料搬運（API → 結構化資料）

## 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| v2.0 | 2026-03-19 | LLM Agent 驅動，簡化指令碼架構 |
| v1.0 | 2026-03-19 | 初始版本 |

## 許可證

MIT License
