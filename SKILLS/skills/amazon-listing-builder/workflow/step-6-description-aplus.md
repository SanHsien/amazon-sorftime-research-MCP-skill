# 第六步：產品描述 + A+ 內容

> **描述和 A+ 不是重複五點，而是用來講完整場景**。把買家代入"使用前痛點 → 使用場景 → 產品解決方案 → 細節對比 → 使用步驟 → 適合人群 → 注意事項"的敘事流。

## 🚨 本步不調 MCP（可選瀏覽器補充）

本步基於**第二步問題庫 + 第三步賣點證據庫 + 第五步五點描述**生成，不再呼叫 MCP 工具。

### ✅ 瀏覽器補充（可選）

```javascript
// 1. 品牌官網（拿品牌定位語言、品牌故事）
mcp__web_reader__webReader({url:"https://yourbrand.com/about"})
mcp__web_reader__webReader({url:"https://yourbrand.com/story"})

// 2. 競品 A+ 模組（如需結構參考，可選）
mcp__web_reader__webReader({
  url:"https://www.amazon.com/dp/B07XXX...",  // 僅看 A+ 模組結構
  retain_images:false
})
```

### ❌ 禁止行為

不要用瀏覽器抓競品描述湊內容，競品描述已在第二步透過 `asin_detail` MCP 拿到。

---

## 一、描述 vs A+ 的分工

| 內容 | 作用 | 重點 |
|------|------|------|
| 產品描述 | 文字版故事 | 移動端閱讀、文字索引 |
| A+ 內容 | 圖文模組敘事 | 桌面端閱讀、視覺信任、語義關聯 |

> A+ 是承接 Cosmo 語義演算法的**最強載體**，因為它可以用圖片和模組把"產品-場景-屬性-問題"完整連線起來。

---

## 二、產品描述結構（7 段式）

```
1. 開頭痛點共鳴（使用者的真實困境）
2. 使用場景代入（讓使用者想象擁有後的樣子）
3. 產品解決方案（核心賣點串講）
4. 細節對比（與普通款的差異）
5. 使用步驟（降低使用門檻）
6. 適合人群（精準定位）
7. 注意事項（預期管理，減少差評）
```

### 案例：抗 UV 戶外模擬植物

> **Want a Colorful Porch Without the Maintenance?**
>
> If you love the look of fresh flowers but don't have time to water, trim, and replant every season, these UV-resistant artificial flowers are designed for low-maintenance outdoor decor.
>
> **Built for Outdoor Use**
>
> Made with UV-resistant materials to help reduce fading, these faux plants are suited for patio, porch, and garden arrangements. The flexible stems insert directly into planters, baskets, and window boxes — no tools required.
>
> **Realistic Look That Lasts**
>
> Natural color variation and layered petals create a lifelike look from a distance. Unlike thin plastic florals that look flat, each bundle is shaped to mimic real blooms.
>
> **How to Use**
>
> 1. Unbox and gently fluff each bundle.
> 2. Insert stems into your planter or window box.
> 3. Arrange 4-6 bundles per medium planter for full coverage.
>
> **Who It's For**
>
> Homeowners, renters, and decorators who want lasting curb appeal without weekly upkeep.
>
> **Please Note**
>
> Like all outdoor decor, long-term extreme sun and weather exposure may gradually affect color. For longest life, shelter during severe storms.

---

## 三、A+ 內容模組結構（標準 6-7 屏）

| 屏 | 內容 | 目的 |
|----|------|------|
| 1 | 戶外場景大圖 + 品牌定位 | 第一眼代入 |
| 2 | 抗 UV 材料示意 | 痛點證據（褪色） |
| 3 | 花瓣細節圖 | 痛點證據（真實感） |
| 4 | 適用場景拼圖（patio/porch/garden/balcony） | 語義覆蓋場景 |
| 5 | 數量與規格對比 | 決策輔助 |
| 6 | 包裝與運輸加固 | 信任建立 |
| 7 | 普通款 vs 抗 UV 款對比 | 差異化價值 |

---

## 四、A+ 模組語義覆蓋矩陣

確保 A+ 視覺模組**覆蓋核心語義關係**：

| 語義關係 | A+ 屏 | 對應關鍵詞 |
|---------|------|----------|
| 產品 → 場景（patio） | 第 1 屏 + 第 4 屏 | patio, outdoor |
| 產品 → 屬性（UV resistant） | 第 2 屏 | UV resistant, fade resistant |
| 產品 → 屬性（realistic） | 第 3 屏 | realistic, natural look |
| 產品 → 規格（12 bundles） | 第 5 屏 | 12 bundles, bulk |
| 產品 → 信任（packaging） | 第 6 屏 | protective packaging |
| 產品 → 差異化 | 第 7 屏 | vs standard faux flowers |

---

## 五、給美工的圖片需求清單

A+ 的成敗在圖片。每個模組都要給美工一份清晰的需求文件：

```markdown
## A+ 第 2 屏：抗 UV 材料示意
- 主體：產品近景，標出花瓣材質
- 配色：溫暖自然，避免過豔
- 文案：UV Resistant Material — Help Reduce Fading
- 標註：陽光照射示意 + "Tested for Outdoor Use"
- 尺寸：970 x 600
- 風格參考：[附競品 A+ 連結]
```

---

## 六、給 Codex 的提示詞（本步專用）

> 輸入：痛點-證據對映表、使用者問題庫、五點描述（來自第五步）、品牌定位、產品規格、合規限制。
>
> 任務：
>
> **A. 產品描述**
> 1. 按 7 段式生成英文描述
> 2. 每段 60-100 字
> 3. 自然融入 L1-L4 關鍵詞（不堆砌）
> 4. 移動端友好（短段落、加粗標題）
> 5. 包含"使用步驟"和"注意事項"降低差評
>
> **B. A+ 模組結構**
> 1. 設計 6-7 屏佈局，每屏對應一個語義關係
> 2. 每屏給出：標題、正文、圖片需求、關鍵詞
> 3. 標註每屏對應哪個使用者問題
> 4. 給出對比模組（普通款 vs 升級款）
> 5. 不重複五點描述的原話

---

## 七、字元與字數規範

### 產品描述
| 站點 | 字數上限 | 建議 |
|------|---------|------|
| 美國站 | 2000 字元 | 800-1200 字元（移動端友好） |

### A+ 內容
| 模組型別 | 文字字數 | 圖片尺寸 |
|---------|---------|---------|
| Standard Image + Text | ≤100 字 | 970 x 600 |
| Standard Image Text Overlay | ≤50 字 | 970 x 600 |
| Standard Single Image | 無文字 | 970 x 600 |
| Comparison | ≤200 字 | 970 x 600 |

---

## 八、常見錯誤

| 錯誤 | 修正 |
|------|------|
| 描述只是五點的複述 | 用敘事流代替賣點羅列 |
| A+ 全是產品特寫，沒有場景圖 | 至少 3 個場景模組 |
| 沒有"使用步驟"模組 | 降低使用門檻 |
| 沒有"注意事項"模組 | 減少差評（預期管理） |
| 沒有對比模組 | 用普通款 vs 升級款凸顯差異 |
| 關鍵詞堆砌 | 自然融入敘事 |

---

## 九、輸出模板

```markdown
# 產品描述 + A+ 內容 — {產品名}

## 產品描述
[7 段式英文文案]

## A+ 模組結構

### 第 1 屏：戶外場景大圖
- 標題：[品牌] UV-Resistant Outdoor Florals
- 正文：Built for outdoor living
- 圖片需求：[詳細描述]
- 關鍵詞：outdoor, patio, UV resistant

### 第 2-7 屏：...

## 圖片需求清單（給美工）
| 屏 | 尺寸 | 需求 | 文案 |
|----|------|------|------|
| 1 | 970x600 | 戶外場景大圖 | [品牌] UV-Resistant Outdoor Florals |
| ... | ... | ... | ... |
```

---

## 十、檢查清單

- [ ] 描述按 7 段式結構
- [ ] 描述含"使用步驟"和"注意事項"
- [ ] A+ 6-7 屏，每屏對應一個語義關係
- [ ] A+ 包含對比模組
- [ ] 圖片需求清單完整
- [ ] 不重複五點原話
- [ ] 字數符合規範
- [ ] 關鍵詞自然融入
