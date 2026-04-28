# -*- coding: utf-8 -*-
import json, os, soundfile as sf
import numpy as np

def make_final_audit():
    final_json = r"E:\VideoTranslator_Project\separated_audio\V9_REBUILD_FINAL.json"
    output_wav = r"E:\VideoTranslator_Project\output_final\V9_DUAL_ROLE_FINAL_AUDIT.wav"
    
    with open(final_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    all_audio = []
    sr = 48000
    
    print("\n[Audit] 正在物理拼接多角色试听音轨...")
    for item in data:
        p = item.get('dub_path')
        if p and os.path.exists(p):
            wav, sr = sf.read(p)
            all_audio.append(wav)
            print(f"  + 加入了 [{item['speaker']}] 的片段")
            
    if all_audio:
        combined = np.concatenate(all_audio)
        sf.write(output_wav, combined, sr)
        print(f"\n🏆 终极多角色对比音轨已产出：{output_wav}")
        print("请听听看，这两个角色的音色是否已经被完美分开并各具特色。")
    else:
        print("❌ 没有任何配音片段。")

if __name__ == "__main__":
    make_final_audit()
