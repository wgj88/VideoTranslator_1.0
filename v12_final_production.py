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

def run_v12_final_production():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v12_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[Production-V12] 正在启动【完美标点版】全篇复刻...")

    for i, item in enumerate(data):
        zh_text = item.get('zh', '').strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/{len(data)}] 复刻 {spk}: {zh_text[:12]}...")
            
            # 物理渲染
            wav = db.model.generate(text=zh_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 双端物理淡入淡出 (V11.3 Safe Recipe)
            polished_p = os.path.join(audio_dir, f"v12_seg_{i}.wav")
            dur = len(wav) / db.sample_rate
            fade_out_st = max(0, dur - 0.2)
            cmd_fade = [ffmpeg_bin, "-y", "-i", raw_p, "-af", f"afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2", polished_p]
            subprocess.run(cmd_fade, check=True, capture_output=True)
            
            item['dub_path'] = polished_p

    # 保存最终带路径的剧本
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 全篇完美配音已全部完成！共计 {len(data)} 个高净空片段。")

if __name__ == "__main__":
    run_v12_final_production()
