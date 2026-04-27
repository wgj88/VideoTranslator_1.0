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

def run_ultimate_clipping():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V11_PRODUCTION_READY.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v11_clipped_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8-sig") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[Clipping] 正在执行【双端物理熔断】测试...")

    valid_segments = []
    for i in range(3):
        item = data[i]
        zh_text = item.get('zh', '').strip()
        # 末尾加上强力停顿符
        final_text = zh_text + "。"
        
        seed = role_lib.get(item['speaker'])
        if seed:
            print(f"  -> 物理熔断渲染 Seg_{i}...")
            wav = db.model.generate(text=final_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            
            raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # --- 核心改进：双端物理熔断 ---
            # 1. 自动去除首尾静默 (切掉模型产生的幻觉空白)
            # 2. 0.1s 开头淡入 (杀掉起手多余音节)
            # 3. 0.2s 末尾淡出 (抹平尾部补词幻觉)
            clipped_p = os.path.join(temp_dir, f"clipped_{i}.wav")
            
            # 获取动态时长
            proc = subprocess.run([ffmpeg_bin, "-i", raw_p], capture_output=True, text=True)
            dur_match = re.search(r"Duration:\s(\d+):(\d+):(\d+\.\d+)", proc.stderr)
            dur = float(dur_match.group(3)) if dur_match else 2.0
            
            fade_out_start = max(0, dur - 0.2)
            
            cmd_clip = [
                ffmpeg_bin, "-y", "-i", raw_p,
                "-af", f"silenceremove=start_periods=1:start_threshold=-50dB:stop_periods=1:stop_threshold=-50dB,afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_start}:d=0.2",
                clipped_p
            ]
            subprocess.run(cmd_clip, check=True, capture_output=True)
            valid_segments.append(clipped_p)

    # 合并试听
    output_wav = r"E:\VideoTranslator_Project\output_final\V11_2_CLIPPED_VERIFY.wav"
    combined = np.concatenate([sf.read(p)[0] for p in valid_segments])
    sf.write(output_wav, combined, db.sample_rate)
    print(f"\n🏆 双端熔断版已产出：{output_wav}")

if __name__ == "__main__":
    run_ultimate_clipping()
