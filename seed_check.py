# -*- coding: utf-8 -*-
import os, sys, torch, soundfile as sf, numpy as np
import librosa, subprocess

# --- 物理路径补丁 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_seed_check():
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    import json
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    test_text = "这是一段测试克隆音质的句子，让我们看看开头和末尾是否有杂音渗漏。"
    
    print("\n[Seed-Check] 正在生成【原始无损】对比样本...")

    for spk, seed in role_lib.items():
        print(f"  -> 正在使用 {spk} 的种子进行渲染...")
        # 重点：100% 原始 generate，不加任何前后缀
        wav = db.model.generate(text=test_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
        
        out_p = f"E:\\VideoTranslator_Project\\output_final\\RAW_SEED_CHECK_{spk}.wav"
        sf.write(out_p, wav, db.sample_rate)
        print(f"     ✅ 样本已产出: {out_p}")

if __name__ == "__main__":
    run_seed_check()
