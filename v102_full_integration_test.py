# -*- coding: utf-8 -*-
"""
V102 Full Integration Test: End-to-End Video Translation & Dubbing
Pipeline: TTS Generation -> VAD Trim -> Pacing Alignment -> BGM Mixing -> Video Muxing -> Subtitling
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
TEMP        = os.path.join(ROOT, "production_workspace", "v102_test")
INTER_DIR   = os.path.join(TEMP, "chunks")
OUTPUT_ZH   = os.path.join(TEMP, "master_zh_only.wav")
OUTPUT_MP4  = os.path.join(ROOT, "output_final", "V102_FULL_TEST_RESULT.mp4")

os.makedirs(INTER_DIR, exist_ok=True)

def smart_steps(text):
    c = len(text)
    if c <= 6: return 12
    if c <= 25: return 25
    return 50

def run_pipeline():
    print("\n" + "🚀"*10 + " V102 全链路集成测试启动 " + "🚀"*10)
    
    # 1. Load Data (Testing first 15 segments for efficiency ~ 1 minute)
    with open(SCRIPT, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = [it for it in data if it["start"] < 60]
    print(f"[*] 目标段落: {len(segs)} 段 (前 60 秒)")

    db = VideoCloneDubber()
    t0 = time.time()
    results = []

    # 2. Audio Generation Loop
    print("\n[*] 步骤 1: 正在生成高质量克隆配音...")
    for i, item in enumerate(segs):
        zh = item["zh"].strip().strip("。？！， ")
        # V91 记忆链：首句用 seed，后续用前一句作为参考
        ref = SEED_WAV if i == 0 else os.path.join(INTER_DIR, f"clean_{i-1}.wav")
        steps = smart_steps(zh)

        # TTS 推理
        raw_p = os.path.join(INTER_DIR, f"raw_{i}.wav")
        wav = db.generate_safe(text=zh, reference_wav_path=ref, inference_timesteps=steps)
        sf.write(raw_p, wav, db.sample_rate)

        # VAD 裁剪
        y, sr = sf.read(raw_p)
        intervals = librosa.effects.split(y, top_db=22)
        phys_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y) / sr
        
        # 语速对齐 (V92 动态对齐)
        quota = item["end"] - item["start"]
        final_p = os.path.join(INTER_DIR, f"final_{i}.wav")
        
        safe_quota = quota - 0.1
        if phys_end > safe_quota and safe_quota > 0.5:
            tempo = min(1.25, phys_end / safe_quota) # 最高加速 1.25 倍
        else:
            tempo = 1.0
        
        # 写入物理裁剪文件作为下一句参考
        clean_p = os.path.join(INTER_DIR, f"clean_{i}.wav")
        subprocess.run([FFMPEG, "-y", "-i", raw_p, "-af", f"atrim=end={phys_end},asetpts=PTS-STARTPTS", clean_p], capture_output=True)

        # 生成最终对齐文件
        subprocess.run([
            FFMPEG, "-y", "-i", raw_p, "-af",
            f"atrim=end={phys_end},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={max(phys_end/tempo-0.05, 0.1)}:d=0.05",
            final_p,
        ], capture_output=True)

        results.append((final_p, item["start"]))
        print(f"  [{i+1}/{len(segs)}] 进度: {((i+1)/len(segs)*100):.1f}% | {zh[:15]}...")

    # 3. Mixing Master Audio
    print("\n[*] 步骤 2: 正在执行多轨道混音...")
    in_args = []
    delays = []
    for idx, (p, start_t) in enumerate(results):
        in_args.extend(["-i", p])
        delays.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    mix_cmd = "".join(f"[a{k}]" for k in range(len(results))) + f"amix=inputs={len(results)}:duration=longest[aout]"
    
    subprocess.run(
        [FFMPEG, "-y"] + in_args + [
            "-filter_complex", ";".join(delays) + ";" + mix_cmd,
            "-map", "[aout]", "-c:a", "pcm_s16le", OUTPUT_ZH,
        ], check=True, capture_output=True
    )

    # 4. Final Video Assembly (Muxing + BGM + Subtitles)
    print("\n[*] 步骤 3: 正在压制最终视频 (包含 BGM 与字幕)...")
    
    # 转义 SRT 路径以兼容 FFMPEG Windows 路径
    srt_escaped = SRT.replace("\\", "/").replace(":", "\\:")
    
    cmd_pack = [
        FFMPEG, "-y", 
        "-ss", "0", "-t", "60", "-i", RAW_VIDEO,  # 原视频 (前60秒)
        "-i", OUTPUT_ZH,                          # 中文配音
        "-ss", "0", "-t", "60", "-i", BGM,        # 背景音乐
        "-filter_complex", 
        f"[1:a]volume=1.5[zh];[2:a]volume=0.2[bg];[zh][bg]amix=inputs=2:duration=first[a_final];" +
        f"[0:v]subtitles='{srt_escaped}':force_style='FontSize=18,PrimaryColour=&H00FFFF,Alignment=2'[v_final]",
        "-map", "[v_final]", "-map", "[a_final]",
        "-c:v", "libx264", "-crf", "23", "-preset", "veryfast", "-c:a", "aac", "-b:a", "192k",
        OUTPUT_MP4
    ]
    
    result = subprocess.run(cmd_pack, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 视频压制失败: {result.stderr}")
    else:
        print(f"\n✨ 测试成功！完整样片已生成: {OUTPUT_MP4}")
        print(f"⏰ 总耗时: {time.time() - t0:.1f} 秒")

if __name__ == "__main__":
    run_pipeline()
