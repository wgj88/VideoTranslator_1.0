# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf

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

def run_v33_ultimate_master():
    print(f"\n" + "💎"*10 + " 正在铸造 V33 【官方正典·旗舰版】 " + "💎"*10)
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    audio_dir = r"E:\VideoTranslator_Project\temp_factory\v33_final_wavs"
    os.makedirs(audio_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    db = VideoCloneDubber()
    
    print("\n[Step 1] 正在启动 50-Step 深度推理渲染流水线...")
    print("注意：本过程极度消耗显卡性能，请耐心等待全篇合成。")

    for i, item in enumerate(data):
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        # 使用净化后的种子
        seed_wav = os.path.join(r"E:\VideoTranslator_Project\temp_factory", f"GENE_CLEAN_{spk}.wav")
        
        if os.path.exists(seed_wav):
            print(f"  -> [{i+1}/{len(data)}] 深度复刻 {spk}: {zh_text[:10]}...")
            
            # --- 核心改进：应用 V32 官方验证成功的参考模式 ---
            # reference_wav_path = 结构化风格克隆
            # inference_timesteps = 50 极致质量
            wav = db.model.generate(
                text=zh_text + "。",
                reference_wav_path=seed_wav,
                inference_timesteps=50,
                cfg_value=2.0
            )
            
            raw_p = os.path.join(audio_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # 物理加固
            polished_p = os.path.join(audio_dir, f"v33_seg_{i}.wav")
            dur = len(wav) / db.sample_rate
            fade_out_st = max(0, (dur - 0.15) - 0.2)
            cmd_fade = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=start=0.15,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2", polished_p]
            subprocess.run(cmd_fade, check=True, capture_output=True)
            item['v33_path'] = polished_p

    # --- Step 2: 最终大合成 ---
    print("\n[Step 2] 正在执行全篇物理级混音...")
    bgm_file = r"C:\Users\Administrator\separated_audio\pure_bgm.wav"
    v_mp4 = r"E:\VideoTranslator_Project\raw_videos\Vlog ｜ New technology paves way for better life at CICPE.mp4"
    temp_zh_track = r"E:\VideoTranslator_Project\temp_factory\v33_zh_full.wav"
    output_video = r"E:\VideoTranslator_Project\output_final\V33_ULTIMATE_FINAL_MASTER.mp4"
    
    input_args = []
    filter_parts = []
    for i, item in enumerate(data):
        if 'v33_path' in item:
            input_args.extend(["-i", item['v33_path']])
            delay = int(item['start'] * 1000)
            filter_parts.append(f"[{len(input_args)//2 - 1}:a]adelay={delay}|{delay}[a{i}]")
    
    mix_zh_str = "".join([f"[a{k}]" for k in range(len(data))]) + f"amix=inputs={len(data)}:duration=longest,volume={len(data)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_zh_str, temp_zh_track], check=True, capture_output=True)

    # 封装回视频
    cmd_pack = [
        FFMPEG_BIN, "-y", "-i", v_mp4, "-i", temp_zh_track, "-i", bgm_file,
        "-filter_complex", "[1:a]volume=1.5[zh];[2:a]volume=0.15[bg];[zh][bg]amix=inputs=2:duration=first[out]",
        "-map", "0:v", "-map", "[out]", "-c:v", "copy", "-c:a", "aac", output_video
    ]
    subprocess.run(cmd_pack, check=True)
    print(f"\n🏆 巅峰之作已诞生：{output_video}")

if __name__ == "__main__":
    run_v33_ultimate_master()
