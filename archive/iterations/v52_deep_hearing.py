# -*- coding: utf-8 -*-
import os, whisper, torch

os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]

def run_deep_hearing():
    input_wav = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    print("\n--- 🎧 正在执行【深度听力】审计 (Medium 模型) ---")
    
    # 物理降噪：先洗一遍耳朵
    clean_wav = r"E:\VideoTranslator_Project\unhinged_tech\deep_clean_vocals.wav"
    import subprocess
    FFMPEG = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    subprocess.run([FFMPEG, "-y", "-i", input_wav, "-af", "afftdn=nf=-20,highpass=f=200", clean_wav], capture_output=True)

    # 使用 medium 模型进行攻坚 (不建议用 large，显存可能会爆)
    model = whisper.load_model("medium")
    
    print("  -> 正在对前 30 秒执行攻坚识别...")
    # 只扫前 30s
    res = model.transcribe(clean_wav, duration=30, verbose=True)
    
    print("\n[AI 深度回听结果]")
    print(f"  识别台词: {res['text']}")

if __name__ == "__main__":
    run_deep_hearing()
