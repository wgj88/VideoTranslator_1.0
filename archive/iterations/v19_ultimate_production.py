# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 1. 暴力环境锁定 ---
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

def run_v19_ultimate_master():
    print(f"\n[V19-Master] 正在启动【终极全量产】汉化计划...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v19_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    print("\n[Step 1] 正在执行【全角色基因净化】...")
    # 对所有种子进行深度降噪
    for spk in role_lib:
        old_wav = role_lib[spk]['wav']
        clean_wav = os.path.join(r"E:\VideoTranslator_Project\temp_factory", f"GENE_CLEAN_{spk}.wav")
        subprocess.run([FFMPEG_BIN, "-y", "-i", old_wav, "-af", "afftdn=nf=-30,highpass=f=100,lowpass=f=16000", clean_wav], check=True, capture_output=True)
        # 重新识别净化后的引导词
        res = auditor.transcribe(clean_wav)
        role_lib[spk]['clean_wav'] = clean_wav
        role_lib[spk]['clean_text'] = res['text'].strip()
        print(f"  ✅ {spk} 基因已净化。")

    print("\n[Step 2] 正在执行【全篇净化渲染】...")
    for i, item in enumerate(data):
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/{len(data)}] 复刻 {spk}: {zh_text[:10]}...")
            # 渲染
            wav = db.model.generate(text=zh_text, prompt_wav_path=seed['clean_wav'], prompt_text=seed['clean_text'])
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 物理淡入淡出净化
            final_p = os.path.join(audio_dir, f"v19_seg_{i}.wav")
            dur = len(wav) / db.sample_rate
            fade_out_st = max(0, dur - 0.2)
            cmd_fade = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2", final_p]
            subprocess.run(cmd_fade, check=True, capture_output=True)
            item['v19_path'] = final_p

    # 3. 总混音
    print("\n[Step 3] 正在合成全长音轨...")
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    temp_zh_track = r"E:\VideoTranslator_Project\temp_factory\v19_zh_full.wav"
    
    input_args = []
    filter_parts = []
    for i, item in enumerate(data):
        if 'v19_path' in item:
            input_args.extend(["-i", item['v19_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{len(input_args)//2 - 1}:a]adelay={delay}|{delay}[a{i}]")
    
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh_track], check=True, capture_output=True)

    # 4. 最终视频压制
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    output_video = r"E:\VideoTranslator_Project\output_final\V19_FINAL_COMMERCIAL_MASTER.mp4"
    
    # 终极混合命令
    cmd_pack = [
        FFMPEG_BIN, "-y",
        "-i", v_mp4,
        "-i", temp_zh_track,
        "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]",
        "-c:v", "copy", "-c:a", "aac",
        output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V19 终极成品视频已产出：{output_video}")

if __name__ == "__main__":
    run_v19_ultimate_master()
