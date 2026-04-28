# -*- coding: utf-8 -*-
import os, sys, subprocess, numpy as np
import soundfile as sf

# 物理注入 FFmpeg
ffmpeg_bin_dir = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32"
os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ["PATH"]

work_dir = r"E:\VideoTranslator_Project\FINAL_DUB_TEMP"
out_p = r"E:\VideoTranslator_Project\output_final\PURE_DUB_AUDIT.wav"

def simple_merge():
    print("\n--- 正在物理合并 8 个原始片段 ---")
    all_audio = []
    sr = 48000
    
    for i in range(8):
        p = os.path.join(work_dir, f"pure_zh_{i}.wav")
        if os.path.exists(p):
            # 使用 soundfile 读取，如果 soundfile 坏了，这里会报错
            try:
                data, sr = sf.read(p)
                all_audio.append(data)
                print(f"  [Merge] 已加入片段 {i}: {len(data)} 采样点")
            except:
                print(f"  [Error] 无法读取片段 {i}，可能是文件损坏。")
    
    if all_audio:
        combined = np.concatenate(all_audio)
        sf.write(out_p, combined, sr)
        print(f"\n🏆 合并完成！请听听这个文件是否有中文：{out_p}")
    else:
        print("❌ 没有任何有效音频片段。")

if __name__ == "__main__":
    simple_merge()
