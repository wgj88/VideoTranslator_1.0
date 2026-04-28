# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time

sys.path.append(r"E:\VideoTranslator_Project")
from factory_final_v1_0 import ProductionFactory

def run_v71_one_minute_peak():
    print("\n" + "🎙️"*10 + " 启动 V71 【一分钟播音员巅峰版】压制 " + "🎙️"*10)
    
    # 指向 V70 正典化剧本 (之前已保存)
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V70_FORMAL_SCRIPT.json"
    # 使用临床级净化种子
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V71_UNHINGED_1MIN_ANNOUNCER.mp4"
    
    # 1. 加载 1.0 旗舰引擎
    factory = ProductionFactory(batch_size=4)
    
    # 2. 截取前 60 秒剧本进行局部渲染
    with open(script_p, "r", encoding="utf-8") as f: all_data = json.load(f)
    test_data = [item for item in all_data if item['start'] < 60.0]
    
    temp_script = r"E:\VideoTranslator_Project\unhinged_tech\v71_temp_script.json"
    with open(temp_script, "w", encoding="utf-8") as f: json.dump(test_data, f, indent=2)

    print(f"  -> 正在全速渲染前 {len(test_data)} 段正典化配音...")
    processed_results = factory.run_production(temp_script, seed_wav)

    # 3. 物理缝合音轨
    FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\v71_zh_peak.wav"
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(processed_results):
        input_args.extend(["-i", p])
        delay = int(start_t * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(processed_results))]) + f"amix=inputs={len(processed_results)}:duration=longest"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    # 4. 字幕生成与硬压
    temp_srt = r"E:\VideoTranslator_Project\unhinged_tech\v71_1min.srt"
    def fmt_t(s): return f"{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d},{int((s%1)*1000):03d}"
    with open(temp_srt, "w", encoding="utf-8") as f:
        for i, item in enumerate(test_data):
            f.write(f"{i+1}\n{fmt_t(item['start'])} --> {fmt_t(item['end'])}\n{item['zh']}\n\n")

    print("\n[Master] 正在压制最终成品...")
    escaped_srt = temp_srt.replace("\\", "/").replace(":", "\\:")
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "60", "-i", raw_v, 
        "-i", temp_zh, "-ss", "0", "-t", "60", "-i", bgm,
        "-filter_complex", f"[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{escaped_srt}':force_style='FontSize=20,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-crf", "22", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V71 播音巅峰样片已交付：{output_mp4}")

if __name__ == "__main__":
    run_v71_one_minute_peak()
