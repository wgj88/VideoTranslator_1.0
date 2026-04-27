# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 暴力路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v41_full_rebuild():
    print(f"\n" + "🚀"*10 + " 正在执行 V41 【全局对齐·无损复活】重制 " + "🚀"*10)
    
    # 找回最完整的 V27 导演版剧本
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v41_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    print(f"\n[Step 1] 正在补全并净化全篇 {len(data)} 个片段...")

    for i, item in enumerate(data):
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed_wav = os.path.join(r"E:\VideoTranslator_Project\temp_factory", f"GENE_CLEAN_{spk}.wav")
        
        print(f"  -> [{i+1}/{len(data)}] 渲染并手术: {zh_text[:10]}...")
        
        # 1. 深度生成
        wav = db.model.generate(text=zh_text + "。", reference_wav_path=seed_wav, inference_timesteps=50)
        raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
        sf.write(raw_p, wav, db.sample_rate)
        
        # 2. AI 词位锁定 (V39 逻辑：防止溢出)
        res = auditor.transcribe(raw_p)
        start_t = res['segments'][0]['start'] if res['segments'] else 0.0
        # 强制熔断：绝不允许超过设定的 Timeline 时长 + 0.2s 冗余
        expected_dur = item['end'] - item['start']
        end_t = min(res['segments'][-1]['end'] if res['segments'] else 100, expected_dur + 0.1)
        
        final_p = os.path.join(audio_dir, f"v41_seg_{i}.wav")
        cmd_trim = [
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atrim=start={start_t}:end={end_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, (end_t-start_t)-0.1)}:d=0.1",
            final_p
        ]
        subprocess.run(cmd_trim, check=True, capture_output=True)
        item['v41_path'] = final_p

    # --- Step 2: 终极时序合成 ---
    print("\n[Step 2] 正在执行毫秒级时序缝合...")
    temp_zh_track = r"E:\VideoTranslator_Project\temp_factory\v41_zh_full.wav"
    input_args = []
    filter_parts = []
    for idx, item in enumerate(data):
        if 'v41_path' in item:
            input_args.extend(["-i", item['v41_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    # 这里的 amix 必须设置足够多的 inputs
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh_track], check=True, capture_output=True)

    # --- Step 3: 封装成品 ---
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_video = r"E:\VideoTranslator_Project\output_final\V41_FINAL_FULL_SYNC_MASTER.mp4"
    
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", v_mp4, "-i", temp_zh_track, "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V41 终极同步版已产出：{output_video}")

if __name__ == "__main__":
    run_v41_full_rebuild()
