# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 暴力路径锁定 ---
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

def run_v17_master_production():
    print(f"\n[V17-Master] 正在启动【多角色+AI手术】全量净化量产...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v17_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    for i, item in enumerate(data):
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/{len(data)}] 手术克隆 {spk}: {zh_text[:10]}...")
            # 1. 克隆渲染
            wav = db.model.generate(text=zh_text + "。", prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 2. AI 寻踪定位 (寻找真实中文区间)
            res = auditor.transcribe(raw_p)
            start_t = res['segments'][0]['start'] if res['segments'] else 0.0
            end_t = res['segments'][-1]['end'] if res['segments'] else len(wav)/db.sample_rate
            
            # 增加安全冗余
            start_trim = max(0, start_t - 0.05)
            end_trim = end_t + 0.05
            
            # 3. 物理切除“杂质”
            snatched_p = os.path.join(audio_dir, f"v17_seg_{i}.wav")
            dur_target = end_trim - start_trim
            
            cmd_snatch = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=start={start_trim}:end={end_trim},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, dur_target-0.1)}:d=0.1",
                snatched_p
            ]
            subprocess.run(cmd_snatch, check=True, capture_output=True)
            item['v17_path'] = snatched_p

    # 4. 全长合成
    print("\n[V17-Mixer] 正在合成全长汉化音轨...")
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V17_ULTIMATE_CLEAN_TRACK.wav"
    
    # 构建物理拼接命令
    input_args = []
    filter_parts = []
    for i, item in enumerate(data):
        if 'v17_path' in item:
            input_args.extend(["-i", item['v17_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{len(input_args)//2 - 1}:a]adelay={delay}|{delay}[a{i}]")
    
    zh_mix_str = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    
    cmd_final = [FFMPEG_BIN, "-y"] + input_args + ["-i", bgm_file] + [
        "-filter_complex", ";".join(filter_parts) + ";" + zh_mix_str + "[zh];[zh]volume=1.4[zh_v];[" + str(len(data)) + ":a]volume=0.15[bg];[zh_v][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_final, check=True, capture_output=True)
    print(f"\n🏆 V17 终极克隆净化音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_v17_master_production()
