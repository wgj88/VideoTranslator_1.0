# -*- coding: utf-8 -*-
import json, os, subprocess

def run_reconfirm():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 搜集 V27 的片段
    valid_dubs = []
    for i, item in enumerate(data):
        p = os.path.join(r"E:\VideoTranslator_Project\temp_factory\v27_final_wavs", f"v27_seg_{i}.wav")
        if os.path.exists(p):
            item['current_p'] = p
            valid_dubs.append(item)

    print(f"\n[Reconfirm] 正在合成全篇 {len(valid_dubs)} 个片段的 V27 音轨...")

    temp_zh = r"E:\VideoTranslator_Project\temp_factory\v27_reconfirm_zh.wav"
    input_args = []
    filter_parts = []
    for i, item in enumerate(valid_dubs):
        input_args.extend(["-i", item['current_p']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{i}:a]adelay={delay}|{delay}[a{i}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest,volume={len(valid_dubs)}"
    subprocess.run([ffmpeg_bin, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    output_wav = r"E:\VideoTranslator_Project\output_final\RECONFIRM_V27_AUDIT.wav"
    cmd_final = [
        ffmpeg_bin, "-y", "-i", temp_zh, "-i", bgm_file,
        "-filter_complex", "[0:a]volume=1.4[zh];[1:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_final, check=True, capture_output=True)
    print(f"\n🏆 V27 确认版音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_reconfirm()
