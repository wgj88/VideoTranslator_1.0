# -*- coding: utf-8 -*-
import json

def audit():
    path = r"E:\VideoTranslator_Project\separated_audio\V11_PRODUCTION_READY.json"
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    
    print("\n--- 📝 汉化剧本标点符号审计清单 ---")
    for i in range(min(10, len(data))):
        print(f"[{i:02d}] {data[i]['zh']}")

if __name__ == "__main__":
    audit()
