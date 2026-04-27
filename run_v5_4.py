# -*- coding: utf-8 -*-
import os, sys, subprocess, re, json, numpy as np
import soundfile as sf

# --- 环境 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v5_4_final():
    temp_dir = r"E:\VideoTranslator_Project\temp_factory"
    # 我们直接利用刚才已经生成好的、消过噪的物理片段
    # 它们保存在 E:\VideoTranslator_Project\temp_factory\clean_v5_3_*.wav
    
    zh_json = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140_zh.json"
    with open(zh_json, "r", encoding="utf-8-sig") as f: data = json.load(f)

    print(f"\n🚀 正在执行【V5.4 终极对齐】混音...")
    
    input_args = []
    filter_parts = []
    valid_count = 0
    
    for i in range(8):
        # 寻找对应的消噪片段
        seg_p = os.path.join(temp_dir, f"clean_v5_3_{i}.wav")
        if os.path.exists(seg_p):
            input_args.extend(["-i", seg_p])
            delay = int(data[i]['start'] * 1000)
            # --- 核心修复：为每一路输入应用物理延迟 ---
            filter_parts.append(f"[{valid_count}:a]adelay={delay}|{delay}[a{valid_count}]")
            valid_count += 1
    
    if valid_count == 0:
        print("❌ 错误：找不到消噪片段。")
        return

    # 构造合并滤镜
    mix_inputs = "".join([f"[a{k}]" for k in range(valid_count)])
    filter_complex = f"{';'.join(filter_parts)};{mix_inputs}amix=inputs={valid_count}:duration=longest,volume={valid_count}"
    
    output_wav = r"E:\VideoTranslator_Project\output_final\V5_4_PERFECT_ALIGNED.wav"
    
    cmd = [FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", filter_complex, output_wav]
    subprocess.run(cmd, check=True)
    
    print(f"\n🏆 V5.4 终极对齐版已产出：{output_wav}")
    print("这回每一句中文都会按照正确的时间顺序响起，且结尾干净利落。")

if __name__ == "__main__":
    run_v5_4_final()
