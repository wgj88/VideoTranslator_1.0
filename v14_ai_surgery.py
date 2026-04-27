# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

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

def run_v14_ai_surgery():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v14_ai_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    # 加载 Whisper 作为“手术导航员”
    print("\n[V14-AI] 正在初始化“声纹外科手术”导航系统...")
    auditor = whisper.load_model("base")

    valid_wavs = []
    for i in range(3):
        item = data[i]
        zh_text = item['zh'].strip()
        seed = role_lib.get(item['speaker'])
        
        if seed:
            print(f"  -> [步骤 1] 生成原始配音 Seg_{i}: {zh_text[:10]}...")
            wav = db.model.generate(text=zh_text + "。", prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # --- 核心改进：AI 导航切割 ---
            print(f"  -> [步骤 2] AI 正在定位中文起始点...")
            # 开启单词级时间轴
            res = auditor.transcribe(raw_p, verbose=False)
            
            # 默认切除 0.05s 的初始冲击波
            start_trim = 0.05
            if res['segments']:
                # 寻找第一个真正发音的时刻
                # Whisper 的 segment start 通常很准
                start_trim = res['segments'][0]['start']
            
            print(f"     📍 发现中文发音始于 {start_trim:.2f}s，正在物理切除多余信号...")
            
            clean_p = os.path.join(temp_dir, f"clean_{i}.wav")
            # 物理切割 + 极速淡入淡出
            dur = len(wav) / db.sample_rate
            fade_out_st = max(0, (dur - start_trim) - 0.2)
            
            cmd_trim = [
                ffmpeg_bin, "-y", "-i", raw_p,
                "-af", f"atrim=start={start_trim},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={fade_out_st}:d=0.2",
                clean_p
            ]
            subprocess.run(cmd_trim, check=True, capture_output=True)
            valid_wavs.append(clean_p)

    # 合并验证
    output_wav = r"E:\VideoTranslator_Project\output_final\V14_AI_SURGERY_VERIFY.wav"
    combined = np.concatenate([sf.read(p)[0] for p in valid_wavs])
    sf.write(output_wav, combined, db.sample_rate)
    print(f"\n🏆 V14 AI导航净化音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_v14_ai_surgery()
