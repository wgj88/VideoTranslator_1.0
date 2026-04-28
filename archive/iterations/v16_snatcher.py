# -*- coding: utf-8 -*-
import os, sys, json, subprocess, re, numpy as np
import librosa, torch, soundfile as sf
import whisper

# --- 暴力路径锁定 ---
FFMPEG_BIN = r"C:\Users\Administrator\miniconda3\envs\blackwell_env\Lib\site-packages\static_ffmpeg\bin\win32\ffmpeg.exe"
os.environ["PATH"] = os.path.dirname(FFMPEG_BIN) + os.pathsep + os.environ["PATH"]

def ffmpeg_robust_load(path, sr=None, **kwargs):
    target_sr = sr if sr else 44100
    cmd = [FFMPEG_BIN, "-y", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(target_sr), "pipe:1"]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    return np.frombuffer(proc.stdout, dtype=np.float32), target_sr
librosa.load = ffmpeg_robust_load

sys.path.append(r"E:\VideoTranslator_Project")
from clone_dubber import VideoCloneDubber

def run_v16_snatcher():
    print(f"\n[V16-Snatcher] 正在启动【毫秒级发音阻断】手术...")
    
    script_path = r"E:\VideoTranslator_Project\separated_audio\V12_CONSTRAINED_SCRIPT.json"
    temp_dir = r"E:\VideoTranslator_Project\temp_factory\v16_snatched_wavs"
    os.makedirs(temp_dir, exist_ok=True)
    
    with open(script_path, "r", encoding="utf-8") as f: data = json.load(f)
    
    db = VideoCloneDubber()
    # 使用 base 模式进行验证，避开外部干扰
    auditor = whisper.load_model("base")

    valid_wavs = []
    for i in range(3):
        item = data[i]
        zh_text = item['zh'].strip()
        
        print(f"  -> 正在手术渲染 Seg_{i}: {zh_text}")
        # 1. 正常生成 (Base Voice)
        wav = db.model.generate(text=zh_text + "。")
        raw_p = os.path.join(temp_dir, f"raw_{i}.wav")
        sf.write(raw_p, wav, db.sample_rate)
        
        # 2. 调用 Whisper 进行单词级对齐，寻找“最后一个字”的终点
        # 我们使用 word_timestamps=True 来获取精准定位
        res = auditor.transcribe(raw_p, word_timestamps=True)
        
        # 寻找真实的起始和结束
        start_trim = 0.0
        end_trim = len(wav) / db.sample_rate
        
        if res['segments']:
            # 起点：第一个 segment 的起点
            start_trim = max(0, res['segments'][0]['start'] - 0.05)
            # 终点：最后一个 segment 的终点 (这是关键！多出来的“啊”会被排除在 segment 之外)
            end_trim = res['segments'][-1]['end'] + 0.05
            
        print(f"     📍 物理发音区间定位: {start_trim:.2f}s -> {end_trim:.2f}s")
        
        # 3. 物理切除“啊”
        clean_p = os.path.join(temp_dir, f"snatched_{i}.wav")
        dur_target = end_trim - start_trim
        
        cmd_snatch = [
            FFMPEG_BIN, "-y", "-i", raw_p,
            "-af", f"atrim=start={start_trim}:end={end_trim},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.05,afade=t=out:st={max(0, dur_target-0.1)}:d=0.1",
            clean_p
        ]
        subprocess.run(cmd_snatch, check=True, capture_output=True)
        valid_wavs.append(clean_p)

    # 合并
    output_wav = r"E:\VideoTranslator_Project\output_final\V16_SNATCHER_VERIFY.wav"
    combined = np.concatenate([sf.read(p)[0] for p in valid_wavs])
    sf.write(output_wav, combined, db.sample_rate)
    print(f"\n🏆 V16 阻断版音轨已就绪：{output_wav}")

if __name__ == "__main__":
    run_v16_snatcher()
