# -*- coding: utf-8 -*-
import json, os, subprocess, sys

# --- 物理路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]
sys.path.append(r"E:\VideoTranslator_Project")
from v53_turbo_factory import TurboFactory

def format_timestamp(seconds):
    td = float(seconds)
    return f"{int(td//3600):02d}:{int((td%3600)//60):02d}:{int(td%60):02d},{int((td%1)*1000):03d}"

def run_1min_full_test():
    print("\n" + "🚀"*10 + " 启动【首分钟】全能样片量产 " + "🚀"*10)
    
    proj_dir = r"E:\VideoTranslator_Project\unhinged_tech"
    script_p = os.path.join(proj_dir, "UNHINGED_FINAL_506_SCRIPT.json")
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    
    # 1. 剧本切片 (仅取 start < 60s 的段落)
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    test_data = [item for item in data if item['start'] < 60.0]
    
    temp_script = os.path.join(proj_dir, "1min_test_script.json")
    with open(temp_script, "w", encoding="utf-8") as f: json.dump(test_data, f, indent=2)
    print(f"  ✅ 锁定前 1 分钟共 {len(test_data)} 段台词。")

    # 2. 异步配音生产
    tf = TurboFactory()
    processed_wavs = tf.run_production(temp_script, seed_wav)

    # 3. 生成局部音轨与 SRT
    temp_zh_wav = os.path.join(proj_dir, "1min_zh_track.wav")
    temp_srt = os.path.join(proj_dir, "1min_subtitles.srt")
    
    # 缝合音轨
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(processed_wavs):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(processed_wavs))]) + f"amix=inputs={len(processed_results) if 'processed_results' in locals() else len(processed_wavs)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh_wav], check=True, capture_output=True)

    # 生成 SRT
    with open(temp_srt, "w", encoding="utf-8") as f:
        for i, item in enumerate(test_data):
            f.write(f"{i+1}\n{format_timestamp(item['start'])} --> {format_timestamp(item['end'])}\n{item['zh']}\n\n")

    # 4. 终极封装 (截取原视频 1 分钟)
    raw_v = r"E:\VideoTranslator_Project\raw_videos\The unhinged world of tech in 2026....f399.mp4"
    bgm = r"E:\VideoTranslator_Project\unhinged_tech\separated\other.wav"
    output_mp4 = r"E:\VideoTranslator_Project\output_final\V61_UNHINGED_1MIN_MASTER.mp4"
    escaped_srt = temp_srt.replace("\\", "/").replace(":", "\\:")

    print("\n[Master] 正在压制首分钟样片 (包含字幕硬压)...")
    cmd_pack = [
        FFMPEG_BIN, "-y", "-ss", "0", "-t", "60", "-i", raw_v, 
        "-i", temp_zh_wav, "-ss", "0", "-t", "60", "-i", bgm,
        "-filter_complex", f"[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out];[0:v]subtitles='{escaped_srt}':force_style='FontSize=18,PrimaryColour=&H00FFFF,BorderStyle=1,Outline=1,Alignment=2'[v_sub]",
        "-map", "[v_sub]", "-map", "[out]", "-c:v", "libx264", "-crf", "23", "-c:a", "aac", output_mp4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 1分钟全能样片已达成！请验收：{output_mp4}")

if __name__ == "__main__":
    run_1min_full_test()
