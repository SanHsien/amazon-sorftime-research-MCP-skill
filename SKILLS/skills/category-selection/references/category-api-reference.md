# 品類選品專用介面參考

本文件列出品類選品分析相關的核心介面及呼叫示例。

---

## 一、類目搜尋與確認

### 1. 類目名稱搜尋 - category_name_search

**用途**: 根據品類名稱查詢對應的類目nodeid

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"site":"US","searchName":"sofas"}}}'
```

**返回資料示例**:
```
類目名稱 | nodeId
---------|---------
Sofas | 3733551
Sofa Slipcovers | 1234567
Bean Bag Chairs | 2345678
```

---

## 二、市場趨勢資料 (11個指標)

### 趨勢指標列表

| ID | 趨勢型別 | trendIndex引數 | 用途 |
|----|----------|---------------|------|
| 1 | 類目月銷量趨勢 | 類目月銷量趨勢 | 市場規模評分 |
| 2 | 品牌數量趨勢 | 品牌數量趨勢 | 競爭烈度評分 |
| 3 | 賣家數量趨勢 | 賣家數量趨勢 | 競爭烈度評分 |
| 4 | 平均售價趨勢 | 平均售價趨勢 | 利潤空間評分 |
| 5 | 平均評論數量趨勢 | 平均評論數量趨勢 | 進入壁壘評分 |
| 6 | 平均星級趨勢 | 平均星級趨勢 | 市場成熟度 |
| 7 | 新品銷量佔比趨勢 | 上架3個月內新品銷量佔比趨勢 | 進入壁壘評分 |
| 8 | 亞馬遜自營銷量佔比 | 亞馬遜自營銷量佔比 | 競爭烈度評分 |
| 9 | Top3產品銷量佔比 | 銷量前3的產品銷量佔比趨勢 | 市場集中度 |
| 10 | Top3品牌銷量佔比 | 銷量前3的品牌銷量佔比趨勢 | 市場集中度 |
| 11 | Top3賣家銷量佔比 | 銷量前3的賣家銷量佔比趨勢 | 市場集中度 |

### 呼叫示例

```bash
# 併發呼叫11個趨勢介面
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_trend","arguments":{"site":"US","nodeId":"3733551","trendIndex":"類目月銷量趨勢"}}}' &

curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"category_trend","arguments":{"site":"US","nodeId":"3733551","trendIndex":"品牌數量趨勢"}}}' &

# ... 繼續其他9個介面
```

---

## 三、Top100產品資料

### 類目報告 - category_report

**用途**: 獲取品類Top100產品列表

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"category_report","arguments":{"site":"US","nodeId":"3733551"}}}'
```

**返回資料欄位**:
| 欄位 | 說明 |
|------|------|
| ASIN | 產品ASIN |
| Title | 產品標題 |
| Brand | 品牌 |
| Price | 價格 |
| Rating | 評分 |
| ReviewCount | 評論數 |
| MonthlySales | 月銷量 |

---

## 四、產品詳情批次獲取

### 產品詳情 - product_detail

**用途**: 獲取單個產品詳細資訊

```bash
# 需要對100個ASIN逐個呼叫
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":100,"method":"tools/call","params":{"name":"product_detail","arguments":{"site":"US","asin":"B07PWTJ4H1"}}}'
```

**批次獲取策略**:
- 併發呼叫，每次最多10個
- 使用不同的id (100-199)
- 失敗的ASIN跳過，記錄日誌

---

## 五、類目關鍵詞

### 類目核心關鍵詞 - category_keywords

**用途**: 獲取類目熱搜關鍵詞

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":200,"method":"tools/call","params":{"name":"category_keywords","arguments":{"site":"US","nodeId":"3733551","page":1}}}'
```

**返回資料欄位**:
| 欄位 | 說明 |
|------|------|
| keyword | 關鍵詞 |
| searchVolume | 月搜尋量 |
| recommendBid | 推薦競價 |

---

## 六、供應鏈分析

### 1688產品搜尋 - products_1688

**用途**: 獲取1688採購價格

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":300,"method":"tools/call","params":{"name":"products_1688","arguments":{"searchName":"沙發","page":1}}}'
```

---

## 七、TikTok跨平臺分析

### TikTok產品搜尋 - tiktok_product_search

**用途**: 搜尋TikTok相似產品

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":400,"method":"tools/call","params":{"name":"tiktok_product_search","arguments":{"site":"US","searchName":"sofa","page":1}}}'
```

---

## 資料收集檢查清單

- [ ] Step 1.1: 類目搜尋，獲取nodeid
- [ ] Step 1.2: 11個市場趨勢指標 (併發)
- [ ] Step 1.3: Top100產品列表
- [ ] Step 1.4: 100個產品詳情 (併發×10)
- [ ] Step 1.5: 類目關鍵詞 (可選)
- [ ] Step 1.6: 1688採購價格 (可選)
- [ ] Step 1.7: TikTok產品搜尋 (可選)

---

## 五維評分計算參考

### 1. HHI指數計算

```
HHI = Σ(各品牌市場份額百分比)²

示例:
品牌A: 12.56% → 12.56² = 157.75
品牌B: 9.11%  → 9.11²  = 82.99
品牌C: 3.55%  → 3.55²  = 12.60
...
HHI = 157.75 + 82.99 + 12.60 + ... = 167.71
```

### 2. CR3集中度計算

```
CR3 = Top3品牌市場份額之和

示例:
品牌A: 12.56%
品牌B: 9.11%
品牌C: 3.55%
CR3 = 12.56 + 9.11 + 3.55 = 25.22%
```

### 3. 同比增長率計算

```
同比增長率 = (本期銷量 - 去年同期銷量) / 去年同期銷量 × 100%

示例:
2026年2月: 1233
2025年2月: 1047
增長率 = (1233 - 1047) / 1047 × 100% = 17.76%
```

---

*最後更新: 2026-03-03*
