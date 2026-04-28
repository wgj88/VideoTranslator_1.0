# -*- coding: utf-8 -*-
import os, sys, subprocess, json, whisper, numpy as np
import soundfile as sf

# 暴力锁定路径
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run():
    print("\n--- 🏁 正在启动 V2 深度消噪实测 ---")
    lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(lib_path, "r") as f: role_lib = json.load(f)
    
    # 1. 物理消噪
    old_wav = role_lib['SPEAKER_00']['wav']
    new_wav = r"E:\VideoTranslator_Project\temp_factory\V2_DENOISED_SEED_00.wav"
    
    # 采用高灵敏度消噪
    subprocess.run([FFMPEG_BIN, "-y", "-i", old_wav, "-af", "afftdn=nf=-30,highpass=f=100,lowpass=f=16000", new_wav], check=True)
    print("✅ 物理消噪完成。")
    
    # 2. 重新定标
    print("  -> AI 正在重新提取基因特征...")
    auditor = whisper.load_model("base")
    res = auditor.transcribe(new_wav)
    new_text = res['text'].strip()
    
    # 3. 渲染
    db = VideoCloneDubber()
    test_zh = "这是消噪后的种子测试，让我们听听起手和收尾是否还有残留杂音。"
    wav = db.model.generate(text=test_zh, prompt_wav_path=new_wav, prompt_text=new_text)
    
    out_p = r"E:\VideoTranslator_Project\output_final\V2_DENOISED_RESULT_00.wav"
    sf.write(out_p, wav, db.sample_rate)
    print(f"🏆 终极成果已产出：{out_p}")

if __name__ == "__main__":
    run()
