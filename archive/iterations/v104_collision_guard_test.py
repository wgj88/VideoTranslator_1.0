# -*- coding: utf-8 -*-
"""
V104 Collision Guard: Anti-Collision & Adaptive Pacing System
Features:
1. Predictive Overlap Detection
2. Dynamic Tempo Unlocking (Auto-fit)
3. Hard Boundary Truncation (Safety Cut)
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
TEMP        = os.path.join(ROOT, "production_workspace", "v104_guard")
INTER_DIR   = os.path.join(TEMP, "chunks")
OUTPUT_ZH   = os.path.join(TEMP, "master_zh_guarded.wav")
OUTPUT_MP4  = os.path.join(ROOT, "output_final", "V104_COLLISION_GUARD_RESULT.mp4")

os.makedirs(INTER_DIR, exist_ok=True)

def run_pipeline():
    print("\n" + "🛡️"*10 + " V104 防撞检测系统启动 " + "🛡️"*10)
    
    with open(SCRIPT, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < 60] 

    db = VideoCloneDubber()
    t0 = time.time()
    results = []

    print("\n[*] 步骤 1: 执行自适应对齐生成...")
    for i, item in enumerate(segs):
        zh = item["zh"].strip().strip("。？！， ")
        ref = SEED_WAV if i == 0 else os.path.join(INTER_DIR, f"clean_{i-1}.wav")
        
        # 1. TTS 推理
        raw_p = os.path.join(INTER_DIR, f"raw_{i}.wav")
        wav = db.generate_safe(text=zh, reference_wav_path=ref)
        sf.write(raw_p, wav, db.sample_rate)

        # 2. VAD 物理分析
        y, sr = sf.read(raw_p)
        intervals = librosa.effects.split(y, top_db=22)
        phys_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr
        
        # 3. 防撞逻辑 (Collision Guard)
        next_start = segs[i+1]["start"] if i < len(segs)-1 else item["end"]
        available_quota = next_start - item["start"]
        safe_boundary = available_quota - 0.05 # 留出 50ms 绝对真空区
        
        final_p = os.path.join(INTER_DIR, f"final_{i}.wav")
        clean_p = os.path.join(INTER_DIR, f"clean_{i}.wav") # 用于下一句参考
        
        tempo = 1.0
        guard_status = "PASS"
        
        if phys_end > safe_boundary:
            # 触发防撞干预：自动计算解除限制后的 tempo
            tempo = phys_end / safe_boundary
            guard_status = f"⚠️ GUARDED (Tempo {tempo:.2f}x)"
        
        # 4. 物理裁剪 (备用参考链)
        subprocess.run([FFMPEG, "-y", "-i", raw_p, "-af", f"atrim=end={phys_end},asetpts=PTS-STARTPTS", clean_p], capture_output=True)

        # 5. 生成对齐音频 (带 atrim 强制边界保护)
        # 即使使用了 atempo，我们也加上 atrim=end={safe_boundary} 作为双重保险
        cmd_align = [
            FFMPEG, "-y", "-i", raw_p, "-af",
            f"atrim=end={phys_end},asetpts=PTS-STARTPTS,atempo={tempo},atrim=end={safe_boundary},afade=t=out:st={max(safe_boundary-0.05, 0.1)}:d=0.05",
            final_p
        ]
        subprocess.run(cmd_align, capture_output=True)

        results.append((final_p, item["start"]))
        print(f"  [{i+1}/{len(segs)}] {status_icon(guard_status)} {zh[:12]}... | Quota: {available_quota:.2f}s | {guard_status}")

    # 6. 混音与合成
    print("\n[*] 步骤 2: 执行安全对齐混音...")
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_cmd = "".join(f"[a{k}]" for k in range(len(results))) + f"amix=inputs={len(results)}:duration=longest[aout]"
    
    subprocess.run([FFMPEG, "-y"] + in_args + ["-filter_complex", ";".join(delays) + ";" + mix_cmd, "-map", "[aout]", "-c:a", "pcm_s16le", OUTPUT_ZH], check=True, capture_output=True)

    print("[*] 步骤 3: 压制最终视频...")
    srt_escaped = SRT.replace("\\", "/").replace(":", "\\:")
    cmd_pack = [
        FFMPEG, "-y", "-ss", "0", "-t", "60", "-i", RAW_VIDEO, "-i", OUTPUT_ZH, "-ss", "0", "-t", "60", "-i", BGM,
        "-filter_complex", f"[1:a]volume=1.5[zh];[2:a]volume=0.2[bg];[zh][bg]amix=inputs=2:duration=first[a_final];[0:v]subtitles='{srt_escaped}':force_style='FontSize=18,Alignment=2'[v_final]",
        "-map", "[v_final]", "-map", "[a_final]", "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", OUTPUT_MP4
    ]
    subprocess.run(cmd_pack, check=True, capture_output=True)
    print(f"\n✨ V104 防撞系统运行完毕！样片: {OUTPUT_MP4}")

def status_icon(status):
    return "✅" if "PASS" in status else "🛡️"

if __name__ == "__main__":
    run_pipeline()
