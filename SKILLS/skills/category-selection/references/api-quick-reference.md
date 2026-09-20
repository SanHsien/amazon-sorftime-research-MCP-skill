# Sorftime MCP API 快速參考

## 品類選品分析常用介面

### 1. category_name_search - 搜尋類目

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"Sofas"}}}'
```

**返回關鍵資料**: `NodeId` (用於後續呼叫)

---

### 2. category_report - 類目報告 (核心)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_report","arguments":{"amzSite":"US","nodeId":"3733551"}}}'
```

**返回資料**:
- `Top100產品[]`: 產品列表 (ASIN, 標題, 價格, 月銷量, 星級, 品牌, 評論數, 賣家來源等)
- `類目統計報告`: 統計資料

**關鍵統計欄位**:
| 欄位名 | 說明 | 用途 |
|--------|------|------|
| `top100產品月銷量` | Top100 總銷量 | 市場規模 |
| `top100產品月銷額` | Top100 總銷額 | 市場規模 |
| `average_price` | 平均價格 | 定價參考 |
| `top3_brands_sales_volume_share` | Top3 品牌佔比 | 競爭集中度 |
| `amazonOwned_sales_volume_share` | Amazon 自營佔比 | 平臺壓力 |
| `low_reviews_sales_volume_share` | 低評論產品佔比 | 新品機會 |

---

### 3. product_detail - 產品詳情

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"B0DDTCQGTR"}}}'
```

**返回關鍵資料**: 標題, 主圖URL, 價格, 星級, 評論數, 品牌, 上線日期, 月銷量, 產品描述等

---

### 4. category_keywords - 類目關鍵詞

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"category_keywords","arguments":{"amzSite":"US","nodeId":"3733551","page":1}}}'
```

**返回關鍵資料**:
- `關鍵詞`: 關鍵詞
- `周搜尋排名`: 搜尋排名
- `月搜尋量`: 月搜尋量
- `cpc精準競價`: PPC 競價

---

## SSE 響應處理

### 響應格式
```
event: message
data: {"result":{"content":[{"type":"text","text":"..."}}]}
```

### Python 解碼示例
```python
import codecs

# 解碼 Unicode 轉義
decoded = codecs.decode(encoded_text, 'unicode-escape')
```

---

## 支援的站點

| 程式碼 | 站點 |
|------|------|
| US | 美國 |
| GB | 英國 |
| DE | 德國 |
| FR | 法國 |
| CA | 加拿大 |
| JP | 日本 |
| ES | 西班牙 |
| IT | 義大利 |
