# -*- coding: utf-8 -*-
"""
V106 Timbre Stabilizer: Fixing Voice Alienation
Strategy: 
1. Switch from "Chain Reference" back to "Global Anchor Reference" (SEED_WAV).
2. Maintains V105 NLP Guard and V104 Collision Guard.
"""
import os, sys, json, subprocess, time
import soundfile as sf
import librosa

# --- Configuration ---
ROOT = r"E:\VideoTranslator_Project"
FFMPEG = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG) + os.pathsep + os.environ["PATH"]

sys.path.insert(0, os.path.join(ROOT, "core_engines"))
from clone_dubber import VideoCloneDubber

# Assets
SCRIPT      = os.path.join(ROOT, "unhinged_tech", "UNHINGED_FINAL_506_SCRIPT.json")
SEED_WAV    = os.path.join(ROOT, "unhinged_tech", "seeds", "ultra_pure_seed.wav")
BGM         = os.path.join(ROOT, "unhinged_tech", "separated", "other.wav")
RAW_VIDEO   = os.path.join(ROOT, "raw_videos", "The unhinged world of tech in 2026....f399.mp4")
SRT         = os.path.join(ROOT, "unhinged_tech", "v81_final.srt")

# Workspace
TEMP        = os.path.join(ROOT, "production_workspace", "v106_stable")
INTER_DIR   = os.path.join(TEMP, "chunks")
OUTPUT_ZH   = os.path.join(TEMP, "master_zh_stable.wav")
OUTPUT_MP4  = os.path.join(ROOT, "output_final", "V106_TIMBRE_STABLE_RESULT.mp4")

os.makedirs(INTER_DIR, exist_ok=True)

def simple_nlp_shorten(text):
    # 保留 V105 的精简逻辑
    rules = {"将会有": "将有", "将会": "将", "成为了": "成了", "成为": "成", "我曾经": "我曾", "已经": "已"}
    short = text
    for k, v in rules.items(): short = short.replace(k, v)
    return short

def run_pipeline():
    print("\n" + "💎"*10 + " V106 音色稳定器启动 (全局锚点模式) " + "💎"*10)
    
    with open(SCRIPT, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < 60] 

    db = VideoCloneDubber()
    t0 = time.time()
    results = []

    for i, item in enumerate(segs):
        zh = item["zh"].strip().strip("。？！， ")
        quota = (segs[i+1]["start"] if i < len(segs)-1 else item["end"]) - item["start"]
        
        # 1. NLP 预处理
        current_text = simple_nlp_shorten(zh) if len(zh)/quota > 4.8 else zh

        # 2. 【核心修复】始终使用 SEED_WAV 作为参考，切断误差累积链
        ref = SEED_WAV 
        
        raw_p = os.path.join(INTER_DIR, f"raw_{i}.wav")
        # 调用 generate_safe (V97 动态 CFG)
        wav = db.generate_safe(text=current_text, reference_wav_path=ref)
        sf.write(raw_p, wav, db.sample_rate)

        # 3. 物理分析与防撞
        y, sr = sf.read(raw_p)
        intervals = librosa.effects.split(y, top_db=22)
        phys_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr
        
        safe_boundary = quota - 0.05
        tempo = max(1.0, phys_end / safe_boundary)
        
        final_p = os.path.join(INTER_DIR, f"final_{i}.wav")
        # 强制边界保护 + 对齐
        subprocess.run([
            FFMPEG, "-y", "-i", raw_p, "-af",
            f"atrim=end={phys_end},asetpts=PTS-STARTPTS,atempo={tempo},atrim=end={safe_boundary},afade=t=out:st={max(safe_boundary-0.05, 0.1)}:d=0.05",
            final_p
        ], capture_output=True)

        results.append((final_p, item["start"]))
        print(f"  [{i+1}/{len(segs)}] 音色稳定生成 | Tempo: {tempo:.2f}x | {current_text[:10]}...")

    # 4. 混音与合成
    print("\n[*] 正在执行高保真混音...")
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_cmd = "".join(f"[a{k}]" for k in range(len(results))) + f"amix=inputs={len(results)}:duration=longest[aout]"
    subprocess.run([FFMPEG, "-y"] + in_args + ["-filter_complex", ";".join(delays) + ";" + mix_cmd, "-map", "[aout]", "-c:a", "pcm_s16le", OUTPUT_ZH], check=True, capture_output=True)

    srt_escaped = SRT.replace("\\", "/").replace(":", "\\:")
    cmd_pack = [
        FFMPEG, "-y", "-ss", "0", "-t", "60", "-i", RAW_VIDEO, "-i", OUTPUT_ZH, "-ss", "0", "-t", "60", "-i", BGM,
        "-filter_complex", f"[1:a]volume=1.5[zh];[2:a]volume=0.2[bg];[zh][bg]amix=inputs=2:duration=first[a_final];[0:v]subtitles='{srt_escaped}':force_style='FontSize=18,Alignment=2'[v_final]",
        "-map", "[v_final]", "-map", "[a_final]", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", OUTPUT_MP4
    ]
    subprocess.run(cmd_pack, check=True, capture_output=True)
    print(f"\n✨ V106 稳定版运行完毕！样片: {OUTPUT_MP4}")

if __name__ == "__main__":
    run_pipeline()
