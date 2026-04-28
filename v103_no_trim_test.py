# -*- coding: utf-8 -*-
"""
V103 No-Trim Test: Disabling VAD Tail Truncation
Pipeline: TTS Generation -> (TRIM DISABLED) -> Pacing Alignment -> Mixing
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

# Workspace (New directory for V103)
TEMP        = os.path.join(ROOT, "production_workspace", "v103_no_trim")
INTER_DIR   = os.path.join(TEMP, "chunks")
OUTPUT_ZH   = os.path.join(TEMP, "master_zh_no_trim.wav")
OUTPUT_MP4  = os.path.join(ROOT, "output_final", "V103_NO_TRIM_TEST.mp4")

os.makedirs(INTER_DIR, exist_ok=True)

def run_pipeline():
    print("\n" + "⚠️"*10 + " V103 禁用尾部截断测试启动 " + "⚠️"*10)
    
    with open(SCRIPT, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < 60] # 前 60 秒

    db = VideoCloneDubber()
    t0 = time.time()
    results = []

    print("\n[*] 步骤 1: 正在生成音频 (不执行 VAD 截断)...")
    for i, item in enumerate(segs):
        zh = item["zh"].strip().strip("。？！， ")
        ref = SEED_WAV if i == 0 else os.path.join(INTER_DIR, f"raw_{i-1}.wav")
        
        # TTS 推理
        raw_p = os.path.join(INTER_DIR, f"raw_{i}.wav")
        wav = db.generate_safe(text=zh, reference_wav_path=ref)
        sf.write(raw_p, wav, db.sample_rate)

        # --- 核心改动：禁用 VAD 检测，直接获取文件总时长 ---
        y, sr = sf.read(raw_p)
        phys_end = len(y) / sr  # 使用完整时长而非 VAD 切断点
        
        # 语速对齐
        quota = item["end"] - item["start"]
        final_p = os.path.join(INTER_DIR, f"final_{i}.wav")
        
        safe_quota = quota - 0.1
        # 由于没有截断，phys_end 包含死寂，大概率会触发加速
        tempo = min(1.3, phys_end / safe_quota) if phys_end > safe_quota else 1.0
        
        print(f"  [{i+1}/{len(segs)}] 原始时长: {phys_end:.2f}s | 配额: {quota:.2f}s | 强制加速: {tempo:.2f}x")

        # 生成最终文件 (移除 atrim 和 afade，仅执行 atempo)
        subprocess.run([
            FFMPEG, "-y", "-i", raw_p, "-af", f"atempo={tempo}", final_p
        ], capture_output=True)

        results.append((final_p, item["start"]))

    # 混音与合成 (同 V102)
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_cmd = "".join(f"[a{k}]" for k in range(len(results))) + f"amix=inputs={len(results)}:duration=longest[aout]"
    
    subprocess.run([FFMPEG, "-y"] + in_args + ["-filter_complex", ";".join(delays) + ";" + mix_cmd, "-map", "[aout]", "-c:a", "pcm_s16le", OUTPUT_ZH], check=True)

    srt_escaped = SRT.replace("\\", "/").replace(":", "\\:")
    cmd_pack = [
        FFMPEG, "-y", "-ss", "0", "-t", "60", "-i", RAW_VIDEO, "-i", OUTPUT_ZH, "-ss", "0", "-t", "60", "-i", BGM,
        "-filter_complex", f"[1:a]volume=1.5[zh];[2:a]volume=0.2[bg];[zh][bg]amix=inputs=2:duration=first[a_final];[0:v]subtitles='{srt_escaped}'[v_final]",
        "-map", "[v_final]", "-map", "[a_final]", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", OUTPUT_MP4
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n✨ V103 测试完成：{OUTPUT_MP4}")

if __name__ == "__main__":
    run_pipeline()
