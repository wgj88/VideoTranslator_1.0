# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

# --- 环境锁定 ---
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

def run_v31_full_production():
    print(f"\n[V31-Full] 正在启动【原基因回归】全篇量产流水线...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v31_full_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[Action] 正在对 21 个片段执行无损渲染与物理加固...")

    for i, item in enumerate(data):
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/{len(data)}] 复刻 {spk}: {zh_text[:12]}...")
            # 1. 渲染 (使用原始种子路径 seed['wav'])
            wav = db.model.generate(text=zh_text + "。", prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 2. 物理加固 (V25/V31 验证配方)
            # atrim=start=0.15 绝杀泄露
            polished_p = os.path.join(audio_dir, f"v31_seg_{i}.wav")
            dur = len(wav) / db.sample_rate
            fade_out_st = max(0, (dur - 0.15) - 0.2)
            cmd_fade = [
                FFMPEG_BIN, "-y", "-i", raw_p, 
                "-af", f"atrim=start=0.15,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2", 
                polished_p
            ]
            subprocess.run(cmd_fade, check=True, capture_output=True)
            item['v31_path'] = polished_p

    # 3. 终极母带混音
    print("\n[Mixer] 正在产出 2.5 分钟终极汉化音轨...")
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    temp_zh_track = r"E:\VideoTranslator_Project\temp_factory\v31_zh_full.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V31_ULTIMATE_PROD_MASTER.wav"
    
    input_args = []
    filter_parts = []
    for i, item in enumerate(data):
        if 'v31_path' in item:
            input_args.extend(["-i", item['v31_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{len(input_args)//2 - 1}:a]adelay={delay}|{delay}[a{i}]")
    
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh_track], check=True, capture_output=True)

    # 叠加 BGM
    cmd_final = [
        FFMPEG_BIN, "-y",
        "-i", temp_zh_track,
        "-i", bgm_file,
        "-filter_complex", "[0:a]volume=1.4[zh];[1:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_final, check=True, capture_output=True)
    print(f"\n🏆 V31 终极纯净音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_v31_full_production()
