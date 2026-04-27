# -*- coding: utf-8 -*-
import os, sys, subprocess, numpy as np, soundfile as sf

FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v24_robust():
    print(f"\n[V24-Robust] 正在执行【稳健播音】重制：物理冗余优先...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    with open(role_lib_path, "r") as f: 
        import json
        role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()

    # 1. 文本层面纠偏：加入更多的标点停顿，物理强迫模型减速
    # 原句：带你逛今年博览会！
    # 改为：带你，逛一逛，今年的，博览会！
    test_zh = "带你，逛一逛，今年的，博览会！"
    
    print(f"  -> [步骤 1] 正在生成原始渲染 (带呼吸感引导)...")
    wav = db.model.generate(text=test_zh, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
    raw_p = r"E:\VideoTranslator_Project\temp_factory\v24_single\raw_v24.wav"
    os.makedirs(os.path.dirname(raw_p), exist_ok=True)
    sf.write(raw_p, wav, db.sample_rate)
    
    # 2. 物理冗余切割：不再靠 Whisper 猜，只执行固定安全头切除
    # 只切掉最开头的 0.15s (防泄露单词)，保留后面所有
    output_wav = r"E:\VideoTranslator_Project\output_final\V24_ROBUST_DUB.wav"
    dur = len(wav) / db.sample_rate
    fade_out_st = max(0, (dur - 0.15) - 0.2)

    cmd_safe = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start=0.15,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={fade_out_st}:d=0.2",
        output_wav
    ]
    subprocess.run(cmd_safe, check=True, capture_output=True)
    
    # 输出实际生成的音频长度供参考
    import librosa
    y, sr = librosa.load(output_wav, sr=None)
    print(f"✅ V24 渲染完成。成品实际时长: {len(y)/sr:.2f}s")
    print(f"🏆 成品路径: {output_wav}")

if __name__ == "__main__":
    run_v24_robust()
