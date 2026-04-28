# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 暴力路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v22_single_sentence():
    print(f"\n[V22-Single] 正在对首句执行【毫秒级起止锁定】手术...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v22_single"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    test_zh = "带你逛今年博览会！"
    # 诱饵引导
    decoy_text = "额。" + test_zh
    
    print(f"  -> [步骤 1] 正在生成原始波形 (包含诱饵词)...")
    wav = db.model.generate(text=decoy_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
    raw_p = os.path.join(temp_dir, "raw_single.wav")
    sf.write(raw_p, wav, db.sample_rate)
    
    print(f"  -> [步骤 2] AI 正在执行全词位审计...")
    res = auditor.transcribe(raw_p, word_timestamps=True)
    
    all_words = []
    for seg in res['segments']:
        if 'words' in seg: all_words.extend(seg['words'])
    
    # 逻辑：我们要找到真正的“带”字的起点和“会”字的终点
    # 过滤掉诱饵词“额”
    # 在这个场景下，第一个词通常是“额”，第二个词开始才是正式台词
    start_t = 0.5
    end_t = len(wav) / db.sample_rate
    
    if len(all_words) > 1:
        # 排除掉诱饵词
        start_t = all_words[1]['start'] 
        end_t = all_words[-1]['end']
    
    print(f"     📍 手术切割点：{start_t:.3f}s (开头) | {end_t:.3f}s (末尾)")
    
    # 执行物理阻断
    output_wav = r"E:\VideoTranslator_Project\output_final\V22_SINGLE_PRECISION_FIX.wav"
    dur_target = end_t - start_t
    
    cmd_lock = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start={start_t}:end={end_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, dur_target-0.05)}:d=0.05",
        output_wav
    ]
    subprocess.run(cmd_lock, check=True, capture_output=True)
    print(f"\n🏆 单句极致净化版已产出：{output_wav}")

if __name__ == "__main__":
    run_v22_single_sentence()
