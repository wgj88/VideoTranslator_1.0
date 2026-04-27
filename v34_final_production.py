# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 补丁 ---
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

def run_v34_crisp_production():
    print(f"\n[V34-Final] 正在铸造最终【极简·高清】版作品...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V34_CRISP_SCRIPT.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v34_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    for i, item in enumerate(data):
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed_wav = os.path.join(r"E:\VideoTranslator_Project\temp_factory", f"GENE_CLEAN_{spk}.wav")
        
        if os.path.exists(seed_wav):
            print(f"  -> [{i+1}/{len(data)}] 手术克隆 {spk}: {zh_text[:10]}...")
            # 1. 50-Step 深度生成
            wav = db.model.generate(text=zh_text + "。", reference_wav_path=seed_wav, inference_timesteps=50)
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 2. AI 外科手术 (V16 阻断技术)
            res = auditor.transcribe(raw_p)
            start_t = res['segments'][0]['start'] if res['segments'] else 0.0
            end_t = res['segments'][-1]['end'] if res['segments'] else len(wav)/db.sample_rate
            
            # 强制切割杂音
            final_p = os.path.join(audio_dir, f"v34_seg_{i}.wav")
            dur_actual = end_t - start_t
            cmd_trim = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=start={start_t}:end={end_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, dur_actual-0.1)}:d=0.1",
                final_p
            ]
            subprocess.run(cmd_trim, check=True, capture_output=True)
            item['v34_path'] = final_p

    # --- 终极混音 ---
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    output_video = r"E:\VideoTranslator_Project\output_final\V34_ULTIMATE_CRISP_MASTER.mp4"
    
    input_args = []
    filter_parts = []
    valid_list = [it for it in data if 'v34_path' in it]
    for idx, item in enumerate(valid_list):
        input_args.extend(["-i", item['v34_path']])
        delay = int(item['start'] * 1000)
        filter_parts.append(f"[{idx}:a]adelay={delay}|{delay}[a{idx}]")
    
    mix_zh = "".join([f"[a{k}]" for k in range(len(valid_list))]) + f"amix=inputs={len(valid_list)}:duration=longest,volume={len(valid_list)}"
    temp_zh = r"E:\VideoTranslator_Project\temp_factory\v34_zh_full.wav"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh, temp_zh], check=True, capture_output=True)

    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", v_mp4, "-i", temp_zh, "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.4[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 V34 终极极简版已诞生：{output_video}")

if __name__ == "__main__":
    run_v34_crisp_production()
