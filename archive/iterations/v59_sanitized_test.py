# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

# --- 物理资产配置 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from v53_turbo_factory import TurboFactory

def run_sanitized_sample():
    print("\n" + "🧴"*10 + " 启动 V59 【无尘级】前 5 句样片渲染 " + "🧴"*10)
    
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_FINAL_506_SCRIPT.json"
    # 使用二次剥离后的纯净人声作为种子来源
    ultra_vocal = r"E:\VideoTranslator_Project\unhinged_tech\separated_ultra\ULTRA_CLEAN_VOCALS.wav"
    
    with open(script_p, "r", encoding="utf-8") as f: script_data = json.load(f)
    
    # 1. 重新提取“超净基因种子”
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    os.makedirs(os.path.dirname(seed_wav), exist_ok=True)
    # 取第一句对应的时间段作为种子
    start, end = script_data[0]['start'], script_data[0]['end']
    subprocess.run([FFMPEG_BIN, "-y", "-i", ultra_vocal, "-ss", str(start), "-t", str(end-start), "-ac", "1", seed_wav], check=True)
    print(f"  ✅ 超净基因已锁定：{seed_wav}")

    # 2. 局部生产 (前 5 句)
    tf = TurboFactory()
    # 截取前 5 句剧本
    temp_script_p = r"E:\VideoTranslator_Project\unhinged_tech\temp_v59_script.json"
    with open(temp_script_p, "w", encoding="utf-8") as f:
        json.dump(script_data[:5], f, indent=2)
    
    processed_results = tf.run_production(temp_script_p, seed_wav)

    # 3. 快速缝合
    print("\n[V59] 正在缝合首批“洗消版”配音...")
    output_wav = r"E:\VideoTranslator_Project\output_final\V59_SANITIZED_FRONT_5_AUDIT.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
    
    print(f"\n🏆 V59 预清洗样片已交付：{output_wav}")

if __name__ == "__main__":
    run_sanitized_sample()
