# -*- coding: utf-8 -*-
import os, sys, json, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v70_finale():
    proj_dir = r"E:\VideoTranslator_Project\temp_factory\v70_run"
    # 我们假设 results 已经存入了一个临时 json 以供缝合 (此处直接扫描目录)
    # 实际上，我们需要 item['start'] 信息，我直接从 V69 脚本读取
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_ELASTIC_SCRIPT.json"
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    # 1. 执行全篇缝合
    input_args = []
    filter_parts = []
    idx_count = 0
    for i, item in enumerate(data):
        p = os.path.join(proj_dir, f"fixed_{i}.wav")
        if os.path.exists(p):
            input_args.extend(["-i", p])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{idx_count}:a]adelay={delay}|{delay}[a{idx_count}]")
            idx_count += 1
            
    mix_zh = "".join([f"[a{k}]" for k in range(idx_count)]) + f"amix=inputs={idx_count}:duration=longest,volume={idx_count}"
    temp_zh_full = os.path.join(proj_dir, "v70_pure_zh.wav")
    
    with open(os.path.join(proj_dir, "v70_mix.txt"), "w") as f:
        f.write(";".join(filter_parts) + ";" + mix_zh)
    
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex_script", os.path.join(proj_dir, "v70_mix.txt"), temp_zh_full], check=True)

    # 2. 生成 SRT
    srt_p = os.path.join(proj_dir, "v70_purity.srt")
    def format_ts(s): return f"{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d},{int((s%1)*1000):03d}"
    with open(srt_p, "w", encoding="utf-8") as f:
        for i, item in enumerate(data):
            f.write(f"{i+1}\n{format_ts(item['start'])} --> {format_ts(item['end'])}\n{item['zh']}\n\n")

    # 3. 最终压制
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V70_PURITY_ULITMATE_2MIN_MASTER.mp4"
    escaped_srt = srt_p.replace("\\", "/").replace(":", "\\:")
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "120", "-i", raw_v, "-i", temp_zh_full, "-ss", "0", "-t", "120", "-i", bgm,
        "-filter_complex", f"[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{escaped_srt}':force_style='FontSize=20,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "22", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V70 终极净化样片已交付！文件：{output_mp4}")

if __name__ == "__main__":
    run_v70_finale()
