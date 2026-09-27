#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
品類選品分析統一報告生成器 v3.0
支援: Markdown, Excel, HTML, CSV 四種格式
所有報告儲存到統一的輸出資料夾

主要改進 (v3.0):
1. 完整的模板變數替換（包括評級、分析、策略等）
2. 自動生成分析文字和風險提示
3. 修復 f-string 花括號轉義問題
4. 支援 Jinja2 風格模板語法
5. 新增品牌分析表格
"""

import os
import sys
import json
import csv
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class CategoryReportGenerator:
    """品類選品分析報告生成器"""

    def __init__(self, data: Dict, output_dir: Optional[str] = None):
        """
        初始化報告生成器

        Args:
            data: 包含 statistics, products, scores 的字典
            output_dir: 輸出目錄，預設為 category-reports/{品類名}_{日期}/
        """
        self.data = data
        self.statistics = data.get('statistics', {})
        self.products = data.get('products', [])
        self.scores = data.get('scores', {})

        # 確定輸出目錄
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # 使用品類名和日期建立資料夾
            category_name = self._get_category_name()
            date_str = datetime.now().strftime('%Y%m%d')
            safe_name = self._sanitize_filename(category_name)
            self.output_dir = Path('category-reports') / f"{safe_name}_{date_str}"

        # 建立輸出目錄
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 建立資料子目錄
        self.data_dir = self.output_dir / 'data'
        self.data_dir.mkdir(exist_ok=True)

        self.generated_files = []

    def _get_category_name(self) -> str:
        """從資料中獲取品類名稱"""
        # 嘗試從各個位置獲取品類名
        if 'category_name' in self.data:
            return self.data['category_name']
        if '品類名稱' in self.data:
            return self.data['品類名稱']
        return 'Unknown_Category'

    def _sanitize_filename(self, name: str) -> str:
        """清理檔名，移除非法字元"""
        # 移除或替換非法字元
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            name = name.replace(char, '_')
        # 移除空格
        name = name.replace(' ', '_')
        return name[:100]  # 限制長度

    def generate_all(self) -> Dict[str, str]:
        """
        生成所有格式的報告

        Returns:
            生成的檔案路徑字典 {格式: 檔案路徑}
        """
        results = {}

        # 1. Markdown 報告
        try:
            md_path = self.generate_markdown()
            results['markdown'] = str(md_path)
        except Exception as e:
            print(f"Markdown 生成失敗: {e}")

        # 2. CSV 資料檔案
        try:
            csv_path = self.generate_csv()
            results['csv'] = str(csv_path)
        except Exception as e:
            print(f"CSV 生成失敗: {e}")

        # 3. Excel 報告 (需要 openpyxl)
        try:
            excel_path = self.generate_excel()
            results['excel'] = str(excel_path)
        except ImportError:
            print("Excel 生成跳過 (需要 openpyxl)")
        except Exception as e:
            print(f"Excel 生成失敗: {e}")

        # 4. HTML 儀表板
        try:
            html_path = self.generate_html()
            results['html'] = str(html_path)
        except Exception as e:
            print(f"HTML 生成失敗: {e}")

        # 5. 儲存原始 JSON 資料
        try:
            json_path = self.generate_json()
            results['json'] = str(json_path)
        except Exception as e:
            print(f"JSON 生成失敗: {e}")

        return results

    def generate_markdown(self) -> Path:
        """生成 Markdown 報告"""
        filename = self.output_dir / "category_analysis_report.md"

        # 讀取模板
        template_path = Path(__file__).parent.parent / 'assets' / 'report_template.md'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = self._get_default_markdown_template()

        # 替換變數
        content = self._replace_variables(content)

        # 寫入檔案
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        self.generated_files.append(filename)
        print(f"✓ Markdown 報告: {filename}")
        return filename

    def generate_csv(self) -> Path:
        """生成 CSV 資料檔案"""
        # 1. 統計資料 CSV
        stats_file = self.data_dir / "statistics.csv"
        with open(stats_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['指標', '數值'])
            for key, value in self.statistics.items():
                writer.writerow([key, value])

        # 2. 產品列表 CSV
        products_file = self.data_dir / "products.csv"
        with open(products_file, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['ASIN', '標題', '品牌', '價格', '月銷量', '評分', '排名']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i, p in enumerate(self.products, 1):
                writer.writerow({
                    'ASIN': p.get('ASIN', ''),
                    '標題': p.get('標題', '')[:100],
                    '品牌': p.get('品牌', ''),
                    '價格': p.get('價格', 0),
                    '月銷量': p.get('月銷量', 0),
                    '評分': p.get('評分', 0),
                    '排名': i
                })

        # 3. 評分資料 CSV
        scores_file = self.data_dir / "scores.csv"
        with open(scores_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['維度', '得分', '滿分', '佔比%'])
            max_scores = {'市場規模': 20, '增長潛力': 25, '競爭烈度': 20, '進入壁壘': 20, '利潤空間': 15}
            total_max = sum(max_scores.values())
            for key, value in self.scores.items():
                if key in max_scores:
                    max_score = max_scores[key]
                    pct = (value / max_score * 100) if max_score > 0 else 0
                    writer.writerow([key, value, max_score, f"{pct:.1f}"])
                elif key not in ['總分', '評級']:
                    writer.writerow([key, value, '', ''])

        self.generated_files.extend([stats_file, products_file, scores_file])
        print(f"✓ CSV 資料檔案: {self.data_dir}")
        return stats_file  # 返回主檔案

    def generate_excel(self) -> Path:
        """生成 Excel 報告"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font as OpenpyxlFont, Alignment, PatternFill
            from openpyxl.utils import get_column_letter
        except ImportError:
            raise ImportError("需要安裝 openpyxl: pip install openpyxl")

        filename = self.output_dir / "category_analysis_report.xlsx"
        wb = Workbook()

        # 刪除預設工作表
        wb.remove(wb.active)

        # 1. 概覽工作表
        self._create_overview_sheet(wb, OpenpyxlFont)

        # 2. 產品列表工作表
        self._create_products_sheet(wb, OpenpyxlFont, PatternFill)

        # 3. 評分工作表
        self._create_scores_sheet(wb, OpenpyxlFont)

        wb.save(filename)
        self.generated_files.append(filename)
        print(f"✓ Excel 報告: {filename}")
        return filename

    def generate_html(self) -> Path:
        """生成 HTML 儀表板"""
        filename = self.output_dir / "dashboard.html"

        # 讀取模板
        template_path = Path(__file__).parent.parent / 'assets' / 'dashboard_template.html'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = self._get_default_html_template()

        # 替換變數
        content = self._replace_html_variables(content)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

        self.generated_files.append(filename)
        print(f"✓ HTML 儀表板: {filename}")
        return filename

    def generate_json(self) -> Path:
        """儲存原始 JSON 資料"""
        filename = self.data_dir / "raw_data.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

        self.generated_files.append(filename)
        print(f"✓ JSON 資料: {filename}")
        return filename

    def _replace_variables(self, content: str) -> str:
        """替換 Markdown 模板變數"""
        # 基礎資訊
        content = content.replace('{{DATE}}', datetime.now().strftime('%Y-%m-%d'))
        content = content.replace('{{TIME}}', datetime.now().strftime('%H:%M:%S'))
        content = content.replace('{{CATEGORY_NAME}}', self._get_category_name())

        # 評級和建議
        total_score = self.scores.get('總分', 0)
        if total_score >= 80:
            rating = "優秀"
            recommendation = "強烈推薦進入"
        elif total_score >= 70:
            rating = "良好"
            recommendation = "可以考慮進入"
        elif total_score >= 50:
            rating = "一般"
            recommendation = "謹慎進入"
        else:
            rating = "較差"
            recommendation = "不建議進入"

        content = content.replace('{{SCORE_評級}}', rating)
        content = content.replace('{{SCORE_建議}}', recommendation)

        # 統計資料表格
        if '{% for key, value in statistics.items() %}' in content:
            # 替換 Jinja2 風格的迴圈為實際表格
            stats_table = ""
            for key, value in self.statistics.items():
                stats_table += f"| {key} | {value} |\n"
            content = content.replace('{% for key, value in statistics.items() %}', '')
            content = content.replace('| {{ key }} | {{ value }} |', stats_table)
            content = content.replace('{% endfor %}', '')

        # 統計資料變數
        for key, value in self.statistics.items():
            content = content.replace(f'{{{{STAT_{key}}}}}', str(value))

        # 評分 (包括佔比計算)
        max_scores = {'市場規模': 20, '增長潛力': 25, '競爭烈度': 20, '進入壁壘': 20, '利潤空間': 15}
        for key, value in self.scores.items():
            placeholder = '{{' + f'SCORE_{key}' + '}}'
            content = content.replace(placeholder, str(value))
            # 新增佔比
            if key in max_scores:
                pct = (value / max_scores[key] * 100) if max_scores[key] > 0 else 0
                placeholder_pct = '{{' + f'SCORE_{key}_佔比' + '}}'
                content = content.replace(placeholder_pct, f'{pct:.1f}%')

        # 生成分析文字
        analysis = self._generate_analysis_text()
        for key, value in analysis.items():
            content = content.replace(f'{{{{ANALYSIS_{key}}}}}', value)

        # 生成策略文字
        strategies = self._generate_strategy_text()
        for key, value in strategies.items():
            content = content.replace(f'{{{{STRATEGY_{key}}}}}', value)

        # 風險提示
        risks = self._generate_risk_text()
        content = content.replace('{{RISK_提示}}', risks)

        # 產品列表
        if '{{PRODUCTS_TABLE}}' in content and self.products:
            products_table = "| 排名 | ASIN | 品牌 | 價格 | 月銷量 | 評分 | 標題 |\n"
            products_table += "|------|------|------|------|--------|------|------|\n"
            for i, p in enumerate(self.products[:20], 1):
                title = p.get('標題', '')[:50]
                # 安全獲取數值
                price = self._safe_float(p.get('價格', 0))
                sales = self._safe_int(p.get('月銷量', 0))
                rating = self._safe_float(p.get('評分', 0))

                products_table += f"| {i} | {p.get('ASIN', '')} | {p.get('品牌', '')} | "
                products_table += f"${price:.2f} | {sales:,} | "
                products_table += f"{rating:.1f} | {title}... |\n"
            content = content.replace('{{PRODUCTS_TABLE}}', products_table)

        # 品牌表格
        if '{{BRANDS_TABLE}}' in content:
            brands_table = self._generate_brands_table()
            content = content.replace('{{BRANDS_TABLE}}', brands_table)

        return content

    def _generate_analysis_text(self) -> dict:
        """生成分析文字"""
        total_revenue = self._safe_float(self.statistics.get('總銷額', 0))
        avg_price = self._safe_float(self.statistics.get('平均價格', 0))
        top3_share = self._safe_float(self.statistics.get('Top3品牌佔比', 0))

        analysis = {}

        # 市場規模分析
        if total_revenue > 50_000_000:
            analysis['市場規模'] = "類目月銷額超過 5000 萬美元，屬於大規模市場，具有巨大的銷售潛力。"
        elif total_revenue > 10_000_000:
            analysis['市場規模'] = "類目月銷額在 1000 萬至 5000 萬美元之間，市場規模可觀。"
        else:
            analysis['市場規模'] = "類目月銷額低於 1000 萬美元，市場規模相對較小。"

        # 增長潛力分析
        growth_score = self.scores.get('增長潛力', 0)
        if growth_score >= 20:
            analysis['增長潛力'] = "低評論產品佔比較高，說明新品有較大的市場機會，增長潛力良好。"
        else:
            analysis['增長潛力'] = "低評論產品佔比較低，市場競爭激烈，新品增長機會有限。"

        # 競爭烈度分析
        if top3_share < 30:
            analysis['競爭烈度'] = "Top3 品牌佔比較低，市場競爭相對分散，新進入者有較多機會。"
        elif top3_share < 50:
            analysis['競爭烈度'] = "Top3 品牌佔比適中，市場存在一定競爭，但仍有機會。"
        else:
            analysis['競爭烈度'] = f"Top3 品牌佔比達到 {top3_share:.1f}%，市場高度集中，競爭非常激烈。"

        # 進入壁壘分析
        barrier_score = self.scores.get('進入壁壘', 0)
        if barrier_score >= 16:
            analysis['進入壁壘'] = "Amazon 自營佔比較低且新品機會多，進入壁壘較低。"
        elif barrier_score >= 10:
            analysis['進入壁壘'] = "Amazon 自營佔比適中或新品機會一般，進入壁壘中等。"
        else:
            analysis['進入壁壘'] = "Amazon 自營佔比較高且新品機會少，進入壁壘較高。"

        # 利潤空間分析
        profit_score = self.scores.get('利潤空間', 0)
        if profit_score >= 10:
            analysis['利潤空間'] = f"平均價格 ${avg_price:.0f}，利潤空間充足。"
        elif profit_score >= 6:
            analysis['利潤空間'] = f"平均價格 ${avg_price:.0f}，利潤空間一般。"
        else:
            analysis['利潤空間'] = f"平均價格 ${avg_price:.0f}，利潤空間有限，需注重成本控制。"

        return analysis

    def _generate_strategy_text(self) -> dict:
        """生成策略建議"""
        strategies = {}
        avg_price = self._safe_float(self.statistics.get('平均價格', 0))

        # 進入策略
        total_score = self.scores.get('總分', 0)
        if total_score >= 70:
            strategies['進入'] = "該品類綜合評分良好，可以考慮進入。建議關注差異化產品和細分市場。"
        elif total_score >= 50:
            strategies['進入'] = "該品類綜合評分一般，建議謹慎進入。需做好充分的市場調研和競爭分析。"
        else:
            strategies['進入'] = "該品類綜合評分較低，不建議進入。建議考慮其他品類。"

        # 定位建議
        strategies['定位'] = f"建議定價在 ${avg_price*0.8:.0f} - ${avg_price*1.2:.0f} 範圍內，注重產品質量和差異化功能。"

        # 定價建議
        if avg_price > 300:
            strategies['定價'] = "高階市場定價策略，強調品質和品牌價值。"
        elif avg_price > 100:
            strategies['定價'] = "中端市場定價策略，平衡價效比。"
        else:
            strategies['定價'] = "經濟型定價策略，注重成本控制和銷量規模。"

        return strategies

    def _generate_risk_text(self) -> str:
        """生成風險提示"""
        risks = []
        top3_share = self._safe_float(self.statistics.get('Top3品牌佔比', 0))

        if top3_share > 50:
            risks.append(f"- 市場高度集中，Top3 品牌佔比 {top3_share:.1f}%，難以與頭部品牌競爭")

        if self.scores.get('進入壁壘', 0) < 10:
            risks.append("- Amazon 自營佔比較高，需注意價格競爭")

        if self.scores.get('增長潛力', 0) < 15:
            risks.append("- 新品機會有限，需投入更多營銷資源")

        if not risks:
            risks.append("- 需關注產品質量以獲取好評")
            risks.append("- 建議定期跟蹤市場變化")

        return "\n".join(risks)

    def _generate_brands_table(self) -> str:
        """生成品牌分析表格"""
        if not self.products:
            return "| 暫無資料 |\n"

        # 統計品牌資料
        brand_stats = {}
        for p in self.products[:20]:
            brand = p.get('品牌', 'Unknown')
            if brand not in brand_stats:
                brand_stats[brand] = {'count': 0, 'total_price': 0, 'total_rating': 0}
            brand_stats[brand]['count'] += 1
            brand_stats[brand]['total_price'] += self._safe_float(p.get('價格', 0))
            brand_stats[brand]['total_rating'] += self._safe_float(p.get('評分', 0))

        # 生成表格
        table = "| 品牌 | 產品數 | 平均價格 | 平均評分 |\n"
        table += "|------|--------|----------|----------|\n"

        for brand, stats in sorted(brand_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
            avg_price = stats['total_price'] / stats['count'] if stats['count'] > 0 else 0
            avg_rating = stats['total_rating'] / stats['count'] if stats['count'] > 0 else 0
            table += f"| {brand} | {stats['count']} | ${avg_price:.2f} | {avg_rating:.1f} |\n"

        return table

    def _safe_float(self, value) -> float:
        """安全轉換為浮點數"""
        try:
            return float(str(value).replace(',', '').replace('%', ''))
        except:
            return 0.0

    def _safe_int(self, value) -> int:
        """安全轉換為整數"""
        try:
            return int(float(str(value).replace(',', '').replace('%', '')))
        except:
            return 0

    def _replace_html_variables(self, content: str) -> str:
        """替換 HTML 模板變數"""
        now = datetime.now()

        # ===== 基礎資訊 =====
        content = content.replace('{{CATEGORY_NAME}}', self._get_category_name())
        content = content.replace('{{SITE}}', self.data.get('site', 'US'))
        content = content.replace('{{DATA_DATE}}', now.strftime('%Y-%m-%d'))
        content = content.replace('{{GENERATED_TIME}}', now.strftime('%Y-%m-%d %H:%M:%S'))
        content = content.replace('{{DATE}}', now.strftime('%Y-%m-%d'))  # 相容舊模板

        # ===== 五維評分 (計算百分比) =====
        max_scores = {
            '市場規模': 20,
            '增長潛力': 25,
            '競爭烈度': 20,
            '進入壁壘': 20,
            '利潤空間': 15
        }

        # 英文鍵名對映
        score_key_map = {
            'market_size': '市場規模',
            'growth_potential': '增長潛力',
            'competition': '競爭烈度',
            'entry_barrier': '進入壁壘',
            'profit_margin': '利潤空間'
        }

        # 處理中文鍵名評分
        for cn_key, max_score in max_scores.items():
            score = self.scores.get(cn_key, 0)
            percent = (score / max_score * 100) if max_score > 0 else 0

            # 變數名轉換: 市場規模 -> MARKET_SIZE
            var_key = cn_key.upper().replace('潛力', '_POTENTIAL').replace('烈度', '').replace('壁壘', '_BARRIER').replace('空間', '_MARGIN')
            if cn_key == '競爭烈度':
                var_key = 'COMPETITION'
            elif cn_key == '進入壁壘':
                var_key = 'ENTRY_BARRIER'
            elif cn_key == '利潤空間':
                var_key = 'PROFIT_MARGIN'

            content = content.replace(f'{{{{{var_key}_SCORE}}}}', str(score))
            content = content.replace(f'{{{{{var_key}_PERCENT}}}}', f'{percent:.0f}')

        # 處理英文鍵名評分 (相容 data_adapter 輸出)
        for en_key, cn_key in score_key_map.items():
            score = self.scores.get(en_key, self.scores.get(cn_key, 0))
            max_score = max_scores[cn_key]
            percent = (score / max_score * 100) if max_score > 0 else 0

            var_key = en_key.upper()
            content = content.replace(f'{{{{{var_key}_SCORE}}}}', str(score))
            content = content.replace(f'{{{{{var_key}_PERCENT}}}}', f'{percent:.0f}')

        # 總分和評級
        total_score = self.scores.get('總分', self.scores.get('total', 0))
        rating = self.scores.get('評級', self.scores.get('rating', ''))
        content = content.replace('{{TOTAL_SCORE}}', str(total_score))
        content = content.replace('{{RATING}}', str(rating))

        # 推薦
        recommendation = self._get_recommendation(rating)
        content = content.replace('{{RECOMMENDATION}}', recommendation['text'])
        content = content.replace('{{STRATEGY}}', recommendation['strategy'])

        # ===== KPI 指標 =====
        kpi = self._calculate_kpi()
        content = content.replace('{{TOTAL_PRODUCTS}}', str(kpi['total_products']))
        content = content.replace('{{AVG_PRICE}}', f"{kpi['avg_price']:.2f}")
        content = content.replace('{{AVG_SALES}}', f"{kpi['avg_sales']:,.0f}")
        content = content.replace('{{AVG_RATING}}', f"{kpi['avg_rating']:.2f}")
        content = content.replace('{{TOTAL_SALES}}', f"{kpi['total_sales']:,.0f}")
        content = content.replace('{{CR3}}', f"{kpi['cr3']:.1f}")
        content = content.replace('{{CR3_RAW}}', f"{kpi['cr3']:.1f}")
        content = content.replace('{{HHI}}', f"{kpi['hhi']:.0f}")

        # ===== 關鍵發現變數 =====
        concentration_level = self._get_concentration_level(kpi['hhi'])
        content = content.replace('{{CONCENTRATION_LEVEL}}', concentration_level)

        conclusion_cr3 = self._get_cr3_conclusion(kpi['cr3'])
        content = content.replace('{{CONCLUSION_CR3}}', conclusion_cr3)

        brand_count = len(set(p.get('品牌', p.get('brand', '')) for p in self.products))
        content = content.replace('{{BRAND_COUNT}}', str(brand_count))
        content = content.replace('{{BRAND_DIVERSITY}}', '品牌多樣性高' if brand_count > 20 else '品牌較集中')

        new_product_pct = kpi.get('new_product_percent', 0)
        content = content.replace('{{NEW_PRODUCT_PERCENT}}', f"{new_product_pct:.1f}")
        content = content.replace('{{NEW_PRODUCT_CONCLUSION}}', self._get_new_product_conclusion(new_product_pct))

        seller_dist = self._get_seller_distribution_summary()
        content = content.replace('{{SELLER_DISTRIBUTION}}', seller_dist)

        competition_conclusion = self._get_competition_conclusion(kpi, rating)
        content = content.replace('{{COMPETITION_CONCLUSION}}', competition_conclusion)

        # ===== 圖表資料 (JavaScript JSON) =====
        chart_data = self._prepare_chart_data()

        content = content.replace('{{SALES_TREND_DATA}}', json.dumps(chart_data['sales_trend'], ensure_ascii=False))
        content = content.replace('{{PRICE_TREND_DATA}}', json.dumps(chart_data['price_trend'], ensure_ascii=False))
        content = content.replace('{{PRICE_DIST_DATA}}', json.dumps(chart_data['price_dist'], ensure_ascii=False))
        content = content.replace('{{RATING_DIST_DATA}}', json.dumps(chart_data['rating_dist'], ensure_ascii=False))
        content = content.replace('{{BRAND_SHARE_DATA}}', json.dumps(chart_data['brand_share'], ensure_ascii=False))
        content = content.replace('{{SELLER_SOURCE_DATA}}', json.dumps(chart_data['seller_source'], ensure_ascii=False))
        content = content.replace('{{BRAND_RATING_TREND_DATA}}', json.dumps(chart_data['brand_rating_trend'], ensure_ascii=False))
        content = content.replace('{{TOP50_PRODUCTS}}', json.dumps(chart_data['top50_products'], ensure_ascii=False))

        # 相容舊模板變數
        content = content.replace('{{STATISTICS_JSON}}', json.dumps(self.statistics, ensure_ascii=False))
        content = content.replace('{{PRODUCTS_JSON}}', json.dumps(self.products[:50], ensure_ascii=False))
        content = content.replace('{{SCORES_JSON}}', json.dumps(self.scores, ensure_ascii=False))

        return content

    def _calculate_kpi(self) -> Dict:
        """計算 KPI 指標"""
        if not self.products:
            return {
                'total_products': 0,
                'avg_price': 0,
                'avg_sales': 0,
                'avg_rating': 0,
                'total_sales': 0,
                'cr3': 0,
                'hhi': 0,
                'new_product_percent': 0
            }

        total_products = len(self.products)
        avg_price = sum(self._safe_float(p.get('價格', p.get('price', 0))) for p in self.products) / total_products
        avg_sales = sum(self._safe_int(p.get('月銷量', p.get('monthly_sales', 0))) for p in self.products) / total_products
        avg_rating = sum(self._safe_float(p.get('評分', p.get('rating', 0))) for p in self.products) / total_products
        total_sales = sum(self._safe_int(p.get('月銷量', p.get('monthly_sales', 0))) for p in self.products)

        # 計算品牌市場份額
        brands = {}
        for p in self.products:
            brand = p.get('品牌', p.get('brand', 'Unknown'))
            revenue = self._safe_float(p.get('月銷額', p.get('monthly_revenue', 0)))
            if revenue == 0:
                revenue = self._safe_float(p.get('價格', p.get('price', 0))) * self._safe_int(p.get('月銷量', p.get('monthly_sales', 0)))
            brands[brand] = brands.get(brand, 0) + revenue

        total_revenue = sum(brands.values())
        if total_revenue > 0:
            brand_shares = sorted(brands.values(), reverse=True)
            cr3 = sum(brand_shares[:3]) / total_revenue * 100
        else:
            cr3 = 0

        # 計算 HHI
        if total_revenue > 0:
            hhi = sum((share / total_revenue * 100) ** 2 for share in brands.values())
        else:
            hhi = 0

        # 新品佔比 (評論數 < 100)
        new_products = [p for p in self.products if self._safe_int(p.get('評論數', p.get('review_count', 0))) < 100]
        new_product_percent = len(new_products) / total_products * 100 if total_products > 0 else 0

        return {
            'total_products': total_products,
            'avg_price': avg_price,
            'avg_sales': avg_sales,
            'avg_rating': avg_rating,
            'total_sales': total_sales,
            'cr3': cr3,
            'hhi': hhi,
            'new_product_percent': new_product_percent
        }

    def _get_recommendation(self, rating: str) -> Dict[str, str]:
        """根據評級獲取推薦"""
        recommendations = {
            '優秀': {
                'text': '強烈推薦進入該品類',
                'strategy': '建議儘快進入，搶佔市場先機。注重產品差異化和服務質量。'
            },
            '良好': {
                'text': '可以考慮進入該品類',
                'strategy': '建議謹慎進入，尋找細分市場機會。做好競爭準備。'
            },
            '一般': {
                'text': '謹慎進入該品類',
                'strategy': '需充分評估風險，尋找差異化切入點。建議小規模試水。'
            },
            '較差': {
                'text': '不建議進入該品類',
                'strategy': '建議選擇其他更有競爭力的品類，或等待市場變化。'
            }
        }
        return recommendations.get(rating, recommendations['一般'])

    def _get_concentration_level(self, hhi: float) -> str:
        """根據 HHI 獲取市場集中度"""
        if hhi < 1500:
            return '低度集中'
        elif hhi < 2500:
            return '中度集中'
        else:
            return '高度集中'

    def _get_cr3_conclusion(self, cr3: float) -> str:
        """根據 CR3 獲取結論"""
        if cr3 < 30:
            return '市場較為分散，新進入者機會較大'
        elif cr3 < 50:
            return '市場有一定集中度，需避開頭部品牌優勢領域'
        else:
            return '頭部品牌優勢明顯，進入難度較大'

    def _get_new_product_conclusion(self, percent: float) -> str:
        """根據新品佔比獲取結論"""
        if percent > 40:
            return '新品表現活躍，市場對新進入者接受度高'
        elif percent > 20:
            return '新品有一定表現空間'
        else:
            return '新品表現乏力，市場存量競爭激烈'

    def _get_seller_distribution_summary(self) -> str:
        """獲取賣家分佈摘要"""
        sources = {}
        for p in self.products:
            source = p.get('賣家來源', p.get('seller_source', '其他'))
            if source not in sources:
                sources[source] = 0
            sources[source] += 1

        parts = []
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            pct = count / len(self.products) * 100 if self.products else 0
            parts.append(f"{source}佔{pct:.1f}%")

        return '、'.join(parts) if parts else '資料不足'

    def _get_competition_conclusion(self, kpi: Dict, rating: str) -> str:
        """獲取競爭結論"""
        parts = []
        if kpi['hhi'] > 2500:
            parts.append('市場高度集中')
        elif kpi['cr3'] > 50:
            parts.append('頭部品牌優勢明顯')

        if kpi['new_product_percent'] < 20:
            parts.append('新品空間有限')

        if not parts:
            return '競爭環境相對寬鬆，存在市場機會'
        return '；'.join(parts) + '，需充分評估競爭風險'

    def _prepare_chart_data(self) -> Dict:
        """準備圖表資料"""
        # 嘗試從 trend_data.json 讀取真實趨勢資料
        trend_data = self._load_trend_data()

        # 如果有真實資料，使用真實資料；否則使用模擬資料
        if trend_data and 'sales_trend' in trend_data:
            sales_trend = trend_data['sales_trend']
        else:
            # 模擬資料作為降級方案
            sales_trend = {
                'dates': [f'{i}月前' for i in range(25, 0, -1)],
                'sales': [10000 + i * 500 for i in range(25)]
            }

        if trend_data and 'price_trend' in trend_data:
            price_trend = trend_data['price_trend']
        else:
            price_trend = {
                'dates': [f'{i}月前' for i in range(25, 0, -1)],
                'prices': [300 + i * 2 for i in range(25)]
            }

        # 價格分佈
        price_dist = self._get_price_distribution()

        # 評分分佈
        rating_dist = self._get_rating_distribution()

        # 品牌份額 Top10
        brand_share = self._get_brand_share_data()

        # 賣家來源
        seller_source = self._get_seller_source_data()

        # 品牌評分趨勢 (使用 rating_trend 或模擬資料)
        if trend_data and 'rating_trend' in trend_data:
            rating_trend_raw = trend_data['rating_trend']
            brand_rating_trend = {
                'brands': list(brand_share['brands'][:5]),
                'dates': rating_trend_raw.get('dates', [f'{i}月前' for i in range(25, 0, -1)]),
                'data': {brand: rating_trend_raw.get('ratings', [4.2 + i * 0.01 for i in range(25)])
                        for brand in list(brand_share['brands'][:5])}
            }
        else:
            brand_rating_trend = {
                'brands': list(brand_share['brands'][:5]),
                'dates': [f'{i}月前' for i in range(25, 0, -1)],
                'data': {brand: [4.2 + i * 0.01 for i in range(25)] for brand in list(brand_share['brands'][:5])}
            }

        # Top50 產品
        top50_products = self._get_top50_products()

        return {
            'sales_trend': sales_trend,
            'price_trend': price_trend,
            'price_dist': price_dist,
            'rating_dist': rating_dist,
            'brand_share': brand_share,
            'seller_source': seller_source,
            'brand_rating_trend': brand_rating_trend,
            'top50_products': top50_products
        }

    def _load_trend_data(self) -> Optional[Dict]:
        """從 trend_data.json 載入趨勢資料"""
        trend_file = self.output_dir / 'trend_data.json'
        if trend_file.exists():
            try:
                with open(trend_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"讀取趨勢資料失敗: {e}")
        return None

    def _get_price_distribution(self) -> List[Dict]:
        """獲取價格分佈資料"""
        ranges = [
            {'name': '超低價($0-50)', 'min': 0, 'max': 50},
            {'name': '低價($50-150)', 'min': 50, 'max': 150},
            {'name': '中價($150-300)', 'min': 150, 'max': 300},
            {'name': '高價($300-500)', 'min': 300, 'max': 500},
            {'name': '超高價($500+)', 'min': 500, 'max': float('inf')},
        ]

        result = []
        for r in ranges:
            count = sum(1 for p in self.products if r['min'] <= self._safe_float(p.get('價格', p.get('price', 0))) < r['max'])
            result.append({'value': count, 'name': r['name']})

        return result

    def _get_rating_distribution(self) -> Dict:
        """獲取評分分佈資料"""
        ranges = [
            {'min': 0, 'max': 3.5, 'label': '低分(<3.5)'},
            {'min': 3.5, 'max': 4.0, 'label': '中低分(3.5-4.0)'},
            {'min': 4.0, 'max': 4.3, 'label': '中等(4.0-4.3)'},
            {'min': 4.3, 'max': 4.7, 'label': '中高分(4.3-4.7)'},
            {'min': 4.7, 'max': 5.0, 'label': '高分(4.7+)'},
        ]

        ranges_data = [r['label'] for r in ranges]
        counts = []

        for r in ranges:
            count = sum(1 for p in self.products if r['min'] <= self._safe_float(p.get('評分', p.get('rating', 0))) < r['max'])
            counts.append(count)

        return {'ranges': ranges_data, 'counts': counts}

    def _get_brand_share_data(self) -> Dict:
        """獲取品牌份額資料"""
        brands = {}
        for p in self.products:
            brand = p.get('品牌', p.get('brand', 'Unknown'))
            revenue = self._safe_float(p.get('月銷額', p.get('monthly_revenue', 0)))
            if revenue == 0:
                price = self._safe_float(p.get('價格', p.get('price', 0)))
                sales = self._safe_int(p.get('月銷量', p.get('monthly_sales', 0)))
                revenue = price * sales
            brands[brand] = brands.get(brand, 0) + revenue

        # 排序並取 Top10
        sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]

        total_revenue = sum(share for _, share in sorted_brands) if sorted_brands else 1

        return {
            'brands': [brand for brand, _ in sorted_brands],
            'shares': [round(share / total_revenue * 100, 1) for _, share in sorted_brands]
        }

    def _get_seller_source_data(self) -> List[Dict]:
        """獲取賣家來源資料"""
        sources = {}
        for p in self.products:
            source = p.get('賣家來源', p.get('seller_source', '其他'))
            sources[source] = sources.get(source, 0) + 1

        return [{'value': count, 'name': source} for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)]

    def _get_top50_products(self) -> List[Dict]:
        """獲取 Top50 產品資料"""
        result = []
        for i, p in enumerate(self.products[:50], 1):
            price = self._safe_float(p.get('價格', p.get('price', 0)))
            sales = self._safe_int(p.get('月銷量', p.get('monthly_sales', 0)))
            total_revenue = sum(self._safe_float(pp.get('價格', pp.get('price', 0))) * self._safe_int(pp.get('月銷量', pp.get('monthly_sales', 0))) for pp in self.products)

            market_share = (price * sales / total_revenue * 100) if total_revenue > 0 else 0

            result.append({
                'asin': p.get('ASIN', p.get('asin', '')),
                'title': p.get('標題', p.get('title', ''))[:80],
                'brand': p.get('品牌', p.get('brand', '')),
                'price': round(price, 2),
                'rating': round(self._safe_float(p.get('評分', p.get('rating', 0))), 1),
                'sales': sales,
                'marketShare': round(market_share, 2)
            })

        return result

    def _create_overview_sheet(self, wb, Font):
        """建立概覽工作表"""
        ws = wb.create_sheet("概覽")

        # 標題
        ws['A1'] = f"{self._get_category_name()} 品類選品分析報告"
        ws['A1'].font = Font(bold=True, size=16)
        ws.merge_cells('A1:D1')

        # 日期
        ws['A2'] = f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        row = 4

        # 五維評分
        ws[f'A{row}'] = "五維評分"
        ws[f'A{row}'].font = Font(bold=True)
        row += 1

        max_scores = {'市場規模': 20, '增長潛力': 25, '競爭烈度': 20, '進入壁壘': 20, '利潤空間': 15}
        for key, max_score in max_scores.items():
            score = self.scores.get(key, 0)
            ws[f'A{row}'] = key
            ws[f'B{row}'] = score
            ws[f'C{row}'] = max_score
            ws[f'D{row}'] = f"{score/max_score*100:.1f}%"
            row += 1

        row += 1
        ws[f'A{row}'] = "總分"
        ws[f'A{row}'].font = Font(bold=True)
        ws[f'B{row}'] = self.scores.get('總分', 0)
        ws[f'C{row}'] = 100

        row += 1
        ws[f'A{row}'] = "評級"
        ws[f'B{row}'] = self.scores.get('評級', '')

    def _create_products_sheet(self, wb, Font, PatternFill):
        """建立產品列表工作表"""
        ws = wb.create_sheet("產品列表")

        # 表頭
        headers = ['排名', 'ASIN', '品牌', '標題', '價格', '月銷量', '評分']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

        # 資料
        for row_idx, product in enumerate(self.products, 2):
            ws.cell(row=row_idx, column=1, value=row_idx - 1)
            ws.cell(row=row_idx, column=2, value=product.get('ASIN', ''))
            ws.cell(row=row_idx, column=3, value=product.get('品牌', ''))
            ws.cell(row=row_idx, column=4, value=product.get('標題', '')[:50])
            ws.cell(row=row_idx, column=5, value=product.get('價格', 0))
            ws.cell(row=row_idx, column=6, value=product.get('月銷量', 0))
            ws.cell(row=row_idx, column=7, value=product.get('評分', 0))

    def _create_scores_sheet(self, wb, Font):
        """建立評分工作表"""
        ws = wb.create_sheet("評分詳情")

        # 表頭
        headers = ['維度', '得分', '滿分', '佔比']
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)

        # 資料
        max_scores = {'市場規模': 20, '增長潛力': 25, '競爭烈度': 20, '進入壁壘': 20, '利潤空間': 15}
        for row_idx, (key, max_score) in enumerate(max_scores.items(), 2):
            score = self.scores.get(key, 0)
            ws.cell(row=row_idx, column=1, value=key)
            ws.cell(row=row_idx, column=2, value=score)
            ws.cell(row=row_idx, column=3, value=max_score)
            ws.cell(row=row_idx, column=4, value=f"{score/max_score*100:.1f}%")

    def _get_default_markdown_template(self) -> str:
        """獲取預設 Markdown 模板"""
        return """# {{CATEGORY_NAME}} 品類選品分析報告

**生成時間**: {{DATE}} {{TIME}}
**資料來源**: Sorftime MCP

---

## 執行摘要

### 綜合評級: {{SCORE_評級}}

### 五維評分

| 維度 | 得分 | 滿分 |
|------|------|------|
| 市場規模 | {{SCORE_市場規模}} | 20 |
| 增長潛力 | {{SCORE_增長潛力}} | 25 |
| 競爭烈度 | {{SCORE_競爭烈度}} | 20 |
| 進入壁壘 | {{SCORE_進入壁壘}} | 20 |
| 利潤空間 | {{SCORE_利潤空間}} | 15 |
| **總分** | **{{SCORE_總分}}** | **100** |

---

## 市場資料

| 指標 | 數值 |
|------|------|
{% for key, value in statistics.items() %}| {{ key }} | {{ value }} |
{% endfor %}

---

## Top 產品列表

{{PRODUCTS_TABLE}}

---

## 資料說明

本報告基於 Sorftime MCP 實時資料生成，所有資料檔案儲存在 `data/` 目錄中。

- `statistics.csv` - 統計資料
- `products.csv` - 產品列表
- `scores.csv` - 評分詳情
- `raw_data.json` - 原始 JSON 資料

---

*報告自動生成於 {{DATE}}*
"""

    def _get_default_html_template(self) -> str:
        """獲取預設 HTML 模板"""
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{CATEGORY_NAME}} 品類選品分析</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #f5f7fa; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        h1 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .score-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .score-item { display: flex; justify-content: space-between; padding: 5px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{CATEGORY_NAME}} 品類選品分析報告</h1>
        <p>生成時間: {{DATE}}</p>

        <div class="score-card">
            <h2>五維評分</h2>
            <div id="scores"></div>
        </div>

        <h2>產品列表</h2>
        <table id="products-table">
            <thead>
                <tr>
                    <th>排名</th>
                    <th>ASIN</th>
                    <th>品牌</th>
                    <th>價格</th>
                    <th>月銷量</th>
                    <th>評分</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
    </div>

    <script>
        const scores = {{SCORES_JSON}};
        const products = {{PRODUCTS_JSON}};

        // 渲染評分
        const scoresDiv = document.getElementById('scores');
        const maxScores = {'市場規模': 20, '增長潛力': 25, '競爭烈度': 20, '進入壁壘': 20, '利潤空間': 15};
        for (const [key, score] of Object.entries(scores)) {
            if (key in maxScores) {
                const div = document.createElement('div');
                div.className = 'score-item';
                div.innerHTML = `<span>${key}</span><span>${score}/${maxScores[key]}</span>`;
                scoresDiv.appendChild(div);
            }
        }

        // 渲染產品
        const tbody = document.querySelector('#products-table tbody');
        products.slice(0, 20).forEach((p, i) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${i + 1}</td>
                <td>${p.ASIN || ''}</td>
                <td>${p.品牌 || ''}</td>
                <td>$${(p.價格 || 0).toFixed(2)}</td>
                <td>${(p.月銷量 || 0).toLocaleString()}</td>
                <td>${(p.評分 || 0).toFixed(1)}★</td>
            `;
            tbody.appendChild(tr);
        });
    </script>
</body>
</html>
"""


def main():
    """命令列入口"""
    if len(sys.argv) < 2:
        print("用法: python generate_reports.py <JSON資料檔案> [輸出目錄]")
        print("\n示例:")
        print("  python generate_reports.py parsed_data.json")
        print("  python generate_reports.py parsed_data.json ./reports")
        sys.exit(1)

    json_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    # 讀取資料
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 生成報告
    generator = CategoryReportGenerator(data, output_dir)
    results = generator.generate_all()

    print("\n" + "=" * 60)
    print("報告生成完成！")
    print("=" * 60)
    print(f"輸出目錄: {generator.output_dir}")
    print("\n生成的檔案:")
    for format_type, path in results.items():
        print(f"  [{format_type.upper()}] {path}")


if __name__ == "__main__":
    main()
