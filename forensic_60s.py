# -*- coding: utf-8 -*-
import json, os, whisper, subprocess

def forensic_60s():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V34_CRISP_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs"
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. 寻找 60s 附近的片段 (通常是 Seg 15-20 左右)
    print("\n--- 🔍 正在检索 60s 附近的技术资产 ---")
    targets = [i for i, d in enumerate(data) if 50.0 < d['start'] < 75.0]
    
    model = whisper.load_model("base")
    
    for idx in targets:
        item = data[idx]
        p = os.path.join(audio_dir, f"v34_seg_{idx}.wav")
        print(f"\n[片段 {idx}] 时间轴: {item['start']:.2f}s -> {item['end']:.2f}s")
        print(f"  设定台词: {item['zh']}")
        
        if os.path.exists(p):
            # 物理回听：AI 到底在这段音频里录进了什么？
            res = model.transcribe(p)
            print(f"  🎙️ AI 实际听到: {res['text']}")
            
            # 如果实际听到的文字远多于设定台词，那就是生成幻觉
            if len(res['text']) > len(item['zh']) + 10:
                print("  🚩 [判定]：检测到生成层幻觉 (Hallucination)！")
        else:
            print("  ⚠️ 物理音频丢失。")

if __name__ == "__main__":
    forensic_60s()
