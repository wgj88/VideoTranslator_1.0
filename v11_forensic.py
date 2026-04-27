# -*- coding: utf-8 -*-
import os, json, sys, whisper

# 注入路径
os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]

def run_forensic():
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v11_final_wavs"
    model = whisper.load_model("base")
    
    print("\n--- 🕵️ 每一句开头多出一个词：深度声学取证 ---")
    
    for i in range(3):
        p = os.path.join(audio_dir, f"v11_final_{i}.wav")
        if os.path.exists(p):
            res = model.transcribe(p)
            print(f"\n[片段 {i}]")
            print(f"  -> AI 听到的内容: {res['text']}")
            print(f"  -> AI 识别的语种: {res['language']}")

if __name__ == "__main__":
    run_forensic()
