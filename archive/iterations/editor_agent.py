# -*- coding: utf-8 -*-
import json

class EditorAgent:
    def __init__(self, config_path="config_filter.json"):
        # 实际生产中这里会连接本地 LLM 或 API
        self.focus_areas = ["tech", "gadgets", "science", "facts", "creative"]

    def review(self, metadata):
        """
        模拟 LLM 审稿逻辑
        """
        title = metadata.get('title', '').lower()
        desc = metadata.get('description', '').lower()
        content = title + " " + desc
        
        # 简单的评分逻辑（模拟智能体思考）
        score = 50 
        reasons = []

        # 1. 领域匹配加分
        for area in self.focus_areas:
            if area in content:
                score += 15
                reasons.append(f"匹配关注领域: {area}")

        # 2. 独特性/新鲜度判断
        if "new" in content or "2026" in content or "first look" in content:
            score += 20
            reasons.append("具有时效性/首发价值")

        # 3. 汉化价值判断
        if "how to" in content or "review" in content:
            score += 10
            reasons.append("具有实用汉化价值")

        is_passed = score >= 70
        
        return {
            "passed": is_passed,
            "score": score,
            "reason": "; ".join(reasons) if reasons else "内容一般，暂不搬运"
        }
