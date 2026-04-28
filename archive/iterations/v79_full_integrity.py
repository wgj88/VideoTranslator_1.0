# -*- coding: utf-8 -*-
import os, json, subprocess, time, requests, whisper
import numpy as np
import soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def generate_full_integrity_master():
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v79_full_run"
    os.makedirs(temp_dir, exist_ok=True)
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V77_BALANCED_SCRIPT.json"
    seed_p = r"E:\VideoTranslator_Project\unhinged_tech\seeds\V73_SURGICAL_SEED.wav"
    seed_text = "It's the year 2026. Your $3,500 smart fridge has a GPU and it's showing you ads."
    
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    print("\n" + "🔓"*10 + " V79 全保全流水线启动：取消一切截断 " + "🔓"*10)
    
    results = []
    for i, item in enumerate(data):
        text = item['zh'].strip()
        raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
        
        # 1. 生成 (维持 0.01 极低温)
        requests.post("http://127.0.0.1:8000/generate", json={
            "text": text + "。", 
            "ref_wav": seed_p,
            "prompt_text": seed_text,
            "save_path": raw_p
        }, timeout=100, proxies={"http": None, "https": None})
        
        # 2. 测量时长
        y, sr = sf.read(raw_p)
        actual_dur = len(y)/sr
        expected_dur = item['end'] - item['start']
        
        # 3. 仅执行调速防撞，绝不截断
        # 只有在音频真的比时间轴长时才加速，否则保持 1.0x
        tempo = max(1.0, actual_dur / expected_dur) if expected_dur > 0 else 1.0
        
        final_p = os.path.join(temp_dir, f"v79_full_{i}.wav")
        # 手术：移除 atrim，仅保留 atempo
        subprocess.run([
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atempo={tempo}",
            final_p
        ], capture_output=True)
        
        results.append((final_p, item['start']))
        print(f"  -> [{i+1}/25] 已保全输出 | 原始:{actual_dur:.2f}s | 压缩后:{actual_dur/tempo:.2f}s")

    # 4. 终极音频缝合
    temp_zh = os.path.join(temp_dir, "v79_master_zh.wav")
    input_args = []
    filter_parts = []
    for idx, (p, st) in enumerate(results):
        input_args.extend(["-i", p])
        delay = int(st * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}:duration=longest,volume={len(results)}"
    with open(os.path.join(temp_dir, "v79_mix.txt"), "w") as f: f.write(";".join(filter_parts) + ";" + mix_str)
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex_script", os.path.join(temp_dir, "v79_mix.txt"), temp_zh], check=True)

    # 5. 与 BGM 混音
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V79_FULL_INTEGRITY_MASTER_2MIN.wav"
    subprocess.run([FFMPEG_BIN, "-y", "-i", temp_zh, "-i", bgm, "-filter_complex", "[0:a]volume=1.5[zh];[1:a]atrim=end=120,volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first", output_wav], check=True)
    
    print(f"\n🏆 V79 全保全音频母带已产出：{output_wav}")

if __name__ == "__main__":
    generate_full_integrity_master()
