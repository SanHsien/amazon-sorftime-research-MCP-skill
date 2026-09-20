---
name: "review-analysis"
description: "對亞馬遜商品評論進行深度分析，自動識別產品痛點、分析退貨原因，生成改進建議和客服回覆模板。Invoke when user uses /review-analysis command with a product ASIN."
---

# 亞馬遜商品評論深度分析

## 快速參考

| 步驟 | 操作 | 說明 |
|------|------|------|
| 1. 獲取API金鑰 | 讀取 `.mcp.json` | 獲取 Sorftime API 金鑰 |
| 2. 建立報告目錄 | mkdir + data子目錄 | 建立 `review-analysis-reports/{ASIN}_{站點}_{日期}/data/` |
| 3. 獲取產品資料 | `product_detail` API | 驗證ASIN並獲取產品資訊，儲存原始SSE資料 |
| 4. 獲取評論資料 | `product_reviews` API | 獲取全部評論資料，儲存原始SSE資料 |
| 5. 解析並分類差評 | 記憶體處理 | 提取1-3星評論，按痛點分類 |
| 6. 儲存分析資料 | JSON輸出 | 儲存差評分析資料到 `data/negative_reviews_analysis.json` |
| 7. 生成分析報告 | Markdown輸出 | 儲存最終報告到 `report.md` |

## 報告輸出結構

```
review-analysis-reports/
└── {ASIN}_{站點}_{YYYYMMDD}/
    ├── report.md                              # 完整分析報告（Markdown）
    └── data/                                  # 原始資料和分析結果
        ├── raw_product_sse.txt                # 原始產品詳情SSE響應
        ├── raw_reviews_sse.txt                # 原始評論SSE響應
        └── negative_reviews_analysis.json     # 差評分析結構化資料
```

## 觸發條件

當使用者使用 `/review-analysis` 命令並提供一個亞馬遜產品 ASIN 時，啟動此分析流程。

**呼叫格式**:
```
/review-analysis {ASIN} {站點}
```

**示例**: `/review-analysis B0D9ZTW7PS US`

## 角色設定

你是一位擁有10年經驗的**亞馬遜高階產品開發顧問**和**客戶體驗專家**，專精於透過使用者評論挖掘產品痛點和改進機會。

你的核心任務是基於提供的**差評文字**，深度剖析產品的核心痛點，並給出**能直接落地**的解決方案。

參考文件中的分析框架，但根據實際評論內容靈活調整。

## 分析流程（最佳化版 v7.0 - 6維分析框架）

### 第一步：讀取 API 金鑰

```python
# 使用 Read 工具讀取配置檔案
Read("D:/amazon-mcp/.mcp.json")

# 從 JSON 中提取 API 金鑰
# 格式: "url": "https://mcp.sorftime.com?key={API_KEY}"
```

### 第二步：建立報告目錄結構

```bash
# 建立報告目錄和資料子目錄
REPORT_DIR="D:/amazon-mcp/reports/review-analysis/{ASIN}_{站點}_20260315"
mkdir -p "$REPORT_DIR/data"
```

### 第三步：獲取產品資料並儲存原始響應

使用 PowerShell 或命令列呼叫 Sorftime API，並儲存原始響應：

```bash
# 獲取產品詳情並儲存原始SSE響應
API_KEY="從.mcp.json中獲取的金鑰"
curl -s -X POST "https://mcp.sorftime.com?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN"}}}' \
  > "$REPORT_DIR/data/raw_product_sse.txt"
```

**如果返回 "Authentication required" 或 "授權失敗"**：
- 告知使用者 API 金鑰無效或已過期
- 指引使用者訪問 https://sorftime.com/zh-cn/mcp 獲取新金鑰
- 更新 `.mcp.json` 檔案

**如果返回 "未查詢到對應產品"**：
- 驗證 ASIN 格式（應為10位字母數字）
- 嘗試使用其他站點
- 提示使用者確認產品是否在該站點銷售

### 第四步：獲取評論資料並儲存原始響應

**使用 `reviewType: "Negative"` 引數專門獲取差評**：

```bash
# 獲取差評（1-3星），儲存原始SSE響應
curl -s -X POST "https://mcp.sorftime.com?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"product_reviews","arguments":{"amzSite":"US","asin":"ASIN","reviewType":"Negative"}}}' \
  > "$REPORT_DIR/data/raw_reviews_sse.txt"
```

**重要提示**：
- Sorftime 返回的是 SSE (Server-Sent Events) 格式
- 資料格式: `event: message\ndata: {JSON}\n\n`
- 如果資料超過 25KB，會自動儲存到臨時檔案
- 使用 Read 工具讀取臨時檔案獲取完整資料
- `reviewType: "Negative"` 只返回1-3星評論，最多100條
- `reviewType: "Both"` 返回所有評論，但差評可能被稀釋

**處理大檔案響應**：
```bash
# 如果響應被儲存到臨時檔案，複製到報告目錄
cp /path/to/temp/file.txt "$REPORT_DIR/data/raw_reviews_sse.txt"
```

### 第五步：解析評論資料並生成分析JSON

**在記憶體中處理評論資料，同時生成結構化分析資料**：

```python
import json

# SSE 資料解析步驟：
# 1. 從響應中提取 "data: " 後的 JSON
# 2. 解析 JSON 獲取 result.content[0].text
# 3. text 中包含 Unicode 轉義的中文和評論陣列
# 4. 從評論陣列中過濾 1-3 星評論

# 解析示例：
start_idx = content.find('data: ') + 6
json_str = content[start_idx:]
data = json.loads(json_str)

# 提取評論文字
text = data['result']['content'][0]['text']

# 查詢評論陣列起始位置
reviews_start = text.find('[{')
reviews_json = text[reviews_start:]
reviews = json.loads(reviews_json)

# 過濾 1-3 星評論
negative_reviews = [r for r in reviews if float(r.get('評星', 5)) <= 3.0]

# 按6大類別歸類差評（v7.0 增加服務維度）
pain_points = {
    "電子模組故障": [],
    "結構/組裝問題": [],
    "設計/功能缺陷": [],
    "外觀/材質問題": [],
    "描述不符": [],
    "服務/物流問題": []
}
```

**服務維度分類關鍵詞**：
```python
# 服務/物流問題 - 優先檢查
service_keywords = {
    '收到二手/瑕疵品': ['used', 'gross', 'dirty', 'scratch', 'ear wax', 'dirt', 'opened', 'previous owner'],
    '配件缺失': ['missing', 'no cord', 'no cable', 'no charger', 'no ear tip', 'no accessory'],
    '退換貨困難': ['return', 'refund', 'exchange', 'difficult', 'challenging'],
    '客服問題': ['customer service', 'seller', 'vendor', 'support'],
    '物流問題': ['shipping', 'delivery', 'package', 'packaging'],
    '發錯貨': ['wrong item', 'wrong color', 'wrong size', 'sent wrong']
}
```

**儲存分析資料到JSON**：

```bash
# 使用 Write 工具生成分析資料檔案
# 檔案路徑: $REPORT_DIR/data/negative_reviews_analysis.json
```

JSON檔案結構應包含：
- 產品基礎資訊（標題、品牌、價格、評分）
- 痛點分類統計（類別、數量、佔比、嚴重程度）
- 每個痛點的詳細分析（根源、改進建議、客戶引用）
- 安全警示（如有）
- 質量指標估算

### 第六步：生成分析報告

```python
import json

# SSE 資料解析步驟：
# 1. 從響應中提取 "data: " 後的 JSON
# 2. 解析 JSON 獲取 result.content[0].text
# 3. text 中包含 Unicode 轉義的中文和評論陣列
# 4. 從評論陣列中過濾 1-3 星評論

# 解析示例：
start_idx = content.find('data: ') + 6
json_str = content[start_idx:]
data = json.loads(json_str)

# 提取評論文字
text = data['result']['content'][0]['text']

# 查詢評論陣列起始位置
reviews_start = text.find('[{')
reviews_json = text[reviews_start:]
reviews = json.loads(reviews_json)

# 過濾 1-3 星評論
negative_reviews = [r for r in reviews if float(r.get('評星', 5)) <= 3.0]
```

### 第七步：生成最終分析報告

**使用 Write 工具生成完整的 Markdown 報告**：

```
報告路徑: $REPORT_DIR/report.md
```

## 分析框架

### 痛點歸類（6大類別）

| 類別 | 判斷標準 |
|------|----------|
| **1. 結構/組裝問題** | 零件破損、密封失效、介面斷裂、安裝孔位偏差、組裝困難、結構不穩 |
| **2. 電子模組故障** | USB/充電失效、LED不亮、APP連線失敗、藍芽斷連、功能失效、電路問題 |
| **3. 設計/功能缺陷** | 尺寸不合理、功能缺失、操作複雜、觸感不符、人體工程學問題、使用不便 |
| **4. 外觀/材質問題** | 有異味、材質過敏、色差、劃痕、生鏽、表面處理差、材質廉價感 |
| **5. 描述不符** | 尺寸預期偏差、功能與描述不符、顏色差異、款式與圖片不一致、藍芽版本不符 |
| **6. 服務/物流問題** | 客服響應慢、退換貨困難、物流延遲、發錯貨、配件缺失、**收到二手產品/瑕疵品**、包裝破損 |

### 服務維度細分

服務維度問題需進一步細分統計：

| 細分類別 | 判斷標準 | 嚴重程度 |
|----------|----------|----------|
| **收到二手/瑕疵品** | 評論提及 used、dirty、ear wax、scratch、opened、previous owner | **高** |
| **配件缺失** | 缺少充電線、耳塞、說明書、保修卡等 | **高** |
| **退換貨困難** | 退貨流程複雜、退款慢、賣家推諉、買家承擔高額運費 | 中 |
| **客服響應慢/態度差** | 客服不回覆、回覆慢、態度惡劣、無法解決問題 | 中 |
| **物流延遲/包裝差** | 發貨慢、物流停滯、包裝破損、快遞服務差 | 低 |
| **發錯貨** | 顏色/尺寸/款式發錯 | 中 |

### 嚴重程度評估

| 程度 | 判斷標準 |
|------|----------|
| **高** | 影響核心功能或存在安全隱患（如破損、洩漏、過敏、漏電） |
| **中** | 影響使用體驗（如操作複雜、觸感不佳、尺寸偏差） |
| **低** | 外觀細節問題（如輕微劃痕、包裝瑕疵、個人偏好） |

### 解決方案雙軌制

對於每個痛點，提供：

1. **產品/供應鏈改進方案**
   - 必須具體可執行（如：將封口寬度從3mm增加到6mm）
   - 避免籠統描述（如："提高質量"是不可接受的）

2. **客服話術/Listing最佳化建議**
   - 客服郵件模板（遵守亞馬遜合規要求）
   - Listing 文案/圖片改進建議

## 報告模板

```markdown
# {產品標題} - 評論深度分析報告

> ASIN: {ASIN} | 站點: {站點} | 分析時間: {時間}

---

## 產品基礎資訊

| 專案 | 內容 |
|------|------|
| 產品標題 | {標題} |
| 品牌 | {品牌} |
| 價格 | ${價格} |
| 評分 | {評分}/5.0 |
| 評論總數 | {總數} |
| 分析樣本 | {差評數量} 條 (1-3星) |

---

## 痛點分析彙總

基於 {差評數量} 條差評的深度分析：

### 痛點分佈概覽

| 排名 | 痛點類別 | 數量 | 佔比 | 嚴重程度 |
|------|----------|------|------|----------|
| 1 | {類別} | {數量} | {佔比}% | {高/中/低} |
| 2 | {類別} | {數量} | {佔比}% | {高/中/低} |
| ... | ... | ... | ... | ... |

---

## 核心痛點深度分析

### 痛點 #1: {痛點名稱}

**類別**: {類別} | **嚴重程度**: {程度} | **影響**: {數量}條評論 ({佔比}%)

#### 客戶反饋摘要
> "{典型差評引用1}"
>
> "{典型差評引用2}"

#### 根源分析
- **設計問題**: {分析}
- **生產問題**: {分析}
- **包裝問題**: {分析} (如適用)

#### 產品改進建議
1. {具體可執行的改進1}
2. {具體可執行的改進2}

#### 客服回覆模板

**Subject**: {郵件主題}

**Dear [Customer Name],**

{完整的郵件內容}

**Best regards,**

[Your Name]
[Brand Name] Customer Success Team

---

[重複其他痛點...]

---

## 給您的產品開發專家建議

### 產品質量改進
- {建議1}
- {建議2}

### 供應鏈端的"防呆"設計
- {建議1}
- {建議2}

### Listing與營銷層面的"預期管理"
- {建議1}
- {建議2}

### 服務與運營最佳化（如存在服務維度問題）
- **客服培訓**: 建立標準話術庫，確保24小時內響應差評
- **退換貨流程**: 簡化退貨流程，提供預付運費標籤
- **發貨質檢**: 100%出庫質檢，杜絕二手/瑕疵品流出
- **配件管理**: 建立配件清單核對機制，確保包裝完整
- **物流合作**: 評估物流服務商，選擇可靠的配送渠道

---

## 亞馬遜差評回覆郵件模板庫

### 模板型別（根據痛點類別提供）

1. **產品質量問題**（電子模組故障、結構問題、設計缺陷）
2. **服務問題**（收到二手/瑕疵品、配件缺失、退換貨困難）
3. **物流問題**（延遲、包裝破損、發錯貨）
4. **描述不符**（功能預期偏差、尺寸顏色差異）

[根據具體產品型別和痛點提供3-5個針對性模板]

### 服務問題專項模板示例

**收到二手/瑕疵品**:
```
Subject: 我們深表歉意 - 立即為您更換全新產品
Dear [Customer Name],
我們非常抱歉您收到了有瑕疵的產品。這絕不符合我們的質量標準。
請立即聯絡 [support email]，我們將為您免費更換全新產品，無需退回原產品。
再次致歉！
[Brand] Customer Service
```

---

## 操作建議（避坑指南）

1. **話術避諱**: 嚴禁使用 "Change your review" 或 "Remove your review"
2. **回覆渠道**: 使用亞馬遜後臺 "Contact Buyer" 功能
3. **時效性**: 1星評價4小時內響應，2星12小時內，3星24小時內
4. **跟進策略**: 首封郵件聚焦解決問題，不主動提補償

---

*報告生成時間: {時間戳}*
*資料來源: Sorftime MCP*
*分析方法: LLM 整體評論分析*
```

## 亞馬遜合規要求

生成郵件模板時必須遵守：
1. 嚴禁直接請求刪除/修改評價
2. 不得用利益交換評價
3. 使用官方渠道 Contact Buyer
4. 24小時內響應差評

## 支援的站點

US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

## 故障排查

### API 授權失敗
**症狀**: 返回 "Authentication required" 或 "授權失敗"

**解決方案**:
1. 訪問 https://sorftime.com/zh-cn/mcp 獲取新金鑰
2. 更新 `.mcp.json` 中的 API 金鑰
3. 重新執行分析

### 產品未找到
**症狀**: 返回 "未查詢到對應產品"

**解決方案**:
1. 檢查 ASIN 格式（10位字母數字）
2. 確認站點是否正確
3. 嘗試使用其他站點

### 中文亂碼
**症狀**: 返回的資料包含 `\u4ea7\u54c1` 等 Unicode 轉義

**解決方案**:
- Python: `json.loads()` 會自動解碼
- 如有 Mojibake: `text.encode('latin-1').decode('utf-8')`

### 資料過大被截斷
**症狀**: 返回 "Output too large... saved to: {temp_file}"

**解決方案**:
1. 從提示的臨時檔案路徑讀取完整資料
2. 使用 Read 工具的 offset/limit 引數分塊讀取
3. 或使用 Grep 工具提取特定模式

### 服務問題識別
**症狀**: 評論中頻繁出現服務相關差評

**服務維度警告閾值**:
| 問題型別 | 警告閾值 | 危險閾值 |
|----------|----------|----------|
| 收到二手/瑕疵品 | >2% | >5% |
| 配件缺失 | >1% | >3% |
| 退換貨困難投訴 | >5% | >10% |
| 客服負面評價 | >3% | >7% |

**改進建議**:
- **二手/瑕疵品問題**: 立即審查倉庫質檢流程，考慮產品召回
- **配件缺失**: 檢查包裝流水線，增加配件掃碼核對
- **退換貨困難**: 簡化退貨流程，提供預付運費標籤
- **客服問題**: 增加客服培訓，建立24小時響應機制

### 差評數量很少
**症狀**: 產品顯示有幾百條評論，但只返回幾條差評

**可能原因**:
1. **產品質量好**: 差評率低是好事，說明客戶滿意度高
2. **API限制**: Sorftime API 最多返回100條評論
3. **使用 `reviewType: "Negative"`**: 只獲取1-3星評論，數量自然會少

**資料分析建議**:
- 如果差評少於5條：分析結果僅供參考，建議結合其他資料來源
- 如果差評少於10條：在報告中明確說明樣本量限制
- 如果差評超過20條：分析結果具有較高的統計意義

**補充資料方案**:
1. 手動檢視亞馬遜產品頁面的差評
2. 使用其他評論抓取工具獲取更多資料
3. 結合客服記錄瞭解常見問題

## 最佳實踐

1. **路徑處理**: 在 Windows 環境下使用正斜槓 `/` 或反斜槓 `\` 均可，但保持一致
2. **資料儲存**: 所有中間資料必須儲存到 `data/` 子目錄，確保可追溯和複用
3. **JSON結構**: 分析資料應採用結構化JSON格式，便於後續程式化處理
4. **錯誤處理**: 每個步驟後檢查返回結果，及時發現問題
5. **使用者反饋**: 遇到問題時清晰告知使用者原因和解決方案

### 中間資料檔案說明

| 檔名 | 用途 | 格式 |
|--------|------|------|
| `raw_product_sse.txt` | 產品詳情原始API響應 | SSE格式 |
| `raw_reviews_sse.txt` | 評論資料原始API響應 | SSE格式 |
| `negative_reviews_analysis.json` | 差評分析結構化資料 | JSON |

### 資料複用場景

- **趨勢分析**: 對比同一產品不同時間段的差評變化
- **競品對比**: 批次分析多個產品的差評資料
- **質量追溯**: 基於原始資料驗證分析結論的準確性
- **報表生成**: 基於JSON資料自動生成Excel/圖表

---

*本技能文件版本: v7.0 (6維分析框架) | 最後更新: 2026-03-15*
