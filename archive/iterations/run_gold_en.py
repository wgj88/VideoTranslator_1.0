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

def run_v5_1_english_gold():
    # 锁定高音质英文素材
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f399.mp4"
    a_m4a = r"E:\VideoTranslator_Project\raw_videos\15 Coolest Gadgets on Amazon You’ll Wish You Had Sooner.f140.m4a"
    
    print(f"\n🚀 正在对【标准英文素材】发起 V5.1 音质巅峰测试...")
    
    ts = AudioTranscriber()
    db = VideoCloneDubber()
    vt = VideoTranslator()

    # 1. 采集 5s 纯净英文声纹种子
    seed_wav = r"E:\VideoTranslator_Project\temp_factory\gold_en_seed.wav"
    subprocess.run([FFMPEG_BIN, "-y", "-i", a_m4a, "-ss", "30", "-t", "5", seed_wav], check=True)
    ref_text = ts.model.transcribe(seed_wav)['text'].strip()
    print(f"🎤 成功复刻标准英文声纹: {ref_text}")

    # 2. 翻译与配音 (前 8 句)
    raw_json = ts.process(a_m4a)
    zh_json = vt.translate_json(raw_json)
    with open(zh_json, "r") as f: data = json.load(f)
    
    valid_dubs = []
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\gold_dubs"
    os.makedirs(audio_dir, exist_ok=True)
    
    for i in range(8):
        # 核心净化：剔除所有括号标签
        text = re.sub(r'\(.*?\)|\[.*?\]', '', data[i].get('translated_text', '')).strip()
        if not text: continue
        
        print(f"  -> 正在高清渲染第 {i} 句: {text}")
        wav = db.model.generate(text=text, prompt_wav_path=seed_wav, prompt_text=ref_text)
        out_p = os.path.join(audio_dir, f"dub_{i}.wav")
        sf.write(out_p, wav, db.sample_rate)
        data[i]['dub_path'] = out_p
        valid_dubs.append(data[i])

    # 3. 极致合成：侧链闪避混音
    final_out = r"E:\VideoTranslator_Project\output_final\V5_1_GOLD_CLEAN_ENGLISH.mp4"
    
    input_args = []
    filter_parts = []
    for idx, item in enumerate(valid_dubs):
        input_args.extend(["-i", item['dub_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx+2}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_dub = ";".join(filter_parts) + ";" + "".join([f"[a{k}]" for k in range(len(valid_dubs))]) + f"amix=inputs={len(valid_dubs)}:duration=longest[d]"
    # 原音完全静默 (volume=0)，只留画面 + 中文配音 + 空白占位
    final_filter = mix_dub + f";[1:a]volume=0[bg];[bg][d]amix=inputs=2[out]"
    
    cmd = [FFMPEG_BIN, "-y", "-i", v_mp4, "-i", a_m4a] + input_args + ["-filter_complex", final_filter, "-map", "0:v", "-map", "[out]", "-c:v", "copy", final_out]
    subprocess.run(cmd, check=True)
    print(f"\n🏆 实战圆满完成！这一次的中文是商业级清晰：{final_out}")

if __name__ == "__main__":
    run_v5_1_english_gold()
