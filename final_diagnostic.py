# -*- coding: utf-8 -*-
import json, os, soundfile as sf

def diagnostic():
    json_path = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
    if not os.path.exists(json_path):
        print("❌ 找不到 JSON 文件")
        return

    with open(json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    print("\n" + "="*50)
    print("📋 汉化内容质量深度审计")
    print("="*50)

    for i in range(min(5, len(data))):
        item = data[i]
        print(f"【片段 {i}】")
        print(f"  原文: {item['text']}")
        print(f"  译文: {item.get('translated_text', 'N/A')}")
        
        dub_path = item.get('dub_path')
        if dub_path and os.path.exists(dub_path):
            stat = os.stat(dub_path)
            print(f"  音频: ✅ 已生成 ({stat.st_size / 1024:.1f} KB)")
        else:
            print(f"  音频: ❌ 缺失")
        print("-" * 30)

if __name__ == "__main__":
    diagnostic()
