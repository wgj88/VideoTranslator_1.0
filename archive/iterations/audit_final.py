# -*- coding: utf-8 -*-
import os, sys, whisper
os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32;" + os.environ.get("PATH", "")

def audit():
    print("--- 🕵️ 终极声学审计 ---")
    model = whisper.load_model("base")
    
    dub_file = r"E:\VideoTranslator_Project\temp_factory\v7_pro_wavs\aligned_0.wav"
    if os.path.exists(dub_file):
        print(f"\n[Audit] 正在听译配音文件: {os.path.basename(dub_file)}")
        res = model.transcribe(dub_file)
        print(f"  -> 语言: {res['language']}")
        print(f"  -> 内容: {res['text']}")
    else:
        print("❌ 找不到配音文件")

    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    if os.path.exists(bgm_file):
        print(f"\n[Audit] 正在听译BGM文件 (前30秒): {os.path.basename(bgm_file)}")
        res = model.transcribe(bgm_file)
        print(f"  -> 语言: {res['language']}")
        print(f"  -> 内容: {res['text']}")
    else:
        print("❌ 找不到BGM文件")

if __name__ == "__main__":
    audit()
