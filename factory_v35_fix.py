# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v35_hard_cut():
    print(f"\n[V35-HardCut] 正在执行【硬熔断】补丁任务...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V34_CRISP_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs"
    output_dir = r"E:\VideoTranslator_Project\temp_factory\v35_fixed_wavs"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)

    # 我们重点重制那个超长的 Seg 12
    for i, item in enumerate(data):
        raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
        if not os.path.exists(raw_p): continue
        
        # 核心改进：硬核计算上限时长
        expected_dur = item['end'] - item['start']
        # 允许 0.2s 的呼吸冗余，超过此长度的全部视为幻觉，物理掐断
        hard_limit = expected_dur + 0.2
        
        print(f"  -> [{i+1}/{len(data)}] 物理熔断检测: {item['zh'][:10]}... (上限 {hard_limit:.2f}s)")
        
        fixed_p = os.path.join(output_dir, f"v35_seg_{i}.wav")
        # 物理执行：atrim 强制截断末尾 + afade 平滑处理
        cmd_cut = [
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atrim=start=0.15:end={hard_limit+0.15},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, hard_limit-0.1)}:d=0.1",
            fixed_p
        ]
        subprocess.run(cmd_cut, check=True, capture_output=True)
        item['v35_path'] = fixed_p

    # 合并压制新视频
    print("\n[V35-Master] 正在压制最终修正版视频...")
    temp_zh = r"E:\VideoTranslator_Project\temp_factory\v35_zh_full.wav"
    input_args = []
    filter_parts = []
    for idx, item in enumerate(data):
        if 'v35_path' in item:
            input_args.extend(["-i", item['v35_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_video = r"E:\VideoTranslator_Project\output_final\V35_FINAL_CRISP_MASTER.mp4"
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", v_mp4, "-i", temp_zh, "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 全篇硬熔断修正完成！成品视频：{output_video}")

if __name__ == "__main__":
    run_v35_hard_cut()
