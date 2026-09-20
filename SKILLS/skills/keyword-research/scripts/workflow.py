#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
關鍵詞調研分析主工作流 v1.1

用法:
    python workflow.py B07PWTJ4H1 US
    python workflow.py B07PWTJ4H1 US --product-info product.json
    python workflow.py B07PWTJ4H1 US --long-tail-limit 20
    python workflow.py B07PWTJ4H1 US --skip-long-tail  # 跳過長尾詞擴充套件
"""

import os
import sys
import json
import re
from datetime import datetime
from collections import Counter

# 匯入本地模組
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from keyword_collector import KeywordCollector
from csv_generator import generate_csv_files
from generate_markdown_report import generate_markdown_report
from generate_html_dashboard import generate_html_dashboard


def get_project_root():
    """獲取專案根目錄"""
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.basename(path) == '.claude':
            return os.path.dirname(path)
        path = os.path.dirname(path)
    return os.getcwd()


PROJECT_ROOT = get_project_root()


class KeywordResearchWorkflow:
    """關鍵詞調研分析工作流"""

    def __init__(self, asin: str, site: str = 'US', product_info: dict = None,
                 long_tail_limit: int = 30, skip_classification: bool = False,
                 enable_llm_classification: bool = True, claude_code_env: bool = None):
        self.asin = asin.upper()
        self.site = site.upper()
        self.product_info = product_info or {}
        self.long_tail_limit = long_tail_limit
        self.skip_classification = skip_classification  # 跳過分類，僅儲存資料
        self.enable_llm_classification = enable_llm_classification  # 啟用 LLM 分類
        self.output_dir = ''
        self.all_keywords = []          # 所有采集的關鍵詞
        self.categorized_keywords = {}  # 分類後的關鍵詞
        self.execution_log = []         # 執行日誌

        # 檢測執行環境（優先使用手動指定的值）
        if claude_code_env is not None:
            self.is_claude_code_env = claude_code_env
        else:
            self.is_claude_code_env = self._detect_claude_code_environment()  # 自動檢測

    def log(self, message: str, level: str = 'INFO'):
        """記錄日誌"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.execution_log.append(log_entry)
        print(f"  {message}")

    def _detect_claude_code_environment(self) -> bool:
        """
        檢測是否在 Claude Code 環境中執行

        Returns:
            bool: 是否在 Claude Code 環境中
        """
        # 方法1: 檢查環境變數
        if os.environ.get('CLAUDE_CODE') or os.environ.get('CLAUDE_CODE_VERSION'):
            return True

        # 方法2: 檢查特定環境標識
        # Claude Code 透過 Skill 呼叫時，父程序通常是特殊的
        if os.environ.get('SKILL_NAME') or os.environ.get('SKILL_MODE'):
            return True

        # 方法3: 檢查工作目錄特徵
        cwd = os.getcwd()
        if '.claude' in cwd or 'skills' in cwd:
            # 進一步驗證：檢查是否在 .claude/skills 下執行
            script_path = os.path.abspath(__file__)
            if '.claude' in script_path and 'skills' in script_path:
                return True

        # 方法4: 檢查命令列引數特徵（透過 Skill 呼叫會有特定模式）
        if len(sys.argv) > 1 and any(arg.upper().startswith('B') for arg in sys.argv[1:3]):
            # 可能是透過 keyword-research skill 呼叫（ASIN 引數特徵）
            # 額外檢查：如果是透過命令列從 Skill 呼叫
            pass

        # 方法5: 檢查 sys 模組
        try:
            if 'claude' in sys.modules or 'anthropic' in sys.modules:
                return True
            # 檢查是否有特殊的模組載入路徑
            site_packages = [p for p in sys.path if 'site-packages' in p]
            if site_packages and 'anthropic' in str(site_packages):
                return True
        except:
            pass

        return False

    def setup_output_dir(self):
        """設定輸出目錄"""
        date_str = datetime.now().strftime('%Y%m%d')
        output_base = os.path.join(PROJECT_ROOT, 'keyword-reports')
        os.makedirs(output_base, exist_ok=True)

        dir_name = f"{self.asin}_{self.site}_{date_str}"
        self.output_dir = os.path.join(output_base, dir_name)
        os.makedirs(self.output_dir, exist_ok=True)

        print(f"\n輸出目錄: {self.output_dir}")

    def step1_collect_keywords(self) -> bool:
        """步驟1: 資料採集"""
        print(f"\n{'='*70}")
        print("步驟 1/4: 採集關鍵詞資料")
        print('='*70)

        try:
            collector = KeywordCollector(self.asin, self.site, verbose=False)
            keywords, fetched_product_info = collector.collect_all(
                long_tail_limit=self.long_tail_limit
            )

            if not keywords:
                self.log("未採集到任何關鍵詞", "ERROR")
                return False

            self.all_keywords = keywords

            # 合併產品資訊（優先使用使用者提供的，補充自動獲取的）
            if fetched_product_info:
                self._merge_product_info(fetched_product_info)
                self.log(f"✓ 產品資訊: {self.product_info.get('product_name', 'Unknown')}")

            self.log(f"✓ 採集到 {len(self.all_keywords)} 個關鍵詞")
            return True

        except Exception as e:
            self.log(f"資料採集失敗: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def _merge_product_info(self, fetched_info: dict):
        """
        合併產品資訊（使用者提供的優先順序更高）

        Args:
            fetched_info: 從 API 自動獲取的產品資訊
        """
        # 如果使用者沒有提供產品資訊，直接使用自動獲取的
        if not self.product_info:
            self.product_info = fetched_info
            return

        # 使用者提供了產品資訊，僅補充缺失的欄位
        for key, value in fetched_info.items():
            if not self.product_info.get(key):
                self.product_info[key] = value
            # 對於列表型別欄位，合併去重
            elif isinstance(value, list) and value:
                existing = self.product_info.get(key, [])
                if isinstance(existing, list):
                    combined = list(set(existing + value))
                    self.product_info[key] = combined

    def step2_classify_keywords(self) -> bool:
        """步驟2: LLM 智慧分類"""
        print(f"\n{'='*70}")
        print("步驟 2/4: LLM 智慧分類（8 維度）")
        print('='*70)

        # 如果跳過分類，直接使用智慧規則分類
        if self.skip_classification:
            self.log("跳過 LLM 分類，使用智慧規則分類", "INFO")
            self.categorized_keywords = self._smart_classify()
            self._log_classification_summary()
            return True

        try:
            # 準備關鍵詞列表（僅關鍵詞字串）
            keyword_list = [kw['keyword'] for kw in self.all_keywords]

            # 構建分類 prompt
            classification_prompt = self._build_classification_prompt(
                keyword_list, self.product_info
            )

            # 儲存 prompt 用於除錯
            prompt_file = os.path.join(self.output_dir, 'classification_prompt.txt')
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(classification_prompt)
            self.log(f"分類提示詞已儲存: {prompt_file}")

            # 檢測執行環境
            if self.is_claude_code_env and self.enable_llm_classification:
                # 在 Claude Code 環境中，輸出標記讓 Agent 執行 LLM 分類
                print(f"\n" + "="*70)
                print("🤖 Claude Code 環境 - 觸發 LLM 分類")
                print("="*70)

                # 先嚐試載入已存在的分類結果
                self.categorized_keywords = self._load_categorized_result()

                if self.categorized_keywords:
                    self.log("✓ 使用已有分類結果", "INFO")
                else:
                    # 輸出特殊標記，讓 Skill 系統知道需要執行 LLM 分類
                    print(f"\n>>> LLM_CLASSIFICATION_NEEDED <<<")
                    print(f">>> PROMPT_FILE: {prompt_file} <<<")
                    print(f">>> OUTPUT_FILE: {os.path.join(self.output_dir, 'categorized_result.json')} <<<")
                    print("\n📋 分類提示詞內容:")
                    print("-" * 70)
                    # 輸出完整提示詞的前1000字元作為預覽
                    preview = classification_prompt[:3000] if len(classification_prompt) > 3000 else classification_prompt
                    print(preview)
                    if len(classification_prompt) > 3000:
                        print(f"\n... (省略 {len(classification_prompt) - 3000} 字元，完整內容見 {prompt_file})")
                    print("-" * 70)

                    # 暫時使用規則分類作為後備
                    self.log("⏳ 等待 LLM 分類結果...", "INFO")
                    self.categorized_keywords = self._smart_classify()

                    # 記錄這是臨時分類結果
                    self.log("⚠ 使用規則分類作為臨時結果，可重新執行 LLM 分類", "WARN")
            else:
                # 非 Claude Code 環境，優先載入已有分類結果
                reason = "已跳過分類" if self.skip_classification else "非 Claude Code 環境"
                self.log(f"{reason}，嘗試載入已有分類結果", "INFO")
                
                # 嘗試載入已存在的分類結果
                self.categorized_keywords = self._load_categorized_result()
                
                if self.categorized_keywords:
                    self.log("✓ 使用已有 LLM 分類結果", "INFO")
                else:
                    self.log("⚠ 無已有分類結果，使用智慧規則分類", "WARN")
                    self.categorized_keywords = self._smart_classify()

            self._log_classification_summary()
            return True

        except Exception as e:
            self.log(f"分類失敗: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            # 異常情況下使用規則分類
            self.categorized_keywords = self._smart_classify()
            self._log_classification_summary()
            return True

    def _log_classification_summary(self):
        """記錄分類摘要"""
        total_categorized = sum(len(v) for v in self.categorized_keywords.values())
        self.log(f"✓ 分類完成，共 {total_categorized} 個關鍵詞已分類")

        for category, keywords in self.categorized_keywords.items():
            if keywords:
                cat_name = self._get_category_display_name(category)
                self.log(f"  - {cat_name}: {len(keywords)} 個")

        # 記錄分類方法到摘要
        if hasattr(self, 'is_claude_code_env') and self.is_claude_code_env:
            method = "LLM (Claude Code)" if self.enable_llm_classification and not self.skip_classification else "規則"
        else:
            method = "規則"
        self.log(f"分類方法: {method}", "INFO")

    def _smart_classify(self) -> dict:
        """
        智慧規則分類（備用方案）

        基於關鍵詞模式和產品資訊進行智慧分類
        """
        # 構建產品上下文
        product_context = self._build_product_context()

        # 獲取產品名稱和核心屬性
        product_name = self.product_info.get('product_name', '')
        if not product_name:
            # 從關鍵詞中推斷
            core_keywords = sorted(self.all_keywords,
                                 key=lambda x: x.get('search_volume', 0),
                                 reverse=True)[:5]
            product_name = core_keywords[0]['keyword'] if core_keywords else ''

        categorized = {
            'NEGATIVE': [],
            'BRAND': [],
            'MATERIAL': [],
            'SCENARIO': [],
            'ATTRIBUTE': [],
            'FUNCTION': [],
            'CORE': [],
            'OTHER': []
        }

        # 常見否定詞模式（根據產品型別動態調整）
        negative_patterns = self._get_negative_patterns(product_context)
        brand_patterns = self._get_brand_patterns()
        material_patterns = self._get_material_patterns(product_context)
        scenario_patterns = self._get_scenario_patterns(product_context)
        attribute_patterns = self._get_attribute_patterns()
        function_patterns = self._get_function_patterns()

        for kw in self.all_keywords:
            keyword = kw['keyword'].lower()
            assigned = False

            # 1. 檢查否定詞
            for pattern, reason in negative_patterns:
                if pattern in keyword and reason:
                    categorized['NEGATIVE'].append(kw['keyword'])
                    assigned = True
                    break

            if not assigned:
                # 2. 檢查品牌詞
                for brand in brand_patterns:
                    if brand in keyword:
                        categorized['BRAND'].append(kw['keyword'])
                        assigned = True
                        break

            if not assigned:
                # 3. 檢查材質詞
                for material in material_patterns:
                    if material in keyword:
                        categorized['MATERIAL'].append(kw['keyword'])
                        assigned = True
                        break

            if not assigned:
                # 4. 檢查場景詞
                for scenario in scenario_patterns:
                    if scenario in keyword:
                        categorized['SCENARIO'].append(kw['keyword'])
                        assigned = True
                        break

            if not assigned:
                # 5. 檢查屬性詞
                for attr in attribute_patterns:
                    if attr in keyword:
                        categorized['ATTRIBUTE'].append(kw['keyword'])
                        assigned = True
                        break

            if not assigned:
                # 6. 檢查功能詞
                for func in function_patterns:
                    if func in keyword:
                        categorized['FUNCTION'].append(kw['keyword'])
                        assigned = True
                        break

            if not assigned:
                # 7. 檢查核心詞（包含產品名稱的）
                if product_name and product_name.lower() in keyword:
                    categorized['CORE'].append(kw['keyword'])
                    assigned = True

            if not assigned:
                # 預設放到核心詞（如果是短詞）或其他（如果是長詞）
                if len(kw['keyword'].split()) <= 3:
                    categorized['CORE'].append(kw['keyword'])
                else:
                    categorized['OTHER'].append(kw['keyword'])

        return categorized

    def _build_product_context(self) -> dict:
        """構建產品上下文資訊"""
        context = {
            'product_name': '',
            'materials': [],
            'use_cases': [],
            'negative_features': []
        }

        if self.product_info:
            context['product_name'] = self.product_info.get('product_name', '')
            context['materials'] = self.product_info.get('materials', self.product_info.get('material', []))
            context['use_cases'] = self.product_info.get('use_cases', [])
            context['negative_features'] = self.product_info.get('negative_features', [])

        # 如果沒有產品資訊，從關鍵詞推斷
        if not context['product_name'] and self.all_keywords:
            top_keywords = sorted(self.all_keywords,
                                key=lambda x: x.get('search_volume', 0),
                                reverse=True)[:10]
            # 簡單推斷：最常見的詞根
            word_counter = Counter()
            for kw in top_keywords:
                words = kw['keyword'].lower().split()
                word_counter.update(words)

            if word_counter:
                most_common = word_counter.most_common(1)[0][0]
                context['product_name'] = most_common

        return context

    def _get_negative_patterns(self, context: dict) -> list:
        """獲取否定詞模式"""
        # 基礎否定詞
        base_patterns = [
            ('freestanding', '與壁掛式不符'),
            ('floor', '與壁掛式不符'),
            ('door', '與牆面不符'),
            ('over door', '與牆面不符'),
            ('tree', '與牆面不符'),
            ('shoe', '不同產品類別'),
        ]

        # 根據產品上下文新增特定否定詞
        if context.get('negative_features'):
            for feature in context['negative_features']:
                base_patterns.append((feature.lower(), f'與產品特性不符: {feature}'))

        return base_patterns

    def _get_brand_patterns(self) -> list:
        """獲取品牌詞模式（包含IP品牌）"""
        # 家居品牌
        home_brands = [
            'umbra', 'simplehuman', 'mdesign', 'mDesign',
            'household essentials', 'colonial candle',
            'melissa & doug', 'crayola'
        ]

        # IP品牌（玩具/娛樂）
        ip_brands = [
            # 電影/電視
            'star wars', 'stranger things', 'lord of the rings', 'game of thrones',
            'marvel', 'dc comics', 'harry potter', 'pixar', 'disney',
            # 遊戲
            'minecraft', 'fortnite', 'roblox', 'pokemon', 'zelda',
            'dungeons and dragons', 'dnd', 'dragon age', 'skyrim',
            # 動畫/系列
            'ninjago', 'monkie kid', 'hidden side', 'bionicle', 'nexo knights',
            'angry birds', 'avatar', 'how to train your dragon',
            # 其他玩具品牌
            'playmobil', 'barbie', 'hot wheels', 'nerf', 'hasbro'
        ]

        return home_brands + ip_brands

    def _get_material_patterns(self, context: dict) -> list:
        """獲取材質詞模式"""
        materials = ['wooden', 'wood', 'metal', 'aluminum', 'bamboo',
                    'plastic', 'steel', 'iron', 'ceramic', 'glass',
                    'fabric', 'leather', 'canvas', 'paper']

        # 新增產品特定材質
        if context.get('materials'):
            materials.extend([m.lower() for m in context['materials']])

        return materials

    def _get_scenario_patterns(self, context: dict) -> list:
        """獲取場景詞模式"""
        scenarios = ['entryway', 'bathroom', 'mudroom', 'garage',
                    'bedroom', 'kitchen', 'living room', 'office',
                    'outdoor', 'indoor', 'patio', 'deck']

        # 新增產品特定場景
        if context.get('use_cases'):
            scenarios.extend([s.lower() for s in context['use_cases']])

        return scenarios

    def _get_attribute_patterns(self) -> list:
        """獲取屬性詞模式"""
        return [
            # 安裝方式
            'mount', 'wall mount', 'freestanding', 'over door',
            # 特性
            'heavy duty', 'rustic', 'vintage', 'expandable', 'folding',
            # 元件
            'hook', 'shelf', 'rack', 'holder', 'organizer', 'storage', 'container',
            # 尺寸
            'large', 'small', 'medium', 'mini', 'giant', 'big',
            # 主題/風格（玩具/套裝常用）
            'medieval', 'castle', 'knight', 'viking', 'fantasy', 'dragon',
            'minifigure', 'set', 'building', 'construction'
        ]

    def _get_function_patterns(self) -> list:
        """獲取功能詞模式"""
        return [
            'hanging', 'display', 'organizer', 'storage',
            'holder', 'stand', 'rack', 'shelf'
        ]

    def _build_classification_prompt(self, keywords: list, product_info: dict) -> str:
        """構建分類提示詞"""
        # 格式化產品資訊
        product_desc = self._format_product_info(product_info)

        # 準備關鍵詞 JSON（前500個作為示例）
        sample_keywords = json.dumps(keywords[:500], ensure_ascii=False)

        prompt = f"""你是一位亞馬遜關鍵詞分類專家。請根據以下產品資訊，將關鍵詞列表按 8 個維度分類。

{product_desc}

【分類維度說明】
1. **NEGATIVE (否定/敏感詞)**: 與產品不相關、描述不符的詞，需直接否定
   - 例：freestanding（落地式）vs wall mount（壁掛式）
   - 例：over door（門後）vs wall（牆面）

2. **BRAND (品牌詞)**: 競品品牌名稱
   - 例：umbra, simplehuman, mDesign, household essentials

3. **MATERIAL (材質詞)**: 描述產品材質的詞
   - 例：wooden, metal, aluminum, bamboo, plastic

4. **SCENARIO (使用場景詞)**: 產品使用的位置/場景
   - 例：entryway, bathroom, mudroom, garage, bedroom

5. **ATTRIBUTE (屬性修飾詞)**: 描述產品屬性/特性的詞
   - 例：wall mount, heavy duty, rustic, vintage, expandable

6. **FUNCTION (功能詞)**: 描述產品功能的詞
   - 例：hanging, storage, organizer, display

7. **CORE (核心產品詞)**: 產品核心名稱
   - 例：coat rack, hook, hanger, hat rack, towel rack

8. **OTHER (其他)**: 未分類、拼寫錯誤、其他語言等
   - 例：coatrac（拼寫錯誤）, perchero（西語）

【待分類關鍵詞】（共 {len(keywords)} 個，前500個示例）
{sample_keywords}

【輸出格式】
請嚴格按照以下 JSON 格式輸出，不要包含任何其他內容：
```json
{{
  "NEGATIVE": ["keyword1", "keyword2", ...],
  "BRAND": ["keyword1", "keyword2", ...],
  "MATERIAL": ["keyword1", "keyword2", ...],
  "SCENARIO": ["keyword1", "keyword2", ...],
  "ATTRIBUTE": ["keyword1", "keyword2", ...],
  "FUNCTION": ["keyword1", "keyword2", ...],
  "CORE": ["keyword1", "keyword2", ...],
  "OTHER": ["keyword1", "keyword2", ...]
}}
```

注意：每個關鍵詞只能屬於一個分類，請根據最相關的特徵進行分類。如果關鍵詞超過500個，請按相同規則處理剩餘關鍵詞。

【產品資訊參考】
ASIN: {self.asin}
站點: {self.site}
"""

        return prompt

    def _format_product_info(self, product_info: dict) -> str:
        """格式化產品資訊"""
        if not product_info:
            return "【產品資訊】未提供（請根據 ASIN 推斷）"

        info_parts = ["【產品資訊】"]
        for key, value in product_info.items():
            if isinstance(value, list):
                info_parts.append(f"{key}: {', '.join(str(v) for v in value)}")
            else:
                info_parts.append(f"{key}: {value}")

        return '\n'.join(info_parts)

    def _load_categorized_result(self) -> dict:
        """載入分類結果（從檔案或透過其他方式）"""
        result_file = os.path.join(self.output_dir, 'categorized_result.json')

        # 嘗試讀取已存在的分類結果
        if os.path.exists(result_file):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.log(f"讀取分類結果失敗: {e}", 'WARN')

        # 如果沒有檔案，返回空字典（需要 Agent 填充）
        return {}

    def _get_category_display_name(self, category: str) -> str:
        """獲取分類顯示名稱"""
        names = {
            'NEGATIVE': '否定/敏感詞',
            'BRAND': '品牌詞',
            'MATERIAL': '材質詞',
            'SCENARIO': '使用場景詞',
            'ATTRIBUTE': '屬性修飾詞',
            'FUNCTION': '功能詞',
            'CORE': '核心產品詞',
            'OTHER': '其他',
            'CHARACTER': '角色詞'  # 特殊分類
        }
        return names.get(category, category)

    def step3_generate_reports(self) -> bool:
        """步驟3: 生成報告"""
        print(f"\n{'='*70}")
        print("步驟 3/4: 生成分析報告")
        print('='*70)

        try:
            # 生成 CSV 檔案
            print("  生成 CSV 詞庫...")
            csv_files = generate_csv_files(
                self.all_keywords,
                self.categorized_keywords,
                self.output_dir
            )
            for file in csv_files:
                print(f"    ✓ {os.path.basename(file)}")

            # 生成 Markdown 報告
            print("  生成 Markdown 分析報告...")
            report_file = generate_markdown_report(
                self.asin,
                self.site,
                self.all_keywords,
                self.categorized_keywords,
                self.output_dir,
                self.product_info
            )
            print(f"    ✓ {os.path.basename(report_file)}")

            # 生成 HTML 儀表板
            print("  生成 HTML 視覺化儀表板...")
            dashboard_file = generate_html_dashboard(
                self.asin,
                self.site,
                self.all_keywords,
                self.categorized_keywords,
                self.output_dir,
                self.product_info
            )
            print(f"    ✓ {os.path.basename(dashboard_file)}")

            # 儲存原始資料
            data_file = os.path.join(self.output_dir, 'keywords_raw.json')
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_keywords, f, ensure_ascii=False, indent=2)
            print(f"    ✓ keywords_raw.json")

            return True

        except Exception as e:
            self.log(f"報告生成失敗: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return False

    def step4_save_summary(self) -> bool:
        """步驟4: 儲存執行摘要"""
        try:
            # 儲存執行日誌
            log_file = os.path.join(self.output_dir, 'execution.log')
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.execution_log))

            # 儲存分類摘要
            summary_file = os.path.join(self.output_dir, 'summary.json')
            summary = {
                'asin': self.asin,
                'site': self.site,
                'generated_at': datetime.now().isoformat(),
                'total_keywords': len(self.all_keywords),
                'categorized': {
                    cat: len(kws) for cat, kws in self.categorized_keywords.items()
                },
                'output_directory': self.output_dir,
                'long_tail_limit': self.long_tail_limit
            }
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            self.log(f"儲存摘要失敗: {e}", "ERROR")
            return False

    def run(self) -> bool:
        """執行完整工作流"""
        print("\n" + "="*70)
        print(f"關鍵詞調研分析: {self.asin} ({self.site})")
        print("="*70)

        # 設定輸出目錄
        self.setup_output_dir()

        # 執行工作流
        success = True

        if not self.step1_collect_keywords():
            self.log("資料採集失敗", "ERROR")
            success = False

        # 注意：步驟2需要 Agent 介入執行分類
        # 如果使用命令列直接執行，會提示使用者手動分類
        if success and not self.categorized_keywords:
            if not self.step2_classify_keywords():
                success = False

        if success and self.categorized_keywords:
            if not self.step3_generate_reports():
                self.log("報告生成失敗", "ERROR")
                success = False

        if success:
            self.step4_save_summary()

        # 列印總結
        print("\n" + "="*70)
        if success:
            print("✓ 分析完成!")
            print(f"報告位置: {self.output_dir}")
            print("\n生成的檔案:")
            for file in sorted(os.listdir(self.output_dir)):
                print(f"  - {file}")
        else:
            print("✗ 分析失敗，請檢視錯誤資訊")
        print("="*70)

        return success


def main():
    """命令列入口"""
    if len(sys.argv) < 3:
        print("用法: python workflow.py <ASIN> <站點> [選項]")
        print("\n選項:")
        print("  --product-info <json檔案>   產品資訊檔案")
        print("  --long-tail-limit <數量>    長尾詞擴充套件數量（預設30，0表示跳過）")
        print("  --skip-long-tail            跳過長尾詞擴充套件")
        print("  --skip-classification       跳過LLM分類，僅儲存資料（可後續手動分類）")
        print("  --enable-llm-classification 啟用LLM分類（預設啟用）")
        print("  --disable-llm-classification 禁用LLM分類，使用規則分類")
        print("  --claude-code-env           指定在Claude Code環境中執行（觸發LLM分類）")
        print("\n示例:")
        print("  python workflow.py B07PWTJ4H1 US")
        print("  python workflow.py B07PWTJ4H1 US --product-info product.json")
        print("  python workflow.py B07PWTJ4H1 US --long-tail-limit 20")
        print("  python workflow.py B07PWTJ4H1 US --skip-long-tail")
        print("  python workflow.py B07PWTJ4H1 US --skip-classification")
        print("  python workflow.py B07PWTJ4H1 US --claude-code-env")
        print("\n注意:")
        print("  - 在 Claude Code 環境中，預設自動使用 LLM 分類")
        print("  - 在命令列環境中，預設使用規則分類")
        print("  - 使用 --claude-code-env 可強制啟用 LLM 分類模式")
        print("  - 使用 --skip-classification 可僅採集資料，稍後手動分類")
        sys.exit(1)

    asin = sys.argv[1]
    site = sys.argv[2]
    product_info = None
    long_tail_limit = 30
    skip_classification = False
    enable_llm_classification = True
    claude_code_env = None  # None=自動檢測，True=強制啟用，False=強制禁用

    # 解析引數
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--product-info' and i + 1 < len(sys.argv):
            with open(sys.argv[i + 1], 'r', encoding='utf-8') as f:
                product_info = json.load(f)
            i += 2
        elif sys.argv[i] == '--long-tail-limit' and i + 1 < len(sys.argv):
            long_tail_limit = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--skip-long-tail':
            long_tail_limit = 0
            i += 1
        elif sys.argv[i] == '--skip-classification':
            skip_classification = True
            i += 1
        elif sys.argv[i] == '--disable-llm-classification':
            enable_llm_classification = False
            i += 1
        elif sys.argv[i] == '--enable-llm-classification':
            enable_llm_classification = True
            i += 1
        elif sys.argv[i] == '--claude-code-env':
            claude_code_env = True
            i += 1
        elif sys.argv[i] == '--no-claude-code-env':
            claude_code_env = False
            i += 1
        else:
            i += 1

    # 執行工作流
    workflow = KeywordResearchWorkflow(
        asin, site, product_info, long_tail_limit,
        skip_classification, enable_llm_classification, claude_code_env
    )
    success = workflow.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
