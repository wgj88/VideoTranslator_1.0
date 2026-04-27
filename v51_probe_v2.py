# -*- coding: utf-8 -*-
import os, whisper, torch

# 暴力注入路径
os.environ["PATH"] = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32" + os.pathsep + os.environ["PATH"]

def run():
    print("\n--- 🏁 V2 语种探测器启动 ---")
    input_wav = r"E:\VideoTranslator_Project\unhinged_tech\aligned_input.wav"
    
    if not os.path.exists(input_wav):
        print("❌ 文件不存在")
        return

    model = whisper.load_model("base")
    print("  -> 模型已加载。正在读取样本信号...")
    
    # 物理读取
    audio = whisper.load_audio(input_wav)
    audio = whisper.pad_or_trim(audio)
    
    # 转 mel
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    
    # 探测
    _, probs = model.detect_language(mel)
    
    print("\n[探测报告]")
    for lang, prob in sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {lang}: {prob*100:.2f}%")

if __name__ == "__main__":
    run()
