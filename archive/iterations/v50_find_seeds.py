# -*- coding: utf-8 -*-
import json, os, subprocess

def find_seeds():
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\FINAL_CLEAN_SCRIPT.json"
    vocals_wav = r"E:\VideoTranslator_Project\unhinged_tech\separated\vocals.wav"
    output_lib = r"E:\VideoTranslator_Project\unhinged_tech\role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\unhinged_tech\seeds"
    os.makedirs(temp_dir, exist_ok=True)
    
    FFMPEG = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"

    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    role_lib = {}
    found_speakers = set(item['speaker'] for item in data)
    
    print(f"\n[Seed-Finder] 正在为 {len(found_speakers)} 个角色寻找基因种子...")

    for spk in found_speakers:
        # 寻找该角色的第一个长片段 (3-8秒)
        for item in data:
            if item['speaker'] == spk:
                dur = item['end'] - item['start']
                if 3.0 < dur < 10.0:
                    seed_wav = os.path.join(temp_dir, f"seed_{spk}.wav")
                    # 物理切割
                    subprocess.run([FFMPEG, "-y", "-i", vocals_wav, "-ss", str(item['start']), "-t", str(dur), "-ac", "1", seed_wav], capture_output=True)
                    role_lib[spk] = {
                        "wav": seed_wav,
                        "text": item['text']
                    }
                    print(f"  ✅ 锁定 {spk} 种子: {item['text'][:30]}...")
                    break
    
    with open(output_lib, "w", encoding="utf-8") as f:
        json.dump(role_lib, f, indent=2)
    print(f"\n🏆 角色基因库已就位：{output_lib}")

if __name__ == "__main__":
    find_seeds()
