# -*- coding: utf-8 -*-
import os, subprocess, whisper, json

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def analyze_60s_gap():
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm_wav = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_dir = r"E:\VideoTranslator_Project\output_final"
    
    print("\n--- 🔍 正在执行 60s 节点物理取证 ---")
    
    # 1. 提取原视频 55s-75s 的音频
    orig_clip = os.path.join(output_dir, "FORENSIC_ORIG_60s.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", v_mp4, "-ss", "55", "-t", "20", "-ac", "1", orig_clip], capture_output=True)
    
    # 2. 提取 pure_bgm 55s-75s 的音频 (核查是否有残留英文)
    bgm_clip = os.path.join(output_dir, "FORENSIC_BGM_RESIDUE_60s.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", bgm_wav, "-ss", "55", "-t", "20", "-ac", "1", bgm_clip], capture_output=True)
    
    # 3. 使用 AI 审计这两段波形
    model = whisper.load_model("base")
    
    print("\n[结果 A] 原视频在此区间的台词：")
    res_orig = model.transcribe(orig_clip)
    print(f"  -> {res_orig['text']}")
    
    print("\n[结果 B] 背景音轨道在此区间是否存在人声残留：")
    res_bgm = model.transcribe(bgm_clip)
    if len(res_bgm['text'].strip()) > 5:
        print(f"  🚩 发现残留人声: {res_bgm['text']}")
        print("  🚩 [结论]：那是剥离不干净的英文原音漏到了背景里。")
    else:
        print("  ✅ 背景音非常纯净。")

if __name__ == "__main__":
    analyze_60s_gap()
