# -*- coding: utf-8 -*-
import os, subprocess, librosa, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

def forensic_clean_seed():
    seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    clean_seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\V73_SURGICAL_SEED.wav"
    
    # 1. 载入种子并分析
    y, sr = sf.read(seed_p)
    duration = len(y)/sr
    
    print(f"\n[Forensic] 正在审计种子音频: {duration:.3f}s")
    
    # 2. 物理截击：切除种子末尾 0.2s 的潜在“呼吸音”
    # 大多数语气词幻觉都源自种子结尾的不干净
    new_dur = max(1.0, duration - 0.25) 
    
    # 3. 频谱洗消：执行高强度高通滤波，切除 120Hz 以下的呼吸重音
    # 并强制淡出，确保种子是以“绝对零分贝”结束的
    cmd = [
        FFMPEG_BIN, "-y", "-i", seed_p,
        "-af", f"atrim=end={new_dur},highpass=f=120,afade=t=out:st={new_dur-0.1}:d=0.1",
        clean_seed_p
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"✅ 种子手术完成：已移除末尾 250ms 风险区，并执行了 120Hz 呼吸隔离。")
    print(f"📂 新种子路径: {clean_seed_p}")

if __name__ == "__main__":
    forensic_clean_seed()
