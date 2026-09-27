# 五維評分模型標準

**版本**: v1.0
**最後更新**: 2026-03-04
**狀態**: ✅ 正式版本

---

## 評分維度總覽

| 維度 | 分值 | 評估指標 | 資料欄位 |
|------|------|----------|----------|
| 市場規模 | 20 分 | Top100 月銷額 | `top100產品月銷額` |
| 增長潛力 | 25 分 | 低評論產品銷量佔比 | `low_reviews_sales_volume_share` |
| 競爭烈度 | 20 分 | Top3 品牌銷量佔比 | `top3_brands_sales_volume_share` |
| 進入壁壘 | 20 分 | Amazon 自營 + 新品機會 | `amazonOwned_sales_volume_share` + `low_reviews_sales_volume_share` |
| 利潤空間 | 15 分 | 平均價格 | `average_price` |
| **總分** | **100 分** | | |

---

## 1. 市場規模 (20 分)

**評估指標**: `top100產品月銷額` (Top100 產品月銷額)

| 銷額範圍 | 得分 |
|----------|------|
| > $10,000,000 | 20 |
| > $5,000,000 | 17 |
| > $1,000,000 | 14 |
| 其他 | 10 |

**Python 程式碼**:
```python
revenue = float(stats.get('top100產品月銷額', 0))
if revenue > 10_000_000:
    market_size_score = 20
elif revenue > 5_000_000:
    market_size_score = 17
elif revenue > 1_000_000:
    market_size_score = 14
else:
    market_size_score = 10
```

---

## 2. 增長潛力 (25 分)

**評估指標**: `low_reviews_sales_volume_share` (低評論產品銷量佔比，即評價數<300的產品)

| 佔比範圍 | 得分 | 說明 |
|----------|------|------|
| > 40% | 22 | 新品空間大 |
| > 20% | 18 | 新品有機會 |
| 其他 | 14 | 新品空間有限 |

**Python 程式碼**:
```python
low_review_share = float(stats.get('low_reviews_sales_volume_share', 0))
if low_review_share > 40:
    growth_score = 22
elif low_review_share > 20:
    growth_score = 18
else:
    growth_score = 14
```

---

## 3. 競爭烈度 (20 分)

**評估指標**: `top3_brands_sales_volume_share` (Top3 品牌銷量佔比)

| 佔比範圍 | 得分 | 競爭程度 |
|----------|------|----------|
| < 30% | 18 | 低度集中，機會大 |
| < 50% | 14 | 中度集中 |
| 其他 | 8 | 高度集中，競爭激烈 |

**Python 程式碼**:
```python
top3_share = float(stats.get('top3_brands_sales_volume_share', 0))
if top3_share < 30:
    competition_score = 18
elif top3_share < 50:
    competition_score = 14
else:
    competition_score = 8
```

---

## 4. 進入壁壘 (20 分)

**評估指標**:
- `amazonOwned_sales_volume_share` (Amazon 自營佔比)
- `low_reviews_sales_volume_share` (新品機會)

**評分邏輯**: Amazon 佔比越低 + 新品機會越大 = 壁壘越低

### Amazon 自營影響 (0-10 分)

| 佔比範圍 | 得分 |
|----------|------|
| < 20% | 10 | 擠壓小 |
| < 40% | 6 | 中等擠壓 |
| 其他 | 3 | 擠壓大 |

### 新品機會影響 (0-10 分)

| 佔比範圍 | 得分 |
|----------|------|
| > 40% | 10 | 機會大 |
| > 20% | 6 | 有機會 |
| 其他 | 3 | 機會小 |

### 總分計算

`進入壁壘得分 = Amazon 自營得分 + 新品機會得分`

**範圍**: 6-20 分

**Python 程式碼**:
```python
amazon_share = float(stats.get('amazonOwned_sales_volume_share', 0))
low_review_share = float(stats.get('low_reviews_sales_volume_share', 0))

barrier_score = 0

# Amazon 佔影響分
if amazon_share < 20:
    barrier_score += 10
elif amazon_share < 40:
    barrier_score += 6
else:
    barrier_score += 3

# 新品機會得分
if low_review_share > 40:
    barrier_score += 10
elif low_review_share > 20:
    barrier_score += 6
else:
    barrier_score += 3
```

---

## 5. 利潤空間 (15 分)

**評估指標**: `average_price` (平均價格)

| 價格範圍 | 得分 |
|----------|------|
| > $300 | 12 |
| > $150 | 10 |
| > $50 | 7 |
| 其他 | 4 |

**Python 程式碼**:
```python
avg_price = float(stats.get('average_price', 0))
if avg_price > 300:
    profit_score = 12
elif avg_price > 150:
    profit_score = 10
elif avg_price > 50:
    profit_score = 7
else:
    profit_score = 4
```

---

## 評級判定

| 總分範圍 | 評級 | 建議 |
|----------|------|------|
| 80 - 100 | 優秀 | 強烈推薦進入 |
| 70 - 79 | 良好 | 可以考慮進入 |
| 50 - 69 | 一般 | 謹慎進入 |
| 0 - 49 | 較差 | 不建議進入 |

---

## 欄位名稱對映表

| 中文名稱 | 英文鍵名 | 資料來源 |
|----------|----------|----------|
| Top100 產品月銷額 | `top100產品月銷額` | category_report |
| Top100 產品月銷量 | `top100產品月銷量` | category_report |
| 平均價格 | `average_price` | category_report |
| 中位數價格 | `median_price` | category_report |
| Top3 品牌銷量佔比 | `top3_brands_sales_volume_share` | category_report |
| Amazon 自營佔比 | `amazonOwned_sales_volume_share` | category_report |
| 高評分產品佔比 | `high_rated_sales_volume_share` | category_report |
| 低評論產品佔比 | `low_reviews_sales_volume_share` | category_report |

---

## 實現檔案清單

以下檔案應使用本標準:

| 檔案 | 狀態 | 備註 |
|------|------|------|
| `scripts/data_utils.py` | ✅ 已修復 | calculate_five_dimension_score() |
| `scripts/parse_sorftime_sse.py` | ✅ 正確 | calculate_scores() |
| `scripts/sse_decoder.py` | ✅ 已新增 | calculate_five_dimension_score() |
| `SKILL.md` | ✅ 正確 | 文件說明 |

---

## 測試用例

### 測試案例 1: Sofas 品類 (美國)

```python
stats = {
    'top100產品月銷額': 24869166.89,  # $24.87M
    'low_reviews_sales_volume_share': 52.99,  # 52.99%
    'top3_brands_sales_volume_share': 19.49,  # 19.49%
    'amazonOwned_sales_volume_share': 6.37,  # 6.37%
    'average_price': 323.75
}

# 預期得分:
# 市場規模: 20 (>$10M)
# 增長潛力: 22 (>40%)
# 競爭烈度: 18 (<30%)
# 進入壁壘: 20 (10 + 10)
# 利潤空間: 12 (>$300)
# 總分: 92/100 → 優秀
```

### 測試案例 2: 小品類

```python
stats = {
    'top100產品月銷額': 800000,  # $0.8M
    'low_reviews_sales_volume_share': 15,  # 15%
    'top3_brands_sales_volume_share': 55,  # 55%
    'amazonOwned_sales_volume_share': 45,  # 45%
    'average_price': 35
}

# 預期得分:
# 市場規模: 10 (<$1M)
# 增長潛力: 14 (<20%)
# 競爭烈度: 8 (>50%)
# 進入壁壘: 6 (3 + 3)
# 利潤空間: 4 (<$50)
# 總分: 42/100 → 較差
```

---

*本文件由 Claude Code 維護 | 如有修改請同步更新所有實現檔案*
