# -*- coding: utf-8 -*-
import json, os, subprocess

def run_v12_mix():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    valid_dubs = [item for item in data if 'dub_path' in item and os.path.exists(item['dub_path'])]
    print(f"\n[V12-Mixer] 正在合成全篇 {len(valid_dubs)} 个片段的终极音轨...")

    # 第一步：物理拼接所有中文片段
    temp_zh_track = r"E:\VideoTranslator_Project\temp_factory\v12_zh_full_track.wav"
    input_args = []
    filter_parts = []
    for i, item in enumerate(valid_dubs):
        input_args.extend(["-i", item['dub_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay}|{delay}[a{i}]")
    
    zh_mix_str = "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest,volume={len(valid_dubs)}"
    cmd_zh = [ffmpeg_bin, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + zh_mix_str, temp_zh_track]
    subprocess.run(cmd_zh, check=True, capture_output=True)

    # 第二步：叠入 BGM
    output_wav = r"E:\VideoTranslator_Project\output_final\V12_ULTIMATE_AUDIT.wav"
    cmd_final = [
        ffmpeg_bin, "-y",
        "-i", temp_zh_track,
        "-i", bgm_file,
        "-filter_complex", "[0:a]volume=1.3[zh];[1:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_final, check=True, capture_output=True)
    print(f"\n🏆 V12 终极试听音轨已就绪：{output_wav}")

if __name__ == "__main__":
    run_v12_mix()
