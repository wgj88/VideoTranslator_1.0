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

def run_ultimate_production_dubbing():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V11_PRODUCTION_READY.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)

    db = VideoCloneDubber()
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v11_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)

    print(f"\n[Final-Dub] 正在启动全篇 33 句【原音色复刻】渲染计划...")

    for i, item in enumerate(data):
        zh_text = item.get('zh', '').strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/33] 正在复刻 {spk}: {zh_text[:15]}...")
            # 物理消噪与闭合
            clean_text = "……" + zh_text + "。"
            
            try:
                wav = db.model.generate(text=clean_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
                out_p = os.path.join(audio_dir, f"v11_final_{i}.wav")
                sf.write(out_p, wav, db.sample_rate)
                item['dub_path'] = out_p
            except Exception as e:
                print(f"     ❌ 片段 {i} 失败: {e}")

    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n🏆 全篇配音完成！")

if __name__ == "__main__":
    run_ultimate_production_dubbing()
