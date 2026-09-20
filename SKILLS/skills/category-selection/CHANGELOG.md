# Category-Selection Skill 變更日誌

## [11.0.0] - 2026-03-05

### v4.0 更新 - 重大 Bug 修復和穩定性改進

**背景**: 在實際使用中發現多個問題，包括 API Key 配置、JSON 解析失敗、類目搜尋失敗等。本次更新系統性地修復了所有已知問題。

### 主要改進

#### 1. 自動 API Key 配置 ✅
**問題**: 需要手動設定環境變數 `SORFTIME_API_KEY`，使用者體驗不友好

**修復**:
- 新增 `get_api_key()` 函式，自動從 `.mcp.json` 讀取 API Key
- 支援多源配置：環境變數 > .mcp.json 配置檔案
- 新增 API Key 有效性檢查和友好錯誤提示

```python
# 程式碼示例
def get_api_key():
    # 1. 嘗試環境變數
    api_key = os.environ.get('SORFTIME_API_KEY', '')
    if api_key:
        return api_key

    # 2. 嘗試從 .mcp.json 讀取
    mcp_config_path = os.path.join(PROJECT_ROOT, '.mcp.json')
    if os.path.exists(mcp_config_path):
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
            sorftime_url = config.get('mcpServers', {}).get('sorftime', {}).get('url', '')
            if 'key=' in sorftime_url:
                return sorftime_url.split('key=')[-1]
    return ''
```

**影響**: 使用者無需配置環境變數，開箱即用

---

#### 2. JSON 字串值中未轉義控制字元修復 ✅
**問題**: `JSONDecodeError: Invalid control character at: line 1 column 3401`

**根本原因**: API 返回的 JSON 字串值中包含原始的換行符（`\n`）、製表符（`\t`）等控制字元，這些字元沒有被正確轉義為 `\n`、`\t` 序列

**示例**:
```json
// API 返回的原始格式（錯誤）
{"標題": "類目：Renewed Laptops，排名:2
類目：Traditional Laptops，排名:11"}

// 正確格式
{"標題": "類目：Renewed Laptops，排名:2\\n類目：Traditional Laptops，排名:11"}
```

**修復**: 新增 `escape_control_chars_in_json_strings()` 函式
```python
def escape_control_chars_in_json_strings(json_str):
    """
    轉義 JSON 字串值中的控制字元
    只處理字串值內部，不影響 JSON 結構
    """
    result = []
    in_string = False
    escape_next = False

    for c in json_str:
        if escape_next:
            result.append(c)
            escape_next = False
        elif c == '\\':
            result.append(c)
            escape_next = True
        elif c == '"':
            in_string = not in_string
            result.append(c)
        elif in_string and c == '\n':
            result.append('\\n')  # 轉義換行符
        elif in_string and c == '\r':
            result.append('\\r')  # 轉義回車符
        elif in_string and c == '\t':
            result.append('\\t')  # 轉義製表符
        else:
            result.append(c)

    return ''.join(result)
```

**影響**: 所有包含換行符的 JSON 響應現在可以正確解析

---

#### 3. 改進類目搜尋策略 ✅
**問題**: 類目搜尋失敗，特別是 "Laptops" 和 "Computers" 等大類目

**修復**:
- 自動嘗試多種搜尋變體
- 支援模糊匹配和關鍵詞變體
- 當返回多個類目時，自動使用第一個類目
- 新增搜尋失敗時的友好提示

```python
# 自動嘗試的搜尋變體
search_variants = [
    self.category,                    # 原始輸入
    self.category.replace(' & ', ' '), # 移除 & 符號
    self.category.split(' ')[0],       # 第一個詞
    self.category.rstrip('s'),        # 移除複數
]
```

**影響**: 類目搜尋成功率顯著提高

---

#### 4. 執行日誌和除錯支援 ✅
**問題**: 難以追蹤執行過程和定位問題

**新增**:
- 執行日誌自動儲存到 `execution.log`
- 詳細的錯誤資訊和上下文
- 時間戳記錄每個操作
- DEBUG、INFO、WARN、ERROR 級別

```python
def log(self, message: str, level: str = 'INFO'):
    """記錄日誌"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    log_entry = f"[{timestamp}] [{level}] {message}"
    self.execution_log.append(log_entry)
```

**影響**: 問題診斷更容易

---

#### 5. 錯誤處理增強 ✅
**問題**: 錯誤資訊不明確，難以定位問題

**改進**:
- API Key 未檢查時提供明確的配置指引
- JSON 解析失敗時儲存除錯資訊到 `parse_debug.txt`
- 認證失敗時提供明確的錯誤提示
- 所有 API 呼叫都有超時處理

**影響**: 使用者體驗更好，問題更容易解決

---

### 故障排查指南更新

在 `SKILL.md` 中新增詳細的故障排查章節，包括：

1. **API Key 未設定** - 解釋兩種配置方式和自動載入邏輯
2. **JSON 解析失敗 - 控制字元** - 詳細說明根本原因和修復方法
3. **類目未找到** - 提供多種解決方案
4. **Mojibake 編碼問題** - 手動修復方法
5. **Python dict 格式問題** - 修復說明
6. **大類目搜尋失敗** - 工作流程建議

---

### 檔案更新

| 檔案 | 版本 | 更新內容 |
|------|------|----------|
| `workflow.py` | v4.0 | ✅ 自動 API Key 載入<br>✅ 控制字元轉義修復<br>✅ 改進類目搜尋<br>✅ 執行日誌<br>✅ 錯誤處理增強 |
| `SKILL.md` | v4.0 | ✅ 更新 API Key 配置說明<br>✅ 新增控制字元問題排查<br>✅ 更新故障排查指南<br>✅ 版本號更新到 v4.0 |

---

### 相容性

- 完全向後相容 v3.x
- 無需修改現有配置
- `.mcp.json` 配置自動識別

---

### 測試驗證

已使用以下類目進行測試驗證：
- ✅ Traditional Laptop Computers (NodeID: 13896615011)
  - 月銷額: $86,231,118.58
  - 產品數量: 100
  - 五維評分: 74/100 (良好)

---

## [10.0.0] - 2026-03-04

### 標準化版本 - 統一評分標準與資料結構

**背景**: 解決多個指令碼中五維評分標準不一致的問題，統一資料結構和報告生成流程。

### 主要改進

#### 1. 統一五維評分標準
- **問題**: workflow.py、data_utils.py、parse_category_report.py 中的評分邏輯不一致
- **修復**: 統一所有指令碼的評分標準為:
  - 市場規模 (20分): >$10M=20, >$5M=17, >$1M=14, 其他=10
  - 增長潛力 (25分): 低評論佔比>40%=22, >20%=18, 其他=14
  - 競爭烈度 (20分): Top3<30%=18, <50%=14, 其他=8
  - 進入壁壘 (20分): Amazon佔比+新品機會組合 (0-20分)
  - 利潤空間 (15分): 均價>$300=12, >$150=10, >$50=7, 其他=4
- **影響**: 所有報告現在使用一致的評分標準

#### 2. 最佳化進入壁壘評分邏輯
- **舊邏輯**: 基於平均評論數和Amazon佔比的組合判斷
- **新邏輯**: Amazon佔比評分 (0-10分) + 新品機會評分 (0-10分)
  - Amazon佔比: <20%=10分, <40%=6分, 其他=3分
  - 新品機會: 低評論產品>40%=10分, >20%=6分, 其他=3分
- **影響**: 評分更加透明，易於理解和調整

#### 3. 統一利潤空間評分標準
- **舊標準**: 基於 $25/$15/$8 的價格閾值
- **新標準**: 基於 $300/$150/$50 的價格閾值
- **影響**: 更符合亞馬遜實際品類價格分佈

#### 4. SKILL.md 文件重構
- 新增詳細的五維評分標準說明
- 完善資料處理流程文件
- 更新故障排查指南
- 新增資料欄位對映表
- 最佳化報告輸出結構說明

### 檔案更新
- `SKILL.md` - 完全重寫，新增標準化說明
- `workflow.py` - 更新評分函式，統一標準
- `data_utils.py` - 確認評分標準一致性

---

## [4.1.0] - 2026-03-03

### Bug 修復 - 一體化分析指令碼

**背景**: 最佳化分析流程，解決資料處理、編碼和報告生成的多個問題。

### 修復內容

#### 1. SSE 響應解析修復
- **問題**: `codecs.decode(text, 'unicode-escape')` 錯誤地二次解碼已由 JSON 解碼的中文字元
- **修復**: 移除不必要的 unicode-escape 解碼，JSON 解析器已正確處理 Unicode 轉義
- **影響**: 中文鍵名 (`Top100產品`, `類目統計報告`) 現在可以正確提取

#### 2. JSON 物件提取邏輯修復
- **問題**: 解析器查詢最後一個 JSON 物件，但產品資料在第一個物件中
- **修復**: 改為查詢第一個完整的 JSON 物件
- **影響**: 產品列表 (100個產品) 現在可以正確提取

#### 3. 數值格式化修復
- **問題**: 模板變數替換時對字串值使用數字格式 (`,`) 導致錯誤
- **修復**: 新增 `_safe_float()` 和 `_safe_int()` 方法安全轉換數值
- **影響**: 價格、銷量等數值現在可以正確格式化顯示

#### 4. Excel Font 作用域問題修復
- **問題**: `OpenpyxlFont` 在 `generate_excel()` 方法內匯入，但輔助方法無法訪問
- **修復**: 將 Font/PatternFill 類作為引數傳遞給輔助方法
- **影響**: Excel 報告現在可以正常生成

### 新增功能

#### 一體化分析指令碼 (`analyze_category.py`)

一個命令完成完整的品類分析流程：

```bash
python .claude/skills/category-selection/scripts/analyze_category.py "品類名稱" [站點] [數量]
```

**功能特點**:
- 自動搜尋類目獲取 nodeId
- 呼叫 category_report API
- 解析 SSE 響應和中文編碼
- 計算五維評分
- 生成所有格式報告 (Markdown, Excel, HTML, CSV, JSON)

**報告輸出結構**:
```
category-reports/
└── YYYY/MM/
    └── {品類名}_{站點}/
        ├── category_analysis_report.md
        ├── category_analysis_report.xlsx
        ├── dashboard.html
        └── data/
            ├── statistics.csv
            ├── products.csv
            ├── scores.csv
            └── raw_data.json
```

### 技術細節

#### SSE 解析流程
```python
# 舊程式碼 (錯誤):
decoded = codecs.decode(text, 'unicode-escape')  # 二次解碼導致亂碼

# 新程式碼 (正確):
decoded = text  # JSON 已自動解碼 Unicode 轉義
```

#### JSON 物件提取
```python
# 舊程式碼:
last_obj_start = decoded.rfind('{')  # 查詢最後一個物件

# 新程式碼:
first_obj_start = decoded.find('{')  # 查詢第一個物件 (包含產品資料)
```

### 支援的亞馬遜站點
US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

### 已知限制
- 部分統計資料包含中文描述字首 (如 "銷量前的80%產品平均價格：")
- 模板中的部分變數 (如 `{{SCORE_建議}}`, `{{ANALYSIS_*}}`) 尚未實現

---

## [4.0.0] - 2026-03-03

### 重大重構 - MCP 風格化

**背景**: 原版本使用 Python 指令碼繞過 MCP 伺服器直接呼叫 API，與 MCP 設計理念不符。

### 變更內容

#### 刪除的檔案
- `scripts/sorftime_client.py` - 獨立的 HTTP 客戶端（繞過 MCP）
- `scripts/sorftime_parser.py` - SSE 響應解析器（MCP 已處理）
- `scripts/analyze.py` - 主分析指令碼（由 SKILL.md 替代）
- `scripts/category_analysis_template.py` - 模板指令碼
- `scripts/__pycache__/` - Python 快取目錄

#### 重寫的檔案
- `SKILL.md` - 完全重寫為 MCP 風格，與 `amazon-analyse` 保持一致

### 架構變化

**舊架構** (v3.x):
```
Claude Code
    ↓
執行 Python 指令碼 (analyze.py)
    ↓
SorftimeMCPClient (直接 HTTP 請求)
    ↓
Sorftime API (繞過 MCP)
    ↓
自定義解析器
```

**新架構** (v4.0):
```
Claude Code
    ↓
MCP 工具呼叫 (PowerShell / curl)
    ↓
Sorftime MCP 伺服器
    ↓
SSE 響應
    ↓
Claude Code 解析
```

### 功能保持

以下功能保持不變，繼續提供：

#### 必需工具
1. `category_name_search` - 搜尋類目獲取 nodeId
2. `category_report` - 獲取類目 Top100 產品和統計資料
3. `product_detail` - 獲取產品詳情

#### 可選工具
4. `category_keywords` - 獲取類目核心關鍵詞
5. `products_1688` - 1688 採購成本分析

#### 保留的輔助工具
- `scripts/data_utils.py` - 資料處理工具（HHI、分組、評分計算等）
- `scripts/generate_excel_report.py` - Excel 報告生成（可選）

### SKILL.md 主要變化

| 章節 | v3.x | v4.0 |
|------|------|------|
| MCP 呼叫 | 描述 Python 指令碼 | 描述 curl 呼叫 MCP |
| 資料解析 | 匯入 Python 模組 | Claude Code 直接處理 |
| 工具參考 | 混合描述 | 統一 curl 格式 |
| 報告生成 | Python 指令碼 | Write 工具 |

### 五維評分計算

評分邏輯保持不變：

| 維度 | 分值 | 資料來源 |
|------|------|----------|
| 市場規模 | 20分 | top100產品月銷額 |
| 增長潛力 | 25分 | low_reviews_sales_volume_share |
| 競爭烈度 | 20分 | top3_brands_sales_volume_share |
| 進入壁壘 | 20分 | amazonOwned + low_reviews |
| 利潤空間 | 15分 | average_price |

### 相容性

- 與 `amazon-analyse` skill 保持一致的 MCP 呼叫風格
- 支援相同的亞馬遜站點 (US, GB, DE, FR, CA, JP, ES, IT, MX, AE, AU, BR, SA)
- 使用相同的 Sorftime MCP 配置

### 遷移指南

如果使用者之前使用 `analyze.py` 指令碼，現在可以直接使用 `/category-select` 命令：

**舊方式**:
```bash
python .claude/skills/category-selection/scripts/analyze.py "Sofas" --site US --limit 20
```

**新方式**:
```
/category-select "Sofas" US --limit 20
```

---

## [3.0.0] - 2026-03-02

### 新增
- 新增 sorftime_parser.py 內建解析器
- 修復 Unicode 轉義中文解析問題
- 修復 JSON 巢狀和控制字元問題
- 新增大檔案處理方案

---

## [2.0.0] - 2026-03-01

### 初始版本
- 基礎品類選品分析功能
- 五維評分模型
- Python 指令碼驅動架構
