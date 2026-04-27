# -*- coding: utf-8 -*-
import sys, os, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

def build_ultimate():
    print("\n--- 🔨 正在构建绝对隔离的纯中文音轨 ---")
    
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v7_pro_wavs"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    
    # 找到所有的 aligned_*.wav
    dub_files = []
    for i in range(10):
        p = os.path.join(audio_dir, f"aligned_{i}.wav")
        if os.path.exists(p):
            dub_files.append(p)
            
    if not dub_files:
        print("❌ 找不到配音文件！")
        return

    # --- 步骤 1：只合成音频，绝对不引入原视频文件！ ---
    # 这样 FFmpeg 就绝对不可能去抓取原视频里的英文音轨了
    pure_audio_out = r"E:\VideoTranslator_Project\output_final\PURE_CHINESE_MIX.wav"
    
    input_args = ["-i", bgm_file] # [0:a] is BGM
    for p in dub_files:
        input_args.extend(["-i", p]) # [1:a], [2:a]... are dubs

    dub_inputs = "".join([f"[{k+1}:a]" for k in range(len(dub_files))])
    
    filter_complex = f"{dub_inputs}amix=inputs={len(dub_files)}:duration=longest,volume={len(dub_files)}[dub_mix];"
    filter_complex += f"[0:a][dub_mix]sidechaincompress=threshold=0.01:ratio=20[bg_ducked];"
    filter_complex += f"[bg_ducked][dub_mix]amix=inputs=2:weights='0.2 1.0'[final_audio]"

    cmd_audio = [FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", filter_complex, "-map", "[final_audio]", pure_audio_out]
    
    print("[Action] 正在合成无污染的纯中文音轨...")
    subprocess.run(cmd_audio, check=True)
    
    # --- 步骤 2：将纯中文音轨与无声画面合并 ---
    print("\n[Action] 正在将音轨压入视频（丢弃原音轨）...")
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    final_video = r"E:\VideoTranslator_Project\output_final\ABSOLUTE_FINAL_CHINESE.mp4"
    
    cmd_video = [
        FFMPEG_BIN, "-y",
        "-i", v_mp4,          # Input 0: Video
        "-i", pure_audio_out, # Input 1: The pure Chinese audio we just made
        "-map", "0:v",        # Take only video from Input 0
        "-map", "1:a",        # Take audio from Input 1
        "-c:v", "copy",
        "-c:a", "aac",
        final_video
    ]
    subprocess.run(cmd_video, check=True)
    
    print(f"\n🏆 终极无污染大片已交付：{final_video}")

if __name__ == "__main__":
    build_ultimate()
