# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 环境锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v29_context_anchoring():
    print(f"\n[V29-Context] 正在执行【上下文联合生成】手术...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V27_ULTIMATE_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v29_context"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    # 目标片段定位：我们要救治的是 Seg 12 ("赶紧坐下吧")
    # 我们将它和 Seg 11 ("这款产品谎称...") 组合
    prev_text = data[10]['zh'] # 这款产品...
    target_text = data[11]['zh'] # 赶紧坐下吧！
    
    combined_text = prev_text + "。" + target_text
    print(f"  -> [步骤 1] 正在通过上下文锚点生成联合波形: '{combined_text}'")
    
    seed = role_lib['SPEAKER_00']
    wav = db.model.generate(text=combined_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
    raw_p = os.path.join(temp_dir, "raw_combined.wav")
    sf.write(raw_p, wav, db.sample_rate)
    
    # 2. AI 审计：寻找“赶紧”这个词的起始点
    print(f"  -> [步骤 2] AI 正在长音频中寻找目标短语的物理切口...")
    res = auditor.transcribe(raw_p, word_timestamps=True)
    
    all_words = []
    for seg in res['segments']:
        if 'words' in seg: all_words.extend(seg['words'])
    
    # 我们要寻找文字中匹配“赶紧”的那个位置
    # 逻辑：从后往前找，或者寻找特定关键词
    start_cut = 0.0
    end_cut = len(wav) / db.sample_rate
    
    # 简单的策略：寻找中间的停顿点
    # 在这个例子中，目标文本大约在后 1/4
    # 我们找“赶紧”这两个字
    for w in all_words:
        if "赶紧" in w['word'] or "坐下" in w['word']:
            start_cut = w['start'] - 0.1 # 留一点气口
            break
    
    end_cut = all_words[-1]['end'] + 0.1
    
    print(f"     📍 成功锚定！目标短语物理区间: {start_cut:.3f}s -> {end_cut:.3f}s")
    
    # 3. 物理切片提取
    output_wav = r"E:\VideoTranslator_Project\output_final\V29_ANCHORED_PHRASE.wav"
    dur = end_cut - start_cut
    
    cmd_snatch = [
        FFMPEG_BIN, "-y", "-i", raw_p,
        "-af", f"atrim=start={start_cut}:end={end_cut},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.1,afade=t=out:st={max(0, dur-0.1)}:d=0.1",
        output_wav
    ]
    subprocess.run(cmd_snatch, check=True, capture_output=True)
    print(f"\n🏆 上下文锚定版短语已产出：{output_wav}")

if __name__ == "__main__":
    run_v29_context_anchoring()
