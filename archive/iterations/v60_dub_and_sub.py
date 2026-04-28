# -*- coding: utf-8 -*-
import json, os, subprocess

def format_timestamp(seconds):
    """将秒数转为 SRT 格式: HH:MM:SS,mmm"""
    td = float(seconds)
    hours = int(td // 3600)
    minutes = int((td % 3600) // 60)
    seconds = int(td % 60)
    milliseconds = int((td % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def run_v60_dub_and_sub():
    print("\n" + "📝"*10 + " 启动 V60 【声影同步+字幕硬压】任务 " + "📝"*10)
    
    proj_dir = r"E:\VideoTranslator_Project\unhinged_tech"
    script_p = os.path.join(proj_dir, "UNHINGED_FINAL_506_SCRIPT.json")
    srt_p = os.path.join(proj_dir, "final_subtitles.srt")
    
    # 1. 生成 SRT 文件
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    
    with open(srt_p, "w", encoding="utf-8") as f:
        for i, item in enumerate(data):
            f.write(f"{i+1}\n")
            f.write(f"{format_timestamp(item['start'])} --> {format_timestamp(item['end'])}\n")
            f.write(f"{item['zh']}\n\n")
    print(f"  ✅ 114 段汉化字幕已生成：{srt_p}")

    # 2. 终极压制 (包含音频缝合 + 字幕烧录)
    FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    temp_zh = r"E:\VideoTranslator_Project\unhinged_tech\ultimate_master_zh.wav" # 假设已生成
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V60_UNHINGED_DUB_AND_SUB_FINAL.mp4"

    # 注意：FFmpeg 硬压字幕需要绝对路径且需转义
    # Windows 下路径中的冒号和反斜杠需要处理
    escaped_srt = srt_p.replace("\\", "/").replace(":", "\\:")
    
    print("\n[Master] 正在执行全视频汉化压制 (预计耗时 2-3 分钟)...")
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", raw_v, "-i", temp_zh, "-i", bgm,
        "-filter_complex", f"[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{escaped_srt}':force_style='FontSize=20,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-c:a", "aac", output_mp4
    ]
    
    # 启动后台进程执行压制
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 终极版已达成！汉化视频+同步字幕已就绪：{output_mp4}")

if __name__ == "__main__":
    run_v60_dub_and_sub()
