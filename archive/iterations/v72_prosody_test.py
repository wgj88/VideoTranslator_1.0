# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import ProductionFactory

def run_v72_prosodic_test():
    print("\n" + "🔥"*10 + " 启动 V72 【B 站博主·灵魂汉化版】压制 " + "🔥"*10)
    
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V72_PROSODY_SCRIPT.json"
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V72_BILIBILI_STYLE_PROSODY.mp4"

    # 1. 启动工厂
    # 强制开启高精模式，适配这种带情绪的文本
    factory = ProductionFactory(batch_size=4)
    # 我们微调 get_smart_steps，让这 10 句都用 45 步
    factory.get_smart_steps = lambda x: 45
    
    processed_results = factory.run_production(script_p, seed_wav)

    # 2. 物理缝合音轨
    FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\v72_zh_prosody.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    # 3. 最终压制
    print("\n[Master] 正在执行全视频汉化压制...")
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "45", "-i", raw_v, 
        "-i", temp_zh, "-ss", "0", "-t", "45", "-i", bgm,
        "-filter_complex", f"[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='E\\:/VideoTranslator_Project/unhinged_tech/1min_subtitles.srt':force_style='FontSize=20,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-crf", "22", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V72 博主灵魂版达成！请验收：{output_mp4}")

if __name__ == "__main__":
    run_v72_prosodic_test()
