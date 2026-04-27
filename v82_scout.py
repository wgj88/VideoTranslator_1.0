# -*- coding: utf-8 -*-
import librosa
import numpy as np
import json, os

def scout_prosody():
    print("\n" + "🔍"*10 + " 启动 V82 声学侦察兵 " + "🔍"*10)
    
    # 物理资产：原始英文人声轨
    vocal_p = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    y, sr = librosa.load(vocal_p)
    
    # 读取英文原始剧本（带时间戳）
    with open(r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json", "r", encoding="utf-8") as f: en_data = json.load(f)
    
    report = []
    print(f"  -> 正在分析原片前 5 段的‘语速性格’...")

    for i in range(5):
        item = en_data[i]
        start_i, end_i = int(item['start']*sr), int(item['end']*sr)
        chunk = y[start_i:end_i]
        
        # 1. 计算英文语速 (Words Per Second)
        word_count = len(item['text'].split())
        dur = item['end'] - item['start']
        wps = word_count / dur
        
        # 2. 计算能量强度 (RMS)
        rms = np.sqrt(np.mean(chunk**2))
        
        # 3. 判定性格
        vibe = "平稳"
        if wps > 4.5: vibe = "急促吐槽"
        elif wps < 2.5: vibe = "深沉/延长"
        if rms > 0.08: vibe += "+高能强调"

        print(f"  [{i+1}] 语速:{wps:.1f} WPS | 能量:{rms:.3f} | 判定:【{vibe}】")
        report.append({"id": i+1, "vibe": vibe, "en_text": item['text']})

    # 保存这份简报
    with open(r"E:\VideoTranslator_Project\unhinged_tech\V82_VIBE_REPORT.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scout_prosody()
