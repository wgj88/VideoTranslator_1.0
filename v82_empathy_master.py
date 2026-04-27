# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time, threading, queue
import soundfile as sf
import whisper

# --- 环境资产锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import ProductionFactory

def run_v82_empathy_master():
    print("\n" + "🎭"*10 + " V82 共情表演版：巅峰音频压制 " + "🎭"*10)
    
    # 指向 V82 共情剧本
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V82_EMPATHY_SCRIPT.json"
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V82_EMPATHY_PEAK_SAMPLE.wav"
    
    # 1. 注入 5.06 CPS 的原始时间轴（由于 V82 剧本只有 ZH，我们要合并原始时间戳）
    with open(r"E:\VideoTranslator_Project\unhinged_tech\RAW_EN_SCRIPT.json", "r", encoding="utf-8") as f: raw_en = json.load(f)
    with open(script_p, "r", encoding="utf-8") as f: refined_zh = json.load(f)
    
    full_data = []
    for it in refined_zh:
        matching_en = next(e for e in raw_en if e['id'] == it['id']-1) # ID偏移修正
        full_data.append({
            "zh": it['zh'],
            "start": matching_en['start'],
            "end": matching_en['end']
        })

    # 2. 启动旗舰工厂 (45步高精 + 纳米审计)
    factory = ProductionFactory(batch_size=1)
    factory.get_smart_steps = lambda x: 45 # 既然是表演版，全量 45 步
    
    temp_json = r"E:\VideoTranslator_Project\unhinged_tech\v82_temp_full.json"
    with open(temp_json, "w", encoding="utf-8") as f: json.dump(full_data, f, indent=2)

    processed_results = factory.run_production(temp_json, seed_wav)

    # 3. 执行时序大缝合
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
    
    print(f"\n🏆 V82 共情巅峰版已就绪：{output_wav}")
    print(f"💡 细节：本版包含破折号长音触发、45步声纹细琢。")

if __name__ == "__main__":
    run_v82_empathy_master()
