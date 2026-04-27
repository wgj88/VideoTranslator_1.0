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

def run_v13_vacuum_dubbing():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v13_vacuum_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[V13-Vacuum] 正在启动【稳态切割】净化重制...")

    valid_wavs = []
    for i in range(2): # 先测试前 2 句
        item = data[i]
        zh_text = item.get('zh', '').strip()
        seed = role_lib.get(item['speaker'])
        
        if seed:
            # --- 核心改进 A：稳态引导语 ---
            # 用“呃”作为前导牺牲品，承接所有泄露音节
            steady_text = "呃。" + zh_text + "。"
            print(f"  -> 净化渲染 Seg_{i}: {zh_text}")
            
            wav = db.model.generate(text=steady_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # --- 核心改进 B：物理外科手术切除 ---
            # 我们物理切掉开头的 0.5s (那里包含了“呃”和泄露的英文音节)
            # 并且在末尾执行极速熔断
            vacuum_p = os.path.join(temp_dir, f"vacuum_{i}.wav")
            
            # 获取总时长
            dur = len(wav) / db.sample_rate
            fade_out_st = max(0, (dur - 0.5) - 0.2) # 相对于切除后的起点
            
            # 解释：atrim=start=0.5 (切除开头), afade (首尾平滑)
            cmd_vacuum = [
                ffmpeg_bin, "-y", "-i", raw_p,
                "-af", f"atrim=start=0.5,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2",
                vacuum_p
            ]
            subprocess.run(cmd_vacuum, check=True, capture_output=True)
            valid_wavs.append(vacuum_p)

    # 合并验证
    output_wav = r"E:\VideoTranslator_Project\output_final\V13_VACUUM_VERIFY.wav"
    combined = np.concatenate([sf.read(p)[0] for p in valid_wavs])
    sf.write(output_wav, combined, db.sample_rate)
    print(f"\n🏆 V13 稳态切割音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_v13_vacuum_dubbing()
