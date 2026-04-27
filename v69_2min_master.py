# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import ProductionFactory

def run_2min_production():
    print("\n" + "🎬"*10 + " 正在铸造 V69 【两分钟先导旗舰版】 " + "🎬"*10)
    
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_SCRIPT.json"
    role_lib_p = r"E:\VideoTranslator_Project\unhinged_tech\UNHINGED_ROLE_LIB.json"
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V69_2MIN_MASTER.mp4"
    
    with open(role_lib_p, "r", encoding="utf-8") as f: seed_wav = json.load(f)['SPEAKER_00']['wav']
    
    # 1. 启动工厂
    factory = ProductionFactory(batch_size=4)
    # 我们暂时借用 factory 里的逻辑，但因为刚才 rewind 后混音部分需要外部串联
    # 这里我们执行渲染并手动缝合
    processed_results = factory.run_production(script_p, seed_wav, None)

    # 2. 物理缝合音轨 (Module 3)
    FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\v69_zh_2min.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}:duration=longest,volume={len(processed_results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    # 3. 封装成品 (Module 4)
    print("\n[Master] 正在压制 2 分钟商业样片...")
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "120", "-i", raw_v, 
        "-i", temp_zh, "-ss", "0", "-t", "120", "-i", bgm,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V69 样片达成！请审阅这 2 分钟的巅峰质感：{output_mp4}")

if __name__ == "__main__":
    run_2min_production()
