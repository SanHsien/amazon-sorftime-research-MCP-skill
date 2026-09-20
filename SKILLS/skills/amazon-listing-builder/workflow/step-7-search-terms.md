# 第七步：Search Terms（後臺搜尋詞）

> **ST 不是垃圾桶**。它的作用是補充索引，不是把所有沒放進標題的詞都塞進來。

## 🚨 本步不調 MCP

本步基於**第一步完整詞庫 + 第四步最終標題 + 第五步五點**做差集運算（找出未在前臺出現的詞），不再呼叫 MCP 工具。

### 資料來源
- 完整詞庫：第一步 MCP 輸出
- 前臺已出現詞：第四步標題 + 第五步五點
- ST 候選詞：詞庫 - 前臺詞 = 後臺補充詞

---

## 一、ST 的真實價值

| 該做的 | 不該做的 |
|-------|---------|
| 放同義詞、變體詞、錯拼詞 | 重複標題已有的詞 |
| 放次要場景詞 | 放競品品牌詞 |
| 放補充索引詞 | 堆砌不相關詞 |
| 遵守 250 位元組限制 | 超欄位限制 |
| 用空格分詞 | 用逗號分隔 |

---

## 二、ST 詞源分類

把第一步的關鍵詞分層詞庫重新分類：

| 詞類 | 是否進 ST | 示例 |
|------|----------|------|
| 核心品類詞（L1） | ❌ 已在前臺 | artificial flowers, faux plants |
| 功能屬性詞（L2） | ❌ 已在前臺 | UV resistant, fade resistant |
| 主場景詞（L3） | ❌ 已在前臺 | patio, garden, porch |
| 次場景詞（L3 變體） | ✅ 進 ST | balcony, terrace, deck |
| 問題詞（L4） | 部分進 ST | for outdoor planters, no watering |
| 規格詞（L5） | ❌ 已在前臺 | 12 bundles |
| **同義詞** | ✅ 進 ST | faux greenery, fake plants |
| **變體詞** | ✅ 進 ST | fake florals, silk flowers |
| **錯拼詞** | ✅ 進 ST | articifial flowers, fake flower |
| **次要場景** | ✅ 進 ST | cemetery, front door, backyard |

---

## 三、抗 UV 戶外模擬植物 ST 示例

假設標題和五點已覆蓋：artificial flowers, outdoor, UV resistant, patio, garden, porch, planters, 12 bundles, fade resistant, realistic。

**ST 候選詞**：
```
faux greenery fake plants outdoor silk flowers front porch decor planter filler backyard terrace deck balcony cemetery window box summer decor wedding centerpiece no watering maintenance free decor realistic fake flower arrangement
```

**最佳化後（去重 + 控制位元組）**：
```
faux greenery silk flowers fake plants front porch planter filler backyard terrace deck balcony cemetery window box summer wedding centerpiece low maintenance outdoor decor fake flower arrangement
```

---

## 四、位元組限制與格式規範

| 站點 | 位元組限制 | 分隔方式 |
|------|---------|---------|
| 美國站 | 250 位元組 | 空格 |
| 歐洲站 | 250 位元組 | 空格 |
| 日本站 | 100 位元組（jp） | 空格 |

### 格式規則
1. 用 **空格** 分隔，**不要用逗號**
2. 全小寫（節省位元組）
3. 不要重複任何詞
4. 單數/複數只放一次（系統會自動匹配）
5. 不要用引號、連字元、特殊符號

---

## 五、給 Codex 的提示詞（本步專用）

> 輸入：完整詞庫、當前標題、當前五點描述。
>
> 任務：
> 1. 找出標題和五點**已經出現**的關鍵詞（這些不進 ST）
> 2. 從詞庫中篩選未在前臺出現的詞，作為 ST 候選
> 3. 按優先順序排序：同義詞 > 次場景 > 問題詞變體 > 錯拼詞
> 4. 控制總位元組在 250 以內（美國站）
> 5. 用空格分隔，全小寫
> 6. 排除競品品牌詞、誇大詞、不相關詞
> 7. 輸出 ST 文字 + 位元組計數 + 已排除詞清單（含原因）

---

## 六、合規紅線

| 禁用 | 原因 |
|------|------|
| 競品品牌名（其他賣家品牌） | 違反亞馬遜品牌政策 |
| 促銷詞（free shipping, best seller, sale） | 平臺禁止 |
| 主觀誇大詞（best, #1, top rated） | 合規風險 |
| 醫療/環保絕對詞（cure, 100% eco） | 合規風險 |
| 重複前臺已出現的詞 | 浪費位元組 |
| 任何不相關的熱詞 | 影響相關性 |

---

## 七、輸出模板

```markdown
# Search Terms 草稿 — {產品名}

## ST 文字（已最佳化）
```
faux greenery silk flowers fake plants front porch planter filler backyard terrace deck balcony cemetery window box summer wedding centerpiece low maintenance outdoor decor fake flower arrangement
```

**總位元組**：238 / 250

## 已排除詞清單
| 詞 | 原因 |
|----|------|
| artificial flowers | 標題已出現 |
| UV resistant | 五點已出現 |
| [其他品牌] | 競品品牌詞 |
| best | 誇大詞 |

## 候選詞優先順序排序
1. 同義詞：faux greenery, silk flowers
2. 次場景：terrace, deck, balcony, backyard, cemetery, window box
3. 問題詞變體：low maintenance
4. 錯拼詞：（如適用）
```

---

## 八、檢查清單

- [ ] 位元組 ≤ 250（美國）/ ≤ 100（日本）
- [ ] 用空格分隔，無逗號
- [ ] 全小寫
- [ ] 無重複
- [ ] 無競品品牌詞
- [ ] 無誇大詞
- [ ] 無前臺已出現的詞
- [ ] 已排除詞清單完整
