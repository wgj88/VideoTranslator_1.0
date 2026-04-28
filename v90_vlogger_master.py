# -*- coding: utf-8 -*-
import os, sys, json, subprocess, time
import soundfile as sf
import librosa
import numpy as np

# --- 物理路径锁死 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v90_vlogger_master():
    print("\n" + "🎤"*10 + " V90 博主重塑版：吐槽音频压制 " + "🎤"*10)
    
    script_p = r"E:\VideoTranslator_Project\blackwell_vlog\scripts\V90_VLOGGER_SCRIPT.json"
    seed_wav = r"E:\VideoTranslator_Project\unhinged_tech\seeds\ultra_pure_seed.wav"
    output_wav = r"E:\VideoTranslator_Project\output_final\V90_VLOGGER_吐槽版_SAMPLE.wav"
    
    db = VideoCloneDubber()
    with open(script_p, "r", encoding="utf-8") as f: data = json.load(f)
    results = []
    
    for i, item in enumerate(data):
        # 1. GPU 生成 (注入博主之魂)
        # 去掉句尾多余标点，配合物理断电
        text = item['zh'].strip("！。？， ")
        wav = db.model.generate(text=text, reference_wav_path=seed_wav, inference_timesteps=20)
        raw_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v90_raw_{i}.wav"
        sf.write(raw_p, wav, db.sample_rate)
        
        # 2. V89 物理断电逻辑 (分贝监测)
        y, sr = librosa.load(raw_p)
        intervals = librosa.effects.split(y, top_db=22) # 稍微收紧阈值
        physical_end = intervals[-1][1] / sr if len(intervals) > 0 else len(y)/sr
        
        # 3. 弹性防撞检测 (V83)
        next_start = data[i+1]['start'] if i < len(data)-1 else item['end']
        available_time = next_start - item['start'] - 0.05
        
        final_p = f"E:\\VideoTranslator_Project\\blackwell_vlog\\final\\v90_clean_{i}.wav"
        if physical_end > available_time:
            tempo = physical_end / available_time
            print(f"  🚨 [Anti-Collision] 第 {i+1} 段压缩 {tempo:.2f}x")
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={physical_end},asetpts=PTS-STARTPTS,atempo={tempo},afade=t=out:st={available_time-0.05}:d=0.05", final_p]
        else:
            cmd = [FFMPEG_BIN, "-y", "-i", raw_p, "-af", f"atrim=end={physical_end+0.01},asetpts=PTS-STARTPTS,afade=t=out:st={physical_end}:d=0.01", final_p]
            
        subprocess.run(cmd, check=True, capture_output=True)
        results.append((final_p, item['start']))
        print(f"  ✅ [{i+1}/5] {item['zh']}")

    # 4. 商业缝合
    input_args = []
    filter_parts = []
    for idx, (p, start_t) in enumerate(results):
        input_args.extend(["-i", p])
        filter_parts.append(f"[{idx}:a]adelay={int(start_t*1000)}|{int(start_t*1000)}[a{idx}]")
    
    mix_str = "".join([f"[a{k}]" for k in range(len(results))]) + f"amix=inputs={len(results)}"
    subprocess.run([FFMPEG_BIN, "-y"] + input_args + ["-filter_complex", ";".join(filter_parts) + ";" + mix_str, output_wav], check=True)
    
    print(f"\n🏆 V90 博主重塑版已就绪：{output_wav}")

if __name__ == "__main__":
    run_v90_vlogger_master()
