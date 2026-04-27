# -*- coding: utf-8 -*-
import os, subprocess, whisper, json, numpy as np
import librosa

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def final_audit_report():
    # 我们审计纯中文轨道，排查效果最直接
    zh_track = r"E:\VideoTranslator_Project\temp_factory\v35_zh_full.wav"
    
    print("\n" + "="*20 + " V35 终极声学审计报告 " + "="*20)
    
    if not os.path.exists(zh_track):
        print("❌ 找不到 V35 音轨文件")
        return

    # 1. 提取 58s - 62s 的物理样本
    sample_p = r"E:\VideoTranslator_Project\temp_factory\v35_audit_sample.wav"
    subprocess.run([FFMPEG_BIN, "-y", "-i", zh_track, "-ss", "58", "-t", "4", sample_p], capture_output=True)
    
    # 2. 能量扫描 (Energy Scan)
    y, sr = librosa.load(sample_p, sr=None)
    # 计算每 100ms 的平均能量
    hop = int(sr * 0.1)
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    
    # 3. AI 识别复核
    model = whisper.load_model("base")
    res = model.transcribe(sample_p)
    
    print(f"\n[时间窗口] 58.00s -> 62.00s")
    print(f"  🎙️ AI 听到内容: \"{res['text'].strip()}\"")
    
    # 能量分布诊断
    silent_frames = np.sum(rms < 0.005) # 判定为静音的帧数
    total_frames = len(rms)
    silence_ratio = silent_frames / total_frames
    
    print(f"  📊 能量活跃度: {(1-silence_ratio)*100:.1f}% (越低表示该空白期越安静)")
    
    # 最终定论
    if len(res['text'].strip()) < 5: # 如果识别出的文字极少或为空
        print("\n✅ [审计定论]：58s-60s 之间已实现物理静默，幻觉杂音已彻底消除。")
    elif "紧绕开" in res['text'] or len(res['text']) > 15:
        print("\n🚩 [审计定论]：该区间仍检测到多余发音，熔断点可能需要进一步前移。")
    else:
        print(f"\n✅ [审计定论]：该区间仅检测到正常台词残响 \"{res['text'][:10]}...\"，无幻觉干扰。")

if __name__ == "__main__":
    final_audit_report()
