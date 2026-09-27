# Product-Research 故障排查指南

## 快速診斷流程

```
問題發生
    ↓
是 API 呼叫錯誤? → 檢視第2節
    ↓
是資料解析錯誤? → 檢視第3節
    ↓
是編碼問題? → 檢視第4節
    ↓
其他問題 → 檢視第5節
```

---

## 1. 資料採集失敗

### 問題: 類目搜尋返回 406 錯誤

**症狀**: `HTTP Error 406: Not Acceptable`

**原因**: API 引數名稱錯誤

**解決方案**:
```python
# ❌ 錯誤寫法
client._call('category_search_from_product_name', {
    'amzSite': 'US',
    'productName': 'bluetooth speaker'  # 錯誤!
})

# ✅ 正確寫法
client.search_category_by_product_name('US', 'bluetooth speaker')
# 或直接呼叫
client._call('category_name_search', {
    'amzSite': 'US',
    'searchName': 'bluetooth speaker'  # 正確!
})
```

### 問題: 找不到類目

**症狀**: 返回空列表或 "未查詢到對應類目"

**診斷步驟**:
1. 檢查關鍵詞拼寫
2. 嘗試更通用的關鍵詞 (如 "speaker" 而非 "portable bluetooth speaker")
3. 檢查站點是否支援該類目

**解決方案**:
```python
# 嘗試多個關鍵詞
keywords = ['bluetooth speaker', 'portable speaker', 'wireless speaker', 'speaker']
for kw in keywords:
    result = client.search_category_by_product_name('US', kw)
    if result:
        break
```

---

## 2. API 呼叫錯誤

### 問題: "An error occurred invoking 'xxx'"

**原因**: 工具名稱不存在

**常用工具名稱對照**:

| 功能 | 正確名稱 | 錯誤名稱 |
|------|----------|----------|
| 類目搜尋 | `category_name_search` | `category_search_from_product_name` ❌ |
| 類目報告 | `category_report` | - |
| 關鍵詞詳情 | `keyword_detail` | - |
| 產品詳情 | `product_detail` | - |

### 問題: 認證失敗

**症狀**: `Authentication required`

**檢查**:
```bash
# 驗證 API Key
curl "https://mcp.sorftime.com?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

**解決方案**:
1. 檢查 `.mcp.json` 檔案
2. 確認 URL 格式: `https://mcp.sorftime.com?key=XXX`
3. 獲取新 API Key: https://sorftime.com/zh-cn/mcp

---

## 3. 資料解析錯誤

### 問題: Top100 資料解析失敗

**症狀**: `KeyError: 'Top100產品'` 或產品列表為空

**原因**: Sorftime 返回格式可能有多種變體

**解決方案**:
```python
def safe_extract_products(data):
    """安全提取產品列表"""
    if not isinstance(data, dict):
        return []

    # 嘗試多個可能的鍵名
    products = (
        data.get('Top100產品') or
        data.get('top100_products') or
        data.get('products') or
        data.get('productList') or
        data.get('product_list') or
        []
    )

    return products
```

### 問題: SSE 響應解析失敗

**症狀**: `API 返回資料解析失敗`

**除錯方法**:
```python
# 儲存原始響應用於除錯
import os
debug_file = os.path.join(output_dir, 'raw_response.txt')
with open(debug_file, 'w', encoding='utf-8') as f:
    f.write(response)

# 檢查響應格式
print("原始響應前500字元:")
print(response[:500])
```

---

## 4. 編碼問題

### 問題: 中文顯示為亂碼

**症狀**: `äº§å` 或類似字元

**解決方案**: 使用 `api_client.py` 中的修複函式

```python
from api_client import fix_mojibake

fixed_text = fix_mojibake(bad_text)
```

### 問題: Unicode 轉義未解碼

**症狀**: `\u4ea7\u54c1` 格式

**解決方案**:
```python
import codecs

decoded = codecs.decode(escaped_text, 'unicode-escape')
```

---

## 5. 其他常見問題

### 問題: 模組匯入失敗

**症狀**: `ModuleNotFoundError: No module named 'xxx'`

**解決方案**:
```python
# 確保指令碼目錄在 Python 路徑中
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from api_client import SorftimeClient
```

### 問題: 檔案儲存失敗

**症狀**: `FileNotFoundError` 或許可權錯誤

**解決方案**:
```python
# 確保目錄存在
os.makedirs(output_dir, exist_ok=True)

# 使用絕對路徑
output_path = os.path.abspath(output_dir)
```

---

## 6. 除錯技巧

### 啟用詳細日誌

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 在程式碼中新增日誌
logger.debug(f"API 請求: {method_name} {arguments}")
logger.info(f"獲取到 {len(products)} 個產品")
```

### 分步測試

```python
# 測試 API 連線
client = SorftimeClient()
result = client._call('category_name_search', {
    'amzSite': 'US',
    'searchName': 'speaker'
})
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 使用 curl 直接測試

```bash
# 測試類目搜尋
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "category_name_search",
      "arguments": {
        "amzSite": "US",
        "searchName": "speaker"
      }
    }
  }'
```

---

## 7. 獲取幫助

1. 檢查 `SKILL.md` 中的執行流程說明
2. 檢視 `api_client.py` 中的方法文件
3. 參考 `category-selection` skill 的類似實現
4. 在專案根目錄執行測試命令驗證環境

---

*最後更新: 2026-03-19*
