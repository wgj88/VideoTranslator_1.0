# -*- coding: utf-8 -*-
import os, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_deep_sanitization():
    input_wav = r"E:\VideoTranslator_Project\unhinged_tech\aligned_input.wav"
    # 净化目标：产出一个“临床级纯净”的源文件，再喂给 Demucs
    sanitized_wav = r"E:\VideoTranslator_Project\unhinged_tech\CLINICAL_CLEAN_SOURCE.wav"
    
    print("\n" + "🧼"*10 + " 启动临床级预清洗流水线 " + "🧼"*10)
    
    # 组合拳滤镜逻辑：
    # 1. highpass: 过滤掉 80Hz 以下的物理振动
    # 2. afftdn: 采样级 FFT 降噪，nf=-30dB 深度
    # 3. gate: 噪声门，如果音量低于 -35dB 则判定为呼吸/噪音，直接强制静默
    filters = (
        "highpass=f=80,"
        "afftdn=nf=-30:tn=1,"
        "agate=threshold=0.015:attack=5:release=50:range=0"
    )
    
    cmd = [
        FFMPEG_BIN, "-y", "-i", input_wav,
        "-af", filters,
        sanitized_wav
    ]
    
    print(f"  -> 正在对全片执行深度波形洗消...")
    subprocess.run(cmd, check=True)
    
    print(f"\n✅ 预处理完成！")
    print(f"📂 纯净源文件：{sanitized_wav}")
    print(f"💡 建议下一步：将此文件重新喂给 Demucs，产出的 vocals.wav 将拥有前所未有的透明度。")

if __name__ == "__main__":
    run_deep_sanitization()
