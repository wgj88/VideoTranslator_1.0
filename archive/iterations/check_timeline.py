# -*- coding: utf-8 -*-
import json, os

def check_timeline():
    path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    with open(path, "r", encoding="utf-8") as f: data = json.load(f)
    
    print("\n--- 📝 60s 前后片段时序表 ---")
    for i, item in enumerate(data):
        # 打印 50s 到 80s 之间的所有片段
        if 40.0 < item['start'] < 90.0:
            print(f"Line_{i:02d}: {item['start']:.2f}s -> {item['end']:.2f}s | 内容: {item['zh']}")

if __name__ == "__main__":
    check_timeline()
