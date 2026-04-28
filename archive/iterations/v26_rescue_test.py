# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v26_rescue():
    print(f"\n[V26-Rescue] 正在执行第二句【逻辑重塑】手术，根治胡言乱语...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()

    # 核心改进：深度优化的口语化文本
    # 增加停顿和辅助词，强迫模型回归中文逻辑
    rescue_text = "横跨了制造、零售、美妆以及农业。这些炫酷的科技产品，正成为全场的焦点！"
    
    print(f"  -> 正在使用修正文本渲染: {rescue_text}")
    
    # 物理生成
    wav = db.model.generate(text=rescue_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v26_rescue\raw_v26_2.wav"
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    sf.write(raw_p, wav, db.sample_rate)
    
    # 物理加固：保留前后的呼吸感
    output_wav = r"E:\VideoTranslator_Project\output_final\V26_RESCUE_SEGMENT_2.wav"
    dur = len(wav) / db.sample_rate
    
    # 我们减少切割量，只切前 0.1s，防止伤到起手
    cmd_safe = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.1,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={max(0, dur-0.2)}:d=0.2",
        output_wav
    ]
    subprocess.run(cmd_safe, check=True, capture_output=True)
    
    print(f"✅ V26 救治完成。成品路径: {output_wav}")

if __name__ == "__main__":
    run_v26_rescue()
