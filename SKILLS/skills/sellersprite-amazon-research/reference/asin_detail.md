# ASIN 分析工具集

## `asin_detail` — ASIN 詳情

### 用途
獲取單個 ASIN 的詳細資訊：標題、品牌、價格、評分、變體、賣家等。

### 請求引數
- `marketplace`: 站點
- `asin`: ASIN（單值）
- `month`: yyyyMM

### 響應欄位
標題、品牌、賣家、價格、評分、評分數、BSR、變體資訊、配送方式、上架日期、圖片 URL、描述等。

---

## `keepa_info` — Keepa 趨勢資料

### 用途
獲取 ASIN 的歷史價格、排名、銷量趨勢曲線（Keepa 風格）。

### 請求引數
- `marketplace`: 站點
- `asin`: ASIN（單值）
- `month`: yyyyMM

### 響應欄位
價格歷史、BSR 歷史、銷量歷史資料點。

---

## `asin_prediction` — 銷量預測

### 用途
基於歷史資料預測 ASIN 的未來銷量。

### 請求引數
- `marketplace`: 站點
- `asin`: ASIN

---

## `asin_coupon_trend` — 優惠趨勢

### 用途
ASIN 的 Coupon/促銷歷史趨勢。

---

## `asin_detail_with_coupon_trend` — 詳情+優惠

### 用途
一次性獲取 ASIN 詳情和優惠趨勢資料。

---

## `bsr_prediction` — BSR 銷量預估

### 用途
根據 BSR 排名估算銷量。

### 請求引數
- `category`: 類目 ID
- `rank`: BSR 排名
