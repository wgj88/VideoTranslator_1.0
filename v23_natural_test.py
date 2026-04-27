# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 环境锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v23_natural_attack():
    print(f"\n[V23-Natural] 正在重制：增加 100ms 冗余以修复“起手过快”问题...")
    
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v23_single"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(role_lib_path, "r") as f: role_lib = json.load(f)
    seed = role_lib['SPEAKER_00']
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    test_zh = "带你逛今年博览会！"
    # 更换诱饵为更稳健的短句
    decoy_text = "好的。" + test_zh
    
    # 1. 生成
    wav = db.model.generate(text=decoy_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
    raw_p = os.path.join(temp_dir, "raw_v23.wav")
    sf.write(raw_p, wav, db.sample_rate)
    
    # 2. 审计
    res = auditor.transcribe(raw_p, word_timestamps=True)
    all_words = []
    for seg in res['segments']:
        if 'words' in seg: all_words.extend(seg['words'])
    
    # 我们要跳过“好的” (通常前两个词是 好、的)
    start_t = 0.8
    end_t = len(wav) / db.sample_rate
    
    if len(all_words) > 2:
        # 核心改进：向左多留 100ms 的气口
        start_t = max(0, all_words[2]['start'] - 0.10) 
        end_t = all_words[-1]['end'] + 0.05
    
    print(f"     📍 优化后切割区间: {start_t:.3f}s -> {end_t:.3f}s (含 100ms 保护区)")
    
    # 3. 物理合成
    output_wav = r"E:\VideoTranslator_Project\output_final\V23_NATURAL_START_FIX.wav"
    dur_target = end_t - start_t
    
    cmd_lock = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start={start_t}:end={end_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={max(0, dur_target-0.1)}:d=0.1",
        output_wav
    ]
    subprocess.run(cmd_lock, check=True, capture_output=True)
    print(f"\n🏆 自然起手版已产出：{output_wav}")

if __name__ == "__main__":
    run_v23_natural_attack()
