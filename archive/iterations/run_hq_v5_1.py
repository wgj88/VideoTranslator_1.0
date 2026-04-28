# -*- coding: utf-8 -*-
import sys, os, subprocess, json, re, numpy as np
import librosa, torch, soundfile as sf

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
from translator import VideoTranslator

def run_v5_1_hq_fixed():
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f399.mp4"
    a_m4a = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140.m4a"
    
    print(f"\n🚀 正在发起【V5.1 最终加固】音质测试...")
    
    ts = AudioTranscriber()
    db = VideoCloneDubber()
    vt = VideoTranslator()

    # 1. 采集最响亮的开场声纹
    seed_wav = r"E:\VideoTranslator_Project\temp_factory\v5_1_gold_seed.wav"
    subprocess.run([FFMPEG_BIN, "-y", "-i", a_m4a, "-ss", "0", "-t", "4", seed_wav], check=True)
    ref_text = ts.model.transcribe(seed_wav)['text'].strip()
    print(f"🎤 锁定开场指纹: {ref_text}")

    # 2. 翻译与配音 (前 10 句)
    raw_json = ts.process(a_m4a)
    zh_json = vt.translate_json(raw_json)
    
    # 强制 UTF-8 读取
    with open(zh_json, "r", encoding="utf-8-sig") as f: 
        data = json.load(f)
    
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v5_1_dubs"
    os.makedirs(audio_dir, exist_ok=True)
    
    valid_dubs = []
    for i in range(10):
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        if len(text) < 2: continue
        print(f"  -> 渲染第 {i} 句: {text}")
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = os.path.join(audio_dir, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        data[i]['dub_path'] = out_p
        valid_dubs.append(data[i])

    # 3. 终极合成：100% 纯净混音
    final_out = r"E:\VideoTranslator_Project\output_final\V5_1_STABLE_CHINESE.mp4"
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+1}:a]adelay={delay}|{delay}[a{idx}]")
    
    filter_str = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4]
    for d in valid_dubs: cmd.extend(["-i", d['dub_path']])
    cmd.extend(["-filter_complex", filter_str, "-map", "0:v", "-map", "[out]", "-c:v", "copy", final_out])
    subprocess.run(cmd, check=True)
    print(f"\n🏆 V5.1 样板打造成功！成品已产出：{final_out}")

if __name__ == "__main__":
    run_v5_1_hq_fixed()
