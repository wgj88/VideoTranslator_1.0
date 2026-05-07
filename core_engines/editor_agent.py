# -*- coding: utf-8 -*-
class EditorAgent:
    def __init__(self):
        self.focus_areas = ["bizarre", "extreme", "tribal", "weird", "survival", "ancient"]

    def review(self, metadata):
        title = metadata.get('title', '').lower()
        desc = metadata.get('description', '').lower()
        content = title + " " + desc
        
        score = 50
        reasons = []

        # 核心猎奇题材加分
        bizarre_words = ["bizarre", "weird", "insane", "shocking", "extreme", "gross", "rare"]
        if any(w in content for w in bizarre_words):
            score += 30; reasons.append("具备极强视觉猎奇/冲击力")
            
        # 非洲/部落特色加分
        if any(w in content for w in ["africa", "tribe", "village", "bush"]):
            score += 25; reasons.append("深度异域文化特色")
            
        # 实用性/故事性
        if "recipe" in content or "how to" in content:
            score += 10; reasons.append("具有配方参考价值")

        return {
            "passed": score >= 70,
            "score": score,
            "reason": "; ".join(reasons) if reasons else "普通美食内容"
        }
