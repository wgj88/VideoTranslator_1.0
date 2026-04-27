# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v46_emotional_fix():
    print(f"\n[V46-Smooth] 正在修正 1分15秒 的“惊叹音调突变”问题...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()

    # --- 核心改进：平滑化文本 ---
    # 去除极端的“哇”，改用引导性的“看呐”
    smooth_text = "看呐，它们动作完全同步，竟然还带按摩功能。"
    
    print(f"  -> 正在使用平滑文本渲染: {smooth_text}")
    
    # 渲染
    wav = db.model.generate(
        text=smooth_text + "。",
        reference_wav_path=seed['wav'],
        inference_timesteps=50,
        cfg_value=1.5 # 降低 CFG，减少情感波动
    )
    
    temp_p = r"E:\VideoTranslator_Project\temp_factory\v46_raw_emotional.wav"
    sf.write(temp_p, wav, db.sample_rate)
    
    # 物理加固：切除开头并执行高频压制
    output_wav = r"E:\VideoTranslator_Project\output_final\V46_SMOOTH_EMOTIONAL_AUDIT.wav"
    
    cmd_fix = [
        r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe",
        "-y", "-i", temp_p,
        "-af", "atrim=start=0.15,asetpts=PTS-STARTPTS,compand=0.3|0.3:1/-90/-90|-70/-70|-60/-20|0/-15,afade=t=in:st=0:d=0.1,afade=t=out:st=" + str(max(0, len(wav)/db.sample_rate-0.3)) + ":d=0.2",
        output_wav
    ]
    subprocess.run(cmd_fix, check=True, capture_output=True)
    
    print(f"✅ V46 救治完成。请试听这个平衡后的版本：{output_wav}")

if __name__ == "__main__":
    run_v46_emotional_fix()
