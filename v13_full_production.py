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

def run_v13_full_production():
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v13_full_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    print(f"\n[V13-Full] 正在启动全篇【稳态净化】量产计划...")

    for i, item in enumerate(data):
        zh_text = item.get('zh', '').strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/{len(data)}] 渲染净化片段: {zh_text[:10]}...")
            
            # 1. 稳态引导语
            steady_text = "呃。" + zh_text + "。"
            wav = db.model.generate(text=steady_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 2. 物理手术切割
            vacuum_p = os.path.join(audio_dir, f"v13_seg_{i}.wav")
            dur = len(wav) / db.sample_rate
            # 扣除切掉的0.5s后的可用时长
            fade_out_st = max(0, (dur - 0.5) - 0.2)
            
            cmd_vacuum = [
                ffmpeg_bin, "-y", "-i", raw_p,
                "-af", f"atrim=start=0.5,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2",
                vacuum_p
            ]
            subprocess.run(cmd_vacuum, check=True, capture_output=True)
            item['v13_path'] = vacuum_p

    # 3. 终极合成
    print("\n[V13-Mixer] 正在生成全长汉化总音轨...")
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    temp_zh_track = r"E:\VideoTranslator_Project\temp_factory\v13_zh_full_track.wav"
    
    input_args = []
    filter_parts = []
    for i, item in enumerate(data):
        if 'v13_path' in item:
            input_args.extend(["-i", item['v13_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{len(input_args)//2 - 1}:a]adelay={delay}|{delay}[a{i}]")
    
    num_inputs = len(input_args) // 2
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    
    cmd_zh = [ffmpeg_bin, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh_track]
    subprocess.run(cmd_zh, check=True, capture_output=True)

    # 叠入 BGM
    output_wav = r"E:\VideoTranslator_Project\output_final\V13_FULL_VACUUM_MASTER.wav"
    cmd_final = [
        ffmpeg_bin, "-y",
        "-i", temp_zh_track,
        "-i", bgm_file,
        "-filter_complex", "[0:a]volume=1.4[zh];[1:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_final, check=True, capture_output=True)
    print(f"\n🏆 V13 终极全长音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_v13_full_production()
