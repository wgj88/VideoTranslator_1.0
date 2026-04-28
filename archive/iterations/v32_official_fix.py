# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf
import librosa

# 补丁
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_official_fix():
    print(f"\n[V32-Official] 正在使用 VoxCPM2 官方推荐参数进行重制...")
    db = VideoCloneDubber()
    
    # 种子
    seed_wav = r"E:\VideoTranslator_Project\temp_factory\GENE_CLEAN_SPEAKER_00.wav"
    
    # 我们测试那个“胡言乱语”的长句
    test_zh = "横跨制造、零售、美妆和农业的炫目科技产品正成为全场焦点！"
    
    print(f"  -> 正在使用 reference_wav_path (Timesteps=50) 生成...")
    # 核心改进：
    # 1. 使用 reference_wav_path 而非 prompt_wav_path
    # 2. 增加 timesteps 到 50
    # 3. 显式设置 cfg_value=2.0
    wav = db.model.generate(
        text=test_zh + "。",
        reference_wav_path=seed_wav,
        inference_timesteps=50,
        cfg_value=2.0
    )
    
    out_p = r"E:\VideoTranslator_Project\output_final\V32_OFFICIAL_PARAMS_AUDIT.wav"
    sf.write(out_p, wav, db.sample_rate)
    print(f"\n🏆 官方参数版已产出：{out_p}")

if __name__ == "__main__":
    run_official_fix()
