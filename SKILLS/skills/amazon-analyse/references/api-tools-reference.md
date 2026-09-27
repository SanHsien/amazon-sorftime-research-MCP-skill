# Sorftime MCP 工具參考 (curl 呼叫格式)

**注意**：Sorftime MCP 使用 SSE 協議，所有工具呼叫格式如下：

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

---

## 核心工具

### 1. 產品詳情 (product_detail)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"B07PQFT83F"}}}'
```

### 2. 產品搜尋 (product_search) - 用於驗證ASIN
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_search","arguments":{"amzSite":"US","keyword":"PRODUCT_NAME","page":1}}}'
```

### 3. 使用者評論 (product_reviews)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_reviews","arguments":{"amzSite":"US","asin":"ASIN","reviewType":"Both"}}}'
```
- reviewType: "Positive" (4-5星), "Negative" (1-3星), "Both" (全部)

### 4. 流量關鍵詞 (product_traffic_terms)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"product_traffic_terms","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 5. 競品關鍵詞佈局 (competitor_product_keywords)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"competitor_product_keywords","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 6. 產品趨勢 (product_trend)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"product_trend","arguments":{"amzSite":"US","asin":"ASIN","productTrendType":"SalesVolume"}}}'
```
- productTrendType: "SalesVolume" (銷量), "SalesAmount" (銷售額), "Price" (價格), "Rank" (排名)

### 7. 關鍵詞詳情 (keyword_detail)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"keyword_detail","arguments":{"amzSite":"US","keyword":"KEYWORD"}}}'
```

---

## 併發請求最佳實踐

為了提高效率，可以同時發起多個請求：

```bash
# 併發獲取所有資料（使用不同的 id）
curl ... '{"id":1,...}' &
curl ... '{"id":2,...}' &
curl ... '{"id":3,...}' &
curl ... '{"id":4,...}' &
curl ... '{"id":5,...}' &
curl ... '{"id":6,...}' &
wait
```

或在同一行使用 `&&` 連線（順序執行）：
```bash
(curl ... '{"id":1,...}' && curl ... '{"id":2,...}' && ...)
```

---

## 支援的亞馬遜站點

US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

---

## 故障排查

### 問題1：ASIN 未找到

**現象**：返回 "未查詢到對應產品，請檢查傳入產品ASIN"

**解決方案**：
1. 使用 product_search 工具驗證：
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_search","arguments":{"amzSite":"US","keyword":"ASIN_OR_KEYWORD","page":1}}}'
```

2. 檢查 ASIN 格式是否正確（10位字母數字）
3. 確認產品是否在該站點上架
4. 嘗試其他站點

### 問題2：資料儲存到臨時檔案

**現象**：返回 "Output too large... Full output saved to: ..."

**解決方案**：
```bash
# 使用 Read 工具讀取臨時檔案
Read <file_path>
```

### 問題3：Unicode 跳脫字元

**現象**：中文顯示為 `\u4EA7\u54C1ASIN\u7801`

**解決方案**：
- 大多數現代工具會自動解碼
- 如果需要手動解碼，使用 Python：
```python
import json
print(json.loads('"\\u4EA7\\u54C1ASIN\\u7801"'))
```

### 問題4：MCP 工具不響應

**現象**：curl 請求超時或無響應

**解決方案**：
1. 檢查網路連線
2. 驗證 API Key 是否有效
3. 檢查 Sorftime 服務狀態：`curl -I https://mcp.sorftime.com`
4. 增加超時時間：`curl --max-time 30`

### 問題5：部分資料缺失

**現象**：評論、趨勢資料返回 "沒有相關資料"

**解決方案**：
- 新產品可能沒有歷史趨勢資料
- 部分產品可能沒有評論資料
- 繼續使用可用資料進行分析，標註缺失部分
