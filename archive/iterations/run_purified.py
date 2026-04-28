# -*- coding: utf-8 -*-
import os, sys, subprocess, re, json, numpy as np
import soundfile as sf
import librosa, torch

# --- 环境补丁 ---
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
from transcriber import AudioTranscriber

def run_v5_2_purified():
    a_m4a = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140.m4a"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory"
    
    print(f"\n🚀 正在发起【V5.2 净化版】测试，消除开头固定音节...")
    
    ts = AudioTranscriber()
    db = VideoCloneDubber()

    # 1. 【核心修复】声学净化音色种子
    raw_seed = os.path.join(temp_dir, "raw_seed.wav")
    pure_seed = os.path.join(temp_dir, "v5_2_pure_seed.wav")
    # 截取 5 秒
    subprocess.run([FFMPEG_BIN, "-y", "-i", a_m4a, "-ss", "0.5", "-t", "5", raw_seed], check=True, capture_output=True)
    # 物理净化：去除开头静默并淡入淡出，消除由于截取产生的爆破音
    cmd_purify = [FFMPEG_BIN, "-y", "-i", raw_seed, "-af", "silenceremove=start_periods=1:start_threshold=-50dB,afade=t=in:st=0:d=0.1,afade=t=out:st=4.9:d=0.1", pure_seed]
    subprocess.run(cmd_purify, check=True, capture_output=True)
    
    ref_text = ts.model.transcribe(pure_seed)['text'].strip()
    print(f"🎤 净化后的指纹台词: {ref_text}")

    # 2. 准备配音文本
    zh_json = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140_zh.json"
    with open(zh_json, "r", encoding="utf-8-sig") as f: data = json.load(f)
    
    valid_dubs = []
    for i in range(5):
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        # --- 核心修复：在文本开头加入“停顿点”，引导模型平稳开口 ---
        safe_text = "……" + text
        
        print(f"  -> 正在生成第 {i} 句 (净化模式)...")
        wav = db.model.generate(text=safe_text, prompt_wav_path=pure_seed, prompt_text=ref_text)
        
        out_p = os.path.join(temp_dir, f"purified_dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        data[i]['dub_path'] = out_p
        valid_dubs.append(data[i])

    # 3. 极简试听合成
    output_wav = r"E:\VideoTranslator_Project\output_final\V5_2_PURIFIED_AUDITION.wav"
    all_audio = []
    for d in valid_dubs:
        wav_data, sr = sf.read(d['dub_path'])
        all_audio.append(wav_data)
    
    sf.write(output_wav, np.concatenate(all_audio), sr)
    print(f"\n🏆 净化版试听音轨已产出：{output_wav}")
    print("请听听看，每句话开头的那个重复音节是否已经消失。")

if __name__ == "__main__":
    run_v5_2_purified()
