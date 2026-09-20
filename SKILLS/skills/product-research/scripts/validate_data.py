#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
資料驗證指令碼 - 校驗 data.json 的欄位命名和資料一致性

使用方式:
    python scripts/validate_data.py path/to/data.json

驗證項:
    1. 欄位命名規範（禁止模糊的命名如 top3_concentration）
    2. 資料一致性（數值在合理範圍內）
    3. 必填欄位完整性
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


class DataValidator:
    """資料驗證器"""

    # 禁止的模糊欄位名
    FORBIDDEN_FIELDS = {
        'top3_concentration': '請使用 top3_product_concentration 或 top3_brand_concentration',
        'top10_concentration': '請使用 top10_product_concentration 或 top10_brand_concentration',
        'concentration': '請明確指定是產品還是品牌的集中度',
    }

    # 必填欄位
    REQUIRED_FIELDS = {
        'metadata': ['category', 'site', 'date'],
        'market_overview': [
            'top100_monthly_sales',
            'top100_monthly_revenue',
            'avg_price',
            'top3_brand_concentration',  # 明確是品牌集中度
        ],
    }

    # 數值範圍檢查
    RANGE_CHECKS = {
        'top3_product_concentration': (0, 1),
        'top3_brand_concentration': (0, 1),
        'top10_brand_concentration': (0, 1),
        'new_product_share': (0, 1),
        'avg_price': (0, 10000),
        'top100_monthly_sales': (0, 10000000),
        'top100_monthly_revenue': (0, 1000000000),
    }

    def __init__(self, data_path: str):
        """初始化驗證器"""
        self.data_path = Path(data_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.data: Dict = {}

    def load_data(self) -> bool:
        """載入資料檔案"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            return True
        except FileNotFoundError:
            self.errors.append(f"檔案不存在: {self.data_path}")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON 解析錯誤: {e}")
            return False

    def check_field_naming(self) -> bool:
        """檢查欄位命名規範"""
        passed = True

        def check_recursive(obj: Any, path: str = ""):
            nonlocal passed
            if isinstance(obj, dict):
                for key in obj.keys():
                    current_path = f"{path}.{key}" if path else key
                    # 檢查禁止的欄位名
                    if key in self.FORBIDDEN_FIELDS:
                        self.errors.append(
                            f"[命名錯誤] {current_path}: 使用了模糊的欄位名 '{key}'。"
                            f"{self.FORBIDDEN_FIELDS[key]}"
                        )
                        passed = False
                    # 遞迴檢查
                    check_recursive(obj[key], current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_recursive(item, f"{path}[{i}]")

        check_recursive(self.data)
        return passed

    def check_required_fields(self) -> bool:
        """檢查必填欄位"""
        passed = True

        for section, fields in self.REQUIRED_FIELDS.items():
            if section not in self.data:
                self.errors.append(f"[缺失] 缺少必要區塊: {section}")
                passed = False
                continue

            section_data = self.data[section]
            for field in fields:
                if field not in section_data:
                    self.errors.append(f"[缺失] {section}.{field} 是必填欄位")
                    passed = False

        return passed

    def check_value_ranges(self) -> bool:
        """檢查數值範圍"""
        passed = True

        def check_value(obj: Any, path: str = ""):
            nonlocal passed
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if key in self.RANGE_CHECKS and isinstance(value, (int, float)):
                        min_val, max_val = self.RANGE_CHECKS[key]
                        if not (min_val <= value <= max_val):
                            self.errors.append(
                                f"[範圍錯誤] {current_path} = {value}，"
                                f"應在 [{min_val}, {max_val}] 範圍內"
                            )
                            passed = False
                    check_value(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_value(item, f"{path}[{i}]")

        check_value(self.data)
        return passed

    def check_consistency(self) -> bool:
        """檢查資料一致性"""
        passed = True

        market = self.data.get('market_overview', {})

        # 檢查 Top3 品牌集中度是否合理
        top3_brand = market.get('top3_brand_concentration')
        top3_product = market.get('top3_product_concentration')

        if top3_brand and top3_product:
            if top3_brand < top3_product:
                self.warnings.append(
                    f"[一致性警告] top3_brand_concentration ({top3_brand:.2%}) "
                    f"小於 top3_product_concentration ({top3_product:.2%})，"
                    f"這通常不合理（品牌集中度應該 >= 產品集中度）"
                )

        # 檢查競品市場份額之和
        competitors = self.data.get('competitors', [])
        if competitors:
            total_share = 0
            for comp in competitors:
                share_str = comp.get('market_share', '0%')
                try:
                    share = float(share_str.replace('%', '')) / 100
                    total_share += share
                except (ValueError, AttributeError):
                    pass

            if total_share > 1.0:
                self.warnings.append(
                    f"[一致性警告] 競品市場份額之和 ({total_share:.1%}) 超過 100%"
                )

        return passed

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """執行完整驗證"""
        print(f"🔍 驗證資料檔案: {self.data_path}")
        print("-" * 50)

        # 載入資料
        if not self.load_data():
            return False, self.errors, self.warnings

        # 執行各項檢查
        checks = [
            ("欄位命名規範", self.check_field_naming),
            ("必填欄位", self.check_required_fields),
            ("數值範圍", self.check_value_ranges),
            ("資料一致性", self.check_consistency),
        ]

        all_passed = True
        for check_name, check_func in checks:
            passed = check_func()
            status = "✓" if passed else "✗"
            print(f"{status} {check_name}")
            if not passed:
                all_passed = False

        print("-" * 50)

        # 輸出警告
        if self.warnings:
            print("\n⚠️ 警告:")
            for warning in self.warnings:
                print(f"  - {warning}")

        # 輸出錯誤
        if self.errors:
            print("\n❌ 錯誤:")
            for error in self.errors:
                print(f"  - {error}")

        # 總結
        if all_passed and not self.warnings:
            print("\n✅ 所有驗證透過！")
        elif all_passed:
            print("\n⚠️ 驗證透過，但有警告需要關注")
        else:
            print(f"\n❌ 驗證失敗，發現 {len(self.errors)} 個錯誤")

        return all_passed, self.errors, self.warnings


def main():
    """命令列入口"""
    if len(sys.argv) < 2:
        print("用法: python validate_data.py <data.json 路徑>")
        sys.exit(1)

    data_path = sys.argv[1]
    validator = DataValidator(data_path)
    passed, errors, warnings = validator.validate()

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
