# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v28_short_phrase_rescue():
    print(f"\n[V28-ShortRescue] 正在救治极短句“Just sit down”产生的胡言乱语...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()

    # --- 核心改进：语义扩容，让模型有“呼吸感” ---
    # 我们把原来的“赶紧坐下吧”扩展为更有逻辑感、更长的句子
    expanded_text = "你只需要赶紧坐下来，亲身感受一下吧！"
    
    print(f"  -> 正在使用扩容文本渲染: {expanded_text}")
    
    # 使用净化过的种子进行渲染
    clean_seed_wav = r"E:\VideoTranslator_Project\temp_factory\GENE_CLEAN_SPEAKER_00.wav"
    
    wav = db.model.generate(text=expanded_text, prompt_wav_path=clean_seed_wav, prompt_text=seed['text'])
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v28_rescue\raw_v28_sit.wav"
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    sf.write(raw_p, wav, db.sample_rate)
    
    # 物理加固
    output_wav = r"E:\VideoTranslator_Project\output_final\V28_RESCUED_SIT_DOWN.wav"
    dur = len(wav) / db.sample_rate
    
    cmd_safe = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={max(0, dur-0.25)}:d=0.2",
        output_wav
    ]
    subprocess.run(cmd_safe, check=True, capture_output=True)
    
    print(f"✅ V28 救治完成。成品路径: {output_wav}")

if __name__ == "__main__":
    run_v28_short_phrase_rescue()
