# -*- coding: utf-8 -*-
import sys, os, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

def build_v8_loud():
    print("\n--- 🔊 正在构建【高增益】纯中文混音 ---")
    
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v7_pro_wavs"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    
    dub_files = []
    for i in range(10):
        p = os.path.join(audio_dir, f"aligned_{i}.wav")
        if os.path.exists(p): dub_files.append(p)

    # 第一步：先合并所有中文，并强制放大音量
    zh_only_wav = r"E:\VideoTranslator_Project\output_final\ZH_ONLY_BOOSTED.wav"
    zh_inputs = []
    for p in dub_files: zh_inputs.extend(["-i", p])
    
    # 物理叠加所有中文，并补偿 amix 导致的音量衰减
    filter_zh = f"amix=inputs={len(dub_files)}:duration=longest,volume={len(dub_files)}"
    subprocess.run([FFMPEG_BIN, "-y"] + zh_inputs + ["-filter_complex", filter_zh, zh_only_wav], check=True)
    
    # 第二步：将 BGM(5%) 与 中文(100%) 混合
    final_audio = r"E:\VideoTranslator_Project\output_final\FINAL_MIX_V8.wav"
    cmd_mix = [
        FFMPEG_BIN, "-y",
        "-i", zh_only_wav,
        "-i", bgm_file,
        "-filter_complex", "[0:a]volume=1.5[zh];[1:a]volume=0.05[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "[out]",
        final_audio
    ]
    subprocess.run(cmd_mix, check=True)

    # 第三步：封装回视频
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    final_video = r"E:\VideoTranslator_Project\output_final\V8_LOUD_CHINESE_FINAL.mp4"
    
    cmd_video = [
        FFMPEG_BIN, "-y",
        "-i", v_mp4,
        "-i", final_audio,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac",
        final_video
    ]
    subprocess.run(cmd_video, check=True)
    print(f"\n🏆 V8.0 高增益版交付：{final_video}")

if __name__ == "__main__":
    build_v8_loud()
