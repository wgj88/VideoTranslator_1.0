# -*- coding: utf-8 -*-
import os, json, subprocess

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def format_ts(s): return f"{int(s//3600):02d}:{int((s%3600)//60):02d}:{int(s%60):02d},{int((s%1)*1000):03d}"

def finalize_v73():
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v73_run"
    script_p = r"E:\VideoTranslator_Project\unhinged_tech\V69_2MIN_ELASTIC_SCRIPT.json"
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    # 1. 音轨大合龙
    input_args = []
    filter_parts = []
    actual_idx = 0
    for i, item in enumerate(data):
        p = os.path.join(temp_dir, f"fixed_{i}.wav")
        if os.path.exists(p):
            input_args.extend(["-i", p])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{actual_idx}:a]adelay={delay}|{delay}[a{actual_idx}]")
            actual_idx += 1
            
    mix_zh = "".join([f"[a{k}]" for k in range(actual_idx)]) + f"amix=inputs={actual_idx}:duration=longest,volume={actual_idx}"
    temp_zh = os.path.join(temp_dir, "v73_final_zh.wav")
    with open(os.path.join(temp_dir, "v73_mix.txt"), "w") as f: f.write(";".join(filter_parts) + ";" + mix_zh)
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex_script", os.path.join(temp_dir, "v73_mix.txt"), temp_zh], check=True)

    # 2. 生成 SRT
    srt_p = os.path.join(temp_dir, "v73_final.srt")
    with open(srt_p, "w", encoding="utf-8") as f:
        for i, item in enumerate(data):
            f.write(f"{i+1}\n{format_ts(item['start'])} --> {format_ts(item['end'])}\n{item['zh']}\n\n")

    # 3. 终极压制
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V73_ZERO_HALLU_MASTER_2MIN.mp4"
    escaped_srt = srt_p.replace("\\", "/").replace(":", "\\:")
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "120", "-i", raw_v, "-i", temp_zh, "-ss", "0", "-t", "120", "-i", bgm,
        "-filter_complex", f"[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{escaped_srt}':force_style='FontSize=20,PrimaryColour=&H00FFFF,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "22", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 样片已正式压制完成！")
    print(f"📂 路径：{output_mp4}")

if __name__ == "__main__":
    finalize_v73()
