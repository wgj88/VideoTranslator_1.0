# -*- coding: utf-8 -*-
import os, sys, soundfile as sf, numpy as np
import librosa, subprocess

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

def run_v31_test():
    print("\n[V31-Engine-Test] 正在使用【工业稳定版配置】进行实测...")
    db = VideoCloneDubber()
    
    # 种子
    seed_wav = r"E:\VideoTranslator_Project\temp_factory\GENE_CLEAN_SPEAKER_00.wav"
    seed_text = "Navigate through this year's Expo," # 之前识别出的真实台词
    
    test_zh = "带你逛今年博览会！"
    
    # 核心：使用新的 generate_safe (Temperature=0.01)
    print(f"  -> 正在以极低温度生成: {test_zh}")
    wav = db.generate_safe(text=test_zh, prompt_wav_path=seed_wav, prompt_text=seed_text)
    
    out_p = r"E:\VideoTranslator_Project\output_final\V31_STABLE_ENGINE_AUDIT.wav"
    sf.write(out_p, wav, db.sample_rate)
    print(f"\n🏆 稳定版引擎样本已产出：{out_p}")

if __name__ == "__main__":
    run_v31_test()
