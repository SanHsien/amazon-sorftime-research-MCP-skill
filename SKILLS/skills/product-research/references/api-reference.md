# Sorftime API 快速參考 (Product-Research)

## API 端點

```
https://mcp.sorftime.com?key={API_KEY}
```

## 請求格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "{工具名稱}",
    "arguments": {
      "amzSite": "US",
      ...
    }
  }
}
```

## 響應格式 (SSE)

```
event: message
data: {"result":{"content":[{\"type\":\"text\",\"text\":\"{資料}\"}],\"isError\":false},"id":1,\"jsonrpc\":\"2.0\"}

```

---

## 常用 API 工具

### 1. category_name_search

**用途**: 按名稱搜尋類目，獲取 NodeId

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | ✓ | 站點程式碼 (US, GB, DE, etc.) |
| searchName | string | ✓ | 類目名稱關鍵詞 |

**示例**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key={KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "category_name_search",
      "arguments": {
        "amzSite": "US",
        "searchName": "bluetooth speaker"
      }
    }
  }'
```

**響應**:
```json
[
  {
    "nodeId": "7073956011",
    "Name": "Portable Bluetooth Speakers"
  },
  {
    "nodeId": "12097477011",
    "Name": "Outdoor Speakers"
  }
]
```

---

### 2. category_report

**用途**: 獲取類目 Top100 產品和統計資料

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | ✓ | 站點程式碼 |
| nodeId | string | ✓ | 類目 Node ID |

**示例**:
```python
client.get_category_report("US", "7073956011")
```

**響應結構**:
```json
{
  "Top100產品": [
    {
      "ASIN": "B0XXXXXXXX",
      "標題": "...",
      "月銷量": "10000",
      "月銷額": "500000.00",
      "品牌": "JBL",
      "價格": 49.99,
      "評論數": 5000,
      "星級": 4.7
    }
  ],
  "類目統計報告": {
    "nodeid": "7073956011",
    "類目名稱": "Portable Bluetooth Speakers",
    "top100產品月銷量": "279733",
    "top100產品月銷額": "19842968.40",
    "top3_product_sales_volume_share": "19.66%"
  }
}
```

---

### 3. category_trend

**用途**: 獲取類目趨勢資料

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | ✓ | 站點程式碼 |
| nodeId | string | ✓ | 類目 Node ID |
| trendIndex | string | ✗ | 趨勢型別 (預設: NewProductSalesAmountShare) |

**trendIndex 選項**:
- `NewProductSalesAmountShare` - 新品銷量佔比
- `NewProductProductShare` - 新品數量佔比
- `BrandConcentration` - 品牌集中度
- `PriceDistribution` - 價格分佈

**示例**:
```python
trend = client.get_category_trend("US", "7073956011", "NewProductSalesAmountShare")
```

**響應**:
```json
[
  "2024年03月=3.32",
  "2024年04月=1.98",
  ...
]
```

---

### 4. keyword_detail

**用途**: 獲取關鍵詞詳情

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | ✓ | 站點程式碼 |
| keyword | string | ✓ | 關鍵詞 |

**示例**:
```python
detail = client.get_keyword_detail("US", "bluetooth speaker")
```

**響應結構**:
```json
{
  "搜尋量": "50000",
  "CPC": "1.50",
  "競價": "8",
  "自然位產品": [...]
}
```

---

### 5. product_detail

**用途**: 獲取單個產品詳情

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | ✓ | 站點程式碼 |
| asin | string | ✓ | 產品 ASIN |

---

### 6. product_reviews

**用途**: 獲取產品評論

**引數**:
| 引數 | 型別 | 必填 | 說明 |
|------|------|------|------|
| amzSite | string | ✓ | 站點程式碼 |
| asin | string | ✓ | 產品 ASIN |
| reviewType | string | ✗ | 評論型別 (Both/Positive/Negative) |

---

## Python 客戶端使用

### 基本用法

```python
from api_client import SorftimeClient

client = SorftimeClient()

# 搜尋類目
categories = client.search_category_by_product_name("US", "bluetooth speaker")
node_id = categories[0]['nodeId']

# 獲取 Top100
top100 = client.get_category_report("US", node_id)
products = top100.get('Top100產品', [])

# 獲取趨勢
trend = client.get_category_trend("US", node_id)

# 獲取關鍵詞詳情
keyword_data = client.get_keyword_detail("US", "bluetooth speaker")
```

### 批次呼叫

```python
# 併發獲取多個產品詳情
asins = ["B0XXX1", "B0XXX2", "B0XXX3"]
details = []
for asin in asins:
    try:
        detail = client.get_product_detail("US", asin)
        details.append(detail)
    except Exception as e:
        print(f"Failed for {asin}: {e}")
```

---

## 支援的站點

| 程式碼 | 市場 |
|------|------|
| US | 美國亞馬遜 |
| GB | 英國亞馬遜 |
| DE | 德國亞馬遜 |
| FR | 法國亞馬遜 |
| IT | 義大利亞馬遜 |
| ES | 西班牙亞馬遜 |
| CA | 加拿大亞馬遜 |
| JP | 日本亞馬遜 |
| MX | 墨西哥亞馬遜 |
| AE | 阿聯酋亞馬遜 |
| AU | 澳大利亞亞馬遜 |
| BR | 巴西亞馬遜 |
| SA | 沙烏地阿拉伯亞馬遜 |

---

## 資料型別說明

### 月銷量/月銷額

- 型別: `string` (需要轉換為數字)
- 示例: `"28908"`, `"1443954.60"`
- 轉換: `float(value)`

### 價格

- 型別: `float` 或 `string`
- 示例: `49.95`, `"29.99"`

### 評論數

- 型別: `int` 或 `string`
- 示例: `14558`, `"5000"`

---

## 錯誤程式碼

| HTTP 狀態 | 含義 | 解決方案 |
|-----------|------|----------|
| 200 | 成功 | - |
| 406 | 引數錯誤 | 檢查引數名稱和格式 |
| 401 | 認證失敗 | 檢查 API Key |
| 500 | 伺服器錯誤 | 稍後重試 |

---

*最後更新: 2026-03-19*
