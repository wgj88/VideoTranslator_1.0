# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch, soundfile as sf

# --- 环境 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from dubber import VideoDubber

v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
v_json = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE_zh.json"
v_bgm = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"

def run_v7_1_strict():
    print(f"\n🚀 正在执行【V7.1 严格路由版】合成，物理屏蔽英文源...")
    
    db = VideoDubber()
    with open(v_json, "r", encoding="utf-8-sig") as f: data = json.load(f)

    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v7_pro_wavs"
    final_segments = []
    
    # 强制重新确认 10 个中文片段的路径
    for i in range(min(10, len(data))):
        p = os.path.join(audio_dir, f"aligned_{i}.wav")
        if os.path.exists(p): final_segments.append(p)

    output_video = r"E:\VideoTranslator_Project\output_final\V7_1_STRICT_CHINESE.mp4"
    
    # --- 核心修复：构造“无死角”显式路由滤镜 ---
    # [2:a] 开始才是中文，[1:a] 是 BGM，[0:a] 是万恶的英文原音（我们要丢弃它）
    
    # 1. 混合所有中文片段
    inputs_zh = "".join([f"[{k+2}:a]" for k in range(len(final_segments))])
    filter_complex = f"{inputs_zh}amix=inputs={len(final_segments)}:duration=longest,volume={len(final_segments)}[dub_only];"
    
    # 2. 用中文去闪避 BGM，并合并。完全不给 [0:a] 任何出镜机会！
    filter_complex += f"[1:a][dub_only]sidechaincompress=threshold=0.01:ratio=20[bg_ducked];"
    filter_complex += "[bg_ducked][dub_only]amix=inputs=2:weights='0.2 1.0'[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4, "-i", v_bgm]
    for p in final_segments: cmd.extend(["-i", p])
    
    # 显式指定：-map 0:v (画面) 和 -map [out] (我们的纯净混音)
    cmd.extend(["-filter_complex", filter_complex, "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video])
    
    print(f"[Action] 正在执行最后的物理压制...")
    subprocess.run(cmd, check=True)
    print(f"\n🏆 V7.1 严格版已产出：{output_video}")

if __name__ == "__main__":
    run_v7_1_strict()
