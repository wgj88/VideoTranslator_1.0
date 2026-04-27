# -*- coding: utf-8 -*-
import os, sys, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v25_smooth():
    print(f"\n[V25-Smooth] 正在执行【丝滑连读】重制：撤销辅助标点...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_path, "r") as f: 
        import json
        role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()

    # 1. 还原纯净文本
    test_zh = "带你逛今年博览会！"
    
    print(f"  -> [步骤 1] 正在生成原始渲染 (回归原始翻译语序)...")
    wav = db.model.generate(text=test_zh + "。", prompt_wav_path=seed['wav'], prompt_text=seed['text'])
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v25_single\raw_v25.wav"
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    sf.write(raw_p, wav, db.sample_rate)
    
    # 2. 物理加固
    output_wav = r"E:\VideoTranslator_Project\output_final\V25_SMOOTH_DUB.wav"
    dur = len(wav) / db.sample_rate
    fade_out_st = max(0, (dur - 0.15) - 0.2)

    cmd_safe = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2",
        output_wav
    ]
    subprocess.run(cmd_safe, check=True, capture_output=True)
    
    print(f"✅ V25 渲染完成。成品路径: {output_wav}")

if __name__ == "__main__":
    run_v25_smooth()
