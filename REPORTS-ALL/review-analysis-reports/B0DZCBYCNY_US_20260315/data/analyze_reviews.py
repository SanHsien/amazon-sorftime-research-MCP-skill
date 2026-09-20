#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""差評 6 維分析框架 - Insta360 X5 評論分析"""

import json
from collections import defaultdict
from datetime import datetime

# 產品資訊
PRODUCT_INFO = {
    "asin": "B0DZCBYCNY",
    "site": "US",
    "title": "Insta360 X5 - Waterproof 8K 360° Action Camera",
    "brand": "Insta360",
    "price": "$549.99",
    "rating": "4.60",
    "total_reviews": 1542,
    "negative_reviews_count": 45
}

# 6 大痛點的關鍵詞分類系統
PAIN_POINT_CATEGORIES = {
    "電子模組故障": {
        "keywords": [
            "battery", "charge", "charging", "power", "drain", "overheat", "hot",
            "usb", "connection", "connect", "bluetooth", "wifi", "app",
            "firmware", "update", "glitch", "freeze", "frozen", "crash",
            "anomaly", "fault", "defect", "broken", "dead", "won't turn on"
        ],
        "severity_keywords": {
            "high": ["won't turn on", "dead", "fire", "smoke", "burning", "shock", "fault", "anomaly", "broken"],
            "medium": ["drain", "overheat", "freeze", "crash", "connection"],
            "low": ["slow", "delay", "lag"]
        }
    },
    "結構/組裝問題": {
        "keywords": [
            "lens", "scratch", "crack", "broken", "loose", "wobble", "rattle",
            "seal", "waterproof", "water", "leak", "moisture", "dust",
            "button", "stuck", "hard to press", "click", "switch",
            "mount", "attach", "tripod", "stand", "holder",
            "assembly", "fit", "gap", "misaligned"
        ],
        "severity_keywords": {
            "high": ["leak", "water damage", "broken", "crack", "won't close"],
            "medium": ["loose", "wobble", "stuck", "hard to"],
            "low": ["scratch", "cosmetic", "minor"]
        }
    },
    "設計/功能缺陷": {
        "keywords": [
            "software", "app", "edit", "editing", "watermark", "cloud", "subscription",
            "complicated", "difficult", "confusing", "intuitive", "user friendly",
            "stitching", "stitch", "quality", "grainy", "noisy", "low light",
            "horizon", "level", "stabilization", "shake", "jitter",
            "workflow", "process", "export", "render", "slow",
            "feature", "missing", "lack", "should", "expect"
        ],
        "severity_keywords": {
            "high": ["impossible", "unusable", "won't work", "can't", "broken"],
            "medium": ["difficult", "complicated", "confusing", "time consuming"],
            "low": ["could be better", "wish", "prefer"]
        }
    },
    "外觀/材質問題": {
        "keywords": [
            "smell", "odor", "chemical", "cheap", "plastic", "flimsy",
            "color", "different", "not as shown", "misleading",
            "scratch", "scuff", "mark", "dent", "cosmetic",
            "texture", "feel", "grip", "slippery"
        ],
        "severity_keywords": {
            "high": ["smell", "allergic", "reaction", "toxic"],
            "medium": ["cheap", "flimsy", "different"],
            "low": ["minor scratch", "cosmetic"]
        }
    },
    "描述不符": {
        "keywords": [
            "not as described", "different", "misleading", "expect", "expected",
            "advertisement", "claimed", "promised", "should",
            "size", "bigger", "smaller", "larger", "dimension",
            "feature", "missing feature", "doesn't have", "not included",
            "compatibility", "not compatible", "won't work with"
        ],
        "severity_keywords": {
            "high": ["completely different", "wrong", "false advertising"],
            "medium": ["not as expected", "different than"],
            "low": ["slight difference", "minor variation"]
        }
    },
    "服務/物流問題": {
        "keywords": [
            "used", "dirty", "gross", "ear wax", "dirt", "opened", "previous owner", "returned",
            "missing", "no cord", "no cable", "no charger", "no accessory",
            "return", "refund", "exchange", "difficult", "challenging",
            "customer service", "seller", "vendor", "support", "response",
            "shipping", "delivery", "package", "packaging", "box",
            "wrong item", "wrong color", "wrong size", "sent wrong"
        ],
        "severity_keywords": {
            "high": ["used", "dirty", "gross", "ear wax", "missing", "no cord"],
            "medium": ["return", "refund", "customer service", "wrong"],
            "low": ["shipping", "delivery", "package"]
        }
    }
}

# 服務維度細分關鍵詞
SERVICE_SUBCATEGORIES = {
    "收到二手/瑕疵品": ["used", "dirty", "gross", "ear wax", "dirt", "opened", "previous owner", "returned", "refurbished"],
    "配件缺失": ["missing", "no cord", "no cable", "no charger", "no ear tip", "no accessory", "incomplete"],
    "退換貨困難": ["return", "refund", "exchange", "difficult", "challenging", "hassle", "complicated"],
    "客服問題": ["customer service", "seller", "vendor", "support", "response", "reply", "contact"],
    "物流問題": ["shipping", "delivery", "package", "packaging", "box", "damaged box"],
    "發錯貨": ["wrong item", "wrong color", "wrong size", "sent wrong", "incorrect"]
}

def classify_review_severity(review_text, category_keywords):
    """判斷評論的嚴重程度"""
    text_lower = review_text.lower()

    # 檢查高嚴重程度關鍵詞
    for kw in category_keywords.get("high", []):
        if kw.lower() in text_lower:
            return "高"

    # 檢查中等嚴重程度
    for kw in category_keywords.get("medium", []):
        if kw.lower() in text_lower:
            return "中"

    # 檢查低嚴重程度
    for kw in category_keywords.get("low", []):
        if kw.lower() in text_lower:
            return "低"

    # 預設中等
    return "中"

def classify_review(review):
    """對單條評論進行分類，返回主要類別和次要類別"""
    text = f"{review.get('標題', '')} {review.get('評論', '')}".lower()
    categories = defaultdict(list)

    for category, config in PAIN_POINT_CATEGORIES.items():
        for keyword in config["keywords"]:
            if keyword.lower() in text:
                categories[category].append(keyword)

    # 確定主要類別（關鍵詞最多的）
    if categories:
        primary = max(categories.items(), key=lambda x: len(x[1]))
        return {
            "primary": primary[0],
            "secondary": list(categories.keys()),
            "matched_keywords": primary[1]
        }

    return {"primary": "其他", "secondary": [], "matched_keywords": []}

def analyze_service_issues(review_text):
    """分析服務維度問題細分"""
    text_lower = review_text.lower()
    subcategories = []

    for subcat, keywords in SERVICE_SUBCATEGORIES.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                subcategories.append(subcat)
                break

    return subcategories

# 主分析流程
def main():
    # 讀取解析後的評論
    with open("D:/amazon-mcp/review-analysis-reports/B0DZCBYCNY_US_20260315/data/parsed_reviews.json", 'r', encoding='utf-8') as f:
        reviews = json.load(f)

    print(f"開始分析 {len(reviews)} 條差評...\n")

    # 初始化分析結果
    analysis = {
        "product_info": PRODUCT_INFO,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pain_points": defaultdict(lambda: {
            "count": 0,
            "percentage": 0,
            "severity": {"高": 0, "中": 0, "低": 0},
            "reviews": [],
            "service_subcategories": defaultdict(int)
        })
    }

    # 分析每條評論
    for review in reviews:
        classification = classify_review(review)
        primary_category = classification["primary"]

        # 獲取評論文字
        review_text = f"{review.get('標題', '')} {review.get('評論', '')}"

        # 判斷嚴重程度
        severity = classify_review_severity(
            review_text,
            PAIN_POINT_CATEGORIES.get(primary_category, {}).get("severity_keywords", {})
        )

        # 記錄分析結果
        analysis["pain_points"][primary_category]["count"] += 1
        analysis["pain_points"][primary_category]["severity"][severity] += 1
        analysis["pain_points"][primary_category]["reviews"].append({
            "star": review.get('評星', 'N/A'),
            "title": review.get('標題', ''),
            "comment": review.get('評論', ''),
            "date": review.get('評論日期', ''),
            "severity": severity,
            "matched_keywords": classification["matched_keywords"]
        })

        # 如果是服務問題，進一步細分
        if primary_category == "服務/物流問題":
            subcats = analyze_service_issues(review_text)
            for subcat in subcats:
                analysis["pain_points"][primary_category]["service_subcategories"][subcat] += 1

    # 計算百分比
    total = len(reviews)
    for category, data in analysis["pain_points"].items():
        data["percentage"] = round((data["count"] / total) * 100, 1)

    # 轉換為普通字典以便 JSON 序列化
    pain_points_dict = {}
    for category, data in analysis["pain_points"].items():
        pain_points_dict[category] = {
            "count": data["count"],
            "percentage": data["percentage"],
            "severity": dict(data["severity"]),
            "reviews": data["reviews"],
            "service_subcategories": dict(data["service_subcategories"])
        }

    analysis["pain_points"] = pain_points_dict

    # 儲存分析結果
    output_file = "D:/amazon-mcp/review-analysis-reports/B0DZCBYCNY_US_20260315/data/negative_reviews_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # 列印摘要
    print("=" * 60)
    print("痛點分析摘要")
    print("=" * 60)
    sorted_pain_points = sorted(
        analysis["pain_points"].items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )
    for i, (category, data) in enumerate(sorted_pain_points, 1):
        print(f"{i}. {category}: {data['count']}條 ({data['percentage']}%)")
        print(f"   嚴重程度: 高{data['severity']['高']} | 中{data['severity']['中']} | 低{data['severity']['低']}")
        if data.get('service_subcategories'):
            print(f"   服務細分: {dict(data['service_subcategories'])}")

    print(f"\n分析完成！結果已儲存到: {output_file}")
    return analysis

if __name__ == "__main__":
    analysis = main()
