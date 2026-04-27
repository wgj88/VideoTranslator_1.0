# -*- coding: utf-8 -*-
import os, sys, subprocess, re, json, numpy as np
import soundfile as sf
import librosa, torch

# --- 补丁 ---
ffmpeg_bin = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [ffmpeg_bin, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_safe_polish():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V11_PRODUCTION_READY.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v11_safe_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8-sig") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[Safe-Polish] 正在执行稳健版配音重制...")

    valid_segments = []
    for i in range(3):
        item = data[i]
        zh_text = item.get('zh', '').strip()
        final_text = zh_text + "。"
        seed = role_lib.get(item['speaker'])
        
        if seed:
            print(f"  -> 渲染 Seg_{i}...")
            wav = db.model.generate(text=final_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            
            raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # --- 核心修正：只做淡入淡出，不做静默切割 ---
            polished_p = os.path.join(temp_dir, f"polished_{i}.wav")
            # 获取物理时长
            data_wav, sr = sf.read(raw_p)
            dur = len(data_wav) / sr
            fade_out_st = max(0, dur - 0.2)
            
            cmd_fade = [ffmpeg_bin, "-y", "-i", raw_p, "-af", f"afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2", polished_p]
            subprocess.run(cmd_fade, check=True, capture_output=True)
            
            if os.path.exists(polished_p) and os.path.getsize(polished_p) > 1000:
                valid_segments.append(polished_p)
                print(f"     ✅ 片段 {i} 渲染成功 ({os.path.getsize(polished_p)} bytes)")

    # 合并
    output_wav = r"E:\VideoTranslator_Project\output_final\V11_3_SAFE_VERIFY.wav"
    combined = []
    for p in valid_segments:
        combined.append(sf.read(p)[0])
    
    if combined:
        sf.write(output_wav, np.concatenate(combined), db.sample_rate)
        print(f"\n🏆 稳健版试听音轨已产出：{output_wav}")
    else:
        print("❌ 合并失败。")

if __name__ == "__main__":
    run_safe_polish()
