# -*- coding: utf-8 -*-
import json, os, subprocess

def run_unhinged_finale():
    proj_dir = r"E:\VideoTranslator_Project\unhinged_tech"
    out_script = os.path.join(proj_dir, "UNHINGED_FINAL_SCRIPT.json")
    
    # 1. 物理合并
    with open(os.path.join(proj_dir, "PART1_ZH.json"), "r", encoding="utf-8") as f: p1 = json.load(f)
    with open(os.path.join(proj_dir, "PART2_ZH.json"), "r", encoding="utf-8") as f: p2 = json.load(f)
    full_data = p1 + p2
    with open(out_script, "w", encoding="utf-8") as f: json.dump(full_data, f, ensure_ascii=False, indent=2)

    # 2. 准备角色基因库
    role_lib = {
        "SPEAKER_00": {
            "wav": os.path.join(proj_dir, "seeds", "main_seed.wav"),
            "text": full_data[0]['en']
        }
    }
    # 提取种子 (取前 5 秒)
    FFMPEG = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    boosted_wav = r"E:\VideoTranslator_Project\unhinged_tech\boosted_vocals.wav"
    os.makedirs(os.path.dirname(role_lib['SPEAKER_00']['wav']), exist_ok=True)
    subprocess.run([FFMPEG, "-y", "-i", boosted_wav, "-ss", str(full_data[0]['start']), "-t", "5", "-ac", "1", role_lib['SPEAKER_00']['wav']], capture_output=True)
    
    role_lib_p = os.path.join(proj_dir, "UNHINGED_ROLE_LIB.json")
    with open(role_lib_p, "w", encoding="utf-8") as f: json.dump(role_lib, f, indent=2)

    # 3. 启动工厂
    print("\n" + "🏭"*10 + " 正在启动【失控科技】9分钟巅峰量产 " + "🏭"*10)
    sys.path.append(r"E:\VideoTranslator_Project")
    from factory_final_v1_0 import TranslationFactory
    
    video = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    
    factory = TranslationFactory()
    factory.run_production(out_script, video, bgm, role_lib_p)

if __name__ == "__main__":
    import sys
    run_unhinged_finale()
