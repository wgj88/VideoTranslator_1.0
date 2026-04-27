# -*- coding: utf-8 -*-
import os, sys, subprocess, re, json, numpy as np
import soundfile as sf
import librosa, torch

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

def run_v5_5_blind_clone():
    v_vocal = r"C:\Users\Administrator\separated_audio\pure_vocals.wav"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory"
    
    db = VideoCloneDubber()

    # 1. 【核心修复】重新截取一段“无含义”种子 (比如 20s 处的平稳发音)
    blind_seed = os.path.join(temp_dir, "blind_seed.wav")
    subprocess.run([FFMPEG_BIN, "-y", "-i", v_vocal, "-ss", "20", "-t", "3", blind_seed], check=True)
    
    zh_json = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140_zh.json"
    with open(zh_json, "r", encoding="utf-8-sig") as f: data = json.load(f)

    final_segments = []
    print(f"\n🚀 正在执行【V5.5 盲读克隆】...")

    for i in range(5):
        # 深度文本清洗
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        if not text: continue
        
        print(f"  -> 盲读渲染第 {i} 句...")
        # 【核心修正】不提供 prompt_text，物理阻断单词渗透
        wav = db.model.generate(text=text, prompt_wav_path=blind_seed, prompt_text=" ")
        
        raw_out = os.path.join(temp_dir, f"blind_raw_{i}.wav")
        sf.write(raw_out, wav, db.sample_rate)
        
        # 物理级前段静默与后段淡出
        clean_out = os.path.join(temp_dir, f"blind_clean_{i}.wav")
        # 强制切掉前 0.2s (可能的渗漏区)，并在末尾执行 0.1s 淡出
        subprocess.run([FFMPEG_BIN, "-y", "-i", raw_out, "-af", "atrim=start=0.2,afade=t=out:st=1.5:d=0.1", clean_out], capture_output=True)
        final_segments.append(clean_out)

    # 3. 合成带延迟的音轨
    output_wav = r"E:\VideoTranslator_Project\output_final\V5_5_BLIND_AUDITION.wav"
    input_args = []
    filter_parts = []
    for idx, path in enumerate(final_segments):
        input_args.extend(["-i", path])
        delay = int(data[idx]['start'] * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    filter_complex = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(final_segments))]) + f"amix=inputs={len(final_segments)}:duration=longest,volume={len(final_segments)}"
    cmd = [FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", filter_complex, output_wav]
    subprocess.run(cmd, check=True)
    
    print(f"\n🏆 V5.5 盲读版已产出：{output_wav}")

if __name__ == "__main__":
    run_v5_5_blind_clone()
