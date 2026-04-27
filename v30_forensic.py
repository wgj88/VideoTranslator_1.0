# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v30_forensic():
    print(f"\n[V30-Forensic] 正在进行全链路崩溃取证...")
    
    db = VideoCloneDubber()
    target_text = "这产品纯属忽悠，说什么能轻松把你家普通沙发椅变成按摩椅了。赶紧坐下吧！"
    
    # --- 样本 A: 官方预设音色 (排除种子干扰) ---
    print("  -> 正在生成样本 A (官方预设音色)...")
    wav_a = db.model.generate(text=target_text)
    sf.write(r"E:\VideoTranslator_Project\output_final\V30_TEST_A_BASE_VOICE.wav", wav_a, db.sample_rate)

    # --- 样本 B: 回退到最原始种子 (排除加工干扰) ---
    print("  -> 正在生成样本 B (回退原始种子)...")
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    # 使用最初那个带点杂音但逻辑完整的种子
    old_seed = role_lib['SPEAKER_00']['wav'] 
    old_text = role_lib['SPEAKER_00']['text']
    
    wav_b = db.model.generate(text=target_text, prompt_wav_path=old_seed, prompt_text=old_text)
    sf.write(r"E:\VideoTranslator_Project\output_final\V30_TEST_B_ORIGINAL_SEED.wav", wav_b, db.sample_rate)
    
    print(f"\n🏆 取证样本已产出：")
    print(f"  A (官方音色): V30_TEST_A_BASE_VOICE.wav")
    print(f"  B (原始种子): V30_TEST_B_ORIGINAL_SEED.wav")

if __name__ == "__main__":
    run_v30_forensic()
