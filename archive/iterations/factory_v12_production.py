# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

# --- 1. 物理环境与补丁 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v12_final_production():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_PURIFIED_NEWS_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v12_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[V12.0] 正在启动【新闻级】全篇汉化配音渲染 (共 {len(data)} 段)...")

    valid_segments = []
    for i, item in enumerate(data):
        zh_text = item['zh']
        spk = item['speaker']
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/{len(data)}] [{spk}] 配音中: {zh_text[:12]}...")
            # 双端静默引导
            target_text = "……" + zh_text + "。"
            
            try:
                # 克隆生成
                wav = db.model.generate(text=target_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
                raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
                sf.write(raw_p, wav, db.sample_rate)
                
                # 物理消噪 + 强制淡出
                clean_p = os.path.join(temp_dir, f"clean_{i}.wav")
                subprocess.run([FFMPEG_BIN, "-y", "-i", raw_p, "-af", "silenceremove=stop_periods=1:stop_duration=0.05:stop_threshold=-45dB,afade=t=out:st=1.3:d=0.1", clean_p], capture_output=True)
                
                # 时间轴对齐
                delay = int(item['start'] * 1000)
                aligned_p = os.path.join(temp_dir, f"aligned_{i}.wav")
                subprocess.run([FFMPEG_BIN, "-y", "-i", clean_p, "-af", f"adelay={delay}|{delay}", aligned_p], check=True, capture_output=True)
                
                item['dub_path'] = aligned_p
                valid_segments.append(aligned_p)
            except: pass

    # 终极混音
    print("\n[Mixer] 正在生成全篇终极混音音轨...")
    output_wav = r"E:\VideoTranslator_Project\output_final\V12_ULTIMATE_PURE_CHINESE.wav"
    
    input_args = ["-i", bgm_file]
    for s in valid_segments: input_args.extend(["-i", s])
    
    mix_zh = "".join([f"[{k+1}:a]" for k in range(len(valid_segments))])
    # 中文合并 -> 增益补偿 -> 侧链压制 BGM
    filter_complex = f"{mix_zh}amix=inputs={len(valid_segments)}:duration=longest,volume={len(valid_segments)}[zh_full];"
    filter_complex += f"[0:a][zh_full]sidechaincompress=threshold=0.01:ratio=20[bg_low];"
    filter_complex += "[bg_low][zh_full]amix=inputs=2:weights='0.15 1.0'[out]"
    
    cmd = [FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", filter_complex, "-map", "[out]", output_wav]
    subprocess.run(cmd, check=True)
    
    print(f"\n🏆 V12.0 终极纯净版音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_v12_final_production()
