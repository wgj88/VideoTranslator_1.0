# -*- coding: utf-8 -*-
import os, sys, subprocess, json, numpy as np, soundfile as sf
import librosa

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v37_v2():
    print("\n--- 🕵️ V37.1 能量门限外科手术启动 ---")
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs\raw_12.wav"
    output_p = r"E:\VideoTranslator_Project\output_final\V37_VAD_PRECISION_AUDIT.wav"
    
    if not os.path.exists(raw_p):
        print("❌ 找不到原始生成片段")
        return

    # 1. 物理读取波形
    print("  -> 正在读取波形并扫描能量...")
    y, sr = librosa.load(raw_p, sr=None)
    
    # 2. 精准 VAD 探测
    # top_db=30: 只要声音比最大音量低 30分贝，就认为是结束
    intervals = librosa.effects.split(y, top_db=30)
    
    if len(intervals) > 0:
        # 取最后一个发音包的物理终点
        # 我们寻找整段音频中最后一个“活跃区域”
        true_end_sample = intervals[-1][1]
        true_end_time = true_end_sample / sr
        print(f"  🚩 [探测结果]：真人语音在 {true_end_time:.2f}s 处停止，之后均为无效幻觉。")
    else:
        true_end_time = len(y) / sr

    # 3. 执行“毫秒级熔断”
    # 增加 50ms 缓冲防止吞字
    cut_point = true_end_time + 0.05
    
    print(f"  -> 正在执行物理熔断 (截断点: {cut_point:.2f}s)...")
    cmd = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15:end={cut_point+0.15},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, cut_point-0.1)}:d=0.1",
        output_p
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    
    print(f"✅ V37.1 救治完成！")
    print(f"🏆 请去听一下这个没有任何多余后缀的版本：{output_p}")

if __name__ == "__main__":
    run_v37_v2()
