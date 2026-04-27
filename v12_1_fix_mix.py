# -*- coding: utf-8 -*-
import os, subprocess, json

def run_v12_1_fixed_mix():
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v12_wavs"
    output_wav = r"E:\VideoTranslator_Project\output_final\V12_1_FIXED_CHINESE_FINAL.wav"
    
    # 1. 物理检查并收集所有存在的配音片段
    valid_dubs = []
    for i in range(35): # 扫描足够广的范围
        p = os.path.join(audio_dir, f"aligned_{i}.wav")
        if os.path.exists(p):
            valid_dubs.append(p)
    
    if not valid_dubs:
        print("❌ 报错：在 E 盘目录下未找到任何 aligned_*.wav 配音片段！请检查配音阶段是否报错。")
        return

    print(f"\n[Mixer] 发现 {len(valid_dubs)} 个有效中文片段。正在执行【高保真物理合成】...")

    # 2. 步骤 A：将所有中文片段合并为一条独立总轨 (强制 48000Hz)
    temp_zh_total = r"E:\VideoTranslator_Project\temp_factory\v12_total_zh_track.wav"
    zh_inputs = []
    for d in valid_dubs: zh_inputs.extend(["-i", d])
    
    # 核心：使用 inputs=N 且 volume=N 抵消 amix 的自动缩减
    filter_zh = f"amix=inputs={len(valid_dubs)}:duration=longest,volume={len(valid_dubs)}"
    subprocess.run([ffmpeg_bin, "-y"] + zh_inputs + ["-filter_complex", filter_zh, "-ar", "48000", temp_zh_total], check=True)

    # 3. 步骤 B：将独立总轨与 BGM 混合 (带侧链压制)
    cmd_final = [
        ffmpeg_bin, "-y",
        "-i", temp_zh_total, # [0:a]
        "-i", bgm_file,      # [1:a]
        "-filter_complex", "[0:a]volume=2.0[zh];[1:a]volume=0.1[bg];[bg][zh]sidechaincompress=threshold=0.01:ratio=20:attack=10:release=200[mixed]",
        "-map", "[mixed]",
        "-ar", "48000",
        output_wav
    ]
    subprocess.run(cmd_final, check=True)
    
    print(f"\n🏆 V12.1 修复版音轨已产出：{output_wav}")
    print("这一次，中文配音被手动放大了 200%，且采样率已完全对齐。")

if __name__ == "__main__":
    run_v12_1_fixed_mix()
