# -*- coding: utf-8 -*-
import os, sys, subprocess, re, json, numpy as np
import soundfile as sf
import librosa, torch

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
from clone_dubber import VideoCloneDubber

def run_v5_3_perfect():
    temp_dir = r"E:\VideoTranslator_Project\temp_factory"
    seed_wav = os.path.join(temp_dir, "v5_2_pure_seed.wav") # 使用已净化的种子
    
    db = VideoCloneDubber()
    
    zh_json = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140_zh.json"
    with open(zh_json, "r", encoding="utf-8-sig") as f: data = json.load(f)
    
    final_segments = []
    print(f"\n🚀 正在执行【V5.3 终极消噪】渲染...")

    for i in range(8):
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        if not text: continue
        
        # --- 核心改进：双重停顿闭合 ---
        target_text = "……" + text + "。"
        
        print(f"  -> 渲染并消噪 Seg_{i}...")
        wav = db.model.generate(text=target_text, prompt_wav_path=seed_wav, prompt_text="Stop scrolling these gadgets")
        
        # A. 原始写入
        raw_out = os.path.join(temp_dir, f"raw_v5_3_{i}.wav")
        sf.write(raw_out, wav, db.sample_rate)
        
        # B. 【核心改进】FFmpeg 物理级静默切割与淡出
        # 逻辑：去除尾部静音 + 最后 0.1s 强制淡出
        clean_out = os.path.join(temp_dir, f"clean_v5_3_{i}.wav")
        cmd_clean = [
            FFMPEG_BIN, "-y", "-i", raw_out,
            "-af", "silenceremove=stop_periods=1:stop_duration=0.1:stop_threshold=-50dB,afade=t=out:st=1.3:d=0.1", # st=1.3 是个预设，稍后根据实际动态调整
            clean_out
        ]
        # 动态获取时长以确定淡出起始点
        proc = subprocess.run([FFMPEG_BIN, "-i", raw_out], capture_output=True, text=True)
        dur_match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", proc.stderr)
        if dur_match:
            dur = float(dur_match.group(3))
            fade_start = max(0, dur - 0.15)
            # 应用精准消噪与淡出
            subprocess.run([FFMPEG_BIN, "-y", "-i", raw_out, "-af", f"silenceremove=stop_periods=1:stop_duration=0.05:stop_threshold=-45dB,afade=t=out:st={fade_start}:d=0.1", clean_out], check=True, capture_output=True)
            final_segments.append(clean_out)

    # 3. 产出试听大包
    output_wav = r"E:\VideoTranslator_Project\output_final\V5_3_ZERO_NOISE_FINAL.wav"
    subprocess.run([FFMPEG_BIN, "-y"] + [arg for s in final_segments for arg in ["-i", s]] + ["-filter_complex", f"amix=inputs={len(final_segments)}:duration=longest,volume={len(final_segments)}", output_wav], check=True)
    
    print(f"\n🏆 V5.3 终极定论版已产出：{output_wav}")

if __name__ == "__main__":
    run_v5_3_perfect()
