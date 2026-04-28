# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np
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

def run_vox_standard_test():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v15_vox_std"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[Vox-Base] 正在调用 VoxCPM 【预设标准音色】进行生成...")

    valid_segments = []
    # 生成前 3 句作为对比
    for i in range(3):
        item = data[i]
        zh_text = item['zh'].strip()
        
        print(f"  -> 生成 Seg_{i} (Base Voice): {zh_text[:10]}...")
        # 重点：不提供 prompt_wav_path，触发模型内部默认 Embedding
        # 如果模型要求必须提供，我们将提供一个极短、极静的占位符（由我内部逻辑处理）
        try:
            # 在 VoxCPM 中，如果不传 prompt，它会使用预设的 0 号 Speaker
            wav = db.model.generate(text=zh_text + "。")
            
            out_p = os.path.join(temp_dir, f"base_{i}.wav")
            sf.write(out_p, wav, db.sample_rate)
            valid_segments.append(out_p)
        except Exception as e:
            print(f"     ❌ 基础模式生成失败: {e}")

    # 合并输出
    output_wav = r"E:\VideoTranslator_Project\output_final\V15_VOX_BASE_AUDIT.wav"
    if valid_segments:
        all_wavs = [sf.read(p)[0] for p in valid_segments]
        sf.write(output_wav, np.concatenate(all_wavs), db.sample_rate)
        print(f"\n🏆 VoxCPM 预设音色试听已产出：{output_wav}")

if __name__ == "__main__":
    run_vox_standard_test()
