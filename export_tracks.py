# -*- coding: utf-8 -*-
import json, os, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

def export_separated_tracks():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    bgm_src = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    
    with open(script_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. 物理合成纯中文轨道 (不带 BGM)
    print("\n[Export] 正在提取纯中文配音音轨...")
    input_args = []
    filter_parts = []
    
    # 搜集所有 V20 净化后的片段
    valid_count = 0
    for i, item in enumerate(data):
        p = os.path.join(r"E:\VideoTranslator_Project\temp_factory\v20_final_wavs", f"v20_seg_{i}.wav")
        if os.path.exists(p):
            input_args.extend(["-i", p])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{valid_count}:a]adelay={delay}|{delay}[a{valid_count}]")
            valid_count += 1
    
    output_zh = r"E:\VideoTranslator_Project\output_final\PURE_CHINESE_V20_ONLY.wav"
    mix_str = "".join([f"[a{k}]" for k in range(valid_count)]) + f"amix=inputs={valid_count}:duration=longest,volume={valid_count}"
    
    cmd_zh = [FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_zh]
    subprocess.run(cmd_zh, check=True, capture_output=True)
    
    # 2. 准备纯背景音轨道 (直接从库中复制)
    import shutil
    output_bgm = r"E:\VideoTranslator_Project\output_final\PURE_BGM_TRACK.wav"
    shutil.copy(bgm_src, output_bgm)

    print(f"\n🏆 资产已物理分离：")
    print(f"  -> 纯中文轨道: {output_zh}")
    print(f"  -> 纯背景音轨: {output_bgm}")

if __name__ == "__main__":
    export_separated_tracks()
