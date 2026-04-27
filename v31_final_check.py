# -*- coding: utf-8 -*-
import os, sys, json, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v31_final_check():
    print(f"\n[V31-Final] 正在执行【无损基因回归】重制测试...")
    
    # 物理读取最原始的库
    lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(lib_path, "r") as f: role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()
    # 这一句是之前崩溃的重灾区
    target_text = "赶紧坐下吧！"
    
    print(f"  -> 正在使用【100% 原始种子】渲染: {target_text}")
    # 不加任何诱导词，直接上原始台词
    wav = db.model.generate(text=target_text + "。", prompt_wav_path=seed['wav'], prompt_text=seed['text'])
    
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v31\raw_v31.wav"
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    sf.write(raw_p, wav, db.sample_rate)
    
    # 应用 V25 证明有效的物理加固 (切除起手杂音单词)
    output_wav = r"E:\VideoTranslator_Project\output_final\V31_NO_LOSS_GENE_VERIFY.wav"
    dur = len(wav) / db.sample_rate
    cmd_safe = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={max(0, dur-0.25)}:d=0.2",
        output_wav
    ]
    subprocess.run(cmd_safe, check=True, capture_output=True)
    print(f"🏆 V31 验证版已产出：{output_wav}")

if __name__ == "__main__":
    run_v31_final_check()
