# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 暴力路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v22_triple_lock():
    print(f"\n[V22-TripleLock] 正在启动【三重锁死】净化生产线...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    role_lib_path = r"E:\VideoTranslator_Project\temp_factory\v9_role_library.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v22_lock_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    with open(role_lib_path, "r", encoding="utf-8") as f: role_lib = json.load(f)
    
    db = VideoCloneDubber()
    auditor = whisper.load_model("base")

    valid_wavs = []
    # 我们针对您反馈的“首句粘连”和“末尾幻觉”最严重的片段进行实测
    for i in range(min(5, len(data))):
        item = data[i]
        zh_text = item['zh'].strip()
        spk = item.get('speaker', 'SPEAKER_00')
        seed = role_lib.get(spk)
        
        if seed:
            print(f"  -> [{i+1}/5] 三重锁死渲染 {spk}: {zh_text[:10]}...")
            
            # --- 锁 1：诱饵文本 ---
            decoy_text = "额。" + zh_text + "。"
            
            # 渲染
            wav = db.model.generate(text=decoy_text, prompt_wav_path=seed['wav'], prompt_text=seed['text'])
            raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
            sf.write(raw_p, wav, db.sample_rate)
            
            # --- 锁 2：AI 单词级溯源 ---
            # 我们通过 Whisper 寻找“额”之后第一个词的起点，以及最后一个词的终点
            res = auditor.transcribe(raw_p, word_timestamps=True)
            
            # 逻辑：跳过第一个词（诱饵词），从第二个词开始截取
            start_t = 0.5 # 默认兜底
            end_t = len(wav) / db.sample_rate
            
            if res['segments']:
                all_words = []
                for seg in res['segments']:
                    if 'words' in seg: all_words.extend(seg['words'])
                
                if len(all_words) > 1:
                    # 跳过“额”这个词
                    start_t = all_words[1]['start'] 
                    # 最后一个词的物理终点
                    end_t = all_words[-1]['end']
            
            print(f"     📍 物理锁死区间: {start_t:.2f}s -> {end_t:.2f}s (已剔除诱饵与幻觉)")
            
            # --- 锁 3：物理静音隔离 ---
            clean_p = os.path.join(temp_dir, f"lock_{i}.wav")
            dur_target = end_t - start_t
            
            # 执行毫秒级切割 + 极速淡入淡出（50ms级）
            cmd_lock = [
                FFMPEG_BIN, "-y", "-i", raw_p,
                "-af", f"atrim=start={start_t}:end={end_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, dur_target-0.05)}:d=0.05",
                clean_p
            ]
            subprocess.run(cmd_lock, check=True, capture_output=True)
            valid_wavs.append(clean_p)

    # 合并
    output_wav = r"E:\VideoTranslator_Project\output_final\V22_TRIPLE_LOCK_AUDIT.wav"
    combined = np.concatenate([sf.read(p)[0] for p in valid_wavs])
    sf.write(output_wav, combined, db.sample_rate)
    print(f"\n🏆 V22 三重锁死版已产出：{output_wav}")

if __name__ == "__main__":
    run_v22_triple_lock()
