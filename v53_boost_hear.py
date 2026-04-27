# -*- coding: utf-8 -*-
import os, whisper, subprocess

os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]

def run_boosted_hearing():
    input_wav = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    boosted_wav = r"E:\VideoTranslator_Project\unhinged_tech\boosted_vocals.wav"
    
    # 物理拉升音量 10dB + 压缩器 (让微弱的人声跳出来)
    FFMPEG = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    subprocess.run([FFMPEG, "-y", "-i", input_wav, "-af", "volume=10dB,compand=attacks=0:points=-80/-80|-40/-15|-10/-1|0/0", boosted_wav], capture_output=True)

    print("\n--- 🎧 正在执行【信号增强】识别 (Base.en 模型) ---")
    model = whisper.load_model("base.en")
    
    # 扫前 30s
    audio = whisper.load_audio(boosted_wav); audio = whisper.pad_or_trim(audio, length=16000*30); res = model.transcribe(audio)
    
    print("\n[AI 增强回听结果]")
    print(f"  识别台词: \"{res['text'].strip()}\"")

if __name__ == "__main__":
    run_boosted_hearing()
