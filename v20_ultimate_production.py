# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 环境硬路径锁定 ---
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

def run_v20_zero_noise_master():
    print(f"\n[V20-Master] 正在启动【零杂音·物理隔离】量产引擎...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v20_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    print("\n[Step 1] 正在执行【种子物理去头】手术...")
    for spk in role_lib:
        old_wav = role_lib[spk]['wav']
        # 核心改进：强制物理切除前 0.3s (绝杀起始泄露)
        trimmed_seed = os.path.join(r"E:\VideoTranslator_Project\temp_factory", f"V20_TRIMMED_{spk}.wav")
        subprocess.run([FFMPEG_BIN, "-y", "-i", old_wav, "-ss", "0.3", "-af", "afftdn=nf=-30", trimmed_seed], check=True, capture_output=True)
        # 重新校准引导词
        res = auditor.transcribe(trimmed_seed)
        role_lib[spk]['v20_seed'] = trimmed_seed
        role_lib[spk]['v20_text'] = res['text'].strip()
        print(f"  ✅ {spk} 基因已完成“物理去头”净化。")

    print("\n[Step 2] 正在执行【AI手术级】渲染...")
    for i, item in enumerate(data):
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/{len(data)}] 手术克隆 {spk}...")
            # 1. 生成
            wav = db.model.generate(text=zh_text + "。", prompt_wav_path=seed['v20_seed'], prompt_text=seed['v20_text'])
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 2. AI 定位真实中文起点
            res_aud = auditor.transcribe(raw_p)
            start_trim = res_aud['segments'][0]['start'] if res_aud['segments'] else 0.0
            end_trim = res_aud['segments'][-1]['end'] if res_aud['segments'] else len(wav)/db.sample_rate
            
            print(f"     📍 AI 物理定位: {start_trim:.2f}s -> {end_trim:.2f}s")
            
            # 3. 物理切除一切杂音
            final_p = os.path.join(audio_dir, f"v20_seg_{i}.wav")
            dur_actual = end_trim - start_trim
            cmd_trim = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=start={start_trim}:end={end_trim},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, dur_actual-0.1)}:d=0.1",
                final_p
            ]
            subprocess.run(cmd_trim, check=True, capture_output=True)
            item['v20_path'] = final_p

    # 4. 全长合成
    print("\n[Step 3] 正在合成终极纯净音轨...")
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V20_TRUE_ZERO_MASTER.wav"
    
    input_args = []
    filter_parts = []
    for i, item in enumerate(data):
        if 'v20_path' in item:
            input_args.extend(["-i", item['v20_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{len(input_args)//2 - 1}:a]adelay={delay}|{delay}[a{i}]")
    
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    
    cmd_final = [FFMPEG_BIN, "-y"] + input_args + ["-i", bgm_file] + [
        "-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str + "[zh];[zh]volume=1.4[zh_v];[" + str(len(data)) + ":a]volume=0.15[bg];[zh_v][bg]amix=inputs=2:duration=first",
        output_wav
    ]
    subprocess.run(cmd_final, check=True, capture_output=True)
    print(f"\n🏆 V20 “零杂音”终极音轨已产出：{output_wav}")

if __name__ == "__main__":
    run_v20_zero_noise_master()
