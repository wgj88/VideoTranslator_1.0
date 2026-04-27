# -*- coding: utf-8 -*-
import json, re, os

class QualityGuard:
    def __init__(self, allowed_languages=["en", "zh"]):
        self.allowed_languages = allowed_languages
        self.max_garbage_ratio = 0.15

    def check_transcript(self, json_path):
        if not os.path.exists(json_path): return False, "文件不存在"
        
        try:
            with open(json_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
        except: return False, "读取失败"

        if not data or len(data) < 3: return False, "内容太少或为空"

        # 1. 乱码检测
        full_text = "".join([i['text'] for i in data])
        # 统计非标准字符
        junk = re.sub(r'[a-zA-Z0-9\s,.\'\"!?\u4e00-\u9fa5]', '', full_text)
        junk_ratio = len(junk) / (len(full_text) + 1)
        
        if junk_ratio > self.max_garbage_ratio:
            return False, f"乱码/杂质占比过高: {junk_ratio:.2%}"

        # 2. 重复性检测
        words = full_text.lower().split()
        for i in range(len(words)-10):
            if len(set(words[i:i+6])) == 1:
                return False, f"检测到 Whisper 死循环幻觉: {words[i]}"

        return True, "OK"

if __name__ == "__main__":
    print("QualityGuard Node Initialized.")
