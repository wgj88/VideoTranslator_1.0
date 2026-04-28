# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 环境补丁 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def run_v40_snatcher_master():
    print(f"\n" + "👑"*10 + " 正在铸造 V40 【词位锁死·终极旗舰版】 " + "👑"*10)
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    raw_audio_dir = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs"
    output_audio_dir = r"E:\VideoTranslator_Project\temp_factory\v40_snatched_wavs"
    os.makedirs(output_audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    # 加载 Whisper 审计官
    print("\n[Step 1] 正在调集 AI 审计官执行全篇扫描...")
    auditor = whisper.load_model("base")

    for i, item in enumerate(data):
        raw_p = os.path.join(raw_audio_dir, f"raw_{i}.wav")
        if not os.path.exists(raw_p): continue
        
        print(f"  -> [{i+1}/{len(data)}] 正在手术截断: {item['zh'][:10]}...")
        
        # 1. 词位扫描
        res = auditor.transcribe(raw_p, word_timestamps=True)
        
        # 2. 寻找锁死坐标
        expected_dur = item['end'] - item['start']
        # 逻辑：取剧本时长+0.5s内的最后一个有效识别词
        all_words = []
        for seg in res['segments']:
            if 'words' in seg: all_words.extend(seg['words'])
        
        cut_point = expected_dur + 0.1 # 默认值
        if all_words:
            # 过滤掉由于模型太长导致的末尾幻觉词
            valid_words = [w for w in all_words if w['end'] < expected_dur + 1.0]
            if valid_words:
                cut_point = valid_words[-1]['end']
        
        # 3. 执行物理熔断
        final_p = os.path.join(output_audio_dir, f"v40_seg_{i}.wav")
        dur_target = cut_point
        cmd_snatch = [
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atrim=start=0.15:end={cut_point+0.15},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, dur_target-0.1)}:d=0.1",
            final_p
        ]
        subprocess.run(cmd_snatch, check=True, capture_output=True)
        item['v40_path'] = final_p

    # --- Step 2: 最终大合成 ---
    print("\n[Step 2] 正在执行全篇物理级总混音...")
    temp_zh_track = r"E:\VideoTranslator_Project\temp_factory\v40_zh_full.wav"
    input_args = []
    filter_parts = []
    
    valid_list = [it for it in data if 'v40_path' in it]
    for idx, item in enumerate(valid_list):
        input_args.extend(["-i", item['v40_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(valid_list))]) + f"amix=inputs={len(valid_list)}:duration=longest,volume={len(valid_list)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh_track], check=True, capture_output=True)

    # 封入视频
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_video = r"E:\VideoTranslator_Project\output_final\V40_ULTIMATE_CLEAN_MASTER.mp4"
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", v_mp4, "-i", temp_zh_track, "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 项目完美大结局！V40 终极纯净版已诞生：{output_video}")

if __name__ == "__main__":
    run_v40_snatcher_master()
