# -*- coding: utf-8 -*-
import json, os, subprocess

def run_full_mix():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V11_PRODUCTION_READY.json"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid_dubs = []
    for item in data:
        if 'dub_path' in item and os.path.exists(item['dub_path']):
            valid_dubs.append(item)

    print(f"\n[Mixer] 正在对全篇 {len(valid_dubs)} 个片段进行物理时序混音...")

    # 分两步：A. 合并所有中文 B. 叠加 BGM
    # 步骤 A：中文总轨
    temp_zh_full = r"E:\VideoTranslator_Project\temp_factory\v11_zh_full_track.wav"
    input_args = []
    filter_parts = []
    for i, item in enumerate(valid_dubs):
        input_args.extend(["-i", item['dub_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay}|{delay}[a{i}]")
    
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest,volume={len(valid_dubs)}"
    cmd_zh = [ffmpeg_bin, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh_full]
    subprocess.run(cmd_zh, check=True)

    # 步骤 B：最终混音
    output_wav = r"E:\VideoTranslator_Project\output_final\FULL_V11_FINAL_AUDIT.wav"
    cmd_final = [
        ffmpeg_bin, "-y",
        "-i", temp_zh_full,
        "-i", bgm_file,
        "-filter_complex", "[0:a]volume=1.2[zh];[1:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_final, check=True)
    print(f"\n🏆 全篇汉化音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_full_mix()
