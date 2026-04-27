# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# 暴力锁定路径
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

def run_v14_ultimate():
    print(f"\n[V14-Ultimate] 正在启动【AI 手术级】净化重制...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v14_ai_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    valid_wavs = []
    for i in range(3):
        item = data[i]
        zh_text = item['zh'].strip()
        seed = role_lib.get(item['speaker'])
        
        if seed:
            print(f"  -> 渲染并手术 Seg_{i}: {zh_text[:10]}...")
            # 1. 正常生成
            wav = db.model.generate(text=zh_text + "。", prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 2. AI 寻踪
            res = auditor.transcribe(raw_p)
            start_trim = res['segments'][0]['start'] if res['segments'] else 0.05
            print(f"     📍 真实起点定位: {start_trim:.2f}s")
            
            # 3. 物理切除
            clean_p = os.path.join(temp_dir, f"clean_{i}.wav")
            dur = len(wav) / db.sample_rate
            fade_out_st = max(0, (dur - start_trim) - 0.2)
            
            cmd_clip = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=start={start_trim},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={fade_out_st}:d=0.2",
                clean_p
            ]
            subprocess.run(cmd_clip, check=True, capture_output=True)
            valid_wavs.append(clean_p)

    # 合并
    output_wav = r"E:\VideoTranslator_Project\output_final\V14_ULTIMATE_VERIFY.wav"
    combined = np.concatenate([sf.read(p)[0] for p in valid_wavs])
    sf.write(output_wav, combined, db.sample_rate)
    print(f"\n🏆 V14 手术版音轨已就绪：{output_wav}")

if __name__ == "__main__":
    run_v14_ultimate()
