# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

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

def run_polish_test():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V11_PRODUCTION_READY.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v11_polished_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[Polish] 正在执行【物理淡入+零干扰】重制...")

    valid_segments = []
    for i in range(3):
        item = data[i]
        zh_text = item.get('zh', '').strip()
        # --- 核心改进：彻底移除开头的 …… 引导 ---
        final_text = zh_text + "。"
        
        seed = role_lib.get(item['speaker'])
        if seed:
            print(f"  -> 渲染 Seg_{i}: {final_text}")
            wav = db.model.generate(text=final_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            
            raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # --- 核心改进：物理淡入 0.1s 杀掉起始音节 ---
            polished_p = os.path.join(temp_dir, f"polished_{i}.wav")
            subprocess.run([ffmpeg_bin, "-y", "-i", raw_p, "-af", "afade=t=in:st=0:d=0.1", polished_p], check=True, capture_output=True)
            valid_segments.append(polished_p)

    # 合并试听
    output_wav = r"E:\VideoTranslator_Project\output_final\V11_POLISHED_VERIFY.wav"
    combined = np.concatenate([sf.read(p)[0] for p in valid_segments])
    sf.write(output_wav, combined, db.sample_rate)
    print(f"\n🏆 净化版试听音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_polish_test()
