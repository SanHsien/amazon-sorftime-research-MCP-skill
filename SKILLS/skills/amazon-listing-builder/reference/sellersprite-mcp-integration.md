# 賣家精靈 MCP 整合方法

> 本專案已配置 sellersprite MCP（`.mcp.json`）。本檔案說明如何呼叫各工具獲取真實資料。

---

## 一、連線配置（已完成）

`.mcp.json`：
```json
{
  "mcpServers": {
    "sellersprite": {
      "url": "https://mcp.sellersprite.com/mcp",
      "headers": {
        "secret-key": "<YOUR_KEY>"
      }
    }
  }
}
```

**關鍵**：
- URL 必須是 `https://mcp.sellersprite.com/mcp`（不是 `/sse`）
- 金鑰透過 `headers.secret-key` 傳入（不是 URL 引數）

---

## 二、呼叫方式

### 方式 A：MCP 客戶端（推薦）
直接呼叫 `mcp__sellersprite__<tool_name>`。

### 方式 B：curl（備用）
```bash
curl -s -X POST "https://mcp.sellersprite.com/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "secret-key: <YOUR_KEY>" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call",
       "params":{"name":"<tool>","arguments":{...}}}'
```

### 方式 C：Python（批次場景）
```python
import json, urllib.request
payload = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"keyword_miner","arguments":{"request":{
        "marketplace":"US","keyword":"artificial flowers"}}}}}).encode()
req = urllib.request.Request("https://mcp.sellersprite.com/mcp",
    data=payload,
    headers={"Content-Type":"application/json",
             "Accept":"application/json, text/event-stream",
             "secret-key":"<KEY>"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    result = json.loads(data['result']['content'][0]['text'])
```

---

## 三、本 Skill 常用工具對映

### 第一步：關鍵詞分層詞庫

| 資料需求 | 工具 | 引數模式 |
|---------|------|---------|
| 關鍵詞挖掘 | `keyword_miner` | `request` 巢狀 |
| 趨勢驗證 | `keyword_research_trends` | 扁平引數 |
| 競品關鍵詞反查 | `traffic_keyword` | `request` 巢狀 |
| 競品出單詞 | `keyword_order` | `request` 巢狀 |

### 第二步：使用者問題庫

| 資料需求 | 工具 | 引數 |
|---------|------|------|
| 競品評論（差評主題） | `review` | `{"marketplace":"US","asin":"B0XXX"}`（扁平） |
| 競品 Listing（QA 不支援 MCP，前臺手動抓） | `asin_detail` | 扁平 |

> ⚠️ `review` 每次最多返回 20 條，是樣本資料。

### 第三步：賣點證據庫

主要靠人工：供應鏈資訊、產品規格、測試資料、認證材料。
**賣家精靈不提供產品內部資料**。

### 第四步：標題、第五步：五點、第六步：A+
基於前三步資料生成，**不需要直接呼叫 MCP**。

### 第七步：Search Terms

基於第一步詞庫，對比前臺已出現詞，**不需要直接呼叫 MCP**。

### 第八步：QA
基於第二步問題庫，**不需要直接呼叫 MCP**。

### 上線後迭代

| 資料需求 | 工具 |
|---------|------|
| 當前 Listing 流量診斷 | `traffic_listing` |
| 關鍵詞出單表現 | `keyword_order` |
| 價格分佈 | `market_price_distribution` |

---

## 四、關鍵陷阱（已踩過的坑）

### 陷阱 1：keyword_research 忽略 keyword 引數
- 現象：傳 `keyword` 引數後，返回全球熱詞，不相關
- 解決：**用 `keyword_miner` 替代**

### 陷阱 2：keyword_research_trends 欄位名
- 文件說：`month` / `searches` / `growth`
- 實際：`time` / `search` / `chainGrowth`（環比）/ `yearlyGrowth`（同比）

### 陷阱 3：review 限制
- `size` 引數無效，**最多返回 20 條**
- 評分分佈是樣本，不代表總體
- 欄位名：`content`（非 body）、`date`（非 createTime）

### 陷阱 4：ABA 工具欄位
- aba_research_trend 只有 `searches` / `rank`，沒有 `clickShareRate` / `conversionShareRate`

### 陷阱 5：traffic_source 引數
- 文件說用 `request` 巢狀
- 實際需要**扁平引數** + `"q": "asin"`

### 陷阱 6：刻度轉換
- 集中度欄位（top*Crn / l*NewRatio）是 0~1 小數，展示 ×100
- purchaseRate / cvsShareRate / monopolyClickRate 是 0~1，展示 ×100
- returnRatio / *Proportion 已是 0~100 百分數，不再換算

### 陷阱 7：nodeLabelLocale 不可靠
- `Microphones` → 錯誤翻譯成"顯微鏡"
- 始終用 `nodeLabelPath`（英文完整路徑）

### 陷阱 8：keepa_info 欄位
- 不存在 `currentPrice` / `bsrHistory`
- 用 `buyBox: [{timePoint, value}]` 和 `bsr: [{timePoint, value}]`

---

## 五、呼叫示例

### 示例 1：擴充套件關鍵詞（第一步）
```python
import json, urllib.request

def call_mcp(tool, args):
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
        "params":{"name":tool,"arguments":args}}).encode()
    req = urllib.request.Request("https://mcp.sellersprite.com/mcp",
        data=payload,
        headers={"Content-Type":"application/json",
                 "Accept":"application/json, text/event-stream",
                 "secret-key":"<YOUR_KEY>"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(json.loads(resp.read())['result']['content'][0]['text'])

# 關鍵詞擴充套件
result = call_mcp("keyword_miner", {"request":{
    "marketplace":"US",
    "keyword":"artificial flowers outdoor"
}})
print(result)
```

### 示例 2：抓競品評論（第二步）
```python
# 獲取競品 ASIN 評論
result = call_mcp("review", {
    "marketplace":"US",
    "asin":"B0XXXXXXX"
})
# 注意：最多返回 20 條，是樣本
```

### 示例 3：競品關鍵詞反查（第一步補充）
```python
result = call_mcp("traffic_keyword", {"request":{
    "marketplace":"US",
    "asin":"B0XXXXXXX"
}})
```

---

## 六、MCP 資料缺失時的處理

如果某些資料 MCP 拿不到（如自己的廣告搜尋詞報告、客服記錄），**必須由人工補充**，不能讓 AI 編造。

### 資料缺失標註規範

```markdown
## 資料需求清單

| 資料 | 來源 | 狀態 |
|------|------|------|
| 關鍵詞搜尋量 | keyword_miner | ✅ 已獲取 |
| 競品評論 | review | ✅ 已獲取（樣本 20 條） |
| 自己的廣告搜尋詞報告 | 亞馬遜後臺 | ⚠️ DATA_MISSING（人工補充） |
| 客服記錄 | 客服系統 | ⚠️ DATA_MISSING（人工補充） |
| 供應鏈材料 | 工廠 | ⚠️ DATA_MISSING（人工補充） |
```

---

## 七、推薦呼叫順序

```
1. keyword_miner → 關鍵詞池
2. keyword_research_trends → 趨勢驗證
3. traffic_keyword (競品 ASIN) → 競品出單詞
4. asin_detail (競品 ASIN) → 競品 Listing 結構
5. review (競品 ASIN) → 差評主題
6. market_price_distribution → 定價參照
```

6 次呼叫即可拿到第一步和第二步的核心資料。

---

## 八、引用

更多細節參見 `sellersprite-amazon-research` skill 的：
- `skill.md` — 42 個工具完整清單
- `reference/tools_index.md` — 工具索引
- `comprehensive/listing-optimizer.md` — Listing 診斷流程
